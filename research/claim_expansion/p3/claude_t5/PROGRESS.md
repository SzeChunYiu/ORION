# P3-U-T5 — running notes (claude_t5)

Blocker: "No new identity coordinate has been discovered from failure and
prospectively validated." Unblock: mine each false merge and false split for a
candidate discriminating coordinate, then validate on held-out cases or prove
the coordinate unnecessary.

## Status: STARTED 2026-08-21

## Step 0 — orientation (done)

Prior work lives in `research/p3-coordinate-necessity-v1/` (FREEZE_2026-08-21.md,
RESULTS_2026-08-21.md). It extended the atlas from n=32 to n=56 and repaired two
ablation arms. Its own §2 records the three items I was asked to confirm:

- `P3.FALSE_SCIENTIFIC_SPLIT` — CANNOT_CHECK / `COMPARATOR_NEVER_EXERCISED`.
  ORION: 0 violations of 42 opportunities. Comparator
  `exact_coordinate_conservative`: 0 separations emitted anywhere, so its
  false-split denominator is 0 on every corpus.
- `P3.OVERRESOLVED_UNRESOLVED_CASE` — CANNOT_CHECK / `NEVER_EXERCISED`, 0/0.
  Neither frozen atlas contains a single gold-`UNRESOLVED` case.
- parent atlas `ordinal_quartile` recovers `CONTRADICTORY` at informedness
  0.513 in-sample on `public-reference-v1.1-confirmatory` (n=32).

Key source: `src/orion/study/p3/identity_opportunity.py` (three-valued guard
denominators), `src/orion/study/p3/atlas_identifiability.py`.

## Next: reproduce all three by execution before building anything.

---

## Step 1 — all three items REPRODUCED by execution (2026-08-21)

`PYTHONPATH=src python -m orion.study.p3.public_reference_audit --cases <atlas>`

| atlas | n | ORION decision kinds | FALSE_MERGE | FALSE_SPLIT | OVERRESOLVED |
|---|---|---|---|---|---|
| `public-reference-v1` (pilot) | 32 | 28 MERGED_CORRECTLY, 4 SEPARATED_CORRECTLY | PASS 0/4 | CANNOT_CHECK `COMPARATOR_NEVER_EXERCISED` | **CANNOT_CHECK `NEVER_EXERCISED` 0/0** |
| `public-reference-v1.1-confirmatory` | 32 | 26 MERGED_CORRECTLY, 6 SEPARATED_CORRECTLY | PASS 0/6 | CANNOT_CHECK, same | **CANNOT_CHECK 0/0** |
| `coordinate-necessity-v1` | 56 | 42 MERGED_CORRECTLY, 14 SEPARATED_CORRECTLY | PASS 0/14 | CANNOT_CHECK, ORION 0/42 vs comparator 0 opportunities | **CANNOT_CHECK 0/0** |

All three confirmed. Exit code 3 in every case. Guard machinery is already
three-valued (`assess_guard` returns `Outcome.CANNOT_CHECK` on a zero
denominator; `GuardAssessment.__post_init__` refuses PASS on a vacuity reason).
So the `not None is True` trap is *not* present in `guard_exercise` /
`identity_opportunity`. That part is sound.

### The finding that actually matters for T5

**ORION has zero false merges and zero false splits on every P3 atlas.**
T5's unblock recipe — "mine each false merge and false split for a candidate
discriminating coordinate" — has an **empty input set**. There is nothing to
mine. That is why T5 is blocked, and no amount of mining the existing evidence
can unblock it.

## Step 2 — structural census of the atlases (pre-freeze diagnosis)

Scripts: `/tmp/.../scratchpad/diag.py`, `diag2.py`, `diag3.py` (scratch only).

1. **No P3 atlas contains a single partially-observed pair.** Across all 9
   coordinates and all 88 cases in the three atlases, every coordinate is
   either observed on *both* sides or absent on *both* sides. One-sided-absent
   count: `{}` — empty, everywhere.
2. On the **real** parent atlas (n=32) the gold is 26 `COMPATIBLE` + 6
   `CONTRADICTORY`. `measurement_ids`, `temporal_context_ids`,
   `assumption_ids`, `attribution_id`, `discourse_relation` are empty on both
   sides in **32 of 32** cases; `construct_ids` in 13 of 32. So on real data the
   only load-bearing coordinates are polarity+modality. (The prior session's two
   repaired arms were repaired entirely on its 24 synthetic cases.)
