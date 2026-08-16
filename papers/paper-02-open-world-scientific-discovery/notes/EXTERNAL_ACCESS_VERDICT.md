# P2 external access verdict

Record: `../protocol/EXTERNAL_ACCESS_AUDIT_V1.json` (revision 2). Table:
`../protocol/TABLE_P2-1_freeze_manifest.md` (generated). Logs: `../evidence/access/`.

> **Revision 2 supersedes the first verdict on AutoResearchBench and MetaSyn.** Revision 1 said the
> unpublished `deepxiv` backend blocked AutoResearchBench official evaluation. It does not — it
> blocks only the authors' *reference agent*. Both benchmarks are more runnable than first reported.
> The error and the corrected evidence are in
> `../evidence/access/autoresearchbench_evaluator_layer_check.md`. SAGE is unchanged.

## Can the official scorers actually be run?

No P0 on the pins: all four 40-character SHAs in `reference_revisions` resolve at their named
repositories, and all four repositories are public and unarchived.

| Task family | Official scorer | Cost to us |
| --- | --- | --- |
| `autoresearchbench_wide` | `YES_NO_CREDENTIALS` | none — **executed during this audit** |
| `autoresearchbench_deep` | `YES_WITH_JUDGE_KEY` | one judge endpoint; id-match deviation covers 540/600 |
| `metasyn_retrieval_screening` | `YES_NO_CREDENTIALS` | local compute for the corpus encode |
| `sage_scientific_retrieval` | `NO_ARTIFACT_MISSING` | unfixable at any price |

**Wide is the headline.** `compute_iou_recall` is pure set arithmetic over gold arXiv ids;
`get_gt_arxiv_ids` reads them from the record and touches Jina only `if use_jina and JINA_API_KEY`;
predictions resolve locally. All 400 of 400 wide records carry usable gold ids, so the fallback is
never reached. Verified by running it: with every credential variable unset the scorer exits 0 and
returns metrics that reproduce by hand.

**Deep** matches gold *titles*, so it needs a judge as shipped; the deterministic id-match deviation
is partial (540 of 600 records carry a usable id, 60 carry `arxiv_id ['']`) and must report the
540/600 denominator rather than quietly drop 60. **MetaSyn** is more runnable than revision 1 said:
`evaluation.py`, `evaluator.py`, `retrieval.py` and `sparse.py` import no LLM client and `judge.py`
is an *embedding* scorer; only `rag.py` touches OpenAI and `--judge-model` is optional. **SAGE is
unchanged and unrunnable** — corpus published nowhere, no evaluator, open-ended weights never stated
numerically; strike `sage_scientific_retrieval`. **AgentSLR** stays key- and PDF-bound, but it is a
baseline, not a protocol task family.

## What the adapter lane must honour

**An output contract, not just a credential.** `get_predicted_arxiv_ids` reads
`candidate['arxiv_id']` from each `final_candidates` entry. A system emitting titles only scores
IoU 0.0 on every task. Attach a resolved arXiv id to every returned candidate.

**Use the exact metrics.** Five identical runs at three passes per record: `avg_iou` was 0.52672
every time, while `avg_max_iou_at_1` ranged 0.512767–0.521167 and `at_2` ranged 0.822500–0.835167 —
~0.008–0.013 run-to-run noise on a [0,1] scale from re-running the scorer alone, roughly a third of
the +0.03 `practical_margin`. Use `avg_iou`/`avg_recall`, or seed the sampler and bind the seed.
`at_4/_8/_16` report 0.0 at 3 repeats because they receive no samples: absent measurements, never
scores. **Their baseline agent is not reproducible**, so it cannot be one of our matched baselines; ours are
unaffected and score against the same official scorer.

## Three findings the protocol should absorb

**Hidden labels are not inherited.** Decrypted AutoResearchBench records carry `answer` and
`arxiv_id` in the same object as `question`, so `access_policy.hidden_labels` must be enforced by
our harness splitting the file before the candidate sees it.

**SAGE contamination is by construction** — gold is public plaintext in the same record as the
query; a verbatim `ground_truth.title` search returned the exact target as top hit.
**Wide contamination is specific, not generic.** Gold is a list of real arXiv ids and our routes are
the arXiv and OpenAlex APIs, so a route can return the benchmark's own artifacts —
arXiv:2604.25256, its GitHub repo, its HuggingFace dataset page — as an ordinary result and hand a
candidate the answer key. Scan route logs for those three identifiers per query.

Redistribution stays a Section-8 problem (SAGE and AgentSLR are unlicensed at any tree depth, so no
frozen snapshot of them can ship — their datasets differ; see Table P2-1).

## Consequence for issue #99 Step 3

Closed: licences and access notes; Table P2-1 generated from records; pinned-revision integrity; and
— newly — **AutoResearchBench Wide official evaluation is executable here**, which revision 1
wrongly reported as blocked. Still `CANNOT_CHECK` pending execution: Deep (judge key), MetaSyn
(compute), AgentSLR (keys + PDFs), and contamination *rates* everywhere. Struck: SAGE.

The external discovery claim is no longer blocked at the access layer for Wide — it is now a
question of running the study, not of obtaining the means. The offline controlled-index companion
remains necessary (the one denominator whose contamination status we control, and SAGE's only
option) but it is no longer the sole route to external evidence.
