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

## Status: TESTED NEGATIVE — the correspondence is a COSTUME

The candidate was tested by measured transfer and **failed**. Recorded as a
tested negative, not carried forward as a MechanicCandidate.

### The transfer produces nothing

**Freeze–Schmid Prop. 3.1(2) -> probe depth: no nonvacuous reading exists.** The
load-bearing step in FS is `|B| = |U^-1 B| + |U|` — the measure decomposes
additively across the peel and **the cost of the peel is its size `|U|`, a
variable quantity**. `M` must be "the cost of one peel". In QG **every probe
costs exactly 1**, whatever its arity or how much it splits. So `M = 1` gives
`D(S) <= D(S_v) + 1`, which is literally the definition; any `M >= 1` is weaker.
Every reading is vacuous — FS's `+M` has nothing to bind to, because QG has no
variable per-step cost.

**The arity bound -> zero-sum: the counterpart quantity does not exist.**
`ceil(log_a |S|)` is a counting bound needing a branching parameter. FS has none;
its lower bounds are constructions (`D_k(G) >= k*exp(G)`, and
`D_k(G) >= D(G^-) - 1 + k*exp(G)` by appending `k` copies of a maximal-order
element). Forcing the transfer predicts `D_k` logarithmic in `k`; **the paper
proves the opposite** — `D_k(G) = D_0(G) + k*exp(G)` for large `k`.

### Where it breaks — four places

1. **FS's `max` is not over branches.** In `max{D_k + l, s_{<=l}(G) - 1}` the
   second argument contains **no recursive call**; it is an absolute cap from the
   definition of `s_{<=l}`. The shape is `T(k+1) <= max{T(k)+c, C}` — a monotone
   recurrence with a ceiling. In QG every argument of the max is a recursive call
   and every branch must be resolved. Both spelled "max"; one quantifies proof
   cases, the other adversarial replies.
2. **FS's `min` is decoupled from the successor, so there is no fixed point.**
   Prop. 3.1(3) holds *for each* `l`, so one minimises afterwards — but `l` does
   not change `D_k`. FS runs one-directionally along a **total** order and
   therefore **unrolls to a closed form**, which is exactly how the paper obtains
   `D_k = D_0 + k*exp(G)`. QG runs over a **partial** order with branching,
   cannot be unrolled, and needs fixed-point iteration over 4,441 states.
3. **The two `D`s are not the same type.** `D_k : N -> N` versus
   `D : 2^X -> N`. Nothing in FS plays the role of the state `S`.
4. **Decisive — the growth laws disagree.** FS is **linear** in the ladder index
   (slope `exp(G)`); QG is **logarithmic** in state size (`3 = ceil(log_4 48)` at
   the top). That is the signature of no-branching versus branching. A shared
   composition law would produce the same growth law.

The "chosen versus forced" asymmetry is real and is part of (2): `M` in Prop.
3.1(2) is a min over which `U` *exist* inside an extremal `B` — extremal
bookkeeping determined by `G` and `k`, optimised by nobody.

### What kills the delta organ specifically

The proposed object was "a refinement lattice whose nodes carry a resolution
**cost**". The cost annotation is the entire delta. But:

- in QG **every probe costs 1** — the lattice is depth-annotated, not
  cost-weighted; there is no nontrivial per-node weight anywhere in the instance;
- in FS the per-rung cost `M = |U|` **is** genuinely variable — but FS has no
  lattice, only `N`.

**The lane with variable costs has no lattice; the lane with a lattice has no
variable costs. Neither instance exhibits the object being proposed.** The two
recursions agree only where the cost annotation is trivial, which is fatal for a
proposal whose whole content is that annotation. Pacini's lattice nodes are
indeed unweighted — but QG-34 does not supply the missing weights either. It
supplies one global depth, `D_* = 3`.

### Named revival path (the negative is not terminal, but it is not open either)

The two lanes disagree precisely on whether per-rung cost is variable. So the
honest next question is narrow and answerable: **does the QG setting admit a
variable-cost probe model at all** — probes with genuinely different acquisition
costs? If it does not, there is no cost-annotated ladder to build from this pair,
and the correct move is to leave Pacini's lattice unweighted and say so.

### What is untouched

QG-34 (`D_* = 3`, minimality certified at depth 2, independent re-derivation
agreeing per class) and C1 (the spectrum is the maximal symmetry quotient) never
depended on this analogy and stand on their own. QG-35 likewise.

### A near-miss worth recording

The adversarial reviewer first flagged the committed
`arity_lower_bound_tight_on: 80` as arithmetically impossible, on the assumption
that probes are Pauli-valued so arity `<= 4`. **That assumption was wrong and the
flag was withdrawn by the reviewer.** `K` is an integer cost difference
(`config_cost - baseline`) taking **11** values (`-3..7`), with per-class max
arity up to **6**. Recomputing with true arities gives lower-bound histogram
`{0:7, 1:30, 2:51, 3:4}` against depth `{0:7, 1:30, 2:39, 3:16}`, forcing exactly
`51 - 39 = 12` classes past the bound: **not tight on 12, tight on 80 of 92** —
the committed figure, now **independently reproduced from `main` by a third
implementation**. Recorded because the near-miss is the useful part: a reviewer
nearly shipped a false positive by not checking what the quantity ranges over.
