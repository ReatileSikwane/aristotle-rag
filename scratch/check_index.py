import json

from config import PROCESSED_DIR, QUERY_PREFIX
from src.index import get_collection, get_model

chunks = json.loads((PROCESSED_DIR / "chunks.json").read_text(encoding="utf-8"))
small = [c for c in chunks if c["n_words"] < 60]
print(f"{len(small)} chunks under 60 words")
for c in small[:8]:
    print(" ", c["citation"], c["n_words"], repr(c["text"][:80]))

model = get_model()
collection = get_collection()
print(f"\n{collection.count()} chunks in index\n")

queries = [
    "What is happiness?",
    "What is eudaimonia?",
    "Is courage a mean between two extremes?",
    "Who won the 2018 football World Cup?",
]
for q in queries:
    emb = model.encode([QUERY_PREFIX + q], normalize_embeddings=True)
    res = collection.query(query_embeddings=emb.tolist(), n_results=3)
    print(f"Q: {q}")
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        print(f"   {1 - dist:.3f}  {meta['citation']}  {doc[:90]!r}")
    print()