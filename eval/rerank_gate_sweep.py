from pathlib import Path

import yaml

from src.retrieve import retrieve

POOL = 12
QUESTIONS = Path("eval/questions_v1.yaml")

questions = yaml.safe_load(QUESTIONS.read_text(encoding="utf-8"))
rows = []
for q in questions:
    top = retrieve(q["question"], k=4, rerank_pool=POOL)[0]
    rows.append({"id": q["id"], "category": q["category"],
                 "rerank": top["rerank_score"], "similarity": top["score"]})

print(f"{'id':<5} {'category':<14} {'rerank':>8} {'similarity':>11}")
for r in sorted(rows, key=lambda r: r["rerank"], reverse=True):
    print(f"{r['id']:<5} {r['category']:<14} {r['rerank']:>8.2f} {r['similarity']:>11.2f}")

inside = [r["rerank"] for r in rows if r["category"] == "in_corpus"]
outside = [r["rerank"] for r in rows if r["category"] == "out_of_corpus"]
ambiguous = [r["rerank"] for r in rows if r["category"] == "ambiguous"]

print("\nthreshold  out-of-corpus refused  in-corpus wrongly refused  ambiguous refused")
for t in range(-11, 4):
    print(f"  {t:>4}         {sum(s < t for s in outside)}/{len(outside)}"
          f"                    {sum(s < t for s in inside)}/{len(inside)}"
          f"                        {sum(s < t for s in ambiguous)}/{len(ambiguous)}")