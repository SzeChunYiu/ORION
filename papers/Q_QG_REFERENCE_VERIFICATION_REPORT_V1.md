# Q/QG reference verification report V1

Date checked: 2026-08-21
Method: `nature-ref-verifier` / `nature-academic-search` source hierarchy — primary publisher/proceedings/arXiv metadata first, DOI/Crossref-compatible identifiers second, manuscript-level donor cards for claim scope.

This report audits metadata/identity and publication use. It does **not** infer that a source supports a claim merely because its metadata is correct; support boundaries live in the donor Paper Cards and final manuscripts.

## Verified / primary-record anchored

| Key / source | Identity used by Q/QG | Verification state | Publication note |
|---|---|---|---|
| `schillo2026tare` | Schillo, Sturm, Quay, **TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation**, arXiv:2601.05740v4 | **Verified primary full text** | Earlier ORION wording used a stale title; V3 uses current title and full-text donor boundary |
| `izmaylov2020unitary` | Izmaylov et al., unitary partitioning of Pauli strings, JCTC 2020, DOI `10.1021/acs.jctc.9b00791` | **Verified DOI identity** | Donor primitive only; no ORION-01 novelty credit |
| `harrigan2024qualtran` | Qualtran, arXiv:2409.04643 | **Verified primary arXiv identity** | ORION-10 donor for compositional resource analysis |
| `moser2026qet` | Moser & Schaper, **Automated Expected Cost Analysis for Quantum Programs**, arXiv:2604.03971 | **Verified primary arXiv identity** | ORION-10 donor; generic static cost analysis ceded |
| `leblond2023realistic` | LeBlond et al., realistic resource estimation / compilation-driven analysis, arXiv:2311.10686 | **Verified primary identifier** | ORION-10 resource-estimation context; final title/authors must match current record |
| `rice1976algorithm` | Rice, algorithm selection, 1976, DOI `10.1016/S0065-2458(08)60520-3` | **Verified DOI identity** | ORION-09 conceptual ancestor |
| `smithmiles2023isa` | Smith-Miles & Muñoz, **Instance Space Analysis for Algorithm Testing: Methodology and Software Tools**, ACM CSUR 55(12), Article 255, DOI `10.1145/3572895` | **Verified primary ACM full text** | ORION-09 primary conceptual parent; feature/footprint novelty removed |
| `chen2025scienceagentbench` | Chen et al., **ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery**, ICLR 2025, arXiv:2410.05080 | **Verified proceedings/arXiv identity** | ORION-02/ORION-03 benchmark parent |
| `bragg2025astabench` | Bragg et al., **AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite**, arXiv:2510.21652v2; ICLR 2026 | **Verified primary record** | Keep version/venue metadata synchronized at submission |
| `meng2026scientistone` | Meng et al., **ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence**, arXiv:2605.26340 | **Verified primary arXiv identity** | ORION-02 direct donor for CoE/research-integrity auditing |
| `liu2026sciagentarena` | **SciAgentArena**, arXiv:2606.12736 | **Verified primary identifier** | ORION-02/ORION-03 benchmark parent; final author/title list must match current record |
| `chao2026stale` | Chao et al., **STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?**, arXiv:2605.06527 | **Verified primary arXiv identity** | ORION-04 donor for semantic stale-memory invalidation |
| `sulpovar2026contextnest` | Sulpovar et al., **ContextNest: Verifiable Context Governance for Autonomous AI Agent**, arXiv:2607.02116 | **Verified primary arXiv identity with naming caution** | Retrieved abstract alternated `ContextNest` / `ContextNext`; final citation must follow current title record, not body typos |
| `russell1991rightthing` | Russell & Wefald, *Do the Right Thing: Studies in Limited Rationality* (1991) | **Verified canonical monograph identity** | ORION-04 value-of-information ancestry |
| `buneman2001provenance` | Buneman, Khanna, Tan, database provenance, DOI `10.1007/3-540-44503-X_20` | **Verified DOI identity** | ORION-04 provenance ancestry |
| `cheney2009provenance` | Cheney, Chiticariu, Tan, provenance survey, DOI `10.1561/1900000006` | **Verified DOI identity** | ORION-04 provenance ancestry |

## Verified identities with final-submission freshness check required

The following are recent/fast-moving works for which title/version/venue metadata can legitimately change between this publication cut and submission:

- TARE v4 — recheck current arXiv version/title within 14 days of ORION-01/ORION-09/ORION-10 submission.
- AstaBench — recheck final ICLR 2026 proceedings metadata.
- ScientistOne — recheck arXiv version and any conference/journal publication.
- SciAgentArena — recheck current arXiv version/title/author list.
- STALE — recheck current version/publication.
- ContextNest — specifically resolve the `ContextNest`/`ContextNext` naming inconsistency from the primary record.
- Qet — recheck current arXiv version/publication.

A venue migration never changes the evidence meaning; update only metadata/citation rendering unless the paper itself materially changes the donor boundary.

## Reference-manager integrity rules

1. One stable citation key per intellectual work across all Q/QG papers.
2. No duplicate DOI may appear under two keys.
3. arXiv version suffix may be recorded in notes/URL but the base arXiv identifier is the stable work identity unless a materially revised paper needs explicit version citation.
4. Proceedings metadata outranks stale arXiv-only venue fields once the final proceedings record exists, while the arXiv identifier may remain as an alternate locator.
5. Author truncation such as `and others` is allowed only at the BibTeX data/rendering layer if the final target style supports it; do not silently drop authors because a web snippet is short.
6. The final bibliography must be regenerated from the shared verified BibTeX, not hand-copied separately into five manuscripts.

## Claim-support warnings

Metadata verification is not support verification. Specifically:
- TARE full text was read for the detailed ORION-01 donor boundary; abstract-level wording is insufficient there.
- ISA full text was read for the ORION-09 conceptual-parent subtraction.
- ScientistOne/AstaBench/ScienceAgentBench/STALE/ContextNest/Qet Paper Cards currently contain source-limited or primary-record boundaries where noted. Do not add detailed mechanism claims beyond what those cards verify without a new full-text read.

## Final gate

Immediately before each submission:
1. rerun current metadata lookups for every cited 2025–2026 preprint;
2. verify every DOI resolves to the cited title/authors;
3. compare title/author/year/venue against the shared BibTeX;
4. rebuild all target source/PDF packages;
5. rerun citation/reference and visual audits.

Do not make a cosmetic citation update if a new version materially subsumes the claimed ORION residual; that triggers a scientific freshness review instead.
