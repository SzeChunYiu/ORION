# A Nine-Qubit Auxiliary Interaction Core for Shared-Tag TARE-M2 — R10

Date: 2026-08-26

Status: analytic corollary of the proved Q1 support-two theorem for the frozen three-block shared-Tag TARE-M2 grammar. This note strengthens the representation consequence; it does not by itself claim a circuit, hardware, or fault-tolerant resource reduction.

## 1. Frozen Q1 input

Q1 proves that every admitted instance of the frozen R6M three-block grammar has an exact optimum in which each of the six auxiliary frame Paulis

`R_{j0}, R_{j1}`, `j in {A,B,C}`

has Pauli support at most two, while each within-block pair anticommutes.

The three blocks share one Tag Pauli `S`. Its label constraints are

`<S,R_{j0}>=l_0`,

`<S,R_{j1}>=l_1`,

with the same ordered label pair for every block and `l_0 != l_1`.

The Tag contributes `2 wt(S)` to the frozen objective. Restore strings depend on targets and frames, not directly on Tag letters outside the frame supports.

## 2. One block occupies at most three auxiliary coordinates

### Lemma Q1-R10.1

If two nonidentity Pauli strings `R_0,R_1` anticommute and both have support at most two, then

`|supp(R_0) union supp(R_1)| <= 3`.

### Proof

Anticommutation means their binary symplectic product is one. If the supports were disjoint, every local symplectic contribution would be zero. Hence the supports intersect. Two sets of size at most two with nonempty intersection have union size at most three. ∎

## 3. Nine-qubit frame core

Let

`U = union_{j,k} supp(R_{jk})`.

### Corollary Q1-R10.2

Every Q1 instance has an exact optimum whose six auxiliary frame Paulis are supported on a common set `U` satisfying

`|U| <= 9`.

### Proof

Apply Lemma Q1-R10.1 to each of the three anticommuting block pairs. Each block contributes at most three coordinates to the union. ∎

The bound is independent of the system qubit count `n`.

## 4. The shared Tag can be projected into the same core

For a Pauli `S`, write `S|_U` for the Pauli obtained by replacing every local letter outside `U` by identity.

### Theorem Q1-R10.3 — constant auxiliary active core

Every admitted instance has an exact optimum for which

1. all six auxiliary frames are supported in a common `U` with `|U|<=9`; and
2. the common Tag can also be chosen with `supp(S) subseteq U`.

Therefore the union of the supports of **all six frames and the shared Tag** has size at most nine.

### Proof

Start from the support-two optimum supplied by Q1 and let `U` be its frame union. For every frame `R_{jk}`, all local letters outside `U` are identity. Consequently

`<S|_U,R_{jk}> = <S,R_{jk}>`

for all six frame strings. Thus `S|_U` satisfies exactly the same six shared-label equations as `S`.

Because the label orientation is nonconstant (`l_0 != l_1`), at least one of those symplectic equations equals one, so `S|_U` cannot be the identity. Its support is no larger than that of `S`, hence its Tag cost `2 wt(S|_U)` does not increase. Frame costs and Restore strings are unchanged because no frame or target is changed.

Replacing `S` by `S|_U` therefore preserves feasibility and cannot increase the total frozen objective. Starting from an optimum yields another optimum with the stated support property. ∎

### Interpretation

The theorem concerns the **auxiliary interaction core**. A target Pauli and its Restore string may have support outside `U`; however, outside `U` every frame letter is identity, so the Restore string agrees locally with the target. The theorem does not claim that the physical Hamiltonian, target support, or final circuit is nine-qubit.

## 5. A six-bit-variable Tag witness

The previous theorem bounds Tag support by nine because it projects onto the frame core. A second purely linear-algebraic observation gives a smaller independent Tag bound.

### Proposition Q1-R10.4

For any fixed feasible six-frame configuration in the frozen grammar, if a compatible Tag exists then there is a compatible Tag with Pauli support at most six.

### Proof

The six label equations are a consistent linear system over `F_2` in the `2n` binary `X/Z` Tag variables. Let its rank be `r<=6`. The right-hand side lies in the span of the `2n` variable columns. Choose a basis of at most `r` variable columns spanning the right-hand side and set only those variables nonzero. This produces a solution with at most `r<=6` nonzero binary variables and therefore Pauli support at most six. ∎

The support-six statement is not needed for Theorem Q1-R10.3, but it shows that the shared-Tag degree of freedom is itself constant-support once the six frame constraints are fixed.

## 6. Exact anticommuting support-two pair count

The original Q1 manuscript gives the looser raw six-frame family `O(n^12)` by treating six support-two frames independently. Anticommutation yields a sharper exact count at the block level.

Let `P(n)` be the number of **ordered** anticommuting pairs `(R_0,R_1)` of nonidentity `n`-qubit Paulis with each support at most two.

### Theorem Q1-R10.5

