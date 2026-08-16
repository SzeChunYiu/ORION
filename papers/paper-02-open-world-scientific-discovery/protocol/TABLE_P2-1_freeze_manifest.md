# Table P2-1: benchmark / data / license / provider / freeze manifest

<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate with:
       python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_1.py
     Source of record: protocol/EXTERNAL_ACCESS_AUDIT_V1.json -->

Audit performed `2026-08-16T17:33:33Z` - `2026-08-16T17:46:22Z`.
Schema `orion.p2-external-access-audit.v1` for protocol `P2.open-world-discovery.v1`.

This table is outcome-blind: it records what can be obtained, under what licence, at what cost, and with what contamination exposure. It contains no ORION-vs-baseline results.

## A. Freeze manifest - identity, licence, obtainability

| Artifact | Kind | Pinned revision | Rev. exists | State | Licence | Redistribute | Content binding |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AutoResearchBench_code` | code | `a46c9bfb8968…` | yes | `OBTAINED` | Apache-2.0 | yes | git_tree_sha=8181218bf3da4b8b… |
| `AutoResearchBench_dataset` | dataset | not pinned | n/a | `OBTAINED` | Apache-2.0 | yes | decrypted_bundle_sha256=db1839438033a32d… |
| `MetaSyn` | code | `51b95b7061e1…` | yes | `OBTAINED` | MIT | yes | git_tree_sha=ee7ee5889e13c275… |
| `AgentSLR` | code | `3111fcf456c6…` | yes | `AVAILABLE_LICENSE_BLOCKED` | NONE_FOUND | no | git_tree_sha=0b0966e5b6ee1729… |
| `SAGE_benchmark` | dataset | `bc62257a13d8…` | yes | `AVAILABLE_LICENSE_BLOCKED` | NONE_FOUND | no | git_tree_sha=4d3b461d9de9c5a5… |
| `AgentSLR_dataset` | dataset | not pinned | n/a | `OBTAINED` | CC-BY-4.0 | yes | hf_revision_sha=01843a781bbd839c… |
| `MetaSyn_dataset` | dataset | not pinned | n/a | `OBTAINED` | MIT (project-authored annotations only); upst… | partial | hf_revision_sha=c8fa07d89c44093d… |
| `SAGE_official_evaluator` | evaluator | not pinned | n/a | `NOT_OBTAINABLE` | UNKNOWN | no | none |
| `SAGE_retrieval_corpus` | dataset | not pinned | n/a | `NOT_OBTAINABLE` | UNKNOWN | no | none |
| `OpenScholar` | code | not pinned | n/a | `CANNOT_CHECK` | Apache-2.0 | yes | none |
| `ResearchArena` | code | not pinned | n/a | `CANNOT_CHECK` | AMBIGUOUS | n/a | none |

## B. Provider, run requirements and contamination exposure

| Artifact | State | Provider / credentials | Judge calls | Hard blocker | Contamination |
| --- | --- | --- | --- | --- | --- |
| `AutoResearchBench_code` | `OBTAINED` | OpenAI-compatible chat endpoint (agent); OpenAI-compatible chat endpoint (LLM judge); uns… | Deep only: one judge call per (ground_truth_title x candidate_title) pair; max_candidates… | PAPER_SEARCH_API_URL is empty in example.env and the default SEARCH_TOOL=deepxiv resolves to tool_deepxivsearch.py, which targets a paper-search serv… | Evaluator and metrics are in-repo and deterministic for Wide; Deep depends on an LLM judge whose model identity must be… |
| `AutoResearchBench_dataset` | `OBTAINED` | none for download or decryption | n/a | none for obtaining the data | LOW-MODERATE. No public plaintext mirror surfaced in a web-search probe, but the upstream README states the obfuscation… |
| `MetaSyn` | `OBTAINED` | OpenAI-compatible chat endpoint | LLM-judge calls for report-quality metrics (coverage, insight, structure) per generated r… | Requires a paid OpenAI-compatible key for the judged report metrics, and Python >=3.10,<3.12 with pinned torch/faiss/transformers versions. The retri… | CANNOT_CHECK. The dataset is public and ungated and included-study lists are directly downloadable, so exposure is plau… |
| `AgentSLR` | `AVAILABLE_LICENSE_BLOCKED` | OpenAI; OpenRouter; Mistral (OCR); OpenAlex; NCBI; or a local vLLM server | Not an LLM-judge design: eval/ scores generated artefacts against PERG ground truth. LLM… | Requires paid API keys (OPENAI_API_KEY, OPENROUTER_API_KEY, MISTRAL_API_KEY for OCR, plus OPENALEX_API_KEY and NCBI_API_KEY) or a local GPU vLLM depl… | CANNOT_CHECK. The label dataset is public and ungated; no contamination probe was run. |
| `SAGE_benchmark` | `AVAILABLE_LICENSE_BLOCKED` | not specified by the repository | not applicable; the stated metrics are Exact Match and Weighted Recall, neither of which… | Two independent blockers. (1) No retrieval corpus: the paper (arXiv:2602.05975) states a 200,000-paper retrieval corpus, but the pinned repository is… | HIGH / UNAVOIDABLE. Query records carry fields paper_id, paper_title, complete_query and ground_truth {paperId, title}… |
| `AgentSLR_dataset` | `OBTAINED` | HuggingFace (anonymous download) | n/a | none for obtaining the labels; the article PDFs the labels describe are not included and must be fetched from publishers at run time | CANNOT_CHECK. Public and ungated; no contamination probe run. |
| `MetaSyn_dataset` | `OBTAINED` | HuggingFace (anonymous download) | n/a | none for obtaining; local encode of the corpus needs meaningful compute and disk | CANNOT_CHECK. Public and ungated with downloadable included-study lists; no contamination probe run. |
| `SAGE_official_evaluator` | `NOT_OBTAINABLE` | n/a | n/a | No evaluator code exists at the pinned revision. README.md specifies Exact Match for short-form and 'Weighted Recall - recall across relevance tiers… | Not applicable. |
| `SAGE_retrieval_corpus` | `NOT_OBTAINABLE` | n/a | n/a | The corpus is required to run the SAGE retrieval task family at all and was not found at any published location. Without it, task family sage_scienti… | Not applicable; artifact not obtained. Note that a closed corpus is exactly what would be needed to de-contaminate SAGE… |
| `OpenScholar` | `CANNOT_CHECK` | n/a | n/a | No pinned revision and no PROTOCOL_V1.json task family or reference_revisions entry. OpenScholar is cited in papers/paper-02-open-world-scientific-di… | Not assessed; artifact not pinned. |
| `ResearchArena` | `CANNOT_CHECK` | n/a | n/a | No canonical artifact identity. ResearchArena is referenced in papers/paper-02-open-world-scientific-discovery/README.md and evidence/FALSIFIER_V1.md… | Not assessed; artifact identity unresolved. |

## C. Locators and licence evidence

| Artifact | Locator | Licence source (verbatim check) |
| --- | --- | --- |
| `AutoResearchBench_code` | https://github.com/CherYou/AutoResearchBench | GET /repos/CherYou/AutoResearchBench/license -> HTTP 200, spdx_id Apache-2.0; LICENSE blob present in tree 8181218b at path LICENSE (10253 bytes). |
| `AutoResearchBench_dataset` | https://huggingface.co/datasets/Lk123/AutoResearchBench | HuggingFace dataset card metadata license: apache-2.0 (GET https://huggingface.co/api/datasets/Lk123/AutoResearchBench -> HTTP 200, cardData.license). Matches the protocol's Apache-2.0 clai… |
| `MetaSyn` | https://github.com/THUIR/MetaSyn | GET /repos/THUIR/MetaSyn/license -> HTTP 200, spdx_id MIT; LICENSE blob present in tree ee7ee588 (1072 bytes); pyproject.toml declares license = {text = "MIT"}. |
| `AgentSLR` | https://github.com/OxRML/AgentSLR | GET /repos/OxRML/AgentSLR/license -> HTTP 404 {"message":"Not Found"}. Full recursive tree at pinned commit 0b0966e5 enumerated (437 entries, truncated=false): no LICENSE, COPYING or NOTICE… |
| `SAGE_benchmark` | https://github.com/HughieHu/Sage | GET /repos/HughieHu/Sage/license -> HTTP 404 {"message":"Not Found"}. Full recursive tree at pinned commit 4d3b461d enumerated (11 entries, truncated=false): no LICENSE, COPYING or NOTICE b… |
| `AgentSLR_dataset` | https://huggingface.co/datasets/OxRML/AgentSLR | HuggingFace card metadata license: cc-by-4.0 (GET https://huggingface.co/api/datasets/OxRML/AgentSLR -> HTTP 200, cardData.license and tags include license:cc-by-4.0). |
| `MetaSyn_dataset` | https://huggingface.co/datasets/THUIR/MetaSyn | HuggingFace card metadata license: other. Resolved by fetching https://huggingface.co/datasets/THUIR/MetaSyn/raw/main/LICENSE (HTTP 200, 1277 bytes), whose preamble reads: 'The MIT license… |
| `SAGE_official_evaluator` | not published | No artifact located. |
| `SAGE_retrieval_corpus` | unpublished; claimed in arXiv:2602.05975 as a 200,000 paper retrieval… | No artifact located, therefore no licence to inspect. |
| `OpenScholar` | https://github.com/AkariAsai/OpenScholar (arXiv:2411.14199) | GET /repos/AkariAsai/OpenScholar -> HTTP 200, license field spdx_id Apache-2.0, 1577 stars, last pushed 2025-08-13T04:16:46Z. |
| `ResearchArena` | arXiv:2406.10291; no canonical repository pinned by P2 material | No canonical repository is identified in the P2 material, so no single licence can be attributed. GitHub repository search for 'ResearchArena in:name' returned at least four candidates with… |

## D. Pinned-revision integrity

- `keys_checked`: 4
- `keys_with_pinned_sha`: 4
- `pinned_shas_resolving`: 4
- `pinned_shas_missing`: 0
- verdict: No P0. Every 40-character SHA in PROTOCOL_V1.json reference_revisions resolves at its named repository, and all four repositories are public and unarchived.

## E. Cross-cutting findings

- Two of the four pinned code repositories (HughieHu/Sage, OxRML/AgentSLR) carry no licence at any depth of their pinned trees, so JOURNAL_READINESS section 8 'frozen corpora/index snapshots where redistribution permits' cannot be satisfied for them.
- The SAGE task family (sage_scientific_retrieval) has neither a published retrieval corpus nor an official evaluator, so it cannot be executed as specified regardless of licensing or budget.
- Every remaining external family requires paid third-party LLM credentials that this audit does not hold; AutoResearchBench additionally requires an unpublished paper-search backend.
- AutoResearchBench's obfuscation is key-less and locally reversible, and its gold labels ship inside the same records as the questions, so PROTOCOL_V1.json access_policy.hidden_labels must be enforced by the ORION harness rather than assumed from the benchmark.
- SAGE's gold set is public plaintext and web-indexed, making any live-provider SAGE result contaminated by construction.

## F. Explicitly not established by this audit

- Contamination rates for any benchmark. Only structural exposure plus two spot-check queries were performed.
- Whether a private or unlisted SAGE corpus exists. HuggingFace returns 401 for both absent and private repositories to unauthenticated callers and no credentials were supplied.
- Whether any of these evaluators actually run to completion, since no LLM credentials were used.
- Total monetary cost of a full evaluation. Call-count scale is estimated from configuration defaults; no provider pricing was applied.

## G. State counts

| State | Artifacts |
| --- | --- |
| `OBTAINED` | 5 |
| `AVAILABLE_LICENSE_BLOCKED` | 2 |
| `NOT_OBTAINABLE` | 2 |
| `CANNOT_CHECK` | 2 |

Total artifacts audited: 11.
