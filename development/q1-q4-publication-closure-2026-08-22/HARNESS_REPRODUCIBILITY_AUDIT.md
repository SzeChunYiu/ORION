# Harness and artifact reproducibility audit

Audit target: PR #829 at
`158fcb08b612ffc82f5a5d2bed4917409084ded8`

Audit date: 2026-08-22

## Authority boundary

This audit tests whether deterministic executables recover committed evidence
and whether custody/build checks behave as specified. It does not treat an LLM
summary, a checker PASS, or an author-authored receipt as scientific truth.

The fixed-ref replays show that the reported computations can execute without
LLM inference:

- Q1's theorem checks and exact local tables regenerate from deterministic
  mathematical code.
- Q2's archive counts regenerate from a deterministic graph validator.
- Q3's QG19/QG20 outcomes regenerate from analyzers that import no Q3
  instrument module.
- Q4's results regenerate from eight deterministic runners.

This does not establish that the harness, rather than an LLM or human, originally
proposed or discovered the solutions. It establishes reproducible computation,
not causal research-origin attribution. The evidence also does **not**
authenticate Q3-R1/R2's named Lane-A model. Those receipts are host-attested and
lack provider-bound request/result provenance.

Per-paper role terminals:

| Paper | Replay inference | Harness-origin authority | Dual-lane executor authority |
|---|---|---|---|
| Q1 | `REPLAY_LLM_INFERENCE=NOT_REQUIRED` | `HARNESS_SCIENTIFIC_ORIGIN_AUTHORITY=NOT_ESTABLISHED` | not applicable |
| Q2 | `REPLAY_LLM_INFERENCE=NOT_REQUIRED` | `HARNESS_SCIENTIFIC_ORIGIN_AUTHORITY=NOT_ESTABLISHED` | not applicable |
| Q3 | scientific analyzers require no LLM inference | `HARNESS_SCIENTIFIC_ORIGIN_AUTHORITY=NOT_ESTABLISHED` | `DUAL_LANE_EXECUTOR_INDEPENDENCE=NOT_AUTHENTICATED_FOR_HISTORICAL_Q3` |
| Q4 | `REPLAY_LLM_INFERENCE=NOT_REQUIRED` | `HARNESS_SCIENTIFIC_ORIGIN_AUTHORITY=NOT_ESTABLISHED` | not applicable |

For historical Q3, the analyzers are code-separated, Lane A is host-attested,
and Lane B uses question-specific rules.

## Environment

Manuscript review used the immutable paper-only archive
`/tmp/orion-pr829-audit.fgvKuu`. Scientific replay used a separate full-tree
archive of the exact head. The object store was first completed and then
archived with:

```bash
git fetch --refetch --no-tags --no-filter origin \
  158fcb08b612ffc82f5a5d2bed4917409084ded8
git archive 158fcb08b612ffc82f5a5d2bed4917409084ded8 | \
  tar -x -C /tmp/orion-q-pr829-full.SEpa81
```

Cut/ancestry validators inherited the source repository object store while
reading the archived worktree:

```bash
GIT_DIR=/workspace/scratch/684dcb6e9333/orion-q-paper-work/.git \
GIT_WORK_TREE=/tmp/orion-q-pr829-full.SEpa81 python3 <validator>
```

Q1/Q4 replay ran under Python 3.12.13 and NumPy 2.3.5. The candidate did not
provide one executable environment lock for all Q1-Q4 studies. Temporary stdout
logs were not promoted to archival evidence; the commands, return codes,
committed comparisons, and decisive differences are recorded below.

## Q1 replay

Command:

```bash
python3 research/extensions/orion-q/max_r6s_all_n_composition.py
```

Recovered outcome:

```text
outcome=THEOREM_MACHINE_CHECKED
lemma_b_w3_to_w8_zero_failures=true
lemma_b_w2_boundary_exact=true
lemma_e_zero_violations=true
exchange_descents_all_verified=true
stress_panel_equality=true
```

The regenerated receipt differs from the committed receipt only in
`runtime_seconds` (`52.677` versus `36.118`). Scientific fields match.

Comparison command:

```bash
git show 158fcb08b612ffc82f5a5d2bed4917409084ded8:\
research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json | \
  diff -u - /tmp/orion-q-pr829-full.SEpa81/research/extensions/\
orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json
```

Independent reviewer replay additionally recovered the R6N 688,041,472 local
checks and the exact `8 < 9` split-anchor counterexample, again excluding only
runtime from equality.

Exact R6N command (from the fixed-ref archive root):

```bash
python3 research/extensions/orion-q/max_r6n_support_dominance_audit.py \
  > /tmp/orion-q-r6n-replay.stdout
```

**Authority:** credible executable support for the finite lemmas and exchange
checker. The article still needs the mathematical proof; bounded enumeration
does not by itself prove an all-n theorem.

## Q2 replay

Command:

```bash
python3 papers/Q-paper-02-recursive-recovery/check_transition_graph.py
```

Output:

