# P2 target-journal scope check

Venue facts fetched **2026-08-17**; quotations are short and attributed to the URL
fetched. Pages that would not load are marked `CANNOT_CHECK`, and no scope, limit
or policy is asserted for them.

**Authority correction (2026-08-17, issue #99):** the offline campaign is
`TIER_B_committed` with the frozen plan's mandatory underpowered label, not
`DESCRIPTIVE_ONLY`. A bounded Deep official-judge probe is now archived
(`DEEP_OFFICIAL_ARCHIVE_V1.json`, hit rate 0.000) and remains separately
scoped from matched ORION-vs-baseline evidence. The TMLR recommendation
below is unchanged. A second dated check
(`protocol/TARGET_JOURNAL_SCOPE_CHECK_2026-08-17.md`) recommends IP&M.
Neither check satisfies issue #99's "after external results stabilize"
precondition: matched Wide/Deep execution is still open (#157 / #279).

## 1. What this paper can honestly offer

From `protocol/CLAIM_LEDGER_V1.json` (checker green; `known_defects` empty):

- **Supported.** The governance mechanism — earned route independence,
  question-conditioned read state, route-stop/task-stop separation, fail-closed
  coverage — probed on a frozen, fully synthetic complete-gold index (task count per
  `evidence/offline_gold/MANIFEST.json` → `task_count`); negative ablations fail in
  the designed directions. Authority `TIER_B_committed` plus the plan's
  mandatory underpowered label: assumed-p half-width exceeds the frozen
  superiority margin, so no promoted interval, *p*-value or superiority
  decision is drawn from the offline companion.
- **Supported, bounded.** One external, official, credential-free retrieval and
  screening evaluation (MetaSyn ID-only, all released test reviews, pinned evaluator)
  whose candidate is a keyless BM25 + deterministic screening probe, **not** the
  matched multi-provider ORION system. A separate AutoResearchBench Deep
  official-judge probe of the keyless public-arXiv candidate is archived and
  is likewise not a matched ORION-vs-baseline result.
- **Not supported.** Superiority on real literature. `CANNOT_CHECK`: no matched
  Wide or Deep ORION-vs-baseline result archived, SAGE not reproducible as
  published, live OpenAlex campaign not run.

Strongest honest sentence: *mechanism demonstrated on a synthetic
complete-denominator world, plus one bounded external probe; external superiority
unproven.* Any venue whose scope requires demonstrated real-world performance
gains is disqualified today, not merely a stretch.

## 2. Candidates

### Transactions on Machine Learning Research (TMLR)

Fetched <https://jmlr.org/tmlr/editorial-policies.html> and
<https://jmlr.org/tmlr/author-guide.html> (2026-08-17).
Acceptance turns on two questions: whether claims are "supported by accurate,
convincing and clear evidence", and whether some of its audience would be
interested. Papers qualify "even if the contribution or significance of the work
is modest"; novelty appears only as a prohibition on incorrectly claiming it.
Scope includes analytical frameworks and reproducibility studies. No page limit —
"Submissions may be any length, but a paper's length should be justified by its
content". Double-blind; supplement up to 100 MB, PDF or ZIP.

**Fit: strong.** The criteria score exactly the axis on which this paper is
defensible, and the prohibition they carry — unsupported bold statements — is what
the mechanised ledger exists to prevent. `DESCRIPTIVE_ONLY` authority and
`CANNOT_CHECK` external status are admissible because modest significance is not
disqualifying, and the 100 MB supplement holds the frozen world, summaries and
regeneration scripts. Risk: reviewers may read a fully synthetic evaluation as
insufficient evidence for the mechanism claim; the answer — a complete denominator
is what makes premature closure observable at all — belongs in the paper.

### Research Synthesis Methods

Fetched <https://www.cambridge.org/core/journals/research-synthesis-methods> (2026-08-17).
Journal of the Society for Research Synthesis Methodology, covering methods
across every stage of synthesis and seeking work "of general interest or utility
for the many fields and disciplines in which research synthesis is undertaken".
No explicit article-type list on the page.

**Fit: moderate, narrower than it looks.** Subject matter matches directly: stopping
rules, retrieval/screening separation and capture–recapture misuse are core concerns,
and the fail-closed argument against treating adaptive routes as independent capture
occasions is a real contribution there. The obstacle is evidential: this readership
evaluates methods against real reviews with real reference standards, and the only
such evidence here is a probe whose candidate is not ORION, so a synthetic result
reads as a simulation study awaiting validation. Viable **after** an external
campaign; weak before one.

### PLOS ONE

Fetched <https://journals.plos.org/plosone/s/criteria-for-publication> (2026-08-17).
Assesses scientific and technical soundness only; novelty, significance and
perceived impact are not criteria. Criterion 4 requires conclusions "supported by
the data" and rejects unjustified interpretation.

**Fit: workable fallback.** Soundness-only suits a paper whose merit is disciplined
scope, but criterion 4 is where this paper is most exposed: the offline campaign is
below its own inferential tier, so any conclusion phrased as superiority fails
there. No advantage over TMLR here, and the journal's breadth makes reviewer
expertise in retrieval governance less likely.

### Journal of Open Source Software (JOSS)

Fetched <https://joss.theoj.org/about> (2026-08-17).
Publishes papers about research software, which must "have an obvious research
application" and "be feature-complete (no half-baked solutions)", with at least
six months of public history. Papers cover the software, not new findings.

**Fit: out of scope for the paper, in scope for one artifact.** JOSS cannot host
the governance argument — it does not publish research findings — but is a
legitimate home for the evaluation harness (world generator, companion runner,
route-stop oracle replay) as a citable complementary artifact. Verify the
six-month public-history gate before assuming it.

### Not verified

`CANNOT_CHECK` (HTTP 403/402 or auth redirect on 2026-08-17; no scope or policy
asserted): QSS <https://direct.mit.edu/qss>, ACM TOIS <https://dl.acm.org/journal/tois>,
PeerJ CS <https://peerj.com/about/aims-and-scope/cs>, Systematic Reviews
<https://link.springer.com/journal/13643/aims-and-scope>. QSS and Systematic Reviews
are plausible on subject matter; re-check from a network that can load them.
## 3. Recommendation

**Submit to TMLR.** Constraint matching, not preference: this paper's evidence is
strong on claim–evidence alignment and absent on demonstrated real-world
superiority, and TMLR is the only verified venue whose criteria score the first and
do not require the second. Having no page limit also removes pressure to compress
the limitations and access-audit material that makes the narrow claim credible.

Two conditions follow, not options: the paper must present the offline result as
a mechanism demonstration and never as a discovery-performance result, with
`support_type: NONE_YET` rows held at `CANNOT_CHECK` in the prose; and
preparation must be double-blind, with manuscript, supplement and any repository
link anonymised. The second is not yet done.

**Reconsider Research Synthesis Methods only if an external campaign lands.** With
a denominator-valid Wide/Deep or real-review result, that readership is the better
long-term home for the stopping-rule argument, but it is the wrong first
submission today. Do not target any venue requiring demonstrated performance gains
until the external status changes; there is nothing to submit to one.
