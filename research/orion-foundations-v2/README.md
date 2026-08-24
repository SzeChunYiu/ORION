# ORION Foundations V2 — local derivation tranche

**Issue:** #1220  
**Base:** `eba4a67e8607cdef96a2bb038d685a9a5d548599`  
**Authority:** `LOCAL_FINITE_DERIVATION_ONLY / NO_PAPER_AUTHORITY_DELTA`

This package completes the theorem derivations and finite executable checks that
fit a bounded local environment. It does not alter P1–P15 manuscripts, evidence,
protocols, or active claim authorities, and it does not touch PR #1218, RR1,
LUNARC, Slurm, custody, integrity, or finalizer paths.

## Reproduce

```bash
PYTHONPATH=src pytest tests/foundations -q
PYTHONPATH=src python -m orion.foundations.cli \
  --output /tmp/LOCAL_THEOREM_RECEIPT_V1.json \
  --assumptions-output /tmp/ASSUMPTION_LEDGER_V1.json \
  --countermodels-output /tmp/COUNTERMODEL_ATLAS_V1.json \
  --theorem-ledger-output /tmp/THEOREM_LEDGER_V1.json
```

The committed compact receipt binds the local theorem IDs, authority ceiling,
coordination state, and canonical executable-core digest. Full ledgers are
regenerated deterministically by the command above rather than duplicated as
large committed prose artifacts.
