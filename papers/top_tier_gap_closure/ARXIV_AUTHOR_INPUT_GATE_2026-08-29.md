# ArXiv-first author-input gate — release-first ORION papers

Applies first to **ORION-06, 07, 08, 10, 12, 14, 16**. These facts are human-controlled filing metadata, not scientific evidence. This record resolves the fields supplied by the author on 2026-08-29 and leaves only fields that were not supplied as explicit omissions rather than inferred values.

## Resolved shared filing metadata

- **Author list/order:** `Sze Chun Yiu` (sole author).
- **Institutional affiliation:** omitted by author preference (operator update 2026-08-30). Named arXiv deposits carry no affiliation. Where a venue or portal *requires* an affiliation (Elsevier AIJ/IP&M metadata, Quantum), use `Stockholm University, Stockholm, Sweden`. No department/unit or street/postal address is inferred.
- **Corresponding author:** none designated by the author. Do not add a corresponding-author mark to the manuscript. If an external submission portal requires one, use the sole-author/submitter role only as a portal requirement and do not infer a separate manuscript designation.
- **Correspondence/contact email:** `sze-chun.yiu@fysik.su.se`.
- **ORCID:** not supplied; omit.
- **Funding:** `The author received no specific funding for this work.`
- **Competing interests / conflicts of interest:** `The author declares no competing interests.`
- **Public-release approval:** approved for the requested arXiv-first publication workflow and subsequent sequential journal submission.
- **Patent/IP timing:** author confirms that public posting does not conflict with patent or other IP timing.

## ArXiv licence decision

- **ORION-10 / Quantum:** **CC BY 4.0**. Quantum requires the final arXiv version to be uploaded under the same CC BY 4.0 licence used for the published article, so this paper is an explicit exception to the conservative default below.
- **ORION-06, 07, 08, 12, 14, 16:** **arXiv.org perpetual, non-exclusive license 1.0**. This is the conservative repository-only licence; copyright remains with the author and arXiv receives limited distribution rights. Do not switch these deposits to CC0 or another Creative Commons licence without a new author instruction or a target-journal requirement because arXiv licence choices are irrevocable for a deposited version.

## AI-assistance disclosure contract

The scientific rule is the same for every venue: AI output is not evidence, novelty authority, authorship, or external verification. Claims must remain grounded in bound code/data/results/proofs and checked citations. The sole human author is responsible for the submitted work.

### Elsevier route — AIJ / Information Processing & Management

Use a separate section immediately before the references, titled **Declaration of generative AI and AI-assisted technologies in the manuscript preparation process**:

> During the preparation of this work, the author used OpenAI ChatGPT and related language-model tooling to support literature triage, code and manuscript auditing, organization, language refinement, and preparation of code and text under author review. The author reviewed and edited all AI-assisted output, independently checked the scientific claims and cited sources against the underlying evidence, and takes full responsibility for the content of the article.

Where AI-assisted tooling materially participated in the research workflow rather than only manuscript preparation, add the following bounded Methods disclosure:

> AI-assisted tooling was used to execute and audit parts of the repository-based research workflow under frozen protocols. Scientific claims were accepted only when supported by the bound code, data, results, or proofs; AI-generated text or judgments were not treated as scientific evidence or independent verification.

### Quantum route — ORION-10

Quantum requires the scope of AI use inside the author-contribution statement. Use:

> **Author contributions.** Sze Chun Yiu conceived and directed the study, curated the evidence, verified the analyses and claims, and wrote and revised the manuscript. OpenAI ChatGPT and related language-model tooling were used for literature triage, code and manuscript auditing, organization, language refinement, and portions of code/text production under author review. The author checked the resulting claims, calculations, citations, and final manuscript and takes full responsibility for the work.

Do not list any AI system as an author.

### TMLR route — ORION-07 / ORION-08 / ORION-14

TMLR permits general-purpose LLM assistance but holds the human author fully responsible. The review PDF must remain anonymous even though a named arXiv preprint may exist. If an explicit disclosure is included in the anonymous review manuscript, use non-identifying wording:

> **AI assistance disclosure.** General-purpose language-model tools, including OpenAI ChatGPT, were used for literature triage, code and manuscript auditing, organization, and language refinement. All scientific claims, citations, analyses, and final text were reviewed against the underlying evidence by the human author, who retains full responsibility. The language-model tools are not authors and are not treated as scientific authority.

The named arXiv/final version may replace “the human author” with `Sze Chun Yiu`.

## arXiv choices per paper

Do not invent an arXiv identifier before upload succeeds.

- **ORION-06:** primary `cs.AI`; optional `quant-ph` cross-list only if the final manuscript materially centers the quantum case; arXiv perpetual non-exclusive licence.
- **ORION-07:** `cs.AI` by default; use `cs.LG` only if the final abstract is primarily an ML/agent-evaluation paper; arXiv perpetual non-exclusive licence.
- **ORION-08:** `cs.AI` by default; optional `cs.LG` cross-list if the final framing materially targets learning/agent evaluation; arXiv perpetual non-exclusive licence.
- **ORION-10:** primary **`quant-ph`**; **CC BY 4.0**.
- **ORION-12:** primary **`cs.IR`**; arXiv perpetual non-exclusive licence.
- **ORION-14:** `cs.AI` by default; optional `cs.LG` cross-list if justified by the final framing; arXiv perpetual non-exclusive licence.
- **ORION-16:** primary `cs.AI`; arXiv perpetual non-exclusive licence.

After arXiv deposition, insert the exact identifier/version into journal-facing availability/front matter only where the target requests it.

## Journal-specific filing notes

- **TMLR (07/08/14):** keep the review PDF and supplement anonymous. Author identity, affiliation, funding, competing-interest information and OpenReview profile details are supplied to the submission system, not exposed in the review PDF. TMLR submissions/publications are CC BY 4.0; the separately deposited arXiv version may retain the arXiv non-exclusive licence.
- **Quantum (10):** supply the `quant-ph` arXiv reference, CC BY 4.0 arXiv licence, and author-contribution/AI-use statement above. No corresponding-author mark is to be invented; use `sze-chun.yiu@fysik.su.se` wherever a contact email is required.
- **Elsevier AIJ/IP&M (06/12/16):** use the funding, competing-interest and generative-AI declarations above. If the submission system mandates a corresponding-author field, use the sole-author/submitter role only to satisfy the portal; the supplied contact email is `sze-chun.yiu@fysik.su.se`.

## Remaining human-only omissions

The only intentionally unresolved identity field is an **ORCID**, if the author later chooses to provide one. A portal may also request a department, street/postal address or phone number; those are submission-system fields rather than scientific or manuscript blockers and must not be invented. No scientific-data blocker remains from author metadata for the seven first-wave papers.
