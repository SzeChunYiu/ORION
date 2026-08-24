# Development packet — issue #1086 P6/P8 easy closure

## Atomic questions

1. Can P6's canonical theorem statement be made consistent with its executable
   read/write-noninterference assumptions?
2. Can P8's already-earned `DENIED`/`CANNOT_CHECK` separation be protected by a
   direct frozen-gold regression?

## Scope

The P6 change corrects two stale manuscript theorem blocks, binds one stable
contract identifier across executable, formal, manuscript, submission and
ledger artifacts, and removes duplicate ledger identifiers. The P8 change adds
one regression over the existing frozen gold.

No public-domain execution, kernel proof, independent review, native-system
validation or external custody is claimed.

## Verification

```bash
python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_commutation_contract_binding_v1.py
python -m pytest -q tests/unit/candidates/test_p6_commutation_contract_binding.py
python -m pytest -q tests/unit/study/p6/test_p6_separation_calculus_smt.py
python -m pytest -q tests/unit/study/p8/test_p8_authority_terminals.py
```
