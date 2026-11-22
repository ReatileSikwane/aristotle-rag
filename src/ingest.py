import re

from config import RAW_DIR

# filename stem -> (display title, expected number of books)
WORKS = {
    "nicomachean_ethics": ("Nicomachean Ethics", 10),
}

SEPARATOR_RE = re.compile(r"^-{20,}$")
BOOK_RE = re.compile(r"^BOOK\s+([IVX]+)$")
CHAPTER_RE = re.compile(r"^(\d{1,2})$")
FOOTER_MARKER = "Copyright statement:"


def roman_to_int(numeral: str) -> int:
    values = {"I": 1, "V": 5, "X": 10}
    total = 0
    for i, ch in enumerate(numeral):
        if i + 1 < len(numeral) and values[numeral[i + 1]] > values[ch]:
            total -= values[ch]
        else:
            total += values[ch]
    return total


def parse_work(raw_text: str, title: str) -> list[dict]:
    sections: list[dict] = []
    book = chapter = None
    buffer: list[str] = []

    def close_section() -> None:
        text = "\n".join(buffer).strip()
        # Anything before the first BOOK/chapter marker (the header) is dropped here.
        if book is not None and chapter is not None and text:
            sections.append(
                {"work": title, "book": book, "chapter": chapter, "text": text}
            )
        buffer.clear()

    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(FOOTER_MARKER) or stripped == "THE END":
            break
        if SEPARATOR_RE.match(stripped):
            continue
        if m := BOOK_RE.match(stripped):
            close_section()
            book, chapter = roman_to_int(m.group(1)), None
        elif m := CHAPTER_RE.match(stripped):
            close_section()
            chapter = int(m.group(1))
        else:
            buffer.append(line)
    close_section()
    return sections


def validate_sections(sections: list[dict], expected_books: int) -> None:
    last_book, last_chapter = 0, 0
    for s in sections:
        if s["book"] == last_book:
            ok = s["chapter"] == last_chapter + 1
        else:
            ok = s["book"] == last_book + 1 and s["chapter"] == 1
        if not ok:
            raise ValueError(
                f"Sequence break at Book {s['book']}, Chapter {s['chapter']} "
                f"(after Book {last_book}, Chapter {last_chapter})"
            )
        last_book, last_chapter = s["book"], s["chapter"]
    if last_book != expected_books:
        raise ValueError(f"Expected {expected_books} books, parsed {last_book}")


def load_documents(raw_dir=RAW_DIR) -> list[dict]:
    sections: list[dict] = []
    for filename, (title, expected_books) in WORKS.items():
        raw_text = (raw_dir / f"{filename}.txt").read_text(encoding="utf-8")
        work_sections = parse_work(raw_text, title)
        validate_sections(work_sections, expected_books)
        sections.extend(work_sections)
    return sections