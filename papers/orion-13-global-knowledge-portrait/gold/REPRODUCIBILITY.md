# ORION-13 Reproducibility Package

**Status:** PREPARED (not yet finalized — gold study not yet executed)

This document enumerates every artifact required to independently reproduce the ORION Paper III evaluation. The checklist is derived from the JOURNAL_READINESS.md Step 8 requirements.

## 1. Annotation artifacts

- [ ] **Annotation handbook:** `protocol/ANNOTATION_HANDBOOK_V1.md` — written before final labeling (DONE)
- [ ] **Annotation schema:** `protocol/ANNOTATION_SCHEMA_V1.json` — frozen taxonomy (DONE)
- [ ] **Adjudication policy:** `protocol/ADJUDICATION_POLICY_V1.md` — frozen before outcome inspection (DONE)
- [ ] **Gold annotations:** `gold/adjudicated/*.json` — adjudicated per-coordinate annotations for all 32 samples (PENDING — gold study not yet executed)
- [ ] **Inter-annotator agreement:** Per-coordinate agreement scores on the double-annotated subset (PENDING)

## 2. Source documents

- [ ] **Source manifest:** `gold/SAMPLE_MANIFEST_SEED_V1.json` — 32 structurally valid entries (DONE — SEED status)
- [ ] **Document identifiers:** DOI, arXiv ID, or PMID for every source (PENDING — final verification)
- [ ] **Legally shareable spans:** Short quoted spans for open-access documents; retrieval instructions for access-controlled sources (PENDING)
- [ ] **Text hashes:** SHA-256 hash of every annotated span (PENDING)

## 3. Evaluation artifacts

- [ ] **Gold evaluation records:** `evaluation/run-*/gold_results.jsonl` — normalized result records per run (PENDING)
- [ ] **Run manifests:** `evaluation/run-*/manifest.json` — gold hash, system versions, seeds, resource policy (PENDING)
- [ ] **Baseline configurations:** `src/orion/study/baselines.py` — 6 baseline implementations (DONE)
- [ ] **Ablation configurations:** `src/orion/study/ablations.py` — 9 ablation variants (DONE)
- [ ] **Raw system outputs:** `evaluation/run-*/raw/` — raw projections, mappings, portraits per system (PENDING)
- [ ] **System prompts:** All prompts used for each baseline and ablation (PENDING)
- [ ] **Model version:** deepseek-v4-pro (pinned) (DONE)

## 4. Evaluation pipeline

- [ ] **Evaluation runner:** `src/orion/study/evaluate.py` — deterministic output given gold + seeds (DONE)
- [ ] **Metrics:** `src/orion/study/metrics.py` — all 17 metrics (DONE)
- [ ] **Statistics:** `src/orion/study/statistics.py` — Wilson CI, bootstrap, Holm correction, effect sizes (DONE)
- [ ] **Plots/Tables:** `src/orion/study/plots.py` — 7 figures + 3 tables (DONE)
- [ ] **Tests:** `tests/unit/study/p3/` — 91 unit tests, all pass (DONE)
- [ ] **One-command evaluation:** `python -m src.orion.study.evaluate --gold gold/adjudicated --systems ORION_FULL,VanillaLongContext,ScientificRAG,CrossDomainRAG,FlatUniversalSchema,SCOPE_SCION_Like,ProvenanceSchema --seeds 5 --output evaluation/` (PENDING — gold study not yet executed)

## 5. Manuscript

- [ ] **Canonical manuscript:** `papers/orion-13-global-knowledge-portrait/manuscript/main.tex` — 8 sections (DONE)
- [ ] **Bibliography:** `papers/orion-13-global-knowledge-portrait/manuscript/bibliography.bib` — 20+ entries (DONE)
- [ ] **Claim ledger:** Every headline claim mapped to an artifact (PENDING — results section tied to frozen artifacts)

## 6. Data licensing

- [ ] **Gold annotations:** CC-BY 4.0
- [ ] **Source documents:** Open-access, CC-BY, or retrieval instructions (PENDING — final verification)
- [ ] **Code:** Same license as ORION codebase

## 7. Permanent archive

- [ ] **Zenodo/GitHub release:** DOIs for gold dataset and evaluation results (PENDING)
- [ ] **Pinned dependencies:** `requirements.txt` or `pyproject.toml` with pinned versions (PENDING)

## One-command path

Once the gold study is executed, the full evaluation can be reproduced with:

```bash
python -m src.orion.study.evaluate --gold gold/adjudicated --systems all --seeds 5 --output evaluation/
python -m src.orion.study.plots --input evaluation/ --output manuscript/figures/
```

The gold hash, system versions, and seeds are recorded in the run manifest for independent verification.