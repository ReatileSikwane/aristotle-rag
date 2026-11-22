import re
from pathlib import Path

text = Path("data/raw/nicomachean_ethics.txt").read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
print(f"{len(lines)} lines, {len(text):,} characters")

print('\n--- first 40 lines ---')
for i, line in enumerate(lines[:40]):
    print(i, repr(line))

books = [(i, L) for i, L in enumerate (lines) if re.match(r'^\s*BOOK\s+[IXV]+\s*$', L, re.I)]
numbers = [(i, L) for i, L in enumerate(lines) if re.match(r"^\s*\d{1,2}\s*$", L)]
print(f"\nbook headings found: {len(books)}")
print(f"bare-number lines found:{len(numbers)}")
print("first book headings:", books[:3])
print("replacement characters:", text.count("\ufffd"))