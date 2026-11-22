import argparse
import json
from pathlib import Path

import yaml

from config import DATA_DIR

RESULTS_DIR = Path("eval/results")
CONTEXT_DIR = DATA_DIR / "eval_context"
SHEET_DIR = DATA_DIR / "grading"
DEFAULT_GRADES = Path("eval/grades.yaml")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_graded_run() -> Path:
    for path in sorted(RESULTS_DIR.glob("run_*.json"), reverse=True):
        if load(path).get("generation") and (CONTEXT_DIR / path.name).exists():
            return path
    raise SystemExit("No run with saved passages found. Run: python -m eval.evaluate --generate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", help="results file name to grade (default: newest run with saved passages)")
    parser.add_argument("--changed-from",
                        help="only include answers that differ from this earlier results file")
    args = parser.parse_args()

    run_path = RESULTS_DIR / args.run if args.run else latest_graded_run()
    run = load(run_path)
    context = load(CONTEXT_DIR / run_path.name)
    answered = [r for r in run["generation"] if not r["refused"]]

    if args.changed_from:
        earlier = {r["id"]: r for r in load(RESULTS_DIR / args.changed_from)["generation"]}
        answered = [r for r in answered
                    if r["id"] not in earlier or r["answer"] != earlier[r["id"]]["answer"]]

    lines = [f"# Grading sheet for {run_path.name}", ""]
    for r in answered:
        lines += [f"## {r['id']}: {r['question']}", "", f"ANSWER: {r['answer']}", ""]
        for i, p in enumerate(context[r["id"]], start=1):
            tag = "CITED" if i in r["cited"] else "not cited"
            lines += [f"### [{i}] {p['citation']} ({tag})", "", p["text"], ""]
        lines += ["---", ""]

    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    sheet_path = SHEET_DIR / f"sheet_{run_path.stem}.md"
    sheet_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(answered)} answers written to {sheet_path}")

    custom = bool(args.run or args.changed_from)
    grades_path = Path(f"eval/grades_{run_path.stem}.yaml") if custom else DEFAULT_GRADES
    if grades_path.exists():
        print(f"{grades_path} already exists, leaving your grades untouched")
        return
    template = [
        {"run": run_path.name, "id": r["id"], "faithful": None,
         "answers_question": None, "notes": ""}
        for r in answered
    ]
    grades_path.write_text(yaml.safe_dump(template, sort_keys=False, allow_unicode=True),
                           encoding="utf-8")
    print(f"grades template written to {grades_path}")


if __name__ == "__main__":
    main()