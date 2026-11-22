import time
import ollama
from config import OLLAMA_MODEL, TEMPERATURE, NUM_CTX

def ask(model: str, question: str) -> None:
    start = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": question}],
        options={"temperature": TEMPERATURE, "num_ctx": NUM_CTX},
    )
    elapsed = time.time() - start
    print(f"--- {model} ({elapsed:.1f}s) ---")
    print(response["message"]["content"])
    print()
if __name__ == "__main__":
    q = "According to Aristotle's Nichomache Ethics, what is eudaimnia? Answer in three sentences."
    for m in ["llama3.2:3b", "qwen2.5:3b"]:
        ask(m, q) # First call loads the model
        ask(m, q)# Second call is the warm timimg, making it faster