```text
Q2_TRANSITION_GRAPH_CHECK=PASS
PUBLICATION_CUT=ca7df1055a43f97eaf8d142a62011c4c261af368
DECLARED_RECEIPT_UNIVERSE=51
INCLUDED_GRAPH_NODES=23
EXCLUDED_WITH_REASON=28
ASSERTED_SUCCESSOR_EDGES=13
NEGATIVE_OR_PARTIAL_NODES=10
STANDALONE_WITHOUT_INVENTED_SUCCESSOR=7
CUT_BOUND_DENOMINATOR_RECEIPTS=51
SCIENTIFIC_CAUSALITY_AUTHORITY=NOT_GRANTED_BY_VALIDATOR
```

The check fails outside a repository history because cut-bound artifacts cannot
be recovered. It passes when evaluated against the exact frozen cuts, as
specified. That is correct fail-closed behavior for artifact identity.

**Authority:** archive identity and declared graph structure only. The validator
does not test semantic edge authorization, causality, usefulness, or the
outcome-independence of the denominator.

## Q3 replay

Commands:

```bash
python3 papers/Q-paper-03-dual-instrument/check_q3_completion.py
python3 papers/Q-paper-03-dual-instrument/check_q3_result_bindings.py
python3 papers/Q-paper-03-dual-instrument/replay_q3_v0.py
```

Outputs include:

```text
Q3_COMPLETION_CHECK=PASS
VALID_PROSPECTIVE_SERIES=V0,Q3-R1,Q3-R2
CONTAMINATED_RETIRED_SLOTS=Q3-V1/QG-7d,Q3-V2/QG-15c
AGGREGATE_RELIABILITY_AUTHORITY=FALSE
SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_CHECKER
Q3_RESULT_BINDINGS=PASS
Q3-R1_RESULT_SHA256=d373028b926c707cb6dc30a85ce4de1bca9f715ad538f8042fd164fc6d86c728
Q3-R2_RESULT_SHA256=ff3768fffe9a464c7d170f1f8e0ccf6ba40bf820f345783505789f6449f7d518
Q3_V0_REPLAY=PASS
```

Independent double-runs recovered byte-identical scientific outputs:

- QG19: 53 rows, zero support-three gaps.
- QG20: 39,489 rows, zero mismatches.

Exact double-run commands (from the fixed-ref archive root) were:

```bash
python3 research/extensions/orion-qg/qg19_outside_cone_sharpness.py \
  --output /tmp/qg19-run-1.json > /tmp/qg19-run-1.stdout
python3 research/extensions/orion-qg/qg19_outside_cone_sharpness.py \
  --output /tmp/qg19-run-2.json > /tmp/qg19-run-2.stdout
cmp -s /tmp/qg19-run-1.json /tmp/qg19-run-2.json

python3 research/extensions/orion-qg/qg20_sixlcu_objective_scope.py \
  --output /tmp/qg20-run-1.json > /tmp/qg20-run-1.stdout
python3 research/extensions/orion-qg/qg20_sixlcu_objective_scope.py \
  --output /tmp/qg20-run-2.json > /tmp/qg20-run-2.stdout
cmp -s /tmp/qg20-run-1.json /tmp/qg20-run-2.json
```

The analyzers' import gates support computational separation from the Q3
instrument code. They do not establish independent authorship or scientific
adjudication.

Current main-source tests for the later D2/D3 repair passed at
`5cf210de2ff5105cc0154f75a33d4c690290d672` using the root-project locked
environment:

```bash
UV_CACHE_DIR=/tmp/orion-q-uv-cache UV_LINK_MODE=copy \
uv run --frozen --extra dev pytest -q \
  packages/orion-research-harness/tests/test_invalid_content_recovery.py \
  packages/orion-research-harness/tests/test_hardening.py \
  packages/orion-research-harness/tests/test_retry_failed.py
```

```text
19 passed in 1.62s
```

The focused collection covered invalid-content recovery, hardening, and
retry-failed behavior. This test result belongs to the successor harness source,
not the historical three-unit Q3 instrument. It is not reproducible from the
package-local extra alone at the audited PR head: that collection fails during
import when `cryptography` is absent. The root lock/source cut above is part of
the authority of the 19-pass result.

**Authority:** chronology, exact scientific analyzer outputs, and historical
receipt bindings. Not authorized: the current diagnosis scoring construct,
provider/model authentication, instrument reliability, or superiority.

## Q4 replay

Exact runner commands, executed from the fixed-ref archive root, were:

