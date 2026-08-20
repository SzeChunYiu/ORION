# P10 positive reopen decision V1

Date: 2026-08-20

Branch: `shadow/p10-positive-claim-expansion-20260820`

Base: `a21c65597129494563b962da398da5f4f059fd08` (`main` at reopen)

## Decision

Reopen P10 for a bounded positive claim-expansion experiment. Do **not** reopen or reinterpret the prior A0 responsibility-control null/equivalence lane.

The existing P10 result is already positive on a prospectively frozen cross-module prediction endpoint:

- 457 selected Mathlib files;
- 31 active top-level modules;
- 4,825 recognized theorem/lemma trajectories;
- 16,667 projected tactic-family actions;
- leave-top-module-out Markov accuracy 0.3842;
- leave-top-module-out unigram accuracy 0.2796;
- difference 0.1046;
- module-bootstrap 95% interval approximately [0.0863, 0.1223].

The candidate package also already records deterministic native audit receipts: eight prospectively selected exact files accepted by the named Lean runtime, a planted invalid proof rejected, two complete replays byte-identical, and mutation controls passing.

The present standalone limitation is therefore not absence of a positive effect. It is that the positive source-level recurrence effect has not been shown to survive comparison with native proof-state/dependency representations and a strong graph/state-aware tactic-mining baseline.

## Expert-team disposition

### Methods/reproducibility reviewer

Disposition: **REOPEN**.

Reason: the V2.1 cross-module effect is nonzero with a positive block-bootstrap interval and a frozen evaluation boundary. A stronger nested blocked experiment can be specified without reusing the held-out modules for feature or hyperparameter selection.

Required guard: freeze the incremental-value protocol before native-state outcomes and preserve every null/negative secondary result.

### Lean/mathlib reviewer

Disposition: **REOPEN WITH NATIVE-TRACE REQUIREMENT**.

Reason: the current source projection explicitly cannot represent elaborated goals, local contexts, tactic semantics, or dependencies. A state/mechanism claim is unavailable until these are extracted from the exact native subject.

Required guard: source-text surrogates do not count as native states; runtime/revision/source receipts must fail closed.

### Hostile integrity reviewer

Disposition: **REOPEN WITH LEAKAGE ATTACKS**.

Principal risks:

- module/file/theorem identity leakage;
- future-step/post-state leakage;
- near-duplicate theorem-family contamination across modules;
- selective state availability;
- outcome-guided feature or module removal;
- weakening the comparator after observing results.

Required guard: identity attacker, label shuffle, future-step mutation, receipt substitution, near-duplicate audit, and identical transition support for paired comparisons.

### Publication/claims reviewer

Disposition: **MAXIMIZE BY CLAIM LADDER, NOT BY RELABELING NULLS**.

The strongest currently supported positive rung is coarse cross-module tactic-history transfer. Native-state and structural-transfer language is contingent on the new frozen gate. Standalone novelty additionally requires a faithful strong nearest-work comparator rather than merely citing it.

## Branch/unmerged-work audit

GitHub-visible P10 heads searched before protocol freeze:

- `shadow/p6-p10-integration-2026-08-18`
- `shadow/p9-p10-integration-2026-08-18`
- `shadow/p10-a0-responsibility-control-20260819`

The A0 lane contains an analytic/donor-equivalence disposition and does not supply a positive standalone residual. Repository commit search found the earlier native-audit work already integrated into the candidate package. No GitHub-visible branch named for a P10 native-state/proof-state/dependency experiment was found before this reopen.

This audit cannot see an uncommitted dirty tree on a workstation. Any later-discovered local-only work must be compared chronologically against this frozen protocol; if it contains outcomes observed before the protocol freeze, it may be used as prior/exploratory evidence but not represented as prospectively tested by this protocol.

## Nearest-work rationale

Two primary nearest-work directions motivate the strong comparator:

1. Yang et al., **LeanDojo: Theorem Proving with Retrieval-Augmented Language Models**, NeurIPS 2023 / arXiv:2306.15626: Lean proof-state/premise extraction, retrieval, and difficult generalization splits.
2. Xin et al., **Automated Discovery of Tactic Libraries for Interactive Theorem Proving**, arXiv:2503.24036 (2025): tactic-dependence graphs and reusable tactic discovery, with downstream proof-automation evaluation.

These references make a raw sequential recurrence-only novelty claim too weak. They also make a positive *incremental* result scientifically meaningful if P10 can show that native structural information contributes beyond its already-positive history baseline under a stricter held-out-module boundary.

## Activated experiment

Protocol: `P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md`

Primary question:

> Does native Lean proof-state plus leakage-safe dependency structure improve held-out-module next-action prediction beyond the exact V2.1 tactic-history baseline?

Primary success is locked to a positive paired accuracy delta whose top-module bootstrap 95% lower bound is above zero, lower paired log loss, non-pathological module consistency, and hostile-control clearance.

## Claim disposition

Until new outcomes exist:

- **SUPPORTED:** cross-module coarse tactic-history transfer on the frozen V2.1 subject.
- **NOT YET SUPPORTED:** native proof-state incremental value.
- **NOT YET SUPPORTED:** reusable custom tactic utility.
- **NOT YET SUPPORTED:** superiority over TacMiner-class graph/state mining.
- **NOT YET SUPPORTED:** standalone novelty.

The purpose of the reopen is to earn the highest of those unsupported rungs without changing the gate after outcomes.