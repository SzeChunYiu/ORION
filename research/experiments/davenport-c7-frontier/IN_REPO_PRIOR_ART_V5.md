# In-repo prior-art subtraction for the V4/V5 claims — V5

Status: **subtraction pass complete for the repository; external literature NOT assessed** (the host is network-blocked — `arxiv.org:443` returns a 403 policy denial at the proxy gateway, tested directly this session). This clears the half of the prior-art gate that is doable here.
Lane: `claude/orion-research-frontier-3ck9yt`.

`PRIOR_WORK_RECONCILIATION_V3.md` §4 mandates that in-repo subtraction come **first**, after four earlier claims turned out to duplicate in-repository work. This is that pass for everything new in V4 and V5.

## 1. Result

| New claim | In-repo prior art found | Verdict |
|---|---|---|
| Theorem G — pointed infeasibility is a base-`p` digit criterion (Fredholm + Newton + Lucas) | none. No occurrence of Newton/forward-difference duality, Fredholm alternative, or a digit criterion anywhere in `research/`, `development/` or `papers/` outside this lane's own files | **new in-repo** |
| Closed-form short-atom law, generic `(3p−1)/2` | none as a short-atom bound. See §2 for a numerical coincidence | **new in-repo** |
| Three special atom lengths `3(p−1)/2`, `2p`, `(5p−3)/2` | the individual values `2p` and `(5p−3)/2` appear in `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md` as the two residue classes that escape the interval `I`; that is the same Lucas mechanism, in the `D_2` proof rather than the `D_3` spectrum. See also §2 | **new as a spectrum statement; mechanism is not new** |
| Four-atom corridor for the `D_4(C_5^3) = 31` branch | see §3 — an ORION-04 gate **requests** exactly this and records it as not supplied | **new, and fills a declared-open gate** |
| Lemma E — the two-sided window needs no packing hypothesis | none | **new in-repo** |

No claim is withdrawn as a result of this pass.

## 2. Two numerical coincidences, recorded not claimed

Both are the same closed form appearing for a *different* quantity elsewhere in the repository. Neither is a duplication; both are worth a reader's attention, and a referee would spot them.

1. **`(3p−1)/2`** is my generic short-atom bound, and is also `M(3,p)`, the rank-three cube capacity in `PAPER_DRAFT_D2_RANK_V1.md` §5, where `D_2(C_p^3)`'s excess over `D + exp(G)` is read as `M(3,p) − p = (p−1)/2` via the triangle's fractional matching number `ν* = 3/2`.
2. **`(5p−3)/2`** is one of my three special atom lengths, and is also `K_p`, the finite-first-failure cap of `FINITE_FIRST_FAILURE_REDUCTION_V1.md` for `p ≥ 11`.

I have no argument that either coincidence is structural, and I do not claim one. They are flagged because a common origin — everything here is Lucas behaviour of `C(·,·)` at arguments built from `N = (11p−3)/2` — is plausible and would be worth someone's time.

## 3. The `D_4(C_5^3)` corridor fills a declared-open ORION-04 gate

`research/orion-rg/wave3/orion04-support11-13-v1/CLAIM_DISPOSITION.md`, under **Explicitly withheld**:

> *"The global saturation-atom/four-atom factorization requested by the top ORION-04 gate is not supplied."*

`D4_C5_FOUR_ATOM_CORRIDOR_V4.md` supplies a four-atom factorization structure for exactly that object — the length-31 total-zero 5-short-free sequence over `C_5^3` — reducing it to five length profiles. So this is not duplication; it answers a request the repository records as outstanding. (Whether it is *the* factorization that gate wanted is for the ORION-04 owners to say; I claim only that a four-atom length classification now exists.)

Two neighbouring in-repo results **combine** with it rather than compete:

- the same packet proves any such obstruction has **support ≥ 14** (supports 11, 12, 13 are UNSAT in two exact state representations) and multiplicities in `{1,2,4}`;
- `research/orion-rg/promotion/orion04-global-certified-search-v1/` carries a **pseudo-Boolean encoding** of the exact length-31 problem — `GL(3,5)`-fixed support basis, multiplicities in `{0,1,2,4}`, length 31, sum zero, support `≥ 14`, all short zero-sums forbidden — whose only positive terminals are a checked UNSAT proof or an explicit witness.

**Actionable:** the five corridor profiles are expressible as constraints in that encoding (each says the 31 terms partition into four zero-sum blocks of prescribed sizes), so they can be added to the existing generator to cut its search space. That is the concrete way this lane's result feeds the ORION-04 lane, and it is offered to that lane rather than executed here.

## 4. Method note

Searched `research/`, `development/`, `papers/` (excluding `papers/skills/`) for: Newton / forward-difference / finite-difference / Fredholm / dual certificate; the closed forms `(3p−1)/2`, `(5p−3)/2`, `3(p−1)/2`; four-atom and length-31 atom structure; digit criteria and digit domination. Hits were read, not counted.

## Claim ceiling

This is a **repository** subtraction only. It says nothing about the published literature, and no priority claim follows from it. The external pass remains a submission gate and cannot be run from this host.
