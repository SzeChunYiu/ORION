# Dual-lane diagnostic — 2026-08-22

Fixed subject: `main@70c16e7e8f72b394f7da9b2e57288da7746ad4f0`  
Execution: isolated `git archive` under `/tmp`; no canonical artifact was edited  
Task: QG8 weighted support-phase analyzer + generic verifier + native typed
campaign

## Why this run was used

The Q1 cross-review rejected an unconditional higher-dimensional support theorem.
The safe current extension is the already declared weighted three-block,
one-Tag-bit cone. The existing QG8 dual driver is therefore a relevant
diagnostic of the bounded positive result, without pretending to discover a new
theorem.

## Execution

The first run failed before analysis:

```text
ModuleNotFoundError: No module named 'numpy'
```

The harness receipt correctly retained the failed process and did not promote a
scientific result. The failure also exposed an environmental binding gap: the
workspace did not declare or provision the analyzer dependency.

The second run supplied the already installed primary-runtime site-packages on
`PYTHONPATH` and completed:

```text
generic_decision: ACCEPT
native_decision: ACCEPT
both_accept: true
terminal: QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED
source_result_digest: d41beb3f5c79851b6c51a7a8ef17b053ca8b2da4c75f997ccc72d229306095c1
```

Generated diagnostic SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| support-phase result | `4f0e1bf6de001b46dc2e072f1f27c07ee4dc3c3b7649573af84d4ef4ae00fb88` |
| generic verification | `b2b82e5430862175b8ef4af7d543031ef6946a3ea5a9e6d04b8000d14da32790` |
| dual receipt | `697b57503da262f424387359ad1776924028085226a6797c1eb8dc7e38d78112` |

## What the run establishes

- the driver can invoke the analyzer through a harness capability receipt;
- the generic verification and native campaign both accept the bounded QG8
  artifact;
- the typed campaign reaches the registered QG8 terminal;
- failure before dependency provisioning is retained rather than converted into
  scientific failure evidence.

## What the run does not establish

- The process receipt explicitly records `sandboxed: false`.
- The successful run depended on an externally supplied Python package path that
  is not bound into the request identity.
- Both lanes execute pre-authored code over a known result. They verify replay
  and agreement, not that the harness discovered the weighted theorem.
- Ordinary unkeyed digests do not attest executor/model identity or prevent an
  authorized workspace editor from resealing a forged receipt.
- The run carries `novelty_authority: false` and
  `physical_quantum_advantage_claim: false`.

Consequently this is diagnostic E2E evidence only. It supports keeping the
weighted Q1 cone as the current bounded positive structure. Any discovery or
causal-harness claim requires a new, answer-free problem frozen after the donor
envelope instruments, independent product, and hidden evaluator are committed.
