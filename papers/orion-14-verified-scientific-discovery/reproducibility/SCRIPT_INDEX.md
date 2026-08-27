# ORION-14 V2 Script Index

| Purpose | Path |
|---|---|
| Host case generation | `host/generate_protected_cases.py` |
| Repaired ORION candidate adapter | `host/run_candidate.py` |
| Frozen comparator mechanisms | `host/run_baselines.py`, `host/run_baselines_v2.py` |
| Frozen ablations | `host/run_ablations.py` |
| Protected scoring | `host/evaluate_campaign.py`, `host/evaluate_campaign_v2.py` |
| Ablation scoring | `host/evaluate_ablations.py` |
| Independent headline reproduction | `host/independent_reproduce.py`, `host/independent_reproduce_v2.py` |
| Publication figures/tables | `figures/generate_figures.py` |
| Signed-freeze orchestration | `.github/workflows/p4_protected_campaign_v2.yml` |
| TMLR PDF/stale-claim audit | `.github/workflows/p4_tmlr_submission_audit.yml` |
