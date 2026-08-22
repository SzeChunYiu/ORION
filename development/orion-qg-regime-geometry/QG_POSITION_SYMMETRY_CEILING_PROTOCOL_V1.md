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

**Block pairing (assumed in Part 2, verified in Part 3).** The six target
letters are paired into three blocks of two. Part 3 confirms this against
QG-31's own `perm`, which pairs positions as `(0,1) (2,3) (4,5)`.
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

## Part 3 — C1 is decided, and it is an equality

C1 was registered as a conjecture on a cardinality coincidence. It is now
**decided**, and it holds.

The spectrum's definition was read from the open QG-31 branch
(`origin/codex/orion-qg-qg31-query-abstraction-20260822`, PR #905). Only the
*definition* was taken: both cost primitives it needs
(`max_r6_p10_candidate_blind_frame_optimizer`, `max_r6s_all_n_composition`) are
already on `main`, so `research/extensions/orion-qg/qg_spectrum_symmetry_identification.py`
recomputes every partition here rather than importing any result from that
branch. Nothing below depends on PR #905 being merged or correct.

**Independent reproduction of four reported counts** — bulk **45**, spectrum
**54**, indexed **715**, joint bulk+spectrum **92** — all match.

### Theorem C1 (confirmed)

> QG-31's unlabeled one-active defect-spectrum partition **equals**, as a set
> system, the orbit partition of the 4096 TARE column types under
> `S_3(letters) x (S_2 wr S_3)(positions)`.

Both refinement directions hold, and 0 of the 715 orbit representatives change
spectrum value under any wreath element. Note this also *verifies* the block
pairing that Part 2 had only assumed: QG-31's `perm` pairs positions as
`(0,1) (2,3) (4,5)`, exactly the wreath structure tabulated there.

**What it means.** The spectrum is not merely one summary among many — it is the
**maximal symmetry quotient**. It carries all of the symmetry-invariant
information about a column type and none of anything else.

### Corollary: bulk is provably not a symmetry quotient

`168` of the 715 orbit representatives change bulk value under some wreath
element, and bulk and the symmetry partition refine each other in neither
direction. The mechanism is visible in the definition: `bulk` reads `baseline`
over only the **first 4** of the 8 swap patterns (`ps[:4]`), so it is not even
`S_2^3`-invariant.

This gives a structural explanation of QG-31's finding that bulk and spectrum
are incomparable: they are different *kinds* of object. Spectrum is a group
quotient; bulk is a computed statistic that deliberately breaks the symmetry.

## Theorem (symmetry ceiling) — corrected scope

> Any family of maps on the TARE column alphabet whose every member is invariant
> under `S_3(letters)` and `S_2 wr S_3(positions)` separates at most **54** of
> the 715 orbit types, at every cardinality including infinite. By Theorem C1
> that ceiling is **attained**, and attained exactly by the spectrum.

*Proof.* Each such map is constant on orbits; a tuple of orbit-constant maps is
orbit-constant, so the family cannot separate beyond the 54 orbits. C1 exhibits
a family reaching it. ∎

**Scope, stated plainly.** The individual QG-31 probes do **not** satisfy the
hypothesis: probe `(p, aux)` fixes one swap pattern `p in S_2^3` and is
therefore position-asymmetric by construction. So this theorem says nothing
about single probes, and an earlier draft of this document over-claimed by
listing it as a constraint on QG-32's probe *set*. What it does constrain is
symmetrized summaries — and with C1 the useful statement is the sharp one:

> `bulk + spectrum` exhausts the symmetric information. Every one of the
> remaining `715 / 92` distinctions QG-32 must make is **position-asymmetric
> information**, and no amount of symmetric probing, adaptive or not, can supply
> any of it.

### What this does and does not give #911 / #918 / #920 / #924

- It explains where 54 comes from and why bulk (45) is a different kind of
  object, so the joint 92 is a quotient-plus-statistic, not two statistics.
- It says the residual separation is entirely position-asymmetric, which is why
  the indexed family is indexed.
- It does **not** predict QG-32's minimum probe count, and is silent on QG-32b's
  four-probe question and on QG-34's adaptive depth. Those are separation
  questions inside the position-asymmetric information; the ceiling only bounds
  the symmetric part.

## Reproduction

```
python3 research/extensions/orion-qg/qg28_generic_replay.py
python3 research/extensions/orion-qg/qg_symmetry_quotient_lattice.py
python3 research/extensions/orion-qg/qg_spectrum_symmetry_identification.py
```
