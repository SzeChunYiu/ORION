# OSTC-T0–T23 theorem derivations V1

## Status vocabulary

- `PROVED_SCHEMA`: mathematical proof for the declared assumptions.
- `FINITE_INSTANCE`: bounded executable instance only.
- `EXTERNAL_CHECK`: proof-assistant or independent review still required.
- `EMPIRICAL_CHECK`: naturalistic/protected computation still required.

All T0–T23 theorem schemas below are derived. External and empirical checks do not reopen the definitions; they may refute assumption applicability or implementation correspondence.

## T0 — non-tautological operational semantics

**Statement.** `Admit_tau` is defined by primitive typed transition rules, while `ValidSANF` is a structural predicate on extracted witnesses. Neither is definitionally reducible to the other.

**Proof.** The operational semantics is specified before certificate extraction and contains only concrete premises: artifacts, validation records, bridge applications, authority records, support families, blockers, and receipts. Define extraction `N` by induction on the final admitting transition and reconstruction `R` by replaying the witnesses in topological order. T6 proves `R` sound and T7 proves `N` complete. Since operational traces exist without invoking `ValidSANF`, and malformed witness tuples can satisfy arbitrary Boolean summaries while failing replay, the equivalence is theorem-level rather than definitional. A mutant semantics `Admit:=V∧S∧E∧B` is separated by traces with missing bridge identity or invalid support lineage.

## T1 — donor-native conservativity

**Statement.** Let `pi_D` project an ORION state to a donor-native state. If every ORION-only rule either leaves donor coordinates unchanged or refines them through a donor-approved operation, then for every extended trace `t`,

\[
\pi_D(run_{ORION}(t,\Sigma))=run_D(\pi_D(t),\pi_D(\Sigma)).
\]

**Proof.** Induction on trace length. The empty trace is immediate. For the step, donor-native events commute by the embedding hypothesis; ORION-only events project to identity. Composition completes the induction. Any adapter changing a donor verdict when ORION coordinates are inert is a counterexample and invalidates the embedding.

## T2 — exact target-sufficiency fibre theorem

For finite `Omega`, `Phi:Omega->Z`, and `T:Omega->Y`:

\[
\exists g\;T=g\circ\Phi
\iff
\Phi(\omega)=\Phi(\omega')\Rightarrow T(\omega)=T(\omega').
\]

**Necessity.** Equal interfaces imply equal decoder input and therefore equal target output.  
**Sufficiency.** Define `g(z)` as the common `T` value on the nonempty fibre `Phi^{-1}(z)`. Fibre constancy makes `g` well-defined.  
**Countermodel.** Any mixed fibre is a minimal indistinguishable-state witness.  
**Construction guard.** Semantic sufficiency does not establish admissible construction; direct access to protected `T` is answer laundering.

## T3 — exact Bayes risk under an interface

Let `mu` be a probability mass on finite `Omega`. The optimal 0–1 target risk from `Phi` is

\[
R^*(\Phi)=\sum_z\left[\mu(\Phi^{-1}(z))-\max_y\mu(\{\omega:\Phi(\omega)=z,T(\omega)=y\})\right].
\]

**Proof.** Decisions on distinct fibres are independent. Within each fibre, the optimal deterministic action is the modal target; its error is total fibre mass minus modal mass. Summing gives the result. Randomization cannot improve 0–1 risk because the objective is linear over the simplex and attains its optimum at an extreme point.

## T4 — no silent scientific-authority amplification

Let `Cl_R(A)` be the least fixed point of registered sound rules. If `F` is authority-neutral and every output of `F` is either a representation-equivalent input or a conclusion already derivable under `R`, then

\[
Cl_R(F(A))\subseteq Cl_R(A).
\]

**Proof.** Induct on the closure rank of each conclusion from `F(A)`. Base outputs map to members of `Cl_R(A)` by authority-neutrality. For a rule conclusion, the induction hypothesis places every premise in `Cl_R(A)`; closure of `Cl_R(A)` under `R` yields the conclusion. Repetition, optimization, serialization, replay, agreement, provenance, valid signatures, and generic permission are therefore non-amplifying unless a registered scientific bridge consumes them.

## T5 — bridge necessity

If target `j` is outside `Cl_R(A)`, no finite sequence of authority-neutral transformations can establish `j`.

**Proof.** Repeated application of T4 yields a descending inclusion chain contained in `Cl_R(A)`. Hence `j` remains outside. Widening requires new authorized evidence, a new sound bridge, protected revalidation, or a protected coercion.

## T6 — SANF soundness

**Statement.** Every structurally valid six-witness certificate reconstructs an operational scientific advance.

