# Evaluator vs reference agent: layer check

Purpose: the v1 audit recorded the unpublished `deepxiv` paper-search backend as the hard blocker
for AutoResearchBench *official evaluation*. That was wrong. This file records the source checks
that establish the correction, performed `2026-08-16T18:07:00Z` against the pinned tarball of
`CherYou/AutoResearchBench@a46c9bfb8968786f73f0a6a5b365b5384cd0f96d` (tree
`8181218bf3da4b8be9a88a61ccd4c03d20760820`) and the locally decrypted bundle
(sha256 `db1839438033a32dd7d76913575d4b76f144d5e442aaac29be4eda32326392c6`).

## Check 1 — agent-only configuration never reaches the evaluator

```
$ grep -rnE 'PAPER_SEARCH|deepxiv|SERPER' evaluate/
  (no matches)

$ grep -rlnE 'PAPER_SEARCH|deepxiv|SERPER' . --include='*.py' --include='*.sh'
  ./run_inference.sh
  ./tool_websearch.py
  ./tool_deepxivsearch.py
  ./inference.py
```

`PAPER_SEARCH_API_URL`, `SEARCH_TOOL=deepxiv` and `SERPER_API_KEY` are inputs to the repository's
own reference agent. No file under `evaluate/` reads them. They block reproducing the authors'
baseline; they do not block scoring our system on their tasks.

The only credential reference under `evaluate/` is in the Deep scorer:

```
evaluate/evaluate_deep_search.py:41: DEFAULT_API_BASE = os.environ.get("EVAL_OPENAI_API_BASE", os.environ.get("OPENAI_API_BASE", ""))
evaluate/evaluate_deep_search.py:252: parser.error("--api-base is required. ...")
```

## Check 2 — the Wide scorer is credential-free

```python
def get_gt_arxiv_ids(input_data, use_jina: bool = True) -> Set[str]:
    raw_ids = input_data.get("arxiv_id", [])
    if raw_ids:
        normalized = {normalize_arxiv_id(str(raw_id)) for raw_id in raw_ids if raw_id}
        normalized.discard("")
        if normalized:
            return normalized
    if use_jina and JINA_API_KEY:
        ...
    return set()

def get_predicted_arxiv_ids(final_candidates) -> Set[str]:
    predicted = set()
    for candidate in final_candidates or []:
        normalized_id = normalize_arxiv_id(str(candidate.get("arxiv_id", "")))
        if normalized_id:
            predicted.add(normalized_id)
    return predicted

def compute_iou_recall(gt_ids: Set[str], pred_ids: Set[str]):
    ...
    intersection = len(gt_ids & pred_ids)
    union = len(gt_ids | pred_ids)
```

Three properties follow, each of which matters:

1. **Gold ids come straight from the record.** The Jina branch is guarded by
   `use_jina and JINA_API_KEY`; with no key set it is skipped and the function returns an empty
   set rather than raising. A `--no-jina` CLI flag disables it explicitly.
2. **Predictions are resolved locally.** `get_predicted_arxiv_ids` reads `candidate["arxiv_id"]`;
   there is no title-to-id lookup on the prediction side, so no network path exists at all.
3. **Scoring is pure set arithmetic.** `compute_iou_recall` is exact.

`main()` raises `SystemExit(1)` only for a missing `--input` file or missing `--gt` file. It never
errors on a missing credential.

## Check 3 — gold-id coverage in the decrypted bundle

Counted by normalising every `arxiv_id` entry the way `normalize_arxiv_id` does and discarding
empties:

| Task type | Records | With usable gold ids | Share |
| --- | --- | --- | --- |
| wide | 400 | 400 | 100% |
| deep | 600 | 540 | 90% |

The 60 uncovered deep records carry `arxiv_id == ['']`. So:

- **Wide** never reaches the Jina fallback for any task — credential-free scoring is not merely
  possible in principle, it is what happens on this data.
- **Deep** as shipped needs the LLM judge (it matches gold *titles* from `input_data["answer"]`).
  A deterministic id-match deviation is available for 540/600; the remaining 60 need the judge or
  a predeclared symmetric exclusion, and the 540/600 denominator must be reported rather than the
  60 quietly dropped.

Incidental gold-consistency note: two wide records have `len(arxiv_id) != len(answer)` (11 vs 10,
21 vs 20). Wide scores on id sets, so the extra id enlarges the gold denominator for those two
tasks. Not a blocker; recorded so it is not rediscovered as a surprise.

