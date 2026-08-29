# Issue #1701 — ORION-01 / Paper 1 closeout status

**Branch:** `codex/issue-1701-orion01-paper1-v3-20260829`  
**Base used for the clean branch:** `b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8`  
**Ordering:** Paper 1 only; no Paper 2 work is included.

## Bounded-paper lane

| Requirement | Status | Evidence |
|---|---|---|
| Preserve PR #1602 terminal and eight cap hits | **Complete on issue branch** | `PR1602_ADOPTION_RECEIPT.json` binds the source commit, Round-2 hash, Round-3 aggregate hash, eight task indices, repeatability, cap hits, and adverse terminal. The strict path transplant is recorded in `development/orion-01-pr1602-evidence-transplant-2026-08-29/TRANSPLANT_MANIFEST.json`; the stale branch is not wholesale-merged. |
| Repair theorem/proof manuscripts | **Implemented in new V3 identity** | `theory-A-MANUSCRIPT_V3.md`, `theory-B-MANUSCRIPT_V3.md`, and `PROOF_REPAIR_DISPOSITION_V3.md`. Frozen V2 is not edited. |
| Implementation-independent checker | **Implemented** | `proof_checker_v3.py`, tests, and the finite-scope result schema. The checker imports no ORION or PyZX production code. |
| Current primary-source novelty subtraction | **Implemented, bounded authority** | `NOVELTY_AUDIT_V2.md`; standard restricted zero-sum theory, binary dependence, generic descent, and product arithmetic are subtracted. |
| Final bounded package/PDF/manifest | **Build and verification pipeline implemented** | `COMPILE.md`, `build_manifest_v3.py`, package statements, cover letters, manifest seed, checksum seed, and `.github/workflows/orion01-v3-bounded-package.yml`. Generated PDFs and final hashes require a successful workflow run and visual page review. |
| Do not enlarge old cap | **Enforced** | Manuscripts, receipt, claim ledger, successor protocol, and protocol checker all forbid same-identity cap escalation. |

## Production-completeness successor lane

| Requirement | Status | Evidence |
|---|---|---|
| Source-complete move grammar before testing | **Prospectively frozen** | `QUESTION.md`, `PROTOCOL.json`, `CORPUS_MANIFEST.json`, and `SOURCE_COMPLETE_MOVE_GRAMMAR.json`. |
| Completeness theorem or counterexample | **Conditional theorem proved; source instance open** | `REGISTRY_COMPLETENESS_THEOREM.md` proves the relative theorem from O1–O6 and defines fail-closed counterexamples. No pinned-source completeness outcome is claimed. |
| New identity; old R3 adverse only | **Implemented** | New V1 successor identity plus `ADVERSE_AND_CANNOT_CHECK.jsonl`. |
| Material consequence, not larger enumeration | **Prospectively enforced** | The quotient-preservation lemma and Phase-4 gate require a fresh material predicate, identity, and budget after `REGISTRY_COMPLETE`. |
| Independent protocol checker | **Implemented** | Canonical `registry_protocol_checker_v1.py`, corrected tests, terminal system, and CI workflow. It validates only the no-outcome protocol freeze. |

## Deliberately open items

1. **Generated package artifacts.** PDFs, final manifest hashes, and the protocol-check receipt depend on successful GitHub Actions execution; visual PDF inspection remains a human release gate.
2. **Pinned-source execution.** The prefix `dade7d46` has not been claimed resolved under this identity, and O1–O6 have not been discharged for the source instance.
3. **External authority.** No external proof review, novelty opinion, replication, submission, or acceptance is claimed.

## Current bounded dispositions

- bounded paper: `BOUNDED_PAPER_RETAINED`
- successor protocol: `PROTOCOL_FROZEN__NO_OUTCOME`
- old execution: `CANNOT_CHECK_MOVE_COMPLETENESS`
- portfolio routing: `TOP_TIER_PROMOTION_ACTIVE__THEORY_OR_EXACT_COMPUTE`
