import re

# Greek term (Latin script, lowercase) -> the English words Ross uses for it.
# Verify every English term against the text (scratch/check_glossary.py) before trusting it.
GLOSSARY = {
    "eudaimonia": ["happiness", "living well", "the good"],
    "eudaemonia": ["happiness", "living well", "the good"],
    "phronesis": ["practical wisdom"],
    "akrasia": ["incontinence", "incontinent"],
    "enkrateia": ["continence"],
    "arete": ["virtue", "excellence"],
    "eleutheriotes": ["liberality"],
    "philia": ["friendship"],
    "theoria": ["contemplation"],
    "ergon": ["function"],
    "mesotes": ["the mean", "intermediate"],
    "hexis": ["state of character"],
    "prohairesis": ["choice"],
}


def expand_query(query: str) -> str:
    lowered = query.lower()
    extra: list[str] = []
    for greek, english in GLOSSARY.items():
        if re.search(rf"\b{re.escape(greek)}\b", lowered):
            for term in english:
                if term.lower() not in lowered and term not in extra:
                    extra.append(term)
    return f"{query} ({', '.join(extra)})" if extra else query

def substitute_query(query: str) -> str:
    result = query
    for greek, english in GLOSSARY.items():
        result = re.sub(rf"\b{re.escape(greek)}\b", english[0], result, flags=re.IGNORECASE)
    return result