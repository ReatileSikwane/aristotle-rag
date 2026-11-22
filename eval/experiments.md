## Experiment 1: cap of 2 chunks per chapter (retrieval only, frozen set)
At k=4 the cap left hit counts unchanged (10/13 in-corpus, 2/4 ambiguous) and raised
distinct chapters per question from 3.47 to 3.59. No benefit, left off.

## Experiment 2: k=6 (full run, run_20261117_055038.json)
Recall rose (in-corpus 10/13 to 12/13, ambiguous 2/4 to 3/4) and the false refusal on
q09 disappeared. But out-of-corpus refusals fell from 9/9 to 8/9 (poet question answered,
citing IX.7; <your reading of the answer>), mean time per answered question rose from
about 30 s to about 57 s, and answers cited up to five chapters. Rejected, k=4 stays.

## Experiment 2: k=6 (full run, run_20261117_055038.json)
Recall rose (in-corpus 10/13 to 12/13, ambiguous 2/4 to 3/4) and the false refusal on
q09 disappeared, but the q09 answer was stitched together from five chapters, so the
recovered recall did not become a better answer. Out-of-corpus refusals fell from 9/9 to
8/9: the poet question (q03) was answered because a retrieved passage (IX.7) mentions
poets only as a comparison for how people love their own work, and the model stretched
that into an answer. Mean time per answered question rose from about 30 s to about 57 s,
and answers cited up to five chapters. Rejected; k=4 stays.

## Experiment 3: cross-encoder reranker (retrieval only, frozen set)
Model: cross-encoder/ms-marco-MiniLM-L-6-v2, candidate pools of 8, 12 and 20, keeping top 4.
Ranking: pool 8 net 0 hits, pool 12 net +1 (13/17 vs 12/17), pool 20 net -1, with an easy
question (q25) demoted at pool 20. Treated as noise. Likely cause: the model was trained
on web search passages, not archaic philosophical English.
Gating: top reranker score separates the groups far more widely in median (in-corpus +2.93,
out-of-corpus -10.84) but the ranges still overlap (lowest in-corpus -8.15, highest
out-of-corpus -6.08). Threshold sweep to follow.

## Experiment 4: reranker as a refusal gate (pre-registered before any held-out run)
Setting: top 12 candidates by embedding similarity; the 4 passages sent to the model stay
in embedding order. Refuse if the best cross-encoder score among the 12 is below -4.7
(midpoint between -6.08, the highest out-of-corpus score, and -3.34, the lowest score of
a question that stays answered). Chosen on the frozen set, so tuning-set numbers only.
Prediction: 9/9 out-of-corpus refused; q21 and q23 newly refused; the other 24 answers
identical to the graded baseline run.

### Experiment 4 result (run_20261119_160901.json)
Prediction confirmed exactly. 9/9 out-of-corpus questions refused: 5 by the similarity gate
and 4 by the reranker gate (q03, q27, q28, q29, which the model alone had refused in the
baseline). q21 and q23 newly refused; the other 24 answers were identical to the graded
baseline, so grades carry over. In-corpus refused 2/13 (q09 by the model, q21 by the
reranker gate), both cases where the answering chapter never reached the model. Of the 13
answers still produced, 9 were graded both faithful and answering the question (9/15 before).
Cost: about 1 s per question reaching the reranker.
Note: the retrieval-only section of this run used the reranker's order because RERANK_POOL
was set in config. It is not the embedding baseline and should be ignored.

## Experiment 5: query glossary for Greek terms (pre-registered)
Change: append Ross's English words for any Greek term in the question before searching;
prompt still receives the original question. Prediction: on the frozen set only q21 changes
search; for q21 the defining chapter (I.7) enters the top 4 and the reranker gate score
rises above the -4.7 threshold. Success on the extension set: the glossary raises or keeps
hit rank for each question and never lowers it. The threshold is not changed to rescue
any question.

