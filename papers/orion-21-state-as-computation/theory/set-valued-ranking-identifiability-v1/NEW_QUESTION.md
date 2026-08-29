# ORION-21 new theorem question — exact ties as set-valued observation

Identity: `ORION21.SET_VALUED_RANKING_IDENTIFIABILITY.v1`.

The spent tie-robust phase experiment showed that an exact score tie can change a downstream verdict. A further tolerance retry would be rescue. The new object is instead the information structure created by an exact tie.

For a score vector `s` and rank budget `r`, let `S_r(s)` be the full family of top-r supports consistent with the exact ordering and all exchanges inside the boundary tie block. For any downstream deterministic functional `F`, ask:

1. when is `F` identifiable from `s,r` despite the tie?
2. when it is not identifiable, what is the smallest exact certificate of non-identifiability?
3. can the exact attainable interval `{F(S): S in S_r(s)}` be computed without introducing a tolerance?

This is a theorem about set-valued ranking observations. It does not reopen or rehabilitate the withdrawn phase-boundary claim.
