# Detail — capture-recapture completeness and information foraging

Families 12-13 of [`../NEAREST_WORK_AUDIT_2026-08.md`](../NEAREST_WORK_AUDIT_2026-08.md).
Raw metadata: `../../evidence/literature/<key>.json`.

Both families are **method literatures, not leaderboards**. Neither has a
"strong system score" to report, and this audit does not manufacture one. What
each contributes is an assumption and a failure mode.

---

## 12. Capture-recapture search completeness — `spoor1996capturerecapture`, `kastner2009capturerecapture`, `rucker2011boosting`

**Primary anchor:** `kastner2009capturerecapture`, because it is the version
that proposes capture-mark-recapture as an explicit **stopping rule** for
searching — the closest prior act to what ORION refuses to do.

**Measures:** the size of the literature a search missed, estimated from the
overlap between two or more search "captures". Spoor et al. introduce the
technique for evaluating search completeness (BMJ 313:342-343)
`spoor1996capturerecapture`; Kastner et al. propose it as a stopping rule
(Journal of Clinical Epidemiology 62:149-157) `kastner2009capturerecapture`;
Rücker et al. revisit the estimator's qualification (Journal of Clinical
Epidemiology 64:1364-1372) `rucker2011boosting`.

**Does not measure — and this is the load-bearing point:** the estimator's
validity rests on the capture occasions being *independent*. It has no procedure
for establishing that they are. In classical use the occasions are separate
bibliographic databases, and independence is argued informally. Applied to
adaptive agentic search, where a later query is conditioned on what earlier
queries returned, the independence assumption is not merely unverified — it is
structurally violated by the search policy itself.

The degenerate case is sharpest: **zero overlap between two captures**. Under
the estimator's assumptions this reads as near-complete coverage. Under
dependent captures it is equally consistent with two routes that partitioned a
small explored region and jointly missed an unbounded remainder. Nothing in the
observation distinguishes the two.

**Reported performance:** not quoted for any of the three — Crossref carries no
abstract for these DOIs and no full text was fetched. Titles, authors, venues,
volumes, pages and DOIs are verified. As method papers, a benchmark score would
not exist for them in any case.

**Absorbed:** the diagnostic itself — overlap between capture occasions carries
information about what was missed — together with the assumption it needs.
Capture-recapture completeness estimation is explicitly **not** an ORION novelty
claim.

**ORION delta under test:** when route independence is not established, does
refusing a bounded unseen-mass estimate (returning `OPEN`/`CANNOT_CHECK` rather
than a flattering number) cost discovery yield? Open question. The refusal
semantics are already locally falsified; whether refusing is *affordable* in
external evaluation is not.

---

## 13. Information foraging — `pirolli1999foraging`, `pirolli1995foragingchi`

**Primary anchor:** `pirolli1999foraging` (Psychological Review 106:643-675),
with the earlier CHI treatment of information access environments
`pirolli1995foragingchi` as the applied companion.

**Measures:** it is a descriptive theory of how an agent under time cost
allocates effort between exploiting a current information patch and moving to
another, borrowing optimal-foraging structure from ecology — information scent,
patch residence time, and the diminishing-returns condition for leaving.

**Does not measure:** anything about correctness or completeness. Foraging
theory predicts *when a rational forager leaves a patch given its perceived
yield*; it says nothing about whether leaving was epistemically justified, and
nothing about obligations to patches never visited. A forager that abandons a
patch on low scent is behaving optimally by the theory even if the patch held
everything relevant.

**Why the family is load-bearing anyway:** it supplies the correct reading of
"marginal yield went flat". Foraging theory says flat marginal yield is a valid
signal to *leave this patch*. It emphatically does not say that flat marginal
yield means the environment is exhausted. Route-level flatness being read as
task-level saturation is a category error the theory itself already forbids —
which is why ORION's route/task separation is an absorption of this parent
rather than a departure from it.

**Reported performance:** not applicable and not quoted; this is theory, not a
benchmarked system. Crossref carries no abstract for either DOI. Titles,
authors, venues, volumes and pages are verified.

**Absorbed:** the patch-leaving calculus as the correct model of a *route* stop,
and information scent as the mechanism behind marginal-gain estimates.

**ORION delta under test:** does treating route-level flatness as a
patch-leaving decision with no task-level authority change premature task
closure, relative to a system in which a flat route may certify completeness?
Open question. Together with family 12 this is the pair that `ORION-12.D4`
(coverage refusal) composes: foraging says the route may leave, capture-recapture
says the estimate is unavailable, and neither licenses closure.
