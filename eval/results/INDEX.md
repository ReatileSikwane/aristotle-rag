# Evaluation runs

One JSON file per run. Older files predate some recorded settings, so fields such as `rerank_pool` or `prompt_version` show `None` there; the notes below say what was actually on.

| File | Questions | Mode | What it was |
|---|---|---|---|
| `run_20261115_200324.json` | 12 (q01 to q14) | retrieval only | First retrieval baseline on the early question set. Superseded |
| `run_20261116_004319.json` | 20 (q01 to q20) | retrieval only | Early retrieval run during question-set construction. Superseded |
| `run_20261116_004733.json` | 20 (q01 to q23) | retrieval only | First 20-question retrieval baseline. Superseded |
| `run_20261116_005701.json` | 20 (q01 to q23) | generation | First full-pipeline run on 20 questions. Superseded |
| `run_20261116_045139.json` | 26 (q01 to q29) | retrieval only | First retrieval run on the frozen 26-question set |
| `run_20261116_051201.json` | 26 | generation | First full-pipeline run on 26 questions, before passages were saved for grading |
| `run_20261116_105924.json` | 26 | generation | Graded baseline (similarity gate and model refusal only). Hand grades in `eval/grades.yaml` |
| `run_20261117_005252.json` | 26 | generation | Rerun of the baseline, 26/26 answers identical to the graded run |
| `run_20261117_055038.json` | 26 | generation | Experiment 2: k=6 (rejected) |
| `run_20261119_160901.json` | 26 | generation | Final configuration on the frozen set (reranker gate on, pool 12, threshold -4.7). Gate settings were not yet recorded in the file |
| `run_20261119_162518.json` | 26 | retrieval only | Embedding-order retrieval baseline used in the README (retrieval-only runs always use embedding order) |
| `run_20261120_130055.json` | 2 (e05, e06) | generation | Glossary off: both out-of-corpus questions refused by the reranker gate |
| `run_20261120_132123.json` | 1 (e07) | generation | Gate blind spot: passed both gates, refused by the model |
| `run_20261120_142421.json` | 26 | generation | Experiment 7: stricter prompt v2 (rejected). Hand grades in `eval/grades_run_20261120_142421.yaml` |
| `run_20261120_144833.json` | 1 (e07) | generation | e07 under prompt v2, refused by the model |
| `run_20261120_232744.json` | 12 (h01 to h12) | generation | Held-out set, final configuration. The reported run. Hand grades in `eval/grades_run_20261120_232744.yaml` |
| `run_20261121_024531.json` | 12 | generation | Held-out repeat, final configuration (12/12 identical to the reported run) |
| `run_20261121_025453.json` | 12 | generation | Held-out, reranker gate off (pool 0) |
| `run_20261121_025644.json` | 12 | generation | Held-out repeat, final configuration |
| `run_20261121_114120.json` | 12 | generation | Held-out, reranker gate off (pool 0), repeat |
| `run_20261121_114415.json` | 12 | generation | Held-out repeat, final configuration |

Settings for every held-out run: prompt v1, glossary off, k=4, similarity gate 0.50; the only difference between runs is the reranker gate (pool 12 or 0).

Held-out answer wording came in two forms. Variant A: `run_20261120_232744.json`, `run_20261121_024531.json`, `run_20261121_114120.json`. Variant B: `run_20261121_025453.json`, `run_20261121_025644.json`, `run_20261121_114415.json`. Runs of the same variant gave identical text for all three answered questions, whatever the reranker setting; answer-or-refuse decisions and cited chapters were identical across all six. The variants line up with whether the model had been idle for more than 30 minutes before the run (A: first run after a long gap, B: run a few minutes after another), which is a hypothesis from the timestamps. The reported run and its hand grades are variant A.
