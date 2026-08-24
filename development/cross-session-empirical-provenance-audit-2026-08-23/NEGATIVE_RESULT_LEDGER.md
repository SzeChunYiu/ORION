# Negative-result ledger

**Terminal:** `CROSS_SESSION_EMPIRICAL_PROVENANCE_AUDIT_P1_P3_COMPLETE__NO_RECORD_PROMOTED__TOP_TIER_EMPIRICAL_CLAIMS_CANNOT_CHECK`

## XPA01_SOURCE_HEAD_AND_UNTRACKED_BINDING
- **Status:** `CANNOT_CHECK`
- **Observed:** Parent observed b55f553b7b16b488cf4c515ba286578783a5fd83; audit ran stably at 8d6d5992a9f0e2b93254ed441b88ea0b5e61644b, one descendant commit later. All 9 selected tracked files are identical between those heads, but the candidate empirical files are untracked.
- **Hazard:** Untracked artifacts are not bound by either commit and can change independently of the source tree.
- **Admissible residual:** Tracked source interpretation is stable across the two heads.
- **Next discriminator:** Freeze the exact evidence files in a content-addressed archive with clean source commit/tree, generator/runner hashes, and immutable manifest.

## XPA02_P1_PILOT_DIRTY_UNTRACKED
- **Status:** `CANNOT_CHECK`
- **Observed:** pilot_runs.jsonl and pilot_scored.jsonl contain 990 unique case-system-seed rows each, are untracked, and declare subject_revision 55f0bc766f2242ca6fffd729f3f44c01168f663d+dirty; 0/990 pilot raw rows report nonzero model tokens.
- **Hazard:** The exact dirty source state and any unstaged implementation differences cannot be reconstructed.
- **Admissible residual:** Grid completeness and hidden-suite fingerprint are exact audit facts.
- **Next discriminator:** Rerun the pilot from a clean immutable revision, bind diff=empty, runner hash, suite fingerprint, raw archive hash, and resource receipt.

## XPA03_P1_CONSTRUCT_SCOPE
- **Status:** `CANNOT_CHECK_NATURALISTIC_ACTION`
- **Observed:** All four P1 files are P1.hidden-formulation.v1 hidden-shift/control harness outputs: 990 pilot rows and 2,880 test rows. The test contains 240 live-provider rows and 289,261 model tokens, but they remain hidden-formulation cases.
- **Hazard:** Hidden-formulation performance cannot be relabeled as naturalistic P1 V2/V3 postpublication-action semantics, action gold, transport, or owner authority.
- **Admissible residual:** The two tracked test files remain admissible only for their historical hidden-formulation harness claim.
- **Next discriminator:** Prospectively freeze and execute a rights-valid naturalistic P1 study with owner-separated action adjudication and independently held outcome/gold.

## XPA04_P3_PLACEHOLDER_SOURCES
- **Status:** `CANNOT_CHECK_REAL_SOURCE_VALIDITY`
- **Observed:** All 64 source references have SEED document IDs and seed:sha256 placeholders; 0 are valid 64-hex content hashes. There are 63 unique placeholders with 1 duplicate excess. Tracked combined-gold source text matches its declared hash in 0/64 references.
- **Hazard:** No real open-access document identity, exact source span, text integrity, retrieval provenance, or rights binding exists.
- **Admissible residual:** The 32 synthetic coordinate templates match tracked combined_gold structurally.
- **Next discriminator:** Replace all 64 placeholders with verified public document/version/span records, exact SHA-256 of retained licensed text, retrieval receipts, and rights evidence.

## XPA05_P3_ANNOTATOR_INDEPENDENCE
- **Status:** `CANNOT_CHECK_INDEPENDENT_AGREEMENT`
- **Observed:** 32 files are annotator-a only, 0 annotator-b files exist, and all declare adjudicated-v1. The tracked freeze explicitly says independent_labels_exist=false and coordinate_agreement_computable=false.
- **Hazard:** System-gold agreement cannot substitute for independent human inter-annotator agreement or blind adjudication.
- **Admissible residual:** One adjudicated synthetic template exists per sample.
- **Next discriminator:** Obtain two independent blind labels on a preregistered substantial shared subset, compute coordinate-wise agreement with uncertainty, then adjudicate disagreements.

## XPA06_P3_GOLD_HASH_MISMATCH
- **Status:** `CANNOT_CHECK_EXACT_GOLD`
- **Observed:** run-full MANIFEST gold_hash is 667be9620944abba078dca442c1283baec59a14989fbdf5761137a7cd11e5c8a, but the current and parent-observed tracked combined_gold byte SHA-256 is 778168a5c05da95464f76b877762c1f9da19f41a8ee5dcc28ac65aca58471e7e; match=false.
- **Hazard:** The exact gold file used for the run is not the tracked gold now available, so scores cannot be independently reconstructed from the declared input.
- **Admissible residual:** The manifest and current gold are each content-addressed separately.
- **Next discriminator:** Retain the exact gold bytes matching the manifest hash or rerun against the tracked gold and bind the new byte hash.

