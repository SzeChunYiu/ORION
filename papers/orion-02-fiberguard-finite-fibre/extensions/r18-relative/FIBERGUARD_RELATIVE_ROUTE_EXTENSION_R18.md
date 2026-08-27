# FiberGuard R18 — relative route certificates, acquisition timing, and transfer margins

Date: 2026-08-27

Status: analytic completion of the route layer exposed by the prospectively preserved R16 null and formalized by R17. Generic reject-option prediction, learning to defer, conformal calibration, Lipschitz extension, and domain adaptation are donor-owned. The scoped FiberGuard object is the oracle-relative comparison between two solver actions when representation cost, observation timing, and authority class are explicit.

## 1. Setup and claim boundary

For a state `x`, let `L_abs(x)` be the absolute cost of a learned action and `F_abs(x)` the absolute cost of a fallback or route action. Let `C*(x)` be the same statewise virtual-best oracle for every arm. Their excess losses are

`L(x)=L_abs(x)-C*(x)` and `F(x)=F_abs(x)-C*(x)`.

Define the relative route loss

`Delta(x)=F(x)-L(x)`.

Negative `Delta` favors fallback; positive `Delta` favors learned. Action-specific acquisition charges must be included in the corresponding total losses. A charge already paid by both actions is common sunk cost; a charge avoided by one action is not common and does not cancel.

The R18 theory gives deterministic finite certificates. Statistical intervals enter only through an explicitly declared simultaneous-validity event. None of the theorems turns marginal calibration into worst-case, pathwise, or distribution-shift safety.

## 2. Relative loss removes only a genuinely common baseline

### Theorem C-R18.1 — common-oracle relative-loss invariance

For every state,

`Delta=(F_abs-C*)-(L_abs-C*)=F_abs-L_abs`.

Therefore pairwise action ordering is invariant to subtraction of one common statewise oracle. More generally, adding the same statewise sunk-cost profile `b(x)` to both actions leaves `Delta` unchanged.

#### Proof

Both identities follow by cancellation. If acquisition costs differ between the actions, they are part of `F_abs` and `L_abs` and do not cancel. ∎

This theorem repairs a frequent accounting error: equal units are insufficient, but a truly common baseline or sunk charge cancels exactly.

## 3. Direct paired route certificates

Suppose a valid interval `[A_Delta(x),U_Delta(x)]` contains `Delta(x)`.

### Theorem C-R18.2 — interval-separated relative routing

On the interval-validity event:

- if `U_Delta(x)<=0`, fallback is certified no worse than learned;
- if `A_Delta(x)>=0`, learned is certified no worse than fallback;
- if `A_Delta(x)<0<U_Delta(x)`, the interval certifies no ordering.

#### Proof

If `U_Delta<=0`, then `F-L=Delta<=U_Delta<=0`, hence `F<=L`. The other direction is symmetric. An interval crossing zero contains values of both signs and therefore does not imply either ordering. ∎

A relative interval certifies a comparison. It does not by itself certify an absolute loss ceiling for the chosen action; that requires an upper certificate for the selected total loss. A controller should therefore keep absolute-loss and relative-order claims as distinct receipt fields.

## 4. Training-only route signs have no open-world authority without structure

### Theorem C-R18.3 — unseen-state relative-sign impossibility

Fix any finite training subject, every byte of its representations, learned losses, fallback losses, certificates, and route decisions. If a new state may share the same declared representation without a structural extension condition, then for every `M>0` there are two admissible extensions with identical training bytes in which the new state's relative loss is respectively `+M` and `-M`.

#### Proof

Leave the complete training subject unchanged. In one extension set `(L,F)=(0,M)` on the new state; in the other set `(L,F)=(M,0)`. Both preserve every training byte and the new representation value, but the signs of `F-L` are opposite. ∎

Thus neither an exact training fibre nor a learned-action certificate determines safe routing on an unseen same-signature state. A valid open-world route certificate requires a closed-world completeness claim, a structural law, or an explicitly statistical authority class.

