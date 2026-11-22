import json
from collections import Counter
from pathlib import Path
import sys

import yaml

RESULTS_DIR = Path("eval/results")
GRADES_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("eval/grades.yaml")


def norm(value):
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return None if value is None else str(value).strip().lower()


def main() -> None:
    grades = yaml.safe_load(GRADES_PATH.read_text(encoding="utf-8"))
    run_name = grades[0]["run"]
    run = json.loads((RESULTS_DIR / run_name).read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in run["generation"]}

    ungraded = [g["id"] for g in grades
                if norm(g["faithful"]) is None or norm(g["answers_question"]) is None]
    graded = [g for g in grades if g["id"] not in ungraded]
    print(f"run: {run_name}")
    print(f"{len(graded)} graded, {len(ungraded)} ungraded {ungraded}")

    print("\nfaithful:", dict(Counter(norm(g["faithful"]) for g in graded)))
    print("answers_question:", dict(Counter(norm(g["answers_question"]) for g in graded)))

    print("\nhand-graded faithfulness against the automatic 'cited an expected chapter' flag:")
    table = Counter((norm(g["faithful"]), rows[g["id"]]["cited_expected"]) for g in graded)
    for (faithful, cited), n in sorted(table.items(), key=str):
        print(f"  faithful={faithful:<7} cited_expected={cited}: {n}")

    print("\nanswers needing attention:")
    for g in graded:
        if norm(g["faithful"]) != "yes" or norm(g["answers_question"]) != "yes":
            r = rows[g["id"]]
            print(f"  {g['id']} faithful={norm(g['faithful'])} answers={norm(g['answers_question'])} "
                  f"cited={r['cited_chapters']} expected={r['expected']}")
            if g.get("notes"):
                print(f"      note: {g['notes']}")


if __name__ == "__main__":
    main()