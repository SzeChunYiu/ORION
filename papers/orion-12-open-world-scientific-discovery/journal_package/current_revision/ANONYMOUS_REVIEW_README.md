# Source and review materials

The editable-source archive builds the manuscript in either a generic article
layout or the target journal's single-column review layout. From the extracted
`manuscript` directory, run one of:

```text
tectonic main.tex
tectonic ipm_submission.tex
```

The review-materials archive supports the bounded control-method paper on
fail-closed scientific-literature discovery. Run `python verify.py` after
extracting it. The standard-library checker recomputes the aggregate outcomes
from all 50 paired public-collection topics, runs a separate fixed-seed paired
bootstrap as a robustness replay, and checks the controlled-index and
exact-contract summaries against the included expected results.

The controlled comparison is underpowered and does not establish superiority.
The registered public external recall-and-cost gate fails: recall is lower and
reading cost is higher. A favorable top-rank result is secondary and does not
replace those criteria. The information-equivalent exact-contract comparator
ties the fail-closed controller, so that comparison isolates unresolved-route
semantics rather than inherent model expressivity.

Third-party corpora are not redistributed. Original provenance and integrity
records are maintained privately and are not reader-facing.
