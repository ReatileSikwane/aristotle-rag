import time

from src.pipeline import answer

questions = [
   "What is justice?",
    "What is eudaimonia?",
    "Who won the 2018 football World Cup?",
    "What is the role of a poet in society?",
    "How does Kant's categorical imperative differ from Aristotle's view of duty?",
]


for q in questions:
    start = time.time()
    r = answer(q)
    elapsed = time.time() - start
    print(f"Q: {q}  ({elapsed:.1f}s)")
    print(f"top score {r['top_score']:.2f} | refused={r['refused']} ({r['reason']}) | "
          f"cited={r['cited']} invalid={r['invalid_citations']} uncited={r['uncited']}")
    print(r["answer"])
    if r["refused"] and r["raw"]:
        print("raw model output:", repr(r["raw"]))
    print()
    print("retrieved:", [c["citation"] for c in r["chunks"]])