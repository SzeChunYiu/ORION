# Table P2-7: AutoResearchBench Wide vs Deep external performance comparison

<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate with:
       python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_7.py
     Sources: evidence/external_results/AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json
              evidence/external_results/AUTORESEARCHBENCH_DEEP_ID_PROBE_V1.json -->

## Probe metadata

| Benchmark | Authority | Candidate | Claim scope |
| --- | --- | --- | --- |
| AutoResearchBench Wide | `OFFICIAL_WIDE_SCORER_EXTERNAL_PROBE` | ORION keyless arXiv public-provider probe | external_probe_not_full_multi_provider_orion |
| AutoResearchBench Deep | `DETERMINISTIC_DEEP_ID_EXTERNAL_PROBE` | ORION keyless public-arXiv probe | deterministic_external_probe_not_official_deep_title_judge |

## Coverage

| Benchmark | Tasks attempted | Records evaluated | Provider requests | Schema version |
| --- | --- | --- | --- | --- |
| AutoResearchBench Wide | 400 | 400 | 400 | `orion.p2.autoresearchbench-wide-official-archive.v1` |
| AutoResearchBench Deep | 600 | 540 | 600 | `orion.p2.autoresearchbench-deep-id-summary.v3` |

## Wide official metrics (400 tasks)

The Wide benchmark uses the official deterministic scorer with IoU, recall, and precision metrics.

| Metric | Value |
| --- | --- |
| Average IoU | 0.005226 |
| Average recall | 0.020012 |
| Average precision | 0.007382 |
| IoU range | [0.0, 0.125] |
| Recall range | [0.0, 0.666667] |

## Deep ID-probe metrics (600 tasks)

The Deep benchmark probe uses deterministic target identification (not the official title judge).

| Metric | Value |
| --- | --- |
| Target hit rate | 0.0 |
| Mean predicted count | 11.13 |
| Scorable records | 540 |

## Provider status counts

| Benchmark | OK | RATE_LIMITED | SERVICE_ERROR |
| --- | --- | --- | --- |
| Wide | 346 | 52 | 2 |
| Deep | 349 | 248 | 3 |

## Interpretation

### Wide probe
Completed: credential-free 400-task AutoResearchBench Wide external probe scored by the pinned official deterministic scorer

Not claimed:
- full multi-provider ORION execution
- matched ORION-vs-baseline superiority
- inferential superiority
- absence of provider throttling or service failures

### Deep probe
*No explicit interpretation field in source JSON. Deep probe authority is `DETERMINISTIC_DEEP_ID_EXTERNAL_PROBE`, which is a deterministic target-ID probe, not the official Deep title judge. A separate official-judge archive exists as `evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json` and is not this table's Deep row.*

## Content integrity hashes (representative)

Wide probe content bindings:
- Candidate output SHA256: `c2dc1d26e1ee0337c2930c3120beb90b…`
- Official evaluation SHA256: `395bd3c12f5022dc7c7e9d4821f7d16e…`

Deep probe content bindings:
- Evaluation SHA256: `dce6bbe0dc698e824a8f6cfdd57bb590…`
- Trace SHA256: `84aeeb1b562d11fba21a207ac6141fe9…`
