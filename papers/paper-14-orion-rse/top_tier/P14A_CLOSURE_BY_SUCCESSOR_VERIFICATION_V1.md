# P14A closure-by-successor verification V1 (NR-11)

**Programme:** #977 · **Lane:** NR-11 (negative-revival backlog) · **State:** `VERIFIED_CLOSED_BY_SUCCESSOR`
**Machine record:** `P14A_CLOSURE_BY_SUCCESSOR_VERIFICATION_V1.json` · **Checker:** `verify_p14a_closure_by_successor_v1.py` (exit 0 = verified)

## Question

The backlog row NR-11 records the P14A negative as a gate defect — "both bars exceeded
statistic supremum" — closed by the P14C successor. This lane verifies the three closure
claims independently on the frozen artifacts: (1) the bars really exceed the statistic's
sampling support; (2) P14C is a successor for the same claim scope, not a different claim;
(3) the remaining external dependency (R1–R3) has a concrete internally-executable
substitute under the backlog's workaround protocol.

## 1. Bar vs supremum — VERIFIED UNATTAINABLE

Both failed P14A gates read ONE quantity q: the prevalence of the single fact state on
which MULTI_REVIEW disagrees with gold. State enumeration over all 256 fact combinations
confirms the discriminating state is unique (positive ∧ valid ∧ ¬donor_owned ∧
¬interaction_only ∧ live_negative_history ∧ ¬material_new_evidence), that ORION_RSE_FULL
returns gold on all 256 states (divergence 0), and that exactly 3 states are promotable.
Because MULTI_REVIEW's false-promotion rate and the full contract's accuracy gain both
equal q, both bars gate the same statistic.

q is a product of independent affine factors in the eight post-mixture rates
(`0.5·sampled + 0.5·base` over the declared uniforms), so its extrema over the declared box
sit at corners. Verified by exhaustive 256-corner enumeration plus 200,000 interior
samples (all interior q within [infimum, supremum]):

| Gate | Bar | Supremum | Margin (bar − sup) | Verdict |
|---|---|---|---|---|
| `strongest_baseline_false_promotion_ge_0_05` | 0.05 | 0.04232587750858594 | +0.007674 | UNATTAINABLE |
| `accuracy_gain_ge_0_08` | 0.08 | 0.04232587750858594 | +0.037674 | UNATTAINABLE |

Infimum 0.009085200732011248; realized shipped-run value 0.018375 (inside the interval,
as required). The supremum and infimum equal, to float equality, the
`declared_statistic_support` recorded in `P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json` —
two independent computations agree. No admissible world the freeze admits could have met
either bar: the published NOT_MET is a measurement that could not be taken.

## 2. P14C successor — SAME SCOPE, DELTAS DISCLOSED

P14C re-registers the same governance question with the circularity repaired rather than
the question changed:

- **Same statistic family:** P14C's primary outcomes are again strongest-baseline false
  promotion and accuracy gain over that baseline; the P14A bars are re-read verbatim
  (0.05 / 0.08) on the P14C register (`P14_ACTIVE_CLAIM_AUTHORITY_V1.json` records
  `p14a_thresholds_unchanged`).
- **Bars now attainable AND refutable:** RETAIN_NEGATIVE prevalence is exactly 4/28 =
  0.142857 in every admissible table; MULTI_REVIEW errs on exactly those 4 cases
  (RN-01..RN-04); so false promotion = accuracy gain = 0.142857 ≥ 0.05 MET and ≥ 0.08 MET.
  The 0.08 bar is strictly inside the reachable subject-gain interval [0.0, 0.142857]:
  ABLATE_DONOR / ABLATE_INTERACTION / ABLATE_NEGATIVE_HISTORY sit at 0.0 — the successor
  can fail. The 0.05 precondition is structural (fixed by the register), which is a
  disclosed limitation, not a hidden one.
