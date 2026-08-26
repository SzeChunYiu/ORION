# Run-requirement source excerpts (verbatim, at pinned revisions)

Every `run_requirements` field in `../../protocol/EXTERNAL_ACCESS_AUDIT_V1.json` is sourced here.
Fetched `2026-08-16T17:35Z–17:39Z` via `gh api repos/<owner>/<repo>/contents/<path>?ref=<pinned sha>`
with `Accept: application/vnd.github.raw`.

## AutoResearchBench — `CherYou/AutoResearchBench@a46c9bfb`

`example.env` (899 bytes) declares these credential slots, all empty in the template:

```
MODEL=
OPENAI_API_KEY=
OPENAI_API_BASE=
SEARCH_TOOL=deepxiv
MAX_TURNS=10
K_PASSES=1
EVAL_MODEL=
EVAL_OPENAI_API_KEY=
EVAL_OPENAI_API_BASE=
EVAL_MAX_WORKERS=100
PAPER_SEARCH_API_URL=
PAPER_SEARCH_OPENAI_API_KEY=
PAPER_SEARCH_OPENAI_API_BASE=
PAPER_SEARCH_SUMMARY_MODEL_NAME=
SERPER_API_KEY=
JINA_API_KEY=
WEB_SEARCH_OPENAI_API_KEY=
WEB_SEARCH_OPENAI_API_BASE=
WEB_SEARCH_SUMMARY_MODEL_NAME=
```

`requirements.txt` (108 bytes): `aiohttp, cryptography, numpy, openai, python-dateutil,
python-dotenv, qwen-agent, requests, soundfile, tiktoken, tqdm`.

`evaluate/evaluate_deep_search.py` — LLM-judge evaluator:

- `class LLMJudge` with `are_titles_matching(gt_title, candidate_title, semaphore)`;
- `DEFAULT_MODEL_NAME = os.environ.get("EVAL_MODEL", os.environ.get("MODEL", ""))`;
- `parser.error("--model is required. Set it explicitly or provide EVAL_MODEL / MODEL in .env.")`
  — the deep evaluator refuses to run without a judge model;
- `--max-workers` default `20` (concurrent judge requests);
- scoring loop issues one judge call per `(ground_truth_title x candidate_title)` pair;
  `Evaluator.max_candidates_per_pass` defaults to `1`.

`evaluate/evaluate_wide_search.py` — deterministic, **no LLM judge**: `compute_iou_recall`
over ground-truth vs predicted id sets, plus `max_iou_at_k_sampling` for
`avg_max_iou_at_{1,2,4,8,16}`. It uses `random.sample` without a seed argument in
`max_iou_at_k_sampling(..., sample_times=1000)`.

`evaluate/run_evaluate.sh` dispatches `deep` -> `evaluate_deep_search.py`,
`wide` -> `evaluate_wide_search.py`, sourcing `.env`.

**Blocker of record:** `PAPER_SEARCH_API_URL` is blank in the template and the default
`SEARCH_TOOL=deepxiv` resolves to `tool_deepxivsearch.py`, which calls an endpoint that the
repository does not publish. Reproducing the official inference route therefore requires a
paper-search backend that is not distributed with the benchmark, in addition to the agent LLM
key, the judge LLM key, and Serper/Jina web-search keys.

## SAGE — `HughieHu/Sage@bc62257a`

Whole tree at the pinned commit is 11 entries: `README.md` plus eight query JSON files under
`Sage_Short_Form_Questions/` and `Sage_Open_Ended_Questions/`. There is no evaluator script, no
`requirements.txt`, no corpus and no license file.

`README.md` specifies the metrics in prose only:

> **Short-Form**: Exact Match — whether the retrieved paper matches the ground truth
> **Open-Ended**: Weighted Recall — recall across relevance tiers with decreasing weights

The "decreasing weights" are not numerically specified anywhere in the repository, so an
independent implementation cannot reproduce the official open-ended metric exactly.

The paper (arXiv:2602.05975) states the benchmark comprises "1,200 queries across four
scientific domains, with a 200,000 paper retrieval corpus". Scanning the paper HTML for
`huggingface.co | github.com | zenodo.org | figshare` URLs returns only
`https://github.com/HughieHu/Sage` (plus arXiv/LaTeXML/pdfplumber/pymupdf infrastructure links).
The corpus is not published at any linked location, and a HuggingFace dataset search for
`Sage scientific literature retrieval` returned zero matching datasets.

## MetaSyn — `THUIR/MetaSyn@51b95b70`

`.env.example` (72 bytes):

```
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=
```

`pyproject.toml`: `requires-python = ">=3.10,<3.12"`; pinned dependencies
`datasets==3.0.0, faiss-cpu==1.8.0, numpy==1.24.4, openai==1.46.1, python-dotenv==1.0.1,
rank-bm25==0.2.2, sentence-transformers==3.2.1, torch==2.3.1, transformers==4.43.1`.

`README.md`: shared corpus of `140,585` PubMed articles; `--judge-model gpt-5.5` appears in the
documented evaluation invocations; report metadata records "dataset ID and revision, judge model,
report hash, and API token usage"; "Exhausted API retries or invalid judge responses produce
`status: failed`". Retrieval uses the `BFTree/MA-Retriever` HuggingFace model (`torch` +
`sentence-transformers`, i.e. local encode of ~140k articles).

## AgentSLR — `OxRML/AgentSLR@3111fcf4`

`requirements.txt` (143 bytes): `pandas, requests, lxml, urllib3, tqdm, openai, scikit-learn,
matplotlib, numpy, seaborn, reportlab, cartopy, plotly, vllm, mistralai, huggingface_hub, pyarrow`.

`README.MD` "API Keys And Config" section names:

```
"openai_api_key": "your-openai-api-key",
"openrouter_api_key": "your-openrouter-api-key",
"mistral_api_key": "your-mistral-api-key"
export OPENAI_API_KEY="..."
export OPENALEX_API_KEY="..."
export NCBI_API_KEY="..."
export MISTRAL_API_KEY="..."
```

Pipeline stages per `README.MD` line 25: "download article metadata and labels, retrieve
available full-text PDFs, run abstract screening, OCR, full-text screening, extraction and
write-up stages, then evaluate generated artefacts against PERG ground truth".

Verbatim redistribution-relevant sentence, `README.MD` line 154:

> The Hugging Face dataset contains article metadata, screening labels and extraction labels. It
> does not redistribute the article PDFs. Download the dataset files first, convert them into the
> harness layout, then run the PDF download stage.

The full-text screening / OCR / extraction stages therefore depend on PDFs that must be fetched
from publishers at run time and are not part of any frozen snapshot.
