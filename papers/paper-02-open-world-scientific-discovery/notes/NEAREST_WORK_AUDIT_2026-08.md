# Nearest-work audit — ORION Paper II (2026-08)

Closes step 1 of `JOURNAL_READINESS.md` §1: nearest-work coverage plus citation
integrity. Nearest work is treated as food — every strong parent is absorbed and
its mechanism named, then the residual ORION fibre is stated as a synthesis.

**Read order:** this file (core) → `nearest-work/*.md` (per-family detail) →
`../evidence/literature/*.json` (raw fetched metadata).

**Outcome-blind:** every number below is reported *by prior work* and quoted with
its citation. No ORION result is stated, predicted or implied. Each ORION delta
is written as a question under test, never as an expected direction.

---

## 1. Citation integrity sweep — result

28 bibliography keys, 28 live fetch records (arXiv API or Crossref), 0 `CANNOT_CHECK`.

**Scope of the recorded verdict — read this before quoting the counts.** The
`verdict` field in every evidence record is a **title comparison only**. Author,
year and venue were fetched and stored, and were compared *by inspection*
against the bibliography while it was rewritten, but that comparison is not
mechanised and is not what the verdict attests. An entry with a correct title
and a wrong named author would therefore be recorded `VERIFIED`. The missing
Min Zhang in `metasyn2026` was found by inspection of the stored record, not by
the automated check. `and others` is a legitimate BibTeX abbreviation and is not
a mismatch in either mode.

| class | n | VERIFIED | MISMATCH |
|---|---|---|---|
| pre-existing claim (independent test) | 10 | 7 | **3** |
| added by this audit (provenance record only) | 18 | 18 | 0 |

The two classes must not be summed as corroboration: for added entries the claim
was transcribed *from* the fetch, so `VERIFIED` is provenance, not independent
support. See `../evidence/literature/README.md`.

### Three mismatches were live defects in the shipped bibliography

- **`agentslr2026`** — claimed title `AgentSLR: Automating Systematic Literature
  Reviews in Epidemiology with Agentic AI` does not exist. The real title of
  arXiv:2603.22327 is *Evaluating AI-based Scientific Knowledge Synthesis with
  Epidemiological Systematic Reviews*. **AgentSLR is real, and is the harness
  introduced inside that paper** — its abstract states "We introduce AgentSLR, a
  large-scale evaluation harness comprising an SLR automation workflow and an
  expert annotated dataset covering 16,248 articles". Corroborated independently
  by `protocol/PROTOCOL_V1.json`, which pins `OxRML/AgentSLR` under
  `reference_revisions`. The citation **key is therefore sound**; only the title
  field was wrong. Fixed in place, with a `note` naming the harness. No
  `main.tex` change and no key rename are required.
- **`metasyn2026`** — claimed title dropped the leading `MetaSyn: A Benchmark
  for`, and the author list omitted Min Zhang. Not previously reported. Fixed.
- **`knowplan2026`** — the post-P2-X bibliography paired arXiv:2608.06530 with
  the wrong title and authors. The primary record is *KNOWPLAN: Knowledge-Driven
  AI Agents for Smart Degree Pathway Planning*. The key remains mechanism-relevant
  because the paper uses finite atomic catalog obligations plus an explicit
  closure certificate; the bibliography metadata is repaired, while the stored
  fetch verdict intentionally remains `MISMATCH` so the defect stays auditable.

Evidence: `../evidence/literature/agentslr2026.json`,
`../evidence/literature/metasyn2026.json`, and
`../evidence/literature/knowplan2026.json`.

---

## 2. Family index

Every family required by `JOURNAL_READINESS.md` §1 and by issue #99. Column
"primary" is the benchmark or work this audit selects as the family anchor.

| # | family | primary | key | detail |
|---|---|---|---|---|
| 1 | AutoResearchBench (Wide + Deep) | AutoResearchBench | `autoresearchbench2026` | [discovery-benchmarks](nearest-work/discovery-benchmarks.md) |
| 2 | SAGE | SAGE | `sage2026` | [discovery-benchmarks](nearest-work/discovery-benchmarks.md) |
| 3 | ResearchArena | ResearchArena | `researcharena2024` | [discovery-benchmarks](nearest-work/discovery-benchmarks.md) |
| 4 | expert literature-review comparison | physics/astro/cosmology study | `physicsreview2026` | [discovery-benchmarks](nearest-work/discovery-benchmarks.md) |
| 5 | MetaSyn | MetaSyn | `metasyn2026` | [screening-and-slr](nearest-work/screening-and-slr.md) |
| 6 | AgentSLR / protocol-driven SLR automation | AgentSLR harness | `agentslr2026` | [screening-and-slr](nearest-work/screening-and-slr.md) |
| 7 | active screening / technology-assisted review / necessary re-reads | CAL | `cormack2014tarprotocols` | [screening-and-slr](nearest-work/screening-and-slr.md) |
| 8 | systematic-review stopping | statistical stopping criteria | `callaghan2020stopping` | [screening-and-slr](nearest-work/screening-and-slr.md) |
| 9 | OpenScholar / scientific RAG | OpenScholar | `openscholar2024` | [retrieval-substrate](nearest-work/retrieval-substrate.md) |
| 10 | federated search | Federated Search survey | `shokouhi2011federated` | [retrieval-substrate](nearest-work/retrieval-substrate.md) |
| 11 | query diversification | search result diversification | `agrawal2009diversifying` | [retrieval-substrate](nearest-work/retrieval-substrate.md) |
| 12 | capture-recapture completeness | CMR as a search stopping rule | `kastner2009capturerecapture` | [completeness-and-foraging](nearest-work/completeness-and-foraging.md) |
| 13 | information foraging | information foraging theory | `pirolli1999foraging` | [completeness-and-foraging](nearest-work/completeness-and-foraging.md) |

