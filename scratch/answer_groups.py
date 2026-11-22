import json
from pathlib import Path

RUNS = ["run_20261120_232744.json", "run_20261121_024531.json", "run_20261121_025453.json",
        "run_20261121_025644.json", "run_20261121_114120.json", "run_20261121_114415.json"]

data = {}
for name in RUNS:
    run = json.loads(Path("eval/results", name).read_text(encoding="utf-8"))
    data[name] = {r["id"]: r for r in run["generation"]}

differing = [q for q in data[RUNS[0]] if len({data[n][q]["refused"] for n in RUNS}) > 1]
print("questions whose answered/refused decision differs across runs:", differing or "none")

for qid in ["h01", "h02", "h03"]:
    groups = {}
    for name in RUNS:
        groups.setdefault(data[name][qid]["answer"], []).append(name[4:19])
    print(f"\n{qid}: {len(groups)} distinct answers")
    for answer, members in groups.items():
        cited = data[RUNS[[n[4:19] for n in RUNS].index(members[0])]][qid]["cited_chapters"]
        print(f"   {members}  cited {cited}")