# P3 public-data successor: CRAFT + SciREX + OAEI

This directory binds the strongest currently bound lawful public-data
transport study in this workspace for Paper 3 without pretending that visible public gold is
protected confirmatory evidence.

## Scientific identity

`P3.PUBLIC.TRANSPORT.CRAFT_SCIREX_OAEI.V1.1` is a **new public transport and
adverse-observation study**. It does not replace or rename:

- the failed partial-observation result `P3.PARTIAL_OBSERVATION.A004`;
- the unexecuted frozen 768-cluster successor
  `P3.PARTIAL_IDENTIFICATION.EXCESS_HARM.V1`; or
- the unexecuted coordinate-obstruction V2 hypothesis.

Current terminal:

`OAEI_INPUT_ONLY_CASE_BUILDER_EXECUTABLE__NO_PUBLIC_GOLD__NO_P3_CANDIDATE__NO_SOURCE_NATIVE_COMPARATOR__NO_EMPIRICAL_RESULT`

## V1.1 adverse-audit repair

The original V1 protocol and its adverse review identity remain preserved.
V1.1 was opened before public reference content or empirical system outputs
were accessed. It repairs mechanics that made V1 scientifically unsafe:

- four-terminal loss now distinguishes `PLURAL`, `OBSTRUCTION`, `GLUE`, and
  `UNRESOLVED` explicitly;
- inventories, cases and predictions use closed contracts plus recursive
  outcome-field rejection;
- predictions may not carry source, panel or cluster weights;
- scoring requires sealed cases and checks valid relations, exact input
  digests, unique and complete `(system_id, case_id)` coverage, and gold/case
  source-panel-cluster equality; and
- every required coordinate must have a complete, nonzero opportunity receipt
  before scoring.

The repaired adapter also includes an OAEI input-only case builder. Direct
execution created 68,043 exhaustive type-compatible pairs across the 20
test-101-to-perturbation comparisons, all within one seed-family cluster. It
read zero `refalign.rdf` members. This is an executable input-universe receipt,
not an empirical or comparative result.

## Why these three donors

| Donor | Strong lawful contribution | Preserved limit |
|---|---|---|
| CRAFT Shared Task 2019 | CC-BY-NC-SA-3.0 biomedical raw text, concepts, coreference, and separately packaged evaluation gold | One biomedical domain; public gold; noncommercial/share-alike conditions; no four-coordinate envelope gold |
| SciREX at `7daad660…` | Apache-2.0 repository and official document-level Method/Metric/Task/Material/Score schema; public train/dev/test layout | Underlying article-text rights are not independently settled by the repository licence; labels are inline and public; README preserves missing-table-mention failure |
| OAEI 2004 at Zenodo `15827226` | CC-BY-4.0 ontology perturbations and reference alignments | One systematic bibliographic seed family; descriptive stress panel, not many independent natural units |

The combined panel is scientifically useful but cannot satisfy the frozen
wide endpoint. In particular, no donor supplies a protected natural temporal-
context mapping panel. Temporal opportunity remains `CANNOT_CHECK`, which
blocks any promotion to the four-coordinate 768-cluster claim.

## Files

- `SOURCE_RIGHTS_REGISTRY_V1.json` — provider records, immutable identities,
  exact files/checksums, licence conditions and content-class cautions.
- `RIGHTS_DECISION_V1_1.schema.json` and
  `RIGHTS_DECISION_TEMPLATE_V1_1.json` — human-owned acquisition gate; the
  template is deliberately `CANNOT_CHECK`.
- `METADATA_RECEIPTS_2026-08-23.json` — refreshed official HTTP receipts; no
  dataset archive body or gold object accessed.
- `P3_PUBLIC_DATA_SUCCESSOR_PROTOCOL_V1.json` — immutable original V1 design.
- `P3_PUBLIC_DATA_SUCCESSOR_PROTOCOL_V1_1.json` — repaired panels, sampling,
  comparators, noncompensatory endpoints and possible negative terminals.
