# Manuscript surface and explanation audit

## Automated surface pass

The final-mode conservative surface scanner was run on `main.tex`, every recursively included section, and both generated tables with `--final --strict`. It returned zero error-severity findings.

Review-only terms were dispositioned contextually:

- MUSE, SCOPE, SCION, LLMATCH, I-ADOPT, and DEC are cited system/framework names rather than unexplained internal run identifiers.
- ORION appears once in Methods solely to identify the implementation under test, as required by house style.
- SHA-256 identifies the standard digest algorithm in Data Availability.
- CC BY identifies the manuscript licence; the final wording uses the corresponding public licence name.
- `P3.cross-domain-atlas.v1` appears only in a non-rendered source comment needed by the structural integrity test; the comment explicitly says it is an unexecuted broader protocol and not a manuscript claim.

## Explanation sufficiency

| Reader need | Surface | Disposition |
|---|---|---|
| Why predicate-only merging can fail | Introduction | Explained through coordinate-dependent agreement |
| What the mapping rule consumes | Methods | Explicitly already-structured projections; no extraction claim |
| What an undetermined outcome means | Methods | Defined separately from negative decisions |
| Why the confirmatory result is prospective | Dataset/Evaluation | Initial result separated; holdout and terminal frozen pre-output |
| How set independence is bounded | Dataset/Limitations | Zero case-ID overlap and two repeated source records both stated |
| Why the baseline result is not system superiority | Related Work/Limitations | Flat rule named as weak registered decision comparator |
| Where the observed effect occurs | Results/Limitations | All six discriminating cases identified as polarity contrasts |
| What the null ablations mean | Results/Limitations | Retained as missing opportunity, not dispensability evidence |
| What the replay establishes | Results/Limitations | No generator-code imports, but same repository/custody |
| What remains unavailable | Data Availability | Immutable URL absence stated directly |

## Artifact-leakage audit

No issue number, pull-request number, branch, workflow run, local path, internal claim ID, machine terminal, or repository filename appears in reader-facing scientific prose. Exact digests remain in Data Availability, where they identify review materials rather than establish scientific truth.
