# ORION-ORION-14 V2 Reproducibility

## Exact identities

- Subject: `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`
- Protected campaign: `31976589735`
- Split SHA-256: `3fe91b669643fa158f2f64c1e6ab70837afbb9b0582e297f1da6e1c3c696fcd9`
- Harness SHA-256: `094f43cb320f8e8e3196049269b20ac22e7e94fa9890b80f27f38ef49f7c82ea`
- Safe bundle SHA-256: `51ac14bc3a6b4b570aaca6d4a41c91f53d9bf2887e66f0620c412f78566a3b44`

## Safe replay

```bash
python papers/orion-14-verified-scientific-discovery/figures/generate_figures.py
pytest -q tests/unit/p4/test_p4_publication_v2.py tests/unit/p4/test_p4_v2_execution_freeze.py
```

The figure generator reads only immutable public V2 aggregates. It does not read the exploratory live arm or protected gold.

## Protected reproduction

After protected scoring, a separate job independently rejoined the protected manifest with one deterministic ORION/comparator output and reproduced `0/360` versus `180/360` false promotions and `60/60` versus `60/60` clean promotions. The receipt is releasable; protected labels are not.

## Comparator scope

Comparator arms are common-protocol mechanism reimplementations. Reproducing this paper does not require or imply executing the external authors' original systems.
