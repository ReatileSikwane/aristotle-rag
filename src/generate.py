from typing import Iterator

import ollama

from config import MAX_ANSWER_TOKENS, NUM_CTX, OLLAMA_MODEL, SEED, TEMPERATURE

OPTIONS = {
    "temperature": TEMPERATURE,
    "num_ctx": NUM_CTX,
    "num_predict": MAX_ANSWER_TOKENS,
    "seed": SEED,
}


def generate(messages: list[dict]) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL, messages=messages, options=OPTIONS, keep_alive="30m"
    )
    return response["message"]["content"].strip()


def generate_stream(messages: list[dict]) -> Iterator[str]:
    for part in ollama.chat(
        model=OLLAMA_MODEL, messages=messages, options=OPTIONS,
        keep_alive="30m", stream=True,
    ):
        yield part["message"]["content"]