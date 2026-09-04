# Extending the orbit sweep to non-maximal atoms — status and a correctness guard — V6

Status: **tool generalised and revalidated; `L = 12` run in progress, result not yet available.** No new theorem claimed here.
Tool: `tools/sweep_atoms_by_length_c5_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. What was done

Theorem Q (`D4_NO_MAXIMAL_ATOM_V6.md`) eliminated the two corridor profiles carrying a maximal atom by sweeping all 3,325 `GL(3,5)` orbits of length-13 atoms. The three surviving profiles — `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)` — have longest parts 12, 11, 10, so the same sweep run at those lengths would decide them in turn.

The tool is now parameterised by atom length. The rank argument still holds at each: an atom of length `L` has a zero-sum-free part of length `L−1`, and `L−1 > D(C_5^2) − 1 = 8` for every `L ≥ 10`, so the atom spans rank three and the `e_1,e_2,e_3` normalisation is complete up to `GL(3,5)`.

**Revalidation.** Run at `L = 13` the generalised tool reproduces Theorem Q exactly — 6,315,607 atoms, **3,325 orbits**, 284,529,220 sweep nodes, **0** completions — so the parameterisation did not disturb the settled case.

## 2. A correctness guard that must be checked before trusting any run

The representative array is capped at 400,000 entries and the collection loop is

    if (nreps < 400000) memcpy(reps[nreps++], c, 16);

so if a length has **more** orbits than that, representatives are silently dropped and the sweep is **not exhaustive**. At `L = 13` the count was 3,325, far under the cap, which is why Theorem Q is safe.

Shorter atoms are less constrained and will have many more orbits. **Any future run must compare the reported orbit count against 400,000 before its "0 completions" is read as a theorem.** If the count reaches the cap, the run proves nothing and the array must be enlarged.

This is recorded now, before the `L = 12` result exists, precisely so the check is not skipped once a tempting number appears.

## 3. Current run

`L = 12` has been running for roughly 40 minutes without completing. At `L = 13` the enumeration and canonicalisation took 557 s for 6.3 million atoms; length-12 atoms are strictly more numerous, so a runtime several times larger is expected. No result is claimed.

## Claim ceiling

Nothing here is a new mathematical result. The tool is revalidated at `L = 13` only. The `L = 12`, `11`, `10` sweeps are unrun or incomplete, and their results — if and when they land — are subject to the orbit-count guard in §2.
