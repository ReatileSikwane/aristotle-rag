import json
import re

from config import CHUNK_MAX_WORDS, CHUNK_OVERLAP_WORDS, PROCESSED_DIR, CHUNK_MIN_NEW_WORDS

# Split after . ? ! ; but not after abbreviations like "e.g." / "i.e." / "viz."
SENTENCE_RE = re.compile(r"(?<!e\.g\.)(?<!i\.e\.)(?<!viz\.)(?<=[.?!;])\s+")


def to_roman(n: int) -> str:
    out = ""
    for value, numeral in [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= value:
            out += numeral
            n -= value
    return out


def split_units(text: str) -> list[str]:
    units = []
    for paragraph in text.split("\n\n"):
        units.extend(u for u in SENTENCE_RE.split(paragraph) if u.strip())
    return units


def overlap_tail(units: list[str], overlap_words: int) -> tuple[list[str], int]:
    tail, count = [], 0
    for unit in reversed(units):
        n = len(unit.split())
        if count + n > overlap_words:
            break
        tail.insert(0, unit)
        count += n
    return tail, count


def chunk_section(section: dict, max_words: int, overlap_words: int,
                  min_new_words: int = CHUNK_MIN_NEW_WORDS) -> list[str]:
    chunks, current, count = [], [], 0
    new_units: list[str] = []  # sentences not already present in the previous chunk
    for unit in split_units(section["text"]):
        n = len(unit.split())
        if current and count + n > max_words:
            chunks.append(" ".join(current))
            current, count = overlap_tail(current, overlap_words)
            new_units = []
        current.append(unit)
        new_units.append(unit)
        count += n
    if current:
        new_words = sum(len(u.split()) for u in new_units)
        if chunks and new_words < min_new_words:
            chunks[-1] += " " + " ".join(new_units)  # fold the remainder back in
        else:
            chunks.append(" ".join(current))
    return chunks


def chunk_documents(sections, max_words=CHUNK_MAX_WORDS, overlap_words=CHUNK_OVERLAP_WORDS):
    chunks = []
    for s in sections:
        slug = s["work"].lower().replace(" ", "-")
        citation = f"{s['work']} {to_roman(s['book'])}.{s['chapter']}"
        for i, text in enumerate(chunk_section(s, max_words, overlap_words)):
            chunks.append({
                "id": f"{slug}:{s['book']}.{s['chapter']}:{i}",
                "text": text,
                "work": s["work"],
                "book": s["book"],
                "chapter": s["chapter"],
                "chunk_index": i,
                "n_words": len(text.split()),
                "citation": citation,
            })
    return chunks


def build_chunks() -> list[dict]:
    sections = json.loads((PROCESSED_DIR / "sections.json").read_text(encoding="utf-8"))
    chunks = chunk_documents(sections)
    out = PROCESSED_DIR / "chunks.json"
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(chunks)} chunks to {out}")
    return chunks


if __name__ == "__main__":
    build_chunks()