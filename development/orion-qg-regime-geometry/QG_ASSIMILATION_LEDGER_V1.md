# Assimilation ledger — symmetry, invariants and resolution cost

Prior work on descriptor completeness is **absorbed here as parent material**,
not treated as a threat. Each parent is recorded with what it establishes, where
its scope ends, and the measured transfer into the ORION-QG setting. The point
is the synthesis and the delta organ, not overlap-avoidance.

## Parents absorbed

| parent | what it establishes | scope boundary |
|---|---|---|
| **Lehmann**, *Testing Statistical Hypotheses* ch.6 (1959); Lehmann–Casella 3.1.7 | Invariant statistic (Def. 8); **maximal invariant** = identifies orbits (Def. 9); **every invariant factors through a maximal invariant** (Thm. 4) | one group, one action, one statistic. No notion of evaluation or query cost |
| **Pacini, Dong, Lepri, Santin**, *Separation Power of Equivariant Neural Networks*, ICLR 2025 ([arXiv:2406.08966](https://arxiv.org/abs/2406.08966)) | A model's induced partition either coincides with the orbit partition or merges orbits; a **refinement lattice** `Q <= P` compares separation powers | the lattice is unweighted — nodes carry no cost |
| **Balcilar et al.**, ICML 2021 ([arXiv:2106.04319](https://arxiv.org/abs/2106.04319)) | The audit *procedure*: evaluate a descriptor on orbit representatives, count undistinguished pairs (`graph8c`, 11,117 reps, all 61M pairs) | measurement of one layer, empirical |
| **Derksen–Kemper**, *Computational Invariant Theory*; Kemper, *Separating Invariants*, JSC 2009 | Separating sets; for finite `G`, invariants separate all orbits, so **complete ≡ separating** | constructive algebra for one group; orbit-closure subtleties collapse in the finite case |
| **Pozdnyakov et al.**, PRL 125 166001 (2020); **Nigam et al.** APL ML 2 016110 (2024); **Widdowson–Kurlin** CVPR 2023 | Incompleteness of specific chemistry descriptors; constructive complete descriptors; complete + continuous + polynomial-time invariants | specific descriptor families |

**Consequence, stated plainly.** The trichotomy "complete invariant / invariant
but coarser / not invariant" is Lehmann's Definitions 8–9 and Theorem 4. The
audit procedure is Balcilar's benchmark. **Neither is ours, and neither is
claimed.** A separate proposal to publish that trichotomy as a method was killed
by this ledger before any investment — the correct outcome.

## What the parents jointly do not contain

Every parent above answers **"which partition does my descriptor induce?"**
None answers **"what does it cost to finish the job?"**

- Lehmann gives the maximal invariant's *existence*, not its price.
- Pacini gives the lattice of partitions, with **no cost attached to any node**.
- Balcilar measures one node's gap empirically.
- Separating-invariant theory bounds *degrees*, not *queries*.

The ORION-QG instance forces that missing dimension into view:

```
4096 column types
  --(letter S_3 quotient, free)-->            715
  --(bulk 45 + spectrum 54, joint)-->          92
  --(3 adaptive probes, PAID)-->              715 fully resolved
```

C1 proves the spectrum is the maximal symmetry quotient, so the first reduction
is exactly what symmetry gives for free. QG-34 proves the residual costs
**exactly 3** adaptive probes, worst case. That is a **decomposition of
identification cost into a free symmetric part and a paid asymmetric part** — and
the paid part is a min–max fixed point, not a partition.

## The delta organ: cost-annotated resolution ladders

The proposed enveloping object is a refinement lattice in which **every node
carries a resolution cost**, together with a **composition law** governing how
partial summaries combine.

The candidate composition law is a min–max recursion, and the reason to take it
seriously is that **both ORION lanes independently produced one**:

| lane | recursion | peel | recurse on |
|---|---|---|---|
| ORION-QG identification | `D(S) = 1 + min_p max_v D(S_v)` | a probe | the residual class |
| zero-sum obstruction ladder | `D_{k+1} <= max(D_k + l, eta_l - 1)` | an obstruction of size `<= l` | the complement |

Both are peel-and-recurse with a cost/resolving-power trade, evaluated as a
min–max fixed point. Under this reading the parents become the **zero-cost
layer** of the ladder: Lehmann/Derksen–Kemper describe the quotient node,
Pacini's lattice is the ladder's poset with the weights erased.

## Status and the falsifying test

This is a `MechanicCandidate`, **not** a theorem. It must be tiered honestly
(mechanism / lens / costume) and it is not yet earned. The two instances share a
recursion *shape*; that is suggestive and no more.

**Designed falsifier.** The claim is only a mechanism if the cost annotation is
*forced* by the lattice structure rather than fitted after the fact. Concretely:
exhibit two descriptors that induce the **same** partition (same lattice node)
but have **different** resolution costs. If that is impossible, cost is a
function of the node and the ladder is well-defined on the lattice. If it is
easy, cost is extra data and the "envelope" is a costume — in which case the
correct move is to say so and keep the lattice unweighted.

That test is cheap on the QG instance and must be run before any claim.
