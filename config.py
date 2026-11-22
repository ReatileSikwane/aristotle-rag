from pathlib import Path

OLLAMA_MODEL = 'qwen2.5:3b'
TEMPERATURE = 0.2 # Kepping low to ensure faithfulness to source material
NUM_CTX = 4096 # Context window in tokens; higher uses more RAM

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR/ "raw"
PROCESSED_DIR = DATA_DIR / "processed"

CHUNK_MAX_WORDS = 180
CHUNK_OVERLAP_WORDS = 40

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "aristotle"

CHUNK_MIN_NEW_WORDS = 30

TOP_K = 4
MAX_ANSWER_TOKENS = 300
SEED = 42

MIN_TOP_SCORE = 0.50  # placeholder: tune on the evaluation set

MAX_PER_CHAPTER = 0   # 0 = no cap (the baseline behaviour); 2 = at most two chunks per chapter
CANDIDATE_POOL = 40   # how many candidates to fetch before the cap is applied

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

RERANK_POOL = 12          # candidates scored for the refusal gate (0 = off, baseline behaviour)
RERANK_MIN_SCORE = -4.7   # refuse if the best cross-encoder score in the pool is below this

USE_GLOSSARY = False

PROMPT_VERSION = "v1"   # "v1" = baseline prompt, "v2" = stricter citation rules