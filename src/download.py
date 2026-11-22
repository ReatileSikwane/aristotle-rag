from pathlib import Path
import requests
from config import RAW_DIR

SOURCES = {
    "nicomachean_ethics": "https://classics.mit.edu/Aristotle/nicomachaen.mb.txt",
}

def download_all()-> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        target = RAW_DIR / f"{name}.txt"
        if target.exists():
            print(f"skip {name} (already downloaded)")
            continue
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        target.write_bytes(response.content)
        print(f"saved {target} ({len(response.content):,} bytes)")

if __name__ == "__main__":
    download_all()