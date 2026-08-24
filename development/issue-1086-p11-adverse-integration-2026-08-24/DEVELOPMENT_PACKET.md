# Development packet — P11 adverse-result integration

## Atomic question

Can the landed ten-responsibility negative be folded into P11's canonical
manuscript, central ledger and active authority without relabelling it or
inventing the absent `P11J` artifact identity from issue #1086?

## Acceptance

- active authority V2 binds primary, independent, binding and narrative receipts;
- manuscript and ledger report LINEAR 3/10, RBF 5/10 and KNN 5/10 against the
  frozen 8/10 gate;
- resource identities remain supported but cannot compensate the quality gate;
- family-scale promotion is explicitly forbidden;
- external validation remains `CANNOT_CHECK`.

## Verification

```bash
python papers/paper-11-state-as-computation/check_p11_adverse_integration_v2.py
python -m pytest -q tests/unit/publication/test_p11_adverse_integration_v2.py
```
