# Formal Epistemic Structures and Mechanics — V5

**Date:** 2026-08-22
**Base manuscripts:** `FINAL_V2_1.md`, `FINAL_V3.md`, `FINAL_V4.md` (historical scientific layers retained)

V4 presented a certificate-lifting semantics whose support was an exhaustive
enumeration over a bounded model. V5 changes what the paper claims to have
proved, in both directions. Eleven theorems are now discharged over
uninterpreted sorts, so the separation and change-propagation results hold at
any size rather than at the enumerated one; and three of the quantities V4
reported as findings are shown here to have been unfalsifiable, so they are
withdrawn as evidence and kept only as a record of what the enumeration could
and could not have detected.

## Replacement abstract for V5

Systems that carry out scientific work inside mature governance machinery
accumulate certificates: runtime proof-of-execution, certified
proposal–execution traces, portable action and approval receipts, workflow
provenance signatures, dependency and effect systems, attested execution
boundaries. This paper treats those mechanisms as reusable donor certificates
rather than competitors, and asks what it takes to lift one of them into
continued *scientific* standing after the scientific state changes.

The answer is a conservative lifting semantics with two halves, and both are
now proved rather than enumerated. The **local half** governs what a change
touches: separated mechanics commute, separation is necessary for commutation
rather than merely sufficient, writes are local to a declared frame, the frame
determines the result, and fixpoints are conservative. The **propagation half**
governs what a change invalidates: reopening is sound, complete and minimal,
conservative and monotone, and a node reopens itself exactly when it lies on a
cycle. Both halves are discharged over uninterpreted sorts — the state
transformer of the local half is an uninterpreted function under a frame
condition, and the propagation half quantifies over dependency graphs of any
size, cyclic or not — so neither is a statement about a particular width.

The bounded model of V4 is then recovered as an instance rather than repeated
as separate support. A certificate over *n* coordinates is interpreted as the
star graph on *n+1* nodes: one node per coordinate, one for the certificate, an
edge from each coordinate to it. Damage is a changed set on the coordinate
nodes and repair removes coordinates from it. Under that interpretation, six
further theorems are discharged at arbitrary width — any damage withdraws the
certificate, a full repair restores it, a partial repair does not, undamaged
coordinates are never collateral damage, the dependency runs one way, and the
certificate supports nothing — and the two revalidation counts V4 published are
recomputed by running the implementation the propagation theorems were checked
against. The finite result is therefore output of a verified instance of the
theorems, not a second enumeration that agrees with them.

Three of V4's reported quantities do not survive this scrutiny and are
withdrawn below.

## What the enumeration could not have found

The bounded model of V4 reported seven quantities. Three of them could not have
come out any other way, and one of the three had never been evaluated at all.
Stating this is not a concession extracted after the fact; it is the result of
pointing the mutation discipline that validates the new theorems at the old
checks.

**The change-propagation check asserted set-algebra tautologies.** It computed a
downstream set and then asserted two things about it: that the retained set does
not intersect the downstream set, and that the retained set equals the certified
set minus the downstream set. The first intersects a set with something already
removed from it. The second compares a variable to the expression it was just
assigned. Both hold for *any* value of the downstream set. The propagation
function was called and its output was never compared against anything.
Confirmed by mutation: replacing it with "always the empty set" left the check
passing, and so did "always every node", both reporting the same case count as
the real implementation. The reported 130,320 cases over 543 acyclic graphs were
therefore 130,320 cases none of which could fail.

**The check itself has since been repaired**, on 2026-08-22, and the sentence
above is a description of what it was. Its assertions now compare the retained
set against a specification built from an independently computed transitive
closure, so both mutants die where both previously survived, and eight declared
wrong propagation operators are rejected where all eight were accepted. The case
count is unchanged at 130,320 over 543 graphs; what changed is that those cases
can now fail.

That is now repaired rather than merely reported. The propagation
specification is written independently of the implementation, and the shipped
implementation is compared against it exhaustively: **61,440 of 61,440** directed
graphs on four nodes and changed subsets agree, **51,712** of them with a
non-empty reopening. The implementation is correct. Before this, that had not
been established.

**Donor conservativity could not be violated.** The counter assigns a projected
verdict from the donor-native verdict on one line and compares the two on the
next. The condition is `x != x`. No theory of lifting, however wrong, moves that
count off zero. It is withdrawn as evidence; donor conservativity is instead
carried by the fixpoint-conservativity theorem, which is proved.

**Ideal-product equivalence compares an expression to itself.** The ideal
product is defined as the same predicate the lifting rule is defined as, so the
mismatch count is zero by construction. The equivalence claim is real and worth
making — an information-equivalent product carrying the same coordinates and the
same lift predicate does agree extensionally — but it is a definitional identity
and the enumeration adds nothing to it. It is withdrawn as an empirical
quantity.

