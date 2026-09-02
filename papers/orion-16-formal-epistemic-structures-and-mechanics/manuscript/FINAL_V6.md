# Formal Epistemic Structures and Mechanics — V6

**Date:** 2026-09-01
**Base manuscripts:** `FINAL_V2_1.md`, `FINAL_V3.md`, `FINAL_V4.md`, `FINAL_V5.md` (historical scientific layers retained)

**V6 changes V5 in one respect.** It adds *Relation to prior work*, attributing each theorem to the field that owns it. No theorem, premise, boundary or count is altered, and V5 remains the frozen record of the results as first stated.

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

**Local mechanics (`ORION-16.COMMUTE.RW_NONINTERFERENCE.V1`).** Let deterministic,
admissible mechanics act on a state over uninterpreted coordinate and value
sorts. Each mechanic must be read-footprint faithful and write-footprint
faithful. Their write coordinates are distinct, neither mechanic reads the
coordinate written by the other, and neither changes an obligation, authority
fact, provenance object, dependency, resource, or declared external input
consumed by the other. Whenever both sequential compositions are defined, the
two orders have the same current scientific projection. Their ordered audit
histories need not be literally equal; they are equivalent under swaps of
adjacent independent commit events.

The two cross-read exclusions are load-bearing. If either is removed while the
writes remain disjoint, a frame-faithful transformer and state can make the two
orders disagree. This is a necessity claim about what the stated assumptions
must exclude to entail commutation for every admissible transformer, not a claim
that every particular pair of interfering mechanics fails to commute. The
bounded V4 modular check is only an instance of this stronger contract, and the
shipped mechanic obeys its declared frame on all **5,280** exhaustive
perturbations.

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
1,055 are 31 and 211 counted five times. The same loop repeats the rest of the
list: 320 states is the 64-point (donor verdict, coordinate vector) space
enumerated once per family, and the 25 minimal separations are 5 counted five
times. Only the 31 product countermodels are 31 distinct facts. That is the
shape of the original loop, reproduced here rather than corrected, and it means
the published counts carry the information of the smaller ones; the
``donor_axis`` block of the result artifact carries the table.

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

The criterion was corrected in stages because each earlier version could turn a
fact about search into a claim about an axiom. Counting any theorem that stopped
being *proved* credited an axiom when the solver returned `unknown`. Requiring an
actual countermodel removed that error, but an open model search was unstable.
Bounding discovery to at most four nodes did not remove the instability: CI run
32927946106 reported the edge restriction only intermittently, and run
32946736266 returned `unknown` for its known one-node witness under full-suite
load, cascading to four ORION-16 test failures. Both adverse runs remain failure
provenance; neither showed the condition inert.

The current measurement no longer discovers a witness. It verifies one pinned,
fully specified exact-domain countermodel for each condition. Without coordinate
support, a two-node world has an unchanged non-coordinate certificate, one
changed coordinate, identity reachability and no edges; this refutes withdrawal
by any damage. Without the edge restriction, a one-node world has a
non-coordinate certificate with a self-edge; this refutes the derived claim that
the certificate supports nothing. Without certificate non-coordinateness, a
one-node world makes the changed certificate itself a coordinate with a
self-edge; because changed nodes are not reopened, this again refutes withdrawal.
All three tables use reflexive reachability and zero ranks. The solver checks the
remaining axioms, the exact domain, every table entry and the negated named
theorem. A certificate is credited only when every repeated check returns an
actual countermodel; `unknown` remains `CANNOT_CHECK`, and an invalid supplied
model is a failed certificate rather than evidence of inertness.

These certificates establish local logical necessity relative to this
formalization and theorem set only. They were written and checked in the same
lane. External or independent validation remains `CANNOT_CHECK` under ORION-16-U-T4;
the certificates provide neither empirical evidence nor external scientific
authority.

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

## Bounded executable evidence: ETS and the heterogeneous transition audit

The theorems above are exact statements about the structures. Two bounded
executable studies test whether the distinction they draw survives contact with
material the structures did not construct. Both were committed as protocol
before their cases, both carry frozen gold, and both were reproduced by a second
checker that does not import or execute the first.

That second checker is not the one whose independence this paper withdraws
above. The withdrawn one replaces a universal quantifier with an early-return
loop and cannot diverge from the reference on any point, so its agreement
confirms a transcription. These two evaluate the same frozen case facts and gold
through a distinct prioritized defect-set formulation and independently
reconstruct the T6.1--T6.3 summary invariants, so they can disagree and the CI
gate requires that they do not on any protected classification. Neither,
however, is external: both implementations are written inside this programme,
and genuine independent review remains outstanding for these studies exactly as
it does for the enumeration.

**ETS, 18 frozen cases in three six-case families.**

