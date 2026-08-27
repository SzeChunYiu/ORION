# SCIFACT_LABEL_STATE_MAP_V1 — frozen label-to-state adapter

- **Canonical artifact:** `SCIFACT_LABEL_STATE_MAP_V1.json` (same directory). This file is the
  prose protocol; where wording differs, the JSON is authoritative.
- **Frozen (UTC):** 2026-08-24T10:10:46Z
- **Freeze status:** FROZEN_BEFORE_ANY_SCIFACT_SCORING (`outcome_accessed: false`; zero SciFact
  outcome artifacts exist under `papers/orion-14-verified-scientific-discovery/evidence/` at freeze
  time).
- **Issue:** SzeChunYiu/ORION#1086 (ORION-14 boxes 1 and 3).
- **Checker:** `check_scifact_label_state_map_v1.py` (importable, `run(path) -> int`; distinct
  exit codes for FAIL vs CANNOT_CHECK). **Tests:** `tests/unit/p4/test_p4_scifact_label_state_map.py`.

## 1. Purpose and authority boundary

This map is the **only** sanctioned adapter from external SciFact gold labels into ORION-14
semantic-support and authority-terminal states. It is frozen **before** any SciFact scoring so
that label semantics cannot be tuned to outcomes. It is an adapter, not an adjudicator: it
creates no external scientific authority and performs no adjudication of its own.

## 2. Source binding

| Item | Value |
|---|---|
| Dataset | `allenai/scifact` @ `68b98a56d93e0f9da0d2aab4e6c3294699a0f72e` (ORION-pinned revision, `PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json`, frozen 2026-08-17) |
| Claims + annotations license | CC BY 4.0 |
| Abstracts | ODC-By 1.0 via S2ORC upstream terms; no full-text redistribution assumption |
| Code | Apache-2.0 |
| Official evaluator | `allenai/scifact-evaluator` — **NOT_EXECUTED_IN_THIS_FREEZE** |

## 3. Label vocabulary

SciFact expresses per-evidence-document labels `SUPPORT`/`REFUTE` and the derived claim verdict
`SUPPORT`/`REFUTE`/`NOT_ENOUGH_INFO`. No other external label may enter the semantic-support
coordinate. The ORION-14 side uses semantic states `SUPPORTED`/`CONTRADICTED`/`INSUFFICIENT`/`UNRESOLVED`
and terminals `PROMOTE`/`BLOCK`/`CANNOT_CHECK` (`ATTACK_CASE_SCHEMA_V1.json`).

## 4. Frozen mapping

| SciFact label | ORION-14 semantic support | Terminal rule |
|---|---|---|
| `SUPPORT` | `SUPPORTED` | `PROMOTE_ELIGIBLE__CONDITIONAL_FAIL_CLOSED` — PROMOTE only if ALL promotion obligations discharged; any unresolved obligation → `CANNOT_CHECK`; never `BLOCK` |
| `REFUTE` | `CONTRADICTED` | `BLOCK_DECISIVE` — maps to `BLOCK` directly; not subject to obligation-based upgrade |
| `NOT_ENOUGH_INFO` | `INSUFFICIENT` | `CANNOT_CHECK_FAIL_CLOSED` |

Promotion obligations (all required for `SUPPORT` → `PROMOTE`): claim scope conformance, evidence
independence, scientific authority resolution, provenance/artifact/version binding, evaluator
custody, contamination defense, evaluation epoch freshness.

**UNRESOLVED policy:** no SciFact label maps to `UNRESOLVED`. `UNRESOLVED` is reserved for
ORION-internal states where the external label itself cannot be read; such transport failures
take terminal `CANNOT_CHECK`.

## 5. Claim-verdict composition (evidence rows → claim verdict)

Applied in order:

1. **contradiction_dominates** — any gold evidence `REFUTE` ⇒ claim verdict `REFUTE`.
2. **support_requires_no_contradiction** — `SUPPORT` only if ≥1 `SUPPORT` evidence and zero `REFUTE`.
3. **empty_evidence_is_insufficient** — empty gold evidence set ⇒ `NOT_ENOUGH_INFO`.

## 6. Crossref / Retraction Watch constraint (ORION-14 box 3)

Crossref/RW is **coordinate-only, never semantic adjudication**. Allowed uses are exactly:

1. `DOI_METADATA_UPDATE` — resolve/update the canonical DOI identifier and deposit metadata.
2. `EVALUATION_EPOCH` — record the snapshot date that stamps when conformance was measured.
3. `REVOCATION_CONFORMANCE` — check whether a cited evidence DOI carries an active retraction.

Forbidden: semantic support adjudication, claim/label alteration, gold substitution, comparator
construction/tuning, evidence substitution or recall augmentation, any change to a SciFact-derived
semantic-support coordinate.

Conformance rules:

- **Active retraction on a gold-evidence DOI** ⇒ `revocation_nonconformant`, forced terminal
  `BLOCK`, recorded as `REVOCATION_BLOCK` — a revocation-coordinate failure, kept distinct from
  semantic `CONTRADICTED`.
- **No retraction observed** clears the revocation coordinate only; it never upgrades semantic
  support.
- **Stale promotion rule:** on exact DOI-update and epoch-change cases the terminal must be
  computed against the frozen evaluation epoch. A promotion justifiable only by the pre-update DOI
  state or a superseded epoch is a **stale promotion**, counts as a false promotion, and must
  occur zero times.
- **Snapshot recording:** before any scoring run the Crossref/RW snapshot date and terms must be
  recorded in the JSON (`snapshot_requirements`); currently `CANNOT_CHECK__NOT_YET_RECORDED`. A
  run without a recorded snapshot is non-conformant to this map.

## 7. Arms and analysis freeze

- **Inference unit:** the SciFact claim (identifier-level). Evidence rows are nested within claims
  and are never independent units; bootstrap intervals are paired over claim identifiers.
- **Required arms:** `full_policy`, `strongest_runnable_baseline`, `component_ablations`. An arm
  that cannot be executed is recorded `CANNOT_CHECK`; weak proxies are never substituted.
- **Held-out rule:** scoring uses held-out claims only; this map froze before any held-out label
  was opened.
- **Pass gates:** macro-F1 improvement over strongest ablation ≥ 0.03 with paired lower CI > 0;
  false promotion rate ≤ 0.01; evidence/rationale F1 noninferior within 0.02; zero stale
  promotions on exact DOI-update/epoch cases.
- **External boundary:** SciFact labels validate claim/evidence status; ORION's governance action
  is an operationalization, not independent policy truth.

## 8. Non-bypass boundaries

1. This map is an adapter frozen before scoring; it creates no external adjudication and no
   scientific authority.
2. No SciFact outcome file existed in this repository at freeze time; any future outcome artifact
   must carry a creation timestamp after `frozen_utc`.
3. Changing any mapping row, composition rule, Crossref/RW constraint, or pass gate after the
   first SciFact scoring artifact appears is a protocol violation and requires a new versioned map
   with a new identity.
