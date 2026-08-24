# P9 bounded claim ledger V1

Status: **pre-result-integration manuscript contract**. Donor saturation is complete, but M1/D1/A2-A4 official receipts are not yet all merged. No `PENDING` row is an authorized claim.

| ID | Candidate claim | Evidence owner | Current state | Ceiling / nonclaim |
|---|---|---|---|---|
| P9.C1 | On frozen hostile pairs, hiding a load-bearing coordinate creates an exact non-identifiability ceiling, and exposing relation semantics, local transport values, or admitted failure history can remove that information deficit. | merged tranche-0/1 + M0 | `SUPPORTED_METHOD_OBJECT`; final wording pending verification | Specific exact D0 coordinates only; not a new Bayes-error theorem. |
| P9.C2 | D0 affine local-transport gluing is solved by payload-only explicit inference when transport values are visible and correctly remains `UNKNOWN` when they are absent. | A5 #478 / merged PR #521 | `BOUNDED_VERIFIED` | One-dimensional affine transport only; no generic inference superiority. |
| P9.C3 | Generic classical learning leaves only localized residual computation on the frozen D0 worlds. | M1 #486 | `PENDING_OFFICIAL_RECEIPT` | No result copied from independent expectations. |
| P9.C4 | Exact typed relational method coordinates improve whole-domain held-out transfer relative to reminted transcript and same-information unstructured serialization controls. | D1 #519 / #479 | `PENDING_OFFICIAL_RECEIPT` | Exact authored/procedural method structures only; no natural-paper extraction claim. |
| P9.C5 | D0 relation-semantics and admitted-failure-history mechanic selection are exhausted by payload-only explicit inference when their decisive coordinates are visible. | A2/A4 #475/#477 | `PENDING_CORRECTED_REPLAY` | Bounded D0 only; no universal operator-learning or memory claim. |
| P9.C6 | The P9 escalation protocol can identify when more complex neural machinery is not justified by the observed residual. | synthesis of C2–C5 | `PENDING_FINAL_SYNTHESIS` | Methodology claim only; does not say neural methods are generally inferior. |

## Claims explicitly struck by donor saturation

P9 does not claim novelty for graph-aware Transformers, heterogeneous/typed graph attention, local/sheaf representations, neural algorithmic reasoning, language+structured-reasoner hybrids, reusable program/module discovery, continuous latent reasoning, production-system rule/entity binding, mechanism-centric world models, causal compositional world models, generic active/counterexample learning, value-of-computation, generic uncertainty/abstention, relational bottlenecks, analogy/role-filler representations, or minimal causal state abstraction.

## Deferred / not-load-bearing research objects

These may remain scientifically useful successor programmes, but they may not appear as experimentally supported P9 contributions unless explicitly reopened with a prospective protocol:

- recurrent/anonymous latent reasoning;
- explicit variable-role binding;
- causal/interventional mechanic learning;
- advanced RL/curriculum/meta-learning;
- natural-paper expert gold;
- LLM integration / P10 structured reasoning.

## Replay determinism record (2026-08-24, append-only)

The reopened 0.50-vs-0.75 serialized-arm divergence (`P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED`)
is mechanistically resolved without changing any claim row:

- **Deciding factor** (one-factor toggle, `evidence/P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json`):
  the binary build of the numerical stack executing lbfgs, beneath the recorded
  version manifest. Bit-identical design inputs, identical scipy 1.17.1 and
  scikit-learn 1.8.0, identical frozen selection rule and selected config —
  conda CPython 3.13.12/NumPy 2.4.4 converges in 480 lbfgs iterations to the
  archived 0.50 (zero per-case flips on all four arms); conda CPython
  3.11.15/NumPy 2.4.3 builds (two independent envs, bit-identical canaries)
  converge in 439 iterations to 0.75, flipping exactly the 32 sub-margin
  UNRESOLVED-truth knife-edge cases. Both sides converge cleanly and are
  deterministic within build. The version manifest underdetermines the replay;
  a version-number pin was never a determinism pin.
- **Determinism enforcement** (`top_tier/replay_d1v1_2_pinned.py`): one documented
  entry point that fingerprints the executing build by a numeric canary (full
  sha256 of the converged serialized-arm coefficient bytes) and fails closed
  unless the canary predicts the observed per-case attractor. This pins the
  pinning protocol, not a hardcoded accuracy.
- **Two clean replays** (`evidence/P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json`,
  `..._R2_...`): separate process executions under the pinned archive-matching
  build with identical deterministic cores, identical result digests
  (`sha256:a79453e6335501bdc1431053ddcf458dbd48ff3a75b77efb28fc71759527e89f`),
  and per-case equality with the archived result on all four arms.
- **No relabelling**: the archived 0.5 remains the modal-class prior of a
  degenerate comparator, not a representation measurement; the divergence
  carries no representation-quality information in either direction; the
  historical terminal stays append-only. Binding checker:
  `top_tier/check_d1v1_2_pinned_replay_v1.py`.

## Paper gate

A standalone P9 manuscript is allowed only if:

1. at least one result-dependent bounded claim survives official execution, independent replay, and current novelty review;
2. the final contribution is independent of P1/P3/P6/P8 and more than a reusable benchmark note;
3. negative and sufficiency results are included rather than hidden;
4. no result exceeds its information/protocol ceiling;
5. #283 and #287 record current P9 dispositions.