- `OUTCOME_BLIND_PRECOMMITMENT_V1.json` — exact selection boundary.
- `COMPARATOR_REGISTRY_V1.json` — four deterministic gold-free comparator
  contracts and explicit external-baseline gaps.
- `CASE_CONTRACT_V1.schema.json` — gold-free common case contract.
- `PUBLIC_GOLD_CONTRACT_V1.schema.json` — evaluator-only public-gold contract;
  `protected_evidence` is fixed to false.
- `CASE_CONTRACT_V1_1.schema.json`, `PREDICTION_CONTRACT_V1_1.schema.json`, and
  `PUBLIC_GOLD_CONTRACT_V1_1.schema.json` — closed repaired contracts.
- `p3_public_data_adapter.py` — rights-gated acquisition, source inventory,
  deterministic sampling, baseline execution and public-only scoring.
- `capture_metadata_receipts.py` — reproducible official metadata capture.
- `OAEI_ACQUISITION_RECEIPT_V1.json` — provider-MD5-verified public archive
  acquisition; records that the container includes public reference bytes but
  that their content was not interpreted.
- `OAEI_INPUT_INVENTORY_V1.jsonl` and
  `OAEI_OUTCOME_BLIND_SAMPLE_V1.json` — 21 input-ontology directories frozen
  outcome-blind and correctly represented as one seed-family cluster.
- `OAEI_INPUT_CASE_BUILD_RECEIPT_V1_1.json` — input-only exhaustive case-build
  receipt; no public reference alignment was opened.

## Outcome-blind workflow

All commands are examples; they do not confer rights or scientific authority.

### 1. Refresh metadata only

```bash
rtk python capture_metadata_receipts.py METADATA_RECEIPTS.json
```

This fetches two Zenodo records, the pinned SciREX commit, README and licence,
and only a `HEAD` response for the SciREX data archive.

### 2. Acquire lawful packages

CRAFT requires a human-owned V1.1 rights-decision receipt covering the
CC-BY-NC-SA-3.0 conditions. A Boolean acknowledgement is retained only as a
legacy V1 argument and does not authorize V1.1 acquisition. Gold is skipped
unless explicitly requested.

```bash
rtk python p3_public_data_adapter.py fetch \
  --source CRAFT_SHARED_TASK_2019_ZENODO_3460908 \
  --source OAEI_2004_ZENODO_15827226 \
  --data-dir /external/path/p3-public-data \
  --receipt acquisition.json \
  --rights-decision craft-rights-decision.json
```

SciREX data-body acquisition is disabled unless a human rights decision
explicitly names the underlying article-text content class:

```bash
rtk python p3_public_data_adapter.py fetch \
  --source SCIREX_GITHUB_7DAAD660 \
  --data-dir /external/path/p3-public-data \
  --receipt scirex-acquisition.json \
  --rights-decision scirex-rights-decision.json
```

The decision must satisfy `RIGHTS_DECISION_V1_1.schema.json`; the adapter still
does not provide legal advice. The safe template remains `CANNOT_CHECK` until a
human rights owner replaces it with evidence and a scoped decision.

### 3. Inventory and freeze selection without gold

```bash
rtk python p3_public_data_adapter.py inventory \
  --data-dir /external/path/p3-public-data \
  --out inventory.jsonl

rtk python p3_public_data_adapter.py sample \
  --inventory inventory.jsonl \
  --out sample-manifest.json
```

- CRAFT evaluation documents are a provider-input census.
- SciREX preserves official train/dev/test membership and uses a test census;
  its inline labels are not retained or used by the sampler.
- OAEI numbered tests are all retained for descriptive stress, with one shared
  independent seed-family cluster.

Build a reproducible OAEI input-only candidate universe without opening
reference alignments:

