# QG-25 — donor search (protocol §1, a HARD precondition run BEFORE any claim)

Date: 2026-08-22 · Lane: ORION-QG / QG-25 · Branch: `claude/orion-harness-verification-b17qdj`
Validator: `orion_research_harness.donor_search.validate_donor_search`, imported and
called in-run by `research/extensions/orion-qg/qg25_no_syndrome_family.py`
**with this file's text passed as `log_text`**, so the residual-W11
passage-occurrence check is exercised rather than skipped. It fails closed.

**Retrieval status, stated honestly.** WebSearch was available and returned
snippet-level text. **Every direct document fetch was refused by the session's
egress proxy** — `arxiv.org` and `www.scottaaronson.com` both returned
`EGRESS_BLOCKED`. Every verbatim passage below is therefore **search-snippet
text, not document-level text**, and every record carries
`document_level_verification: false`. Retrieval was available, so this lane does
not take a donor-search-unavailable terminal; but no passage below may be cited
as though it had been read in its source.

**Prior expectation, frozen in the protocol before searching.** Protocol §1
records that this lane *expects* to be subsumed: optimal stabilizer-state
preparation and Clifford synthesis are heavily worked (Aaronson–Gottesman,
Bravyi et al., Maslov, the CNOT-count literature), and the automata-theoretic
content of "minimum dimension of a state abstraction that still decides the
language" is Myhill–Nerode, 1958. **The expectation was met.** A subsumed claim
is a successful outcome here, exactly as in QG-19 and QG-24.

---

## Family 1 — own vocabulary {#family-1}

| # | Query | Bearing results |
|---|-------|-----------------|
| 1.1 | `conserved syndrome dimension collapse agent regime geometry family without fixed-dimension syndrome StabPrep` | none |

Returned deep-learning "neural collapse" geometry (EmergentMind, OpenReview
*Understanding dimensional collapse in contrastive learning*), a delayed
Lotka–Volterra model, a JEPA world-model preprint, and several USPTO patents on
collapsible wound-therapy dressings. Nothing bears on quantum circuit synthesis,
on conserved quantities of a dynamic program, or on automata state complexity.

**Verdict (record QG25-C4): `NO_PRIOR_ART_FOUND`.** This is **not a novelty
grant**. It is a statement about this programme's private vocabulary: the words
"conserved syndrome", "collapse agent" and "regime geometry" do not retrieve the
two fields that actually own this mathematics. Both claims this family would
have protected are removed anyway under Family 2 — which is exactly QG-19's
mechanism, and exactly why all three families are mandatory.

## Family 2 — donor-field translation {#family-2}

| # | Query | Bearing results |
|---|-------|-----------------|
| 2.1 | `minimal automaton transitive group action Myhill-Nerode one state per element lower bound DFA states permutation group` | **killing** |
| 2.2 | `"permutation DFA" transition group transitive "group language" state complexity minimal DFA strongly connected` | **killing** |
| 2.3 | `number of stabilizer states 2^n product (2^k+1) Aaronson Gottesman improved simulation stabilizer circuits counting` | **killing** |
| 2.4 | `optimal preparation of stabilizer states minimum CNOT count Clifford circuit synthesis Bravyi Maslov shortest circuit` | **killing** |

### QG25-C1 — "the minimum dimension of a feasibility-deciding state abstraction for StabPrep is log2 of the number of stabilizer states, hence Θ(n²)" → **INSTANCE_OF_KNOWN_GENERAL**

Claim: *no state abstraction of StabPrep coarser than the stabilizer-state set
itself still decides whether a gate word prepares the target; therefore the
minimum syndrome dimension is ⌈log2|S_n|⌉ and it grows quadratically in n.*

General result: Myhill–Nerode. From query 2.1 (Cornell CS682 Lecture 15
*Myhill–Nerode Relations*; IIT Bombay CS310 *DFA minimization and Myhill–Nerode
theorem*; CMU *CDM Minimization of Finite State Machines*):

