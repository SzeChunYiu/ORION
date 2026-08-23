# X1-A audit correction — Freeze--Schmid parity recheck confirms original C_p^3 lower bound

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`

## Why this audit exists

During live research, an exploratory arithmetic re-read briefly suggested that the committed X1-A campaign had omitted the odd-parity `delta=1` term in Freeze--Schmid Theorem 4.1 and therefore understated the C_p^3 lower bound.

That alarm was itself caused by a parsing/arithmetic mistake. The repository campaign was already correct. This note preserves the audit trail rather than silently erasing the transient false alarm.

## Exact donor theorem

Freeze--Schmid Theorem 4.1 states, for

`G=C_n1 ⊕ ... ⊕ C_nr`, `1<n1|...|nr`,

and `s,t` satisfying `s(s-1)/2 <= r-t+1`, that

`D_k(G) >= D*(G) + s floor(n_t/2) + delta + (k-2)n_r`,

where `delta=0` if `n_t` is even and `delta=1` if `n_t` is odd.

For `G=C_p^3` with odd prime p, choose `r=3`, `s=3`, `t=1`. Then

- `D*(G)=3p-2`;
- `s floor(p/2)=3(p-1)/2`;
- `delta=1`;
- `(k-2)n_r=(k-2)p`.

Therefore

`D_k(C_p^3) >= 3p-2 + 3(p-1)/2 + 1 + (k-2)p`

`= pk + 5(p-1)/2`.

Thus the original X1-A campaign arithmetic

`freeze_schmid_lower_intercept = 5*(p-1)//2`

is correct for odd p.

## Consequences

- No campaign code correction is required.
- For p=3 the theorem gives `D_k(C_3^3)>=3k+5`; the exact donor value for k>=3 is `3k+6`, so the general lower construction is not sharp there.
- For p=5 the theorem gives `D_k(C_5^3)>=5k+10`; in particular `D_3(C_5^3)>=25`.
- The qualitative X1-A conclusion remains unchanged: ordinary k-wise Davenport induction cannot reach the ideal intercept `2p-2`, since `5(p-1)/2 > 2p-2` for every odd p>1.

## Claim boundary

This is an audit correction of our reading, not a new mathematical result. Source theorem and all lower bounds are donor-owned.
