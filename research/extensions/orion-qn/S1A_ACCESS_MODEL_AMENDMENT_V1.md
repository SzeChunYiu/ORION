# ORION-QN S1A access-model amendment v1

Status: **PRE-OUTCOME CORRECTION / ADDITIVE AMENDMENT**  
Programme: `SzeChunYiu/ORION#734`  
Parent packet retained unchanged: `development/orion-qn-q2/S1A_IMPLEMENTATION_PACKET_V1.md`  
Correction frozen before any result-bearing S1A Actions outcome.

## 1. Defect discovered by hostile review

The S1A simulator is a known-answer semantic fixture. The evaluator supplies `marked_index` so the test harness can synthesize a Grover phase oracle and independently score the returned candidate.

That fixture fact is compatible with **query-complexity testing**, but it does not itself prove that an ordinary problem exposing only a classical predicate can supply the coherent unitary oracle required by Grover at the same access cost.

The initial campaign adjudicator incorrectly made this distinction implicit by constructing:

```text
QAccessMatch(
    same_problem=True,
    same_information=True,
    same_tolerance=True,
    stronger_quantum_interface_unresolved=False,
)
```

without binding which quantum access model was admitted.

A positive `QUANTUM_QUERY_ADVANTAGE_ONLY` terminal could therefore be read as though coherent oracle access had been derived from the classical predicate. That would violate `NO_STRONGER_ORACLE` outside the standard query model.

## 2. Literature/access-model boundary

The standard quantum query model defines quantum access to a Boolean function through a coherent unitary oracle `U_f`, with query cost treated separately from the gate cost of realizing `U_f`.

This is a valid theoretical model and S1A may test it.

It is a **different access contract** from an ordinary input that provides only classical evaluation of `f(x)`. Coherent access may be unavailable, expensive, or require an explicit reversible construction.

Therefore ORION-QN must distinguish model-relative query evidence from access derivability.

## 3. Frozen access modes

Add the following explicit Q1 access coordinate:

```text
UNSPECIFIED
NATIVE_COHERENT_ORACLE
DERIVED_COHERENT_ORACLE
CLASSICAL_PREDICATE_ONLY
```

Interpretation:

### `NATIVE_COHERENT_ORACLE`
The registered problem/query model supplies `U_f` as the quantum access primitive. A bounded query-complexity comparison is admissible. Oracle implementation cost remains outside the query terminal and unresolved for stronger claims.

### `DERIVED_COHERENT_ORACLE`
The problem does not natively supply `U_f`; a construction from admitted problem access is claimed. A positive quantum terminal requires an explicit derivation/access obligation to be resolved. End-to-end resource claims additionally require its resource cost.

### `CLASSICAL_PREDICATE_ONLY`
Only ordinary classical evaluation of `f(x)` is admitted. The current S1A known-answer fixture may still validate Grover circuit semantics, but it cannot issue a positive quantum-advantage terminal for this access contract. Correct route terminal is `CANNOT_CHECK_ACCESS_MODEL` until coherent construction is separately established.

### `UNSPECIFIED`
No positive quantum terminal is admissible.

## 4. Q1 hardening rule

For every positive terminal:

```text
QUANTUM_QUERY_ADVANTAGE_ONLY
QUANTUM_PROJECTED_FT_ADVANTAGE
QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED
```

Q1 must reject the receipt unless:

- quantum access mode is explicit;
- mode is `NATIVE_COHERENT_ORACLE`, or mode is `DERIVED_COHERENT_ORACLE` with derivation resolved;
- no independent `stronger_quantum_interface_unresolved` flag remains;
- all existing problem/information/tolerance gates still pass.

The amendment strengthens the gate and does not relax any frozen criterion.

## 5. S1A dual interpretation

One physical simulator execution may support two **different scientific readings**, which must be recorded separately:

### A. Query-model reading

```text
quantum_access_mode = NATIVE_COHERENT_ORACLE
oracle_construction_status = QUERY_MODEL_ASSUMPTION
claim ceiling = QUANTUM_QUERY_ADVANTAGE_ONLY
```

This asks only whether Grover uses fewer coherent oracle queries than the frozen classical oracle-query comparators under their respective standard query access models.

### B. Ordinary-classical-input reading

```text
quantum_access_mode = CLASSICAL_PREDICATE_ONLY
coherent_oracle_derivation_resolved = false
terminal = CANNOT_CHECK_ACCESS_MODEL
```

This explicitly prevents S1A from becoming evidence that a normal computer input can be converted to the required coherent oracle for free.

The second interpretation is mandatory in every S1A size summary even if the query-model reading is positive.

## 6. P4 reconstruction obligations

Independent reconstruction must verify:

- the query-model terminal names `NATIVE_COHERENT_ORACLE` explicitly;
- the ordinary-input interpretation is `CANNOT_CHECK_ACCESS_MODEL`;
- no S1A record claims coherent-oracle derivation from classical predicate access;
- end-to-end unresolved coordinates still include coherent oracle construction;
- changing the access mode to `CLASSICAL_PREDICATE_ONLY` while retaining a positive terminal is rejected.

## 7. Hostile RED cases

Before Q1 implementation is changed, freeze tests requiring rejection when:

1. positive query terminal uses `UNSPECIFIED` access;
2. positive query terminal uses `CLASSICAL_PREDICATE_ONLY`;
3. `DERIVED_COHERENT_ORACLE` claims positive terminal with derivation unresolved;
4. S1A query summary omits its explicit query access model;
5. S1A ordinary-input interpretation reports query advantage instead of `CANNOT_CHECK_ACCESS_MODEL`.

## 8. Claim correction

This amendment does not reduce the legitimacy of a standard Grover **query-complexity** result. It prevents that result from being misrepresented as access-matched end-to-end evidence for ordinary classical inputs.

Expected strongest S1A language, if the frozen run succeeds:

> Under an explicitly supplied coherent-oracle query model, the S1A Grover route demonstrates a bounded query-count advantage over the frozen classical oracle-query baselines on the registered sizes. The same simulator result remains `CANNOT_CHECK_ACCESS_MODEL` for a classical-predicate-only input because coherent oracle construction has not been derived or costed.

Physical speedup remains unlicensed.
