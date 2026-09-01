# A6 Phase 1 — theorem restatement and donor subtraction (ORION-16, ORION-18)

**Status:** `DONOR_SUBTRACTION_FIRST_PASS__NO_AUTHORITY_DELTA`
**Scientific authority delta:** `NONE`. No terminal moves and no claim is promoted. This
document can only *reduce* what the papers may claim, never increase it.

## Why this is the right response to the review

The hostile review's sharpest charge is that the theory is *"too close to classical
decision/information theory without sufficient differentiation."* The defensive answer is
to argue the papers are different. The scientific answer is to **do the subtraction
explicitly** — restate each result in standard language, name the nearest prior art, and
mark what survives.

Issue #49 A6 Phase 1 asks for exactly this: restate every theorem "without ORION-specific
nouns", build a donor matrix, and mark each result `DONOR`, `SPECIALIZATION` or
`SURVIVING_NEW_CONSEQUENCE`.

This is a first pass over the results visible in `FORMAL_CORE_V2_1.md` for both papers. It
is deliberately harsh, because a subtraction that flatters the papers is worthless.

## Donor fields consulted

Truth maintenance (JTMS/ATMS), belief revision (AGM), non-monotonic logic, abstract
interpretation and static-analysis soundness/precision, dependence analysis and
parallelising compilers, build-system and cache invalidation, separation logic and typed
effects, deontic logic and authorization/delegation calculi, provenance algebras.

## ORION-16

### Theorem 1 — safe root-inclusive reopening

**Restated.** In a directed graph over claims where every actual support is represented by
an edge or a path, invalidating the changed set together with its transitive descendants
leaves no possibly-invalid claim marked valid.

**Nearest prior art.** This is the soundness half of truth maintenance. Retracting a
justification and propagating to dependents is the defining JTMS operation (Doyle 1979)
and the ATMS label-update operation (de Kleer 1986). It is also exactly what every
build system does: if an input changed, rebuild the target and everything downstream.

**Verdict: `DONOR`.** The result is classical dependency-invalidation soundness restated
in the paper's vocabulary. The paper should cite it as inherited and claim nothing here.

### Countermodel 2.1 — support soundness does not imply minimality

**Restated.** A sound over-approximation of the dependency relation does not yield a
minimal invalidation set; conservative edges cause over-invalidation.

**Nearest prior art.** The soundness/precision gap in static analysis. A may-analysis is
sound and imprecise by construction, and the fact that over-approximation costs minimality
is textbook abstract interpretation (Cousot & Cousot 1977).

**Verdict: `DONOR`.** Correct, well-posed, and not new. Its role is to motivate Theorem 4,
which is legitimate — but it must not be presented as a finding.

### Theorem 4 — uniform graph-only minimality under affected realizability

**Restated.** If for every member of the affected set there exists an admissible semantics
in the declared class under which that member is genuinely invalidated, then the
graph-descendant set is not merely sound but inclusion-minimal.

**Nearest prior art.** This has the shape of a *completeness* result in abstract
interpretation: an over-approximation becomes exact when the abstraction is complete for
the concrete semantics class. The premise plays the role of demonic realizability — every
over-approximated case is witnessed by some admissible concrete run.

**Verdict: `SPECIALIZATION`, with a candidate surviving edge.** The general
"exactness under a realizability premise" pattern is donor-owned. What is not obviously
donor-owned is that the premise is required **uniformly over the whole affected set,
including directly changed roots**, rather than only over descendants — the paper's own
prose notes that a directly changed certified root can be invariant under a restricted
class. If that uniformity is genuinely load-bearing and has no counterpart in the donor
literature, it is the strongest formal thing ORION-16 owns. **This needs a targeted
literature check before any claim is made on it.**

### Theorem 7 — history-aware commutation under faithful full separation

**Restated.** Two operations commute when their read and write footprints are disjoint and
the footprint abstraction is faithful.

**Nearest prior art.** Bernstein's conditions (1966) for safe parallel execution are
exactly disjointness of read/write sets. The frame rule of separation logic and the
disjointness conditions of typed effect systems are the same result in other clothing.

