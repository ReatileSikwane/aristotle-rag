import re

from config import MIN_TOP_SCORE, RERANK_MIN_SCORE, RERANK_POOL, TOP_K, USE_GLOSSARY
from src.generate import generate
from src.prompt import REFUSAL_TOKEN, build_prompt
from src.retrieve import rerank_gate_score, retrieve
from src.glossary import expand_query

CITATION_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
REFUSAL_MESSAGE = (
    "I find nothing in the passages before me that answers this, and I will not guess."
)


def extract_citations(answer_text: str, n_chunks: int) -> tuple[list[int], list[int]]:
    cited, invalid = set(), set()
    for group in CITATION_RE.findall(answer_text):
        for number in group.split(","):
            idx = int(number)
            (cited if 1 <= idx <= n_chunks else invalid).add(idx)
    return sorted(cited), sorted(invalid)


def prepare(query: str, k: int = TOP_K, work: str | None = None) -> dict:
    search_query = expand_query(query) if USE_GLOSSARY else query
    pool = retrieve(search_query, k=max(k, RERANK_POOL), work=work, rerank_pool=0)
    chunks = pool[:k]  # passages for the prompt stay in embedding order
    top_score = chunks[0]["score"] if chunks else 0.0

    gate_score, gate_reason = None, None
    if top_score < MIN_TOP_SCORE:
        gate_reason = "low_retrieval_score"
    elif RERANK_POOL:
        gate_score = rerank_gate_score(search_query, pool)
        if gate_score < RERANK_MIN_SCORE:
            gate_reason = "low_rerank_score"

    return {
        "query": query,
        "search_query": search_query,
        "chunks": chunks,
        "top_score": top_score,
        "gate_score": gate_score,
        "gate_reason": gate_reason,
        "gated": gate_reason is not None,
        "messages": None if gate_reason else build_prompt(query, chunks),
    }


def finalize(prep: dict, raw: str | None) -> dict:
    result = {
        "query": prep["query"],
        "chunks": prep["chunks"],
        "top_score": prep["top_score"],
        "gate_score": prep["gate_score"],
        "raw": raw,
        "answer": raw,
        "refused": False,
        "reason": None,
        "cited": [],
        "invalid_citations": [],
        "uncited": False,
    }
    if prep["gated"]:
        result.update(answer=REFUSAL_MESSAGE, refused=True, reason=prep["gate_reason"])
    elif REFUSAL_TOKEN in raw:
        result.update(answer=REFUSAL_MESSAGE, refused=True, reason="model_refusal")
    else:
        cited, invalid = extract_citations(raw, len(prep["chunks"]))
        result.update(cited=cited, invalid_citations=invalid, uncited=not cited)
    return result


def answer(query: str, k: int = TOP_K, work: str | None = None) -> dict:
    prep = prepare(query, k, work)
    raw = None if prep["gated"] else generate(prep["messages"])
    return finalize(prep, raw)