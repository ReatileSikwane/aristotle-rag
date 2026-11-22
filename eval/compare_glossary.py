from pathlib import Path

import yaml

from config import RERANK_MIN_SCORE
from src.glossary import expand_query
from src.retrieve import rerank_gate_score, retrieve

FILES = [Path("eval/questions_v1.yaml"), Path("eval/extension_greek.yaml")]
K = 4
POOL = 12


def chapter_ref(result: dict) -> str:
    return result["citation"].split()[-1]


def evaluate(question: str, expected: list, use_glossary: bool) -> dict:
    query = expand_query(question) if use_glossary else question
    pool = retrieve(query, k=POOL, rerank_pool=0)
    top = pool[:K]
    refs = [chapter_ref(r) for r in top]
    rank = next((i for i, r in enumerate(refs, 1) if r in expected), None) if expected else None
    return {"query": query, "rank": rank, "similarity": top[0]["score"],
            "gate": rerank_gate_score(query, pool), "refs": refs}


for path in FILES:
    questions = yaml.safe_load(path.read_text(encoding="utf-8"))
    print(f"\n{path.name}")
    for q in questions:
        off = evaluate(q["question"], q["expected"], False)
        on = evaluate(q["question"], q["expected"], True)
        changed = on["query"] != off["query"]
        if path.name.startswith("extension") or changed or on["rank"] != off["rank"]:
            print(f"  {q['id']} {q['question']!r}")
            print(f"      expanded: {on['query']!r}" if changed else "      (no glossary term found)")
            print(f"      hit rank {off['rank']} -> {on['rank']}, similarity "
                  f"{off['similarity']:.2f} -> {on['similarity']:.2f}, reranker gate "
                  f"{off['gate']:.1f} -> {on['gate']:.1f} (threshold {RERANK_MIN_SCORE})")
            print(f"      top 4: {off['refs']} -> {on['refs']}")