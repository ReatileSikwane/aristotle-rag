import json
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL, PROCESSED_DIR


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL)


def get_collection(reset: bool = False):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection did not exist yet
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embed_model": EMBED_MODEL},
    )


def embed_and_index(chunks: list[dict], batch_size: int = 32) -> None:
    model = get_model()
    collection = get_collection(reset=True)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(
        texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True
    )
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "work": c["work"],
                "book": c["book"],
                "chapter": c["chapter"],
                "chunk_index": c["chunk_index"],
                "citation": c["citation"],
            }
            for c in chunks
        ],
    )
    print(f"indexed {collection.count()} chunks into '{COLLECTION_NAME}'")


if __name__ == "__main__":
    chunks = json.loads((PROCESSED_DIR / "chunks.json").read_text(encoding="utf-8"))
    embed_and_index(chunks)