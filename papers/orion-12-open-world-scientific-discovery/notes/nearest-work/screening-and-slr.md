# Detail — screening, SLR automation and stopping

Families 5-8 of [`../NEAREST_WORK_AUDIT_2026-08.md`](../NEAREST_WORK_AUDIT_2026-08.md).
Every number is reported by the cited source. Raw metadata:
`../../evidence/literature/<key>.json`.

---

## 5. MetaSyn — `metasyn2026`

**Primary because** it is the only anchor that separates retrieval recall from
eligibility/screening recall against expert-curated inclusion decisions, which
is what makes "retrieval ceiling does not imply inclusion recall" testable
rather than asserted.

**Measures:** meta-analysis reproduction under a PI/ECO protocol — "422
expert-curated meta-analyses manually selected from more than 34,000 published
articles in Nature Portfolio journals", with "research questions and structured
eligibility criteria, the studies included by original reviewers, and a shared
PubMed-anchored corpus containing both eligible studies and plausible ineligible
distractors" `metasyn2026`. Evaluation is stage-wise.

**Does not measure:** open-world discovery. The corpus is PubMed-anchored and
shared, so route availability and cross-backend independence are out of scope by
construction. A system cannot be penalised here for a route that does not exist.

**Reported performance:** "experiments on multiple LLMs and baseline methods
show existing AI systems are far from perfect"; the authors "conducted a
stage-wise evaluation analysis to shed light on why existing AI systems fall
short on meta-analysis" `metasyn2026`. The abstract reports no single headline
scalar, so no scalar is quoted here.

**ORION delta under test:** does question-conditioned read state change screening
outcomes when the eligibility criteria change but the candidate set does not —
i.e. are re-reads that a seen/unseen bit would suppress actually necessary? Open
question.

---

## 6. AgentSLR / protocol-driven SLR automation — `agentslr2026`

**Primary because** it is the strongest currently-runnable end-to-end
systematic-review automation baseline, and it settles that end-to-end SLR
automation is an occupied field rather than an ORION contribution.

**Naming note:** AgentSLR is the harness introduced inside arXiv:2603.22327, not
a separately titled paper — see §1 of the core audit for the citation defect
this resolved.

**Measures:** each SLR stage as a separate unit with dedicated metrics — "a
large-scale evaluation harness comprising an SLR automation workflow and an
expert annotated dataset covering 16,248 articles", with reference annotations
"derived from peer-reviewed studies on WHO priority pathogens and produced by
domain experts" `agentslr2026`.

**Does not measure:** search-route governance. The dataset is fixed and
epidemiology-specific; provider independence, transport failure and route
starvation cannot appear.

**Reported performance:** across five frontier reasoning models, "no single model
dominated across all tasks, showing sub-task specialisation often hidden by
aggregate benchmarks". "Structured data extraction is a major bottleneck, with
no model exceeding an average field-level F1 of 0.67." Costs "vary substantially,
by up to 96 times across evaluated models", and documented failure modes
"suggest that the evaluated models are not yet reliable enough for unsupervised
deployment" `agentslr2026`.

**Absorbed:** stage-local metrics over aggregate scores; end-to-end SLR
automation is not a novelty claim available to Paper II.

**ORION delta under test:** does route governance change anything upstream of
the extraction bottleneck AgentSLR identifies, or is the bottleneck downstream
of discovery entirely? Open question — and a negative here is informative.

---

## 7. Active screening / technology-assisted review / necessary re-reads — `cormack2014tarprotocols`, `cormack2015autonomycal`, `wallace2010semiautomated`, `vandeschoot2021asreview`

**Primary because** continuous active learning (CAL) is the standard against
which any "we avoided redundant processing" claim must be stated; it is the
parent of ORION's read-ledger mechanic.

**Measures:** how much of a collection must be reviewed before substantially all
relevant documents are found. The 2015 follow-up characterises the 2014 method
as one "in which documents from the collection are retrieved and reviewed, using
relevance feedback, until substantially all relevant documents have been
reviewed" `cormack2015autonomycal`.

**Does not measure:** whether a document already reviewed under one question
must be reviewed again under a different question, extraction schema or content
version. TAR state is a per-review seen/relevance bit; it has no notion of a
*changed question*. This is the precise gap ORION's `P2.D2` addresses.

**Reported performance:** the 2015 work eliminates "topic-specific and
dataset-specific tuning parameters" so that the only user input is "a short
query, topic description, or single relevant document" plus ongoing relevance
assessments, and reports "consistently ... superior results" over the 2014 CAL
version and other methods "not only on average, but on the vast majority of
topics" across four separate sets of tasks `cormack2015autonomycal`. ASReview
reports by simulation that "active learning can yield far more efficient
reviewing than manual reviewing while providing high quality", against
"extremely imbalanced data: only a fraction of the screened studies is relevant"
`vandeschoot2021asreview`.

**Unfetched dimension:** no reported scalar is quoted for
`cormack2014tarprotocols` or `wallace2010semiautomated` — Crossref carries no
abstract for either DOI and no full text was fetched. Their titles, authors,
venues and DOIs are verified.

**ORION delta under test:** does conditioning read state on question, extraction
schema and content version preserve legitimate re-reads while still suppressing
duplicate processing — or do the two objectives trade off? Open question.

---

## 8. Systematic-review stopping — `callaghan2020stopping`, `li2020whentostop`, `yang2021heuristicstopping`

**Primary because** this literature already solves *one* stopping problem
rigorously, which sharpens what is left: it stops a single screening process
against a recall target, not a multi-route task with untried routes outstanding.

**Measures:** when to stop showing documents to a reviewer, and with what
guarantee. Callaghan and Müller-Hansen frame it as "rejecting a hypothesis of
having missed a given recall target with a given level of confidence"
`callaghan2020stopping`. Li and Kanoulas frame it as jointly ranking and
estimating "the total number of relevant documents in the collection", proving
"the unbiasedness of the proposed estimators under a with-replacement sampling
design" `li2020whentostop`.

**Does not measure:** task-level scientific closure across heterogeneous routes.
The collection is given and single; there is no notion of a route that is
unavailable, censored, or never attempted. Stopping the screening of a
collection is not the same act as declaring a research question searched.

**Reported performance:** flexible statistical stopping criteria "achieve a
reliable level of recall, while still providing work reductions of on average
17%", and "other methods proposed previously are shown to provide inconsistent
recall and work reductions across datasets" `callaghan2020stopping`. Li and
Kanoulas report their approach "effectively retrieves relevant documents; but it
also provides a transparent, accurate, and effective stopping point", and
criticise prior work that "provides an ad-hoc stopping point, without indicating
how many relevant documents are still not found" `li2020whentostop`. No scalar
is quoted for `yang2021heuristicstopping` — Crossref carries no abstract for that
DOI.

**Absorbed:** a stopping guarantee is only meaningful paired with a retained
recall target; a work-saving number alone is not a result. The transparency
critique in `li2020whentostop` is the same objection ORION's route/task
separation raises, applied one level up.

**ORION delta under test:** when route stop is typed separately from task stop,
does premature task closure change relative to a system where a route stop may
certify task completeness? Open question.
