# ORION-12 successor mechanic result: lexical-echo-resistant candidate generation

- **Record id**: `P2_LEXICAL_ECHO_SUCCESSOR_RESULT`
- **Date**: 2026-08-21
- **Freeze it answers**: `../../protocol/P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21.md`
  (twin `…_FREEZE_2026-08-21.json`, `parameters_sha256`
  `1a93ebbfcc0ea671aff098a466b995d29e7c2b881200febc03b49cab2291dd9f`)
- **Machine-readable result**: `P2_LEXICAL_ECHO_SUCCESSOR_RESULT_2026-08-21.json`
- **World content hash**: `3711a6f7b3997d7a6f24b292ec65fd2b6f56e13cd2161a45c4ca8bf28ed3f534`
- **Verdict**: `VALIDATED_ON_CONSTRUCTED_REPRODUCTION`
- **Claim scope**: `CONSTRUCTED_REPRODUCTION_ONLY`
- **Gate served**: `ORION-12-U-T5`

The freeze document was written, dated and hashed before the world was generated and before any arm
was executed. Every threshold below was set there. Nothing was retuned after a number was seen.

## 1. Did the construction reproduce the failure mode?

Yes, and more completely than the pre-committed band required.

| Quantity | Real probe | Constructed `echo` family |
|---|---|---|
| Recovery of the target by the current mechanic | 0 exact / 0 substring of 564; 8 (0.0142) at token overlap ≥ 0.5 | `hit@10 = 0.0000` over 120 tasks |
| Candidate budget | `mean_predicted_count = 11.13` | `k = 11` |
| Median rank of the target | not recoverable from the archive | **294** of 2760 |
| Best rank of the target over all 120 tasks | — | **46** — never once inside the budget |

**G1 REPRODUCTION passed** (`0.0000 ≤ 0.05`).

The mechanism is visible, not inferred. Worked case `TASK-0001`, question *"Which analysis gives the
spectral nucleation anomaly … the value is not in the main text: it appears in the supplementary
material, and the supplementary section presents it as a figure, with the figure note…"*:

- current mechanic's query terms: `supplementary, figure, analysis, gives, spectral, nucleation`
- its top three candidate titles: **`Supplementary Spectral`**, **`Figure Nucleation`**,
  **`Supplementary Spectral`**
- target rank: 299

That is the stage attribution's sentence, executed: *"'supplementary' in the question retrieving a
title containing 'Supplementary Orbit'."*

World precondition (checked on the corpus before any query issued): apparatus words sit at df/N
median **0.2255** (min 0.2141, max 0.2301); domain content words at df/N median **0.0380** (min
0.0239, max 0.0594). Apparatus vocabulary is genuinely non-discriminative and content vocabulary is
genuinely discriminative, as the freeze required.

## 2. Baseline versus successor on the primary outcome

Primary outcome: `hit@10` on the `echo` family, 120 paired tasks.

| Arm | hit@1 | **hit@10** | hit@11 | MRR@50 | median target rank |
|---|---|---|---|---|---|
| **B0** current mechanic (`D1` + unweighted surface match) | 0.0000 | **0.0000** | 0.0000 | 0.0002 | 294 |
| **B1** reference (`D1` + BM25, `baselines.Bm25Scorer`) | 0.0083 | **0.6333** | 0.7083 | 0.1665 | 9 |
| **A2** ablation: `D1` query, weighted saturating scoring | 0.0083 | **0.6667** | 0.7250 | 0.1758 | 8 |
| **A1** ablation: gated query, unweighted scoring | 0.8333 | **1.0000** | 1.0000 | 0.8731 | 1 |
| **S1** successor (`D4_DISCRIMINATIVE_TERM_GATING`) | **0.9833** | **1.0000** | 1.0000 | **0.9889** | 1 |

- Absolute gain S1 − B0 on `hit@10`: **+1.0000** (threshold was ≥ 0.30).
- Exact two-sided McNemar on paired `hit@10`: `b = 0`, `c = 120`, **p = 1.50e-36** (threshold < 0.01).
- **G2 SUCCESSOR passed.**

### What the ablations show, which is the more interesting result

The two halves of the repair are not equal.

- **Scoring alone is not enough.** Giving the *same* `D1` query a corpus-grounded weight (A2), or
  handing it to BM25 (B1), lifts `hit@10` from 0.00 to ≈ 0.65 but leaves `hit@1` at ≈ 0.008. The
  target is dragged into the candidate list and almost never to the top of it.
- **Query-term selection is where the failure lives.** Refusing to let a term that occurs in more
  than 5% of the corpus enter the query at all (A1), with the *old* unweighted ranking, already
  reaches `hit@10 = 1.00` and `hit@1 = 0.83`.
- The successor's weighting and admission rule add the remaining `hit@1` 0.83 → 0.98.

This sharpens the stage attribution. The defect is not that the ranker scored the wrong documents
highly — it is that the incidental term was ever treated as a content term at the query-formation
step, which is upstream of any ranker and cannot be fixed by swapping the ranker.

## 3. The guards

