import sys

from src.glossary import expand_query
from src.retrieve import retrieve

question, chapter = sys.argv[1], sys.argv[2]
results = retrieve(expand_query(question), k=40, rerank_pool=0)
found = False
for rank, r in enumerate(results, start=1):
    if r["citation"].split()[-1] == chapter:
        found = True
        print(f"rank {rank}  similarity {r['score']:.2f}  {r['text'][:220]!r}")
if not found:
    print(f"no chunk from {chapter} in the top 40")