## Check 4 — the same layer error, checked for in MetaSyn

Rather than re-reading the README (the source of the original mistake), the import graph was read:

```
evaluation.py imports: __future__ re statistics collections typing
evaluator.py  imports: __future__ hashlib datetime typing
retrieval.py  imports: __future__ json pathlib typing faiss numpy datasets sentence_transformers
sparse.py     imports: __future__ re typing numpy datasets rank_bm25
judge.py      imports: __future__ numpy sentence_transformers
rag.py        imports: __future__ os re unicodedata typing openai
```

Only `rag.py` touches an LLM. MetaSyn's `judge.py` is an *embedding* scorer, not an LLM judge.
`scripts/run_retrieval.py` contains no LLM reference, and `scripts/evaluate.py` declares
`--judge-model` without `required=True`. So the `metasyn_retrieval_screening` family the protocol
names scores without credentials; only the generated-report metrics need a key.

## Why the first pass got it wrong

The v1 audit read `example.env`, saw every credential slot the repository defines in one file, and
attributed all of them to "running the benchmark". `example.env` is shared by the agent and the
evaluator, so the file does not distinguish the layers — but the code does. The correct unit of
analysis is which module reads which variable, not which variables the project declares.

## Check 5 — the Wide scorer was actually executed, with no credentials

Reading code establishes that no credential is required; running it establishes that nothing else
breaks. A synthetic inference file was built from three real wide records (gold sizes 20, 21, 6)
with one perfect, one partial-plus-false-positive and one empty prediction, then scored with every
relevant variable unset:

```
$ env -u JINA_API_KEY -u OPENAI_API_KEY -u SERPER_API_KEY -u EVAL_OPENAI_API_KEY \
      -u PAPER_SEARCH_API_URL -u OPENAI_API_BASE \
  python3 evaluate_wide_search.py --input synthetic_wide_inference.jsonl --output out.json
exit=0
avg_iou 0.484848   avg_recall 0.492063   avg_precision 0.636364
```

Hand-check of the exact metrics, which match: record 1 gold 20 / pred 20 -> IoU 1.0; record 2 gold
21 / pred 11 of which 10 correct -> 10/22 = 0.4545 IoU, 10/21 = 0.476 recall, 10/11 = 0.909
precision; record 3 gold 6 / pred 0 -> 0. Means 0.4848 / 0.4921 / 0.6364.

**This is a self-test of the scorer on synthetic input. It is not a result for any system, and no
ORION or baseline output was scored.**

## Check 6 — the sampling nondeterminism, measured at the protocol's 3 repeats

A first attempt used one pass per record and produced identical `avg_max_iou_at_1` across runs.
That is not evidence of determinism: with a single pass, `random.sample(list_of_1, 1)` can only
return one value. The residual gap to `avg_iou` there (0.484833 vs 0.484848) is the function's
internal `round(..., 4)`, not sampling.

Re-run with three passes per record, matching `statistics.stochastic_repeats: 3`, five identical
invocations:

| Run | `avg_iou` (exact) | `avg_max_iou_at_1` | `avg_max_iou_at_2` | `avg_max_iou_at_4` |
| --- | --- | --- | --- | --- |
| 1 | 0.52672 | 0.521167 | 0.822500 | 0.0 |
| 2 | 0.52672 | 0.515367 | 0.824567 | 0.0 |
| 3 | 0.52672 | 0.519233 | 0.828867 | 0.0 |
| 4 | 0.52672 | 0.512767 | 0.835167 | 0.0 |
| 5 | 0.52672 | 0.519667 | 0.834700 | 0.0 |

Three things are now measured rather than inferred:

1. `avg_iou`, `avg_recall` and `avg_precision` are bit-identical across runs — exact metrics.
2. `avg_max_iou_at_1` and `at_2` vary run to run on identical input, with an observed spread of
   about 0.008 and 0.013 respectively on a [0,1] scale.
3. `avg_max_iou_at_4/_8/_16` are 0.0 because `len(record_ious) >= k` never holds at 3 passes. They
   are not measurements and must not be tabulated as scores.

Point 2 has a direct bearing on the design: `PROTOCOL_V1.json` `statistics.practical_margin` sets a
target of +0.03 absolute. Run-to-run noise of ~0.01 on the `at_k` family is a third of the effect
the study intends to detect, from re-running the scorer alone with no change to any system. Use
`avg_iou`/`avg_recall` as the primary Wide metric, or seed the sampler and bind the seed in the run
manifest.