```bash
rtk python p3_public_data_adapter.py build-oaei-cases \
  --data-dir /external/path/p3-public-data \
  --out oaei-input-cases.jsonl \
  --receipt oaei-input-case-build-receipt.json
```

This pairs test 101 with every other numbered input ontology and emits the
exhaustive cross-product within each source-native entity type. It is large by
design and remains one cluster.

### 4. Run the frozen gold-free comparators

After a source adapter emits `CASE_CONTRACT_V1_1` JSONL with no gold fields:

```bash
rtk python p3_public_data_adapter.py seal-cases \
  --cases public-cases-unsealed.jsonl \
  --out public-cases.jsonl

rtk python p3_public_data_adapter.py run-comparators \
  --cases public-cases.jsonl \
  --out frozen-predictions.jsonl
```

The four arms are flat label equality, forced token Jaccard, type-aware
pairwise matching, and complete-case conservative matching. They are runnable
development comparators, not a claim to be the strongest external ontology,
IE or alignment systems.

Accordingly, these four arms can falsify the candidate and quantify common
failure modes, but cannot alone authorize a broad superiority claim. A
source-native external comparator must also be bound for every panel on which
comparative superiority is claimed. The pinned SciREX repository supplies an
official-model candidate, but its environment and terminal-preserving adapter
remain unexecuted. No equally exact runnable CRAFT shared-task or OAEI matcher
has been bound in this packet. Until that gap closes, the comparative terminal
is `PUBLIC_TRANSPORT_CANNOT_CHECK_STRONGEST_SOURCE_NATIVE_COMPARATOR`.

### 5. Public-only scoring

Only after candidate and comparator outputs are frozen may an evaluator join
the public gold contract:

```bash
rtk python p3_public_data_adapter.py score-public \
  --cases public-cases.jsonl \
  --predictions frozen-predictions.jsonl \
  --gold evaluator-public-gold.jsonl \
  --out public-score.json \
  --ack-public-gold-not-protected
```

V1.1 rejects missing `identified_relations` before scoring; it never
substitutes a visible point label for an independently justified
identification set. Complete nonzero opportunity receipts are also mandatory
for every coordinate named by a sealed case.

## Endpoints and inference

The primary endpoint is cluster-weighted avoidable harm above the observation
floor across three declared loss regimes. V1.1 adds explicit costs for false
plurality, plurality collapse and unjustified resolution rather than silently
mapping `PLURAL` to `OBSTRUCTION`. It is usable only when an independent
identified-relations set and coordinate-opportunity audit exist. Secondary
endpoints are noncompensatory:

1. false merge on separable opportunities;
2. false split on glueable opportunities;
3. over-resolution on non-singleton identified sets;
4. gold-in-envelope coverage;
5. envelope size conditional on coverage;
6. coordinate/source-family strata; and
7. stage-attributed raw-text failures.

Cases, mentions and reference links are never treated as independent when the
source-artifact-family cluster is shared. OAEI 2004 contributes one independent
seed family regardless of its number of numbered tests. There is no pooled
cross-donor PASS.

## What a positive result could say

A lawful executed result could state only that the named method reduced a
specified public transport endpoint on the named public versions under the
declared comparators and costs. It could not state:

- protected independent confirmation;
- completion of the frozen 768-cluster successor;
- four-domain or temporal-coordinate generality;
- ownership of CRAFT, SciREX, OAEI, ontology alignment, scientific IE or
  partial-identification theory; or
- downstream scientific benefit without a separately governed decision task.

Null, harmful, invalid-coverage, rights-blocked and cannot-check terminals are
all first-class outcomes.

The original V1 adapter mechanics were smoke-checked on two temporary
synthetic cases. V1.1 additionally passed the ten direct checks recorded in
`ADAPTER_REPAIR_EXECUTION_RECEIPT_V1_1.json`, and eight retained input-only
OAEI cases produced 32 comparator mechanics rows. None is public gold,
protected evidence, or a scientific result.
