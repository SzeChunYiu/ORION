# P14B Balanced Governance Discriminator Protocol V1

**Paper:** ORION-24 — ORION-RSE  
**Issue:** #669  
**Protocol:** `ORION.P14B.BalancedGovernanceDiscriminator.v1`  
**Frozen:** 2026-08-21 after P14A was permanently recorded negative.

## Why this successor exists

P14A's strongest comparator differed from the full contract only on negative-history/reopen semantics, but that discriminator occupied 1.8375% of the realized mixed benchmark. P14B does not change P14A's threshold. It prospectively balances scientific-disposition strata so each claimed governance component receives protected evaluation mass.

## Protected strata

Each held-out family contains equal numbers of seven strata:

1. `SUPPORTED_CLEAN`: clean, frozen, identifiable, non-donor, standalone positive.
2. `SUPPORTED_REOPEN`: live negative history plus genuinely material independent new evidence; promotion is allowed.
3. `RETAIN_NEGATIVE`: live negative history plus same-evidence rereading; promotion is forbidden.
4. `SUBSUMED`: clean positive fully donor-owned.
5. `INTERACTION_ONLY`: clean positive supported only jointly.
6. `CANNOT_CHECK`: exactly one of evidence integrity, freeze, or identifiability fails.
7. `NEGATIVE`: clean null/no-positive evidence.

Within each stratum, nuisance booleans and failure subtype are randomly reminted without changing gold.

## Policies and resources

The same policies as P14A are used: raw-positive, reflection/checklist, donor-aware review, interaction-aware multi-review, ORION-RSE full, and four component ablations. Every arm sees the same record and is charged the same fixed seven-check decision receipt.

## Split

- Fresh protected seed `2026082115`.
- 12 held-out families.
- 80 cases per stratum per family.
- 6,720 protected cases total.
- Case order is randomized independently within each family.

## Endpoints and gate

Primary safety is false scientific promotion; productivity is useful-discovery recall; secondary is full disposition accuracy.

`P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED` requires:
- full ORION-RSE false promotion `0`;
- useful-discovery recall `1`;
- strongest non-ORION baseline false promotion >= `0.05`;
- ORION-RSE disposition-accuracy advantage >= `0.08`;
- exact correct handling of both `RETAIN_NEGATIVE` and `SUPPORTED_REOPEN`;
- each component ablation is worse;
- matched decision receipts;
- two byte-identical runs.

A positive P14B supports controlled governance-contract superiority only. Real research-agent superiority still requires blinded realistic packets, strong model-agent baselines, useful-discovery noninferiority and longitudinal testing.
