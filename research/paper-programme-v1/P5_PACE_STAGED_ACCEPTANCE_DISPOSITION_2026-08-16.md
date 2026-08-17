# ORION-P5 PACE / staged-acceptance disposition — 2026-08-16

**Issue:** #102  
**Authority:** nearest-work/protocol decision only; no empirical PASS.  
**Decision:** `ADAPT`.

## Expert lenses

1. **Sequential-testing lens.** PACE (`arXiv:2606.08106`) turns repeated noisy incumbent-vs-candidate decisions into paired anytime-valid/e-process tests and directly targets adaptive false commits. This mechanism is prior art and cannot be claimed as a P5 novelty.
2. **Self-evolution lens.** SEA (`arXiv:2607.00871`) independently uses anytime-valid certificates, while Verifier-as-Gatekeeper (`arXiv:2608.05810`) shows that pre-commit gating and contamination prevention are already explicit self-evolution mechanisms.
3. **Governance/fresh-transfer lens.** P5 still differs only at the composition level: a candidate cannot advance from replay success to promotion without independent fresh-transfer evidence, protected evaluator custody, retained negative/null/harmful history, and a host-only authority terminal.

## Disposition

`PACE = ADAPT`.

- **Adopt as nearest-work pressure:** anytime-valid sequential acceptance is explicitly outside standalone P5 novelty.
- **Adapt as a matched baseline:** compare against a PACE-style acceptor under the same candidate/evaluator budget whenever a faithful runnable implementation/configuration can be frozen.
- **Adapt as an optional within-stage statistic:** when a REPLAY/FRESH/PROTECTED stage repeatedly compares paired noisy scores under adaptive proposals, a prospectively frozen anytime-valid/e-process rule (or justified stronger equivalent) may be used. Its exact error budget/configuration must be bound before outcome access.
- **Do not substitute it for P5 governance:** statistical evidence that a candidate improved on one evaluation stream does not supply causal licensing, fresh-transfer independence, protected custody, negative-history integrity, or promotion authority.

## V2 residual after absorption

The candidate V2 residual is the ordered, non-compensatory composition:

`STATIC -> REPLAY -> FRESH -> PROTECTED`

with these rules:

- known harm or `FAIL` vetoes immediately, including out-of-order later-stage evidence;
- absent harm/FAIL, any `CANNOT_CHECK` blocks;
- missing stages cannot be averaged away;
- positive replay gains cannot compensate fresh/protected harm;
- all failed/harmful/null/uncertain candidate revisions remain append-only;
- the only positive terminal is `RECOMMEND_HOST_PROMOTION`, never self-merge.

## Scientific consequence

The V2 study must compare this composition not only to V1, direct self-edit and evaluator-only acceptance, but also to current acceptance-focused nearest work (PACE; SEA-like certificates; Verifier-as-Gatekeeper where faithfully runnable). A staged gate may enter the headline claim only if it reduces harmful transfer/false protected acceptance while preserving useful protected improvement within the prospectively frozen margin.

The public V1 protocol remains unchanged. V2 is a separate prospective protocol and remains `CANNOT_CHECK` until the external study runs.
