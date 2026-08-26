# ORION-23 verifier-backed responsibility shift result receipt V1

**Run:** GitHub Actions `32655587071`  
**Artifact:** `p13-verifier-responsibility-shift-v1`, artifact ID `9497357999`  
**Artifact ZIP SHA-256:** `2c95e18e92086d73af909b338d188ada66bffe86a30aba02bd99e918c7524362`  
**Primary terminal:** `P13_VERIFIER_RESPONSIBILITY_SHIFT_V1_SUPPORTED`  
**Independent terminal:** `P13_VERIFIER_RESPONSIBILITY_SHIFT_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** `P13_VERIFIER_RESPONSIBILITY_SHIFT_TWO_IMPLEMENTATIONS_AGREE`

## Exact binding

- protocol SHA-256: `1e7ca95274c07a280cde444a39962e9d2b2df599839fe2224b1c2fe303fa79c8`
- frozen cases SHA-256: `19d5a1f34dd4fa466f738d3050ddc3415ddf047cb05b367635b44447334e727c`
- primary receipt SHA-256: `89029b5348d5c2ec8391c3a61e70a3afcb8362838b3db9988f6fd9a348e34c22`
- independent receipt SHA-256: `05afc5f7663319f8b761a61a19834088e82ed0e2ad51e1506a4d37f491e75c59`
- deterministic primary replay: GREEN
- deterministic independent replay: GREEN

## Protected result

Twelve disjoint verifier-backed CNF cases were frozen before runner/checker implementation. Each base formula fixes four of five variables and leaves one registered variable free, yielding exactly two satisfying models. The previous model is independently valid for the old responsibility at epoch `E`.

A new unit clause then changes the formula/epoch so that the previous model is invalid while exactly one alternate model remains. The compact old certificate therefore does not transport to the new responsibility.

Across `24` old/new-responsibility episodes per arm:

| arm | verifier-correct | stale reuse after change | raw literal reads |
|---|---:|---:|---:|
| RCS | 24/24 | 0 | 60 |
| ALWAYS_RAW | 24/24 | 0 | 108 |
| CONFIDENCE_ONLY | 12/24 | 12 | 0 |
| PROVENANCE_ONLY | 12/24 | 12 | 0 |

RCS reduces raw literal reads by `44.44444444444444%` relative to always-raw while matching exact verifier correctness.

Every old compact certificate is valid for the old responsibility. Every post-change certificate transport is explicitly revoked (`old_certificate_transport_after_change = false`). Confidence/provenance-only arms nevertheless reuse the stale model on all 12 changed responsibilities and fail the exact CNF verifier on all 12.

## Scientific disposition

This result closes a **verifier-backed second-domain responsibility shift** at bounded scope. Together with the existing 17,970-episode handwritten-digits result, ORION-23 now has qualitatively distinct real-data and formal/verifier-backed evidence that state sufficiency is responsibility-relative and that a semantic/epoch change can require reopening despite confidence/provenance continuity.

It does not establish arbitrary certificate transport under all semantic changes, nor external scientific-authority judgments beyond these exact verifier-backed responsibilities. Those wider claims remain open.
