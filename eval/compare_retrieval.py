import statistics
from pathlib import Path

import yaml

from src.retrieve import retrieve

QUESTIONS = Path("eval/questions_v1.yaml")

CONFIGS = [
    {"name": "baseline", "k": 4, "cap": 0},
    {"name": "cap2_k4",  "k": 4, "cap": 2},
    {"name": "k5",       "k": 5, "cap": 0},
    {"name": "cap2_k5",  "k": 5, "cap": 2},
    {"name": "k6",       "k": 6, "cap": 0},
    {"name": "cap2_k6",  "k": 6, "cap": 2},
]


def chapter_ref(result: dict) -> str:
    return result["citation"].split()[-1]


def run(questions: list[dict], k: int, cap: int) -> dict:
    out = {}
    for q in questions:
        refs = [chapter_ref(r) for r in retrieve(q["question"], k=k, max_per_chapter=cap, rerank_pool=0)]
        out[q["id"]] = {
            "hit": any(r in q["expected"] for r in refs) if q["expected"] else None,
            "distinct": len(set(refs)),
        }
    return out


questions = yaml.safe_load(QUESTIONS.read_text(encoding="utf-8"))
in_corpus = [q for q in questions if q["category"] == "in_corpus"]
ambiguous = [q for q in questions if q["category"] == "ambiguous"]
scored = in_corpus + ambiguous

print(f"{'config':<10} {'k':>2} {'cap':>4}  {'in-corpus hit':>14} {'ambiguous hit':>14} {'distinct chapters':>18}")
baseline = None
for cfg in CONFIGS:
    res = run(questions, cfg["k"], cfg["cap"])
    hit_in = sum(res[q["id"]]["hit"] for q in in_corpus)
    hit_amb = sum(res[q["id"]]["hit"] for q in ambiguous)
    distinct = statistics.mean(res[q["id"]]["distinct"] for q in scored)
    cap = "off" if cfg["cap"] == 0 else cfg["cap"]
    print(f"{cfg['name']:<10} {cfg['k']:>2} {cap:>4}  "
          f"{hit_in:>9}/{len(in_corpus):<4} {hit_amb:>9}/{len(ambiguous):<4} {distinct:>18.2f}")
    if baseline is None:
        baseline = res
    else:
        gained = [q["id"] for q in scored if res[q["id"]]["hit"] and not baseline[q["id"]]["hit"]]
        lost = [q["id"] for q in scored if baseline[q["id"]]["hit"] and not res[q["id"]]["hit"]]
        print(f"{'':<10} vs baseline: gained {gained}, lost {lost}")