`P(n) = 6n + 54 n (n-1)^2`

or equivalently

`P(n)=54n^3-108n^2+60n`.

### Proof

Partition by frame weights and support overlap.

1. `(1,1)`: both strings must use the same qubit. There are `6n` ordered distinct local Pauli pairs.
2. `(1,2)` and `(2,1)`: the weight-one support must be one endpoint of the weight-two support. For one orientation there are

   `n (n-1) * 3 * 2 * 3 = 18 n(n-1)`

   pairs, hence `36 n(n-1)` for both orientations.
3. `(2,2)` with identical two-qubit support: for each support pair, after the first two local letters are chosen, exactly four of the nine second-string local-letter pairs give odd total symplectic parity. This contributes

   `36 C(n,2)=18n(n-1)`.
4. `(2,2)` with one shared coordinate: choose the shared coordinate and the two ordered distinct private coordinates. The local letters contribute `3*3*2*3=54`, giving

   `54 n(n-1)(n-2)`.

Disjoint supports commute. Summing the four cases gives

`6n + 54n(n-1) + 54n(n-1)(n-2) = 6n + 54n(n-1)^2`. ∎

Checks: `P(1)=6`, `P(2)=120`, `P(3)=666`, matching the existing QG-28 support-capped implementation records.

## 7. An O(n^9) direct exact checker after preprocessing

The three block frame pairs can therefore be enumerated in

`P(n)^3 = O(n^9)`

combinations, up to the frozen constant factors for branch permutations, central choices, and the two label orientations.

The nine-qubit active-core theorem removes a further apparent system-size dependence from candidate evaluation:

- for fixed target matching/permutation, precompute the target-only Restore-factor contribution over all `n` coordinates;
- a candidate frame triple differs from the identity-frame baseline only on its active core `U`, with `|U|<=9`;
- update the precomputed Restore contribution only on those at-most-nine coordinates;
- solve the six Tag parity constraints on `U` (or by the constant-rank syndrome formulation).

### Corollary Q1-R10.6

For the frozen fixed-six-slot grammar, there exists a direct theorem-certified exact checker with `O(n^9)` candidate combinations and `O(1)` candidate-local evaluation after `O(n)` preprocessing, with constants depending on the fixed grammar but not on `n`.

This is an **algorithm-existence and completeness corollary for the frozen grammar**, not a claim that it beats the current 512-state XOR dynamic program in wall time. Indeed, the existing QG-28 measurements show that the naive support-capped enumerator is substantially slower on `n<=3`; the scientific value is a different exact architecture whose search space is polynomial for an independent reason.

## 8. Relationship to existing QG-28 engineering evidence

The existing QG-28 lane already realized a support-capped exact search and compared it with the committed family search on 13,368 declared instances. It also showed that the shared Tag sweep can be replaced by a 64-state syndrome DP, and its prospective cell-count model predicts a crossover only at larger `n` (reported as `n=7` for the table-driven count and `n=9` for the DP variant). Small-`n` measured wall times favor the existing search.

The R10 result strengthens the analytic side:

- exact block-pair count `P(n)` rather than six independent frame counts;
- constant nine-qubit auxiliary footprint;
- constant-support Tag projection;
- a direct `O(n^9)` preprocessed checker rather than the earlier `O(P(n)^3 n)` cell accounting.

Any measured crossover for the new checker must be obtained prospectively; it cannot be inferred from the QG-28 wall-clock data.

## 9. High-value application hypotheses

The theorem creates three falsifiable application questions.

### A. Exact compiler kernelization

Can the nine-qubit auxiliary core be used as a kernel for independent exact verification or certification of a production TARE optimizer? A proof receipt can name `U`, the six frames, the projected Tag, and the objective decomposition.

### B. AI-guided exact search with a theorem shield

A learned/LLM heuristic may propose the active core `U`, frame pairs, or ordering, while exactness remains protected by exhaustive fallback over the theorem-certified `O(n^9)` family and semantic checks. The heuristic may change search order, never the admissible completeness envelope.

### C. Hardware/locality mapping

Because all auxiliary frame/Tag operations can be concentrated on at most nine system coordinates, one may test whether mapping those coordinates to a low-diameter hardware subgraph reduces routing or two-qubit overhead. This is an **experimental hypothesis only**: the theorem does not account for target-string support, Restore synthesis, normalization, or hardware-native compilation.

## 10. Publication boundary

The paper may claim, after independent proof review:

> The sharp support-two theorem implies a system-size-independent nine-qubit auxiliary interaction core and an exact `O(n^9)` direct checker for the frozen three-block TARE-M2 grammar.

It may not claim without downstream measurements:

- a nine-qubit physical circuit;
- constant circuit depth;
- a universal TARE or block-encoding kernel;
- fault-tolerant resource reduction;
- quantum advantage; or
- superiority to the existing dynamic program.
