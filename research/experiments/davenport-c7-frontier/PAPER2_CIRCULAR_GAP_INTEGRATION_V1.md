# Paper-2 circular-gap / shared-donor integration — 2026-09-04

This additive integration preserves both concurrent descendants of shared
head `6be5e754005317f9389d677065572a0ce26743e9`:

- `22bde5131b8603858df4406d20580e5b773c1c02`: generic rank-three circular-gap
  theorem, V9 checkpoint, regression checker, and deterministic receipt.
- `c036ce05619206ef0d7d4ec9b9452d2f3bbe399e`: the parallel `a=2` shared-donor
  plane rigidity theorem, sharp one-value classification, and lower-overlap
  limitation theorem, with its checker and result.

The live branch moved to the second commit during verification of the first.
The comparison against their common parent contains only three added paths
for the shared-donor lane, disjoint from the four circular-gap paths. The
merge retains both commit histories and all seven files, without rewriting
producer branches. `FIRST_CORRIDOR_GENERALIZATION_CHECKPOINT_V9.md` records
the original circular-gap packet; this note adds the later parallel result.

## Combined mathematical frontier

The circular-gap theorem closes the whole canonical `a>=4` rank-three
support-four companion face. The historical shared-donor note's reference to
unresolved generic rank-three edges predates this integration and is
superseded by that theorem, not by its own one-value argument.

The shared-donor result materially sharpens the remaining `a=2` rank-two
work. At maximal overlap `c=H` and `p=4q+1>=13`, its exact one-value theorem
forces a high-multiplicity new value to have `y_1+y_2 != 0` in the
`(e1,e2,g)` coordinates. It excludes the whole plane `y_1+y_2=0`, not just
the two earlier standard families. It does not classify or eliminate values
outside that plane.

For lower overlap it also identifies an actual limitation of the method:
with `B_K=U s^c`, `K=c+2<=H+1`, and `y=(A,-A,1)`, `A!=0`, every nonempty
zero-sum in `B_K y^t`, `1<=t<=p-1`, has length at least `2p-K>=m`.
These are compatible partial donor extensions, not full zero-sum companion
counterexamples. They show that increasing a pure-power scan cannot settle
that lower-overlap family.

Accordingly the next joint target is a **mixed-subsequence** obstruction
using both new values. The circular-gap packet supplies attainable-height
expansion and a rank/length transfer inequality; the shared-donor packet
supplies exact capacities, a sharper plane envelope, and a proof of where
one-value arguments stop. Their combination is a research direction, not a
claim that the remaining `a=2` or `a=3` cases have already been closed.

The live all-prime equality gaps remain rank-two light types `a=1,2` and
rank-three types `a=2,3`, with the overlap and prime-specific refinements in
the respective notes. Full support-seven, `D_3(C_7^3)`, global `D_k`,
novelty/priority, and external independent review remain unclaimed.

## Verification scope

The four circular-gap files were read back from commit `22bde513` and their
Git blob hashes matched the local packet. Its checker passed with ordinary
Python and `python -O`, producing byte-identical receipts.

The concurrent shared-donor proof and its explicit limitation statement were
read for scope and consistency. Its committed numerical receipt remains that
lane's report; this integration does not claim to rerun its checker or the
full repository suite. Neither a Git merge nor a green regression substitutes
for independent mathematical review or a novelty audit.
