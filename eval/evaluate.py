import argparse
import json
import statistics
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from src.index import get_collection
from src.glossary import expand_query

import yaml

from config import (CHUNK_MAX_WORDS, CHUNK_OVERLAP_WORDS, DATA_DIR, EMBED_MODEL,
                    MIN_TOP_SCORE, OLLAMA_MODEL, SEED, TEMPERATURE, TOP_K, NUM_CTX, MAX_ANSWER_TOKENS, MAX_PER_CHAPTER, RERANK_MIN_SCORE, RERANK_POOL, USE_GLOSSARY, PROMPT_VERSION)
from src.retrieve import retrieve

QUESTIONS_PATH = Path("eval/questions.yaml")
RESULTS_DIR = Path("eval/results")
CONTEXT_DIR = DATA_DIR / "eval_context"
MAX_K = 8


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def chapter_ref(result: dict) -> str:
    return result["citation"].split()[-1]  # "Nicomachean Ethics IV.2" -> "IV.2"


def first_hit_rank(results: list[dict], expected: list[str]):
    for rank, r in enumerate(results, start=1):
        if chapter_ref(r) in expected:
            return rank
    return None


# ---------- retrieval-only evaluation ----------

def evaluate_retrieval(questions: list[dict]) -> list[dict]:
    rows = []
    for q in questions:
        query = expand_query(q["question"]) if USE_GLOSSARY else q["question"]
        results = retrieve(query, k=MAX_K, rerank_pool=0)
        rows.append({
            "id": q["id"],
            "category": q["category"],
            "style": q["style"],
            "top_score": results[0]["score"],
            "rank": first_hit_rank(results, q["expected"]) if q["expected"] else None,
            "retrieved": [chapter_ref(r) for r in results[:TOP_K]],
            "expected": q["expected"],
        })
    return rows


def report_retrieval(rows: list[dict]) -> None:
    print("\n=== RETRIEVAL (no language model) ===")
    for category in ("in_corpus", "ambiguous"):
        group = [r for r in rows if r["category"] == category]
        if not group:
            continue
        print(f"\n{category} (n={len(group)})")
        for k in (1, TOP_K, MAX_K):
            hits = sum(1 for r in group if r["rank"] is not None and r["rank"] <= k)
            print(f"  hit@{k}: {hits}/{len(group)} = {hits / len(group):.0%}")
    print("\nper question:")
    for r in rows:
        if r["expected"]:
            status = f"hit at rank {r['rank']}" if r["rank"] else "MISS"
            print(f"  {r['id']}  top={r['top_score']:.2f}  {status:<14} "
                  f"expected={r['expected']} got={r['retrieved']}")
        else:
            print(f"  {r['id']}  top={r['top_score']:.2f}  (out of corpus) got={r['retrieved']}")


def report_gate_sweep(rows: list[dict]) -> None:
    inside = [r["top_score"] for r in rows if r["category"] == "in_corpus"]
    outside = [r["top_score"] for r in rows if r["category"] == "out_of_corpus"]
    print("\n=== SCORE GATE SWEEP ===")
    if not inside or not outside:
        print("needs both in_corpus and out_of_corpus questions")
        return
    print(f"in_corpus top score:     lowest {min(inside):.2f}, median {statistics.median(inside):.2f}")
    print(f"out_of_corpus top score: median {statistics.median(outside):.2f}, highest {max(outside):.2f}")
    print("threshold   out-of-corpus refused   in-corpus wrongly refused")
    for t in [x / 100 for x in range(40, 76, 4)]:
        refused_out = sum(s < t for s in outside)
        refused_in = sum(s < t for s in inside)
        print(f"  {t:.2f}        {refused_out}/{len(outside)}                     {refused_in}/{len(inside)}")


def report_styles(rows: list[dict]) -> None:
    print("\n=== PHRASING EFFECT (in_corpus) ===")
    by_style = defaultdict(list)
    for r in rows:
        if r["category"] == "in_corpus":
            by_style[r["style"]].append(r)
    for style, group in by_style.items():
        mean_score = statistics.mean(r["top_score"] for r in group)
        hits = sum(1 for r in group if r["rank"] is not None and r["rank"] <= TOP_K)
        print(f"  {style}: n={len(group)}, mean top score {mean_score:.2f}, hit@{TOP_K} {hits}/{len(group)}")


# ---------- full-pipeline evaluation ----------

