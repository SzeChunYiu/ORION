# P1-P5 umbrella synthesis: information-limited scientific authority

**Date:** 2026-08-23  
**Status:** programme theory; not a new empirical result

## 1. The common scientific object

P1-P5 now form one evidence-to-transition theory rather than five unrelated
architectures:

```text
scientific world
    |
    v
P2 acquisition-authority envelope
    |  acquired transcript, unresolved obligations, closure status
    v
P3 epistemic portrait envelope
    |  source-compatible global portraits and query identified sets
    v
P4 verification-axis envelope
    |  claim/terminal attainability, nuisance audit, panel resolution
    v
P1 epistemic transition envelope
    |  minimal admissible front of scientific changes
    v
P5 minimal method-revision envelope
    |  discriminator programme, challenger, fresh transfer, host disposition
    +-------------------------------> revised acquisition/integration/verification loop
```

The shared principle is:

> Scientific authority cannot increase merely because a downstream mechanism
> is more capable. It increases only when new evidence refines a decision fibre,
> a justified assumption removes worlds from it, or a separately authorized
> rule changes the admissible transition set.

This is wider than a named agent framework. It covers scientific search,
source integration, benchmark construction, belief/claim transition, and
failure-driven method evolution.

## 2. Stagewise sufficiency theorem

Let `W ~ mu` on a standard Borel latent-world space `Omega`; let the
stage-interface spaces also be standard Borel; let the stage maps and
nonempty finite-alphabet target `Y` be measurable; and let `S_i` be the
interface exposed after stage `i`. Suppose every later stage is a function only
of `S_i`: conditional on `S_i`, it receives no additional world-bearing
observation after that interface (the downstream chain is Markov with respect
to the target information).

### Theorem (stagewise sufficiency and irreversible collapse)

1. If each required stage output factors through the interface supplied to
   that stage, their composition implements the final target exactly.
2. If some interface `S_i` maps two worlds to the same value while the final
   target differs, no composition of later stages using only `S_i` can be exact.
3. Under zero-one loss, the best possible downstream error is at least the
   conditional Bayes impurity of the final decision inside the `S_i` fibres.

### Proof

The first claim follows by composition of the stagewise factor maps. For the
second, every later composition receives the same `S_i` value in the two worlds
and must return the same final decision, so it is wrong in at least one. For the
third, condition on `S_i`; no randomized rule can exceed the largest
conditional target probability in a fibre. Averaging the complementary
probability gives the bound.

This programme theorem explains why the same factorization boundary appears in
different scientific roles without making the papers duplicates:

- **P2:** closure cannot recover an unresolved material route erased by the
  acquisition/state interface.
- **P3:** global portrait queries cannot recover a source coordinate erased by
  the observation operator.
- **P4:** a verifier cannot emit or correctly choose a terminal absent from its
  representation or output alphabet.
- **P1:** a donor product cannot select an authorized transition when its
  interface merges different transition fronts.
- **P5:** a method reviser cannot choose a correct revision or promotion when
  same-symptom situations remain observationally equivalent.

### Comparator-terminal admissibility theorem

The comparator audit exposes a more general version of the same boundary. Let
`Y = Gamma(W)` be a finite nonempty target, and let an external system emit a
possibly stochastic output `Z` in a common standard-Borel measurable space,
with joint law induced by `W ~ mu` and a Markov kernel `K(dz | W)`. A measurable
terminal adapter `g : Z -> Y` has zero error almost surely if and only if `Y` is
measurable with respect to `Z`: equivalently, there is a measurable partition
`{A_y : y in Y}` such that

```text
K(A_Gamma(w) | w) = 1
```

for `mu`-almost every world. Under zero-one loss the best adapted error is

```text
1 - E[max_y P(Y = y | Z)].
```

For a deterministic system this reduces to decision constancy on its output
fibres. Pointwise exactness is stronger: the partition condition must hold for
every registered world, including distribution-null worlds. Therefore a
binary verdict, parse failure, empty answer, free-text caveat, or timeout may be
mapped to a three-way authority decision only when that observable output
actually determines the required terminal. A wrapper cannot create the missing
information.

This result turns comparator mismatch into a scientific object rather than an
implementation inconvenience. It governs P1 external transition agents, P2
retrieval-agent adapters, P3 ontology/schema comparators, P4
`CANNOT_CHECK`-capable verifiers, and P5 revision-level mechanisms.

### Active refinement of a mixed fibre

The static factorization boundary is not the end of the programme.  A mixed
decision fibre defines an acquisition problem: which licensed tests should be
run, in which order, at what cost, and when should the system decide or defer?
For the wider finite controlled-state model, let `g(w)` be the target,
`Pi` a fixed ex-ante credal set over worlds, `s` an observable laboratory
state, `E(s)` its legal acquisitions, `c(s,e)` their costs, and
`Q_{s,e}(o,s'|w)` the known joint outcome--next-state kernel.  Let
`Gamma_{n,s}` be the world-risk vectors of deterministic legal policy trees
using at most `n` acquisitions.  The donor-derived controlled policy-vector
recursion gives

