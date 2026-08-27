# FiberGuard R17 — fallback alignment and paired route certificates

Date: 2026-08-26

Status: analytic response to the prospectively frozen R16 null terminal. Generic selective prediction, reject-option classification, learning to defer, expert routing, cost-sensitive classification, and conformal risk control are donor-owned. The FiberGuard-specific object is the exact oracle-relative loss comparison between a learned solver action and its declared fallback, including acquisition timing and two-sided route certificates.

## 1. The blocker exposed by R16

R16 transferred one split-conformal selected-action certificate construction from SAT16-MAIN to SAT18-EXP and the untouched SAT20-MAIN. The empirical joint false-certificate rate stayed below the frozen `alpha+0.02` check on all three subjects. Yet no SAT16 development configuration met the selective-value gate, and the validation and untouched-test gates were false.

The failure was not simply poor learned prediction. The full learned selector reduced mean total excess relative to the robust fallback on all three scenarios. The failure was **fallback misalignment**: on the certificate-rejected SAT16 and SAT18 cases, the fallback was much worse than the learned action. On SAT20 the sign reversed slightly.

A certificate for the learned action answers whether that action is below a declared tolerance. It does not answer whether a fallback, expert, exact solver, or abstention action is better on the rejected subset. R17 formalizes this independent obligation.

## 2. Common-oracle setup

Let `X` be a finite panel or a random state under a declared distribution. Let

- `L(X)` be the complete terminal excess loss of the learned action;
- `F(X)` be the complete terminal excess loss of the fallback or route action;
- `G(X) in {0,1}` be the deployment indicator, with `G=1` choosing the learned action and `G=0` choosing fallback.

All terminal losses use one statewise oracle baseline. If an absolute route cost is `D_abs(x)`, then its FiberGuard terminal loss is `D_abs(x)-C*(x)`. The selected terminal loss is

`S(X)=G(X)L(X)+(1-G(X))F(X)`.

This section first compares terminal losses after any common representation cost has already been paid. Section 9 restores acquisition timing.

The same formulas apply to deterministic action regret or to statewise expected regret of a declared mixed action. An expected-loss certificate does not imply pathwise or tail safety.

## 3. Exact fallback-alignment identities

Let `R={x:G(x)=0}` be the rejected set and let `r=P(R)`.

### Theorem C-R17.1 — exact mean alignment identity

`E[S-L] = r E[F-L | R]`.

Therefore the selective policy has strictly smaller mean terminal loss than the full learned policy if and only if

`E[F-L | R] < 0`

on a positive-probability rejected set.

#### Proof

Pointwise,

`S-L=(1-G)(F-L)`.

Taking expectations and conditioning on `R` proves the identity. The strict criterion follows immediately. ∎

Calibration, rejection coverage, and fallback alignment are therefore separate quantities. A perfectly calibrated rejection rule can increase loss whenever the fallback is conditionally worse on rejected states.

### Corollary C-R17.2 — exact binary adverse-event identity

For any binary action-level event `H(a,x)`, let `H_L(X)` and `H_F(X)` be its indicators under learned and fallback actions. Then

`P(H_S)-P(H_L) = r E[H_F-H_L | R]`.

The selective policy lowers catastrophic wrong-action rate if and only if the fallback has lower catastrophic rate on the rejected subset.

The event may be “selected solver is PAR10 while the statewise oracle is not PAR10,” but the identity is generic.

### Theorem C-R17.3 — exact robust alignment identity

On a finite panel,

`max_x S(x) = max { max_(x:G=1) L(x), max_(x:G=0) F(x) }`,

with the maximum of an empty set omitted.

Let `V_L=max_x L(x)`. The selective policy strictly improves the robust value over the full learned policy if and only if both

`max_(G=1) L < V_L`

and

`max_(G=0) F < V_L`.

#### Proof

The first identity partitions the panel by the two route decisions. The selected maximum is below `V_L` exactly when both partition maxima are below `V_L`. ∎

Rejecting the learned worst case is not enough. The fallback loss on every rejected state must also remain below the original learned maximum.

## 4. Oracle contextual routing and heterogeneity value

Suppose both terminal losses were known before routing. The pointwise oracle route selects the smaller loss and has profile

`O(x)=min{L(x),F(x)}`.

### Theorem C-R17.4 — exact contextual routing gains

`E[L-O]=E[(L-F)_+]`

and

`E[F-O]=E[(F-L)_+]`.

Thus the oracle route weakly beats both fixed actions in mean. It strictly beats both exactly when the learned action is strictly better on a positive-mass set and the fallback is strictly better on a positive-mass set.

#### Proof

The identities are the pointwise equalities

`L-min(L,F)=(L-F)_+`

and

`F-min(L,F)=(F-L)_+`.

