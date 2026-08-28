# ORION-21 NR07 exact-anchor v2 — forensic theory

## Question

The registered NR07 width-law run stopped at
`CANNOT_CHECK_INSTRUMENT_DRIFT` because one replay anchor changed from
`0.94912109375` to `0.949169921875`. This successor asks only:

> Which exact atomic transcript choices can produce the two recorded
> numerators under the committed NR07 data stream and decoder score?

It does not test the width law, relax the original exact gate, or read any
ladder outcome.

## Review roles

- **Numerical proof auditor:** converts every reported accuracy into an integer
  numerator over the frozen denominator and checks uniqueness.
- **Algorithm auditor:** reconstructs the screening boundary without using the
  runtime ordering of tied features.
- **Custody auditor:** distinguishes committed parent bytes from the absent
  LUNARC experiment-runner bytes.
- **Independent transcript auditor:** checks the committed labels, predictions,
  mismatches, counts, worlds, and terminal without importing the generator or
  NumPy.

## Frozen atomic object

The anchor is cell `(14,3,3)`, seed `2026082201`, train size `64`, with five
ordered queries and 4,096 ordered test rows per query. Therefore the exact
score denominator is

`5 × 4096 = 20480`.

The recorded values are exactly:

- historical NR07: `19438 / 20480 = 0.94912109375`;
- LUNARC replay: `19439 / 20480 = 0.949169921875`.

The difference is one **net correct count**. It does not imply that only one
prediction bit changed.

## Boundary reconstruction

For each query, v2 computes integer correlation numerators

`sum_i Y_i A_ij`

over the 64 training rows. It then identifies all features equal at the
absolute-correlation value occupying the third support slot. Every admissible
support at that equality boundary is enumerated. No call to `argsort` decides
the forensic result.

Queries 1–4 each admit one support world and score `4096/4096`. Query 0 has
two features strictly above the boundary, indices `16` and `311`, and a
three-way tie at absolute correlation `24/64 = 0.375`:

| Third feature | Query-0 correct count | Aggregate numerator |
|---:|---:|---:|
| 35 | 3054 | 19438 |
| 93 | 3055 | 19439 |
| 263 | 3092 | 19476 |

Thus the historical numerator uniquely maps to support `[16,311,35]`, while
the LUNARC numerator uniquely maps to `[16,311,93]`.

The two mapped query-0 prediction vectors differ on 1,011 test rows. On those
rows, the historical vector agrees with 505 labels and the LUNARC vector with
506 labels, yielding the observed one-count net delta.

## Source-level interpretation

The committed NR07 decoder selects support with:

```python
order = np.argsort(-np.abs(c))
support = order[:r_width]
```

It declares no stable sorting kind and no feature-index secondary key.
Therefore equal absolute correlations do not define a unique scientific
support. The exact pair of recorded numerators is fully explained by two
members of that under-specified boundary tie.

This is a localization of the numerical discrepancy, not a proof of the exact
runtime mechanism. The sbatch records source commit
`86202ab577b6c3efb331fc3a2f9185911911fe98`, but the exact experiment runner
it invoked was not committed at that revision and is still absent from the
controlling evidence PR. Only a post-outcome modified copy survives in
quarantine.

## Authority

Authorized:

> The two recorded NR07 anchor numerators uniquely correspond to different
> members of one three-way feature tie at the decoder's top-r boundary. The
> committed source supplied no secondary tie key.

Not authorized:

- re-adjudicating the registered run;
- using a tolerance to pass P0;
- claiming the width law is confirmed or falsified;
- claiming byte identity with the missing LUNARC executable;
- changing the controlling `CANNOT_CHECK_INSTRUMENT_DRIFT` terminal.
