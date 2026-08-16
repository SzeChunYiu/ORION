# ORION journal peer-review readiness standard

**Purpose:** define a hard, journal-agnostic terminal for when an ORION flagship manuscript is ready to be sent to external peer review.

`PEER_REVIEW_READY` is a process/evidence terminal, **not a prediction of acceptance**. A paper may be scientifically strong and still be rejected for scope, taste, competition or reviewer disagreement. Conversely, local tests, a polished PDF or a novel-sounding architecture are not enough to reach this terminal.

The standard intentionally follows a high reproducibility bar: claims must be supported by empirical or theoretical analysis; code/data needed to verify the claims must be reviewable; and every result-bearing figure/table must be regenerable from archived artifacts.

## Gate 0 — paper identity and claim coherence

- [ ] Stable ORION paper ID, title and canonical manuscript path are fixed.
- [ ] One-sentence primary claim is stated without umbrella language.
- [ ] Secondary claims are enumerated and each has an evidence owner.
- [ ] Claim ownership does not overlap another flagship paper except through an explicit interface/cross-reference.
- [ ] Every term introduced by ORION is defined and justified against existing terminology.
- [ ] The abstract, introduction, methods, results and conclusion use the same claim boundary.

## Gate 1 — nearest-work / novelty closure

- [ ] Fresh literature closure is rerun within 14 days of submission.
- [ ] Search routes include exact terminology, function-only descriptions, parent disciplines, historical precursors, implementation analogues, benchmark literature and adversarial "already solved" queries.
- [ ] The five strongest nearest systems/papers are compared mechanism-by-mechanism rather than by name or prose similarity.
- [ ] Every nearest-work mechanism receives `ADOPT`, `ADAPT`, `COMPOSE`, `DEFER` or `REJECT` with evidence.
- [ ] Any idea already provided by nearest work is removed from the ORION novelty claim.
- [ ] The surviving novelty is written as a falsifiable residual hypothesis, not a priority claim such as "first autonomous scientist".
- [ ] No nearest-work route remains `OPEN` for a claim presented as novel.

## Gate 2 — manuscript completeness

A submission manuscript must contain, as applicable:

- [ ] title, author block, abstract and keywords;
- [ ] introduction with the concrete scientific problem and contribution list;
- [ ] precise task/problem definition and assumptions;
- [ ] method/system description sufficient to reimplement the claimed mechanism;
- [ ] formal definitions/algorithms where they clarify the contribution;
- [ ] experimental design, datasets/tasks, baselines, resources and frozen evaluation protocol;
- [ ] results with uncertainty/statistical analysis rather than only point estimates;
- [ ] mechanism ablations and negative controls;
- [ ] failure/error analysis, including null and harmful outcomes;
- [ ] related work organized around mechanisms and claim boundaries;
- [ ] limitations and threats to validity;
- [ ] ethics/safety/governance discussion where relevant;
- [ ] reproducibility statement;
- [ ] data availability statement;
- [ ] code/artifact availability statement;
- [ ] conclusion that does not exceed the evidence;
- [ ] appendices/supplement for prompts, configurations, annotation guides and full result tables.

## Gate 3 — prospective evaluation freeze

Before looking at test outcomes:

- [ ] primary and secondary hypotheses are frozen;
- [ ] task/dataset versions and splits are content-addressed or otherwise immutable;
- [ ] model/provider/tool versions are frozen where possible and fully logged where not;
- [ ] baseline implementations/configurations are frozen;
- [ ] resource budgets are frozen and parity rules are explicit;
- [ ] primary metrics and direction of improvement are frozen;
- [ ] exclusion/failure rules are frozen;
- [ ] statistical analysis plan is frozen;
- [ ] plot/table specifications are frozen enough to prevent post-hoc metric shopping;
- [ ] evaluator/holdout/search-access policy is frozen;
- [ ] the exact subject commit is recorded.

If a design change is required after outcome access, the old run remains immutable and the new protocol receives a new version.

## Gate 4 — empirical adequacy

- [ ] At least one strong simple baseline is included.
- [ ] Strong current nearest-work baselines are included or an explicit, defensible reason prevents execution.
- [ ] Resources are matched or the trade-off is reported transparently.
- [ ] Test examples are fresh/held out with respect to development and tuning.
- [ ] Public benchmark leakage/search-time contamination is audited when agents can browse or retrieve.
- [ ] Task families cover both cases where the proposed mechanism should help and negative controls where it should not.
- [ ] Sample size is chosen prospectively using a power/precision analysis or a justified benchmark-complete evaluation, never by stopping when significance appears.
- [ ] Multiple stochastic runs/seeds are used where randomness materially affects outcomes.
- [ ] Confidence intervals or other uncertainty intervals accompany primary estimates.
- [ ] Effect sizes and practical significance are reported, not only p-values.
- [ ] Multiple-comparison control is specified when many hypotheses/metrics are tested.
- [ ] Human adjudication uses a written rubric, blinded ordering where possible and inter-annotator agreement where labels are subjective.

