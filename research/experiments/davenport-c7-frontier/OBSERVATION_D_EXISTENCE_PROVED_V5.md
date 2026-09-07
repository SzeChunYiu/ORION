# The forcing half of Observation D, proved for every prime — V5

Status: **proved.** The useful direction of Observation D — *every obstruction has atoms of at least two of the three special lengths* — is now a theorem for all primes `p ≥ 5`, not a verified range. Only the sharpness (minimality) part remains verified-only.
Checker: `verify_existence_proved_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem J.** Let `p ≥ 5` be prime, `h = (p−3)/2`, and let `a = 3(p−1)/2 = p+h`, `b = 2p`, `c = (5p−3)/2 = 2p+h` be the three special lengths. For each of the three pairs `Z ⊆ {a,b,c}` the atom-spectrum system with `Z` excluded is inconsistent. Hence **every `D_3(C_p^3)` obstruction has atoms of at least two of `a`, `b`, `c`.**

## 2. The construction

Take the ansatz `F_2 = 0`, so that `G_j = F_0 + jF_1` is **linear** in `j` (not merely quadratic), and let `F_0, F_1` be supported on the two residues `{0, h}`. Then `P(jp+t) = F_0(t) + jF_1(t)`. With `s = (−1)^N` and `δ_t` the indicator of a residue, the following coefficients — **integers in `s`, with no dependence on `p`** — give a dual:

| | `F_0` | `F_1` |
|---|---|---|
| `Z = {b,c}` | `(−4−4s)δ_0 + (−4−4s)δ_h` | `(1+2s)δ_0 + (4s)δ_h` |
| `Z = {a,c}` | `(−4−4s)δ_0 + (−4−4s)δ_h` | `(−2+s)δ_0 + (2+4s)δ_h` |
| `Z = {a,b}` | `(−4−4s)δ_0 + (−4−4s)δ_h` | `(2s)δ_0 + (1+4s)δ_h` |

Degree: `F_2 = 0` kills the `d_1 = 2` block, so `d ≤ p + (p−1) = 2p−1 ≤ A = 2p+h+2`. The ansatz is admissible.

## 3. Why the verification is finite, hence uniform in `p`

`Q(jp+t)` involves `G_j(t)` together with `G_{5−j}(h−t)` (for `t ≤ h`) or `G_{4−j}(p+h−t)` (for `t > h`). Since `F_0, F_1` vanish off `{0,h}`, a condition is nontrivial only if `t ∈ {0,h}` **or** the partner argument is. For `t ≤ h`, `h−t ∈ {0,h}` exactly when `t ∈ {h,0}`; for `t > h`, `p+h−t ∈ {0,h}` would need `t = p` or `t = p+h`, neither a residue. So the only nontrivial conditions live at

`p` (not in the atom range), `p+h = a`, `2p = b`, `2p+h = c`.

And `P = 0` on the overlap interval `[A,D]` is automatic: that interval is `j = 2` with `t ∈ [h+2, p−2]`, which contains neither `0` nor `h`.

So the whole check is a **fixed finite set of identities in `s`** (with `s² = 1`), independent of `p`.

## 4. The one delicate point

`Q(0) = F_0(0) + s[F_0(h) + 5F_1(h)]` evaluates to a fixed integer per branch:

| `Z` | `s = +1` | `s = −1` |
|---|---|---|
| `{b,c}` | `4` | `20` |
| `{a,c}` | `14` | `10` |
| `{a,b}` | `9` | `15` |

Several of these are divisible by a small prime — `20` by `5`, `14` by `7`, `10` by `5`, `15` by `5`. The construction survives because of a parity fact: `N = (11p−3)/2` is even exactly when `p ≡ 1 (mod 4)`, so

`s = +1 ⟺ p ≡ 1 (mod 4)`.

The `s = −1` branches therefore only ever occur for `p ≡ 3 (mod 4)`, and `5 ≡ 1`, `7 ≡ 3`. So `Q(0) = 20` is never evaluated at `p = 5`, `Q(0) = 14` never at `p = 7`, and so on. The checker asserts this directly: for each branch it lists the primes in the relevant residue class dividing that value, and the list is empty in all six cases.

This is exactly the kind of interaction that a per-prime computation would hide, and it is the reason the theorem needs the parity observation rather than just an ansatz.

## 5. Status of Observation D now

| part | status |
|---|---|
| unrestricted system consistent | verified `p ≤ 31` |
| **forcing**: each special pair is forced | **PROVED, all primes** (Theorem J) |
| **structure**: any dual has `supp Q ⊆ S` | **PROVED, all primes** (`SUPP_Q_PROVED_V5.md`) |
| **minimality**: no other pair or single length is forced | verified `p ≤ 19`, **not proved** |

The consequence the programme actually uses — *every obstruction carries atoms of at least two of the three special lengths* — follows from the forcing part alone, so **it now holds for every prime**. Minimality is a sharpness statement: it says the three pairs are the *only* minimal forced sets, and nothing downstream depends on it.

## Claim ceiling

Theorem J is proved for all primes `p ≥ 5`. It does not establish minimality, and it does not by itself decide `D_3(C_p^3)` for any `p > 7` — the corridors still have to be closed. The `p = 7` chain is unaffected: it used the richer `p = 7` forced family, of which the special pairs are a part.
