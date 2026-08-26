# P1-T2_baseline_ablation_results

**Status:** `OK`

Suite fingerprint(s): `21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420` · subject revision(s): `0cf4e8d82771252de94be8c696a3f39fd3191019` · records: 2880 · repeats/case: 5
Intervals: Wilson 95% on the case unit; matched differences by paired percentile bootstrap (10000 resamples, seed 20260815).
Comparator: `arex_like_recursive_audit_followup` — highest overall root_success (0.0208) among BASELINE systems, ties broken on system_id.

| system | role | scope | metric | n cases | rate | 95% CI | Δ vs comparator | Δ 95% CI | Cohen's h | p (2-sided) | verdict | CANNOT_CHECK cases |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `arex_like_recursive_audit_followup` | BASELINE | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | — | — | — | — | — | 0 |
| `arex_like_recursive_audit_followup` | BASELINE | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | — | — | — | — | — | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `full_reset_instead_of_dependency_reopen` | ABLATION | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.1875 | [0.0659, 0.4301] | 0.1875 | [0.0000, 0.3750] | 0.8957 | 0.0748 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | evidence_only_negative_control | unnecessary_reframe | 8 | 0.2500 | [0.0715, 0.5907] | 0.2500 | [0.0000, 0.6250] | 1.0472 | 0.2128 | DESCRIPTIVE_ONLY | 0 |
| `generic_retry_instead_of_typed_reframe` | ABLATION | execution_only_negative_control | unnecessary_reframe | 8 | 0.1250 | [0.0224, 0.4709] | 0.1250 | [0.0000, 0.3750] | 0.7227 | 0.6868 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `iris_like_information_state_revision` | BASELINE | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_full` | SUBJECT | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | NOT_SUPPORTED | 0 |
| `orion_full` | SUBJECT | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | NOT_SUPPORTED | 0 |
| `orion_full` | SUBJECT | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | EQUIVALENT | 0 |
| `orion_full` | SUBJECT | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | NOT_SUPPORTED | 0 |
| `orion_full` | SUBJECT | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | NOT_SUPPORTED | 0 |
| `orion_full` | SUBJECT | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | NOT_SUPPORTED | 0 |
| `orion_full` | SUBJECT | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | NOT_SUPPORTED | 0 |
| `orion_full` | SUBJECT | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | EQUIVALENT | 0 |
| `orion_full` | SUBJECT | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | EQUIVALENT | 0 |
| `orion_live_provider` | BASELINE | ALL | root_success | 48 | 0.0000 | [0.0000, 0.0741] | -0.0208 | [-0.0625, 0.0000] | -0.2897 | 0.7342 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0000 | [0.0000, 0.1072] | -0.0312 | [-0.0938, 0.0000] | -0.3554 | 0.7284 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | hidden_decomposition_or_interface | root_success | 8 | 0.0000 | [0.0000, 0.3244] | -0.1250 | [-0.3750, 0.0000] | -0.7227 | 0.7004 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_live_provider` | BASELINE | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_M` | ABLATION | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_explicit_W` | ABLATION | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.1875 | [0.0659, 0.4301] | 0.1875 | [0.0000, 0.3750] | 0.8957 | 0.0748 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | evidence_only_negative_control | unnecessary_reframe | 8 | 0.2500 | [0.0715, 0.5907] | 0.2500 | [0.0000, 0.6250] | 1.0472 | 0.2128 | DESCRIPTIVE_ONLY | 0 |
| `orion_without_mechanic_self_audit` | ABLATION | execution_only_negative_control | unnecessary_reframe | 8 | 0.1250 | [0.0224, 0.4709] | 0.1250 | [0.0000, 0.3750] | 0.7227 | 0.6868 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `scion_like_dependency_execution_plan` | BASELINE | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.0000 | [0.0000, 0.1936] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | evidence_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `static_react_tool_workflow` | BASELINE | execution_only_negative_control | unnecessary_reframe | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | ALL | root_success | 48 | 0.0208 | [0.0037, 0.1090] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | HIDDEN_SHIFT_SUBSET | root_success | 32 | 0.0312 | [0.0055, 0.1574] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | NEGATIVE_CONTROLS | unnecessary_reframe | 16 | 0.1875 | [0.0659, 0.4301] | 0.1875 | [0.0000, 0.3750] | 0.8957 | 0.0748 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | hidden_parent_domain | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | hidden_representation_or_coordinate_system | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | hidden_decomposition_or_interface | root_success | 8 | 0.1250 | [0.0224, 0.4709] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | hidden_measurement_or_operationalization | root_success | 8 | 0.0000 | [0.0000, 0.3244] | 0.0000 | [0.0000, 0.0000] | 0.0000 | 1.0000 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | evidence_only_negative_control | unnecessary_reframe | 8 | 0.2500 | [0.0715, 0.5907] | 0.2500 | [0.0000, 0.6250] | 1.0472 | 0.2128 | DESCRIPTIVE_ONLY | 0 |
| `tree_search_iterative_research` | BASELINE | execution_only_negative_control | unnecessary_reframe | 8 | 0.1250 | [0.0224, 0.4709] | 0.1250 | [0.0000, 0.3750] | 0.7227 | 0.6868 | DESCRIPTIVE_ONLY | 0 |

## Mechanistic metrics (scope ALL)

| system | responsibility macro-F1 | reframe-target acc. | reopen P | reopen R | reopen F1 | stale-closure survival | invariant viol. | authority viol. | trace fidelity | wallclock s/trial | tokens/trial | tool calls/trial |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `arex_like_recursive_audit_followup` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `full_reset_instead_of_dependency_reopen` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `generic_retry_instead_of_typed_reframe` | 0.0000 | 0.0000 | 0.2727 | 0.0200 | 0.0373 | 0.9800 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `iris_like_information_state_revision` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `orion_full` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `orion_live_provider` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 11.68 | 1205.3 | 1.00 |
| `orion_without_explicit_M` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `orion_without_explicit_W` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `orion_without_mechanic_self_audit` | 0.0455 | 0.0000 | 0.3333 | 0.0333 | 0.0606 | 0.9667 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `scion_like_dependency_execution_plan` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `static_react_tool_workflow` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |
| `tree_search_iterative_research` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.00 | 0.0 | 8.88 |

## Multiplicity (Holm, inferential secondary family)

| comparison | raw p | Holm-adjusted p | rejected at α=0.05 |
|---|---|---|---|
| P1.secondary:HIDDEN_SHIFT_SUBSET | 1.0000 | 1.0000 | no |
| P1.H2 | 1.0000 | 1.0000 | no |
| P1.secondary:hidden_parent_domain | 1.0000 | 1.0000 | no |
| P1.secondary:hidden_representation_or_coordinate_system | 1.0000 | 1.0000 | no |
| P1.secondary:hidden_decomposition_or_interface | 1.0000 | 1.0000 | no |
| P1.secondary:hidden_measurement_or_operationalization | 1.0000 | 1.0000 | no |
| P1.H2 | 1.0000 | 1.0000 | no |
| P1.H2 | 1.0000 | 1.0000 | no |

_Rates use the frozen case as the unit; the 5 stochastic repeats are reduced per case before any interval is taken. `CANNOT_CHECK` marks a quantity that was not observed and is never rendered as 0._
