# QG-24 — donor search (protocol §1, a HARD precondition run BEFORE any novelty claim)

Date: 2026-08-22 · Lane: ORION-QG / QG-24 · Branch: `claude/orion-harness-verification-b17qdj`
Validator: `orion_research_harness.donor_search.validate_donor_search` (imported and
called in-run by `research/extensions/orion-qg/qg24_rotation_regime.py`; it fails closed).

**Retrieval status, stated honestly.** WebSearch was available and returned
snippet-level text. **Every direct document fetch was refused by the session's
egress proxy** — `arxiv.org` and `www.cs.ox.ac.uk` both returned
`EGRESS_BLOCKED`. So every verbatim passage below is **search-snippet text, not
document-level text**, and every record carries
`document_level_verification: false`. The lane therefore does **not** take the
`QG24_BLOCKED__DONOR_SEARCH_UNAVAILABLE` terminal — retrieval was available; only
document fetch was not — but no passage below may be cited as though it had been
read in its source.

**Prior expectation, recorded in the protocol before searching.** This lane
*expects to be subsumed*: phase polynomials, T-par, TODD, Gray-Synth and
Pauli-rotation merging are a heavily worked area, and the honest prior was that
the merging criterion is known. **The expectation was met.** A subsumed claim is
a successful outcome here, exactly as in QG-19.

---

## Family 1 — own vocabulary {#family-1}

| # | Query | Bearing results |
|---|-------|-----------------|
| 1.1 | `"regime" decidable membership predicate trade currency intrinsic support number rotation count compilation geometry` | none |

Returned exchange-rate-regime economics (Princeton IES, CFA, Wikipedia
*Managed float regime*, *Currency union*) and formal-logic decidability notes
(Cambridge *Supplementary notes on decidability*, Grokipedia *Decidability
(logic)*). Nothing bears on quantum compilation.

**Verdict (record QG24-C4): `NO_PRIOR_ART_FOUND`.** This is **not a novelty
grant**. It is a statement about this programme's private vocabulary: the
programme's own words do not retrieve the field that owns the mathematics. The
claim this family would have protected is removed anyway under Family 2 — which
is precisely QG-19's mechanism, and precisely why all three families are
mandatory.

## Family 2 — donor-field translation {#family-2}

| # | Query | Bearing results |
|---|-------|-----------------|
| 2.1 | `merging adjacent Pauli rotations same axis reduce T count phase polynomial optimization Clifford+T` | **killing** |
| 2.2 | `T-par matroid partitioning phase polynomial T-count reduction CNOT+T circuits Amy Maslov Mosca` | context |
| 2.3 | `TMerge Pauli rotation merging same axis T-count optimal algorithm arXiv` | **killing** |
| 2.4 | `"merging those exponentials of the same Pauli" "commuting Paulis in between" stabiliser reduction Pauli exponentials` | **killing** |
| 2.5 | `Pauli rotation merging "same axis" condition "commute" between them circuit optimisation T-count Vandaele` | supporting |

### QG24-C1 — the merge relation itself → **SUBSUMED**

Claim: *two arbitrary-angle Pauli rotations about the same axis, separated only
by operations that commute with that axis, may be merged into one, lowering the
non-Clifford count.*

Source: the **TMerge** / Pauli-rotation-merging line, as reported for
*Optimal number of parametrized rotations and Hadamard gates in parametrized
Clifford circuits with non-repeated parameters*, arXiv:2407.07846.

> "TMerge reduces the T-count by exploiting the commutativity of Pauli rotation
> axes, reordering gates within each T layer and merging rotation gates that have
> the same axis."

Supporting, from query 2.5:

> "Two Pauli rotations R(P₁) and R(P₂) commute if and only if the corresponding
> Pauli strings P₁ and P₂ commute."

