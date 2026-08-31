# Papers that declare their own submission status

Two papers state their status inside the artifact rather than leaving it to be inferred. Where they do, that statement is authoritative and overrides any completeness-based judgement.

| paper | where | what it says |
|---|---|---|
| ORION-22 | `check_p12_lifecycle_integration_v4.py` | `top_tier_submission_allowed: false`, **enforced** --- the checker fails if the flag is flipped |
| ORION-01 | V3 rendered front matter | `Status: candidate successor to the frozen V2 text; no external review or submission authority claimed` |

Both were found by accident while looking for something else: ORION-22's while running checkers, ORION-01's while chasing a banner. Neither would have surfaced from a packaging audit, because both papers look reasonably complete.

## ORION-16 is a different case

A first-page sweep also returns ORION-16, whose front matter reads `Working framework draft`. That is a **placeholder author**, not a status declaration --- the paper does not say it is unready, it simply never had its author block filled. It is freeze-blocked and already recorded.

## The sweep is not complete, and here is why

The sweep selects one PDF per paper with `find -name 'main.pdf' -o -name 'manuscript.pdf' -o -name '*MANUSCRIPT_V3.pdf' | head -1`. For ORION-01 that returns `journal_package_A/main.pdf` --- the **superseded V2 artifact** --- so the V3 disclaimer was missed, and only a direct check on the V3 path found it.

Any paper with multiple generations can be misread the same way. The result above should be read as *at least these two*, not *exactly these two*. Fixing it properly requires knowing which artifact is current for each paper, which is not recorded anywhere machine-readable.

## Why this matters more than the count

A packaging audit measures what a paper has. It cannot measure whether the paper is permitted to be submitted. Two papers here answer that question themselves, in opposite registers --- one in enforced code, one in rendered prose --- and both answers are negative. Neither is moved by adding a cover letter or a reference.
