# ORION-23 top-tier theory expansion V1 — responsibility-scoped support and certified reuse

**Programme:** #977  
**Boundary:** exact support, transport/revocation and approximate calibration theory only. Real verifier-backed and research-agent responsibility shifts remain separate promotion gates.

## T13.1 — learner-free responsibility-indexed support

Let raw world/state be `x in X`, representation `S:X->Z`, and responsibility-specific externally defined gold behavior be `G_r:X->Y_r`.

Define the representation equivalence relation

\[
x\sim_S x' \iff S(x)=S(x').
\]

`S` **exactly supports responsibility `r`** iff

\[
x\sim_S x' \Rightarrow G_r(x)=G_r(x')
\]

for every pair `x,x'`.

Equivalently, `G_r` factors through `S`: there exists `h_r` with `G_r=h_r\circ S`. This is a state property relative to the responsibility, not a conclusion from one weak learner's performance.

### Responsibility implication

Define `r2 >= r1` only when the gold partition induced by `G_r2` refines the partition induced by `G_r1`; i.e. equality under `G_r2` implies equality under `G_r1`.

If `r2 >= r1` and `S` supports `r2`, then `S` supports `r1`.

The converse need not hold. If neither gold partition refines the other, responsibilities are incomparable and ORION-23 must preserve the partial order rather than force a ladder.

## T13.2 — certificate transport and revocation

A responsibility-support certificate binds at minimum

`(representation/compiler identity, source/evidence identity, responsibility set, epoch/context, omitted distinctions, recovery route, resource envelope, independent witness)`.

Consider representation transport `T:Z->Z'`, giving new state `S'=T\circ S`.

### Safe transport condition

For responsibility `r`, an exact support certificate transports from `S` to `S'` iff every class merged by `T` remains homogeneous under `G_r` and every bound source/epoch/context coordinate declared `required_same` remains unchanged (or has a separately authorized transport witness).

Equivalently:

\[
S'(x)=S'(x') \Rightarrow G_r(x)=G_r(x').
\]

If `T` merges two old state classes with different `G_r` values, the certificate must be revoked/reopened for `r` even if provenance and confidence remain valid.

### Responsibility upgrade

A certificate for `r1` does not transport automatically to a stricter or incomparable `r2`. Upgrade is permitted only after the support condition for `r2` is independently established.

### Recovery loss

If the certificate promises reopening through a raw-recovery route and that route becomes unavailable/stale, the *support fact* may remain mathematically true while the *safe reuse contract* must be downgraded because its registered failure/recovery semantics changed.

## T13.3 — approximate support with prospectively calibrated risk

For approximate settings, define a fixed sampling/calibration procedure yielding iid collision tests

`Z_i = 1{S(X_i)=S(X'_i) and G_r(X_i) != G_r(X'_i)}`

under a prospectively specified pair distribution. Let true collision-risk be `p_r=E[Z_i]` and empirical rate be `p_hat` over `n` tests.

For confidence parameter `alpha in (0,1)`, Hoeffding gives

\[
P\left[p_r > \hat p + \sqrt{\frac{\log(1/\alpha)}{2n}}\right] \le \alpha.
\]

Define the conservative upper certificate

\[
U_r=\min\left(1,\hat p+\sqrt{\frac{\log(1/\alpha)}{2n}}\right).
\]

A state receives approximate support at tolerance `delta` only if `U_r <= delta`, where `alpha`, `delta`, pair distribution and sample count are frozen before protected outcomes.

This is a statistical certificate for the declared pair distribution, not universal semantic sufficiency. Distribution shift or changed responsibility reopens calibration authority.

## Safety-cost consequence

If an exact/approximate responsibility certificate authorizes reuse only within its supported responsibility set, then a system can avoid both failure modes:

- **unsafe reuse:** reusing state after a responsibility/semantic change not covered by the certificate;
- **always-reopen degeneration:** discarding compact state even when the certificate remains valid.

The empirical ORION-23 top-tier claim requires demonstrating an interior point with lower unsafe reuse than unqualified/confidence/provenance baselines and lower resource cost than always-raw/reopen.

## Cross-paper boundary

ORION-23 consumes ORION-16/ORION-17/ORION-18 transition/transport/authority interfaces only as frozen upstream semantics. ORION-23's owned object is whether a specific state supports a named responsibility and whether that support/recovery contract survives a state/evidence/context change.
