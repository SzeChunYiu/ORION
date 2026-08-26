# ORION-23 drift-bounded certificate transport protocol V1

**Programme:** #977
**State:** `FROZEN_BEFORE_EXECUTION`
**Purpose:** execute the semantic-change certificate-transport requirement for the ORION-23 maximum claim: certificates issued in one episode regime must be transported to a shifted regime under an explicit, mechanically checkable transport predicate, with gold dispositions frozen before any arm runs.

## Setting

Verifier-backed CNF certificates (same family as the ORION-23 responsibility-shift protocol and the D2 baseline). An issued certificate binds `(model m, formula digest d(F), epoch e, domain tag, registered support)`. The world moves to a shifted formula `W` (clause added, removed, or strengthened). A transport decision must answer: may the certificate be served for the shifted world without full re-verification, or must it be re-issued (or the request refused)?

## Transport predicate (frozen)

Transport is permitted iff the transport checker, comparing `F` to `W` clause-by-clause, finds the drift bounded:

- `MONOTONE_ADD`: every difference is an added clause, and the stored model satisfies all added clauses (locally verified, literal cost only);
- `MONOTONE_DROP`: every difference is a removed clause that was never in the registered support's justification set (justification = the unit clauses fixing variables present in the stored model's certification), and the stored model still satisfies `W` by construction (dropping clauses cannot violate a model).

Any mixture of add+drop, any strengthened (modified) clause, or any added clause violating the stored model → transport denied → re-issue via the raw tier. `MONOTONE_DROP` cases where a removed clause IS in the justification set also deny (the certificate's evidential basis changed).

## Arms (frozen)

- `UNCONDITIONAL`: serve compact whenever task type is CERTIFY and provenance currency matches (ignores drift entirely);
- `SIGNATURE_ONLY`: serve compact iff `d(F) == d(W)` (pure signature equality; any drift forces re-issue);
- `CONDITIONAL_DRIFT_BOUNDED`: serve compact iff the frozen transport predicate above returns PERMIT, with local verification of added clauses; else re-issue;
- `ALWAYS_RE_ISSUE`: never transport (safety/cost ceiling).

## Case grid (60 cases, gold frozen)

Deterministic generator seed `20261407`. 5 variables, 20 cases per stratum:

| stratum | drift class | gold disposition |
|---|---|---|
| `REDUNDANT` (20) | added clause entailed by F (model set unchanged), stored model satisfies it | TRANSPORT_SOUND |
| `CONFLICTING` (20) | added clause violated by stored model (model set shrinks; if SAT, exactly one alternate remains) | TRANSPORT_DENY → re-issue; correct answer = alternate model or UNSAT |
| `MIXED` (20) | added entailed clause + removed justification unit clause (or added+removed mixture / strengthened clause, per frozen per-case recipe) | TRANSPORT_DENY (justification changed / non-monotone mixture) |

Gold per case: `gold_transport` ∈ {TRANSPORT_SOUND, TRANSPORT_DENY}, `stored_model_satisfies_shifted`, `correct_model` (a model of `W` if SAT, else `null` + `unsat: true`), and for REDUNDANT cases `model_set_preserved` (verified by enumeration in the independent checker).

## Endpoints (frozen)

1. `wrong_transport_count`: episodes where the arm transported an UNSOUND certificate or refused a SOUND transport (both directions count, reported separately as `unsound_transport` / `needless_reissue`);
2. verifier-correct episode count (exact CNF verification of the final answer against `W`);
3. mean literal reads per episode per arm;
4. solver invocations.

## Frozen positive terminal

`P13_CERT_TRANSPORT_V1_SUPPORTED` requires ALL of:

1. `CONDITIONAL_DRIFT_BOUNDED`: `unsound_transport == 0` AND `needless_reissue == 0` AND verifier-correct `60/60`;
2. `UNCONDITIONAL`: `unsound_transport >= 1` on CONFLICTING (transport without drift check is unsound);
3. `SIGNATURE_ONLY`: `needless_reissue >= 1` on REDUNDANT (signature equality refuses sound transports — the missed-efficiency witness);
4. `ALWAYS_RE_ISSUE`: verifier-correct `60/60` and mean literal reads strictly greater than `CONDITIONAL_DRIFT_BOUNDED` on the REDUNDANT stratum (the cost of refusing sound transports).

If any item fails, the result is retained as evidence against this protocol and no parameter is retuned.

## Hostile checks

- the transport checker never receives the precomputed gold; it sees only `F`, `W`, the stored record;
- `SIGNATURE_ONLY` sees the same inputs as `CONDITIONAL_DRIFT_BOUNDED` (no information asymmetry);
- model-set preservation and exact-one-alternate invariants verified by brute-force enumeration in the independent checker, not by the generator's own bookkeeping;
- no wall-time or hardware-dependent quantity enters any endpoint;
- UNSAT worlds (if any CONFLICTING case renders W unsatisfiable) have gold `unsat: true` and no arm may return a model.

## Authority boundary

A positive establishes, at bounded verifier-backed CNF scope, that (i) unconditional certificate transport is unsound under conflicting drift, (ii) signature-equality transport forfeits sound transport efficiency, and (iii) a clause-diff drift bound with local added-clause verification is exactly correct on this grid and cheaper than re-issue. It does not establish transport under formula classes beyond CNF, under adversarially chosen drift, or in real agent workflows; those remain open strengthenings.
