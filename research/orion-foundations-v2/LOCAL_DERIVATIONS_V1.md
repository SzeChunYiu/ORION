# Local derivations for OSTC-T0 through OSTC-T23

**Authority:** exact only for the finite classes implemented in
`src/orion/foundations/`; no P-paper authority delta.

## Semantic foundation

**T0 — non-tautological semantics.** A state can have coarse declarations
`V=S=E=B=true` while the registered bridge binds content `y` rather than target
content `x`. The primitive transition therefore returns `DENY`. Admission is not
defined by four unbound booleans.

**T1 — native conservativity.** Artifacts are immutable. Scientific admission
reads but never rewrites a donor-native verdict, so the verdict is identical
before and after admission evaluation.

**T2 — exact fibre theorem.** For finite state set `S`, interface `Φ`, and target
`T`, a deterministic `g` with `T=g∘Φ` exists iff `T` is constant on every fibre
of `Φ`. Necessity follows by substitution. For sufficiency, choose one state in
each nonempty fibre and define `g` by its target; fibre constancy makes the choice
well-defined. The checker exhausts all 64 binary three-state interface/target
pairs and emits a minimal collision when the condition fails.

**T3 — approximate sufficiency.** Under finite mass `p` and 0–1 loss,

\[
R^*(\Phi)=1-\sum_z\max_y P(T=y,\Phi=z).
\]

A coarsening merges fibres. Since
`max_y(a_y+b_y) <= max_y a_y + max_y b_y`, coarsening cannot reduce target risk.

## Discharge normal form

Let `Cl_R(A)` be the least fixed point of registered monotone bridge rules.

**T4 — no silent amplification.** An authority-neutral step adds only elements
already in `Cl_R(A)`, so reclosing yields the same fixed point. Finite sequences
preserve it by induction.

**T5 — bridge necessity.** If target `j` is outside `Cl_R(A)`, T4 implies every
neutral prefix leaves `j` outside. New authorized evidence, a sound bridge, or
protected revalidation is necessary.

The finite operational workflow checks native validity/integrity, target
sufficiency, exact target/responsibility/scope/epoch authority, and one complete
support family with cleared blockers. A normal-form certificate records those
same witnesses as `Π=(πV,πS,πE,πB)`.

**T6 — soundness.** Independent validation of `Π` rechecks every primitive premise;
reconstructing `DISCHARGE` therefore yields `ESTABLISH`.

**T7 — completeness for the finite bridge class.** Any admitted transition has
passed every primitive check, so its read artifacts, interface, applied bridge,
authority, support family, and blocker resolutions can be extracted into a valid
`Π`.

**T8 — factor independence.** Across all 16 Boolean factor worlds, removing only
`V`, `S`, `E`, or `B` changes the clean `ESTABLISH` terminal to `DENY` or
`CANNOT_CHECK`. This is class-relative, not universal, minimality.

**T9 — scientific full abstraction.** The quotient mapping each state to its
target-equivalence class satisfies
`Φ(s1)=Φ(s2) iff T(s1)=T(s2)`. A richer identity interface is sufficient but not
minimal. A protected-gold read is mathematically sufficient but rejected by the
no-answer-laundering guard.

**T10 — composition.** Contracts compose only when intermediate type, content,
scope, epoch, responsibility, and authority agree. A one-coordinate content
mismatch is a countermodel.

**T11 — revocation.** Retain exactly complete support families disjoint from the
revoked artifact set. A judgment survives iff at least one complete family
remains. The witness has two independent supports: one revocation preserves the
judgment; two remove it.

## Open worlds and changing regimes

**T12 — closure impossibility.** Two equal-prior worlds have identical finite
history and opposite closure truth. A history-only deterministic rule emits one
common decision and is wrong in one world, so error is at least `1/2`.

**T13 — transport and path dependence.** A hop is locally sound only when evidence
semantics, objective semantics, and epoch binding are preserved. Two locally
sound paths can map the same source obligation to different target obligations;
path independence therefore needs an additional coherence bridge.

## Capability, computation, and responsibility

**T14 — diagnosis identifiability.** Causes are identifiable under selected
interventions iff their restricted response signatures are pairwise distinct.
Equal signatures are observationally inseparable; distinct signatures admit a
lookup decoder. The finite model separates information, access, compute, method,
and formulation causes.

**T15 — obstruction-certified expansion.** For finite method language `L`, a valid
extension `e` for target `t` requires

\[
t\notin Cl(L),\quad e\notin Cl(L),\quad t\in Cl(L\cup\{e\}),
\]

plus held-out reach. The affine-to-square witness satisfies all conditions.

**T16 — placement phase law.** With compile cost `F`, raw/query `r`, compiled/query
`c<r`, compiled state is no more expensive exactly when

\[
n\ge\left\lceil F/(r-c)\right\rceil.
\]

A declared recovery charge replaces `F` by `F+R`. The exact witness gives horizons
13 and 15.

**T17 — allocation sufficiency.** Two worlds share one coarse certificate but have
different optimal actions (`STATE`, `REASON`). No coarse policy is exact on both.
Revealing the cost state yields a sufficient certificate and exact selection.

**T18 — responsibility-relative state.** Responsibility `r2` refines `r1` when
equality under `r2` implies equality under `r1`. A prediction quotient merges
states that verification distinguishes; the join of both responsibility labels is
sufficient for both.

## Recursion and integrity

**T19 — reflexive custody impossibility.** Genuine improvement and evaluator gaming
share the same candidate-visible PASS record. No candidate-only gate separates
them. Protected fresh assurance does.

**T20 — execution/science noninterference.** Two cases have identical complete
execution-integrity vectors but terminals `ESTABLISH` and `BLOCK`. By T2,
execution integrity alone cannot identify scientific validity or authority.

**T21 — governed evolution.** A valid evolution certificate requires issue identity,
diagnosis/discriminator, candidate, isolation, replay, fresh transfer, protected
assurance, negative-history update, and external adoption. Deleting only external
adoption invalidates the certificate.

**T22 — synthesis/checking separation.** With `N` black-box candidates and one
unique valid candidate, an adversary marks the last candidate in any deterministic
search order, forcing `N` queries; checking a supplied witness needs one.

**T23 — coupled advance.** Define

\[
Advance(y)=Reachable(y)\land Admissible(y).
\]

The finite model realizes all four truth-table cells, proving neither capability
nor governance substitutes for the other.

## Local terminal

All T0–T23 checks plus the no-answer-laundering guard are `LOCAL_PROVED` in their
registered finite classes. Universal, naturalistic, proof-assistant, novelty, and
external-authority claims remain open or `CANNOT_CHECK` as listed in
`HEAVY_COMPUTE_BACKLOG_V1.md`.
