# P2 final-six adaptive route-portfolio result

## Frozen terminal

`P2_SYNERGY_ADAPTIVE_ROUTE_PORTFOLIO_REQUIRES_NEW_DATA_FAMILY_OR_CONTROLLER`

All 18 frozen files and all six exact label/work joins passed.  The adaptive
controller did not pass its noncompensatory promotion gates.

## Positive central diagnostic, failed promotion

The adaptive controller reached macro recall **0.732144** at 10% screened versus
**0.597800** for ACTIVE_LOGREG, a macro gain of **+0.134344**.  It remained near
the best per-world comparator: macro regret **-0.019823**, worst-world regret
**-0.081081**.  The random-harm and near-oracle gates passed.

The gain was not stable across worlds.  The 100,000-replicate world-bootstrap
interval was **[-0.042683, +0.447638]**, exact one-sided sign-flip value
**0.40625**, and strict active-controller wins occurred in only **2/6** worlds.
Macro WSS@95 was **0.060110** below ACTIVE_LOGREG, narrowly beyond the frozen
noninferiority floor of -0.05.  Thus the active-gain, replication and work-saving
gates failed.

Bos_2018 supplied the largest gain: the pilot exposed the review-query route's
value and the adaptive trajectory reached recall 1.0, whereas the separately
run active arm reached 0.1.  Meijboom_2021, Sep_2021 and van_de_Schoot_2018
retained losses.  The mean effect is therefore heterogeneous and partly driven
by one high-leverage routing event; it cannot be promoted as a stable
cross-world advantage.

## What the complete 26-world campaign establishes

The public SYNERGY programme now contains outcomes for all 26 V1 review worlds.
It shows that sequential label feedback frequently yields large recall and
work-saving gains, that a fixed query/seed/active mixture dilutes those gains,
and that a short adaptive route pilot can create large world-specific benefits
without yet delivering stable replication or WSS noninferiority.  These are
bounded public-label development results.  None establishes ORION-specific
superiority, open-world route invention, task closure, protected freshness, or
external custody.

## Next research identity

`P2.PUBLIC.CROSS_DATASET.CONTROLLER.TRANSPORT.V1`: freeze the unchanged active
and adaptive controllers on a different licensed citation-screening data family
before opening its labels.  The pinned CC-BY-4.0 Zenodo 10423427 physiotherapy
review corpus is the immediate lawful one-world transport check.  A publication
claim still requires a multi-review, source-disjoint external family rather than
post-outcome tuning on SYNERGY.
