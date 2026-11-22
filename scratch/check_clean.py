import re
from src.ingest import load_documents
from src.clean import clean_text


def words(t: str) -> list[str]:
    return re.findall(r"\w+", t)


raw = load_documents()
mismatches = 0
leftover = 0
for s in raw:
    cleaned = clean_text(s["text"])
    if words(cleaned) != words(s["text"]):
        mismatches += 1
        print("WORD MISMATCH at Book", s["book"], "Chapter", s["chapter"])
    leftover += len(re.findall(r"-(?:\s|$)", cleaned))

print(f"{len(raw)} sections checked, {mismatches} word mismatches")
print(f"hyphens followed by space/end still uncleaned: {leftover}")

ch8 = next(s for s in raw if s["book"] == 1 and s["chapter"] == 8)
c8 = clean_text(ch8["text"])
i = c8.find("Delos")
print("\n--- around 'Delos' (Book I.8) ---")
print(repr(c8[max(0, i - 40): i + 220]))

last = clean_text(raw[-1]["text"])
print(f"\n--- last section: Book {raw[-1]['book']}.{raw[-1]['chapter']}, {len(words(last))} words ---")
print(repr(last[-300:]))