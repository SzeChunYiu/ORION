# Independent protected benchmark

The successor retains the interpretable world but evaluates support exactly: `Z1` supports `{PREDICT, DECIDE}`; `Z2` supports `{PREDICT, DECIDE, INTERVENE, VERIFY}`; and `Z3` supports all five responsibilities. The exact equivalence-class matrix is checked directly and matches the registered support sets.

Protected seed: `2026082113`. Families: **24**. Episodes per family: **512**. Total protected episodes: **12,288**.

Family probabilities for hidden variables `m` and `r` vary independently over `[0.65,0.95]`. Compact state is `Z1` or `Z2` with equal probability; requested responsibility is uniform over five tasks. Raw recovery is independently available with probability `0.95`. When compact state lacks a needed coordinate, an unqualified decoder uses the family MAP value, deliberately creating cases that can be high-confidence yet structurally unsupported.

## Baselines

1. `UNQUALIFIED`: always reuse compact state.
2. `CONFIDENCE_ONLY`: reuse if estimated task accuracy is at least `0.80`; otherwise reopen when possible.
3. `PROVENANCE_ONLY`: valid lineage is present, so provenance alone permits reuse.
4. `RCS`: reuse only when exact responsibility support holds; otherwise reopen if raw is recoverable, else `CANNOT_CHECK`.
5. `ALWAYS_RAW`: reopen raw state whenever possible.

Fixed resource units are `REUSE=1`, `REOPEN=6`, `CANNOT_CHECK=0.5`.

Baselines 1 and 3 are the same policy on this corpus, and the list is four
distinct policies rather than five. Every episode supplies valid lineage by
construction, so the provenance check never refuses and `PROVENANCE_ONLY`
reduces to "always reuse" — which is `UNQUALIFIED`. Their measured rates are
identical on every metric reported: unsafe reuse `0.3961588541666667`, verified
correctness `0.9248046875`, mean cost `1.0`. This follows from the construction
above rather than from anything that happened during the run, and the results
report the two together for that reason. It has one consequence worth stating
plainly: this benchmark does not test whether a provenance check helps, because
the check is never exercised. Establishing that would need episodes with absent
or broken lineage, which this corpus does not contain.