3. **Redaction census** — cases where a coordinate is observed on both sides,
   the two values differ, and emptying it on one side changes the answer:
   - parent v1.1 (n=32): **6**, all `polarity`, all `CONTRADICTORY -> COMPATIBLE`
   - pilot v1 (n=32): **4**, same shape
   - extended (n=56): **14** = 6 polarity + 4 `measurement_ids` + 4
     `temporal_context_ids`; each `-> COMPATIBLE`
   These 14 are exactly ORION's 14 separations. **Silencing one side of the
   deciding coordinate destroys every separation ORION makes.**
4. `compare_meaning` overloads "unobserved" three inconsistent ways in one
   function: list coordinates (`_same_or_empty` and the `left.X and right.X`
   guards) read absence as **agreement**; `polarity` UNKNOWN reads as
   **agreement**; `modality` UNKNOWN reads as a **distinct value** (separation).

### Diagnosis

The over-resolution guard's 0/0 is not a sampling accident. The corpus contains
no partially-observed pair, so the failure mode that would expose a missing
coordinate has never had an instance. The channel is closed by construction.

## Next: write the freeze BEFORE building the probe.

---

## Step 3 — freeze written, then run (2026-08-21)

Freeze: `papers/orion-13-global-knowledge-portrait/protocol/P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md`
Twin:   same path, `.json`, `parameters_sha256 = 28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691`
Runner refuses to execute on digest mismatch (`verify_against_twin`).
Instrument: `src/orion/study/p3/partial_observation_probe.py`
Result: `papers/orion-13-global-knowledge-portrait/evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-21.json`
Probe cases: `.../PROBE_CASES_2026-08-21.jsonl` (48 cases)
Exit code 3 (FAIL), as designed.

### Primary result

`P3.OVERRESOLVED_UNRESOLVED_CASE` for `A0_orion_current`:

| corpus | before this study | after |
|---|---|---|
| `PROBE_DERIVATION` (12 cases from 6 real adjudicated pairs) | CANNOT_CHECK `NEVER_EXERCISED` 0/0 | **FAIL `VIOLATED` 12/12, rate 1.0** |
| `PROBE_HELDOUT_REAL` (8) | — | **FAIL 8/8, rate 1.0** |
| `PROBE_HELDOUT_SYNTHETIC` (28, three coordinate strata) | — | **FAIL 28/28, rate 1.0** |

48 of 48. First time in the programme this guard has had a denominator.
The movement is `CANNOT_CHECK -> FAIL`: a subtraction, not a repair.

Secondary `PARENT_GOLD` scoring (same decisions, parent's adjudicated relation as
gold): `P3.FALSE_SCIENTIFIC_MERGE` for A0 goes **12/12, 8/8, 28/28, rate 1.0** —
FAIL. The paper's PASS on that guard (0 of 6, 0 of 14) holds only under full
observation.

### Gates

| gate | outcome | number |
|---|---|---|
| G1 CONSTRUCTION | PASS | C1–C5 hold on all three probes |
| G2 CHANNEL_OPENED | PASS | 12 opportunities where there were 0 |
| G3 FAILURE_ON_REAL_CASES (primary) | PASS | rate 1.0 >= 0.90 |
| G4 HELD_OUT | PASS | 1.0 and 1.0 |
| G5 MINING_YIELD | **CANNOT_CHECK** | (a) 0 intact failures to mine -> CANNOT_CHECK; (b) 48/48 probe over-resolutions have an EMPTY discriminating-coordinate set -> PASS |
| G6 HARM_A1 | **CANNOT_CHECK, vacuous** | A1 could fire on 0 of 120 intact pairs; its 0 changes is a structural zero |
| G7 COST_A2 | reported | A2 changes **32/32, 32/32, 56/56** intact decisions and destroys **every** correct answer in all three atlases |
| G8 NOVELTY | **FAIL by construction** | `observation_status` is constant on fully observed pairs |

Overall: **FAIL**. Verdicts: `CHANNEL_OPENED_FAILURE_DEMONSTRATED`,
`FAILURE_CARRIES_TO_HELDOUT_STRATA`,
`T5_NOT_DISCHARGED__CANDIDATE_IS_NOT_A_NEW_IDENTITY_AXIS`.

### Two honest negatives worth naming

1. **G5(a) is CANNOT_CHECK, not PASS.** There are zero false merges and zero
   false splits on the intact corpora, so the "prove the coordinate unnecessary"
   branch of T5's unblock has nothing to prove anything about. Reporting it as
   "no failure demanded a new coordinate, therefore none is needed" would be the
   vacuous-guard fallacy verbatim. The gate refuses.
