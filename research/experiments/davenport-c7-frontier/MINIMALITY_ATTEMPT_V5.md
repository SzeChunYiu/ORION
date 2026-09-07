# Sharpness of Theorem J: one lemma gained, the proof not closed — V5

Status: **negative/partial record.** A lemma that retroactively validates Theorems I and J is proved; the attempted proof of *sharpness* (that the three special pairs are the only minimal forced sets) **failed**, and the specific reason is recorded so the attempt is not repeated blindly.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Lemma K (proved) — the parametrisation used by Theorems I and J is the right one

> **Lemma K.** None of the special lengths `a = p+h`, `b = 2p`, `c = 2p+h`, and none of their complements `N−a = 4p`, `N−b = 3p+h`, `N−c = 3p`, lies in the overlap range `[N−D, D] = [2p+h+2, 3p−2]`.

*Proof.* `a, b, c < 2p+h+2` and `N−a, N−b, N−c > 3p−2`, each by inspection: `p+h < 2p+h+2`; `2p < 2p+h+2`; `2p+h < 2p+h+2`; `4p > 3p−2`; `3p+h > 3p−2`; `3p > 3p−2`. ∎ (Checked for all 76 primes `5 ≤ p ≤ 397`.)

**Why it matters.** The `X_L` columns of the spectrum system are present exactly for `L ∈ [N−D,D]` with `L ∉ Z` and `N−L ∉ Z`. Lemma K says that when `Z` consists of special lengths, **no `X_L` column is dropped**. So the condition "`P` vanishes on the whole interval `[N−D,D]`" — which the Newton parametrisation behind `SUPP_Q_PROVED_V5.md` and `OBSERVATION_D_EXISTENCE_PROVED_V5.md` builds in from the start — is exactly correct there, not an extra assumption. Those two theorems are unaffected; this closes a gap in their setup that had been implicit.

## 2. A structural fact

With `P` ranging over the parametrised space (degree `≤ A`, vanishing on `[N−D,D]`) and no atom-range conditions imposed, the achievable values of `Q` on the six involution-pair representatives `0, p, 2p, 3p, 4p, 5p` form a space of dimension exactly **3** (out of 6), for every prime tested (`p = 11 … 29`).

## 3. The attempt, and why it failed

The plan was: since the achievable space is 3-dimensional and the relevant conditions are `Q(x) = 0` for `x ∈ {a,b,c} \ Z`, sharpness should be a dimension count. Writing `Q(0) = αQ(a) + βQ(b) + γQ(c)` on that space:

- `|{a,b,c} \ Z| = 1` must leave `Q(0) ≢ 0` (a dual exists — Theorem J);
- `|{a,b,c} \ Z| = 2` must force `Q(0) = 0` (no dual — sharpness).

The second requirement, applied to each of the three choices of two, forces `α = β = γ = 0`, i.e. `Q(0) ≡ 0` — which contradicts the first. So the model is **wrong**, and the computation confirms the premise it rests on is false: `Q(a), Q(b), Q(c)` are *independent* functionals on the 3-dimensional space (no relation exists), where the model needed exactly one relation.

**The missing ingredient is the `X_L` columns.** Lemma K guarantees they are untouched for special `Z`, but sharpness quantifies over **non-special** `Z` too, and a non-special `z` can lie in `[N−D,D]` — that range is a sub-interval of the atom range. For such `z` an `X` column *is* dropped, so the space of admissible `P` is strictly larger than the fixed parametrised one, and the "fixed 3-dimensional space with varying conditions" picture does not apply. Any correct argument must let the ambient space move with `Z`.

## 4. What is and is not known about sharpness

Verified (`verify_general_spectrum_v4.py`, and the scan here for `p = 11,13,17`): no single length is forced; no pair meeting a non-special length is forced — 187, 273 and 493 such pairs respectively, none forced. Also observed: for every non-special single `z`, **every** dual direction is supported in `S`, which is what makes the relaxation at `z` vacuous. That observation is the likely core of a correct proof, but it is not proved, and it is exactly the step that needs the moving ambient space.

Sharpness therefore remains **verified for `11 ≤ p ≤ 19`, not proved**. Nothing downstream uses it: the consequence the programme needs — every obstruction carries atoms of at least two of the three special lengths — is Theorem J, which is proved for all primes.

## Claim ceiling

Lemma K is proved for all `p ≥ 5`. The dimension-3 fact is verified, not proved, and is recorded as an observation. The sharpness proof is **not** obtained; §3 records the failed route and its precise defect so it is not retried unchanged.