**The "independent" reproduction is a paraphrase.** The second implementation
replaces a universal quantifier with an early-return loop. It diverges from the
reference on 0 of 320 points because it cannot diverge on any. A second
implementation that cannot disagree confirms a transcription, not a theorem.
The claim of independent reproduction is withdrawn; genuine independent review
remains outstanding and is named in the limits below.

**And one wrong theory walks through every check that remains.** Each assertion
in the bounded checker evaluates the lift rule with the donor certificate valid.
The 32 points of the space where it is invalid are enumerated into the published
digest and never asserted about. A rule that lifts on the scientific coordinates
alone, ignoring the donor entirely, passes the whole battery. Conservativity is
carried by the 1,536-state derivation reported below, where dropping it
disagrees on 72 states — not by the bounded checker.

## The general theorems

**Local mechanics.** Let a mechanic act on a state over an uninterpreted
coordinate sort and an uninterpreted value sort, with a declared frame naming
the coordinates it may write. The transformer itself is an uninterpreted
function constrained only by that frame. Then: two mechanics whose frames are
disjoint commute; separation is *necessary* for commutation and not only
sufficient; a mechanic writes only inside its frame; the frame and the input
determine the output; and the fixpoint of a mechanic is conservative over
coordinates outside its frame.

Because the transformer is arbitrary, commutation is a property of separation.
The bounded check of V4 instantiated it at modular arithmetic, which is a
property of that arithmetic. The shipped mechanic is shown to obey its declared
frame on all **5,280** exhaustive perturbations, so the bounded result is an
instance.

**Change propagation.** Over an uninterpreted node sort, with reachability
axiomatised as the reflexive–transitive closure of the dependency edge:
reopening is sound (every reopened node is reachable from a change), complete
(every reachable non-changed node is reopened), minimal (no proper subset of the
reopened set is closed under the edge relation from the changed set),
conservative, monotone in the changed set, and a node lies in its own reopened
set exactly when it lies on a cycle. Graphs of any size, cyclic or acyclic.

One clause of the closure axiomatisation is load-bearing and easy to omit.
Transitive closure is not first-order definable, so the four clauses *are* the
definition, and the fourth attaches a well-founded rank to each reachability
fact. Without it a model may contain two reachability facts that justify each
other in a cycle, and the completeness direction becomes unprovable. That was
not anticipated: an earlier axiomatisation without the rank admitted a model in
which a sink domain reached its own source, and a differential against the
committed implementation is what exposed it.

## The bounded model as an instance

Two derivations connect the general theorems to what V4 published.

**The lift rule.** Three primitives are stated without reference to the rule:
a donor certificate establishes only what its own embedding declares; each
scientific coordinate is a separate obligation rather than a contribution to a
score; and lifting is conservative, adding no authority the donor did not have.
The lift rule computed from them reproduces the shipped rule on all **1,536**
states of the embedding cube, with both verdicts present (24 admissible, 1,512
not). It is a derivation and not a restatement: making a scientific coordinate
compensatory disagrees on 96 states, waiving an embedding's donor requirement on
9, and dropping conservativity on 72.

**The revalidation counts.** A certificate over *n* coordinates is the star
graph on *n+1* nodes; damage is a changed set on the coordinate nodes; repair
removes coordinates from it. Six theorems are discharged under that reading at
arbitrary *n*, listed in the abstract above. The two published counts —
**155** full restorations and **1,055** proper-subset failures — are then
recomputed by running the shipped propagation implementation over the
interpreted graph, so they are output of an implementation independently
verified against the theorems rather than a separate enumeration agreeing with
them. Independently, the shipped revalidation assertion block accepts the
derived rule and rejects three weakenings of the non-compensatory primitive.

Two properties of that pair are stated because they are not obvious from the
numbers.

*The 155 discriminates between almost nothing.* A full repair leaves nothing
changed, which satisfies any monotone admissibility rule and reopens nothing in
any dependency graph. Every wrong graph tried returns 155, and so does every
weakened primitive tried. It is the number of (donor, non-empty damage) pairs.
The 1,055 is the count that moves: to 655, 255 and 0 under the three primitive
weakenings.

*And neither count identifies the interpretation.* This is the sharper
limitation, and it was found by looking for it. Seven dependency graphs were
tried against the star. Three collapse the failure count to zero — edges
reversed, no edges, coordinates chained without reaching the certificate. One
moves it to 975 — a single coordinate stops supporting the certificate. But
three reproduce **1,055 exactly**: a chain running through the coordinates *into*
the certificate, the star with extra coordinate-to-coordinate edges, and the
complete graph. The pair of counts tests whether every coordinate reaches the
certificate, and nothing beyond that; every graph in that reachability class
returns the same two numbers.

What separates the star from those three is the proof, not the arithmetic. Each
of them reopens coordinates as collateral damage — 245, 100 and 375 instances
respectively — and collateral reopening is precisely what
*undamaged coordinates are never collateral damage* forbids, and precisely what
is lost when the frame condition forbidding coordinate-to-coordinate support is
dropped. The shipped implementation is confirmed to reopen nothing but the
certificate under the star. So the theorems pin the graph and the counts confirm
its reachability class; a paper that reported the counts alone as evidence for
the structure would be reporting something the counts cannot see.

