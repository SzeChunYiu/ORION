# ORION-QN S1A benchmark-dependence amendment v1

Status: **PRE-OUTCOME CORRECTION / ADDITIVE AMENDMENT**  
Programme: `SzeChunYiu/ORION#734`  
Parents retained unchanged:
- `development/orion-qn-q2/S1A_IMPLEMENTATION_PACKET_V1.md`
- `research/extensions/orion-qn/S1A_ACCESS_MODEL_AMENDMENT_V1.md`

This amendment was frozen before any result-bearing S1A Actions outcome.

## 1. Defect found by hostile review

The original S1A implementation packet freezes eight marked positions per search size using a public deterministic generator. Those fixtures are excellent for reproducible semantic testing, but their public support distribution is itself side information.

A classical strategy designed after reading the protocol can query those eight possible positions first. Therefore the originally declared C1/C2 fixture means are not the strongest classical baseline for an advantage claim once public benchmark-construction information is admitted.

The error would be to confuse:

```text
reproducible known-answer conformance fixtures
```

with:

```text
an information-hiding benchmark distribution suitable for advantage adjudication
```

## 2. Current prior-art boundary

Pal, Sharma & Podila, **Loophole-Robust Certification of Quantum Advantage** (arXiv:2607.13090, 2026), formalize benchmark dependence as classical side information correlated with the evaluated task instance. Their result makes construction-side information a quantitative resource rather than a narrative leakage concern.

This amendment adopts the same hostile principle qualitatively for S1A: a public fixture generator cannot be used as though its support were hidden from the classical comparator.

## 3. Revised role of the eight frozen cases

The eight cases per `n` remain unchanged and must still execute.

They are now **semantic/conformance fixtures only**. They test:

- Grover circuit construction;
- exact analytic-vs-statevector probability;
- actual computational-basis measurement;
- retry accounting;
- returned-candidate predicate verification;
- backend/version identity;
- logical/transpiled resource telemetry;
- harness request/result binding;
- independent P4 reconstruction.

They do **not** determine the query-advantage baseline.

Every result must record:

```text
fixture_cases_used_for_advantage = false
```

P4 must reject a report that sets or implies otherwise.

## 4. Registered query-advantage model

For each `n`, define the theoretical benchmark independently of the eight fixtures:

```text
N = 2^n
one marked item y ~ Uniform({0, ..., N-1})
algorithm does not observe y except through its admitted oracle access
```

Quantum access is the separate access amendment's:

```text
NATIVE_COHERENT_ORACLE
```

so `U_f` is an explicit query-model primitive. Ordinary classical-predicate-only input remains separately `CANNOT_CHECK_ACCESS_MODEL`.

No benchmark seed, case id, fixture support, or construction-side variable is available to the query-model classical strategy.

## 5. Quantum query coordinates

For the frozen Grover iteration count `r`:

```text
theta = asin(1/sqrt(N))
p_q = sin^2((2*r+1)*theta)
quantum_query_budget = r
```

S1A uses the **single-run** analytic success `p_q` for query-model adjudication.

The measured/retry harness remains useful implementation evidence but does not inflate the theoretical query-model success target or become the advantage comparator.

This cleanly separates:

```text
query algorithm theorem/model
from
robust simulator execution procedure
```

## 6. Strong classical hidden-uniform comparator

Under a single hidden uniformly distributed marked item and no benchmark-correlated side information, a classical oracle algorithm that makes `K` distinct queries and only returns a predicate-verified found item succeeds with probability:

```text
p_c = K / N
```

To match or exceed the quantum single-run success probability, the minimum classical query budget is:

```text
K_match = ceil(p_q * N)
```

capped at `N`.

For a uniformly random hidden mark and an optimal no-replacement scan that stops when it finds the item or reaches `K_match`, the expected number of predicate queries is:

```text
E_C = sum_{j=1..K_match} P(mark not found before query j)
    = K_match - K_match*(K_match-1)/(2*N)
```

Both coordinates must be reported:

```text
classical_matching_query_budget = K_match
classical_matching_expected_queries = E_C
```

The query-only terminal requires conservatively:

```text
r < K_match
and
r < E_C
```

plus all semantic/access/P4 gates.

This comparator is stronger and cleaner than using one arbitrary deterministic scan over a public eight-point support.

## 7. Fixture telemetry retained as non-authorizing evidence

The original per-case C1/C2 call counts remain in raw records for diagnostics and to preserve the frozen packet history.

They must be labeled:

```text
fixture_classical_diagnostic_only = true
```

and must not enter the terminal decision.

This prevents silent rewriting of old fields while removing their authority role.

## 8. P4 reconstruction obligations

Independent reconstruction must recompute from `n` alone:

- `N`;
- frozen optimal `r`;
- analytic `p_q`;
- `K_match = ceil(p_q*N)`;
- `E_C`;
- query-model terminal;
- `fixture_cases_used_for_advantage = false`;
- native coherent-oracle query access;
- ordinary-input `CANNOT_CHECK_ACCESS_MODEL`.

It must reject:

1. a terminal computed from fixture C1/C2 means;
2. `fixture_cases_used_for_advantage = true`;
3. a query-model success probability derived from observed fixture success frequency;
4. a classical matching budget smaller than `ceil(p_q*N)`;
5. a report that uses the public fixture support as hidden classical information.

## 9. Consequence for scientific wording

If S1A passes, allowed language becomes:

> The pinned simulator reproduces Grover semantics on prospectively frozen known-answer fixtures. Separately, under the explicitly supplied coherent-oracle, hidden-uniform single-mark query model, the frozen Grover iteration count uses fewer queries than the classical oracle budget/expected-query cost required to match its analytic single-run success probability. This is a bounded query-model result only. The public fixture distribution is not used to establish the advantage, coherent-oracle construction remains unresolved for ordinary classical inputs, and no physical speedup is claimed.

## 10. No change to stronger programme gates

S2–S4 remain mandatory. In particular:

- structure-aware classical algorithms can destroy the S1 residual;
- coherent oracle construction can destroy it;
- classical preprocessing/indexing/amortization can destroy it;
- fault-tolerant resources can destroy it.

A clean S1 query result is a correctness/base-case milestone, not the flagship result.