## Gate 5 — mechanism identification

- [ ] Full ORION is compared with ablations that remove each claimed residual mechanism.
- [ ] Ablations are matched in compute/data/tool access.
- [ ] A positive result is not attributed to a mechanism if an ablation performs equivalently within the predeclared equivalence/non-inferiority margin.
- [ ] Failure cases are assigned to a prospective taxonomy rather than explained only after the fact.
- [ ] The paper distinguishes architectural conformance from empirical utility.

## Gate 6 — result figures and tables

Every flagship paper should have a compact evidence package. Exact figures differ by paper, but the following rules are universal:

- [ ] one figure shows the mechanism or experimental protocol, not decorative architecture;
- [ ] one main plot shows the primary outcome across matched baselines;
- [ ] one plot shows the key trade-off (cost, coverage, safety, transfer or integration) rather than a single score;
- [ ] one ablation plot/table identifies which mechanism contributes;
- [ ] one failure-analysis figure/table exposes where the method does not work;
- [ ] all uncertainty bars/intervals are defined in the caption;
- [ ] every plot/table is generated by a script from archived raw result files;
- [ ] captions state sample sizes and aggregation rules.

## Gate 7 — reproducible artifact

- [ ] exact source commit/tag is frozen;
- [ ] environment/dependency lock is included;
- [ ] a clean-machine install path is tested;
- [ ] one command or a short deterministic sequence reproduces the main analysis from available artifacts;
- [ ] raw run manifests, outputs, logs and evaluator decisions are retained;
- [ ] seeds and stochastic settings are retained;
- [ ] scripts exist for every result-bearing figure/table;
- [ ] expected runtime and hardware/resource requirements are documented;
- [ ] licenses and third-party data/model restrictions are documented;
- [ ] a permanent archival snapshot/DOI is prepared for submission/publication where possible;
- [ ] at least one independent person/session reproduces the headline tables/figures from a clean environment.

## Gate 8 — integrity and authority

- [ ] benchmark/evaluator code cannot be silently modified by the candidate being evaluated;
- [ ] holdout labels/answers are inaccessible to the candidate unless the task definition explicitly permits them;
- [ ] search-time contamination is measured when public benchmarks coexist with web access;
- [ ] post-hoc evaluator changes trigger a new evaluation version;
- [ ] negative/null/harmful results are preserved;
- [ ] `CANNOT_CHECK` remains a valid outcome when evidence or independence is insufficient;
- [ ] any human or external verification dependency is named explicitly.

## Gate 9 — submission package

- [ ] target journal is selected and scope fit is checked against recent articles.
- [ ] manuscript is converted to the journal style/template only after the scientific content is frozen.
- [ ] word/page limits, abstract limit, keyword count and supplementary-material rules are satisfied.
- [ ] cover letter states the scoped contribution and why it matters to that journal's audience.
- [ ] funding, conflicts, author contributions and acknowledgements are complete.
- [ ] data/code availability wording matches the actual artifact.
- [ ] references/DOIs/arXiv versions are checked against source metadata.
- [ ] figures are legible in print/grayscale and at journal dimensions.
- [ ] final PDF is proofread independently for claim drift, broken references and formatting errors.

## Terminal

A paper reaches:

```text
PEER_REVIEW_READY
```

only when Gates 0–9 are all `PASS`. Any empirical item that cannot yet be checked keeps the paper at `CANNOT_CHECK`; it must not be converted into a cosmetic percentage.

## External policy anchors

This standard is deliberately stricter than a minimum submission checklist. Useful high-bar references include:

- JMLR Information for Authors: https://jmlr.org/author-info.html
- Nature Machine Intelligence reporting/data/code policies: https://www.nature.com/natmachintell/editorial-policies/reporting-standards
- Nature Machine Intelligence reproducibility/reusability editorial (2026): https://www.nature.com/articles/s42256-026-01219-7
- ACM artifact evaluation principles (functional, reusable, available, reproduced): https://sigsim.acm.org/conf/pads/2026/blog/artifact-evaluation/

Venue-specific formatting is the final gate; scientific readiness must precede it.
