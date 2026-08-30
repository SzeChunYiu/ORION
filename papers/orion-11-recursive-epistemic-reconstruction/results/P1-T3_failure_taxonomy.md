# P1-T3_failure_taxonomy

**Status:** `OK`

_Attribution:_ one primary failure mode per trial by the precedence in metrics.classify_failure (authority > invariant > trace integrity > abstention > control selectivity > diagnosis > targeting > reopening > terminal outcome); every mode that fired is retained on the record

| system | role | failure mode | trials | distinct cases | share of scored trials | representative blinded cases |
|---|---|---|---|---|---|---|
| `arex_like_recursive_audit_followup` | BASELINE | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `full_reset_instead_of_dependency_reopen` | ABLATION | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `iris_like_information_state_revision` | BASELINE | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `orion_full` | SUBJECT | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `orion_without_explicit_M` | ABLATION | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `orion_without_explicit_W` | ABLATION | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `scion_like_dependency_execution_plan` | BASELINE | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `static_react_tool_workflow` | BASELINE | ABSTENTION | 235 | 47 | 0.9792 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `orion_live_provider` | BASELINE | MISSED_REFRAME | 160 | 32 | 0.6667 | `P1-C-14aefdd887`, `P1-C-2a87cda138`, `P1-C-39818be118` |
| `generic_retry_instead_of_typed_reframe` | ABLATION | ABSTENTION | 155 | 31 | 0.6458 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `orion_without_mechanic_self_audit` | ABLATION | ABSTENTION | 155 | 31 | 0.6458 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `tree_search_iterative_research` | BASELINE | ABSTENTION | 155 | 31 | 0.6458 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| `orion_live_provider` | BASELINE | WRONG_RESPONSIBILITY | 80 | 16 | 0.3333 | `P1-C-239f672ebc`, `P1-C-4dd49eab04`, `P1-C-8b5889326e` |
| `generic_retry_instead_of_typed_reframe` | ABLATION | WRONG_RESPONSIBILITY | 65 | 13 | 0.2708 | `P1-C-43c471c226`, `P1-C-44d2443b8b`, `P1-C-557ed886fe` |
| `tree_search_iterative_research` | BASELINE | WRONG_RESPONSIBILITY | 65 | 13 | 0.2708 | `P1-C-43c471c226`, `P1-C-44d2443b8b`, `P1-C-557ed886fe` |
| `orion_without_mechanic_self_audit` | ABLATION | WRONG_RESPONSIBILITY | 55 | 11 | 0.2292 | `P1-C-43c471c226`, `P1-C-44d2443b8b`, `P1-C-6884911ddd` |
| `generic_retry_instead_of_typed_reframe` | ABLATION | UNNECESSARY_REFRAME | 15 | 3 | 0.0625 | `P1-C-8b5889326e`, `P1-C-9fbf65695c`, `P1-C-e2cb3aa558` |
| `orion_without_mechanic_self_audit` | ABLATION | UNNECESSARY_REFRAME | 15 | 3 | 0.0625 | `P1-C-8b5889326e`, `P1-C-9fbf65695c`, `P1-C-e2cb3aa558` |
| `tree_search_iterative_research` | BASELINE | UNNECESSARY_REFRAME | 15 | 3 | 0.0625 | `P1-C-8b5889326e`, `P1-C-9fbf65695c`, `P1-C-e2cb3aa558` |
| `orion_without_mechanic_self_audit` | ABLATION | INCOMPLETE_REOPEN | 10 | 2 | 0.0417 | `P1-C-557ed886fe`, `P1-C-ffb30e12b4` |
| `arex_like_recursive_audit_followup` | BASELINE | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `full_reset_instead_of_dependency_reopen` | ABLATION | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `generic_retry_instead_of_typed_reframe` | ABLATION | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `iris_like_information_state_revision` | BASELINE | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `orion_full` | SUBJECT | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `orion_without_explicit_M` | ABLATION | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `orion_without_explicit_W` | ABLATION | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `orion_without_mechanic_self_audit` | ABLATION | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `scion_like_dependency_execution_plan` | BASELINE | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `static_react_tool_workflow` | BASELINE | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |
| `tree_search_iterative_research` | BASELINE | MISSED_REFRAME | 5 | 1 | 0.0208 | `P1-C-2a87cda138` |

## Roll-up by failure mode (all systems)

| failure mode | trials | systems | share of all scored trials | representative blinded cases |
|---|---|---|---|---|
| ABSTENTION | 2345 | 11 | 0.8142 | `P1-C-14aefdd887`, `P1-C-239f672ebc`, `P1-C-39818be118` |
| WRONG_RESPONSIBILITY | 265 | 4 | 0.0920 | `P1-C-239f672ebc`, `P1-C-43c471c226`, `P1-C-44d2443b8b` |
| MISSED_REFRAME | 215 | 12 | 0.0747 | `P1-C-14aefdd887`, `P1-C-2a87cda138`, `P1-C-39818be118` |
| UNNECESSARY_REFRAME | 45 | 3 | 0.0156 | `P1-C-8b5889326e`, `P1-C-9fbf65695c`, `P1-C-e2cb3aa558` |
| INCOMPLETE_REOPEN | 10 | 1 | 0.0035 | `P1-C-557ed886fe`, `P1-C-ffb30e12b4` |

_Case ids are blinded pseudonyms derived from the host-owned suite fingerprint; the raw suite is never published._
