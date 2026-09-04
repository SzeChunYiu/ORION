# No `D_4(C_5^3)` obstruction contains a maximal atom — two of five profiles eliminated — V6

Status: **proved by complete `GL(3,5)`-orbit sweep.** Strengthens Theorem M from the support-four branch to **all** maximal atoms, and eliminates two of the five corridor profiles — including the flat one.
Checker: `verify_d4_no_maximal_atom_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem Q.** No zero-sum 5-short-free sequence of length 31 over `C_5^3` contains an atom of length `13 = D(C_5^3)`.
>
> **Corollary.** The corridor profiles `(6,6,6,13)` and `(7,7,7,10)` are **eliminated**. `D_4(C_5^3) = 31` therefore requires one of `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)`.

`(6,6,6,13)` carries a maximal atom by construction; `(7,7,7,10)` carries one by Theorem O (`D4_FLAT_PROFILE_BRIDGE_V6.md`). Both die.

## 2. Method — and why it is now cheap

A maximal atom is an extremal zero-sum-free sequence of length 12 plus its completing element. Zero-sum-freeness prunes hard: carry `Σ` = the set of **all** subsums as a 125-bit mask; adding `v` is legal exactly when `−v ∉ Σ`.

A length-13 atom must span rank three — inside a plane the zero-sum-free part would have length `12 > D(C_5^2) − 1 = 8` — so it contains three independent elements, which `GL(3,5)` sends to `e_1,e_2,e_3`. Enumerating atoms that contain `e_1,e_2,e_3` is therefore complete up to `GL`.

| step | measured |
|---|---|
| maximal atoms containing `e_1,e_2,e_3` | **6,315,607** |
| reduced to `GL(3,5)` orbits | **3,325** |
| canonicalisation time | 557 s |
| exhaustive extension of each representative to length 31 | 3,325 reps, 284,529,220 nodes, **199 s** |
| **zero-sum length-31 completions found** | **0** |

Canonical form: the lexicographic minimum, over every ordered independent triple drawn from the atom's *support*, of the sorted image under the map sending that triple to `(e_1,e_2,e_3)`. Using the support rather than the 13 positions cuts the triples from `≤ 1716` to about `|supp|^3`.

Testing one representative per orbit suffices: if `T` is a zero-sum 5-short-free length-31 sequence containing an atom `A`, then `g(T)` is one containing `g(A)` for any `g ∈ GL(3,5)`, so the property is orbit-invariant.

## 3. What changed, and how fast

`FLAT_TRIPLE_INFEASIBILITY_MEASURED_V6.md` measured the enumeration route as infeasible from a *short* atom (`> 3 × 10^8` nodes for one 6-atom) and concluded a different method was needed. `D4_MAXIMAL_SWEEP_FEASIBLE_V6.md` then measured the *long*-atom route at 114 hours raw and predicted `≈ 3,700` orbits. The orbit count came out at **3,325**, and the sweep took **199 seconds**.

So the correction to record is this: the obstacle was never the mathematics of long atoms, it was running the sweep on 6.3 million redundant copies. Deduplication turned 114 hours into three minutes.

## 4. Where `D_4(C_5^3)` stands

| profile | status |
|---|---|
| `(6,6,6,13)` | **eliminated** (Theorem Q) |
| `(7,7,7,10)` | **eliminated** (Theorem O + Theorem Q) |
| `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)` | open — no part reaches `D = 13`, and each contains a 6, so the spectrum congruence is exhausted on them (`D4_FLAT_PROFILE_BRIDGE_V6.md` §4) |

`D_4(C_5^3)` remains **open**, but the surviving branch is three profiles rather than five, and all three are genuinely flat. The natural next step is the same sweep run from the *longest* part of each: 12-atoms, 11-atoms, 10-atoms. Those are not maximal, so the zero-sum-free pruning is weaker and the orbit counts will be larger — the cost is unmeasured.

## Claim ceiling

Theorem Q is exhaustive within the stated frame and rests on the completeness of the orbit enumeration (§2), not on any classification result — it supersedes the support-four restriction of Theorem M rather than depending on it. It does not decide `D_4(C_5^3)`, and says nothing about the three surviving profiles.
