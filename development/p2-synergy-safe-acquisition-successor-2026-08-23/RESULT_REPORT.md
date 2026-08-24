# P2 safe query-conditioned acquisition result

## Frozen terminal

`P2_SYNERGY_SAFE_QUERY_CONDITIONED_ACQUISITION_REQUIRES_SUCCESSOR`

All 25 frozen files and all eight review-world joins passed.  The candidate did
not pass the scientific gates.

## Result

SAFE_RANK_FUSION attained macro recall **0.584318** at 10% screened.  The
unchanged ACTIVE_LOGREG arm attained **0.602179**.  Against the strongest of
random, static seed, static review query and active logistic within every world,
the fused candidate's paired macro difference was **-0.047816**, with a
100,000-replicate world-bootstrap interval of **[-0.104537, -0.001431]** and
exact one-sided sign-flip value **0.957031**.  It strictly won only **1/8**
worlds.  Its macro WSS@95 difference was **-0.138554**.

The only passed scientific harm gate was the random-screening floor: the fused
candidate was never more than 0.05 below random recall at 10%.  That protection
does not compensate for the failed incremental, replication and work-saving
gates.

## Causal diagnosis

The fixed 0.40/0.30/0.20/0.10 fusion repaired Chou_2004 and Oud_2018 in
development but diluted strong sequential label feedback on the new panel.
ACTIVE_LOGREG exceeded the fusion on Wassenaar_2017, Menon_2022, Nelson_2002,
Jeyaraman_2020 and Brouwer_2019; it reached recall 1.0 on Brouwer_2019.  Static
review-query or seed views remained locally stronger on several other worlds.
The failure is therefore not that the donor views lack value.  It is that a
fixed global mixture cannot choose their world-dependent value.

## Next research identity

`P2.SYNERGY.ADAPTIVE.ROUTE.PORTFOLIO.V1`: treat active labels, review-query
similarity, seed similarity and exploration as acquisition routes.  Allocate a
small frozen pilot budget across routes, update only from labels revealed by
selected records, and route the remaining budget to the empirically supported
controller with a noncompensatory random-harm guard.  Develop on the twenty
burned worlds and confirm only on the six SYNERGY worlds whose label and work
bodies remain unopened.

The failed fusion terminal remains immutable and is not a negative claim about
ORION as a whole.  It is a result about this exact public screening controller.
