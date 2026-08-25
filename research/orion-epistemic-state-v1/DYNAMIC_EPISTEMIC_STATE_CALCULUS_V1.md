# ORION Dynamic Epistemic State Calculus V1

## Status

```text
theory = COMPLETE_FOR_DECLARED_TYPED_AND_FINITE_CLASSES
reference_implementation = INCLUDED
paper_authority_delta = NONE
empirical_superiority = CANNOT_CHECK
external_novelty = CANNOT_CHECK
```

This is the shared formal object for the P1–P15 top-tier successor manuscripts. Historical terminals, receipts, active authorities, and negative evidence remain immutable.

## Scientific state

For object or claim `c`, responsibility `tau`, and epoch `t`, ORION stores

\[
X_t(c,\tau)=(E,\Theta,C,R,P,F,V,A,S,Q,D,B,K,U,M,G).
\]

The coordinates are heterogeneous:

- `E`: evidence as an effect, likelihood, posterior, or interval;
- `Theta`: identified set or target-relevant partition;
- `C`: coverage bounds plus an explicit open-world residual;
- `R`: required, satisfied, and unresolved obligations;
- `P`: provenance and derivation hypergraph;
- `F`: freshness, validity interval, and epoch dependencies;
- `V`: verifier identities, results, and dependence graph;
- `A`: scope-indexed scientific authority partial order;
- `S`: alternative complete support families;
- `Q`: reproducibility outcomes and heterogeneity;
- `D`: active defeater set;
- `B`: required and available resource vector;
- `K`: custody and lineage-overlap graph;
- `U`: compute, time, memory, money, and experimental burden;
- `M`: registered method language and reachable closure;
- `G`: typed scientific knowledge hypergraph.

A human-readable terminal is a decision projection, not the stored state:

\[
L_{d,\tau,\rho,t}=\pi_{d,\tau,\rho}(X_t).
\]

The reverse map is generally set-valued:

\[
\Gamma_\rho(\ell)=\{X:\pi_\rho(X)=\ell\}.
\]

Hence a non-injective legacy label has no faithful inverse.

## Updates

A content-bound event updates the state:

\[
X_{t+1}=U_{\eta_t}(X_t).
\]

Events include evidence, replication, contradiction, revocation, responsibility change, regime change, donor absorption, method expansion, resource change, custody change, and external adjudication. Each event binds subject, kind, digest, scope, epoch, authorized coordinate writes, dependencies, receipts, and estimator version.

The update algebra requires replay determinism, idempotence, independent commutation, explicit noncommutation, exact revocation locality, and no silent authority amplification.

## Hard obligations and ranking

For decision `d`, non-compensatory predicates `H(d,tau)` determine admissibility:

\[
\operatorname{Admissible}_{d,\tau}(X)\iff\bigwedge_{h\in H(d,\tau)}h(X).
\]

Only admissible alternatives may be ranked. Without a preference vector frozen before outcomes, ORION returns a Pareto frontier. High evidence cannot compensate for non-identifiability; internal replay cannot replace hard external custody; provenance cannot create scientific truth.

## Knowledge growth and the apple principle

The knowledge web is a typed directed hypergraph. A source contributes new nodes, load-bearing edges, support families, method reach, verification, or defeaters. Source value is therefore a vector rather than the count of papers read.

For search action `a`, define a target-relative gain vector

\[
g_\tau(a\mid X_t)=(\Delta\Theta,\Delta C,\Delta R,\Delta S,-\Delta R_{donor},\Delta M,\Delta\mathcal F,-\Delta U).
\]

Nearest-neighbour search is locally saturated when every registered local action has a gain upper envelope that is negligible, redundant, or Pareto-dominated. This is not global closure.

A remote structural jump is licensed when a load-bearing obstruction remains, local gain is saturated, a remote source is chosen by a typed structural correspondence, and its expected gain is non-dominated. The remote source may be another discipline, an engineering design, a musical structure, or any artifact; scientific credit comes only from the target-native correspondence and hidden consequence, not from topical proximity.

## Ideal donor frontier

Let `D` include the strongest donor methods and admissible donor products under matched information and resources. Their Pareto frontier is

\[
\mathcal F_D^\tau=\operatorname{Pareto}\left(\bigcup_{d\in Cl(D)}Y_d^\tau\right).
\]

ORION is superior only if it is donor-conservative and strictly extends this frontier. A tradeoff is not superiority without a preregistered preference vector.

For candidate semantic hypergraph `H_C` and admissible donor explanation `e`, let `R_e=H_C\setminus e`. Retain all inclusion-minimal residuals and the unavoidable core `R_core=intersection_e R_e`. Valid states are `FULLY_DONOR_ABSORBED`, `NONUNIQUE_RESIDUAL`, `INTERACTION_ONLY_RESIDUAL`, `ROBUST_RESIDUAL_CANDIDATE`, and `DONOR_ACCESS_CANNOT_CHECK`. Adding donors can only preserve or shrink the residual.

## Claim frontier and boundary escape

Claims form an implication order. ORION retains every incomparable maximal supported claim, not one artificially cautious sentence. A refuted broad claim is preserved and transformed into:

```text
counterexample -> exact boundary -> missing coordinate -> constructive escape
               -> prospectively frozen prediction -> strongest donor test
```

## Theorem programme

- `DES-T0` state/label separation;
- `DES-T1` legacy non-reconstruction;
- `DES-T2` strict planning advantage over label-only control;
- `DES-T3` impossibility of a faithful compensatory global score;
- `DES-T4` decision-relative minimal-state quotient;
- `DES-T5` event replay coherence and idempotence;
- `DES-T6` independent-update commutation;
- `DES-T7` exact support-family revocation;
- `DES-T8` local saturation is not open-world closure;
- `DES-T9` structural-jump sufficiency under a calibrated gain model;
- `DES-T10` donor-residual monotonicity;
- `DES-T11` ideal-frontier superiority;
- `DES-T12` interaction-only novelty;
- `DES-T13` open move-class necessity;
- `DES-T14` maximal-supported-claim antichain;
- `DES-T15` conservative reproduction and strict extension of legacy decisions.

## Claim ceiling

```text
DYNAMIC_STATE_FORMALISM_AND_P1_P15_SUCCESSOR_MANUSCRIPTS_DRAFTED
EMPIRICAL_TOP_TIER_AUTHORITY = NONE
```