Protocol task families (`protocol/PROTOCOL_V1.json`) map onto the above as:
`autoresearchbench_deep` and `autoresearchbench_wide` → row 1;
`sage_scientific_retrieval` → row 2; `metasyn_retrieval_screening` → row 5;
`offline_complete_gold` → the frozen local corpus, which has no external parent
benchmark and is the only family where a complete denominator is owned by us.

---

## 3. Absorbed synthesis — the residual fibre

Each parent contributes a mechanism; none is claimed as ORION novelty. The
detail files record the per-family absorption. Composed, the residual is:

- **Earned route independence** (from federated search + capture-recapture):
  federated search supplies resource selection and merging over heterogeneous
  backends; capture-recapture supplies the independence *assumption* that makes
  completeness estimable. ORION asks whether independence can be derived from
  backend, query-derivation and capture identity rather than asserted.
- **Question-conditioned read memory** (from TAR + information foraging):
  TAR supplies "already reviewed" state; foraging supplies the value-of-patch
  calculus for revisiting. ORION asks whether conditioning read state on the
  question, extraction schema and content version preserves necessary re-reads
  that a seen/unseen bit would suppress.
- **Route-vs-task stopping** (from SR stopping literature): the stopping
  literature terminates one screening process against a recall target. ORION
  asks whether typing route stop separately from task closure changes premature
  closure behaviour when other routes remain untried or unavailable.
- **Fail-closed coverage** (from capture-recapture + the expert-comparison
  study): ORION asks whether refusing a bounded unseen-mass estimate under
  unmet independence assumptions is achievable without losing discovery yield.

None of the four is novel as a *component*. The tested object is the
composition, under complete denominators, against strong simple baselines.

---

## 4. Minimum useful improvement — evidence basis

**The statistics lane owns the margins.** This section supplies only the
evidence basis: what effect sizes the source papers themselves present as
meaningful, so margins can be frozen against prior practice rather than taste.
No margin is proposed here, and nothing below should be read as one.

| family | effect size prior work presents as meaningful | source |
|---|---|---|
| AutoResearchBench | frontier systems reach 9.39% Deep accuracy / 9.31% Wide IoU, with many strong baselines below 5% — so the discriminating scale is single-digit percentage points | `autoresearchbench2026` |
| SAGE | authors present a ~30% BM25-over-LLM-retriever gap as the headline finding, and their own corpus-augmentation gains of 8% (short-form) and 2% (open-ended) as an improvement worth reporting | `sage2026` |
| AgentSLR | field-level extraction F1 ceiling of 0.67 across five frontier reasoning models is presented as a blocking bottleneck; cost varies up to 96x | `agentslr2026` |
| SR stopping | statistical stopping is presented as useful at an average 17% work reduction *while holding a stated recall target at a stated confidence* — the recall target, not the saving, is the binding constraint | `callaghan2020stopping` |
| OpenScholar | correctness margins of 5% over GPT-4o and 7% over PaperQA2 are presented as the headline result | `openscholar2024` |
| expert comparison | human/AI reference overlap below 6%, and 64% of real AI-cited papers carrying at least one wrong metadata field, are presented as evidence that expert search is not yet reproduced | `physicsreview2026` |

Two constraints follow for whoever freezes the margins. First, on
AutoResearchBench the absolute scale is compressed near zero, so a margin stated
in absolute points behaves very differently from the same margin on a benchmark
scored near the middle of the range. Second, the stopping literature does not
treat a work-reduction number as meaningful on its own — it is only meaningful
paired with a retained-recall guarantee, which is the same fail-closed shape
`P2.H3` asserts.

---

## 5. Residual gaps

- Reported-performance numbers could not be quoted for
  `kastner2009capturerecapture`, `rucker2011boosting`, `spoor1996capturerecapture`,
  `cormack2014tarprotocols`, `yang2021heuristicstopping` and
  `wallace2010semiautomated`: Crossref carries no abstract for these DOIs and no
  full text was fetched. Their titles, authors, venues and DOIs *are* verified.
  This is a bounded `CANNOT_CHECK` on one dimension, not on the citation.
- Four of these are method literatures rather than leaderboards, so a
  "what a strong system achieves" number may not exist for them at all; that is
  recorded per family in the detail files rather than assumed either way.
- `offline_complete_gold` has no external parent benchmark; its denominator
  discipline is owned by the frozen-corpus lane, not by this audit.
