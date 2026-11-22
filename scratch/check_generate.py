import time

from config import TOP_K
from src.generate import generate
from src.prompt import build_prompt
from src.retrieve import retrieve

questions = [
    "What is justice?",
    "What is eudaimonia?",
    "Who won the 2018 football World Cup?",
]

for q in questions:
    chunks = retrieve(q, k=TOP_K)
    messages = build_prompt(q, chunks)
    start = time.time()
    answer = generate(messages)
    elapsed = time.time() - start
    print(f"Q: {q}  ({elapsed:.1f}s)")
    print("retrieved:", [f"[{i}] {c['citation']} {c['score']:.2f}" for i, c in enumerate(chunks, 1)])
    print(answer)
    print()