| Gate | Outcome | Numbers |
|---|---|---|
| **G3 HARM** (`no_echo`) | **passed**, non-vacuous | B0 `hit@10` 1.0000, S1 `hit@10` 1.0000, loss 0.0000. Vacuity floor 0.30 cleared by the baseline. At `hit@1`, S1 0.9833 vs B0 0.9000 — the successor is mildly *better* off-mode, not worse. |
| **G4 MARGINAL-OVER-BM25** (`echo`, non-blocking) | **passed** | S1 `hit@1` 0.9833 vs B1 0.0083, margin **+0.9750** (threshold +0.10). BM25's document-side IDF is *not* a substitute for the successor at the sharp end. |
| **G5 SPECIFICITY** (`paraphrase_gap`, non-blocking) | **passed** | Every arm scores `hit@1 = hit@10 = 0.0000`. The successor does **not** repair a semantic gap, which is correct: it is a lexical mechanic and its claim is confined to lexical echo. |

## 4. The successor's own failure mode, stated

The df gate is a threshold, and a threshold discards genuine content terms that sit above it. Over
the 220 tasks, **53 tasks (24%) had at least one content term discarded by the 0.05 gate**, 58 terms
in total — the corpus's most common domain words. In the worked case `TASK-0000` the gate threw away
`cortex` (df/N 0.0522) and the successor still found the target at rank 1, because three
discriminative terms remained. This is the mechanic's real exposure: on a question whose *entire*
content vocabulary is common, the gate would empty the query. That case does not occur in this
world and is not tested by it.

## 5. Deviation from the freeze, reported not repaired

The freeze (§3.3) states that a `paraphrase_gap` needle shares no content token with its question.
The synonym map is a permutation of the whole domain lexicon, so one of a task's own four terms can
be the image of another; **4 of 40 `paraphrase_gap` tasks leak exactly one content token**
(`TASK-0192`, `TASK-0200`, `TASK-0204`, `TASK-0212`). The world was **not** re-rolled: re-drawing
every task after an outcome was visible is exactly what the freeze forbids. The leak awarded no arm
any credit — all five arms score 0.0000 on that family including the four affected tasks — and
`paraphrase_gap` is a non-blocking control that enters no verdict gate. Declared in the result JSON
under `known_construction_defects` and pinned by a test.

The post-hoc gate diagnostic in §4 was computed after the frozen run. It changed no parameter, no
arm and no gate, and is labelled as post-hoc in the artifact.

## 6. What this does and does not license

**Licensed.**

1. The mechanism named in `DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json` is *sufficient on its
   own* to drive the probe's candidate generator to zero recovery: with no other defect present, the
   current mechanic never once placed the target inside an 11-candidate budget over 120 tasks, and
   its top candidates were literally `Supplementary Spectral` and `Figure Nucleation`.
2. A successor that gates query terms by corpus document frequency, selects by discriminativeness
   rather than by within-question repetition, weights matches by IDF with term saturation, and
   requires agreement on two discriminative terms, is **not** driven to zero by that mechanism —
   `hit@10` 1.00, `hit@1` 0.98 — while not degrading questions that never carried echo.
3. The repair is located at the **query-formation** stage, not the ranking stage. Substituting a
   stronger ranker (BM25) into the existing query recovers about two-thirds of `hit@10` and
   essentially none of `hit@1`.

**Not licensed. None of the following follows from this result:**

1. Any statement about `target_hits` on AutoResearchBench Deep. The official probe was **not**
   re-run and cannot be: `official_input.jsonl` is absent from the repository (only its sha256
   `46fd5500…` is recorded) and arXiv/OpenAlex return `CONNECT tunnel failed, response 403` at this
   environment's proxy.
2. Revival of `AUTORESEARCHBENCH_DEEP_ID_PROBE_V1`. That artifact and its `target_hits: 0` stand
   unmodified, as does `DEEP_JUDGE_CONTROL_2026-08-17.json` and the stage attribution.
3. Any claim that the successor has been run against a real provider, or that the effect size seen
   here (a constructed world with a designed-in remedy, near ceiling) transfers to a real corpus.
   The successor also carries an undischarged engineering dependency: it needs corpus-level document
   frequencies, which offline are exact but against a live provider require a result-count endpoint
   or a sampled index.
4. Any conclusion about non-lexical retrieval failures. `paraphrase_gap` shows the successor is
   inert against a semantic gap.

**The next step this result implies** — not taken here, for the environment reasons above — is to
re-generate Deep candidates with `D4_DISCRIMINATIVE_TERM_GATING` against the real provider under the
matched frozen envelope, and re-score with the same judge that passed `CONTROL_PASSED 9/9`.

## 7. Reproduction

```
PYTHONPATH=src python -c "import sys; from orion.study.p2.echo_campaign import main; sys.exit(main(['--repo-root','.']))"
python -m pytest tests/unit/study/p2_open_world/test_p2_lexical_echo_successor.py
```

The runner recomputes its own parameter digest and refuses to execute unless it equals the value in
the freeze twin, so the code and the frozen record cannot drift apart silently.