> "The number of states in a minimal machine equals the index of the right
> language equivalence relation, which represents the minimum cardinality for any
> DFA accepting the language."

This lane's "minimum dimension of a feasibility-deciding quotient" **is** the
index of the right-congruence, written in base 2. The measurement below is an
instance; the theorem is sixty-eight years old and belongs to the donor field.
Novelty is at most the arithmetic for this particular family.

### QG25-C2 — "no additive/abelian conserved syndrome of any dimension decides StabPrep feasibility" → **INSTANCE_OF_KNOWN_GENERAL**

Claim: *the obstruction is not the size of StabPrep's state space but the
non-commutativity of its transition monoid, so no homomorphism into an abelian
group of order 2^D decides feasibility at any D — fixed or growing.*

General result, from query 2.2 (Springer, *Theory of Computing Systems*;
arXiv:1702.00877 *Primitivity, Uniform Minimality and State Complexity of
Boolean Operations*):

> "A DFA is called a permutation DFA if its transition monoid is a permutation
> group on the states, and in this case the transition monoid is called the
> transition group rather than the transition monoid."

> "For a permutation DFA, the following are equivalent: the automaton is
> accessible, the automaton is strongly connected, and the transition group is
> transitive."

StabPrep's referee graph is precisely a permutation DFA whose transition group is
the n-qubit Clifford group acting on stabilizer states — transitive, and for
n ≥ 1 non-abelian. That an abelian image of a non-abelian transition monoid
cannot separate the states is the standard transition-monoid reading of
Myhill–Nerode, not a finding of this lane. Novelty removed; what survives is the
exhibited witness word pair for this specific alphabet.

### QG25-C3 — the StabPrep family itself: exact minimum-cost preparation by exhaustive shortest path over the complete stabilizer-state graph → **SUBSUMED**

Source, from query 2.4 (*CNOT-Optimal Clifford Synthesis as SAT*, Shaik & van de
Pol, LIPIcs SAT 2025; *Optimal Clifford Synthesis as Planning*, ICAPS):

> "Bravyi, Latone, and Maslov (2022) propose normal forms that guarantee cx-count
> optimality. By employing a brute force search of 100 days, they were able to
> synthesize all 6-qubit Clifford circuits, resulting in a 2.1 TB database."

Supporting, from query 2.3 (the stabilizer-state count this lane re-enumerates):

> "for n = 2 the number of stabilizer states is 60, and for n = 3 it is 1080."

Exhaustive optimal Clifford / stabilizer-state synthesis over the complete state
space, at exactly this scale, is established practice with a published database
an order of magnitude larger than anything this lane enumerates. Novelty removed.
QG-15 already conceded the family is donor construction; the search confirms the
concession.

## Family 3 — inverted / survey {#family-3}

| # | Query | Bearing results |
|---|-------|-----------------|
| 3.1 | `complexity of optimal quantum circuit synthesis NP-hard shortest Clifford circuit exponential search stabilizer state preparation hardness survey` | **narrowing** |

### QG25-C5 — the residual: that a growing minimal-quotient dimension is a regime-geometry statement about this family rather than an instance of known synthesis complexity → **INSTANCE_OF_KNOWN_GENERAL**

From query 3.1 (*Quantum Circuit Synthesis and Compilation*, OpenReview review;
*Depth-Optimal Synthesis of Clifford Circuits with SAT Solvers*, arXiv:2305.01674;
*CNOT-Optimal Clifford Synthesis as SAT*, arXiv:2504.00634):

> "Quantum-gate-synthesis algorithms, which decompose a given unitary into gates,
> run for times exponential in the system size."

> "The Clifford synthesis problem is contained in the first level of the
> polynomial hierarchy (NP), while the classical synthesis problem for logical
> circuits is known to be complete for the second level of the polynomial
> hierarchy (Σ₂ᴾ)."

