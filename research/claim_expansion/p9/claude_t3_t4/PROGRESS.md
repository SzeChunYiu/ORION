# P9-U-T3 / P9-U-T4 working notes

Started 2026-08-21. Branch `claude/papers-1-10-issues-uqrj2o`.

## Targets

- **P9-U-T4** (HARM_GUARD, "representation-length and format-prior attacks fail").
  Ledger blocker: "The representation-length and format-prior attacks are named as
  hostile alternatives but have not been run."
  Ledger unblock: "Run equal-token/length controls, semantic-orbit controls, symbol
  and order reminting, and same-information round-trip validation as gates rather
  than as robustness appendices."
- **P9-U-T3** (HARM_GUARD, "scale/compute crossing is on-grid and prospectively defined").
  Ledger blocker: "The critical scale S*(k,q) and critical inference budget C*(k,q)
  grid is not prospectively defined, so a crossing could not be shown to be on-grid
  rather than fitted."
  Ledger unblock: "Freeze the relational-complexity x representation x model-scale x
  inference-budget grid before outcomes, and preserve any null cell rather than
  fitting an exponent post hoc."

Source of truth for both: `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`
(P9 blockers block) and `src/orion/programme/superiority_terminals.py:420-434`.

## Orientation findings (read-only)

1. The attacks are *named* in `papers/orion-19-structured-epistemic-learning/successor/P9_U_MANUSCRIPT.tex`
   (sections "Frozen factorial design", "Adaptive Access Geometry Discovery", H4):
   "Equal-token/length controls, order/symbol reminting, semantic-orbit controls and
   exact information checks are mandatory"; "tests, in order, whether the cause is
   information mismatch/leakage, token/length confound, ...".
   They are named nowhere else and no runner exists. Confirmed by grep across
   `*.py|*.md|*.tex|*.json`: only hits are the terminal statement itself, the ledger,
   and the failure record.
