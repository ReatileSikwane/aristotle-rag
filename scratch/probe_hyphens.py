import re
from pathlib import Path

text = Path("data/raw/nicomachean_ethics.txt").read_text(encoding="utf-8")
lines = text.splitlines()

ends = [i for i, ln in enumerate(lines) if ln.rstrip().endswith("-")]
print(f"{len(ends)} lines end with a hyphen")
for i in ends[:12]:
    print(i, repr(lines[i][-30:]), "->", repr(lines[i + 1][:25]))

print("mid-line 'word- word' dashes:", len(re.findall(r"\w- \w", text)))

print("\n--- last 12 lines of file ---")
for ln in lines[-12:]:
    print(repr(ln))