**Proof.** Replay `pi_R` to obtain the relied-upon artifacts within budget. Replay each donor validator in `pi_V`. Check target-required integrity facts in `pi_X`. Use `pi_S` to obtain a target decision rule or mixed-fibre refusal. Apply the typed bridge and authority in `pi_E`. Validate one complete support family and blocker clearance in `pi_B`. The corresponding primitive admission rule is enabled, producing the target transition. Structural induction handles composed certificates.

## T7 — SANF completeness

**Statement.** Every operational scientific advance in `W-dagger` has a six-witness certificate.

**Proof.** Induct on the finite operational trace ending in the admitting event. Availability events form `pi_R`; native validation events form `pi_V`; execution and custody events consumed by the final rule form `pi_X`; the target decision interface used by the rule yields `pi_S`; the exact inference/identity/transport/promotion/revalidation/coercion/adoption rule and grant yield `pi_E`; the final complete support hyperedge and blocker records yield `pi_B`. Stratification and finite support ensure the extraction terminates. Alternative derivations produce alternative valid certificates rather than threatening completeness.

## T8 — factor independence and class-relative minimality

For every witness factor there is a matched countermodel in `W-dagger`:

- remove `R`: target lies outside method/retrieval closure;
- remove `V`: forged or invalid local artifact;
- remove `X`: right bytes but wrong/unbound occurrence when occurrence matters;
- remove `S`: identical interface, different correct terminals;
- remove `E`: valid evidence with wrong target scope/content/epoch/responsibility;
- remove `B`: unresolved blocker or all support families revoked.

All remaining factors are held fixed. Therefore no factor is eliminable from a class containing these models. This is minimality for `W-dagger`, not universal metaphysical minimality.

## T9 — scientific full abstraction

Two implementations `I,J` are scientifically fully abstract for responsibility family `R0` when

\[
obs_I(s)=obs_I(t)\iff obs_J(s)=obs_J(t)
\]

for every pair distinguished by some target terminal in `R0`. If both expose the same quotient partition and implement the same bridge rules, they induce identical target judgments.

**Proof.** Each target map factors through the common quotient by T2. Equality of quotient classes gives equal decoder inputs and equal terminals. This establishes ideal-product ties and forbids inherent centralization claims without an additional measurable property.

## T10 — certificate composition and coherence

Let `Pi_01` establish `j_1` from `j_0`, and `Pi_12` establish `j_2` from `j_1`. They compose exactly when the produced and consumed intermediate object, content, responsibility, scope, epoch, authority, and blocker contracts match or are related by a registered bridge.

Composition concatenates reachability/validity/integrity traces, composes sufficiency maps, composes entitlement bridges, and unions support while retaining unresolved blockers. Associativity follows from associativity of trace and relation composition; identity certificates are empty traces with reflexive bridges. Mismatched contracts yield a typed countermodel, not a coercion by convention.

## T11 — exact revocation with alternative support

Let `MinSup(j)` be the antichain of inclusion-minimal complete support families for `j`. Under revoked token set `R`,

\[
j\text{ survives}\iff\exists F\in MinSup(j):F\cap R=\varnothing.
\]

**Proof.** If such `F` exists, all its premises remain and the derivation replays. Conversely every valid derivation contains a complete support family; minimizing it gives an element of `MinSup(j)` disjoint from `R`. If none exists, every derivation has a revoked premise.

## T12 — finite-history open-world closure impossibility

If a workflow class contains two worlds with identical finite observable history `h` but different correct closure terminals, no deterministic history-only rule is sound on both.

**Proof.** The rule receives the same `h` and returns one terminal. It disagrees with at least one world. Under equal prior, its error is at least `1/2`. Positive closure therefore requires a coverage model, bounded universe, capture assumption, or protected witness.

## T13 — regime transport and path dependence

For regime morphisms `f:rho0->rho1` and `g:rho1->rho2`, transport is path independent iff every load-bearing coordinate satisfies a commuting coherence square and

\[
T_{g\circ f}\cong T_g\circ T_f.
\]

**Proof.** If the squares commute, structural induction on the certificate shows both paths map every witness identically up to isomorphism. If one square fails, choose an object supported on the differing coordinate; the two paths produce different obligations or terminals, yielding a path-dependence countermodel.

## T14 — intervention identifiability of failure location

Let causes be rows of an intervention-response matrix `H` and available interventions be columns. A cause is exactly identifiable iff its row is distinct from every other row on the selected columns.

**Proof.** Equal restricted rows are observationally indistinguishable. Distinct rows admit lookup decoding. A minimum diagnostic experiment set is therefore a minimum separating column set, reducible to set cover/hitting set.

