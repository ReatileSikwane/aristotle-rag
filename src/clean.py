import json
import re

from config import PROCESSED_DIR
from src.ingest import load_documents

PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")
ARCHIVE_DASH_RE = re.compile(r"(?<=\w)-(?:\s+|$)")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    paragraphs = []
    for block in PARAGRAPH_SPLIT_RE.split(text):
        joined = WHITESPACE_RE.sub(" ", block).strip()  # reflow hard-wrapped lines
        if not joined:
            continue
        joined = ARCHIVE_DASH_RE.sub(" \u2014 ", joined).strip()  # "word- word" -> dash
        paragraphs.append(joined)
    return "\n\n".join(paragraphs)


def build_processed() -> list[dict]:
    sections = load_documents()
    for s in sections:
        s["text"] = clean_text(s["text"])
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "sections.json"
    out.write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(sections)} sections to {out}")
    return sections


if __name__ == "__main__":
    build_processed()