def evaluate_generation(questions: list[dict]) -> list[dict]:
    from src.pipeline import answer  # imported here so retrieval-only runs never touch Ollama

    results = []
    for q in questions:
        start = time.time()
        r = answer(q["question"])
        elapsed = time.time() - start
        cited_chapters = [chapter_ref(r["chunks"][i - 1]) for i in r["cited"]]
        row = {
            "id": q["id"],
            "category": q["category"],
            "style": q["style"],
            "question": q["question"],
            "expected": q["expected"],
            "top_score": r["top_score"],
            "gate_score": r["gate_score"],
            "refused": r["refused"],
            "reason": r["reason"],
            "cited": r["cited"],
            "cited_chapters": cited_chapters,
            "cited_expected": bool(set(cited_chapters) & set(q["expected"])),
            "invalid_citations": r["invalid_citations"],
            "uncited": r["uncited"],
            "answer": r["answer"],
            "seconds": round(elapsed, 1),
            "passages": [
                {"citation": c["citation"], "score": round(c["score"], 3), "text": c["text"]}
                for c in r["chunks"]
            ],
        }
        results.append(row)
        outcome = f"refused ({r['reason']})" if r["refused"] else f"answered, cited {cited_chapters}"
        print(f"  {q['id']} [{q['category']}] {elapsed:.0f}s  {outcome}")
    return results


def report_generation(results: list[dict]) -> None:
    print("\n=== GENERATION (full pipeline) ===")
    out = [r for r in results if r["category"] == "out_of_corpus"]
    if out:
        refused = sum(r["refused"] for r in out)
        by_gate = sum(r["reason"] in ("low_retrieval_score", "low_rerank_score") for r in out)
        print(f"out_of_corpus correctly refused: {refused}/{len(out)} "
              f"({by_gate} by score gate, {refused - by_gate} by the model)")
        for r in out:
            if not r["refused"]:
                print(f"   ANSWERED but should refuse: {r['id']} {r['question']!r}")
    inn = [r for r in results if r["category"] == "in_corpus"]
    if inn:
        answered = [r for r in inn if not r["refused"]]
        print(f"in_corpus wrongly refused: {len(inn) - len(answered)}/{len(inn)}")
        if answered:
            print(f"  answered with no citation:       {sum(r['uncited'] for r in answered)}/{len(answered)}")
            print(f"  answered with invalid citation:  {sum(bool(r['invalid_citations']) for r in answered)}/{len(answered)}")
            print(f"  cited an expected chapter:       {sum(r['cited_expected'] for r in answered)}/{len(answered)}")
    for r in results:
        if r["category"] == "ambiguous":
            print(f"ambiguous {r['id']}: {'refused' if r['refused'] else 'answered'}")


# ---------- saving ----------

def save_run(rows: list[dict], generation) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.json"

    public_generation, context = None, {}
    if generation:
        public_generation = []
        for row in generation:
            row = dict(row)
            context[row["id"]] = row.pop("passages")  # passage text stays out of the repo
            public_generation.append(row)
        CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
        (CONTEXT_DIR / path.name).write_text(
            json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    payload = {
        "settings": {
            "llm": OLLAMA_MODEL, "embedding_model": EMBED_MODEL,
            "chunk_max_words": CHUNK_MAX_WORDS,"use_glossary": USE_GLOSSARY, "chunk_overlap_words": CHUNK_OVERLAP_WORDS,
            "top_k": TOP_K, "prompt_version": PROMPT_VERSION, "rerank_pool": RERANK_POOL, "rerank_min_score": RERANK_MIN_SCORE, "max_per_chapter": MAX_PER_CHAPTER, "min_top_score": MIN_TOP_SCORE,
            "temperature": TEMPERATURE, "num_ctx": NUM_CTX, "max_answer_tokens": MAX_ANSWER_TOKENS, "seed": SEED,
            "n_chunks": get_collection().count(),
        },
        "retrieval": rows,
        "generation": public_generation,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true",
                        help="also run the full pipeline through the language model (slow)")
    parser.add_argument("--questions", default=str(QUESTIONS_PATH),
                        help="question file to run (default: eval/questions.yaml)")
    parser.add_argument("--only", default="",
                        help="comma-separated question ids to run, e.g. q21,e01")
    args = parser.parse_args()

    questions = load_questions(Path(args.questions))
    if args.only:
        wanted = {i.strip() for i in args.only.split(",")}
        questions = [q for q in questions if q["id"] in wanted]
        if not questions:
            raise SystemExit("no questions matched --only")

    rows = evaluate_retrieval(questions)
    report_retrieval(rows)
    report_gate_sweep(rows)
    report_styles(rows)

    generation = None
    if args.generate:
        print("\nrunning the full pipeline, expect roughly 20 to 40 seconds per answered question...")
        generation = evaluate_generation(questions)
        report_generation(generation)

    print(f"\nsaved to {save_run(rows, generation)}")


if __name__ == "__main__":
    main()