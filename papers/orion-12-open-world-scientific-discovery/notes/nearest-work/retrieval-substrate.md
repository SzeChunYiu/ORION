# Detail — retrieval substrate: scientific RAG, federated search, diversification

Families 9-11 of [`../NEAREST_WORK_AUDIT_2026-08.md`](../NEAREST_WORK_AUDIT_2026-08.md).
Every number is reported by the cited source. Raw metadata:
`../../evidence/literature/<key>.json`.

---

## 9. OpenScholar / scientific RAG — `openscholar2024`

**Primary because** it is the strongest published scientific retrieval-augmented
synthesis system with an accompanying benchmark, and it fixes the boundary:
scientific RAG, corpus-scale indexing and self-feedback synthesis are **not**
available as ORION novelty.

**Measures:** correctness and citation accuracy of citation-backed long-form
answers. The system "retrieves relevant passages from 45 million open-access
papers", and ScholarQABench comprises "2,967 expert-written queries and 208
long-form answers across computer science, physics, neuroscience, and
biomedicine" `openscholar2024`.

**Does not measure:** discovery recall against a complete denominator. The
metric is answer correctness and citation support, so a system that retrieves a
sufficient passage set for a fluent, well-cited answer scores well regardless of
how much relevant literature it never surfaced. This is exactly the
discovery/synthesis conflation ResearchArena's staging is designed to break.

**Reported performance:** "OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2
by 7% in correctness, despite being a smaller, open model. While GPT4o
hallucinates citations 78 to 90% of the time, OpenScholar achieves citation
accuracy on par with human experts." "OpenScholar-GPT4o improves GPT-4o's
correctness by 12%." In human evaluation, "experts preferred OpenScholar-8B and
OpenScholar-GPT4o responses over expert-written ones 51% and 70% of the time,
respectively, compared to GPT4o's 32%" `openscholar2024`.

**Absorbed:** passage-level retrieval, corpus-scale datastore, citation-backed
synthesis, retrieval self-feedback. All parent mechanisms; none survives as an
ORION claim.

**ORION delta under test:** with synthesis quality held out of scope entirely,
does discovery recall against a complete denominator move under route
governance? Open question — and the point of the delta is that the OpenScholar
metric cannot answer it either way.

---

## 10. Federated search — `shokouhi2011federated`

**Primary because** it is the canonical treatment of searching across multiple
independent, heterogeneous, partially-cooperative backends, which is the
substrate ORION's route model sits on.

**Measures:** the classical federated-search subproblems — resource
representation, resource (collection) selection, and results merging across
searchable collections that do not share an index.

**Does not measure:** whether two selected resources constitute *independent*
evidence channels. Federated search selects resources for expected yield; it has
no notion of a route earning independence, and none of "this backend was
unavailable, so the obligation stays open" as a first-class state. Unavailability
in federated IR is a degraded-service condition, not a reportable coverage gap.

**Reported performance:** not quoted — this is a monograph-length survey
(Foundations and Trends in Information Retrieval 5:1-102) rather than a system
with a headline score, and Crossref carries no abstract for the DOI. Title,
authors, venue, volume, pages and DOI are verified.

**Absorbed:** resource selection and merging over heterogeneous backends;
the vocabulary of cooperative vs uncooperative collections.

**ORION delta under test:** does deriving route independence from backend,
query-derivation and capture identity — rather than from the resource label —
change the unique-relevant-per-route contribution? Open question.

---

## 11. Query diversification — `carbonell1998mmr`, `agrawal2009diversifying`, `santos2015diversification`

**Primary because** diversification is the established answer to "how do I stop
my queries from returning the same thing", and it makes clear that ORION's route
diversity claim is not about result-list novelty.

**Measures:** redundancy and coverage *within a ranked result list* for a single
query or query intent. MMR reranks for marginal relevance
`carbonell1998mmr`; the WSDM formulation diversifies results over query
subtopics/intents `agrawal2009diversifying`; the survey consolidates the area
(Foundations and Trends in Information Retrieval 9:1-90)
`santos2015diversification`.

**Does not measure:** independence of the *generating process*. Two diversified
result lists from the same backend under the same query-derivation policy remain
one capture occasion no matter how dissimilar their contents. Diversification
maximises observed dissimilarity; ORION's independence question is about
whether dissimilarity was *earned* by the process, and those come apart exactly
in the hostile case of "same backend, same query, two route names".

**Reported performance:** not quoted for any of the three — Crossref carries no
abstract for these DOIs and no full text was fetched. Titles, authors, venues,
pages and DOIs are verified.

**Absorbed:** subtopic/intent coverage as an explicit objective; marginal-gain
reranking as the mechanism for redundancy control.

**ORION delta under test:** do routes that earn independence contribute more
unique relevant evidence than nominally distinct routes whose diversity is only
list-level? Open question, and it is the direct operationalisation of `ORION-12.H2`.

---

## 12. Structurally bounded scholarly graph search — `hazra2026crase`

Crase builds a bounded, inspectable citation-graph candidate set and applies an
explicit stopping condition to scholarly deep search. It therefore owns an
adjacent acquisition-and-stopping design. The residual tested here is different:
whether a prospectively material route that is unavailable, censored, or
provider-invalid may disappear from task-level closure. The citation supports
the nearest-work boundary; it does not supply evidence for external retrieval
superiority or open-world completeness.
