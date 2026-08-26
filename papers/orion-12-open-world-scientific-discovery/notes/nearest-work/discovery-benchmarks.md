# Detail — discovery benchmarks

Families 1-4 of [`../NEAREST_WORK_AUDIT_2026-08.md`](../NEAREST_WORK_AUDIT_2026-08.md).
Every number is reported by the cited source. Raw metadata and full abstracts:
`../../evidence/literature/<key>.json`.

---

## 1. AutoResearchBench (Wide + Deep) — `autoresearchbench2026`

**Primary because** it is the only family anchor that splits discovery into a
targeted mode and an open-ended set mode, and the open-ended mode leaves the
number of qualifying papers unknown — which is exactly the condition under which
a stopping rule has to do real work.

**Measures:** Deep Research — whether a specific target paper is tracked down
through progressive multi-step probing. Wide Research — set overlap (IoU)
against a qualifying set collected under given conditions.

**Does not measure:** downstream synthesis quality; whether the route that found
an item was independent of any other route; whether the system stopped for a
good reason or a lucky one. A Wide IoU score is agnostic to *how many* routes
produced the set and to whether unavailable routes were silently dropped.

**Reported performance:** "Even the most powerful LLMs, despite having largely
conquered general agentic web-browsing benchmarks such as BrowseComp, achieve
only 9.39% accuracy on Deep Research and 9.31% IoU on Wide Research, while many
other strong baselines fall below 5%" `autoresearchbench2026`.

**ORION delta under test:** does typing route stop separately from task closure
change the premature-closure rate on Wide tasks, where the qualifying-set size
is unknown by construction? Open question; no direction asserted.

---

## 2. SAGE — `sage2026`

**Primary because** it establishes the lexical-baseline promotion gate on
scientific retrieval specifically, on a frozen corpus, inside deep-research
agent workflows rather than in isolation.

**Measures:** retrieval quality for deep research agents over a fixed scientific
corpus — 1,200 queries across four scientific domains against a 200,000-paper
retrieval corpus `sage2026`.

**Does not measure:** open-world discovery over live providers; provider
unavailability; cross-route deduplication. The corpus is fixed, so a route that
fails in the open world cannot fail here.

**Reported performance:** six deep research agents were evaluated and "all
systems struggle with reasoning-intensive retrieval"; using a DR Tulu backbone,
"BM25 significantly outperforms LLM-based retrievers by approximately 30%"
because "existing agents generate keyword-oriented sub-queries". The authors'
corpus-level test-time scaling framework "yields 8% and 2% gains on short-form
and open-ended questions, respectively" `sage2026`.

**Absorbed:** BM25 is a promotion gate, not a straw man. Any ORION route stack
that cannot beat it on a frozen corpus has not earned promotion.

**ORION delta under test:** does query-derivation independence across routes
change the sub-query distribution away from the keyword-oriented mode SAGE
identifies as the failure cause? Open question.

---

## 3. ResearchArena — `researcharena2024`

**Primary because** it separates discovery from selection from organization and
attributes error to the stage, which is the precondition for claiming a
discovery result rather than a synthesis result.

**Measures:** three staged capabilities — information discovery (identifying
relevant literature), information selection (relevance and impact), information
organization (hierarchical frameworks; mind-map construction is a bonus task)
`researcharena2024`.

**Does not measure:** live-provider behaviour. The environment is offline by
construction — 12M full-text academic papers and 7.9K survey papers, built from
S2ORC via released construction code rather than redistributed corpora
`researcharena2024`.

**Reported performance:** "Preliminary evaluations reveal that LLM-based
approaches underperform compared to simpler keyword-based retrieval methods,
though recent reasoning models such as DeepSeek-R1 show slightly better
zero-shot performance" `researcharena2024`.

**Absorbed:** stage-attributed evaluation. ORION may not claim search progress
because organization output looks good. This is the second independent source
(with SAGE) for the lexical-baseline gate.

**ORION delta under test:** does the discovery stage alone move when route
governance is added, holding selection and organization fixed? Open question.

---

## 4. Controlled expert literature-review comparison — `physicsreview2026`

**Primary because** it is the only anchor whose denominator is an expert's own
search rather than a curated benchmark, which is the closest available proxy
for the open-world completeness question Paper II cannot resolve from finite
search.

**Measures:** overlap between references selected by human experts and by AI
systems on identical literature-review tasks across eight expert-conceived
research projects in physics, astrophysics and cosmology; plus reference
reliability, split into fabrications and metadata mismatches
`physicsreview2026`.

**Does not measure:** recall against a complete gold set — no complete
denominator exists for these projects. Low overlap is evidence of divergence,
not proof that either side missed relevant work.

**Reported performance:** overlap between human- and AI-selected references is
"small ($<$6\%), indicating AI models do not yet reproduce competent expert
search on their own". On reliability: "fabricated references make up 3\% of
AI-generated references, [and] 64\% of real papers [have] at least one incorrect
field (title, author, year, journal, DOI, or link)". A single-project test of a
2026 model showed "zero fabrication and metadata mismatches"
`physicsreview2026`.

**Directly relevant to this audit:** the 64% metadata-mismatch finding is the
same failure class this sweep found twice in our own bibliography (§1 of the
core audit). Verification is not optional for either side.

**ORION delta under test:** does fail-closed coverage reporting — naming
unavailable routes and censored obligations rather than converting them into
absence — change what a low-overlap result licenses one to conclude? Open
question.