## XPA07_P3_SYNTHETIC_RAW_HASH_AND_STUB_PASS
- **Status:** `CANNOT_CHECK_RAW_EXECUTION`
- **Observed:** All 75 raw_artifact_hash values are valid hex but all 75/75 equal SHA256(system_id|seed), not a retained raw output. ORION_FULL has 5 PASS rows while the bound tracked evaluator contains ORION_FULL_NOT_YET_BOUND.
- **Hazard:** PASS and raw hash fields do not prove that a model/backend ran or that model outputs were retained.
- **Admissible residual:** The 15-system x 5-seed result-record grid is structurally complete.
- **Next discriminator:** Bind an actual ORION backend, retain immutable raw outputs, hash those bytes, record provider/model/revision, and fail closed if the backend is unbound.

## XPA08_P3_COST_INVALID
- **Status:** `CANNOT_CHECK_COST`
- **Observed:** All 75 result rows report zero wallclock, model tokens, tool calls, and currency cost; all 75 have cost_metrics_error=-1. AST audit finds cost_metrics declares one positional parameter while the dispatcher calls every metric with two.
- **Hazard:** The run cannot support cost, efficiency, latency, or resource-normalized claims; -1 is an error sentinel, not a favorable cost.
- **Admissible residual:** The exact failure is localized to a reproducible signature mismatch and hard-coded zero metadata path.
- **Next discriminator:** Repair the cost metric interface, capture measured resources per case/run, require error absence and nonnegative receipts, then rerun.

## XPA09_P3_CHECKPOINT_DUPLICATE_EXCESS
- **Status:** `CANNOT_CHECK_DEDUPLICATED_METRICS`
- **Observed:** Final checkpoint has 3340 rows for 2400 unique keys: 940 excess rows across 683 duplicate keys; all 683 duplicate keys conflict, exact duplicate excess is 0, and max multiplicity is 7. Pre-retry has 2720 rows, 2328 unique keys, and 392 excess; final adds 72 previously missing keys.
- **Hazard:** The analyzer silently uses a dictionary keyed by case_id, so later conflicting retry rows overwrite earlier predictions without a frozen attempt-selection rule.
- **Admissible residual:** The final key set covers exactly 15 systems x 32 cases x 5 seeds = 2,400 keys.
- **Next discriminator:** Freeze attempt IDs and a prospective winner rule, retain one selected row/key plus a rejection receipt for every discarded attempt, then recompute from a duplicate-free checkpoint.

## XPA10_P3_PARTIAL_ANALYSIS
- **Status:** `CANNOT_CHECK_COMPLETE_ANALYSIS`
- **Observed:** analysis/aggregates.json has 0 systems; metrics_by_system_seed.json contains only ['ORION_FULL', 'VanillaLongContext'] with seed counts {'ORION_FULL': 1, 'VanillaLongContext': 1}.
- **Hazard:** The analysis directory does not represent the 15-system x 5-seed full checkpoint and cannot support registered hypotheses.
- **Admissible residual:** Partial files are hashable diagnostics only.
- **Next discriminator:** After duplicate repair, regenerate all per-system/seed metrics, aggregates, hypotheses, and report tables from the frozen checkpoint in one content-addressed derivation.

## XPA11_P3_RESULT_CHECKPOINT_DISCONNECTION
- **Status:** `CANNOT_CHECK_DERIVATION`
- **Observed:** run-full results contain 75 system-seed records, while checkpoint contains 3340 prediction rows. Result raw hashes bind only system_id|seed and the partial analyzer has not emitted a complete derivation receipt.
- **Hazard:** No immutable mapping proves which selected checkpoint row produced each metric in results.jsonl or aggregates.json.
- **Admissible residual:** Both layers have exact independent hashes and counts.
- **Next discriminator:** Emit a derivation manifest binding gold hash, duplicate-free checkpoint hash, selected row hashes, analyzer hash, metric configuration, and every result/aggregate hash.

## XPA12_P3_RESOURCE_POLICY_UNBOUND
- **Status:** `CANNOT_CHECK_MATCHED_RESOURCES`
- **Observed:** run-full resource_policy freezes model family=deepseek-v4-pro but leaves context_budget_per_case=TBD and retrieval_allowance=TBD; no source revision is bound.
- **Hazard:** Matched resource budgets, retrieval access, and implementation identity cannot be checked across systems.
- **Admissible residual:** The system and seed lists are explicit.
- **Next discriminator:** Freeze numeric context/retrieval/tool budgets, provider/model versions, source commit/tree, and enforce them with per-run receipts.