Take expectations. ∎

This is donor decision theory, but it identifies the empirical target for FiberGuard routing: the sign and magnitude of the conditional difference `F-L`, not learned-action uncertainty alone.

## 5. Optimal rejection at fixed coverage

On a finite panel of `n` states define

`Delta_i=F_i-L_i`.

If exactly `k` states must be rejected, the mean selected loss differs from full learned loss by

`(1/n) sum_(i in R) Delta_i`.

### Theorem C-R17.5 — fixed-cardinality optimal rejection

Among all rejection sets of cardinality `k`, mean terminal loss is minimized by rejecting the `k` states with the smallest values of `Delta_i`, with deterministic index ties.

#### Proof

For any set that contains `j` but omits `i` with `Delta_i<Delta_j`, swapping `j` for `i` strictly lowers the sum. Repeating exchanges yields the sorted prefix. ∎

A confidence score is an optimal rejector for mean loss only when it orders states compatibly with fallback-minus-learned loss. R16 shows that selected-action conformal uncertainty need not have that ordering.

For a rejection budget of at most `k`, reject exactly the negative `Delta_i` values among the first `k`; rejecting a state with positive `Delta_i` worsens mean terminal loss.

## 6. A learned-action certificate cannot bound fallback harm

### Theorem C-R17.6 — single-action certificate impossibility

Fix any learned loss profile, any learned-action certificate, and any rejection rule that rejects at least one state. Without a restriction on fallback loss, for every `M>0` there exists a fallback profile that leaves the learned profile, learned certificate, and route decisions unchanged but increases selected mean loss by at least `M/n` and selected robust loss by at least `M` on a rejected state.

#### Proof

Choose one rejected state and assign fallback loss `M` above its learned loss there, leaving all other fallback losses arbitrary. The learned action and its certificate are unchanged because they contain no fallback information. The selected policy uses fallback on that state, producing the claimed increases. ∎

No calibration theorem for the learned action alone can establish safe deferral. The fallback must be known, modeled, bounded, or separately certified.

## 7. Paired upper certificates

Let `U_L(x)` and `U_F(x)` be upper certificates for learned and fallback terminal losses.

### Theorem C-R17.7 — pointwise paired-upper routing

On the simultaneous-validity event

`L(x)<=U_L(x)` and `F(x)<=U_F(x)`,

choose the action with smaller upper certificate. Then the routed loss obeys

`S_U(x) <= min{U_L(x),U_F(x)}`.

#### Proof

If the route chooses learned, then `U_L<=U_F` and `S_U=L<=U_L=min(U_L,U_F)`. The fallback case is symmetric. ∎

This route minimizes the available certified upper loss among the two actions. It need not minimize realized loss when the bounds are loose.

### Corollary C-R17.8 — separate certificates pay a union budget

If

`P(L>U_L)<=alpha_L`

and

`P(F>U_F)<=alpha_F`,

then the paired route violates its selected upper certificate with probability at most

`alpha_L+alpha_F`.

This is a union-bound guarantee. Marginal certificates for the two actions do not generally share one `alpha` budget.

### Theorem C-R17.9 — joint paired-residual calibration uses one budget

Suppose proper training fixes predictions `Lhat,Fhat`, and calibration scores are

`s_i=max{L_i-Lhat_i, F_i-Fhat_i}`.

Let `q_alpha` be the usual split-conformal upper quantile and define

`U_L=Lhat+q_alpha`, `U_F=Fhat+q_alpha`.

Under exchangeability,

`P(L<=U_L and F<=U_F) >= 1-alpha`.

Consequently the paired route in Theorem C-R17.7 has one joint failure budget `alpha`.

#### Proof

The future paired score is exchangeable with calibration scores after proper training. The split-conformal rank argument gives `s_future<=q_alpha` with probability at least `1-alpha`, which is exactly simultaneous validity of both upper bounds. Apply Theorem C-R17.7. ∎

Joint calibration can be more economical than a union bound, but it may produce wider bounds because it calibrates the worse residual of the pair.

## 8. Certified no-harm switching requires interval separation

Upper bounds alone certify absolute loss, not improvement relative to the action being replaced. Let `[A_L,U_L]` and `[A_F,U_F]` be simultaneous valid lower/upper intervals.

### Theorem C-R17.10 — interval-separated no-harm routing

A switch from learned to fallback is certified not to increase terminal loss whenever

`U_F <= A_L`.

A switch from fallback to learned is certified not to increase terminal loss whenever

`U_L <= A_F`.

If neither separation holds, retain the declared default or acquire more information; the intervals do not certify an ordering.

#### Proof

On simultaneous validity, `F<=U_F<=A_L<=L` in the first case. The second is symmetric. ∎

