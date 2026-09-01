# Adversarial pass on the two remaining A6 candidates

**Status:** `ONE_FALLS_ONE_HOLDS`
**Scientific authority delta:** `NONE`. This can only narrow what the papers may claim.

`A6_DONOR_SUBTRACTION_V1.md` flagged three candidates.
`A6_PROPOSITION12_ADVERSARIAL_V1.md` refuted the strongest of them. This completes the
pass on the other two, as that document required before either is quoted.

## ORION-16 Theorem 4 — uniform graph-only minimality under affected realizability

**Restated.** Let the dependency graph be support-sound and the semantics class be
affected-realizable for `(E, X)`. Any repair strategy that observes only the graph, the
changed set and the pre-change certification, and must be sound for **every** semantics in
the class, must invalidate or revalidate every member of the affected set. So
root-inclusive reopening is inclusion-minimal among uniformly sound graph-only strategies.

**The proof is an indistinguishability argument**, and that is the giveaway. Assume a sound
strategy preserves some affected `q`. Realizability supplies a semantics with *identical
graph-visible information* in which the change invalidates `q`. A graph-only strategy
cannot tell the two apart, so it preserves a stale certification in one of them,
contradicting uniform soundness.

**Donor.** This is the standard optimality proof for an abstraction: to show an
over-approximating analysis is not merely sound but *exact* relative to its observation,
one exhibits, for each element of the abstract result, a concrete input consistent with the
abstraction that realizes it. That is precisely what affected-realizability asserts. The
pattern is abstract-interpretation completeness (Cousot & Cousot), and the same shape
appears as indistinguishability arguments in distributed computing and cryptography:
*if two worlds are indistinguishable to the observer, any strategy correct in both must act
conservatively in both.*

**Verdict: `SPECIALIZATION`.** A known optimality meta-argument instantiated to
dependency-graph repair. The instantiation is competent and the premise is stated
carefully — Definition 3 is more precise than most papers bother with — but the theorem is
not a new consequence.

The prediction recorded in the previous document was that Theorem 4 would fall to
abstract-interpretation completeness. It does.

## ORION-18 Proposition 14 — demotion is mandatory and forward-only

**Restated.** If an authorization held at epoch `t` and its premises are revoked at
`t' > t` such that no complete support set survives:

1. an uncommitted effect is *not* authorized at `t'` — the prior certificate does not
   transport;
2. a committed effect's epoch-`t` judgment stands as a **historical fact** — correctly
   issued on epoch-`t` premises — while carrying **no forward authorization**, so any
   dependent effect must be re-derived.

**Where the content is not.** The ratchet itself is ordinary. Forward-only epoch counters
and monotone generation numbers are standard distributed-systems machinery, and clause 1 is
routine certificate freshness.

**Where the content is.** Clause 2 separates two things that systems habitually conflate:
the *historical validity of a judgment* and its *continuing authority*. The paper names the
failure mode this prevents — reading "the commit was authorized, so it stands" as
continuing authority — and calls it the fail-open error. It then makes demotion an
**obligation on the pending queue** rather than a rewrite of history, and gives the reason:
history is immutable, and the epoch-`t` judgment is preserved *precisely so the loss of
support remains visible*, not so it can be cited as authority.

**Donor search.** Non-monotonic logic gives retraction; AGM gives contraction; neither
makes demotion *obligatory*. Deontic logic distinguishes permission from obligation but I
found no formulation in which the loss of support *obliges* a demotion while leaving the
historical judgment standing. Distributed systems supply the mechanism (epochs, leases,
fencing tokens) but treat it as a correctness device, not a normative requirement.

**Verdict: `SURVIVING_NEW_CONSEQUENCE`, provisionally, and it is the only one left.**

## Where the A6 subtraction now stands

| verdict | count |
|---|---|
| `DONOR` | 6 |
| `SPECIALIZATION` | 5 |
| `SURVIVING_NEW_CONSEQUENCE` | 1 (Proposition 14 clause 2) |

Eleven of twelve results are inherited or specialisations. **That is the honest position and
it is close to the reviewer's.**

## What this means for the two papers, concretely

**ORION-16 has no surviving formal novelty.** Its four examined results are one donor, one
donor, one specialisation and one donor. Its value is the careful statement of premises —
Definition 3's affected-realizability is a genuinely well-posed condition — and the
mechanised checking. That is a solid formal-methods contribution and not a theory
contribution, and it should be submitted as such.

**ORION-18 retains exactly one claim**, and it is narrow: that demotion is obligatory and
forward-only while the historical judgment stands. A paper can be built on one real claim
if the claim is stated at its true size and the rest is properly attributed. It cannot be
built on a claim that dissolves under an hour of reading, which is what happened to
Proposition 12.

## Honesty note on this pass

I produced the candidate list and have now refuted two of my own three entries. The
survivor should be treated with the same suspicion the other two earned: it survived *my*
donor search, and my donor search is not a literature review. The specific check that would
settle it is whether any normative-systems or deontic-logic formulation already states an
obligation-to-demote under loss of support. Until that is run, Proposition 14 is the best
candidate rather than an established contribution.
