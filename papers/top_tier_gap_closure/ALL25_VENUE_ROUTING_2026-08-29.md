# ORION-01–25 venue routing — arXiv first, journal second

**Method:** academic-paper-pipeline v1.6.0. Venue follows the strongest earned paper archetype; claims are never widened to fit a venue. Every paper goes to arXiv first when author-controlled metadata/licensing are supplied, then to one archival journal at a time.

`EXACT` means the route is already established in the repository or checked against a current official venue contract. `PROVISIONAL` means the journal family fits the bounded contribution, but exact current instructions/scope must be re-resolved immediately before package conversion.

| Paper | Earned paper archetype | Primary journal route | Fallback / narrower route | Route status |
|---|---|---|---|---|
| ORION-01 | exact quantum-compilation theory, split A/B | **Quantum** | Theoretical Computer Science (quantum/natural-computing theory) | PROVISIONAL pending independent proof/novelty closeout |
| ORION-02 | finite-fibre theorem + adverse transfer boundary | **TMLR** if framed as learning/certifiability insight | Machine Learning / theory-oriented specialist after exact scope check | PROVISIONAL |
| ORION-03 | typed merge/retraction and provenance-safety calculus | formal/security journal selected after final native-semantics reframe | Theoretical Computer Science if the paper is theorem-first | PROVISIONAL; do not force into ML |
| ORION-04 | proof-producing exact combinatorial/computational theorem | Journal of Automated Reasoning-style formal reasoning venue | Theoretical Computer Science | PROVISIONAL; exact authority gate remains |
| ORION-05 | exact quantum expressivity/support theorem | **Quantum** | Theoretical Computer Science | EXACT Quantum route already packaged |
| ORION-06 | negative-result successor/recovery method + theorem | **Artificial Intelligence (AIJ)** | **TMLR** if AIJ breadth/value screen is unfavorable | EXACT primary/fallback family |
| ORION-07 | prospective deferred-outcome evaluation benchmark | **TMLR** | AIJ Research Note only if TMLR scope fit weakens | EXACT TMLR package route |
| ORION-08 | matched-information typed-state mechanism studies | **TMLR** | AIJ if reframed toward broader AI decision mechanisms | EXACT TMLR package route |
| ORION-09 | quantum regime geometry with adverse transfer | **Quantum** | Theoretical Computer Science | EXACT Quantum fallback; do not inflate to PRX-style breadth |
| ORION-10 | certified quantum forecasting + explanation lower bound | **Quantum** | Theoretical Computer Science | EXACT Quantum/arXiv route |
| ORION-11 | corrected mechanism/failure-analysis paper with preserved retraction | **TMLR** if learning/research-agent mechanism is central | AIJ Research Note / specialist AI methods venue | PROVISIONAL |
| ORION-12 | information-retrieval governance / critical system design | **Information Processing & Management** | JASIST-style information-science venue after exact scope check | EXACT IP&M route |
| ORION-13 | polarity-sensitive structured semantic mapping | **Journal of Web Semantics** | Data & Knowledge Engineering | PROVISIONAL; strong semantic/KG fit |
| ORION-14 | protected scientific-authority evaluation relation | **TMLR** | AIJ if manuscript is broadened without new claims | EXACT TMLR route |
| ORION-15 | formal governance / anytime-safe revision + fail-closed non-computation | **TMLR** for bounded learning/research-agent governance | AIJ / formal-methods specialist depending final center | PROVISIONAL |
| ORION-16 | formal epistemic lifting and graph-quality mechanics | **Artificial Intelligence (AIJ)** | Theoretical Computer Science for a theorem-first contraction | EXACT AIJ route |
| ORION-17 | bounded regime-change navigation + `NO_DISCRIMINATION` mechanism diagnosis | AIJ if the corrected AI-mechanism story is retained | software-evolution empirical venue if the repository-change mechanism dominates | PROVISIONAL; density route stays closed |
| ORION-18 | non-laundering authority calculus / non-identifiability | AIJ for the AI-governance theorem | Journal of Automated Reasoning / Theoretical Computer Science for theorem-first version | PROVISIONAL |
| ORION-19 | small-n structured causal-diagnostic learning | **TMLR** | AIJ Research Note | PROVISIONAL, family-level inference mandatory |
| ORION-20 | negative/impossibility theorem: multiple singleton minima | **Theoretical Computer Science** | Journal of Automated Reasoning-style venue if proof automation is central | PROVISIONAL; no minimality rescue |
| ORION-21 | tie-equivalence impossibility + scoped placement boundary | **Theoretical Computer Science** | AIJ if decision-theoretic AI interpretation dominates | PROVISIONAL |
| ORION-22 | exact bounded adaptive-state allocator law + broken robustness axes | **TMLR** | AIJ | PROVISIONAL; untouched transfer is successor only |
| ORION-23 | responsibility-carrying transport law with three-valued authority | **TMLR** | AIJ / semantic-governance specialist | PROVISIONAL; self-scored safety excluded |
| ORION-24 | research-software/governance conformance with principled nulls | empirical software-engineering journal after exact contract resolution | TMLR only if the final object is genuinely a learning/evaluation method | PROVISIONAL; external adjudication remains successor |
| ORION-25 | execution-integrity / trust-domain separation theorem | security/formal-systems journal after exact contract resolution | Theoretical Computer Science for theorem-first version | PROVISIONAL; signatures are not scientific authority |

## Current official-contract anchors

- **TMLR:** claims must be supported by accurate, convincing evidence; reducing claims is an explicit alternative to collecting more experiments. TMLR emphasizes technical correctness rather than subjective significance and permits arXiv preprints while the review PDF remains anonymous.
- **Quantum:** submission is arXiv-first; the preprint must be in or cross-listed with `quant-ph`. The first pages should clearly state main results and assumptions.
- **AIJ:** broad AI advances, including reasoning, knowledge representation, planning, ML and multi-agent systems; results/proposals must demonstrate value and effectiveness. Use the TMLR fallback when a bounded methods paper is technically strong but does not clear AIJ's breadth/value screen.
- **IP&M:** explicitly welcomes research methods and critical system-design manuscripts at the computing/information-science intersection, matching ORION-12's narrowed claim.
- **Theoretical Computer Science:** welcomes mathematical, logical and formal concepts motivated by computing, including theoretical quantum/natural computing; suitable for bounded theorem/negative-theorem papers without an empirical breadth claim.
- **Journal of Web Semantics:** explicitly covers formal ontology/KG representation, consistency/change/evolution, provenance, governance and evaluation, making it a strong candidate family for ORION-13.

## Routing rule

Before converting any `PROVISIONAL` row into a journal package, re-open the current official Guide for Authors and write a one-page venue decision contract: exact article type, scope fit, anonymity/preprint policy, word/page constraints, data/code/declaration requirements, and the exact claim that would trigger a desk-reject risk. If the contract does not fit the earned claim, change the journal—not the science.