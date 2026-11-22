import json
from pathlib import Path

for path in sorted(Path("eval/results").glob("run_*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = [r["id"] for r in data["retrieval"]]
    settings = data["settings"]
    mode = "generation" if data.get("generation") else "retrieval only"
    print(f"{path.name}  {len(ids):>2} questions {ids[0]}..{ids[-1]}  {mode}  "
          f"pool={settings.get('rerank_pool')} prompt={settings.get('prompt_version')} "
          f"glossary={settings.get('use_glossary')}")
    