```text
deterministic robust value = min_{v in Gamma_{n,s}} sup_{p in Pi} p.v
randomized robust value    = min_{v in conv(Gamma_{n,s})} sup_{p in Pi} p.v .
```

The state index is scientific, not cosmetic.  An unavailable or destructive
test cannot re-enter a plan merely because horizon remains; stochastic next
state is part of the observed transcript; and no-repeat or replenishment must
be encoded by legal state transitions.  Exact rational exhaustive-tree checks
cover seven such controlled witnesses.

For a singleton prior, scalarization yields the controlled posterior Bayes
Bellman equation, conditioning jointly on outcome and next state.  For an
arbitrary fixed nonrectangular prior set, retaining risk vectors until the root
preserves which posterior histories came from the same licensed prior.  A
posterior-local worst-case recursion instead solves the historywise-pasting
rectangular hull.  For a fixed policy these expectations agree for every
bounded loss exactly when the induced closed convex path-law family is already
stable under positive-history pasting.  Policy minima are attained on the
finite/convex policy frontier; a worst licensed prior need not exist when `Pi`
is nonclosed.

Exact finite discrimination remains a target-class transcript-singularity
question.  Positive KL without support separation may reduce approximate
error but cannot yield finite exactness.  Positive information-cost obligations
require strictly positive charged resources: two complementary zero-cost tests
can identify a target at total acquisition cost zero, so free histories must be
retained rather than assigned fabricated cost.

This is a wide common representation for P1 transition measurement, P3
credal envelopes, and P5 active discriminators, but the prior-art audit blocks
promotion as a new Bellman, alpha-vector, robust-POMDP, multiple-priors, or
adaptive-KL theorem.  Its scientific value is a donor-derived synthesis and
audit interface.  The stationary packet's eight failures, the adversarial
review's three scope witnesses, and controlled-state S1--S9 remain immutable
successor identities; overlapping diagnoses are not inflated into a fabricated
count of independent discoveries.

## 3. Division of scientific ownership

| Paper | General object owned | Strongest analytic advance | Empirical authority retained |
| --- | --- | --- | --- |
| P1 | Minimal admissible front over a well-founded partial order of scientific transitions | exact donor substitution; mixed-fibre error; controlled-state legal risk frontier; conservative extension; universal front representation | exactly two high-fan-out roots remain: owner-algebra construct validity and naturalistic transport/custody; 0/12 sufficient groups, 0 eligible dossiers, 0/9 ready arms and 0/14 custody bindings |
| P2 | Guarded frontier joining acquisition, scientific utility, future optionality, closure validity, and cost | acquisition ceiling; closure factorization; safe residual embedding; donor-fibre saturation/separation; TV lower bound; maximal robust safe set | V10 rejects title emphasis under four frozen gates; V11 retains exact u4 and proves that strict same-contract ascent needs fibre-separating information/state, new acquisition support or donor-class incompleteness |
| P3 | Set of source-compatible global portraits and authority-augmented query identified sets | fibre identification; coarsest sufficient query interface; refinement monotonicity; robust action bounds; joint-completion obstruction; local-readiness noncomposition | V12/V13 reach 5/5 native artifacts and structural conformance; V14 admits no provider-native reference for the synthetic pair, leaving scientific readiness 0/3 |
| P4 | Conditions under which a verification axis supports a scientific interpretation | exact terminal attainability; claim-level TV identifiability; adequacy envelope | V8 repairs 3/10 exact residual identities and raises JOSS bridges to 73/80, but seven authoritative edges, lineage, natural pairs and source-disjoint replication remain open |
| P5 | Minimal method revision under same-symptom observational equivalence and separated promotion authority | arbitrary-loss revision risk; discriminator cover and transcript purity; controlled-state legal discriminator frontier; no sound-and-complete self-promotion | V9 proves an exact-source C3 initialization-interface impossibility; panel remains 55/126 bound, 71 blockers and 0/6 ready |

P1 is the most general transition theory. P2-P4 own different upstream
information problems. P5 owns active revision discrimination and governance.
Shared factorization and Bayes identities are parent mathematics, not five
separate novelty claims.

## 4. Strongest-neighbour envelopment rule

Each paper now treats the strongest nearest mechanisms as donor components:

- retrieval, citation expansion, stopping, evidence plans and memory in P2;
- scientific IE, variable semantics, schema/ontology alignment, provenance,
  partial identification and constraint processing in P3;
- provenance, authorization, partial-evidence and evaluation-integrity systems
  in P4;
- diagnosis, repair, belief revision, dependency maintenance and Blackwell
  information comparison in P1;
- self-evolving agents, causal attribution, archives, anytime-valid acceptance,
  transfer benchmarks and active diagnosis in P5.

Adding a donor enlarges the attainable mechanism class. It does **not** grant a
wider authority claim automatically. A donor matters scientifically when it:

