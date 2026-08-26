# Search-time contamination probes

Probes run `2026-08-16T17:36Z–17:42Z`. Purpose: decide whether live-provider search routes can be
trusted on these public benchmark tasks, per `PROTOCOL_V1.json`
`access_policy.search_contamination_policy`.

Scope limit stated up front: these are **spot checks plus a structural exposure analysis**, not an
exhaustive contamination measurement. They are sufficient to classify exposure per benchmark; they
are not sufficient to quantify a contamination rate. Quantification remains open.

## AutoResearchBench — structural exposure: obfuscation is key-less and reversible

The published bundle declares `"scheme": "public_canary_xor_sha256"`. `decrypt_benchmark.py`
derives the mask as `sha256(canary_string)` where `canary_string` is stored **inside the bundle's
own metadata**. No password, key or credential is required; the decryption in
`autoresearchbench_decrypt_record.json` was performed with no secret supplied and reproduced the
declared `original_sha256` exactly.

The upstream README states this plainly:

> The published file uses public reversible obfuscation for benchmark release. It lowers casual web
> exposure, but it is not strong access control.

Consequence: obfuscation raises the cost of *accidental* indexing but places no barrier in front of
any party that has the file. The dataset reported 255 downloads at audit time.

**Probe 1.** Web search: `"AutoResearchBench.jsonl" decrypted benchmark questions answers`.
Result: no public dump of decrypted question-answer pairs surfaced; hits were the official
repository, the arXiv paper, and unrelated benchmarks. Recorded outcome: **no evidence of a public
plaintext mirror**. This is a negative result from one query and does not establish absence.

**Exposure classification: LOW-MODERATE.** Question and gold text are not published in plaintext
and no mirror was found, but the protection is declared-weak by its own authors, so a
frozen-provider live run should still record answer-exposure per query rather than assume cleanliness.

Note for the protocol's `access_policy.hidden_labels` clause: the decrypted records carry
`answer` and `arxiv_id` in the same record as `question`. The official distribution therefore
places gold labels inside candidate custody. Any hidden-label guarantee for AutoResearchBench must
be enforced by the harness (split the file before the candidate sees it), not inherited from the
benchmark.

## SAGE — structural exposure: gold answers are public plaintext, adjacent to the query

`Sage_Short_Form_Questions/*.json` records have fields
`['paper_id', 'paper_title', 'complete_query', 'ground_truth']`, with
`ground_truth = {'paperId': ..., 'title': ...}`. The answer sits in the same public JSON object as
the query, in an unobfuscated public GitHub repository. 150 records per domain file.

**Probe 2.** Took `ground_truth.title` of record 0 of `Sage_Short_Form_Questions/natural_science.json`
— `"Thermodynamics of Schwarzschild-AdS black hole in non-commutative geometry"` — and web-searched
it verbatim. The exact target paper was the top result
(`cpc.ihep.ac.cn/article/doi/10.1088/1674-1137/adbacd`, mirrored on IOPscience and arXiv). No new
exposure was created by this probe: the string was already public in the benchmark repository.

**Exposure classification: HIGH / UNAVOIDABLE.** The query-to-answer mapping is itself a public,
indexable web document. A live-provider route can reach it. Any SAGE number obtained with live web
search is contaminated by construction and cannot support the headline claim; SAGE would have to be
run against a closed index with the repository excluded, and that closed index (the paper's
200,000-paper corpus) is not published — see `run_requirements_sources.md`.

## MetaSyn

`THUIR/MetaSyn` HuggingFace dataset is public and ungated, and `data/reviews/test-*.parquet` plus
`test_ids.json` are directly downloadable, so included-study lists are public. Not separately
probed by web search. **Exposure classification: CANNOT_CHECK (public artifact, contamination rate
not measured).**

## AgentSLR

`OxRML/AgentSLR` HuggingFace dataset is public, ungated, CC-BY-4.0, and carries screening and
extraction labels against PERG ground truth. Not separately probed by web search.
**Exposure classification: CANNOT_CHECK (public artifact, contamination rate not measured).**

## Bearing on the protocol

`JOURNAL_READINESS.md` section 3 requires "audit search-time contamination when benchmark
questions/answers are public" and "run an offline/controlled-index companion evaluation so
reproducibility does not depend entirely on mutable web results". These probes convert that from a
precaution into a requirement for SAGE specifically, where public indexing of the gold set is
established rather than hypothetical.
