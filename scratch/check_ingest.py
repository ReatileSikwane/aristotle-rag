from collections import Counter
from src.ingest import load_documents

sections = load_documents()
print(f"{len(sections)} sections (expect 116)")
print("chapters per book:", dict(sorted(Counter(s["book"] for s in sections).items())))

sizes = sorted(sections, key=lambda s: len(s["text"].split()))
shortest, longest = sizes[0], sizes[-1]
print(f"shortest: Book {shortest['book']}.{shortest['chapter']} = {len(shortest['text'].split())} words")
print(f"longest:  Book {longest['book']}.{longest['chapter']} = {len(longest['text'].split())} words")

last = sections[-1]
print("\n--- END of last section (check for footer junk) ---")
print(repr(last["text"][-400:]))