```bash
python3 research/extensions/orion-q/nlanes/n4_a_unknown_voi.py > /tmp/q4-n4-a.stdout
python3 research/extensions/orion-q/nlanes/n4_b_stale_receipt_reopening.py > /tmp/q4-n4-b.stdout
python3 research/extensions/orion-q/nlanes/n4_c_interval_pareto.py > /tmp/q4-n4-c.stdout
python3 research/extensions/orion-q/nlanes/n4_d_laundering_detection.py > /tmp/q4-n4-d.stdout
python3 research/extensions/orion-q/nlanes/n4_e_active_experiments.py > /tmp/q4-n4-e.stdout
python3 research/extensions/orion-q/nlanes/n4_f3_remint_transport.py > /tmp/q4-n4-f3.stdout
python3 research/extensions/orion-q/nlanes/n1c_costly_verification_voi.py > /tmp/q4-n1-c.stdout
python3 research/extensions/orion-q/nlanes/n2_f5b_donor_comparison.py > /tmp/q4-n2-f5b.stdout
```

All returned zero and preserved their qualitative terminals. Byte comparison
against the committed fixed-ref receipts found:

| Result | Replay status |
|---|---|
| N4-A | byte-identical |
| N4-B | one last-bit floating-point difference |
| N4-C | one last-bit floating-point difference |
| N4-D | byte-identical |
| N4-E | byte-identical |
| N4-F3 | three last-bit floating-point differences |
| N1-C | byte-identical |
| N2-F5B | eight last-bit floating-point differences |

Example:

```diff
-0.5041679258526743
+0.5041679258526734
```

Second runs in the same environment were byte-identical. Therefore the
deterministic conclusions recover, but the package cannot claim
cross-environment byte identity without a locked numeric environment or
canonical quantization.

Each committed Q4 result was compared to its rerun with:

```bash
git show 158fcb08b612ffc82f5a5d2bed4917409084ded8:<result-path> | \
  cmp -s - /tmp/orion-q-pr829-full.SEpa81/<result-path>
```

For drifting files, `diff -u` isolated only the last-bit values tabulated above.

Git chronology supports pre-result protocol freezes for N4-A/B. N4-C/D/E/F3
introduce protocol, runner, and result together, so current repository history
does not establish prospectivity for those four studies.

**Authority:** deterministic seeded-synthetic construction behavior and retained donor/null
boundaries. Not authorized: six-study prospectivity, a general population
effect, causal state-only attribution, or field superiority.

## References and package checks

The shared metadata checker passed:

```bash
python3 papers/check_q_qg_references.py
```

```text
Q_QG_REFERENCE_CHECK=PASS
BIB_ENTRIES=24
UNIQUE_DOIS=10
CITATION_MAP_KEYS=20
METADATA_AUTHORITY=VERIFIED_FIELDS_ONLY
NOVELTY_AUTHORITY=NOT_GRANTED_BY_REFERENCE_CHECK
```

This validates only selected identity fields. It does not establish literature
coverage, novelty, or claim support. The candidate bibliographies are too sparse
for the necessary nearest-work subtraction.

The candidate's structural package-manifest checks pass. Exact-head source
inspection still finds no submission-complete Q1 package; Q2-Q4's Pandoc
conversion paths exist but do not carry self-contained venue dependencies.

The GitHub Actions runs associated with head
`158fcb08b612ffc82f5a5d2bed4917409084ded8` checked out the synthetic PR merge
commit `d95156e9c661c0fdd1e41ee3a27ac6b28ad2181b` (head merged into
`c5ba39fef4f25c46de5fb69bf07f50530f4693ca`) and failed:

| Workflow | Run | Exact failure |
|---|---|---|
| q1-qg2-quantum-preprint | [32557446455](https://github.com/SzeChunYiu/ORION/actions/runs/32557446455) | `Undefined control sequence` at `\tightlist` (line 108) |
| q2-aij-package | [32557446458](https://github.com/SzeChunYiu/ORION/actions/runs/32557446458) | `Undefined control sequence` at `\tightlist` (line 137) |
| q3-tmlr-package | [32557446449](https://github.com/SzeChunYiu/ORION/actions/runs/32557446449) | `LaTeX Error: File 'lmodern.sty' not found` |
| q4-tmlr-package | [32557446426](https://github.com/SzeChunYiu/ORION/actions/runs/32557446426) | `LaTeX Error: File 'lmodern.sty' not found` |
| q-qg-render-preflight | [32557446403](https://github.com/SzeChunYiu/ORION/actions/runs/32557446403) | `LaTeX Error: File 'lmodern.sty' not found` |
| q-qg-figures-v2 | [32557446387](https://github.com/SzeChunYiu/ORION/actions/runs/32557446387) | `EXPECTED_VALUE_NOT_FOUND` for Q2, Q4, QG1, and QG2 figure data |

A manifest that labels an artifact `PENDING_*` or a checker that validates path
existence does not make a failed package submission-ready.

## Reproducibility release gates

1. Bind each study to protocol, runner, result, exact source cut, seed,
   environment, and semantic/byte comparison policy.
2. Distinguish host-attested from provider-authenticated LLM receipts.
3. Treat every harness repair as a new version and preserve historical results.
4. Require a separate protocol commit before any result-bearing execution for a
   study described as prospective.
5. Publish a clean chaptered TeX source, bibliography, PDF, build log, rendered
   page audit, and artifact hash for every paper.
6. Keep scientific-claim authorization separate from executable integrity.
