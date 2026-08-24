# Coverage-one selectivity–harm bound

Let a binary controller emit either a correct singleton or the full envelope
`{GLUE, OBSTRUCTION}` on a scorable case. Under the inherited V3 loss, a correct
singleton costs zero and the full envelope costs `u=0.25`. Coverage one excludes
wrong singletons. If `q` is the full-envelope rate, then

\[
H = u q = 0.25q.
\]

Therefore harm noninferiority to comparator harm `h` requires

\[
q \le 4h, \qquad \text{or equivalently}\qquad
1-q \ge 1-4h.
\]

This makes the V3 adverse result sharper. AML's three harms were
`0.02520057`, `0.02526842`, and `0.05647760`. A coverage-one successor would
therefore need correct proper singletons on at least `89.919772%`, `89.892634%`,
and `77.408959%` of cases, respectively. Every regime must pass, so the first
threshold is binding on the V3 census.

The only outcome-licensed V3 singleton cell available without reconstructing a
new feature search is `AML=GLUE` plus document-aware exact-label equality. It
had 361 correct scorable singletons, zero false positives, and support across 15
transformations. Its selection rate is only `0.306155%`. If all remaining cases
receive the full envelope, projected harm is `0.24923461`, still worse than AML
by `+0.22403404`, `+0.22396620`, and `+0.19275701`.

## Scientific consequence

A sparse high-precision positive certificate cannot resolve
`PUBLIC_V3_NO_HARM_SUPERIORITY`. V4 requires either a broadly applicable and
prospectively valid obstruction certificate or substantially stronger
source-native matcher evidence that safely selects almost all cases. The bound
is arithmetic under the frozen V3 loss, not a transport claim. V4 must recompute
it family by family and may not pool families to hide failure.
