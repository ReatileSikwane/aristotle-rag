import json
import sys
from pathlib import Path


def load(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {r["id"]: r for r in data["generation"]}


a, b = load(sys.argv[1]), load(sys.argv[2])
differ = [i for i in a if a[i]["answer"] != b[i]["answer"]]
print(f"{len(a) - len(differ)}/{len(a)} answers identical")
for i in differ:
    print(f"  {i} differs")