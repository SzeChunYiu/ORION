# A5 — Exact input contract

`scientific_authority_delta = NONE` · detail file for
[`../THEOREM_PROOF_AUDIT_V1.md`](../THEOREM_PROOF_AUDIT_V1.md)

**Statement audited** (`PAPER_THEOREM_PACKAGES_V1.md:455-457`, proof
`PAPER_THEOREM_PROOFS_V1.md:243`): origin-only selection supports a
family-level method claim **only when** the selected semantic primitive
solves prospectively hidden targets sharing the certified obstruction,
without access widening.

**Assessment.** Stated as a *necessary condition on evidence*, this is sound
and correctly scoped. The proof explicitly limits itself — "does not
establish transfer outside family" — which is good practice and should
survive verbatim into the manuscript.

---

## The contract is the strongest artifact in the paper

The zero-execution input audit is exact, traceable, and needs no empirical
support to stand. From
`research/orion-epistemic-state-v1/results/P10-DES-01/PRIMARY_RESULT_V1.json`:

| Field | Value |
|---|---|
| `cases_executed` | `0` |
| `run_cells_executed` | `0` |
| `cannot_check_rows` | `480` |
| `censored_rows` / `crashed_rows` | `0` / `0` |
| `case_denominator` | `480` |
| `domain_denominator` | `4` (Lean, SyGuS, IPC, code) |
| `arm_denominator` | `9` |
| `seed_denominator` | `3` |
| `known_method_control_denominator` | `80` |
| `planned_run_cell_denominator` | `12,960` |

Terminal: `P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT`. Nothing found in
this pass contradicts any of it. Establishing *the exact input contract
required to distinguish search, composition and genuine method-language
expansion* is a legitimate formal contribution, and it is the contribution
the Wave-2 disposition assigns to this paper.

The domain/source/licence layer of that contract is separately frozen in
`protocol/P10_DOMAIN_SOURCE_FREEZE_V1.json` with checker
`protocol/check_p10_domain_source_freeze_v1.py`. `README.md` correctly
states that the 100-tasks-per-domain and 80-control figures are "committed
minimums, not selected or executed counts", and that the per-task
enumeration is `NOT_POPULATED`. That distinction must not be blurred in the
rewrite.

## G-12 (major) — the donor-conservativity conjunct is nowhere defined or proved

`TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md:23` states: "invention
requires **donor conservativity** plus a hidden, transferable strict
extension."

Neither `PAPER_THEOREM_PACKAGES_V1.md` nor `PAPER_THEOREM_PROOFS_V1.md`
defines or proves anything about donor conservativity for P10. The proof of
P10-T5 addresses transfer only. The conjunct is imported from the
donor-frontier apparatus in
`research/orion-epistemic-state-v1/DYNAMIC_EPISTEMIC_STATE_CALCULUS_V1.md`,
whose own theorem programme (`DES-T0..T15`, lines 113-136) is likewise
headline-only — statements with no proofs in that file. `ORION-20-T5` thus
rests on an unproved dependency in another lane.

## Preserved adverse records this object depends on

These are authority-bearing and must not be softened anywhere in the
rewrite:

- `top_tier/P10_NATIVE_LEAN_CANNOT_CHECK_HANDOFF_V1.md` —
  `CANNOT_CHECK_NATIVE_STATE_COVERAGE`: 457 files traced, 11,842 candidate
  transitions, **0** satisfying the frozen eligibility contract. Explicitly
  not a timeout and not evidence that native proof state is unhelpful.
- The 480 `CANNOT_CHECK` rows above.
- `top_tier/P10_MODULE_NEGATIVE_REVIVAL_RECEIPT_V1.md` — the Control and
  CategoryTheory module negatives, re-attributed to measurement resolution
  rather than mechanism failure, with the CategoryTheory `calculation`
  context retained as a genuine localized failure.
- `manuscript/sections/03-immutable-negative-history.tex` — the four
  regimes in which no invention claim is permitted.