**Verdict: `DONOR`.** The "history-aware" qualifier may narrow the setting, but
commutation-under-footprint-disjointness is not ORION's.

## ORION-18

### Proposition 10 — blocker absence is not blocker refutation

**Restated.** Failure to detect an obstruction does not establish its absence.

**Verdict: `DONOR`.** This is the open-world assumption, and the absence-of-evidence
distinction that non-monotonic logic exists to handle.

### Proposition 11 — blockers are monotone under evidence accumulation

**Restated.** The obstruction set grows monotonically as evidence accumulates.

**Verdict: `SPECIALIZATION`.** Monotone growth of a derived set under an increasing
evidence base is standard fixed-point reasoning; the content is which set is chosen.

### Proposition 12 — permission is not a function of confidence and expected utility

**Restated.** The authorization predicate is not determined by the pair (confidence,
expected utility); two states agreeing on both can differ in permission.

**Nearest prior art.** Deontic logic separates permission from preference, and the is/ought
gap is old. But the specific claim that permission is **not a function of** a
decision-theoretic pair is a separation result about a concrete signature, and
decision-theoretic accounts of autonomy routinely assume the opposite.

**Verdict: `SURVIVING_NEW_CONSEQUENCE`, provisionally.** This is the most distinctive
formal claim in either paper and it directly contradicts the review's charge that the work
reduces to classical decision theory — *if* it holds as stated. It is also the claim most
worth attacking: a donor that already proves it would collapse the paper's core.

### Proposition 13 — authority is non-monotone

**Restated.** Authority can decrease as evidence increases.

**Verdict: `DONOR`.** Non-monotonicity is the founding observation of non-monotonic logic
and AGM contraction. That authority specifically is non-monotone is a substitution into a
known frame.

### Proposition 14 — demotion is mandatory and forward-only

**Restated.** Once authority is reduced, it cannot be restored by the same evidence path;
the reduction is a ratchet.

**Nearest prior art.** Forward-only epoch counters and monotone generation numbers are
standard in distributed systems; irreversibility itself is not novel.

**Verdict: `SPECIALIZATION`, possible surviving edge.** The mandatory quality — that
demotion is *obligatory* rather than permitted — is a deontic claim rather than a
mechanism claim, and I did not find an obvious donor for the obligation. Flagged for the
same targeted check as Theorem 4.

### Propositions 15–16 — protected custody is one root class, not the only one

**Restated.** Protected custody is sufficient but not necessary for authorization; other
root classes exist.

**Verdict: `SPECIALIZATION`.** A scope-restriction result about the paper's own earlier
proposition. Valuable for honesty, not a contribution.

## Tally

| verdict | count |
|---|---|
| `DONOR` | 5 |
| `SPECIALIZATION` | 4 |
| `SURVIVING_NEW_CONSEQUENCE` (provisional) | 1 |

**Nine of ten results are inherited or are specialisations of inherited results.** That is
a serious finding and it substantially supports the reviewer rather than the papers. The
honest reading is that ORION-16's formal core is largely a restatement of truth
maintenance plus abstract interpretation, and ORION-18's is largely non-monotonic logic
plus deontic separation.

**What survives is narrow and worth everything.** Proposition 12 — permission not being a
function of confidence and expected utility — is the one claim that is both distinctive and
directly responsive to the "reduces to classical decision theory" charge. Theorem 4's
uniformity premise and Proposition 14's obligation are two further candidates.

## What must happen before any of this is quoted

This pass is **my** reading of the nearest prior art, and I am not an independent reviewer.
Three specific literature checks decide the three survivors:

1. Does any completeness result in abstract interpretation already give Theorem 4's
   uniform-over-affected-set version?
2. Does any deontic or authorization calculus already prove Proposition 12's
   non-functionality?
3. Is mandatory forward-only demotion stated anywhere in normative-systems literature?

Until those are run, the three survivors are **candidates**, not contributions. The five
`DONOR` verdicts, by contrast, should be acted on immediately: those results should be
presented as inherited, with citations, and the papers' novelty claims narrowed
accordingly.