The relation frozen in QG-24 protocol §2 is this relation. Novelty removed —
which the protocol already conceded ("donor mathematics and carries zero novelty
credit in this lane"); the search confirms the concession rather than
discovering it.

### QG24-C2 — that this rewrite is the right one → **SUBSUMED**

Source: A. Cole, *Quantum Circuit Optimisation Through Stabiliser Reduction of
Pauli Exponentials* (Oxford thesis; document fetch `EGRESS_BLOCKED`).

> "Writing a circuit as a series of Pauli exponentials and merging those
> exponentials of the same Pauli when there are only commuting Paulis in between
> them is essentially the best possible rewrite strategy when minimising the
> number of non-Clifford components of the circuit."

This is QG-24's objective (`θ_rot`, non-Clifford count) and QG-24's rewrite,
stated as the known best strategy. Novelty removed.

### Context (not a verdict): T-par / phase polynomials

> "Using matroid partitioning, Amy, Maslov, Mosca created an automated,
> polynomial time tool for reducing and parallelizing T gates called T-par."

> "The circuit's phase polynomial was shown to be expressible as a weighted sum
> of linear Boolean functions … used to optimize both T-count and T-depth."

Confirms the protocol's recorded prior that this is a heavily worked area.

## Family 3 — inverted / survey {#family-3}

| # | Query | Bearing results |
|---|-------|-----------------|
| 3.1 | `lower bounds T-count minimization NP-hard survey fault-tolerant resource estimation magic state count` | **narrowing** |
| 3.2 | `"Optimising T-count is NP-hard" van de Wetering Amy abstract` | **narrowing** |

### QG24-C3 — the residual candidate → **INSTANCE_OF_KNOWN_GENERAL**

Residual claim: *that the seven-rotation floor of this frozen grammar, and the
decidability of reaching it, is a regime-geometry statement rather than an
instance of known rotation merging.*

General result (arXiv:2407.07846):

> "An efficient algorithm for solving the Pauli rotation merging problem
> constructs the associated optimized quantum circuit with a complexity of
> O(nM+nhm) where h is the optimal of internal Hadamard gates required to
> implement the initial sequence of Pauli rotations."

Complexity backdrop — van de Wetering & Amy, *Optimising quantum circuits is
generally hard*, arXiv:2310.05958:

> "optimising the T-count or T-depth in Clifford+T circuits, which are important
> metrics for the computational cost of executing fault-tolerant quantum
> computations, is NP-hard"

and, from query 3.1:

> "a unitary's stabilizer nullity is a lower bound for T-count"

**Reading.** The general problem is NP-hard; QG-24's instance is decidable in
`O(n)` only because the frozen grammar is a nine-rotation sequence with a fixed
seam structure. That is the shape of a *specialization*, not of a new result.
The general merging rule, its optimality and its complexity are donor property.
**What survives is at most the arithmetic** that in *this* grammar the relation
admits exactly the two block seams, so the floor is 7 and not 9, and that the
floor is reachable on every real row — an accounting fact about a committed
family, which is what a lane at `NOT_R6` is entitled to.

---

## Summary of verdicts

| record | claim | verdict | source | doc-level |
|--------|-------|---------|--------|-----------|
| QG24-C1 | merge relation | `SUBSUMED` | TMerge / arXiv:2407.07846 | false |
| QG24-C2 | rewrite is best for non-Clifford count | `SUBSUMED` | Cole, Oxford thesis | false |
| QG24-C3 | 7-floor + decidability as regime geometry | `INSTANCE_OF_KNOWN_GENERAL` | arXiv:2407.07846; arXiv:2310.05958 | false |
| QG24-C4 | own-vocabulary framing | `NO_PRIOR_ART_FOUND` (**not a grant**) | — | false |

`novelty_credit: false`, `novelty_authority: false`, `donor_novelty_credit: false`.

## Sources

- [Optimal number of parametrized rotations and Hadamard gates in parametrized Clifford circuits with non-repeated parameters (arXiv:2407.07846)](https://arxiv.org/pdf/2407.07846)
- [Quantum Circuit Optimisation Through Stabiliser Reduction of Pauli Exponentials — A. Cole (Oxford)](https://www.cs.ox.ac.uk/people/aleks.kissinger/theses/cole-thesis.pdf)
- [Optimising quantum circuits is generally hard — van de Wetering & Amy (arXiv:2310.05958)](https://arxiv.org/abs/2310.05958)
- [Polynomial-Time T-Depth Optimization of Clifford+T Circuits Via Matroid Partitioning — Amy, Maslov, Mosca](https://www.semanticscholar.org/paper/Polynomial-Time-T-Depth-Optimization-of-Clifford+T-Amy-Maslov/91c90eca57fbfb022d22c83b7a349149cfbe6512)
- [Lower bound for the T count via unitary stabilizer nullity (arXiv:2103.09999)](https://arxiv.org/pdf/2103.09999)
- [Nontrivial multi-product commutation relation toward reducing T-count in sequential Pauli-based computation (arXiv:2509.20052)](https://arxiv.org/pdf/2509.20052)
