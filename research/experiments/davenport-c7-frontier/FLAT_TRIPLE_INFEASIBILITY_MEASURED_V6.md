# The flat-triple gap is a method gap, not a compute gap — measured — V6

Status: **measured negative.** The enumeration that closed the maximal-atom branch (`Theorem M`) does **not** scale to short atoms, by a measured factor of `>10^3` per atom. Recording the numbers so the programme does not spend compute on a method that cannot finish.
Probe: `tools/probe_flat_extension_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Why the question arose

`COMBINED_COMPLETION_MAP_V6.md` identified the single blocking gap for both open problems as **elimination for flat triples** — atom triples with no maximal part. `D4_C5_SUPPORT4_MAXIMAL_CLOSURE_V6.md` then closed the one `D_4(C_5^3)` profile that *does* carry a maximal atom, by exhaustively enumerating 5-short-free length-31 multisets containing a fixed 13-atom.

That method never used maximality — only that the atom is **fixed**. So the obvious next step was to run it from a short atom instead, since every one of the five profiles has minimum part 6 or 7, and every obstruction therefore contains an atom of length 6 or 7. Enumerating those is cheap: after normalising an independent triple to `e_1,e_2,e_3`, there are only **2,187** rank-three length-6 atoms.

## 2. The measurement

| starting atom | elements it forbids | further elements needed | candidates | search |
|---|---|---|---|---|
| maximal, length 13, `a=1` | 50 of 124 | 18 | 74 | **complete**, 135 length-31 extensions |
| maximal, length 13, `a=2` | 60 of 124 | 18 | 64 | **complete**, 192 length-31 extensions |
| length 6 (sample) | 24 of 124 | 25 | 100 | **incomplete after 3·10⁸ nodes / 223 s** |

The short-atom search was capped at `3 × 10^8` nodes and aborted; at that point it had found 189 length-31 extensions (none zero-sum), so it was still deep in the tree rather than nearly done.

## 3. What this implies

A length-13 atom forbids half the group and leaves only 18 slots; a length-6 atom forbids a fifth and leaves 25. The branching factor and the depth both move the wrong way, and the product is brutal: **one** 6-atom already exceeds `3 × 10^8` nodes, and there are 2,187 of them (rank three alone, before the rank-two family and before length 7). A conservative lower bound on the full sweep is `>10^{11}` nodes — hundreds of core-hours, for a single profile at a single prime.

So the flat-triple gap is **not** a compute gap that a bigger machine closes. It is a method gap. This also explains, retrospectively, why lane A's programme is built around maximal atoms: that is precisely where the enumeration is tractable, because a maximal atom is a strong enough constraint to make the completion search finite in practice.

## 4. What a workable method would need

Any approach to flat triples must supply constraint strength that a short atom does not. Three directions, none attempted here:

1. **Work from the longest part, not the shortest.** Every profile has a longest part `≥ 10`; a length-10, 11 or 12 atom constrains far more than a length-6 one. The cost moves to classifying those atoms up to `GL(3,5)`, which is the harder half of lane A's work but is at least the right shape.
2. **Pair constraints rather than single atoms.** Lane A's maximal-pair machinery gets its strength from fixing two atoms at once; the analogue for flat profiles would fix, say, the two longest parts.
3. **A congruence attack.** The pointed/spectrum machinery of this lane is prime-uniform and indifferent to whether a part is maximal; whether it can separate flat profiles is untested.

## Claim ceiling

This is a measurement on one host with one implementation, not a proof that flat-triple elimination is intractable. A better encoding — the ORION-04 lane's pseudo-Boolean route with a solver, for instance — could change the constant. What the numbers do establish is that the *specific* method that closed the maximal-atom branch is off by orders of magnitude for short atoms, so reusing it unchanged is not a plan.
