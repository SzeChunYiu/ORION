# Literature entailment and novelty-subtraction audit

Date: 2026-08-28

## Search state

This audit reconciles the full-text primary-source subtraction record dated 2026-08-26, the additive 2026-08-28 search rerun, and the hostile prior-art gate. The inspected sources and identifiers remain recorded in the bound evidence. Search limitations include incomplete index neighborhoods, patents, private manuscripts, unindexed software, non-English sources and work after the cutoff.

## Entailment table

| Source family | What the source establishes | What is subtracted from this paper | Residual manuscript statement |
|---|---|---|---|
| Schillo, Sturm and Quay, TARE v4 | Tag-and-Restore block encoding; freely chosen anticommuting frames; shared label construction and resource tradeoffs | invention of TARE, Tag/Restore, frame freedom and generic resource tradeoffs | one fixed TARE-derived grammar has a cost-monotone support-two optimum normal form |
| Izmaylov et al. | anticommuting-unitary partitioning | anticommuting grouping as a new primitive | exact grammar/objective threshold only |
| Cowtan et al.; Amy et al. | one/two-qubit phase-gadget decompositions and parity sharing | support-two components and sharing as new ideas | auxiliary-frame exchange preserving the declared optimum |
| DiVincenzo; Fattal et al. | two-qubit universality and stabilizer normal-form foundations | two-local universality and stabilizer methods as new | sharp objective-specific frame threshold only |
| van den Berg and Temme; PCOAST; PHOENIX; Symphony | Pauli-cluster and Pauli-level compiler optimization, including symplectic simplification | first Pauli optimization, first support reduction or general compiler improvement | narrow exact normal form and direct upper bound |
| Hastings; Kempe--Kitaev--Regev | Hamiltonian weight reduction and perturbative gadgets | broad weight-reduction novelty | different object: no added degrees of freedom and no approximate encoding |

## Donor contribution crosswalk

The final manuscript now makes the exact donor delta reader-visible:

- **Inherited:** the Tag-and-Restore primitive in Section 4 of arXiv:2601.05740v4; the user-selectable anticommuting frames, ancilla count and controls in Theorem 1 / Remark 1; and nonunique optimizable label solutions in Theorem 2 / Remark 2.
- **Donor numerical specialization:** the donor's Section 5 comparison fixes its canonical frame family and independently minimizes the label strings.
- **Present specialization:** six target slots, three paired blocks, branchwise three-way factorization, one common binary syndrome, two/four frame multipliers and the normalized logical objective.
- **Present analysis objects:** the normalized logical support objective, support-capped frame families, the cost-nonincreasing support-two transformation, the sharp two-qubit obstruction and constructive exact-solvability bound.
- **Explicitly not claimed:** invention of selectable frames or label optimization, a universal donor objective, or a general compiler/resource improvement.

The arXiv API was rechecked on 2026-08-28 and still identified version 4, updated 2026-05-13. The bibliography and manuscript now bind that version and the exact full-text anchors above.

## Exact-equivalent search result

The bounded current searches, refreshed through 2026-08-28 with the query families listed in the manuscript, did not locate a source stating the complete combination of:

- this three-block shared-label grammar;
- this exact support-count objective;
- the per-coordinate cost-monotonicity exchange;
- the sharp paired-instance support-one obstruction; and
- the induced exact `O(n^9)` direct algorithm.

This is a search observation, not proof of absence or priority. The manuscript says so explicitly and makes no “first”, “novel”, “unique”, “general”, “superior” or top-tier claim.

## Significance adjudication

The hostile gate found every broad mathematical ingredient to be published or folklore and reduced the defensible contribution to grammar-specific cost bookkeeping plus an exact algorithmic consequence. The adverse runtime result removes a practical-performance route to significance. The bounded residual may support a focused formalization note, but does not satisfy Quantum's requirement for a very significant advance beyond the state of the art.

## Citation closure

The final bibliography includes the direct TARE donor, anticommuting partitioning, phase gadgets, parity networks, two-qubit universality, stabilizer normal forms, Pauli compilers, current binary-symplectic work, Hamiltonian weight reduction and perturbative gadgets. The manuscript does not use literature to warrant its internal theorem; citations delimit ownership and neighboring objects.

## Audit terminal

- Theorem/proof originality claim: **not made**.
- Bounded residual formulation: **fairly stated**.
- External novelty authority: **not established**.
- Quantum significance gate: **not met**.
- Final implication: `scientifically_sound_but_target_mismatch`.