**Reading, and it cuts against this programme's own conjecture.** The second
passage is the sharpest thing the search returned. QG-22 located hardness in
families without a conserved syndrome and named StabPrep. The donor field
reports Clifford synthesis as sitting **in NP** — so whatever QG-22's CONJECTURE
could mean, it cannot mean hardness above NP for this family, and the field
records no hardness result for it at all, only exponential *algorithms*. That is
the same distinction QG-22's own gate G3 draws: an exponential algorithm is not a
hard problem. Novelty here is at most the arithmetic on a committed family, which
is what a lane at `NOT_R6` is entitled to.

### Context (not a verdict)

From query 2.4, on why exhaustive optimal synthesis is worked at all:

> "Since two-qubit gate fidelities are up to 10x lower than single-qubit gates on
> many quantum platforms, previous work has mainly focused on optimizing the CNOT
> gate count (cx-count) or the CNOT circuit depth (cx-depth)."

This is the reason StabPrep's frozen cost model charges CNOT 3 and the
single-qubit gates 1. The cost model is donor practice.

---

## Summary of verdicts

| record | claim | verdict | source | doc-level |
|--------|-------|---------|--------|-----------|
| QG25-C1 | min feasibility-deciding dimension = log2 of the Nerode index | `INSTANCE_OF_KNOWN_GENERAL` | Myhill–Nerode (Cornell CS682 L15; IIT-B CS310; CMU CDM) | false |
| QG25-C2 | no abelian syndrome at any D; obstruction is non-commutativity | `INSTANCE_OF_KNOWN_GENERAL` | permutation DFA / transition group, arXiv:1702.00877 | false |
| QG25-C3 | the StabPrep family and its exhaustive optimal referee | `SUBSUMED` | Bravyi–Latone–Maslov 2022 via LIPIcs SAT 2025 | false |
| QG25-C4 | own-vocabulary framing | `NO_PRIOR_ART_FOUND` (**not a grant**) | — | false |
| QG25-C5 | growing dimension as regime geometry rather than known synthesis complexity | `INSTANCE_OF_KNOWN_GENERAL` | OpenReview synthesis review; arXiv:2305.01674; arXiv:2504.00634 | false |
| QG25-C6 | no hardness result is claimed (does not assert novelty) | n/a — `asserts_novelty: false` | — | false |

`novelty_credit: false`, `novelty_authority: false`, `donor_novelty_credit: false`.

## Sources

- [Myhill–Nerode Relations, Cornell CS682 Lecture 15](https://www.cs.cornell.edu/courses/cs682/2008sp/Handouts/MN.pdf)
- [DFA minimization and Myhill–Nerode theorem, IIT Bombay CS310](https://www.cse.iitb.ac.in/~akg/courses/2019-cs310/lec-13-myhill.pdf)
- [CDM: Minimization of Finite State Machines — Klaus Sutner, CMU](https://www.cs.cmu.edu/~cdm/pdf/22-minimization.pdf)
- [Primitivity, Uniform Minimality and State Complexity of Boolean Operations (arXiv:1702.00877)](https://arxiv.org/pdf/1702.00877)
- [Improved Simulation of Stabilizer Circuits — Aaronson & Gottesman](https://www.scottaaronson.com/papers/chp6.pdf) (fetch `EGRESS_BLOCKED`)
- [On the Geometry of Stabilizer States (arXiv:1711.07848)](https://arxiv.org/pdf/1711.07848)
- [CNOT-Optimal Clifford Synthesis as SAT (arXiv:2504.00634 / LIPIcs SAT 2025)](https://arxiv.org/pdf/2504.00634)
- [Optimal Clifford Synthesis as Planning — Shaik & van de Pol, ICAPS](https://ojs.aaai.org/index.php/ICAPS/article/download/42836/50396)
- [Depth-Optimal Synthesis of Clifford Circuits with SAT Solvers (arXiv:2305.01674)](https://arxiv.org/abs/2305.01674)
- [Quantum Circuit Synthesis and Compilation — review (OpenReview)](https://openreview.net/pdf?id=PlJz4JUOYh)
