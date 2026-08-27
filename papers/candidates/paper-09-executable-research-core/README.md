# ORION-19 candidate — Executable Research Core

**Status:** MERGED INTO P8/PROGRAMME / PUBLIC DISCRIMINATOR PASSED / NO STANDALONE MANUSCRIPT
**Shared lane:** `../orion-learning-machine/`

## Research question

Can an agent accumulate *capability* — named mechanics, a competence map over where they work, learned state-effect contracts, and retained failure experience — such that routing improves measurably, **without any of that accumulation becoming authority to act**?

## Candidate contribution

`LearningMachine` (`../orion-learning-machine/framework/orion_learning_machine/runtime.py`) separates four responsibilities and lets none of them authorize an effect:

| Component | Holds |
|---|---|
| `library` | named mechanics with donor lineage |
| `competence` | where admitted success/failure evidence supports use |
| `contracts` | empirical state-effect regularities induced from transitions |
| `ledger` | append-only retained experience, including failures and `UNKNOWN` |

The module states the boundary in its own docstring: *"None of those components can authorize an external effect. Execution always passes through an authority callback owned outside ORION-19."* That is the same capability/authority split ORION-18 formalizes, instantiated as running code rather than as a calculus.

## Evidence that exists

### Public discriminator — ASlib `SAT11-HAND-ALGO`

The protocol was committed before public-outcome access and binds exact ASlib
source digests plus the scenario-provided outer folds. On 296 instances, 115
features and 15 algorithms, FAILURE_AWARE_RF reduced attempts on 77
VBS-unsolved instances by **0.7143 absolute** (paired bootstrap 95% CI
0.6104–0.8182) while retaining **0.9645** of RF_ROUTER's solved instances. It
paid the visible cost of lower solve rate and higher mean PAR10.

Two complete runs produced byte-identical JSON with SHA-256 `8246d007…`.
Reproduce with `benchmark/run_aslib_v1.py`; the exact protocol, public inputs,
source record, full-precision result and hostile tests live under `benchmark/`
and `results/`.

Two experiments, both **byte-identical on re-run** (`SEED=20260818`), with outputs committed under `../orion-learning-machine/results/`.

### Phase 0 — solver ecology (`PHASE0_SOLVER_ECOLOGY.txt`)

A learned schedule matches the best fixed solver's success at roughly a third of the effort, and holds under distribution shift:

| Regime | Best fixed | Learned schedule | Oracle |
|---|---|---|---|
| IID holdout | `companion` 0.953 @ effort 56.2 | **0.953 @ 17.9** | 0.953 @ 5.9 |
| Distribution shift | `companion` 0.957 @ effort 58.2 | **0.957 @ 22.1** | 0.957 @ 8.1 |

Competence AUC 0.993–1.000 (IID) and 0.978–0.999 (shift). First-choice success degrades under shift (0.937 → 0.880) while scheduled success does not — the routing recovers what the first guess loses.

### Phase 1 — mechanic composition (`PHASE1_MECHANIC_COMPOSITION_V2.txt`)

Across three regimes (scale, length, mixed), `failure_aware` composition **matches the oracle on every metric**:

| Arm | solve_rate | effort (mixed) | early_abstain_opaque | effort_opaque | false-commit status |
|---|---|---|---|---|---|
| `frequency` | 0.642 | 48.7 | 0.000 | 15.0 | NOT MEASURED |
| `blind` | 0.642 | 31.5 | 0.000 | 12.0 | NOT MEASURED |
| `imitation` | 1.000 | 18.0 | 0.000 | 12.0 | NOT MEASURED |
| `failure_aware` | 1.000 | 18.0 | **1.000** | **0.000** | NOT MEASURED |
| `oracle` | 1.000 | 18.0 | 1.000 | 0.000 | NOT MEASURED |

**Read this carefully.** `imitation` and `failure_aware` are indistinguishable on solve rate and effort — both reach the ceiling. The whole difference is on *opaque* tasks: `failure_aware` abstains immediately at zero effort, `imitation` spends 12. So the claim supported here is about **knowing when not to try**, not about solving more. Anyone quoting "matches oracle" without that qualification is overstating it.

Phase 1 has no commit event and did not prospectively define false commitment.
The delivered V1 runner hard-coded `false_commit=0.000`; that field is rejected,
not interpreted as an observed null. The V2 result reports
`false_commit_status=NOT_MEASURED` for every arm and a hostile test prevents the
numeric claim from returning.

## Ownership boundary

- **ORION-18** owns the authority calculus. ORION-19 supplies capability and routes it; it never upgrades capability into authority.
- **ORION-11** owns responsibility-typed reframing and dependency-directed reopening.
- **ORION-15** owns protected self-change and no-self-promotion.
- ORION-19 claims none of those. Its object is the executable core that accumulates capability under those constraints.

After constructive nearest-work saturation, that object is retained as ORION-18's
executable/public empirical companion rather than a ninth manuscript. See
`SATURATION_LEDGER_2026-08-18.md`, `CLAIM_LEDGER.md`,
`MERGE_DISPOSITION.md`, and `JOURNAL_READINESS.md`.

### Explicit nonclaims

ORION-19 does not claim novelty for algorithm selection, algorithm portfolios, meta-learning, macro/option discovery, learned schedulers, or competence modelling. Each is a mature field and the phase-0 result is a standard portfolio-routing shape. What is being proposed is the *separation* — accumulation that structurally cannot become permission — not the routing itself.

## Deliberate limits

- **No standalone manuscript.** The terminal is an evidenced merge, not an
  unfinished paper.
- **No AutoFolio-class baseline.** This blocks selector-superiority language and
  is a named reopen condition.
- Phase 0 and phase 1 remain synthetic. The public ASlib discriminator is a
  single bounded scenario, not cross-domain evidence.
- Routing and abstention cannot authorize execution; ORION-18 owns that boundary.
- External authority and multi-scenario selector superiority remain
  `CANNOT_CHECK` from ORION-19 alone and are not promoted by the merge terminal.

## Reproduce

See `../orion-learning-machine/REPRODUCE.md`.
