import json

from config import PROCESSED_DIR
from src.glossary import GLOSSARY

sections = json.loads((PROCESSED_DIR / "sections.json").read_text(encoding="utf-8"))
corpus = " ".join(s["text"] for s in sections).lower()

for greek, english in GLOSSARY.items():
    for term in english:
        count = corpus.count(term.lower())
        flag = "" if count else "   <-- NOT FOUND, remove or replace"
        print(f"{greek:<14} {term:<18} {count:>4}{flag}")