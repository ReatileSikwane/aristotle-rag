import json
import sys
from collections import Counter

import yaml

from config import PROCESSED_DIR

CATEGORIES = {"in_corpus", "out_of_corpus", "ambiguous"}
STYLES = {"neutral", "second_person", "aristotle_named"}
REQUIRED = ("id", "question", "category", "expected", "style")

with open(sys.argv[1] if len(sys.argv) > 1 else "eval/questions.yaml", encoding="utf-8") as f:
    questions = yaml.safe_load(f)

chunks = json.loads((PROCESSED_DIR / "chunks.json").read_text(encoding="utf-8"))
valid_refs = {c["citation"].split()[-1] for c in chunks}  # e.g. "IV.2"

problems = []
seen_ids, seen_text = set(), set()
for q in questions:
    qid = q.get("id", "<no id>")
    for key in REQUIRED:
        if key not in q:
            problems.append(f"{qid}: missing '{key}'")
    if qid in seen_ids:
        problems.append(f"{qid}: duplicate id")
    seen_ids.add(qid)
    text = q.get("question", "").strip().lower()
    if text in seen_text:
        problems.append(f"{qid}: duplicate question text")
    seen_text.add(text)
    if q.get("category") not in CATEGORIES:
        problems.append(f"{qid}: bad category {q.get('category')!r}")
    if q.get("style") not in STYLES:
        problems.append(f"{qid}: bad style {q.get('style')!r}")
    for ref in q.get("expected", []):
        if ref not in valid_refs:
            problems.append(f"{qid}: unknown chapter reference {ref!r}")
    if len(set(q.get("expected", []))) != len(q.get("expected", [])):
        problems.append(f"{qid}: duplicate chapter in expected")
    if q.get("category") == "in_corpus" and not q.get("expected"):
        problems.append(f"{qid}: in_corpus needs at least one expected chapter")
    if q.get("category") == "out_of_corpus" and q.get("expected"):
        problems.append(f"{qid}: out_of_corpus should have expected: []")

print(f"{len(questions)} questions:", dict(Counter(q.get("category") for q in questions)))
print(f"styles: {dict(Counter(q.get('style') for q in questions))}")
if problems:
    print(f"\n{len(problems)} problems:")
    for p in problems:
        print(" -", p)
else:
    print("\nno problems found")