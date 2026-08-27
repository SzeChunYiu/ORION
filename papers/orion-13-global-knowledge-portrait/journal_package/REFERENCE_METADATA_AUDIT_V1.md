# ORION-13 reference metadata audit V1

**Audit date:** 2026-08-18  
**Scope:** references used by the scoped ORION-13 manuscript  
**Status:** `CURRENT_METADATA_REPAIRED / SUBMISSION_REFRESH_STILL_REQUIRED`

This audit checks bibliographic identity rather than scientific novelty. It records corrections made before submission packaging and does not replace the required literature-refresh window immediately before actual submission.

## Material corrections

| Key | Previous defect | Corrected identity / disposition |
|---|---|---|
| `discoveryEngine2025` | Wrong title and author attribution (`Hope et al.`). | Vladimir Baulin, Austin Cook, Daniel Friedman, Janna Lumiruusu, Andrew Pashea, Shagor Rahman, Benedikt Waldeck, **The Discovery Engine: A Framework for AI-Driven Synthesis and Navigation of Scientific Knowledge Landscapes**, arXiv:2505.17500. |
| `biosage2025` | Wrong title and author attribution (`Taylor et al.`). | Svitlana Volkova et al., **Cross-Disciplinary Knowledge Retrieval and Synthesis: A Compound AI Architecture for Scientific Discovery**, arXiv:2511.18298. |
| `openScholar2024` | Wrong lead author and title wording. | Akari Asai et al., **OpenScholar: Synthesizing Scientific Literature with Retrieval-Augmented LMs**, arXiv:2411.14199. |
| `llmatch2025` | Truncated/noncanonical title and wrong author attribution. | Sha Wang et al., **LLMATCH: A Unified Schema Matching Framework with Large Language Models**, arXiv:2507.10897. |
| `adias2026` | Citation existed but the manuscript described ADIAS as schema/prompt integration. ADIAS is an issue-centric agent-design/self-improvement system, not a ORION-13 schema-integration source. | Removed from the ORION-13 manuscript/bibliography. ORION-15 retains ADIAS where it is scientifically relevant. |
| `raghunathan2022stance` | arXiv:2204.14178 resolves to an algebraic-geometry paper, not a stance survey. | Replaced with Hardalov, Arora, Nakov & Augenstein, **A Survey on Stance Detection for Mis- and Disinformation Identification**, Findings of NAACL 2022, DOI `10.18653/v1/2022.findings-naacl.94`. |
| `liu2022scholar` | arXiv:2206.05014 resolves to **Building an Icelandic Entity Linking Corpus**, not a scholarly-KG survey. | Replaced with Verma, Bhatia, Harit & Batish, **Scholarly Knowledge Graphs through Structuring Scholarly Communication: A Review**, *Complex & Intelligent Systems* 9, 1059–1095, DOI `10.1007/s40747-022-00806-6`. |
| `oh2017unified` | Exact title/metadata in the old bibliography could not be verified and was not needed for the scoped argument. | Replaced with Hofer, Obraczka, Saeedi, Köpcke & Rahm, **Construction of Knowledge Graphs: Current State and Challenges**, *Information* 15(8):509 (2024), DOI `10.3390/info15080509`, which directly covers ontology/schema matching, entity resolution, fusion, provenance, and KG construction. |
| `sebastian2017measurement` | Cited title/journal combination could not be verified. | Replaced with Jilke, Petrovsky, Meuleman & James, **Measurement Equivalence in Replications of Experiments: When and Why It Matters and Guidance on How to Determine Equivalence**, *Public Management Review* 19(9):1293–1310, DOI `10.1080/14719037.2016.1210906`. |
| `euzenat2007ontology` | Entry was typed as conference proceedings and incorrectly marked `edition=2` for 2007. | Corrected to the 2007 **first edition** Springer book, DOI `10.1007/978-3-540-49612-0`. The second edition is 2013 and is a different DOI. |
| `swanson1990` | Key/year/type were inconsistent with the cited 1997 *Artificial Intelligence* article. | Replaced by `swanson1997interactive`: Swanson & Smalheiser, **An Interactive System for Finding Complementary Literatures: A Stimulus to Scientific Discovery**, *Artificial Intelligence* 91(2):183–203, DOI `10.1016/S0004-3702(97)00008-8`. |
| `swanson1986` | Missing DOI. | Bound to DOI `10.1353/pbm.1986.0087`. |
| `kellert2006` | Edited volume represented the editors as ordinary book authors. | Corrected to editors Stephen H. Kellert, Helen E. Longino & C. Kenneth Waters, *Scientific Pluralism*, Minnesota Studies in the Philosophy of Science 19 (2006). |
| `chang2012` | Exact article metadata in the old entry was not established by the audit and was unnecessary to support the pluralism boundary. | Removed rather than retain an uncertain citation; the scoped statement remains supported by Kellert–Longino–Waters and Cartwright. |

## Primary/authoritative metadata sources checked

- arXiv records for `2608.10974`, `2607.27955`, `2607.21610`, `2606.05415`, `2507.10897`, `2505.17500`, `2511.18298`, and `2411.14199`;
- ACL Anthology record `2022.findings-naacl.94`;
- Springer records for *Ontology Matching* and the scholarly-KG review;
- MDPI/University of Leipzig record for *Construction of Knowledge Graphs: Current State and Challenges*;
- publisher/DOI records for Jilke et al. measurement equivalence and the Swanson literature-based-discovery papers;
- University of Minnesota / publisher records for *Scientific Pluralism*;
- Cambridge University Press record for *The Dappled World*.

## Related-work semantic corrections

Metadata repair alone was insufficient. `manuscript/sections/20-related-work.tex` was rewritten so that:

- MUSE is described as a problem–solution–rationale resource, not as producing one canonical structure per source;
- SCOPE/SCION are credited for evidence-linked schema induction and optional fusion without claiming their object is identical to ORION-13;
- ontology matching is credited for equivalence, subsumption, disjointness, and other correspondence relations rather than caricatured as a single equivalence output;
- stance detection is described as target-relative stance classification, not a binary contradiction oracle;
- ADIAS is removed from ORION-13 schema integration because it belongs to self-improving agent design;
- OpenScholar and BioSage are credited for retrieval/synthesis/agent orchestration rather than inaccurately described as single-prompt canonicalization systems.

## Submission rule

- [x] current scoped bibliography has no knowingly retained wrong arXiv identity from the audited set;
- [x] current related-work prose is aligned to the functional mechanism of the corrected sources;
- [ ] rerun exact title/author/DOI/version metadata against current publisher/primary records inside the submission literature-refresh window;
- [ ] add any materially closer work found in that final refresh and reopen the residual claim if necessary.

A corrected bibliography does not itself establish novelty or `PEER_REVIEW_READY`.