## 5. A valid deterministic extension law

Let `d` be a declared metric on representation values. Suppose total learned and fallback losses satisfy

`|L(x)-L(z)|<=K_L d(x,z)` and `|F(x)-F(z)|<=K_F d(x,z)`.

Then `Delta` is Lipschitz with any registered `K_Delta>=K_L+K_F`; a smaller directly proved constant is also admissible. For a nonempty anchor set `T` with exact relative losses, define

`A_T(x)=max_(z in T) [Delta(z)-K_Delta d(x,z)]`,

`U_T(x)=min_(z in T) [Delta(z)+K_Delta d(x,z)]`.

### Theorem C-R18.4 — exact Lipschitz relative extension

For every state `x`,

`A_T(x)<=Delta(x)<=U_T(x)`.

Consequently `U_T(x)<=0` is a deterministic fallback-safe certificate and `A_T(x)>=0` is a deterministic learned-safe certificate.

#### Proof

For every anchor `z`, Lipschitz continuity gives

`Delta(z)-K_Delta d(x,z)<=Delta(x)<=Delta(z)+K_Delta d(x,z)`.

Taking the maximum of all lower bounds and the minimum of all upper bounds proves the claim. ∎

If `A_T>U_T`, the registered metric, constant, or data are inconsistent and the checker must fail closed. The theorem does not authorize estimating `K_Delta` after seeing test outcomes.

### Theorem C-R18.5 — anchor monotonicity and sign-margin coverage

If `T subseteq T'`, then

`A_T(x)<=A_T'(x)` and `U_T'(x)<=U_T(x)` for every `x`.

Hence the deterministically certified learned-safe and fallback-safe sets can only expand when valid anchors are added. A fallback sign certificate transfers exactly when the upper margin reaches zero; a learned sign certificate transfers when the lower margin reaches zero.

#### Proof

Adding anchors adds candidates to the maximum defining `A` and to the minimum defining `U`. The stated inequalities and sign-set inclusion follow. ∎

An underestimated Lipschitz constant may reverse a route verdict. Such a constant is a hostile invalid-certificate control, not a sensitivity setting that may be selected post outcome.

## 6. Acquisition timing is part of the decision problem

Let `c(x)>=0` be the cost of an acquired representation, `G(x) in {0,1}` choose learned when one and fallback when zero, and assume the fallback terminal action is otherwise identical in the two timings.

A post-acquisition controller pays for the representation before routing:

`S_post(x)=c(x)+G(x)L(x)+(1-G(x))F(x)`.

If the same route decision is available before acquisition, a pre-acquisition controller pays only on learned paths:

`S_pre(x)=G(x)[c(x)+L(x)]+(1-G(x))F(x)`.

### Theorem C-R18.6 — exact pre/post acquisition identity

For every state,

`S_post(x)-S_pre(x)=(1-G(x))c(x)`.

Therefore post-acquisition rejection loses exactly the feature charge on every fallback path; no valid accounting rule may refund it after the route decision.

#### Proof

Subtract the displayed definitions and collect terms. ∎

This identity compares two policies only when the route decision can actually be made from pre-acquisition information. The next theorem gives the exact finite criterion.

## 7. When can a route be moved before acquisition?

Let `Phi_0` be the information available before paid acquisition. A pre-acquisition deterministic route is any function of `Phi_0(x)`.

### Theorem C-R18.7 — finite route measurability criterion

A route map `G:X->{0,1}` can be implemented before acquisition using exactly `Phi_0` if and only if `G` is constant on every attained `Phi_0` fibre.

#### Proof

If `G=g o Phi_0`, equal `Phi_0` values imply equal routes. Conversely, if `G` is constant on each fibre, define `g(y)` to be that common value for every attained `y`; then `G=g o Phi_0`. ∎

