# ORION-QG — position-symmetry ceiling on the TARE column alphabet

Generic-ORION replay of QG-28 (`#888`) plus an exact symmetry-quotient lattice
that fixes a hard ceiling on what any position-symmetric probe family can
separate. Direct consumers: QG-31 `#904`, QG-32 `#911`, QG-32b `#918`,
QG-33 `#920`, QG-34 `#924`.

## Authority

- `mathematical_proposal: true`, `proof_authority: false` beyond the
  machine-checked counts below, `novelty_claim: false`
- **No R6 / compiled-resource claim.** Nothing here touches compiled cost.
- No credit taken over Burnside/Pólya counting, local-Clifford symmetry, or the
  QG-26/27/28 chain. QG-28's expected census is the *donor* here; this lane
  supplies the independent replay that `#888` Q1 explicitly demands
  ("Generic ORION rebuilds `F_2^2` independently") plus one new theorem.

## Part 1 — independent replay of QG-28

`research/extensions/orion-qg/qg28_generic_replay.py` rebuilds the phase-free
one-qubit Pauli algebra from `F_2^2` symplectic coordinates
(`I=(0,0), X=(1,0), Z=(0,1), Y=(1,1)`) and derives, without importing any
production R6M table:

- `local_mul(a,b) = a XOR b`, `local_symp(a,b) = a_x b_z + a_z b_x (mod 2)`,
  `local_wt(a) = [a != I]`;
- the 6 automorphisms of `{I,X,Y,Z}` fixing `I` and permuting `X,Y,Z`;
- equivariance of `local_mul` and invariance of `local_symp`, `local_wt` under
  all 6 — **all pass**;
- Burnside over the diagonal `S_3` action on six letters:
  `identity 4096`, `three transpositions 64 each`, `two 3-cycles 1 each`,
  `(4096 + 192 + 2)/6 = 715`;
- explicit enumeration of all 4096 types: **715 orbits**, size histogram
  `{1: 1, 3: 63, 6: 651}`, canonical representative = lexicographic minimum.

Every number matches the frozen expectation on `#888`. Replay verdict:
**CONFIRMED**.

`F3` is named in `#888` Q1 but its defining table is not reproduced in the issue
text, so it is **not** checked here. That check remains open and is recorded as
such rather than asserted.

## Part 2 — exact symmetry-quotient lattice (new)

`qg_symmetry_quotient_lattice.py` computes the exact orbit count of the 4096
types under every natural subgroup of `S_3(letters) x Sym(6 positions)`.

**Stated assumption.** The six target letters are taken to be paired into three
blocks of two, following the three-block TARE language used across QG-7/QG-23.
The position subgroups tabulated are: swapping the two targets inside a block
(`S_2^3`), permuting the three blocks (`S_3`), their wreath product
`S_2 wr S_3`, and the full `S_6`. The counts below are pure combinatorics on six
positions and stand independently of that pairing; only the *naming* of the rows
depends on it, and the full-`S_6` row bounds every position group whatsoever.

| letters | positions | `\|G\|` | orbits |
|---------|-----------|------|--------|
| trivial | trivial   | 1    | 4096 |
| trivial | swaps     | 8    | 1000 |
| trivial | blocks    | 6    | 816 |
| trivial | wreath    | 48   | 220 |
| trivial | full `S_6`| 720  | 84 |
| `S_3`   | trivial   | 6    | **715** |
| `S_3`   | swaps     | 48   | 199 |
| `S_3`   | blocks    | 36   | 160 |
| `S_3`   | wreath    | 288  | **54** |
| `S_3`   | full `S_6`| 4320 | 23 |

Two of the three partition cardinalities QG-31 reports fall exactly on this
lattice, and one does not:

- **715** (indexed response) `=` orbits under `S_3 x trivial` — by construction,
  this is QG-28.
- **54** (unlabeled one-active defect spectrum) `=` orbits under
  `S_3 x (S_2 wr S_3)`, the **coarsest** quotient by the full admissible
  symmetry group.
- **45** (bulk signature) is **not** an orbit count of any subgroup in the
  lattice. So the bulk signature is a computed statistic, not a symmetry
  quotient — which is consistent with QG-31 finding bulk and spectrum
  incomparable, and explains *why* they are of different kinds.

## Theorem (position-symmetry ceiling)

> Let `P` be any family of probes on the TARE target-column alphabet whose every
> member is invariant under the letter group `S_3` and under the position group
> `S_2 wr S_3`. Then the joint response map `o -> (K_p(o))_{p in P}` is constant
> on each of the 54 orbits of `S_3 x (S_2 wr S_3)`, so `P` separates at most 54
> of the 715 orbit types — **for every cardinality of `P`, including infinite**.

*Proof.* Each `K_p` is invariant under the group, hence constant on its orbits;
a tuple of orbit-constant functions is orbit-constant. ∎

### Consequence for QG-32 / QG-32b / QG-33 / QG-34

QG-32 asks for the smallest fixed subset of the 384 indexed probes that
separates all 715 types above the joint bulk+spectrum summaries. The theorem
says no amount of position-symmetric probing can get past 54 classes, so:

- every separating probe set **must** contain position-asymmetric probes;
- the separating power of the indexed family comes from position indexing, not
  from letter structure — the letter structure is already fully spent in
  reaching 715 from 4096;
- for QG-34, an adaptive tree over a position-symmetric probe family has
  unbounded depth with no separation past 54; adaptivity cannot substitute for
  position asymmetry.

This is a ceiling, not a lower bound on the number of probes. It does not
predict QG-32's minimum, and it is silent on QG-32b's four-probe question.

## Falsifiable conjecture (registered before QG-31 merges)

> **C1.** QG-31's 54-class unlabeled one-active defect spectrum partition is not
> merely equinumerous with, but **equal to**, the orbit partition of the 4096
> column types under `S_3(letters) x (S_2 wr S_3)`.

C1 is decidable the moment `#904` merges: compare the two partitions as set
systems. If C1 holds, the defect spectrum *is* the maximal symmetry quotient and
the ceiling above is exactly its information content. If C1 fails, the equality
of cardinalities at 54 is a coincidence and must be reported as one.

## Reproduction

```
python3 research/extensions/orion-qg/qg28_generic_replay.py
python3 research/extensions/orion-qg/qg_symmetry_quotient_lattice.py
```
