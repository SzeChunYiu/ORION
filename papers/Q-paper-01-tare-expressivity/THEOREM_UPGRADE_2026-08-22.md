# Q1 theorem upgrade note — 2026-08-22

Status: publication-derivation note from already committed ORION-Q receipts. This file introduces **no new experimental data** and grants no novelty or R6 authority. Its purpose is to state consequences of the final closed ORION-Q mathematics that were not yet foregrounded in `MANUSCRIPT_V1.md`.

## 1. Sharp intrinsic support number for the frozen R6M grammar

Define the **uniform frame-support number** of the frozen R6M family by

\[
\kappa_{\mathrm{R6M}}
:= \min\{k:\ \text{every admitted R6M instance has an exact optimum in which every frame Pauli has support }\le k\}.
\]

The final ORION-Q receipts determine this number exactly.

### Upper bound

`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` proves, for every qubit count `n`, every target six-tuple, every perfect matching, every target permutation, and every central choice in the frozen R6M grammar and frozen support-count objective,

\[
C_{\mathrm{DP}}=C_{D^{++}},
\]

where `D++` restricts every frame Pauli to global support at most two. Hence

\[
\kappa_{\mathrm{R6M}}\le 2.
\]

### Lower bound

`research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` contains an exact structured-`n=2` counterexample (`instance_index = 16`) with

\[
C_{\mathrm{DP}}=5 < 6=C_{D^+}.
\]

`D+` exhausts the frozen family with **all frames restricted to support one**, arbitrary per-block anchors, and the unique minimum-weight compatible shared Tag. Therefore no all-support-one representation attains the unrestricted optimum on this instance, so

\[
\kappa_{\mathrm{R6M}}>1.
\]

Combining the two bounds gives the sharp statement

\[
\boxed{\kappa_{\mathrm{R6M}}=2.}
\]

The threshold is attained already at two qubits. This is stronger and cleaner than saying merely that support two is sufficient.

## 2. Why support two is the exact boundary

R6S does more than establish the upper bound. Its exchange proof associates each qubit in the support of a frame Pauli with a class `(alpha,beta) in F_2^2`. For support `w >= 3`, the odd-alpha condition forces a proper zero-sum subset of size at most two; zeroing that subset preserves both the required local anticommutation bit and the shared-Tag syndrome, while the exhaustive Lemma-E table proves that the Restore-factor increase never exceeds the refunded frame cost.

The composition argument fails **exactly at weight two** on four class tuples. The R6S receipt identifies these patterns with the already observed R6O mechanism: a locally commuting frame letter can still anticommute with the shared Tag, so deleting it forces a Tag-syndrome change. The exact R6O counterexample realizes this obstruction physically inside the frozen compiler grammar.

Thus the theorem and counterexample meet at the same boundary:

- support `>= 3`: exchange-removable without cost increase;
- support `= 2`: genuine coupling trade can be strictly optimal;
- support `= 1`: insufficient uniformly across the family.

This correspondence should be the conceptual center of the revised Q1 paper.

## 3. Normal-form candidate-count corollary

An `n`-qubit nonidentity Pauli with support at most two has

\[
M_2(n)=3n+9\binom{n}{2}
\]

possible unsigned letter/support assignments: `3n` weight-one Paulis and `9 * C(n,2)` weight-two Paulis.

The frozen three-block R6M grammar has six frame-Pauli slots. R6S therefore implies that an exact optimum is always contained in a direct frame search of at most

\[
M_2(n)^6 = O(n^{12})
\]

raw frame tuples before enforcing the anticommutation and shared-Tag constraints. Per-block target permutations and central choices contribute only a constant factor (`2^3 * 2^3`).

For any fixed frame tuple, a minimum-cost compatible shared Tag never needs support outside the union of the frame supports: a Tag letter outside that union changes no frame-Tag symplectic constraint and only increases the frozen support-count objective. The union contains at most 12 qubits, so a naive local Tag enumeration is bounded by a constant `4^12` independent of `n`.

Consequently the all-`n` theorem gives a **polynomial-size exact normal-form candidate family** for the fixed six-term R6M grammar. A straightforward evaluator that scans the `n` target coordinates per candidate is bounded by `O(n^13)` time up to grammar constants. This is a structural enumeration corollary, **not** a claim that the existing unrestricted dynamic program was exponential; the production DP already exploits additional factorization.

The safe publication claim is therefore:

> R6S collapses the representational candidate family from arbitrary-support Pauli frames to a polynomial-size support-two normal form for the fixed three-block grammar.

## 4. Finite-domain regime classification remains separate

The sharp support theorem does **not** upgrade the R6Q three-family identity or two-trade predicate to an all-`n` theorem. R6Q itself states that its exactness is machine-evidenced on the frozen finite panels only.

This distinction is especially important because subsequent ORION-QG adversarial work (outside the Q1 claim set) found additional support-two subregimes at higher `n`. Those later results do not affect `kappa_R6M = 2`; they do show that the R6N/R6O two-trade closed form must remain explicitly finite-domain in Q1.

The revised paper should therefore separate two statements:

1. **All-`n`, theorem-grade:** `kappa_R6M = 2` under the frozen R6M grammar/objective.
2. **Finite-domain, machine-evidenced:** the R6Q split/borrow predicate and `min(C_R6L,C_D+,f_B)` identity on its registered panels, plus the R6R prospective confirmation on one fresh subject.

## 5. Publication consequence

The Q1 headline should move from

> support-two closure on verified domains

into

> **a sharp all-size normal-form theorem with an exact support threshold, explicit minimal obstruction at the threshold, and finite-domain structural regime prediction.**

This is the main mathematical upgrade required for `MANUSCRIPT_V2.md`.
