# P8 protected cross-capability authority benchmark seed V1

`authority_cases_v1.jsonl` freezes 17 paired/hostile case contracts.

## Composition

- 5 clean authorized cases across `REFRAME`, `SEARCH_STOP`, `MAP_MERGE`, `ASSERT` and `SELF_MODIFY`;
- 5 paired cases with missing obligations or active defeaters;
- 5 authority-laundering attacks in which a signal valid in one layer is used as authority in another;
- 1 `CANNOT_CHECK` case;
- 1 clean authorized cross-domain coercion case, preventing a blanket no-coercion/deny-all policy from passing.

## Reference verdict semantics

1. active defeater -> `REJECT`;
2. unresolved missing hard obligation -> `CANNOT_CHECK`;
3. known missing hard obligation -> `UNAUTHORIZED`;
4. source-signal domain mismatch without registered coercion -> `UNAUTHORIZED`;
5. otherwise -> `AUTHORIZED`.

The deterministic oracle executes manifest labels. It is not an agent, policy optimizer or protected evaluator.

## Required prospective baselines

- the actual independent P1–P5 gate composition;
- strong domain-specific rule policies;
- provenance-only verification;
- paired abstention policy;
- expected-utility/scalar policy;
- a current authorization-language or policy-engine implementation where operationally comparable;
- full shared P8 calculus and type/coercion/revocation ablations.

## Anti-total-refusal rule

A system must jointly minimize unauthorized/laundered actions and unnecessary refusal while preserving clean authorized coverage. Zero action is not a successful authority system. Valid registered cross-domain coercions must remain usable.
