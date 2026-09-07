# The `p = 5` bridge does not generalise — and a constraint that does — V6

Status: **negative result, plus a positive by-product.** The lead recorded in `D4_FLAT_PROFILE_BRIDGE_V6.md` §4 — that flat `D_3(C_p^3)` rows at `p ≥ 11` might likewise be forced to contain a maximal atom — is **false**. Tested and refuted. The same computation yields a constraint that does hold at every prime.
Checker: `verify_d3_bridge_negative_v6.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The lead, and its refutation

At `p = 5` the congruence forced the flat profile `(7,7,7,10)` to carry a maximal atom (Theorem O), which put it back inside the reach of maximal-atom methods. The obvious hope was that the `b`- and `c`-rows of the special-length corridor — which contain no maximal triple at any prime — behave the same way.

They do not.

| `p` | `D` | corridor triples | flat (no maximal part) | is `D` forced outright? | flat triples forcing `D` |
|---|---|---|---|---|---|
| 7 | 19 | 8 | 7 | no | **0 of 7** |
| 11 | 31 | 14 | 13 | no | **0 of 13** |
| 13 | 37 | 17 | 16 | no | **0 of 16** |
| 17 | 49 | 23 | 22 | no | **0 of 22** |

Excluding `D` alone leaves the spectrum system consistent at every prime tested, so no maximal atom is forced; and no flat triple forces one either.

**Why `p = 5` was different.** There the forced structure was exceptionally rigid — `N_6 = 0` forces `N_x ≠ 0` for *every* `x ∈ [7,24]`, so a profile avoiding the minimum length inherits all the others, maximal length included. At `p ≥ 11` the forced sets are only the three special pairs (`GENERAL_SPECTRUM_SPECIAL_LENGTHS_V4.md`), which is far weaker and never reaches `D`. The `p = 5` bridge is a small-prime accident, of the same family as the richer forced spectra at `p = 5, 7` noted throughout this packet.

## 2. The by-product, which does generalise

> **Proposition P (verified for `p = 7, 11, 13, 17`).** For **every** flat triple of the special-length corridor, the spectrum system with the atom lengths confined to that triple's three parts is **inconsistent**.

So no obstruction has its atom lengths confined to a single flat corridor triple: it must carry at least a fourth distinct atom length. That is a genuine constraint at every prime tested — 7 of 7, 13 of 13, 16 of 16, 22 of 22 flat triples — and it says the corridor triples are not self-consistent spectra, only factorization patterns.

It does not say which extra length appears, and in particular not `D` (§1).

## 3. Consequence for the completion map

`COMBINED_COMPLETION_MAP_V6.md` §4 named flat-triple elimination as the single blocking gap. This record narrows how it can be attacked:

- **not** by forcing a maximal atom (§1 refutes that route at every prime `≥ 7`);
- but every flat triple does require a fourth atom length (§2), so the right object is not a triple but a triple-plus-extra, and the elimination should quantify over that larger, still-finite, structure.

The two remaining directions of `FLAT_TRIPLE_INFEASIBILITY_MEASURED_V6.md` §4 — working from the longest part, and fixing two atoms at once — are untouched by this and remain open.

## Claim ceiling

§1 is a refutation over the primes tested, and it refutes a *hope*, not a theorem — nothing previously claimed depended on it. §2 is verified for four primes, not proved. Neither decides `D_3(C_p^3)` for any `p > 7`.