If the criterion fails, a post-acquisition gate cannot be relabeled as a pre-acquisition router. The correct object is the R12 statewise profile Bellman controller, which explicitly prices acquisition before the additional observation exists.

### Theorem C-R18.8 — unbounded acquisition-timing gap

For every `M>0`, there is a one-state same-unit routing problem in which post-acquisition rejection has loss `M` and the corresponding pre-acquisition fallback has loss `0`.

#### Proof

Take one state, `c=M`, `G=0`, and fallback terminal loss zero. Theorem C-R18.6 gives the gap `M`. ∎

Thus timing is not a lower-order implementation detail. The gap is unbounded even without prediction error, distribution shift, or representation ambiguity.

## 8. Transfer requires a registered drift margin

Suppose a source state `z` and target state `x` are linked by a content-bound bridge, and a registered drift budget satisfies

`|Delta_target(x)-Delta_source(z)|<=tau(x,z)`.

If the source relative certificate is `[A_s(z),U_s(z)]`, define the transported interval

`[A_s(z)-tau(x,z), U_s(z)+tau(x,z)]`.

### Theorem C-R18.9 — drift-aware route-certificate transfer

The transported interval contains `Delta_target(x)`. A source fallback certificate transfers only when

`U_s(z)+tau(x,z)<=0`,

and a source learned certificate transfers only when

`A_s(z)-tau(x,z)>=0`.

#### Proof

The source certificate contains `Delta_source(z)`, and the drift condition moves that value by at most `tau`. The expanded interval therefore contains the target value. The sign conditions are exactly Theorem C-R18.2 applied to the transported interval. ∎

A sign may flip whenever the source margin is no larger than the allowed drift. Applying one model configuration across scenarios is not successful certificate transfer unless the bridge and drift budget are independently justified.

## 9. Closed internal theory story

The FiberGuard route story is now a single fail-closed chain:

1. complete finite fibres give exact transductive action-regret certificates;
2. state-dependent acquisition requires R12 loss profiles rather than a scalar refund;
3. R13 separates deterministic/pathwise and randomized expected authority;
4. R14 refutes exact-equality induction on SAT12-ALL;
5. R15 separates recurrence, certificate validity, and paid decision value;
6. R16 shows marginal learned-action calibration can coexist with harmful fallback alignment;
7. R17 identifies the exact rejected-set alignment obligation and paired action certificates;
8. R18 supplies the relative-order, timing, observability, structural-extension, and transfer laws needed for a valid router.

This closes the internal finite theory architecture. It does not close the application or publication gates.

## 10. Required decisive experiment

The next application must freeze before outcomes:

- one learned action and at least one fallback or route action;
- absolute total-loss and direct relative-loss predictors;
- a paired calibration rule and one declared failure budget;
- a pre-acquisition information map and a post-acquisition information map;
- action-specific acquisition costs;
- no-route, one-sided abstention, paired-upper, direct-relative, pre-acquisition Bellman, and oracle-route arms;
- strongest current algorithm-selection baselines;
- one untouched non-SAT or production-derived portfolio.

It must report absolute loss, relative-sign validity, feature cost, rejected and deployed subset alignment, robust, tail, and mean outcomes, route measurability, and every case where source margins fail under registered transfer drift.

The experiment is not executed in this tranche. A null or sign-reversal result remains admissible.

## 11. Prior-art and authority boundary

Generic selective classification, expert deferral, contextual routing, conformal intervals, Lipschitz extension, covariate or domain shift, and value-of-information dynamic programming receive no novelty credit. The residual candidate is their exact integration with complete-fibre action regret, one statewise solver oracle, state-dependent acquisition profiles, direct relative-action receipts, prospective sign reversals, and explicit authority separation between closed-world, structural, and statistical certificates.

Analytic proofs carry the theorem statements. The finite verifier is implementation corroboration only. `paired_ASlib_experiment_executed=false`, `non_SAT_transfer_executed=false`, external independence and novelty remain `CANNOT_CHECK`, and journal authority remains false.
