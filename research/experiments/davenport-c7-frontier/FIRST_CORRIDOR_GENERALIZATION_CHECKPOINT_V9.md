# First-corridor generalization checkpoint — V9, 2026-09-04

Status: **generic rank-three canonical types a>=4 closed by a circular-gap /
attainable-height argument**. This is a local structural theorem, not the full
first-corridor support-seven theorem or an exact generalized Davenport value.

## New theorem

For every prime `p>=7`, write `H=(p-1)/2`, `m=(3p-1)/2` and

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-a^(-1)(e1+e2)`, `4<=a<=H`.

Every zero-sum companion

`V=s^c g^d x^r y^t`, `c,d,r,t>=1`, `|V|=m`,

with two distinct new values `x,y` outside `supp(U)`, forces a nonempty
zero-sum in `UV` of length less than `m`.

Proof: `SUPPORT4_RANK3_A_GE4_CIRCULAR_GAP_ELIMINATION_V1.md`.

The result removes the **entire** generic rank-three equality face. It does
not merely close the scalar-seven edge or enlarge the range of a search.
It requires no separate rank assumption on `V` beyond the displayed form.

## Why this advances the frontier differently

An exact identity converts antipodal depth on an overlap-plane height slice
to the diameter of a short modular rotation block. A small largest circular
gap makes a whole band of plane heights too shallow for any proper companion
subsequence.

The companion relation supplies a set of admissible scalar multiples. Adding
available shared occurrences expands their attained heights by an interval.
The attained set has at least `H+2` residues, while the complement of the
forbidden band has only `2ell-1<=H+1`. This cardinality contradiction avoids
choosing a separate multiplier for every multiplicity tuple.

The arithmetic cover is proved by exact full-block gaps and two/three
short rotation chains for every prime `p>=53`. A small-prime table leaves
only `(p,a)=(17,7)`, which is closed by explicit double/triple relations and
four displayed occurrence-level certificates.

This proof does not depend on the previous simultaneous-overlap sum bound,
V8 doubling reduction, central scalar-three theorem, or any unproved
classification of quotient atoms. Those results are preserved but no longer
needed to close this generic face.

The note also proves a reusable transfer inequality for other lengths and
ambient ranks: with `G_ell` the largest rotation gap, a short-free pair of
rank `R` and companion length `M` in the same two-new-value form must satisfy

`M <= max(p+(R-1)(G_ell-1), p+2ell-3)`

for each `1<=ell<=a`, under the explicitly stated capacity and nonzero-overlap
hypotheses. This is not an assertion about a global Davenport constant.

## Parallel-commit review and preservation

The parent of this packet is

`6be5e754005317f9389d677065572a0ce26743e9`.

A GitHub comparison verified it is 36 commits ahead of V8
`9229d28be5a643ff7bf30ea6213aba717c48e309`, with zero commits behind and only
additive path changes in that comparison. It includes the parallel `a=2`
fiber-envelope theorem, conditional standard-family elimination, the finite
`p=7,a=2` rank-three packet, manuscript draft, claim ledger, and reproduction
manifest. The `a=3` final branch head
`a884877ca181bfbd66c31c0baef75039392c270d` is also an ancestor of this parent
(54 commits ahead, zero behind, in the comparison).

The parallel `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md` and
`A2_MAXIMAL_OVERLAP_STANDARD_FAMILIES_EMPTY_V1.md` were read for mathematical
scope. The latter eliminates the two specified standard forms at maximal
light overlap; it does **not** prove every high-multiplicity value has one
of those forms. That classification gap is retained.

The new packet builds on the shared parent without rewriting the producer
branches or deleting prior work. Review of ancestry and selected proof notes
is not represented as a rerun of every collaborator's executable.

Historical V1 manuscript/claim-ledger surfaces remain frozen in this change.
This checkpoint supersedes their open status only for the generic rank-three
`a>=4` face. Updating those publication surfaces and their bound manifests is
separate editorial work; their old counts must not be read as the current
frontier. No submission-readiness upgrade is made here.

## Verification actually executed

`check_rank3_circular_gap_v1.py` completed successfully with ordinary Python
and with `python -O`; their deterministic output was byte-identical.
The checker uses explicit exceptions, not removable `assert` statements.

| Check | Rows |
|---|---:|
| Exact antipodal identity against raw capacity enumeration | 132492 |
| Separate occurrence-level DP against raw plane depth | 802 |
| Full-block gap formula, including coprime composite moduli | 1472 |
| Directed-chain inequality controls | 2124 |
| Rotation types through prime 1009 | 18866 |
| Scalar-set intersection and interval-growth controls | 5646 |
| Complete small-prime tables | 12 |
| All multiplicity rows at the sole rotation exception | 36 |
| Proper subsequences of a compatible p=5 control | 34 |

Six targeted mutation controls were detected. The compatible `p=5` control
lies outside the theorem's hypotheses and is deliberately accepted; the
regression does not indiscriminately declare every companion impossible.

Receipt: `RANK3_CIRCULAR_GAP_RECEIPT_V1.json`.

Transcript SHA-256:
`c3c787f6e2d6b32cfff96f6c3c764661980a10ab57750663345a4268621b20ef`.

These are finite regression checks. The proof authority is the symbolic
argument and its explicitly bounded arithmetic remainder, not the prime-1009
replay. This pass did not run the full ORION test suite or certify remote CI,
and it is not an external independent mathematical review.

## Remaining theorem frontier

Combining the new result with the previously established normal-form and
rank-two reductions, the unresolved all-prime equality mechanisms are:

1. Rank-two light type `a=1`, with remaining overlaps `c>=5`.
2. Rank-two light type `a=2`, with remaining overlaps `c>=5`; the conditional
   maximal-overlap standard-family theorem is available, not its converse.
3. Rank-three type `a=2`, outside the finite prime-specific closures.
4. Rank-three type `a=3`.

The generic rank-three `a>=4` edges from V8 are no longer on this list.
The two/three-chain proof explains the exceptional denominators: unit
steps correspond exactly to the inverse types `a=2,3` (or their reflected,
noncanonical counterparts), where the generic rotation cover breaks down.

The next structural target is therefore the exceptional small-denominator
slices: combine the attained-height expansion with the exact `a=2` fiber
envelope and an analogous graded analysis for `a=3`. Do not presume the
conditional standard-family classification, and do not restart the generic
scalar-by-scalar scan.

## Claim ceiling

- Generic rank-three `a>=4` face: proved by the accompanying argument.
- Full first-corridor support-seven theorem for every prime: still open here.
- `D_3(C_7^3)` and the candidate generalized all-prime `D_k` formula: not proved.
- Maximal atoms with larger support and the other global corridors: not closed
  by this packet.
- Novelty/priority and journal acceptance: not certified.
