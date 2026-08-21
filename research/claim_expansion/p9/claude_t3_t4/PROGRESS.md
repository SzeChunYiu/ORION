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

1. The attacks are *named* in `papers/paper-09-structured-epistemic-learning/successor/P9_U_MANUSCRIPT.tex`
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
  `papers/paper-09-structured-epistemic-learning/protocol/` BEFORE any arm runs.
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
- `papers/paper-09-structured-epistemic-learning/protocol/P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.md`
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
