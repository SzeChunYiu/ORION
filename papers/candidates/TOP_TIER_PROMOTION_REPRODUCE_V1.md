# Reproduce the ORION-16–ORION-25 promotion contract audit

From repository root:

```bash
python papers/candidates/check_top_tier_promotion.py
pytest -q tests/unit/programme/test_top_tier_promotion.py
```

Expected CLI terminal:

```text
P6_P15_TOP_TIER_PROMOTION_CONTRACT_GREEN
```

This terminal validates only the **structure of the publication-promotion contracts**. It does not authorize any scientific result, novelty claim or submission-ready terminal.

A scientific promotion receipt must additionally bind the protected protocol, raw results, independent verification/adjudication, hostile review, current literature/donor saturation, reproduction environment and exact manuscript package described in `TOP_TIER_PROMOTION_GATE_V1.md`.
