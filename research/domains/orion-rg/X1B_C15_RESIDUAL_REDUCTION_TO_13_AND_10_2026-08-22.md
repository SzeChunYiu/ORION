# X1-B theorem — hypothetical C15 counterexamples reduce to only the 13-point and 10-point C3^3 residuals

Parent: reopened #900. Committed before downstream use.

## Setup

Assume for contradiction that `S` is zero-sum-free over

`C_15^3 ≅ C_3^3 ⊕ C_5^3`

with `|S|=43`.

Project to `C_3^3` and greedily remove pairwise-disjoint quotient zero-sums of length 3 until no such triple remains. As in the Bhowmik--Schlage-Puchta donor argument, the residual has size

`3k+1`

with `k<=5`.

The number of removed triples is

`14-k`.

If the residual contains `k-1` further pairwise-disjoint nonempty quotient zero-sums, then altogether we obtain

`(14-k)+(k-1)=13`

pairwise-disjoint quotient zero-sum blocks. Their lifted sums lie in the kernel `C_5^3`, and `D(C_5^3)=13`, so a nonempty subcollection of the 13 kernel block sums is zero. The corresponding union is a zero-sum subsequence of S, contradiction.

Therefore any hypothetical counterexample can survive only when the residual fails to supply `k-1` disjoint zero-sums.

## k<=2 closes immediately

The donor `C_3^3` block-count results used in the classical proof provide the required `k-1` blocks for `k=0,1,2`. Thus these cases close without any kernel-specific inverse structure.

## k=5 also closes quotient-only

The residual has 16 points and contains no quotient zero-sum of length 3 (by maximal greedy removal).

Bhowmik--Schlage-Puchta Lemma 1(2) gives a unique 16-point configuration up to linear equivalence in this no-3-sum extremal situation, and its total sum is zero. Their argument then uses the donor fact that any 15-point submultiset contains three disjoint zero-sums: deleting the complement of those three blocks from a 16-point zero-total sequence yields a fourth zero-sum block.

Hence the 16-point residual contains **four** pairwise-disjoint quotient zero-sums, exactly `k-1=4`.

Together with the `14-5=9` triples removed initially, this yields 13 quotient blocks and therefore a zero-sum upstairs by `D(C_5^3)=13`.

Thus k=5 is impossible for C15, independently of whether the kernel is cyclic or vector-valued.

## Only two residual interfaces remain

Every hypothetical length-43 zero-sum-free sequence over C15^3 therefore reduces to one of:

### k=4

- residual size: 13;
- initial triple blocks: 10;
- generic donor guarantee: 2 residual zero-sum blocks;
- total available: 12;
- need one more effective block/correction.

### k=3

- residual size: 10;
- initial triple blocks: 11;
- generic donor guarantee: 1 residual zero-sum block;
- total available: 12;
- need one more effective block/correction.

These are precisely the residual sizes in which the cyclic donor proof invokes scalar lift-value constraints.

## Consequence for the vector-kernel programme

The fresh p-group local-scalarization lemma need only be made strong enough to reproduce/replace the donor scalar contradiction on:

1. the 13-point k=4 residual; and
2. the 10-point k=3 residual.

No 16-point vector-kernel analysis is needed.

This sharply limits the prospective exact obstruction atlas and makes complete quotient-side enumeration/replay feasible if required.

## Claim boundary

This is a reduction theorem from admitted donor `C_3^3` residual facts and `D(C_5^3)=13`. It does not close the 13- or 10-point interfaces, prove `D(C_15^3)=43`, or establish novelty authority.