2. The successor experiment those attacks were written for (frozen Qwen2.5
   0.5B/1.5B/3B direct-LLM run, issue #618) **does not exist**; P9-U-T1 is blocked on
   it and the model weights/network are unavailable in this sandbox. So the attacks
   cannot be run against that. They *can* be run against the only representation
   contrast P9 actually publishes: **D1**.
3. D1 is already known to be partly prior-valued:
   `research/failures/2026-08-unresponsive-comparator-prior-valued-margin/README.md`
   shows `TRANSCRIPT_BAG` and `TYPED_SERIALIZED_BAG` each emit a single label on all
   128 protected cases, so `+0.75` and `+0.50` are `1 - prior`. The only margin
   against a responsive comparator is `TYPED_RELATIONAL - UNTYPED_PAIR = +0.09375`.
   **Consequence for T4: an attack cannot "fail" against a margin that is already
   CANNOT_CHECK.** The gate has to be three-valued per contrast.

## Plan

- Freeze doc + JSON twin (hashed parameter block) under
  `papers/orion-19-structured-epistemic-learning/protocol/` BEFORE any arm runs.
- Instruments under `src/orion/study/p9/`.
- Evidence JSON under `papers/.../evidence/`.
- Tests under the P9 test convention, each mutation-checked.

## Log

- [x] Orientation / grep for where attacks are named.
- [ ] Read `records.Outcome`, `guard_exercise`, `comparator_response` APIs.
- [ ] Write freeze.
- [ ] Build instruments.
- [ ] Run.
- [ ] Tests.

---

## Milestone 1 (T3 done except tests) — 2026-08-21

Freeze written **before** any instrument existed:
- `papers/orion-19-structured-epistemic-learning/protocol/P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.md`
- `.json` twin, `parameters_sha256 = sha256:33138930449fda9a77c99a325f6c9ca2c13b58291218beb94704ea045334fe8c`

Instrument: `src/orion/study/p9/frontier_grid.py`. `main(argv)` + `__main__` guard.
Result: `papers/.../evidence/P9_U_T3_FRONTIER_GRID_STATUS_2026-08-21.json`, exit code 4.

**Verdict today: `T3_GRID_DECLARED_NO_CELL_EXECUTED` / `CANNOT_CHECK`, denominator 0 of 1344.**

Grid: k in {1,2,4,8} x 7 representations x {QWEN2_5:(0.5B,1.5B,3B,7B), LLAMA3_2:(1B,3B)}
x C in {1,4,16,64} x domain block in {FORMAL_RELATIONAL, NON_FORMAL_PROCEDURAL} = 1344 cells.
q in {0.70,0.85,0.95}. N fixed at 4 and N* declared out of scope.
S* = min ladder point with Q >= q else RIGHT_CENSORED; no interpolation, no fitted exponent.

Deliberate design points:
- The off-grid FAIL branch is driven by `claimed_crossings` **supplied by the outcome file**, not by
  the runner's own readings. A check over crossings the runner itself constructed could never fail;
  that would have been another empty-denominator guard. The audit reports `claims_checked` and says
  in words when it is 0 that it was not exercised.
- A fully executed grid with 0 evaluable crossing tests is `T3_NO_EVALUABLE_CROSSING_TEST` /
  `CANNOT_CHECK`, not PASS.
- No surrogate: the grid needs open-weight checkpoints that are not in this repo and a provider the
  sandbox proxy 403s. Refused to rename a classical-learner capacity ladder `S*`.

## Next

- [ ] T4 freeze written (done, see protocol/P9_U_T4_...md) — instrument next.
- [ ] T4 instrument `src/orion/study/p9/hostile_representation_attacks.py`.
- [ ] Mint T4 twin, run, write evidence.
- [ ] Tests for both, mutation-checked.

---

## Milestone 2 (T4 run) — 2026-08-21

Freeze: `papers/.../protocol/P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE_2026-08-21.md` + `.json`,
`parameters_sha256 = sha256:3a4c8a1e4211e8032ab3bbee0f9bb16f0d1f626b42f9c96c6b40cf0f115e18eb`.
Instrument: `src/orion/study/p9/hostile_representation_attacks.py`.
Result: `papers/.../evidence/P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json`, exit code 3.

### Verdict: `T4_ATTACK_SUCCEEDED` / **FAIL**. One component of the format-prior attack succeeded.

Preconditions, all passed, all with real denominators:
- PC-1 dataset fidelity: regenerated manifest == shipped `sha256:27752984…`.
- PC-2 gold preservation: 512 instances x 3 variants, 0 labels changed.
- PC-3 cardinality match: 192 corrupted instances, 1536 coordinate-side comparisons, 0 mismatches.
- PC-4 orbit bijectivity: 220 atoms, 220 distinct images.
- PC-5 index reversibility: 512/512 decode back byte for byte.
- RT same-information round trip: 512/512 serialized token lists decode back to the typed payload.
  (This is the first time P9's "same information" claim about TYPED vs TYPED_SERIALIZED has been
  checked rather than asserted. It holds.)
- PC-6 label variety: 128 protected cases, 3 distinct gold labels.

### BASE arms (this environment)

| arm | acc | distinct preds | informedness | departures |
|---|---|---|---|---|
| TYPED_RELATIONAL | 1.0 | 3 | 1.0 | 64 |
| UNTYPED_PAIR | 0.90625 | 3 | 0.8958 | 76 |
| LENGTH_RELATIONAL (new) | 0.875 | 3 | 0.8611 | 80 |
| TYPED_SERIALIZED_BAG | **0.75** | 2 | 0.5 | 32 |
| LENGTH_ONLY (new) | 0.75 | 2 | 0.5 | 32 |
| SERIALIZED_INDEXED (new) | 0.75 | 2 | 0.5 | 32 |
| SERIALIZED_PATHONLY (new) | 0.71875 | 3 | 0.4653 | 36 |
| TRANSCRIPT_BAG | 0.25 | **1** | 0.0 | **0** |

`TYPED_SERIALIZED_BAG` is 0.75 here, not the official 0.5 — the environment discrepancy already
recorded in `research/failures/2026-08-unresponsive-comparator-prior-valued-margin/`. It follows that
locally the serialized contrast is measurable (0.25) while officially it was CANNOT_CHECK.

Contrasts (`measure_contrast_margin`): typed-minus-transcript **CANNOT_CHECK /
COMPARATOR_CONSTANT**; typed-minus-serialized PASS (0.25 local); typed-minus-untyped PASS (0.09375).

### Representation-length attack: **FAILED** (does not explain the effect)

- RL-1 LENGTH_ONLY 0.75 vs typed 1.0, denominator 128. Reaches 2/3 of typed's above-floor margin.
- RL-2 LENGTH_RELATIONAL 0.875 vs typed 1.0, denominator 128.
- RL-3 equal-length control: typed stays **1.0** when corruption no longer changes any cardinality.
  Same control drops UNTYPED_PAIR 0.90625 -> 0.609375 and LENGTH_RELATIONAL 0.875 -> 0.75, i.e. most
  of the untyped comparator's score *was* length. Typed's was not.

### Format-prior attack: **SUCCEEDED** against `TYPED_SERIALIZED_BAG`

`FP-2_SEMANTIC_ORBIT_INVARIANCE::TYPED_SERIALIZED_BAG` = FAIL, 32 violations / 128 opportunities.
Under a bijective renaming of every value atom (gold labels preserved 512/512, verified):

    TYPED_SERIALIZED_BAG   0.75, 2 distinct predictions, informedness 0.5
      -> orbit             0.50, **1** distinct prediction (OBSTRUCTION x128), informedness 0.0

Separate diagnostic (scratch, not in the frozen artifact) makes it sharper: the orbit is an **exact
renaming of that arm's feature keys**. Renaming BASE's keys by the orbit map reproduces the ORBIT
feature rows exactly; both have 279 distinct keys, 150 train keys, 26 surviving in-vocabulary
protected keys, and the same 7 distinct protected rows with the same multiplicities
`[48,32,15,14,11,4,4]`. The design matrix is identical up to column *names*. The arm still changed
32 of 128 protected answers. Its decision on a whole 32-case group is not determined by its input.

Note this reproduces the official 0.5 constant-predictor result as one point of the orbit: the
shipped `+0.50` headline sits on a symbol orbit whose other points are different numbers.

- FP-1a/FP-1b reformat gap closure: **did not succeed** (0.25 -> 0.25 and -> 0.28125 against a
  0.125 threshold). The reformat does not close the local gap.
- FP-2 for TRANSCRIPT / UNTYPED / TYPED / LENGTH_ONLY / LENGTH_RELATIONAL / SERIALIZED_PATHONLY:
  **CANNOT_CHECK, 0 of 128 feature dicts changed.** Those arms read equality, presence and
  cardinality, never symbols, so the orbit cannot reach them. Structural invariance, reported as
  CANNOT_CHECK not PASS, because a guard with no opportunity has not held.
- FP-2 for SERIALIZED_INDEXED: **PASS**, 0 violations over 128 opportunities. The reversible-index
  reformat removes the symbol dependence even though it does not close the accuracy gap.
- FP-3 order remint: **CANNOT_CHECK for all 8 arms, 0 opportunities**, exactly as declared in
  advance in §7.3 of the freeze. `build_method_realization` passes every sequence coordinate through
  `tuple(sorted(set(...)))`, so the permuted dataset reproduces the base manifest digest
  `sha256:27752984…` byte for byte. The order-reminting control named in the ledger unblock is
  **vacuous by construction on D1** and cannot be reported as having been passed.

## Next

- [ ] Tests for both instruments, mutation-checked.
- [ ] Receipt MD under evidence/.
- [ ] ruff.

---

## Milestone 3 (tests + mutation checks) — 2026-08-21

- `tests/unit/study/p9/test_p9_frontier_grid.py` (17 tests)
- `tests/unit/study/p9/test_p9_hostile_representation_attacks.py` (32 tests)
- `ruff check` clean on all four touched files. 62 pass in 15 s; the wider P9 set
  (`tests/test_p9_d1.py tests/unit/study/p9 tests/test_p9_m1.py tests/test_p9_m1_v12.py
  tests/test_p9_identifiability.py`) is 91 pass in 89 s.
- The runner replays byte-identically twice (105 s per run), including after the two refactors
  below.

### Mutation checks — each mutation applied, test run RED, mutation reverted, test run GREEN

| # | mutation | test(s) driven red |
|---|---|---|
| M1 | equal-length control appends instead of replacing | `..._replaces_rather_than_appends`, `..._every_construction_precondition_holds...` |
| M2 | `LENGTH_ONLY` smuggles in a cross-side equality feature | `..._carries_no_value_identity_and_no_comparison` |
| M3 | `AttackComponent` lets a successful attack report a non-FAIL outcome | `..._cannot_report_a_successful_attack_as_anything_but_fail` |
| M4 | round-trip decoder stops restoring dependency integers | `..._really_does_carry_the_typed_information`, preconditions |
| M5 | orbit remint truncated to one hex digit (non-injective) | `..._every_construction_precondition_holds...` |
| M6 | invariance component counts every case as an opportunity when nothing changed | `..._no_opportunity_is_cannot_check_not_a_pass`, `..._order_remint_component_is_cannot_check...` |
| M7 | frontier extrapolates to the top of the ladder instead of censoring | `..._right_censored_rather_than_extrapolated`, `..._claimed_crossing_over_a_censored_frontier_fails` |
| M8 | grid with no evaluable crossing test reported as PASS | `..._no_uncensored_frontier_is_cannot_check_not_pass` |
| M9 | missing cell silently ignored | `..._blocks_rather_than_being_dropped` |
| M10 | `NOT_RUN` cell allowed to carry a quality | `..._may_not_carry_a_quality` |
| M11 | orbit salt drifts from the frozen record | twin digest test + artifact test |
| M12 | length-sufficiency tolerance widened from 1/128 to 0.25 | `..._decided_at_one_case_not_at_a_wider_tolerance` |
| M13 | constant reformatted arm scored instead of refused | `..._cannot_check_not_a_refuted_attack` |
| M14 | contrast with a constant comparator admitted as attackable | `..._not_eligible_to_be_attacked` |

Two mutations initially came back GREEN and each exposed a real weakness, both fixed:

- **M3 first pass** stayed green because `AttackComponent.__post_init__` carried a second guard
  (`outcome is PASS and succeeded`) strictly subsumed by the first. It was dead code. Removed, and
  the test parametrised over `PASS` and `CANNOT_CHECK`.
- **M12 / M14 first pass** stayed green because the only tests covering those code paths read the
  already-written result artifact rather than exercising the code. An artifact-pinning test pins the
  artifact, not the runner. Added two live tests, and extracted `eligible_contrasts()` out of
  `run_campaign` so the eligibility rule is directly testable. Neither change alters
  `FROZEN_PARAMETERS`; the digest is unchanged and the artifact replays byte-identically.

## Milestone 4 — receipt

`papers/orion-19-structured-epistemic-learning/evidence/P9_U_T3_T4_HOSTILE_ATTACK_RECEIPT_2026-08-21.md`

## Not done, deliberately

- The programme ledger (`research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`)
  is **not** edited. Neither gate is discharged and the blockers stand; T4's blocker sentence
  ("have not been run") is now false, but rewriting a frozen ledger is not this lane's to do.
- No `research/failures/` record is created. The FP-2 result looks like a distinct class —
  *an arm whose protected answers are a function of the symbol alphabet rather than of the
  semantics*, i.e. a score that lives on a semantic orbit — and it is a candidate for whoever owns
  that ledger. It is adjacent to but not the same as
  `2026-08-unresponsive-comparator-prior-valued-margin` (that record is about a comparator that gave
  one answer; this is about a comparator whose answer changes when nothing but the spelling does).

## Milestone 5 — post-run disclosure appended to the T4 freeze (Appendix A)

§8 of the freeze defined the FP-2/FP-3 denominator as "protected instances whose feature dict
changed". The runner is stricter: when the *training* input also changed, every protected case counts
as an opportunity, because the fitted model itself differs. Measured, the two readings coincide on
every arm in this run (128/128 for the two serialized arms, 0/0 for the other six), so no outcome
depends on it. Disclosed in Appendix A rather than silently, and §§1-10 are untouched.

Also recorded there: `SERIALIZED_INDEXED` is *not* structurally orbit-invariant — the per-instance
index follows sorted atom order and a rename permutes it, so all 128 of its protected feature dicts
change and its `PASS` is a measured one over a denominator of 128, not a free one. That is stronger
than the freeze expected and nothing was retuned to get it.

## Final state

| gate | verdict | outcome | denominator | disposition |
|---|---|---|---|---|
| P9-U-T4 | `T4_ATTACK_SUCCEEDED` | FAIL (exit 3) | 21 components, 7 with a live denominator, 14 CANNOT_CHECK | still BLOCKED |
| P9-U-T3 | `T3_GRID_DECLARED_NO_CELL_EXECUTED` | CANNOT_CHECK (exit 4) | 0 of 1344 cells | still BLOCKED |
