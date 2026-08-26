# ORION-23 donor-complete provenance-tiered baseline protocol V1

**Programme:** #977
**State:** `FROZEN_BEFORE_EXECUTION`
**Purpose:** execute the donor-complete comparator requirement (common gate B) for the ORION-23 maximum claim by implementing the strongest form of the D2 donor — provenance-aware tiered agent memory (ICLR 2026, see `P13_NEAREST_WORK_REFRESH_2026-08-23.md` disposition COMPOSE) — as a frozen head-to-head arm against the responsibility-carrying state (RCS) policy on identical episode streams.

## Donor-complete D2 specification (frozen, strongest form)

Two-tier memory. The compact tier stores records `(model m, formula digest d(F), issue epoch e, grounding grade G=MAX, support tag "certify-vs-d(F)")`. The raw tier stores the full current formula and solver.

Two donor mechanisms are implemented, in increasing strength:

- `D2_CORE` — provenance-currency tiering: serve compact iff `record.epoch == world.checkpoint_epoch` (else raw re-verify). This is the literal donor axis: tier by provenance currency and grounding.
- `D2_PLUS` — demand-graded tiering, the strongest published reading: additionally map each request to a grounding-demand grade by **task type** (`CERTIFY` on a verifier-issued record has LOW grounding demand because the record's grounding grade is MAX; raw construction has HIGH demand). Serve compact iff provenance current AND `G >= demand`.

Also run `ALWAYS_RAW` (safety/cost ceiling), `RCS` (responsibility-registered reuse with epoch-matched local re-verification), and `COMPOSED` (D2_PLUS tiering plus RCS responsibility registration — the two-dimensional product named by the refresh's upward move 1).

## Why D2_PLUS is not a strawman

D2_PLUS is given every advantage the donor architecture admits: it re-validates on every announced epoch bump, it grades grounding demand, and its records are verifier-issued with maximal grounding. The single structural fact it lacks: its axis is a **grounding/currency scalar over task types**, so it cannot consume the identity of the requested obligation. Episodes where the requested obligation differs from the registered one while task type, grounding grade, provenance currency and confidence all remain unchanged are outside its decision surface by construction, not by weakening.

## Domain and episode grid

Verifier-backed CNF, same frozen family as `P13_VERIFIER_RESPONSIBILITY_SHIFT_PROTOCOL_V1.md`: 5 variables, base formula = unit clauses fixing four variables, one registered variable free, exactly two satisfying models. Deterministic generator seed `20261307`. 12 frozen cases per cell, 4 cells:

| cell | requested obligation | world formula | checkpoint epoch | record provenance |
|---|---|---|---|---|
| `A_SUPPORTED_CURRENT` | certify-vs-F (registered) | F (unchanged) | == record epoch | current |
| `B_CHANGED_CURRENT` | certify-vs-F' (NOT registered; F' = F + unit clause excluding stored model, exactly one alternate model remains) | F' | == record epoch (change unannounced to provenance view) | current |
| `C_SUPPORTED_STALE` | certify-vs-F (registered) | F + redundant clause (model set unchanged) | > record epoch (announced bump) | stale |
| `D_CHANGED_STALE` | certify-vs-F' (NOT registered) | F' + redundant clause | > record epoch | stale |

Cell B is the responsibility-axis witness; cell C is the provenance-axis witness where the donor is correct. The `B_CHANGED_CURRENT` modeling assumption — a semantic change with no announced checkpoint bump — is the donor-faithful between-checkpoints regime: the donor trusts provenance-current records between explicit re-validation epochs. Reducing the checkpoint interval to zero degenerates D2 to `ALWAYS_RAW` cost (reported).

## Decision rules (frozen)

- `D2_CORE`: compact iff `record.epoch == checkpoint_epoch`; else raw re-verify then answer from current formula.
- `D2_PLUS`: compact iff current AND demand(CERTIFY)=LOW; else raw re-verify.
- `RCS`: compact iff requested obligation digest is in the registered support set AND epochs match; on epoch mismatch alone, local re-verification of the stored model against only the added clauses; on obligation mismatch, verify stored model against current formula and re-solve if violated.
- `COMPOSED`: D2_PLUS tiering with the RCS obligation-registration gate substituted for the task-type demand gate.
- `ALWAYS_RAW`: always verify against full current formula and answer from a model of it.

## Resource accounting (literal reads; no invented multipliers)

- compact reuse: certificate payload = assignment literals (5) + 1 digest token = 6;
- local re-verification: literals of added clauses only;
- raw re-verification/re-solve: literals of the full current formula.
Solver invocations reported as separate integer counts.

## Primary endpoints (frozen)

1. `unsupported_reuse_count`: episodes answered from compact state under an obligation absent from the record's registered support;
2. verifier-correct episode count (exact CNF model verification);
3. mean literal reads per episode per arm;
4. solver invocations.

## Frozen positive terminal

`P13_D2_DONOR_BASELINE_V1_SUPPORTED` requires ALL of:

1. `D2_PLUS` and `D2_CORE` each commit >= 1 unsupported reuse on `B_CHANGED_CURRENT`;
2. `RCS` and `COMPOSED` verifier-correct `48/48` with `0` unsupported reuse;
3. `COMPOSED` mean literal reads per episode `<=` both `D2_CORE` and `D2_PLUS`;
4. `ALWAYS_RAW` verifier-correct `48/48` (sanity ceiling).

If any item fails, the result is retained as evidence against this protocol and no parameter is retuned.

## Hostile checks

- stored compact record never contains the current world formula or added clauses;
- obligation identity (requested formula digest) is present in the request for every arm; `D2_*` arms structurally ignore it, `RCS`/`COMPOSED` consume it;
- redundant-clause cell C changes no model set (verified by enumeration in the independent checker);
- exactly one alternate model remains in every F' (verified by enumeration);
- epoch bump visibility is the only difference between the B and D worlds;
- no wall-time or hardware-dependent quantity enters any endpoint.

## Authority boundary

A positive establishes, at bounded verifier-backed CNF scope, that (i) the donor-complete provenance-tiered product in its strongest demand-graded form performs unsupported reuse under responsibility change with provenance continuity, (ii) the responsibility-registration axis is not reducible to the provenance/grounding axis, and (iii) their composition dominates both. It does not establish the research-agent-scope external authority gate, real workflow deployment, or transport under arbitrary semantic change classes. The real-data (digits) replication of the D2 arm remains open strengthening.