This is stronger than choosing the smaller upper bound. The paired-upper rule certifies a small selected loss; interval separation certifies a pairwise improvement.

An equivalent route can use a direct upper certificate `U_Delta` for `F-L` and switch to fallback only when `U_Delta<=0`.

## 9. Acquisition timing and the no-refund rule

If the learned and fallback actions are compared only after a common feature representation has been acquired, the common statewise acquisition charge cancels from Theorems C-R17.1--C-R17.5.

If fallback uses no acquired representation but the controller first acquires features and then rejects, feature cost is sunk on both deployed and rejected paths. Relative to a no-acquisition fallback, R15 applies:

`E[L_selective-L_no_feature_fallback]`

`=E[feature cost] - P(deploy) E[action saving | deploy]`.

Rejecting after acquisition does not refund the feature charge.

If the route decision is made before acquiring the expensive representation, the controller must compare the statewise future profiles in the R12 Bellman state. A scalar expected cost or post-outcome refund is not exact under state-dependent charges.

A route to an exact solver may itself have state-dependent cost. Its absolute runtime enters as excess over the same statewise virtual-best oracle, never as an unbaselined defer constant.

## 10. Exact interpretation of R16

R16 compares a full learned selector with a selective version that uses the same learned action on deployed states and the robust fallback on rejected states. Therefore Theorem C-R17.1 applies exactly.

### SAT16 development

- deployment coverage `0.6751824817518248`;
- rejection rate `0.3248175182481752`;
- selective minus full mean `1622.197547445255`;
- implied fallback-minus-learned mean on rejected states `4994.18121348314`;
- implied catastrophic-rate difference on rejected states `0.101123595505618`.

The fallback was substantially worse on the rejected subset.

### SAT18 validation

- deployment coverage `0.8583569405099151`;
- rejection rate `0.1416430594900849`;
- selective minus full mean `3768.282222787025`;
- implied fallback-minus-learned mean on rejected states `26604.0724928764`;
- implied catastrophic-rate difference on rejected states `0.54`.

The certificate identified difficult learned actions, but the robust fallback was even worse on those cases.

### SAT20 untouched test

- deployment coverage `0.68`;
- rejection rate `0.32`;
- selective minus full mean `-219.74631665`;
- implied fallback-minus-learned mean on rejected states `-686.70723953125`;
- implied catastrophic-rate difference on rejected states `-0.015625`.

Here the fallback was slightly better on rejected cases. The sign reversal is preserved rather than used for retuning.

## 11. Corrected controller architecture

The post-R16 controller has four independent objects:

1. a predictor or certificate for learned-action loss;
2. a predictor or certificate for fallback/route loss;
3. a comparison rule with an explicit absolute-loss or no-harm guarantee;
4. acquisition timing represented in the R12 loss-profile Bellman state.

A one-sided learned-action threshold is insufficient.

Required future arms are:

- full learned selector;
- global robust fallback;
- one-sided learned-action abstention;
- paired-upper routing;
- interval-separated no-harm routing;
- direct difference-certificate routing;
- oracle contextual route;
- strongest current algorithm-selection baseline.

Report learned and fallback losses on deployed and rejected subsets separately. Aggregate calibration without rejected-subset alignment is incomplete.

## 12. Prior-art and novelty boundary

Reject-option classification already studies risk--coverage tradeoffs. Learning-to-defer already models prediction versus expert cost and learns routing functions. Post-hoc deferral explicitly compares base-model error probability with expert cost. Conformal risk control and modern selective prediction already study marginal, group, and post-selection guarantees.

FiberGuard therefore does not claim abstention, expert routing, loss-difference learning, interval comparison, or conformal calibration as generic novelty.

The residual candidate is the exact combination of:

- one common statewise oracle for solver actions, fallback, and route cost;
- state-dependent acquisition profiles;
- complete-fibre and probabilistic action certificates kept as distinct authority classes;
- exact fallback-alignment identities for mean, adverse-event, and robust loss;
- small paired upper/lower route receipts;
- and a prospectively preserved sign reversal across solver portfolios.

## 13. Verification and authority

`verify_fiberguard_fallback_alignment_r17.py` checks:

- 5,000 exact mean, binary-event, robust, and strict-improvement identities;
- 1,000 finite systems and 74,676 explicit fixed-cardinality rejection subsets;
- 3,000 paired-certificate systems and 39,338 state checks for each certificate construction;
- 2,704 systems where contextual routing strictly beats both fixed actions;
- 100 learned-certificate-only fallback attacks;
- and the exact R16 rejected-set decompositions.

The analytic proofs carry the theorem statements. Finite execution is implementation corroboration only. No paired fallback certificate has yet been executed on ASlib. Strongest-baseline comparison, non-SAT or production transfer, external reproduction, novelty adjudication, production value, and journal authority remain open.
