# Five-paper publication handoff R3

Date: 2026-08-25
ORION base: `cb3b73f1a971716022b7c5ee25e561b755218a31`
Writing implementation: `academic-paper-skills@8a2ff684eb4b777b88592e57637984f08544f56e`
Branch: `codex/orion-publication-rewrite-20260825`
Worktree: `/workspace/scratch/d9c618f2e1ef/orion-publication-rewrite`

## Binding scientific closure

`FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`

The five papers remain separate scientific namespaces. Shared terminology may
be calibrated across manuscripts, but proof, evidence, novelty, and target
authority never transfer across namespaces. The struck universal-calculus
novelty claim is not present in any V3 title, abstract, body, caption, or
availability statement.

## Verified manuscript map

| Paper | Verified direct parent | Submission source | Primary target | Pipeline state |
|---|---|---|---|---|
| A | `theory-A-multitag-constraint-rank/MANUSCRIPT_V2.md` plus its R2 ledger | `theory-A-multitag-constraint-rank/MANUSCRIPT_V3_PIPELINE.md` | Quantum | `simulated_publication_ready_for_target` |
| B | `theory-B-certificate-complexity/MANUSCRIPT_V2.md` plus its R2 ledger | `theory-B-certificate-complexity/MANUSCRIPT_V3_PIPELINE.md` | ACM Transactions on Quantum Computing | `simulated_publication_ready_for_target` |
| C | `theory-C-low-order-information/MANUSCRIPT_V2.md` plus its R2 ledger | `theory-C-low-order-information/MANUSCRIPT_V3_PIPELINE.md` | Quantum; Quantum Information Processing fallback | `simulated_publication_ready_for_target` |
| D | `theory-D-falsification-authority/MANUSCRIPT_V2.md` plus its R2 ledger | `theory-D-falsification-authority/MANUSCRIPT_V3_PIPELINE.md` | Journal of Automated Reasoning | `simulated_publication_ready_for_target` |
| Non-quantum | `nonquantum-c5cubed-davenport/MANUSCRIPT_V2.md` plus its R2 ledger | `nonquantum-c5cubed-davenport/MANUSCRIPT_V3_PIPELINE.md` | Electronic Journal of Combinatorics | `simulated_publication_ready_for_target` |

Each paper has a colocated `PIPELINE_CONTROL_V3.md` that seals its identity,
claim/evidence/source/display/concern ledgers, target, and prohibited
expansions.

## Authority reconciliation

The complete R2 five-paper wave already on current `main` is the scientific
parent. `papers/verify_five_theory_hardening_r2.py` reproduces its committed
result object with `all_checks=true`.

ORION PR #1181 was not imported. Its concatenated base64 transport is truncated;
only ten complete tar members can be recovered, its result ledgers are absent,
Paper A's verifier cannot be bound to claimed results, and Paper B's verifier is
corrupted. The readable documents were checked for claim conflicts, but they do
not supply admissible implementation authority. This R3 lane is the clean
replacement.

The three untracked ownership/portfolio overlays remain byte-preserved intake
evidence rather than repository authority. Their ideas enter V3 only when they
are independently present in the verified R2 parent and sealed ledger.

## Cross-paper overlap lock

- A owns the alphabet-sensitive compiler normal form and frozen R6M sharpness.
- B may cite A's normal-form theorem, but owns only the certificate-versus-
  intrinsic-support separation and registered product amplification.
- C owns the query-specific decision/value/optimizer information hierarchy.
- D owns only the finite typed evidence-license evaluator and semantics. Its
  cases encode results from other namespaces without combining their theories.
- N owns the generalized-Davenport corridor and obstruction phase. No quantum
  evidence enters its claim ledger.

## Submission boundary

The terminal state is an internal editor/reviewer simulation, not an acceptance
claim. Before actual journal upload, authors must provide names, affiliations,
contribution statements, conflicts, funding, final archive identifiers, and any
venue-specific disclosure of generative-tool use. External novelty review and
independent proof scrutiny remain scholarly responsibilities; they are not
silently represented as completed by repository checks.
