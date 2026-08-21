# ORION-Q N4-D protocol: stronger-oracle laundering detection under representation remints

Date frozen: 2026-08-21 (before any result-bearing execution)
Parent issue: #677 (registered successor family 5; family 3 — representation
remints requiring transport/reverification — is exercised here as the
laundering vector and this coupling is recorded explicitly)
Lane: ORION-Q N4, branch `claude/orion-harness-verification-b17qdj`
Status: FROZEN before outcomes.
Study script: `research/extensions/orion-q/nlanes/n4_d_laundering_detection.py`
Results artifact: `research/extensions/orion-q/nlanes/N4_D_LAUNDERING_DETECTION_RESULTS.json`

## Question

When representation edits remint interface nodes and transport their
derivability certificates, can ORION full-chain transport verification detect
every attempt to launder a stronger oracle through an edit chain whose final
interface LABEL matches the target, while accepting all honest transports —
and do label-level, summary-trusting, and last-hop-only checkers provably miss
laundering classes in the same worlds?

Hard requirement inherited from the lane charter: a laundering attempt that
smuggles a stronger oracle through an edit MUST be detected and rejected by
the candidate mechanism; any miss fails the primary gate.

## World (exact synthetic)

Each instance is a remint/edit chain of length 2..6 transporting a source
interface node to a target label.

- Node certificate: (label, content_hash, oracle_tier in {0,1,2,3}).
- Declared budget per instance: `T_max in {1,2}` (drawn per instance).
- Honest hop: carries a re-verification receipt
  `(input_hash, output_hash, tier_used)` with `tier_used <= T_max`, and
  `input_hash` equals the previous hop's `output_hash`. Honest chains end at
  the target label; a visible summary field `summary_max_tier` truthfully
  reports the max hop tier.
- Laundering classes (final label ALWAYS matches the target):
  - (a) `MISSING_RECEIPT`: one interior hop has no receipt at all.
  - (b) `SPOOFED_SUMMARY`: one hop truly used `tier_used > T_max`, but
    `summary_max_tier` reports the MIN over hops instead of the max (the
    smuggle is only visible in the per-hop receipt).
  - (c) `DEEP_SPLICE`: every individual hop shows `tier_used <= T_max`, but at
    some interior hop k the `input_hash` does not equal hop k-1's
    `output_hash` — a substituted artifact whose true provenance required a
    stronger oracle was spliced in. Detectable only by walking the full hash
    chain; the LAST hop's receipt is locally consistent.
- Instance mix: N = 400 instances; 50% honest, 50% laundering split uniformly
  over classes (a), (b), (c). Class-(c) splices are placed at interior
  positions, never the final hop.
- Ground truth accept/reject is defined by construction.
- Seed: 20260821. Stdlib RNG. All fields deterministic.

Matched information: all checkers receive the identical serialized chain
(labels, receipts where present, hashes, summary field, `T_max`). They differ
only in what they inspect.

## Arms (checkers)

1. `LABEL_MATCH` — accept iff final label == target label (registered
   LLM-style/surface baseline analogue: label-level agreement).
2. `SUMMARY_TIER` — accept iff label matches AND `summary_max_tier <= T_max`
   (trusts the summary).
3. `LAST_HOP_CHECK` — accept iff label matches AND the final hop's receipt
   exists, is hash-consistent with its predecessor, and has
   `tier_used <= T_max`.
4. `ORION_CHAIN_TRANSPORT` — candidate mechanism: walk the full chain; require
   every hop to carry a receipt; require `output_hash(k-1) == input_hash(k)`
   for all k; recompute `max tier_used` over hops and require `<= T_max`;
   reject otherwise (rejection is the typed CANNOT_ACCEPT outcome, not a
   silent accept).
5. `GROUND_TRUTH` — evaluator reference.

## Prespecified endpoints and gates

Endpoints per arm: recall on laundering instances, false-positive rate (FPR)
on honest instances, per-class recall, overall accuracy.

- G1 (mandatory hard gate): `ORION_CHAIN_TRANSPORT` recall == 1.0 on ALL
  laundering classes including every DEEP_SPLICE instance, and FPR == 0.0 on
  honest transports. Any single miss or false rejection fails the family.
- G2 (non-vacuity of the threat model): `LABEL_MATCH` recall == 0.0 (all
  laundering instances match the label by construction; if any is caught the
  generator is broken and the run is invalid).
- G3 (summary spoof effectiveness): `SUMMARY_TIER` recall < 1.0 and
  specifically misses class (b) and class (c) at rate >= 0.9 within those
  classes.
- G4 (deep-splice hostility): `LAST_HOP_CHECK` per-class recall on
  DEEP_SPLICE < 0.2 (the splice must genuinely evade local checking; if
  last-hop checking catches deep splices the construction failed and the run
  is invalid).
- G5 (determinism): double run, byte-identical receipt line.

Claim boundary: G1 shows completeness of full-chain checking ONLY within this
world, where receipts themselves cannot be forged consistently end-to-end
(hash forgery is out of model). No cryptographic or real-adversary claim.

## Terminal vocabulary

- Positive: `N4_D_CHAIN_TRANSPORT_LAUNDERING_DETECTION_SUPPORTED__EXACT_SYNTHETIC`.
- Negative: `N4_D_CHAIN_TRANSPORT_INCOMPLETE` (G1 fails honestly — a
  laundering instance evaded the full-chain checker).
- Invalid: `N4_D_WORLD_INVALID` (G2, G3, or G4 fails).
- `CANNOT_CHECK` on runtime failure.

## Determinism and authority

Frozen seed; hashes are deterministic integers from the seeded generator, not
cryptographic digests. Authority: `exact-synthetic-bounded; no cryptographic
security claim; no real-adversary claim; no P10/novelty; family-3 remint
transport is exercised only as the laundering vector, not independently
closed`.
