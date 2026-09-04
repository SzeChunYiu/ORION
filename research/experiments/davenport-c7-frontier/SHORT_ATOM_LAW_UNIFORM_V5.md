# The short-atom bound obeys a closed law at every prime — V5

Status: **verified for every prime `5 ≤ p ≤ 23` and every length the programme uses.** Generalises the `p = 7` Proposition 4.3′ to a formula valid at all primes, and **corrects the range** stated in `SHORT_ATOM_BOUND_UNIFORM_V4.md`.
Checker: `verify_short_atom_law_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The lemma needs no packing hypothesis

> **Lemma.** Let `C` be zero-sum over `C_p^3` with `|C| = m` and suppose every atom of `C` has length `≥ w+1`. Then every proper nonempty zero-sum subsequence of `C` has length in `[w+1, m−w−1]`.

*Proof.* A proper nonempty zero-sum `B` contains an atom, so `|B| ≥ w+1`; its complement `C B^{−1}` is zero-sum and nonempty, so it contains an atom too, giving `m − |B| ≥ w+1`. ∎

No packing number appears, so the window is two-sided at every `k`. The pointed system on that window must be consistent, and infeasibility forces an atom of length `≤ w`.

## 2. The law

> **Theorem (verified range).** Let `p ≥ 5` be prime, `D = 3p−2`, and let `C` be zero-sum over `C_p^3` with `D < |C| = m ≤ (11p−3)/2` and every atom of length `≥ p+1`. Write `r = m mod p` and `h = (p−1)/2`. Then `C` has an atom of length at most
>
> `w(p,m) = (3p−1)/2`               if `r ≤ h` or `r = p−1`,
> `w(p,m) = (3p−1)/2 + r − h`       if `h+1 ≤ r ≤ p−2`.

Three things are worth naming.

1. **The generic bound is `(3p−1)/2`** — that is `⌈D/2⌉`, half the Davenport constant. So *any* long enough zero-sum sequence over `C_p^3` whose atoms all exceed `p` must carry an atom of at most half the maximum possible length. That is a statement about `C_p^3` at large, not about `D_3` obstructions.
2. **The exceptional residues are exactly `r ∈ [(p+1)/2, p−2]`**, a run of `(p−3)/2` residues, on which the bound degrades linearly to a maximum of `2p−2`.
3. **The law is periodic in `m` with period `p`**, which is what one expects from a Lucas mechanism and is the main evidence that it is a theorem rather than a coincidence of the tested range.

### Specialisations

| `p` | generic `(3p−1)/2` | exceptional residues | worst case `2p−2` |
|---|---|---|---|
| 5 | 7 | `r = 3` | 8 |
| 7 | 10 | `r = 4, 5` | 12 |
| 11 | 16 | `r = 6,…,9` | 20 |
| 13 | 19 | `r = 7,…,11` | 24 |

At `p = 7`: `m = 23,24,27,28,29` have `r = 2,3,6,0,1`, all non-exceptional, so the bound is 10; `m = 25, 26` have `r = 4, 5`, and the bounds are 11 and 12.

## 3. Correction to `SHORT_ATOM_BOUND_UNIFORM_V4.md`

That record stated Proposition 4.3′ with the hypothesis `23 ≤ |C| ≤ 29`. **That range overreached.** Only `|C| ∈ {23,24,27,28,29}` was ever verified, and by §2 the two omitted lengths genuinely fail the conclusion: at `|C| = 25` the true bound is 11, at `|C| = 26` it is 12.

**No downstream conclusion changes.** The first corridor consumes `|C| = 29, 28, 27` and the second consumes `|C| = 24, 23` — exactly the five verified lengths. Both corridor statements, `D_3(C_7^3) = 36`, and the `D_4(C_5^3)` corridor stand unchanged; the last of these never used a range claim at all, since `verify_d4_c5_corridor_v4.py` computes `w(m)` separately for each of its eighteen lengths.

The V4 record now carries the corrected statement and a pointer here.

## 4. Verification

`verify_short_atom_law_v5.py`:

1. checks the closed form against the directly computed bound for every prime in `{5,7,11,13,17,19,23}` and **every** length `m ∈ [3p−1, (11p−3)/2]` — with `w−1` shown feasible at each, so no entry is vacuous, and every sufficiently small window additionally decided by exhaustive search over all `p^{|S|}` assignments;
2. checks the generic value is `(3p−1)/2` and the maximum is `2p−2`;
3. checks the exceptional residue set is exactly `[(p+1)/2, p−2]` at every prime;
4. asserts the `p = 7` correction explicitly: the bound is 10 on `{23,24,27,28,29}` and is 11, 12 at 25, 26;
5. range control: the law continues to hold well past the applied range — the first failure is at `m = 34` for `p = 5` (against `N = 26`) and `m = 62` for `p = 7` (against `N = 37`), so the restriction `m ≤ (11p−3)/2` is comfortable rather than tight.

## Claim ceiling

Verified, not proved: this is a finite computation per prime over a finite length range, for seven primes. The periodicity in `m mod p` and the closed form make a Lucas-based proof plausible, but the degree-set minimisation reported in `GENERAL_SPECTRUM_SPECIAL_LENGTHS_V4.md` — the contradiction uses essentially every available degree — suggests it will need a rank argument rather than a short certificate. The law also fails for `m` far beyond the applied range, so any proof must carry the upper restriction on `m`.