- **Circularity repair verified:** the policy evaluates `facts_only(case)`, which strips
  {case_id, stratum, gold_disposition, rationale}; 28 cases across 7 strata × 4;
  zero gold leaks into policy inputs; independent policy implementation; canonical
  digest `74032348…` reproduces byte-for-byte on this platform, exit 0,
  terminal `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`.
- **Scope delta (disclosed in the authority file):** P14C's supported claim is
  **conformance** over the frozen 28-case register — a controlled-governance
  conformance result. It is NOT a superiority claim over external systems; no
  superiority claim is currently registered. That is exactly what the backlog row
  requires ("remaining work only if a superiority claim is re-registered").

## 3. P14A replay fidelity — decision layer stable, byte digest platform-pinned

Replaying `run_p14a_controlled_governance_v1.py` end-to-end (scratch OUT, seed
2026082114): exit 1, terminal `…SUPERIORITY_GATE_NOT_MET`, and every summary metric equal
to the receipt (MULTI_REVIEW fp 0.018375, acc 0.981625; ORION_RSE_FULL perfect). The
full-result byte digest, however, comes out `eda969e6…` on this platform (Python
3.13.12 / arm64) against the receipt's `3ac625b7…`; the in-repo fidelity anchor
`orion.study.p14.governance_gates.bench()` — whose payload is deeply equal to the
runner's on this platform — returns the same `eda969e6…`. Attribution: the full-result
bytes embed the per-family post-mixture rate floats, whose low bits follow the
executing platform's numpy float path; the adjudication's `committed_digest_reproduced:
true` was established on the pinning platform (and `tests/unit/study/p14/
test_p14_governance_gates.py:66` pins it there). Decision-level counts and summary
metrics are platform-stable. Consequence for this lane: the closure verdict gates on the
decision layer, with the byte-digest platform-pinning recorded as a disclosed artifact,
not excused silently. (P14C — the active authority — reproduces byte-for-byte here.)

## 4. R1–R3 external status and substitute plan

- Co-primary promotion condition: `PENDING_EXTERNAL` (frontier-agent execution and
  independent human adjudication have not run).
- P14D preflight terminal: `P14D_EXTERNAL_ACQUISITION_BLOCKED`, `execution_authorized:
  false`, eight missing custody artifacts.
- Under the backlog's workaround protocol (externals substituted, boundary disclosed,
  claim bounded to the substitute):

| Round | External dependency | Substitute | Boundary label |
|---|---|---|---|
| R1 frontier-agent | ≥2 external frontier agent systems execute the frozen 67-packet contract | third-party public reference implementations re-hosted frozen in our harness as donor baselines (external = not authored by us, executed by us) | `PUBLIC_REFERENCE` |
| R2 adjudication | independent blinded human experts | independent frozen checker + label-blind cross-model adjudicator under a pre-registered rubric | `MACHINE_BLINDED` |
| R3 longitudinal | external systems re-run on round-pair subset | same PUBLIC_REFERENCE systems on the frozen round-pair subset, negative-history partition withheld vs present | `PUBLIC_REFERENCE` |

**Next executable step (R1 entry):** select ≥2 public reference research-decision systems
(e.g. from the donor set in `P14_EXTERNAL_FRONTIER_DELTA_2026-08-23.md`), freeze their
pinned revisions + adapter digests into the harness, execute the frozen 67-packet
contract from `external_v1/pilot`, and register the resulting claim as
`PUBLIC_REFERENCE`-bounded. R2's frozen rubric + cross-model adjudicator must be
registered before any R1 output is unblinded.

## Verdict

`closure_by_successor_verified: true` — bars genuinely exceed the statistic supremum
(both unattainable by construction of the declared support), P14C is a same-scope
successor with disclosed deltas and byte-reproducible on this platform, and R1–R3 are
blocked externally with backlog-conformant substitutes assigned. NR-11 closes under
backlog criterion (c): superseded by a landed successor claim.