| system | exact accuracy | unsafe false-admissible | laundering false-admissible | unnecessary reopen |
|---|---:|---:|---:|---:|
| strong declared donor product | 0.50 | 9 | 3 | 0 |
| ETS checker | **1.00** | **0** | **0** | **0** |

ETS accuracy is 1.00 in each of formal/software, agent-memory/tool-state and
scientific-evidence-state; the donor product is 0.50 in each. The second
verifier reproduces all 18 gold dispositions exactly, and its label-independence
attack remints `id`, `family` and `case_type` and confirms the scientific
terminal does not move.

**Heterogeneous transition audit, 16 frozen cases in four real-domain families**
(four each: `rocrate-standard`, `p9-artifact-recovery`, `p10-native-coverage`,
`p15-provenance-import`). The epistemic-transition gate is exact -- `1.0`
accuracy, `0` unsafe false-admissible, `0` unnecessary reopen, `0` authority
laundering, perfect in every family. The donor-only gate reaches `0.4375`, with
`9` unsafe false-admissible decisions and `1` authority-laundering decision, and
is unsafe in all four families (3/2/2/2). The independent checker's per-family
unsafe counts agree exactly.

The two studies fail the donor layer in the same direction on different
material, which is the point: the separation is not an artifact of the
constructed enumeration.

**Exact scope.** Eighteen and sixteen frozen cases respectively, with gold
dispositions fixed before execution. Agreement is between two implementations
inside the same programme, not external adjudication. The ideal enriched-product
tie is preserved: enriched-product mismatches remain **0**, so the donor product
is not being beaten on expressive power. Nothing here supports a claim of
inherent expressivity or inherent centralization -- the donor layer fails on
admissibility decisions under transition, not because it can express less.


## Relation to prior work

Every theorem below restates, in a certificate vocabulary, a result an established field
already owns. Saying so precisely is more useful than a novelty claim the theorems do not
support.

**Dependency invalidation.** Theorem 1 — invalidating a changed set together with its
transitive descendants leaves no possibly-invalid claim marked valid — is the soundness half
of truth maintenance. Retracting a justification and propagating to dependents is the
defining operation of a justification-based TMS (Doyle 1979) and of ATMS label update
(de Kleer 1986), and it is what a build system does whenever an input changes. What is
particular here is the sort discipline the theorem is stated over, not the theorem.

**Soundness without minimality.** Countermodel 2.1 exhibits a sound over-approximation of
the dependency relation that is not minimal. This is the soundness–precision gap of static
analysis: a may-analysis is sound and imprecise by construction, and over-approximation
costs minimality (Cousot and Cousot 1977). Corollary 4.1 — full reset is sound and strictly
non-minimal whenever a certified claim lies outside the affected set — is the baseline the
incremental-computation literature is defined against rather than a result within it.

**Exactness under a realizability premise.** Theorem 4 has the shape of a completeness
result in abstract interpretation: an over-approximation becomes exact when the abstraction
is complete for the concrete semantics class. What the theorem adds is the exact form of the
premise. Affected realizability is required uniformly over the whole affected set, including
directly changed roots, rather than over descendants alone, and the boundary below records
that a directly changed certified root can be invariant under a restricted class. Whether
that uniformity has a counterpart in the abstraction literature is open; this paper does not
assert that it has none.

**Declared versus actual footprints.** Countermodel 6.1 — a procedure that secretly branches
on ambient state can be reordered against a writer of that state while their declared sets
stay disjoint — is the standard motivation for effect systems. An effect annotation is
worthless without a soundness theorem tying it to real accesses (Lucassen and Gifford 1988),
and non-interference conditions for parallel execution are stated over actual rather than
declared dependences for the same reason (Bernstein 1966). Theorem 7 is those conditions
with footprint fidelity made an explicit hypothesis and the ordered audit history carried
alongside the scientific projection.

**What is not settled here.** Read as separate theorems, the results above are inherited.
What is not inherited is the question of how much authority a re-certification may carry:
truth maintenance does not ask it, having no notion of authority, and authorization calculi
do not answer it, modelling no repair mechanism. This paper supplies the repair half and its
mechanized checking. It does not settle that question and claims nothing beyond the theorems
stated above.

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

## The exact commutation statement, kernel-mechanized

Theorem 7's full statement — multi-component environments, mechanics that are
read-footprint faithful and write-footprint faithful over their declared
footprints, fully scientifically separated — is now checked as a kernel proof
under contract id `ORION-16.COMMUTE.EXACT_THEOREM7.V1`: 450 rule applications in an
LCF-style kernel, the serialized log replayed from nothing in a fresh kernel
(reproducing the exact conclusion, all residual hypotheses inside the theory),
and a z3 cross-check of the same sentence alongside. The conclusion pairs
equality of the two scientific projections with swap-equivalence of the two
ordered histories under independent events. The kernel is ORION-authored
Python, not Lean and not independently reviewed; that boundary is recorded in
the mechanized artifact with the replay verdict.
