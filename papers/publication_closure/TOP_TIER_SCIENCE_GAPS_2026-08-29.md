# Top-tier science gaps, ORION-01…25

**Date:** 2026-08-29 · **Assessed tree:** `origin/main` · **`scientific_authority_delta`:** NONE

This ranks, per paper, the single highest-value gap a referee at a top venue would
raise, scored by (referee impact) × (closable without external authority).

**Provenance is marked on every row.** `[V]` = I verified it myself against primary
sources. `[R]` = reported by a survey pass and **not** independently verified; treat as
a lead, not a finding. Do not cite an `[R]` row as established.

**Structural** = needs external data, external investigators, new cluster compute, or the
operator. **Operational** = closable by analysis over artifacts already in the repo.

---

## Closed in this pass

| Paper | Gap | PR |
|---|---|---|
| ORION-08 `[V]` | Effect sizes without uncertainty; abstract asserted a contrast whose own committed CI crosses zero | [#1738](https://github.com/SzeChunYiu/ORION/pull/1738) |
| ORION-13 `[V]` | Degenerate baseline; discordance count undisclosed; holdout exercises 1 of 10 coordinates | [#1739](https://github.com/SzeChunYiu/ORION/pull/1739) |

### ORION-08 — what was wrong
`PUBLICATION_PAIRED_ANALYSIS_V1.json` already held paired 95 % bootstrap CIs, `n_pairs`
and win/tie/loss for all twelve N4 comparisons. None reached the manuscript.
`sections/03-results.tex` asserted scoped-vs-never reopening as a result while both
committed intervals for it contain zero (`[-0.540, 0.634]`, `[-0.663, 2.254]`, n=200 each).
Now wired through, with the abstract narrowed and multiplicity stated.

One trap avoided: N4-F3's remint-unnecessary row also has a zero-containing interval, but
it is `[0,0]` — an exact tie on all 200 pairs and the study's **prespecified passing
outcome**. It carries a distinct marker. Flagging it as "undetermined" would have
misreported a passed negative control as a failure.

### ORION-13 — what was wrong
Verified from primary source: `flat_predicate_baseline` merges iff predicates match
(`src/orion/study/p3_public_reference.py:230`), and **all 32 cases in each holdout are
predicate-equal**. The published baseline is therefore a **constant always-merge
predictor**, and its false-merge rate 0.1875 is identically the minority base rate 6/32 —
any always-merge rule reproduces the headline `-0.1875` exactly.

Battery at `papers/orion-13-global-knowledge-portrait/scripts/null_and_baseline_battery.py`
(hard-fails unless published aggregates reproduce; they do) further found:

- **Six cases carry the result.** McNemar b=6, c=0, exact two-sided p=0.031. The initial
  holdout gives b=4, c=0, **p=0.125 — not significant alone**. Pooled p=0.002. All three
  reported; the pooled figure does not replace the per-set ones.
- **Nine of ten coordinates decide no case** in either holdout. Every discriminating case
  is decided at `polarity`. A rule using only predicate+modality+polarity reproduces the
  full mechanism on all 64 cases at accuracy 1.000.

Framed, per the paper's own convention for its zero-effect ablations, as a coverage limit
on these corpora — not as evidence the other coordinates are dispensable.

**Deliberately not added:** a label-permutation null. Permuting gold on a deterministic
rule whose inputs determine the labels tests a question no referee asked; it would pad the
statistics without addressing whether the comparison is *informative*.

---

## The flagship lead was wrong — ORION-15 `[V]`

The brief flagged **seven empty tables in ORION-15 as an instrumentation omission**, high
value and cheap to wire. Verified directly: they are **honest `CANNOT_CHECK` declarations**
with stated reasons and an explicit refusal to impute
(`papers/orion-15-self-orion/manuscript/tables/P5-{2,4,5,6,7,T2,T3}*.tex`). Each carries a
header naming why the archive cannot support the row, e.g. P5-T2: *"no matched
baseline/ablation arms, round identities, or campaign-level outcomes. Numbers are not
imputed from the 21/24 diagnostic accuracy."*

**Wiring numbers into them would have been the defect, not the fix.**

I also chased the four extra 24-case arms in `evidence/glm-5.{2,3}-attribution-v2/`. They
are a **prompt-version ablation of the diagnostic instrument** (control = v1 prompt replay,
treatment = v2), on the same protected suite — *not* the transfer/integrity arms P5-T2
requires. **P5-T2's `CANNOT_CHECK` stands.** And the manuscript already reports the
treatment arm (24/24) and flags its provenance caveats in `sections/10-limitations.tex:222`.
ORION-15 is being handled honestly throughout; its real gap is structural.

---

## Ranked operational gaps still open

Highest value first. Each names the artifact holding the numbers.

1. **ORION-11 `[R]` — undisclosed floor effect.** `FLOOR_EFFECT_DIAGNOSIS_20260823.md`
   reportedly establishes that `orion_full` is 0/240-records different from three of its
   own ablations, that repeats are vacuous (1 of 576 pairs varies), and that 1/48 root
   success is a lexical-detector ceiling — while `manuscript/tables/P1-T2_baseline_ablation.tex`
   prints twelve apparently distinct rows advertising "5 stochastic repeats". If it holds,
   this is the highest-impact open item: a table implying independent arms that are
   record-identical. Raw: `results/raw/test_scored.jsonl`.
   **Verify the record-identity claim before acting on it.**
2. **ORION-19 `[R]` — headline with no uncertainty against a definitional comparator.**
   "4/5 vs 1/5, 0 vs 4 false compute escalations" over five families, no CI, no exact test,
   while the same paper computes bootstrap CIs and McNemar elsewhere. The comparator
   `uncertainty-escalate-compute` escalates compute by construction. Artifacts:
   `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_RUN.json`, `HEADLINE_TABLES_V1.json`.
3. **ORION-24 `[R]` — +0.142857 is 4 of 28 self-authored cases**, no interval, no exact
   test. Same shape as the ORION-13 fix: report the discordance count and an exact test.
   Artifact: `P14C_ADJUDICATION_CASES_V1.json`.
4. **ORION-12 `[R]` — premature closure is definitional.** All six baselines score 1.00 vs
   0.00, but only the governed system has an "undetermined" terminal available, so the
   difference could not have failed to appear. ORION-14 already applied this standard to
   its own H3 and reported inability-to-discriminate; the same reading is available here.
   Artifacts: `evidence/offline_results/RESULTS_SUMMARY_V1.json`, `OFFLINE_MECHANISMS_V1.json`.
5. **ORION-22 `[R]` — three-domain transfer is nine cases**, 0/3 regret, no CI, controls
   are degenerate corner policies. Artifact: `top_tier/p12_transfer_cases_v1.json`.
6. **ORION-02 `[R]` — three correlation statistics reported uncorrected** on a single
   n=44 PMLB corpus. Artifact: `rounds/r24-arm-conditional-fibres-revival/…R24_RESULT.md`.
7. **ORION-14 `[R]` — H1 CI treats 360 cases as independent** though drawn from twelve
   30-case families; clustering ignored. Closable **only if** per-case records are in-repo;
   the survey did not open them, so this may be structural.

## Structural — not closable here

ORION-01 (necessity open), 03 (donor-subtraction never measured), 04 (`theorem_authority=false`),
05 (pinned sector lemma-open), 06 (N=1, no counterfactual), 09 (single compiler family),
10 (frozen panels only), **15 (H1–H4 core unexecuted; needs a live protected campaign)**,
16 (self-authored kernel, no Lean-grade formalization), 17 (no ≥2-domain corpus exists),
18 (OPA/Cedar/in-toto binaries absent), 20 (H1–H6 `PROSPECTIVE_NOT_EXECUTED`),
21 (only non-synthetic test failed its gate), 23 (definitional ablation, no non-RCS
comparator), 25 (self-authored corpus, comparator by same lane). All `[R]` except 15 `[V]`.

## Honest negatives — correct practice, do not "fix"

ORION-09 `size-transfer-invariant-v1/CLAIM_DISPOSITION.md`; ORION-15's seven `CANNOT_CHECK`
tables `[V]`; ORION-14's self-diagnosed saturated H3; ORION-20's `PROSPECTIVE_NOT_EXECUTED`;
ORION-21's failed 8/10 digits gate; ORION-22's `BROKEN` verdicts; ORION-24's P14A vacuity
and P14B circularity self-corrections.

## What I could not verify

- **23 of 25 rows are `[R]`.** Only ORION-08, ORION-13 and ORION-15 were verified against
  primary sources. The survey pass was detailed and internally consistent, but a confident
  unverified table is exactly the shape that launders into fact.
- **ORION-07** — two scored dual-lane instances (`Q3-R1-QG19`, `Q3-R2-QG20`) exist while the
  manuscript says one. They may be the "independently launched frontier lanes" the Deferred
  subsection already accounts for. Resolving it needs the Q3 instance-eligibility rule,
  which was not located. **A flag, not a defect.**
- **ORION-14** clustered-CI recomputation — per-case records never opened.
- **Bookkeeping defects, not science:** ORION-06's ledger is titled "ORION-02"; ORION-13's
  `CLAIM_LEDGER_V1.md` declares `ORION-13.C10` twice with different claims.
- No PDF was built for either PR. `pdflatex` is absent on this machine and CI is the only
  place these are allowed to build, so **LaTeX validity is asserted by CI, not by me**.