### Experiment 5 result (retrieval only, glossary on vs off)
Prediction half confirmed. q21: reranker gate score rose from -8.1 to 0.6 (above -4.7), but
the defining chapter I.7 did not enter the top 4 (now I.12, I.8, I.9, I.8). Five questions with
a glossary term (q21, e01 to e04): hit@4 rose from 1/5 to 3/5; e01 and e02 went from misses to
hits, e03 improved from rank 4 to 3, e04 and q21 unchanged. No question got worse.

### Experiment 5b (pre-registered, before running e05, e06 or any generation)
Predictions: e05 and e06 (out-of-corpus, contain a Greek term) keep a reranker gate score below
-4.7 and stay refused. In the generation run, q21 changes from refused to answered; the other
25 frozen answers are identical to run_20261119_160901. No glossary or threshold edits to
rescue any result.

### Experiment 6 result (eval.compare_gate_query)
Rule: adopt a variant only if it refuses e05 and e06 and answers at least 3 of the 5 in-corpus
items. No variant qualified, so the glossary stays off in the pipeline (USE_GLOSSARY = False).
- off and B (search expanded, gate on the original wording): refuse e05 and e06 but wrongly
  refuse q21, e01 and e02 (4/7 correct gate decisions). B's decisions match "off"; its scores
  differ by up to 3 points because the candidate pool changes.
- A (expanded) and C (Greek word substituted): answer all five in-corpus items but let e05 and
  e06 through (5/7). Substituted e06 scored +2.2 against a threshold of -4.7.
Reading: the cross-encoder score follows the wording of the query, not whether the specific thing
asked is in the text; corpus words added or substituted raise it regardless of answerability.
Glossary still improved retrieval: hit@4 on the five Greek-term questions rose from 1/5 to 3/5.
With the glossary off, e05 and e06 are refused by the reranker gate (run_20261120_130055).
Known limitation: questions containing an unlisted or listed Greek term are refused.

### e07 result (run_20261120_132123.json)
Prediction (gate blind spot) confirmed. "What does Plato's Republic say about practical wisdom?"
had top similarity 0.77 and passed both the similarity gate and the reranker gate (-4.7). The
model refused it (model_refusal). Evidence for the layered design; one question, one seed.

### Experiment 7 (pre-registered): stricter prompt (PROMPT_VERSION v2)
Change: system prompt only. Added rules: cite only a passage that directly answers the
question; do not combine ideas from different passages; refuse if no passage directly
answers. Model, seed, passages and both gates unchanged.
Adopt v2 only if ALL hold on the frozen set after regrading changed answers:
1. all 9 out-of-corpus questions still refused, and e07 still refused;
2. none of the 9 answers graded both faithful and answering the question gets a worse grade;
3. at least one of q07, q10, q20, q22 becomes both-yes (for q22, an ambiguous question,
   a refusal also counts);
4. in-corpus false refusals rise by at most 1 (currently 2 of 13).
If any condition fails, PROMPT_VERSION goes back to "v1" and v2 is reported as a finding.

