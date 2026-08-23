# P7 top-tier theory V1 — Scientific Regime Transport

**Programme:** #977  
**Boundary:** this file raises the formal object above generic schema/category/regime transport. Artifact/fact transport mechanisms are donor-owned; P7 owns the conditions for transporting scientific support, closure, obligations and honest stopping.

## T7.1 — regime-change object and preservation ladder

A scientific regime is modeled as

\[
R=(\rho,\mathcal E,G,W,\Sigma,\Omega),
\]

where:

- `rho` is the representation/observation interface;
- `E` is the admissible evidence language/source interface;
- `G` is the objective/responsibility;
- `W` is the world/ontology/measurement assumptions;
- `Sigma` is support semantics;
- `Omega` is the outstanding-obligation/stopping semantics.

A regime change `u:R->R'` may carry artifact/fact values while failing to carry higher scientific coordinates.

For a claim `q`, distinguish:

1. value/fact transport;
2. evidence-meaning transport;
3. support-derivation transport;
4. obligation transport/discharge;
5. scientific closure transport;
6. stopping-terminal transport.

### Non-implication

Fact/value preservation does not imply evidence-meaning preservation. Evidence-meaning preservation does not imply complete support transport. Support transport does not imply that obligations/objectives are unchanged or discharged. Therefore none of these lower levels alone implies closure transport.

### Sufficient closure witness

For a previously closed claim to remain closed after `u`, a transport witness must establish at least:

- the transported claim has the intended identity/content under `rho -> rho'`;
- every load-bearing support derivation is transported or independently replaced;
- evidence meaning/scope/epoch needed by those supports is preserved;
- the target responsibility/objective is unchanged or validly mapped;
- every old obligation remains discharged under the new regime and no newly induced obligation is left open;
- any stopping/coverage premise used for closure remains valid.

Missing any required witness yields `CANNOT_CHECK` or `REOPEN`, not implicit closure.

## T7.2 — sequential transport composition

Let `w01` witness `R0->R1` and `w12` witness `R1->R2`.

The composite closure witness `w02` is valid only when:

1. the codomain interfaces/types of `w01` match the domain interfaces/types consumed by `w12`;
2. every assumption/context coordinate required by `w01` is preserved by `w12` or re-established independently in `R2`;
3. transported support identities compose without silently dropping a load-bearing derivation;
4. obligation mappings compose and no intermediate/new obligation is discarded;
5. any closure/coverage premise is transported through both changes.

Individual local validity is therefore not sufficient for composability. A witness may be correct for `R0->R1` while relying on an `R1` assumption that `R1->R2` invalidates.

### Obstruction rule

If an intermediate assumption needed by the first witness is changed and no replacement witness exists, the correct composite terminal is `REOPEN` or `CANNOT_CHECK` even when both artifact maps are individually well-formed.

## T7.3 — open/censored transport impossibility

Let two post-change worlds `w_closed` and `w_open` induce exactly the same observed evidence/history under the new regime up to time `t`.

- in `w_closed`, the registered route/support universe is complete and no additional relevant evidence exists;
- in `w_open`, an unobserved admissible continuation exists that can change the closure judgment.

Any deterministic terminal using only the shared observed data must output the same decision in both worlds. Therefore no observed-data-only rule can be both sound and complete for distinguishing `CLOSED` from `CONTINUE` across this pair.

A positive closure terminal requires an external coverage/support witness that separates the worlds; otherwise `CANNOT_CHECK`/open continuation is the honest boundary.

This is an indistinguishability result, not a claim that open-world research can never stop.

## Donor absorption after 2026-08-23 refresh

Category-theoretic regime transition and provenance-preserving artifact transport are explicitly donor-owned, including the 2026 categorical self-revising discovery framework recorded in `P7_P9_TOP_TIER_LITERATURE_DELTA_2026-08-23.md`.

P7's higher object is the preservation/non-preservation of scientific closure and obligations *over* such regime mappings.

## Remaining external gate

These theorems do not satisfy the required non-synthetic regime-change evidence. Top-tier promotion still requires protected versioned/formal and research/agent regime changes with donor-complete baselines and independent adjudication.