2. **G6 declares my own harm guard vacuous.** A1 changes 0 intact decisions —
   but only because no intact pair has a one-sided absence. That zero is
   structural and cannot be cited as evidence A1 is safe.

A1 and A2 score 0/48 on the over-resolution guard. **That is true by
construction** — they abstain on exactly the property the probe injects — and it
licenses nothing. A2's real number is G7: the strict reading destroys 100% of
every atlas.

## Next: tests + mutation checks, then RESULTS.md.

---

## Step 4 — tests and mutation checks (2026-08-21)

`tests/unit/study/p3/test_partial_observation_probe.py`, 36 tests, all green.
Full P3 lane re-run: `tests/unit/study/p3` + the four `test_p3_*` modules =
**239 passed**. `ruff check` clean on both new files.

`main(argv)` has `argv` required (no default) and a `__main__` guard;
`test_main_requires_argv_and_is_invocable_as_a_subprocess` asserts `TypeError`
on `main()` and then actually invokes the module with `subprocess.run`.
The artifact reproduces byte-identically on re-run.

### Mutation checks — each change applied, test run, then reverted from a backup

| # | mutation | tests that went red | reverted |
|---|---|---|---|
| M1 | A1 harm gate returns `PASS` on a zero denominator instead of `CANNOT_CHECK` | `test_the_a1_harm_gate_declares_itself_vacuous` | yes |
| M2 | mining gate returns `PASS` on an empty failure set | `test_the_mining_gate_cannot_check_an_empty_failure_set` | yes |
| M3 | `discriminating_coordinates` drops the observedness conditions | `test_a_one_sided_absence_discriminates_nothing`, `test_every_probe_over_resolution_lacks_a_discriminating_coordinate`, +1 | yes |
| M4a | C2 detection neutralised (both assignments flipped to `True`) | `test_a_probe_silenced_on_both_sides_is_rejected` | yes |
| M4b | `construction_precondition` always reports `passed: True` | that test + `test_an_empty_probe_fails_c1_rather_than_passing_quietly` | yes |
| M5 | `max_violation_rate` changed `0.0 -> 0.1` after the freeze | `test_runner_digest_matches_the_frozen_twin` | yes |
| M6 | novelty gate returns `PASS` | `test_novelty_fails_by_construction_and_t5_is_not_discharged`, `test_the_campaign_is_a_failure_overall` | yes |
| M7 | `build_probe` silences the mirror side too | 25 tests, incl. all `TestArmsAreTotal` | yes |
| M8 | `A0_orion_current` abstains instead of calling `compare_meaning` | 6 tests | yes |

Note on M4: the first attempt (disabling only the leading `if` of the C2 block)
stayed green, because the `elif` arm still caught that particular malformation.
That is a redundant check, not a hole; M4a disables C2 entirely and the test
goes red, so the test is sensitive to C2 being switched off.

After every mutation the file was restored from `scratchpad/probe.bak` and the
suite re-confirmed green.

## Step 5 — one incidental observation, not repaired

`src/orion/study/metrics.py:142` and `:184` compute
`false_merges / total if total else 0.0` and `false_splits / total if total
else 0.0`. That is the same `VACUOUS_GUARD_ZERO_DENOMINATOR` shape the
`identity_opportunity` docstring already documents for
`p3_public_reference._rates`, in a module the docstring does not name. It is
**not** repaired here: changing it would alter numbers in committed P3 results,
which rule 3 forbids, and `orion.study.p3.identity_opportunity` already exists
as the correct replacement path. Recorded so it is on the register.

---

## FINAL STATE

- Freeze: `papers/orion-13-global-knowledge-portrait/protocol/P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md`
- Twin: same stem, `.json`, `parameters_sha256 = 28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691`
- Instrument: `src/orion/study/p3/partial_observation_probe.py`
- Result: `papers/orion-13-global-knowledge-portrait/evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-21.json` (exit 3, FAIL)
- Probe cases: `papers/orion-13-global-knowledge-portrait/evidence/partial-observation-t5/PROBE_CASES_2026-08-21.jsonl` (48)
- Tests: `tests/unit/study/p3/test_partial_observation_probe.py`
- No committed P3 result, receipt, atlas or evidence artifact was modified.
  `orion.knowledge.semantics` was not modified.

**P3-U-T5 is NOT discharged.** The ledger blocker should stay closed, with its
reason replaced: not "nobody mined the failures" but "there are no ORION
failures to mine, and the one channel that could produce a candidate now
demonstrably fails at rate 1.0 while yielding a candidate that is not a new
identity axis."