### Experiment 7 result (run_20261120_142421.json): v2 REJECTED
Conditions: (1) met, 9/9 out-of-corpus refused and e07 refused by the model; (2) FAILED,
q08, q24 and q26 got worse among the nine baseline answers graded faithful and answering
(q24's downgrade was a usefulness judgement; without it q08 and q26 still fail);
(3) met, q07 and q20 became both-yes and q22 became a refusal; (4) met, in-corpus false
refusals unchanged at 2/13. Both faithful and answering: 9/13 answered at baseline, 8/12
under v2. v2 cited fewer passages and refused more often, but traded good answers for
others. New failure type: answers use content from retrieved passages they do not cite
(q10, q26), and chapter-level scoring can disagree with passage-level citation (q08).
PROMPT_VERSION returned to v1.

### Held-out evaluation (pre-registered)
Configuration: prompt v1, glossary off, k=4, no chapter cap, similarity gate 0.50 plus reranker
gate (pool 12, threshold -4.7). Questions: eval/heldout.yaml, run once on this configuration and
once with RERANK_POOL=0 for comparison. No setting is changed between or after the runs.
Predictions: (1) at least 7 of 8 out-of-corpus questions refused with the reranker gate, fewer
with it off; (2) h10 (enkrateia) refused by the gate, a known limitation, counted as a false
refusal; (3) h07 (Epicurus) and h08 (Stoics and anger) are the most likely out-of-corpus leaks.

### Experiment 7 result (run_20261120_142421.json): v2 REJECTED
Conditions: (1) met, 9/9 out-of-corpus refused and e07 refused by the model; (2) FAILED,
q08, q24 and q26 got worse among the nine baseline answers graded faithful and answering
(q24's downgrade was a usefulness judgement; without it q08 and q26 still fail);
(3) met, q07 and q20 became both-yes and q22 became a refusal; (4) met, in-corpus false
refusals unchanged at 2/13. Both faithful and answering: 9/13 answered at baseline, 8/12
under v2. v2 cited fewer passages and refused more often, but traded good answers for
others. New failure type: answers use content from retrieved passages they do not cite
(q10, q26), and chapter-level scoring can disagree with passage-level citation (q08).
PROMPT_VERSION returned to v1.

### Held-out evaluation (pre-registered)
Configuration: prompt v1, glossary off, k=4, no chapter cap, similarity gate 0.50 plus reranker
gate (pool 12, threshold -4.7). Questions: eval/heldout.yaml, run once on this configuration and
once with RERANK_POOL=0 for comparison. No setting is changed between or after the runs.
Predictions: (1) at least 7 of 8 out-of-corpus questions refused with the reranker gate, fewer
with it off; (2) h10 (enkrateia) refused by the gate, a known limitation, counted as a false
refusal; (3) h07 (Epicurus) and h08 (Stoics and anger) are the most likely out-of-corpus leaks.

### Held-out comparison (pre-registered)
Same questions and settings as run_20261120_232744 but RERANK_POOL=0 (similarity gate plus the
model's own refusal). Predictions: h10 is answered instead of refused; the five questions the
reranker refused (h04, h05, h09, h11, h12) reach the model, which refuses at least 3 of them.
No setting changed after seeing results. Result is reported either way, including if the model
alone refuses all 8 out-of-corpus questions (then the reranker gate adds speed and a second
layer, not measured accuracy).

### Held-out comparison result (run_20261121_114120.json, RERANK_POOL=0; full configuration repeat run_20261121_114415.json)
Prediction 1 FAILED: h10 was not answered with the reranker gate off, the model refused it
(model_refusal). Prediction 2 held: the five questions the gate refused (h04, h05, h09, h11,
h12) reached the model, which refused all five. With the gate off the model alone refused 8/8
out-of-corpus questions (0 by the similarity gate). Answers to h01, h02, h03 unchanged. Reading:
on unseen questions the reranker gate adds speed (about 1 s against 16 to 37 s per gated question
in the same run) and a second layer, not measured accuracy. Per-answer timings varied between
runs (answered questions 24 to 45 s in one run, 10 to 32 s in another).

### Cold versus warm model (pre-registered)
Observation: six held-out runs gave two answer variants, three each, identical within a variant
whatever the reranker setting. Variant A runs followed an idle gap of more than 30 minutes
(232744, 024531, 114120); variant B runs followed another run by 2 to 9 minutes (025453, 025644,
114415). Hypothesis: A = freshly loaded model, B = warm model. Test: `ollama stop qwen2.5:3b`,
then two consecutive held-out runs. Prediction: the first run reproduces variant A and the second
reproduces variant B. If both reproduce the same variant, or neither, the hypothesis is wrong
and the README keeps describing two unexplained variants.