from collections import Counter
from functools import lru_cache

from config import (CANDIDATE_POOL, MAX_PER_CHAPTER, QUERY_PREFIX,
                    RERANK_MODEL, RERANK_POOL)
from src.index import get_collection, get_model


@lru_cache(maxsize=1)
def _collection():
    return get_collection()


@lru_cache(maxsize=1)
def _reranker():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(RERANK_MODEL)


def retrieve(query: str, k: int = 5, work: str | None = None,
             max_per_chapter: int | None = None,
             rerank_pool: int | None = None) -> list[dict]:
    if max_per_chapter is None:
        max_per_chapter = MAX_PER_CHAPTER
    if rerank_pool is None:
        rerank_pool = RERANK_POOL

    pool = k
    if max_per_chapter:
        pool = max(pool, CANDIDATE_POOL)
    if rerank_pool:
        pool = max(pool, rerank_pool)

    embedding = get_model().encode([QUERY_PREFIX + query], normalize_embeddings=True)
    res = _collection().query(
        query_embeddings=embedding.tolist(),
        n_results=pool,
        where={"work": work} if work else None,
    )
    results = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        results.append({
            "text": doc,
            "citation": meta["citation"],
            "work": meta["work"],
            "book": meta["book"],
            "chapter": meta["chapter"],
            "score": 1 - dist,
        })

    if max_per_chapter:
        kept, seen = [], Counter()
        for r in results:
            if seen[r["citation"]] < max_per_chapter:
                kept.append(r)
                seen[r["citation"]] += 1
        results = kept

    if rerank_pool:
        candidates = results[:max(rerank_pool, k)]
        scores = _reranker().predict([(query, c["text"]) for c in candidates])
        for c, s in zip(candidates, scores):
            c["rerank_score"] = float(s)
        results = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)

    return results[:k]


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or "What is happiness?"
    for r in retrieve(question, k=5):
        print(f"{r['score']:.3f}  {r['citation']}\n    {r['text'][:300]}...\n")

def rerank_gate_score(query: str, candidates: list[dict]) -> float:
    scores = _reranker().predict([(query, c["text"]) for c in candidates])
    return float(max(scores))