## T15 — method-closure obstruction and certified expansion

Let `Cl(L)` be the least closure of seeds under legal operations. An obstruction certificate for target `t` is sound iff it binds the complete closure semantics and proves `t notin Cl(L)`. An extension `e` is genuinely semantic for `t` iff

\[
t\notin Cl(L),\quad e\notin Cl(L),\quad t\in Cl(L\cup\{e\}).
\]

**Proof.** Closure membership is by least-fixed-point induction. Search, repair, synthesis, or evolution restricted to `L` cannot reach a target outside `Cl(L)`; adding an operator whose behavior is already in `Cl(L)` is only a macro.

## T16 — state/computation placement phase law

For one-time compilation cost `K`, direct per-query cost `d`, compiled per-query cost `c`, and horizon `U`, compilation dominates iff

\[
K+Uc<Ud.
\]

If `d>c`, the least integer horizon is

\[
U^*=\left\lfloor\frac K{d-c}\right\rfloor+1.
\]

For vector resources, dominance is Pareto or price-vector relative; no universal scalar crossover follows without prices. Future responsibility and recovery costs add explicit terms rather than disappearing.

## T17 — vector allocation and coarsening regret

With finite action set `A`, exact per-case cost vector and an independently supplied objective, selecting the minimum feasible action has zero hindsight regret. If two cases share the same visible certificate but have different unique optimal actions, every certificate-only deterministic allocator incurs positive regret on at least one; under equal prior its expected regret is at least half the smaller cross-action loss gap.

This is the allocation analogue of T12 and explains why exact hidden charge certificates cannot be silently assumed available.

## T18 — responsibility-relative state sufficiency

Let `Pi_r` be the partition induced by responsibility `r`. A state representation with partition `Pi_Z` is sufficient for `r` iff `Pi_Z` refines `Pi_r`. For responsibility family `R0`, the coarsest jointly sufficient partition is the common refinement `join_{r in R0} Pi_r`.

Safe reuse after responsibility change `r->r'` holds iff the stored state still refines `Pi_{r'}` and the regime/authority bridge is valid. Provenance freshness alone is neither necessary nor sufficient for responsibility support.

## T19 — reflexive-custody / self-promotion impossibility

Suppose a candidate controls both the evaluator predicate and all evidence read by it. Construct two external worlds: one where the candidate truly satisfies the protected property and one where it modifies evaluator/evidence to emit the same visible PASS while failing externally. The system-visible transcript is identical, so no internal gate can distinguish the worlds. Sound nontrivial adoption therefore requires at least one protected invariant, evaluator, evidence channel, or adoption authority outside candidate control.

## T20 — execution/science noninterference

Model state as product `E x V x A` for execution facts, scientific validity, and scientific authority. An execution-only transformation is `(f,id,id)`. Therefore it cannot alter validity or authority. A bridge may read `E` and update `V` or `A`, but the bridge and assumptions are explicit premises. Valid signatures prove only the signed relation under key assumptions; full key compromise provides the standard countermodel.

## T21 — governed recursive evolution

If every adopted change carries a valid evolution certificate and strictly decreases a well-founded rank `rank(H,Obl)` or consumes a finite protected budget, no infinite adoption sequence exists.

**Proof.** An infinite sequence would induce an infinite descending chain in a well-founded order or infinitely consume a finite budget, both impossible. Proposal generation may be unbounded; adoption is not.

## T22 — synthesis/checking complexity separation

For a finite certificate language, checking a supplied derivation is polynomial in certificate and rule size. Finding a certificate can be NP-hard: encode a CNF formula as a method problem whose candidate artifacts are assignments and whose target bridge is enabled exactly by satisfying assignments. Verification is polynomial; existence is SAT. Richer method languages may make synthesis undecidable while proof checking remains decidable.

## T23 — coupled scientific advance

\[
ScientificAdvance_{\mathcal C}(\Sigma,j)
\iff
Available_{\mathcal C}(\Sigma,j)\land Admit(\Sigma,j).
\]

This follows from the operational definition and T6–T7. Independence is witnessed by two countermodels: a reachable but scientifically unauthorized result, and a scientifically well-specified target outside the current method/retrieval closure. More compute cannot replace missing authority; stronger governance cannot manufacture unreachable methods.

## Final theorem terminal

```text
OSTC_T0_T23_THEOREM_SCHEMAS_COMPLETE_FOR_W_DAGGER
IMPLEMENTATION_AND_REAL_DOMAIN_APPLICABILITY_PENDING
```
