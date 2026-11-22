import statistics
from pathlib import Path

import yaml

from src.retrieve import retrieve

QUESTIONS = Path("eval/questions_v1.yaml")
POOLS = [0, 8, 12, 20]  # 0 = no reranking (baseline)
K = 4


def chapter_ref(result: dict) -> str:
    return result["citation"].split()[-1]


questions = yaml.safe_load(QUESTIONS.read_text(encoding="utf-8"))
in_corpus = [q for q in questions if q["category"] == "in_corpus"]
ambiguous = [q for q in questions if q["category"] == "ambiguous"]
out_corpus = [q for q in questions if q["category"] == "out_of_corpus"]
scored = in_corpus + ambiguous

baseline = None
for pool in POOLS:
    hits, top = {}, {}
    for q in questions:
        res = retrieve(q["question"], k=K, rerank_pool=pool)
        hits[q["id"]] = any(chapter_ref(r) in q["expected"] for r in res)
        if pool:
            top[q["id"]] = res[0]["rerank_score"]
    label = "baseline" if pool == 0 else f"pool {pool}"
    print(f"{label:<9} in-corpus hit@{K}: {sum(hits[q['id']] for q in in_corpus)}/{len(in_corpus)}   "
          f"ambiguous: {sum(hits[q['id']] for q in ambiguous)}/{len(ambiguous)}")
    if baseline is None:
        baseline = hits
    else:
        gained = [q["id"] for q in scored if hits[q["id"]] and not baseline[q["id"]]]
        lost = [q["id"] for q in scored if baseline[q["id"]] and not hits[q["id"]]]
        print(f"          vs baseline: gained {gained}, lost {lost}")
    if pool:
        inside = [top[q["id"]] for q in in_corpus]
        outside = [top[q["id"]] for q in out_corpus]
        print(f"          top reranker score: in-corpus lowest {min(inside):.2f}, "
              f"median {statistics.median(inside):.2f}; out-of-corpus median "
              f"{statistics.median(outside):.2f}, highest {max(outside):.2f}")