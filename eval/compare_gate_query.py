from pathlib import Path

import yaml

from config import RERANK_MIN_SCORE
from src.glossary import expand_query, substitute_query
from src.retrieve import rerank_gate_score, retrieve

POOL = 12
SOURCES = [(Path("eval/questions_v1.yaml"), {"q21"}), (Path("eval/extension_greek.yaml"), None)]
NAMES = ["off", "A expanded", "B original", "C substituted"]


def gate(retrieval_query: str, gate_query: str) -> float:
    pool = retrieve(retrieval_query, k=POOL, rerank_pool=0)
    return rerank_gate_score(gate_query, pool)


def scores_for(question: str) -> dict:
    expanded, substituted = expand_query(question), substitute_query(question)
    return {
        "off": gate(question, question),
        "A expanded": gate(expanded, expanded),
        "B original": gate(expanded, question),
        "C substituted": gate(substituted, substituted),
    }


questions = []
for path, only in SOURCES:
    for q in yaml.safe_load(path.read_text(encoding="utf-8")):
        if only is None or q["id"] in only:
            questions.append(q)

totals = {n: 0 for n in NAMES}
print(f"{'id':<5}{'expects':<8}" + "".join(f"{n:>15}" for n in NAMES))
for q in questions:
    scores = scores_for(q["question"])
    expect = "answer" if q["category"] == "in_corpus" else "refuse"
    row = f"{q['id']:<5}{expect:<8}"
    for n in NAMES:
        s = scores[n]
        correct = s >= RERANK_MIN_SCORE if expect == "answer" else s < RERANK_MIN_SCORE
        totals[n] += correct
        row += f"{s:>12.1f} {'ok' if correct else 'XX'}"
    print(row)
print(f"\ncorrect gate decisions out of {len(questions)}: {totals}")