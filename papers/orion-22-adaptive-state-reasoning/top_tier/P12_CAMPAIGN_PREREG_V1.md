# P12 stop/go campaign preregistration V1 — families, difficulty prior, splits, repeat policy

**Artifact class:** FROZEN PROTOCOL — NO RESULTS. Nothing here is evidence of
any empirical outcome; every execution flag in the machine twin is false.

- **Machine twin:** `P12_CAMPAIGN_PREREG_V1.json`; verifier
  `check_p12_campaign_prereg_v1.py` (fail-closed; recomputes every frozen
  value from the pinned verified parquet and rejects six hostile mutations).
- **Binding:** SzeChunYiu/ORION#2139 Stage 1; SzeChunYiu/ORION-paper#49 A2
  Phase 1. Consumes, verbatim and unchanged:
  `P12_SCIENCEAGENTBENCH_VERIFIED_SUBSTRATE_FREEZE_V1.json` (substrate),
  `p12_stopgo_frozen_menus_v1.json` (actions/signals/arms),
  `P12_STOPGO_FINAL_ANALYSIS_FREEZE_V1.json` (gate).
- **Status:** this closes the three campaign-prereg elements the frozen menus
  deferred (`S_FAMILY_DIFFICULTY_PRIOR` implementation, the tuning split, the
  repeat policy). Model identities remain unfrozen (Stage 0); no model has
  been called.

## 1. Family census (frozen key, unchanged)

Family key is `github_name`, exactly as the substrate freeze records. The 96
clean instances form **28 families** over 4 domains. Two families span two
domains (`deepchem/deepchem`, `mad-lab-fau/BioPsyKit`); each family carries a
deterministic *primary domain* (majority of its instances, ties lexicographic)
used only for split stratification. Gate criterion 3 (per-domain direction and
leave-one-domain-out) aggregates at instance-domain level.

## 2. `S_FAMILY_DIFFICULTY_PRIOR` — frozen implementation

Per clean instance,
`d_i = z(log(1+bytes(task_inst))) + z(log(1+bytes(domain_knowledge))) +
z(log(1+file_count(dataset_folder_tree))) + z(comma_count(subtask_categories))`,
with population z-scores over exactly the 96 clean instances; the family value
is the mean of its instances' `d_i`, rounded to 6 decimals. Inputs are the four
licensed metadata fields only; `gold_program_name`, `output_fname`,
`eval_script_name` and `src_file_or_path` are enumerated as forbidden, and the
verifier's recomputation path never reads them. **All 28 family values are
committed in the machine twin now**, so no post-outcome latitude exists.

## 3. Tuning/protected split (frozen)

Purpose: select the stronger one-signal comparator on tuning data before any
protected evaluation (menus §4). Algorithm: within each primary domain,
families sorted by id; `k = max(1, floor(n/4))` tuning indices drawn by
`random.Random(20260902).sample`; remainder protected. Result, committed by
id in the machine twin: **6 tuning families (17 instances) / 22 protected
families (79 instances)**; the protected side spans all four domains and
satisfies the frozen minimums (>=20 families, >=3 domains) with headroom.

## 4. Repeat and decoding policy (frozen)

One protected run per `(instance, action, model_identity)` cell; deterministic
decoding where the provider supports it (exact parameters frozen per identity
at Stage 0); retries for infrastructure failures only, logged under #664
accounting; a completed run is never re-rolled. Repeats and retries are
execution evidence, never additional statistical units.

## 5. What this artifact does not do

It freezes no model identity (Stage 0), runs nothing (Stage 2 harness does not
exist yet), and licenses no claim. Scientific authority delta:
`NONE__PRE_OUTCOME_PREREG_ONLY`. Editing any frozen value after any protected
model call is forbidden; a successor campaign requires its own prereg.