1. acquires evidence outside the previous action support;
2. refines an identified set or mixed decision fibre;
3. adds a genuinely admissible smaller transition;
4. discharges a registered material obligation; or
5. improves a protected fresh-transfer endpoint without violating any hard
   safety, preservation, validity or custody gate.

If a donor-complete information-equivalent product ties, that tie is required
evidence against architectural privilege.

## 5. Negative-result ascent operator

Every adverse terminal remains immutable and is mapped to one of five upward
research operators:

1. **Support expansion (P2):** the necessary evidence never entered the
   candidate pool. Invent or validate a materially different acquisition route.
2. **Observation refinement (P3):** the source-compatible identified set is too
   wide. Acquire a missing coordinate or test a world-class assumption.
3. **Axis repair (P4):** the benchmark is saturated, nuisance-decodable,
   terminal-mismatched or resolution-zero. Repair the corresponding axis.
4. **Transition refinement (P1):** the admissible front is empty, mixed or
   altered by a stronger donor. Measure the discriminator or adopt the new
   conservative/non-conservative extension honestly.
5. **Revision discrimination (P5):** identical symptoms support different
   revisions. Add interventions that cover the cross-decision pair universe.

A successor becomes positive only by executing a materially new discriminator
under a new identity. Relabeling, threshold relaxation, comparator deletion or
subgroup selection does not count as ascent.

## 6. Current top-tier frontier

The P1-P5 theorem layer is now broad enough for serious mathematical and
conceptual review. A same-repository adversarial audit found no counterexample
to the corrected displayed theorems under their explicit finite action,
finite-branch, bounded-horizon, and other stated assumptions. Eight stationary
and seven controlled-state finite witness checks pass; those are local
mathematical witnesses rather than external review or empirical evidence. The
common empirical blocker is not another local test or synthetic benchmark. It is protected naturalistic
execution:

- frozen external source snapshots and source-family cluster identities;
- strongest runnable, information/output-matched donor comparators;
- independent gold/evaluator/scorer custody;
- changed hosts/models/environments where the claim requires transfer;
- non-compensatory worst-domain, harm, validity and preservation gates;
- source-disjoint replication before any general headline.

A first metadata-only preflight pinned twelve official GitHub software
repository identities.  The outcome-blind G01 successor has now replaced that
monoculture with a sixteen-root, two-wave candidate frame: each wave contains
four metadata providers, four artifact modalities, four domains and two roots
per domain, with no cross-wave family or persistent-identifier collision.  All
16 live provider identities and all 13 conformance checks verify.  This is a
positive metadata-structure result only.  Exact historical Crossref bytes
remain unavailable for eight roots, future case-content rights remain
unresolved for all sixteen, eligibility remains unassessed for all sixteen,
and the downstream verified-case counts remain zero.  Consequently the
scientific terminal is still `CANNOT_CHECK_SOURCE_UNIVERSE`.  The comparator
audit also retains
`CANNOT_CHECK_FULL_COMPARATOR_FREEZE`: SIEVE is a runnable P2 candidate, MDA v3
is structurally source-grounded but has no released official solver, and the
P1/P3/P4/P5 external contrast identities or terminal adapters remain
incomplete. These adverse results define the next research identities in
`P1_P5_RECURSIVE_GAP_LEDGER_V1.md` rather than being repaired by wording.

P1's rights-valid structured-metadata successor provides a large lawful frame:
11,976 of 11,991 notices receive exactly one provider-native stratum and 11,988
normalized relation sets agree. V4 then tests the wider public-standard route:
four institutional families supply structural analogues for 9/12 owner groups,
but none supplies named-custodian authorship/delegation, so 0/12 remains the
exact sufficiency upper bound for that library; the P1 compression audit then
separates owner semantics from naturalistic custody as two independent roots.
P2 V10 rejects the one source-disjoint title residual while retaining exact u4,
and V11 converts the repeated donor failures into a safe-envelope and
donor-fibre separation theory rather than another grid. P3 V11--V13 close the
Java, five-artifact and lexical-interface chain; V14 stops at the missing
provider-native reference identity. P4 V8 reduces the exact-identity queue from
ten to seven. P5 V6/V7 close shared case rights and C1's environment, while V9
proves that the exact released C3 interface cannot be initialized outcome-free
without changing the comparator.
Alongside V7T's two-world authority countermodel, these are positive structure,
repair and efficiency results, not naturalistic performance.

The current wide protocols each target roughly 768 independent clusters in
their own scientific unit and retain adverse outcomes. Planning power is not
evidence. Until the external panels run, the defensible programme claim is:

> P1-P5 provide a unified information-and-authority theory that characterizes
> when scientific acquisition, integration, verification, transition and method
> revision are possible, impossible, or decision-theoretically bounded. Their
> present empirical studies validate exact mechanisms and expose specific
> adverse boundaries; they do not yet establish naturalistic cross-domain
> superiority.
