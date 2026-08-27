# ORION-13 Public-Reference Pilot — Authority Correction V1

**Status:** CORRECTION / supersedes the authority interpretation in `PUBLIC_REFERENCE_PILOT_V1.md` while retaining that document as development history.

## What remains useful from the pilot

The pilot correctly identified a low-cost direction: existing public scientific datasets contain expert/manual annotations that can be reused rather than commissioning a new 32-case annotation project from scratch.

It also correctly identified that public resources have uneven coverage across ORION's semantic coordinates.

## What is withdrawn

The pilot's reported **“simulated inter-annotator agreement” κ = 0.83 is not inter-annotator agreement** and must not appear as evidence of annotation reliability.

There was one annotator. Comparing heuristic-derived labels with a manual review of three cases is a development check, not independent IAA.

The following proposed shortcuts are also withdrawn as final-gold mechanisms:

- citation-count heuristics for `attribution_relation`;
- heuristic hedging/polarity labels promoted directly to gold;
- manually augmented `recoverability_target` without independent external authority;
- a “double-blind 10% sample” performed by non-independent LLM personas.

These may discover candidates only.

## Replacement

`PUBLIC_REFERENCE_AUTHORITY_POLICY_V1.md` defines the allowed route:

- reuse external expert/human labels;
- use deterministic standards/identities when the relation is mechanically entailed;
- mask unsupported coordinates;
- require immutable provenance for every scored label;
- never let an LLM, proxy, or simulation become final gold.

## Consequence for the paper

The public-reference route is intentionally narrower than the original end-to-end expert-gold protocol. It evaluates the mapping/integration layer on externally grounded structured cases. The raw-text expert-gold study remains a stronger future experiment, not a prerequisite for running this narrower study.
