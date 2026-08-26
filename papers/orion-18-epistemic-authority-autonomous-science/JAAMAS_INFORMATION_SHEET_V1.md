# ORION-18 — JAAMAS submission information sheet (V1)

JAAMAS requires a 1–2 page sheet with every submission, and returns submissions
whose sheet is incomplete or uninformative without review. It asks two questions
and warns that "We are the first to have done X" is not an acceptable answer to
the first without stating the importance of X.

## 1. What is the main claim, and why is it an important contribution?

**Claim.** Local action/release authority and scientific-discharge authority are
distinct relations, and the distinction is not recoverable from provenance. This
paper gives a typed, non-amplifying authority calculus in which donor-local
verdicts stay intact while scientific discharge propagates only through
scope/domain/epoch-confining delegation or explicit protected coercion, with
three-valued blocker and exact support-revocation semantics.

**Why it matters for agents.** The failure mode is authority laundering: an agent
holds permission to *run* something, the run succeeds, and that local success is
carried forward as though it authorized a *conclusion*. In a delegation chain
this compounds — each hop sees a valid verdict from the hop before and widens
what it licenses, with no step doing anything locally wrong. Multi-agent systems
that compose provenance, release gates and evidence ledgers have exactly the
structure in which this happens, and the calculus makes the widening a typed
error rather than an emergent one. The three-valued blocker matters for the same
reason: collapsing "refused on the evidence" into "not answerable" manufactures
a negative finding out of an absent one.

**What is not claimed.** No novelty for any of the thirteen donor mechanisms, no
universal minimality of the five type coordinates, no deployed-agent
superiority, and no broad autonomous-science authority.

## 2. What evidence is provided? Be precise.

**Exhaustive finite model.** The X4 model covers **3,072 distinct exact
authority states**, each replayed across **thirteen donor families** for
**39,936 evaluations** — the unit is the state, not the evaluation, and the
paper says so. Result: **zero** donor-conservativity violations and **zero**
mismatches against an equally typed decentralized product.

**Composition law with matched countermodels.** Every ordered pair among the
thirteen registered donor families admits a scientifically valid two-hop
composition when local verdicts are native-valid, type is compatible or
protectedly bridged, and authority does not widen. For every ordered pair, a
matched unbridged widening variant remains unavailable while both donor-native
steps stay valid, yielding **169 matched widening countermodels**. The
success/countermodel pairing is what makes this a tested finite law rather than
an intuition: local authority stays valid; only the unjustified widening is
rejected.

**Real evidence-discharge study (20 frozen cases, four domains).** Empirical,
formal, multiple-support and systems settings. Exact scientific-discharge
accuracy **1.0 in all four domains**, **0** false scientific promotions, 12
explicit action/scientific-separation cases, full support revocation blocking
discharge and partial revocation preserving retained support. Independent
checker and deterministic replay GREEN.

**Corrected historical count.** The 169 chain compositions are retained as
*reflexive multiplicity of one composition*, not as heterogeneous breadth. The
earlier reading — that they exhausted the heterogeneous 13×13 donor-pair product
— is withdrawn and the corrected reading is stated in the manuscript.

**Scope of agreement.** The mechanized interpretation and tests are
programme-internal and the real evidence study is bounded. Independent external
scientific adjudication, plus a strong integrated authorization/evidence donor,
remain necessary for any broad autonomous-science authority claim and have not
occurred.
