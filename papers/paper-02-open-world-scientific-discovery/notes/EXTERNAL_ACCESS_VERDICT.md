# P2 external access verdict

Record: `../protocol/EXTERNAL_ACCESS_AUDIT_V1.json`. Table: `../protocol/TABLE_P2-1_freeze_manifest.md`
(generated). Logs: `../evidence/access/`. Window `2026-08-16T17:33Z`-`17:46Z`.

## No P0 on the pins

All four 40-character SHAs in `PROTOCOL_V1.json` `reference_revisions` resolve at their named
repositories, and all four repositories are public and unarchived.

| Artifact | State | Consequence |
| --- | --- | --- |
| AutoResearchBench code | `OBTAINED`, Apache-2.0 | Blocked on credentials + an unpublished search backend |
| AutoResearchBench dataset | `OBTAINED`, Apache-2.0 | In hand, decrypted, hash-verified |
| SAGE | `AVAILABLE_LICENSE_BLOCKED` | Cannot be run at all; cannot be redistributed |
| MetaSyn code + dataset | `OBTAINED`, MIT / partial-MIT | Best candidate; blocked only on an LLM key |
| AgentSLR code | `AVAILABLE_LICENSE_BLOCKED` | Code unlicensed; its dataset is separately CC-BY-4.0 |
| ResearchArena, OpenScholar | `CANNOT_CHECK` | Cited as nearest work, pinned nowhere |

## Nothing is runnable here, for three different reasons

**SAGE is structurally unrunnable.** Its 200,000-paper corpus is claimed in arXiv:2602.05975 and
published nowhere - the only artifact URL in the paper is the GitHub repository, whose pinned tree
is 777 KB of queries. Nor is there an evaluator: the metrics are two prose sentences and the
open-ended "decreasing weights" are never given numerically. No budget fixes this.

**AutoResearchBench and AgentSLR are execution-blocked.** AutoResearchBench needs an agent key, a
judge key, Serper and Jina keys, and a paper-search backend whose URL the repo leaves blank
(`PAPER_SEARCH_API_URL=`, `SEARCH_TOOL=deepxiv`). AgentSLR needs OpenAI/OpenRouter/Mistral keys or
a local GPU vLLM, plus publisher PDFs its own dataset states it does not redistribute. Both are
operator-unblockable in principle; neither by this lane.

**MetaSyn is closest to runnable.** MIT, dataset public and ungated, retriever public, and only the
report-quality metrics need a key. If exactly one external family is attempted, it is this one.

## Redistribution is a Section-8 problem, not a runnability one

SAGE and AgentSLR carry no licence at any depth of their pinned trees (`GET /repos/.../license`
-> 404; full recursive tree, `truncated=false`, no `LICENSE`/`COPYING`/`NOTICE`; no inline terms in
either README), so default copyright applies. That blocks "frozen corpora/index snapshots where
redistribution permits" for those two; it does not stop reading them in place. Do not read the
AgentSLR *code* finding across to the AgentSLR *dataset*, which is CC-BY-4.0.

## Three findings the protocol should absorb

**Hidden labels are not inherited.** Decrypted AutoResearchBench records carry `answer` and
`arxiv_id` in the same object as `question`, so `access_policy.hidden_labels` must be enforced by
the ORION harness splitting the file before the candidate sees it.

**SAGE contamination is by construction.** Its gold set is public plaintext, question and answer in
one public GitHub record. A verbatim search on one `ground_truth.title` returned the exact target
paper as the top hit. Any live-provider SAGE number is contaminated, and the closed index that
would fix it is the corpus that does not exist.

**Part of the Wide metric is unseeded.** `max_iou_at_k_sampling` draws `random.sample` 1000 times
with no seeding anywhere in the evaluator, so `avg_max_iou_at_k` is a Monte-Carlo estimate: an
`evaluator_hash` pins the code but not the value. At `stochastic_repeats=3` only `at_1` and `at_2`
receive samples at all; `at_4`, `at_8` and `at_16` report 0.0 rather than a measurement.

## Consequence for issue #99 Step 3

Closed here: benchmark licences and access notes (Section 8, first line), with sources; Table P2-1,
generated from records; `reference_revisions` integrity, four for four.

Becomes `CANNOT_CHECK`, with reasons on the record rather than silence: AutoResearchBench Deep and
Wide with official evaluation (credentials + unpublished backend); MetaSyn retrieval and screening
(LLM key); an AgentSLR-like protocol-driven SLR baseline (keys + non-redistributable PDFs); and
contamination *rates* for every benchmark, since only structural exposure and two spot checks were
performed.

Struck rather than deferred: SAGE scientific retrieval - no corpus, no evaluator, at any price.

## The honest consequence

The external open-world discovery claim stays `CANNOT_CHECK`. Nothing in this lane can promote it,
and for SAGE nothing can promote it at all in its official form. Mechanism evidence for H1-H4 must
therefore be carried by the offline controlled-index companion - the frozen local complete-gold
corpus with a legally distributable denominator. That companion is not a fallback: given SAGE's
public gold and AutoResearchBench's key-less obfuscation, it is the only denominator in this suite
whose contamination status the host actually controls.
