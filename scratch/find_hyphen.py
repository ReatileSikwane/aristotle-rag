import json, re
from pathlib import Path

data = json.loads(Path("data/processed/sections.json").read_text(encoding="utf-8"))
for s in data:
    for m in re.finditer(r"-(?:\s|$)", s["text"]):
        print(s["book"], s["chapter"], repr(s["text"][max(0, m.start() - 50): m.end() + 50]))