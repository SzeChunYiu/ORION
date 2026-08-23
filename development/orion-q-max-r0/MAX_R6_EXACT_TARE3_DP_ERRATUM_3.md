# MAX-R6 exact TARE-3 joint DP erratum 3

Date: 2026-08-20
Applies before any exact-joint-DP outcome.
Authority: pre-outcome implementation/comparator exactness clarification only; no R6 or novelty authority.

## E4 — exact characterization of the frame-only minimum set

Erratum 2 defines `B_FRAME_ONLY_STRONG` by first retaining every auxiliary-frame/central-axis pair attaining the global minimum of

`C_Uanti_parity = sum_k mu_k (w(R_k)-1)`,

with `mu_c=2` and the other two multiplicities equal to `4`, under pairwise anticommutation.

Literal enumeration of every `n`-qubit Pauli triple is unnecessary and becomes impractical on the open 8- and 12-qubit subjects. The retained minimum set is nevertheless exactly characterizable before any target outcome:

1. pairwise anticommutation implies every `R_k` is nonidentity, hence every `w(R_k)-1 >= 0` and `C_Uanti_parity >= 0`;
2. zero is attainable by `X_q,Y_q,Z_q` on any single system qubit `q`;
3. equality `C_Uanti_parity=0` requires `w(R_k)=1` for all three strings;
4. three weight-one Pauli strings can be pairwise anticommuting only when they act on the same qubit and are the three distinct nonidentity single-qubit Paulis;
5. therefore the complete global Uanti-minimum set is exactly all ordered permutations of `(X_q,Y_q,Z_q)` for every system qubit `q`, with every central axis. Since all three weights are one, every central axis has the same zero Uanti cost.

The implementation may generate this complete minimum set directly rather than enumerate nonminimal global frames. It must still perform Erratum-2 stage 2 exactly over every retained frame, target permutation, admissible distinct label assignment, exact Tag solution and Restore string. This is an exact reduction of the same comparator, not a new or weaker baseline.

## E5 — top-four panel cardinality is a gate

Erratum 1's expensive-verifier panel is exactly the deterministic top four **improving** P10 triples per open subject. If either open subject supplies fewer than four improving P10 triples, the exact-joint development cannot claim its positive terminal. The receipt must report the selected count per subject and the development conjunction must include

`TOP_FOUR_PANEL_COMPLETE = (selected_count_H4 == 4 and selected_count_eqN2 == 4)`.

No fifth or substitute triple may be introduced after seeing the exact-joint outcome.

No scientific objective coefficient, donor credit, subject, threshold, evidence budget, or protected-subject rule changes. Errata 1 and 2 remain controlling.
