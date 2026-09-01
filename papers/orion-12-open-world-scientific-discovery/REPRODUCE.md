# Reproduce ORION-12

Run from the repository root with Python 3.12.

## Claim and protocol gates

```bash
python papers/orion-12-open-world-scientific-discovery/scripts/check_claim_ledger.py --check
python papers/orion-12-open-world-scientific-discovery/scripts/check_p2_assimilation.py
python papers/orion-12-open-world-scientific-discovery/scripts/check_p2_v2.py
python papers/orion-12-open-world-scientific-discovery/scripts/mirror_ci_evidence.py --check
```

These checks fail closed on unledgered result prose, donor/source drift,
unauthorized V2 promotion, and mutated or missing CI evidence archives.

## Controlled headline evidence

```bash
python papers/orion-12-open-world-scientific-discovery/scripts/run_offline_companion.py --check
python papers/orion-12-open-world-scientific-discovery/scripts/render_suite_facts.py --check
python papers/orion-12-open-world-scientific-discovery/scripts/render_offline_mechanisms.py --check
python papers/orion-12-open-world-scientific-discovery/scripts/render_route_stop_oracle.py --check
```

The offline companion rebuilds the 390-task × 14-system × 3-repeat projection
and refuses any digest drift. Repeats test deterministic harness stability; they
do not enlarge the statistical unit. The headline remains descriptive and
underpowered for the frozen 0.03 superiority margin.

## External evidence

MetaSyn and AutoResearchBench rerun instructions and pinned revisions are in
`protocol/` and `evidence/access/`. The OpenAIRE/Crossref matched campaign is
not rerun into a different result: its immutable failed capture, first evaluator
handoff, and evaluator-only repair are mirrored as the three
`evidence/ci_mirror/p2-wide-openaire-matched-*.zip` files. Verify them with the
mirror command above and audit the terminal in:

- `evidence/external_results/P2_WIDE_OPENAIRE_MATCHED_RESULT_V1.json`;
- `evidence/external_results/P2_WIDE_OPENAIRE_MATCHED_RUN_RECEIPT_V1.json`.

Its `P2_WIDE_EXTERNAL_CANNOT_CHECK` terminal is mandatory because only 800 of
1,200 provider calls succeeded. A new campaign requires a new prospective
protocol; do not overwrite this capture or interpret its zero paired difference
as a valid null.

## KIFMS V6 source/protocol feasibility

The V6 packet validates without opening labels or running a comparison:

```bash
python development/p2-continuous-recall-effort-v6-2026-08-23/validate_p2_v6_packet.py
```

Expected terminal:

`P2_KIFMS_V6_LAWFUL_EXACT_SOURCE_AND_LABEL_BLIND_DISJOINT_POPULATION_FROZEN__INDEPENDENT_PROTECTED_EXECUTION_CANNOT_CHECK`

The validator checks 14 JSON files, three Python files and all 23 manifest
entries.  It binds 14 exact revision-one OSF CSV identities, the 5,074-to-4,934
label-blind population, one excluded raw V5 content match, 65 shared KIFMS
content identities affecting 132 excluded rows, zero final SWIFT/V5 content
overlap, the missing KIFMS PMID channel, the CRE20/R@10 coprimary freeze and the
independent-custody refusal.  Manifest SHA-256 is
`cb7aac3ea6cc4b1070515dff882c4e3cb0a85632e5829af379208dd70448f710`.

The public KIFMS, SWIFT and V5 source bodies are not redistributed in the V6
packet.  With exact receipt-matching source roots, the label-blind calculation
can be reproduced by
`run_label_blind_overlap_preflight_v6.py`; it indexes KIFMS key, title,
abstract and PubMed fields but never indexes, counts or emits the three outcome
columns.  `capture_kifms_source_metadata_v6.py` is a live metadata refresh, not
a substitute for the frozen receipt.  Historical public ASReview simulation
artifact paths exist for the KIFMS family; their metric contents were not opened
in V6.  No command in this section authorizes label access, model fitting or a
claim that the family is globally outcome-sealed.

## KIFMS V7 transparent public-development execution

V7 has already executed under its own pre-outcome hash freeze. Its packet can
be checked without source CSVs, pytest or repository CI:

```bash
python development/p2-kifms-transparent-execution-v7-2026-08-23/validate_v7.py
```

Expected terminal:

`P2_KIFMS_V7_TRANSPARENT_PUBLIC_EXECUTION_FAILS_ONE_OR_MORE_LOCKED_PERFORMANCE_GATES_REQUIRES_SUCCESSOR`

The exact CC-BY-4.0 source CSVs are not redistributed. A rerun requires all 14
revision-one files to match the V6 receipt bytes and SHA-256 values; the V7
runner refuses any fixed-file, source, population, class or complete-order
mismatch. Re-execution is a deterministic public-development reproduction, not
independent confirmation and not a new statistical unit.

## KIFMS V8 nested donor-envelopment development

V8 can be checked without source CSVs, pytest or repository CI:

```bash
python development/p2-donor-envelopment-v8-2026-08-23/validate_v8.py
```

Expected terminal:

`P2_V8_DONOR_ENVELOPMENT_CROSSFIT_FAILS_CRE20_WSS95_AND_HARM__NO_RESIDUAL_ADMITTED__EXACT_U4_FALLBACK`

The validator checks seven JSON files, four Python files, exact u4 reproduction
for all 14 reviews and 84 residual executions. It also distinguishes the raw
execution selector terminal from the authoritative post-execution scientific
classification in `SCIENTIFIC_ADJUDICATION_V8.json`. Twelve outer folds retain
exact u4 and the two non-fallback activations harm their held-out reviews; no
residual is promoted. Result SHA-256 is
`8aa6438b470a7facd7e630a8280afdbc034120c631eac4fdfe744d48a0e63e75` and
adjudication SHA-256 is
`fe1f5633a465c0b6d8e21673d867d77e3ccc8fc3af58c86703a25ea3f3d0ec25`.
Re-running the V8 experiment requires the exact private source stage named in
the packet README; validation of the archived result does not. V8 is open
same-workspace development, not independent confirmation or source-general
residual evidence.

## Manuscript and package

```bash
cd papers/orion-12-open-world-scientific-discovery/manuscript
python ../scripts/build_ipm_submission.py --check
TEXINPUTS=./elsevier-cas//: latexmk -xelatex -interaction=nonstopmode -halt-on-error ipm_submission.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error arxiv_submission.tex
python ../scripts/check_manuscript_typography.py --log ipm_submission.log
python ../scripts/check_manuscript_typography.py --log arxiv_submission.log
cd ..
python scripts/build_submission_package.py --check
```

Expected filing artifacts are the anonymous IP\&M CAS PDF and the attributed
arXiv PDF in `submission/publication-final-20260901/`. The builder reconstructs
each PDF from its distributed source archive, verifies exact PDF equality,
checks the anonymous route for author identity, and refreshes the manifest and
checksums. The package attests only the bounded methods / critical system-design
claim; external ORION-vs-baseline superiority remains unestablished.
