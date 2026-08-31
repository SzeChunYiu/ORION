# Data, code, and reproducibility — ORION-05

## Data availability

Every result-bearing statement in this manuscript resolves to a committed,
immutable JSON artifact. The artifacts below are the evidence for the
manuscript's headline numbers; each digest is SHA-256 over the file bytes at
the submitted revision.

| Artifact | Supports | SHA-256 |
|---|---|---|
| `research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` | Complete local audit: 688,041,472 configurations, zero violations, split 536,870,912 / 175,616 / 150,994,944 | `95e2b4b1c8a943b3fca515f18ae821562b2e24cad5b1b1b3d9f8f4177904ef61` |
| `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` | All-`n` composition receipt for the support exchange theorem | `b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875` |
| `research/extensions/orion-qg/QG5B_EXACT_FORECASTER_RESULTS.json` | Static evaluator: 9,547 compared instances, zero nonzero-error total; H4 / N2 / Benzene-DUCC2 panels | `7701d4fb708a0a235493a0e4da72076d5d8b77a3e19fa9997ab6a5de51997f16` |
| `research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json` | Enlarged-borrow closure and its refutation counts | `7341f9630c2ca32b8a6cc601e9c1201db68f21212e04eb3b2e36bca63f214159` |
| `research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json` | 64 hostile hybrid witnesses; 10,481 compared instances | `70cee5a5f80482d84e89a92365286e1043cf3e5cf9f847a204fa84d3abcab530` |

Three further `SHA256SUMS` bindings under
`papers/orion-05-tare-expressivity/rounds/` cover the production benchmark,
parent-certificate ordering, and crossover-budget revival rounds. They are
unchanged by this submission.

The analytic argument behind the all-`n` theorem is committed as
`papers/orion-05-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md`, with an
independent sanity script at `independent_human_proof_sanity.py`.

## Code availability

The generating and checking modules are committed alongside the results:
`research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py`,
`research/extensions/orion-qg/qg5b_exact_forecaster.py`, and
`research/extensions/orion-qg/qg7b_hybrid_family.py`. Each writes the
corresponding results file above and is deterministic under its recorded seed
(the fresh-panel seed is `20260826`).

## Reproducibility statement

Reproduction should proceed in the order the science happened, because the
paper's contribution includes its refutations:

1. Re-run the complete local audit and confirm zero violations across all three
   components. This establishes why frame support is expensive and reproduces
   the declared Tag-coupling gap.
2. Verify the all-`n` exchange theorem receipt, then check the analytic proof
   independently.
3. Re-run the static evaluator against the unrestricted dynamic program and
   confirm the zero-error total over 9,547 instances.
4. Re-run the hostile searches and confirm that the 64 hybrid witnesses are
   reproduced, not suppressed.

Collapsing steps 1–4 into a final agreement table would erase the evidence the
paper exists to present. A reproduction that recovers only the positive results
has not reproduced this paper.

## Scope of the digests

The digests above bind evidence, not authority. They establish that a
computation was run and that its output has not moved. They do not by
themselves establish that the frozen grammar or objective is the right model of
any physical compilation task; that boundary is stated in the manuscript's
Limitations.
