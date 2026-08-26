# ORION-16–ORION-18 formal-assumption audit V2

**Date:** 2026-08-17  
**Authority:** adversarial mathematical review; not a novelty or publication terminal  
**Scope:** additive audit of the current V1 formal cores on draft PR #348

## 1. Executive finding

The current ORION-17 and ORION-18 formal cores already state their main impossibility, transport, anti-laundering and revocation claims with appropriately explicit premises. The material defect found in this audit is in the **ORION-16 minimal-reopening theorem boundary**, plus one assumption that should be made explicit in the ORION-16 commutation theorem.

This addendum therefore does not replace the V1 formal cores. It narrows two ORION-16 claims and adds outcome-executed contract suites for ORION-17/ORION-18.

## 2. ORION-16 defect A — graph soundness does not by itself imply minimal reopening

### V1 pressure point

ORION-16 V1 defines dependency soundness as an over-approximation condition: every semantic support whose change may affect a certified claim is represented by an ancestor path in the graph. It then claims that reopening every graph descendant is inclusion-minimal among strategies sound for every semantics compatible with that graph.

The proof constructs a semantics in which every edge on an arbitrary descendant path is necessary support. That construction needs an additional premise: the constructed semantics must belong to the admissible semantics class. Soundness alone does not provide that premise.

### Counterexample

Let the graph contain `x -> q`, but let every admissible semantics in the fixed class make `q` depend only on an independent support `y`. The graph is still sound as an over-approximation: it has not omitted any actual support path. Its edge from `x` to `q` is merely conservative/spurious.

After changing `x`, a strategy that preserves `q` is sound for this semantics class. Descendant reopening remains safe, but it is not inclusion-minimal. Thus:

\[
\text{dependency soundness} \not\Rightarrow \text{graph-only minimality}.
\]

### Corrected premise

For robust graph-only minimality, require **path realizability relative to the admissible class**:

> For every certified descendant `q` of the changed set `X`, there exists at least one admissible semantics compatible with the graph in which a path from `X` to `q` is necessary support and the change invalidates `q`.

Under that premise, any strategy that sees only the graph and must remain sound uniformly over the admissible class must reopen every descendant. The corrected theorem is stated in the ORION-16 V2 formal addendum.

### Claim disposition

- downstream reopening **sufficiency** remains formal under dependency soundness;
- downstream reopening **minimality** is formal only under the stronger path-realizability/robust-class premise;
- any wording that presents minimality as a consequence of soundness alone is struck.

## 3. ORION-16 defect B — commutation needs footprint fidelity, not declarations alone

Disjoint declared read/write sets are not sufficient if a transition can inspect undeclared state, mutable ambient state, hidden authority/provenance objects, or another mechanic's outputs through an unregistered channel.

The necessary extensionality condition is:

\[
E\vert_{R_m}=E'\vert_{R_m}
\Longrightarrow
\tau_m(E)\vert_{W_m}=\tau_m(E')\vert_{W_m},
\]

with all changed coordinates contained in `W_m`. The same requirement applies to authority, provenance, obligations, dependency edges and invariant inputs consumed by the mechanic.

Under deterministic footprint fidelity and strong separation:

- the two orders have equal **scientific projections**;
- their ordered histories remain different sequences;
- the histories are equivalent only modulo swapping independent adjacent events.

The V1 formal core already corrected whole-state equality to scientific-projection equality plus trace equivalence. V2 makes footprint fidelity explicit and freezes a regression test for the distinction.

## 4. ORION-17 audit

No theorem correction is required by this pass. The V1 formal core already avoids the common overclaim that absence of a closure certificate always implies ambiguity; it states the stopping impossibility directly on observationally indistinguishable admissible extensions and introduces a separate richness premise when deriving ambiguity from missing closure information.

The remaining gap is empirical and contractual: benchmark rows must be **executed against a terminal oracle**, not merely parse as JSON. V2 adds eight frozen cases, suite-level coverage constraints, negative controls and a non-retrieval transfer case.

## 5. ORION-18 audit

No theorem correction is required by this pass. The typed anti-laundering theorem is a syntactic/derivational result under the premise that registered coercions are the only domain-changing rules. It does not establish that the coercion registry is sound or that the calculus improves live agents.

The remaining gap is discriminating evaluation. A deny-all mechanism would trivially block laundering, so V2 requires:

1. clean authorized cases in all five domains;
2. blocked paired cases in all five domains;
3. explicit laundering attacks;
4. `CANNOT_CHECK` distinct from rejection;
5. at least one clean authorized cross-domain coercion control.

## 6. Executable receipt

Run:

```bash
python papers/candidates/run_assumption_regressions_v2.py \
  --json-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.json \
  --markdown-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.md
```

Frozen V2 result:

- 28 unit tests;
- 29 named structural checks;
- 37 machine-readable hostile/negative-control cases;
- artifact-set SHA-256 `bbf26697db10993486c3620c8571b6231de7eef997d966cdda8f87761e569a04`;
- local terminal `PASS`.

## 7. Authority boundary

This audit authorizes only the corrected formal wording and the reproducibility claim that the listed local artifacts execute deterministically in the recorded environment. It does not authorize distinct novelty, empirical benefit, flagship promotion or peer-review readiness.