*The donor axis is a multiplier, not a dimension.* The donor family enters
neither the dependency graph nor the changed set. The five families replicate
the same 31 restorations and 211 failures rather than extending them: 155 and
1,055 are 31 and 211 counted five times. That is the shape of the original loop,
reproduced here rather than corrected, and it means the published pair carries
the information of the smaller pair.

*The revalidation block cannot see conservativity.* Every state it asserts about
is built with the donor verdict pinned valid, so the derived rule with its donor
conjunct deleted is accepted unchanged. Its acceptance of the derivation is
evidence for the non-compensatory primitive only.

## An axiom set that was not minimal

The interpretation was first stated with four frame conditions. A check that
drops each condition and re-runs the proofs reported two of them inert: dropping
either lost no theorem — where "lost" then meant "no longer proved", which is
the wrong criterion and is corrected below. Neither was a reprieve. Dropping *both* loses three
theorems, because each was derivable from the other three, so the four were a
redundant presentation of the same constraint. The interpretation now rests on
three independent conditions — every coordinate supports the certificate, every
edge runs from a coordinate to the certificate, and the certificate is not one
of its own coordinates — and the fourth, that the certificate supports nothing,
is discharged as a theorem about them. Each of the three loses at least one
theorem when dropped, and which theorem each carries is recorded.

An axiom that no theorem needs is either decoration or a redundant presentation
of an axiom that is doing the work, and the two are indistinguishable from
inside. The check that told them apart is worth more here than the axiom it
removed.

That check has since been wrong twice, and both corrections are worth stating
because they change what "load-bearing" can mean rather than only how it is
computed. It first counted any theorem that stopped being *proved* when an axiom
was dropped. That credits an axiom for the solver failing to settle a question:
a solver returning `unknown` has said nothing about whether the theorem still
holds. Requiring an actual countermodel fixed the criterion and broke the
stability, because refuting a universally quantified claim over an uninterpreted
sort is an unbounded model search — the same dropped axiom yielded a
countermodel on one run and `unknown` on the next. The measurement now asks for
a countermodel in a universe bounded to four nodes, which is sound in that
direction and in no other (a countermodel in a small universe is a countermodel;
failing to find one there proves nothing), and takes the intersection over
repeated runs.

Under that strictest reading all three conditions remain necessary, so the
conclusion survived both corrections. The per-condition detail did not: the
edge-restriction condition refutes between one and three theorems on identical
repeated runs, of which exactly one falls every time, and only that one is
credited to it.

## Bounded general statement

> Strong execution, action, workflow and attestation certificates can be
> composed and preserved as lower-level objects across change in a dynamic
> scientific state, but preservation of *scientific* standing requires an
> explicit lift across claim-specific semantic obligations; a scientifically
> material change reopens exactly the coordinates reachable from it, and
> revalidating precisely those restores the lift while any proper subset of them
> does not.

The separation and propagation halves of that statement hold at any size. The
five registered lift coordinates and five donor families are an instance of it,
recovered rather than assumed.

## Limits

The lift coordinates are not claimed to be universally minimal. No claim is made
that existing certificate systems fail their native goals, or that any formal
result here establishes utility for a deployed system; nothing in this paper is
an empirical claim.

Two limits travel with the mechanization. Reachability is axiomatised rather
than defined, because transitive closure is not first-order definable, so the
theorems are relative to that axiomatisation — the well-founded rank included.
And the interpretation connecting the bounded model to the general theorems was
written alongside the model it interprets; its frame conditions are shown to be
load-bearing and its counts are produced by an implementation checked against
the theorems, but no reviewer outside that lane has examined either — and, as
recorded above, those counts are consistent with three graphs other than the one
claimed. Independent
proof review remains outstanding, and the withdrawal above of a "second
implementation" that could not disagree is the reason to be exact about it.

Finally, the naturalistic question is untouched. No multi-domain corpus of real
changes — code patches, dataset revisions, model revisions, analysis changes,
instrument recalibrations, manuscript claim revisions — has been assembled, so
no claim is made about revalidation cost saved against revalidating everything
or against dependency-graph-only propagation.

## Conclusion

The strongest version of this result is not a rejection of existing certificate
systems; it is a way to use them more completely, and V5's contribution is that
the way is now proved rather than enumerated. Runtime proof, certified traces,
portable action receipts, workflow signatures, provenance and execution
attestation remain valuable and reusable after absorption into a scientific
stack. What the lifting semantics adds is a typed bridge from operational
certificates to scientific standing, together with soundness, completeness and
minimality results for what a change reopens — at any size, with the bounded
model of V4 as one instance.

Three of V4's seven reported quantities are withdrawn here, and the check that
was supposed to validate change propagation is shown to have asserted
tautologies. The result is a smaller set of claims held more firmly. That
exchange is the point of the exercise.
