# Custodian-nondelegation upper bound (P1 V4)

## Frozen setting

Let $G=\{g_1,\ldots,g_{12}\}$ be the twelve requirement groups in the byte-bound V8 custodian registry (`42fd386b113802b5b269dada6ab2965503fa5afa020a06e52a25ce667d03dae4`). For a frozen source library $S$, define

$$\operatorname{Suff}(g,S)=A_g(S)\land C_g(S)\land L_g(S)\land E_g(S),$$

where $A_g$ is named-custodian authorship or explicit delegation, $C_g$ is exact R7 target coverage, $L_g$ is applicable completed-target-algebra rights, and $E_g$ is satisfaction of all schema and exhaustiveness conjuncts. This is not a new admission rule; it is the V8 rule written as a conjunction.

## Theorem

For every $g$, $\operatorname{Suff}(g,S)\le A_g(S)$. Hence

$$\sum_{g\in G}\operatorname{Suff}(g,S)\le \sum_{g\in G}A_g(S).$$

If no captured source is authored by the named R7/host/target-rights/review custodian and no source contains explicit delegation from that custodian over the completed R7 algebra, then the right-hand side is zero and exactly zero requirement groups can be sufficient.

## Proof

Conjunction elimination gives $A_g(S)$ from $\operatorname{Suff}(g,S)$, so each Boolean sufficiency indicator is bounded by its authority indicator. Summing preserves the inequality. V4 evaluates $A_g(S)=0$ in all twelve frozen rows. Nonnegativity then gives both an upper and lower bound of zero. $\square$

## Exact V4 evaluation

- Accessible authoritative institutional families: **4** (NISO, Crossref, NLM/JATS, COPE).
- Source-native structural-analogue groups: **9/12**.
- Named-custodian/delegation groups: **0/12**.
- Sufficient owner-algebra groups: **0/12**.
- Scientific-action gold cells: **0**.

## Scope boundary

This theorem says web standards cannot substitute for the named owner/custodian conjunct in this frozen registry. It does **not** prove that a future owner-signed algebra is impossible, that any postpublication standard is defective, or that any R7 map is false. The 720 V8 maps remain `CANNOT_CHECK`; the map audit was not rerun.
