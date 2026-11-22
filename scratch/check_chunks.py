import json
import statistics
from pathlib import Path

from config import PROCESSED_DIR, CHUNK_MAX_WORDS
from src.chunk import chunk_documents, split_units

sections = json.loads((PROCESSED_DIR / "sections.json").read_text(encoding="utf-8"))
chunks = chunk_documents(sections)

sizes = [c["n_words"] for c in chunks]
print(f"{len(chunks)} chunks | words per chunk: min {min(sizes)}, "
      f"median {statistics.median(sizes):.0f}, max {max(sizes)}")
oversized = [c for c in chunks if c["n_words"] > CHUNK_MAX_WORDS + 40]
print(f"chunks more than 40 words over the limit: {len(oversized)}")

missing = 0
for s in sections:
    joined = "\n".join(c["text"] for c in chunks
                       if (c["book"], c["chapter"]) == (s["book"], s["chapter"]))
    for unit in split_units(s["text"]):
        if unit not in joined:
            missing += 1
print(f"sentences missing from chunks: {missing}")

long_ch = [c for c in chunks if (c["book"], c["chapter"]) == (4, 1)]
print(f"\nBook 4.1 has {len(long_ch)} chunks; citation: {long_ch[0]['citation']}")
print("END of chunk 0  :", repr(long_ch[0]["text"][-160:]))
print("START of chunk 1:", repr(long_ch[1]["text"][:160]))