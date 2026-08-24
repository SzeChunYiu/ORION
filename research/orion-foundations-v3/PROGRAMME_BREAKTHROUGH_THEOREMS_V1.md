# Programme-level breakthrough theorems V1

These theorems compress the P1–P15 programme into a small number of field-level laws. They are consequences of the OSTC formalism under the stated assumptions; empirical importance and external novelty remain separate questions.

## B1 — Scientific status non-fungibility

Let `q_a` be a locally valid terminal about object/responsibility `a`, and `q_b` a target terminal about distinct object/responsibility `b`. Let `F` be any sequence of authority-neutral operations. If there is no registered sound bridge from the discharge closure of `a` to `b`, then

\[
q_b\notin Cl_R(F(q_a)).
\]

**Proof.** OSTC-T4 and T5.

**Meaning.** Correct execution, high confidence, local verification, provenance, planning success, permission, or agreement is not a fungible currency exchangeable for arbitrary scientific standing. Each status transition has its own target relation.

## B2 — The two-barrier law of scientific advance

For a candidate judgment `j`, scientific advance requires both:

\[
Available_{\mathcal C}(j)
\quad\text{and}\quad
Admit(j).
\]

Neither implies the other.

**Proof.** OSTC-T23 plus two witnesses:

1. reachable but unsupported/unauthorized result;
2. well-specified admissible target outside the current information/method closure.

**Corollaries.**

- more compute cannot repair missing evidence or authority;
- stronger governance cannot produce an unreachable method/result;
- P9–P12 optimize availability while P4/P6–P8/P13–P15 constrain admission;
- a complete scientific agent must diagnose which barrier is active before acting.

## B3 — Dual expansion theorem: formulation versus method

Let a task be defined by target terminal map `T`. Let `Π_Φ` be the partition induced by the current formulation/interface and `Cl(L)` the current method closure.

A failure can be structurally separated into:

1. **formulation obstruction:** `T` does not factor through `Φ`;
2. **method obstruction:** `T` factors through `Φ`, but the required artifact is outside `Cl(L)`;
3. **resource obstruction:** the artifact lies in `Cl(L)` but outside the bounded reachable set;
4. **admission obstruction:** the artifact is available but SANF witnesses fail.

P1 changes `Π_Φ`; P10 changes `Cl(L)`. These are dual but non-substitutable expansions.

**Proof.** T2 classifies formulation insufficiency; T15 classifies method closure; capability semantics separates resource reach; T23 separates admission.

**Decision law.** A sound controller gives first refusal in the order:

```text
check information sufficiency
→ check old method closure
→ check bounded resources
→ check scientific admission
→ mutate only the first failed layer
```

This prevents expensive method invention for a representation problem and prevents endless compute escalation for an outside-closure target.

## B4 — Responsibility–resource frontier theorem

For responsibility family `R`, let

\[
\Pi_R=\bigvee_{r\in R}\Pi_r
\]

be the coarsest exact decision partition. Any exact reusable state must refine `Π_R`. Among such states, computation placement induces a Pareto frontier over:

```text
acquisition,
transformation,
compiler work,
state memory/update,
downstream reasoning,
verification,
cache/recovery,
latency,
future responsibility coverage.
```

No state can lie below the information lower bound, and no universal scalar optimum exists without prices.

**Proof.** T18 gives the information lower bound; T16 gives placement tradeoffs; T17 gives allocation limits under coarsened signals.

**Corollaries.**

- P9 identifies which frontier coordinate is binding;
- P11 chooses an offline state/compute placement;
- P12 allocates resources online;
- P13 determines whether the resulting state remains sufficient under changed responsibility;
- a compact state can be optimal now and harmful to future optionality.

## B5 — Protected-root theorem for recursive science

No recursively self-modifying scientific system can obtain sound nontrivial adoption authority solely from predicates and evidence it may rewrite. At least one protected root must remain outside candidate control:

```text
evaluator identity,
protected evidence,
constitutional invariant,
external adoption authority,
or an equivalent unforgeable boundary.
```

If every adopted change additionally decreases a well-founded rank or finite budget, the adopted sequence terminates.

**Proof.** T19 indistinguishability plus T21 well-founded descent.

**Corollaries.**

- P5 self-improvement and P14 governance share one custody theorem;
- internal diagnosis may guide search but cannot become self-issued adoption;
- negative history is part of the protected state when it constrains recurrence;
- same-owner CI cannot be the final scientific authority.

## B6 — Layered integrity noninterference theorem

Let scientific state factor as

\[
Execution\times Validity\times Authority.
\]

Any transformation acting only on execution coordinates preserves validity and authority. Therefore no combination of richer logs, replay, agreement, signatures, provenance transport, or receipt composition can create scientific truth or authorization unless an explicit bridge consumes those facts and supplies all missing scientific premises.

**Proof.** T20 and B1.

**Corollary.** P15 is not a receipt-format paper. Its theoretical object is the noninterference boundary and the exact assumptions under which a bridge from execution to science is sound.

## B7 — Scientific full-abstraction invariance

For any responsibility family, architectures exposing the same target-relevant quotient and sound bridge relation are extensionally equivalent on scientific decisions. An architectural superiority claim requires either:

- a strictly more informative admissibly constructed interface;
- a stronger sound bridge/evidence relation;
- a better resource/cost property;
- a better robustness or operational property.

Centralization, branding, or internal organization alone cannot create decision authority.

**Proof.** T2 and T9.

## B8 — Predictive completeness criterion

A foundational ORION claim becomes scientifically consequential only when the theory prospectively predicts all three types of outcomes on held-out families:

1. a failure caused by a missing factor;
2. a tie with an information-equivalent donor product;
3. a successful repair that restores exactly the missing witness without invalidating unrelated facts.

This is not a logical theorem but the programme’s empirical demarcation criterion. It prevents retrospective unification from being mistaken for predictive science.

## Programme headline to earn

> Scientific advance is governed by two independent barriers—availability and auditable admission. Availability depends on information, accessibility, method closure, computation, and placement; admission depends on native validity, occurrence integrity where required, target sufficiency, typed entitlement, and surviving support. Formulation and method expansion repair different obstructions, while governance and execution integrity remain irreducible protected layers.

The mathematical theory is fixed. The execution issue #1234 now tests whether these laws predict naturalistic scientific systems.
