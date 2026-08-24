# Paper 2: Nature Machine Intelligence Article stress test

**Date:** 2026-08-24  
**Target used for this stress test:** *Nature Machine Intelligence*, Article  
**Status:** structural stress test, **not** a submission-readiness claim  
**Manuscript:** `papers/paper-02-open-world-scientific-discovery/manuscript/main.tex`

## Target profile

The local journal profile reviewed on 2026-08-14 gives the following Article
targets:

- no more than 3,500 words of counted main text;
- an unreferenced abstract of no more than 150 words;
- no more than six main figures and tables combined;
- typically no more than 50 references;
- an unheaded introduction followed by `Results`, `Discussion` and `Methods`;
- separate `Data availability` and `Code availability` statements.

Source: `/Users/billy/.codex/skills/nature-shared/journal-formats/nature-machine-intelligence.md`.

## Reproducible budget measurement

Run from the repository root:

```bash
rtk python development/p2-nmi-target-stress-test-2026-08-24/measure_nmi_budget.py
```

The script performs a transparent approximate visible-word count. It removes
comments, displayed and inline mathematics, figure and table environments,
citations, labels and TeX control sequences. Custom-macro expansion can differ
slightly from the submission-system count, so this is a planning measure rather
than a claim about the publisher's final counter.

| Quantity | Measured | NMI Article target | Stress-test result |
|---|---:|---:|---|
| Abstract | 147 words | <=150 | within target, 3-word headroom |
| Counted main text | approximately 15,289 words | <=3,500 | 11,789 words over; approximately 4.37x the limit |
| Methods, reported separately by the script | approximately 1,698 words | excluded from the local profile's main-text limit | retained for planning, not added to the 15,289 |
| Main figures | 6 | figures and tables combined <=6 | see combined total |
| Main tables | 3 | figures and tables combined <=6 | see combined total |
| Main displays | 9 | <=6 | 3 over |
| Bibliography entries | 39 | typically <=50 | within the typical ceiling |

Approximate counted-main-text components are:

| Current component | Words |
|---|---:|
| Introduction opening | 287 |
| State and stopping setup | 140 |
| Acquisition/authority synthesis | 763 |
| Formal mechanics | 1,139 |
| Envelope theory | 3,349 |
| Empirical results | 3,449 |
| Public screening transport | 2,271 |
| Post-saturation validation | 591 |
| Successor interface | 399 |
| Related work | 390 |
| Limitations and integrity | 1,398 |
| Conclusion | 1,113 |

The main-text overage is decisive even allowing for small counter differences.
This checkout is therefore not NMI-Article-shaped yet.

## Local edit made in this pass

The abstract was compressed to 147 measured words. It remains unreferenced and
keeps the outcome-changing boundaries that cannot be hidden by compression:

- the controlled index is descriptive and external screening does not establish
  superiority;
- V7 fails six locked gates and the full candidate loses to frozen u4;
- V8 admits no residual;
- V10 fails four gates;
- V13 supplies a provider-native fibre-separating coordinate, but only 4/7
  reviews support it;
- V15 binds a signed coherent source-state snapshot containing 61 dataset blobs,
  but supplies no index parse, census or performance result;
- the V15 template error was never executed and V15B repairs only a successor;
- independent custody remains 0/3; and
- open-world benefit remains unconfirmed.

This edit is compression, not promotion. It does not change any authority level.

## Required main-text reconstruction

A defensible Article conversion requires a new information architecture, not
line-by-line trimming. The following target leaves approximately 50 words of
headroom for the publisher's counter:

| Target main-text block | Target words | Content retained in main text |
|---|---:|---|
| Unheaded introduction | 500 | problem, acquisition--authority envelope, five contributions, tightly integrated nearest-work positioning |
| Results | 2,050 | core formal consequences; controlled-index mechanism result; external screening succession; adverse authority synthesis |
| Discussion | 900 | interpretation, donor-saturation consequence, limitations, licence/custody boundaries, prospective discriminator |
| **Target total** | **3,450** | **50-word planning headroom** |

### Main-text map

1. **Unheaded introduction (approximately 500 words).** Merge the current
   `Introduction`, `Question-conditioned cumulative read state`, `Route stopping
   versus task stopping` and the essential nearest-work contrast. The present
   standalone `Related work` section should be distributed between the opening
   motivation and Discussion. Do not use literature breadth to imply empirical
   breadth.
2. **Results 1: Envelope and formal consequences (approximately 700 words).**
   State the joint non-compensatory object and the acquisition-ceiling,
   closure-factorization, indistinguishable-world and donor-saturation results.
   Retain theorem statements only at the granularity needed to support the
   scientific argument; move definitions, full proofs, corollaries and secondary
   constructions to Supplementary Information (SI).
3. **Results 2: Controlled-index mechanism test (approximately 350 words).**
   Retain denominator, underpowered/descriptive label, comparator result and
   stopping-safety interpretation. Preserve the fact that stable repeated runs
   do not create independent statistical units.
4. **Results 3: Public screening successors (approximately 750 words).** Use one
   consolidated authority table plus a short narrative. The narrative must keep
   the adverse V7, V8 and V10 decisions and the exact V12--V15 boundaries. No
   one-pool or source-state witness may become screening benefit, system
   superiority, population transport or open-world success.
5. **Results 4: Authority consequence (approximately 250 words).** Connect the
   mechanism and adverse empirical sequence to the theorem-level discriminator:
   strict ascent beyond the donor requires new acquisition support,
   fibre-separating information/state, or evidence that the donor class is
   incomplete. This is a research target, not an achieved result.
6. **Discussion (approximately 900 words).** Interpret the joint contribution;
   compare to the nearest acquisition, screening and stopping families; preserve
   mutable-provider, complete-denominator, external-validity and custody limits;
   end with the prospectively testable route/state discriminator. Rename and
   absorb the current `Limitations and integrity` and `Conclusion` material
   rather than repeating it.
7. **Methods.** Move the Methods section after Discussion. Keep preregistration,
   identities, three-valued outcomes, measurement and statistical authority.
   Detailed packet mechanics and long validation chronology belong in SI.
8. **Availability.** Split the current combined statement into separate `Data
   availability` and `Code availability` sections. `Reproducibility` and `Ethics`
   should be conformed to the journal's submission fields rather than left as
   extra main-text sections without checking the live guide.

### Supplementary Information map

Move detail; do not erase it:

- complete formal definitions, proofs, corollaries and compatible-world
  constructions;
- full V1--V15 chronology, including stopped and unexecuted routes;
- exact validator terminals, hashes, byte counts, manifests and packet
  mechanics;
- secondary endpoint and gate tables, per-review diagnostics and frozen
  decision rules;
- V12 keyword diagnosis, with the exact-V10 identity failure kept explicit;
- V13 per-review support details and its unchanged 6/7 gates;
- the V14 frozen commit/path mismatch and pre-census/performance stop;
- V15 root-licence and source-state details, including historical MIT versus
  current CC0 metadata, 404 index attestation, the unexecuted erroneous template
  and successor-only V15B correction;
- all provenance and claim-ledger mappings; and
- protocol and adapter details that establish conformance but not empirical
  performance.

Every outcome-changing adverse finding must still appear in the abstract,
Results authority synthesis and Discussion. SI is the location for complete
evidence, not a place to conceal falsification.

## Six-display main-text plan

1. **Joint controller and envelope.** Merge current P2-7 and P2-1 into one
   conceptual display showing acquisition, screening, route stopping, task
   closure and the non-compensatory authority frontier.
2. **Controlled-index comparison table.** Retain the main descriptive estimates,
   frozen underpowered label and statistical unit.
3. **Recall versus query figure.** Retain the current P2-2 mechanism curve with a
   caption that prevents open-web generalization.
4. **Route contribution and overlap.** Merge current P2-4 and P2-5 as two panels;
   do not interpret zero overlap as independent capture occasions.
5. **Stopping-safety figure.** Retain P2-6 and distinguish route stopping from
   task closure.
6. **Adverse-authority table.** Consolidate public-screening successors, at
   minimum V7, V8, V10 and V12--V15, with columns for population/source,
   prospective gate, observed terminal, authority level and forbidden
   promotion.

This plan reduces 9 displays to 6 without deleting the empirical contradiction
that controls the claim.

## Non-negotiable authority boundaries

- V12 fails exact-V10 identity; its keyword difference is diagnosis only.
- V13 is a genuine non-simulation metadata witness, but 4/7 support is below the
  unchanged 6/7 sign gates and supplies no performance claim.
- V14 stops on a frozen commit/path mismatch before census or performance.
- V15 is a coherent source-state metadata witness only.
- The exact historical root licence is MIT; it cannot be blended with current
  CC0 repository metadata.
- The V15 erroneous route was never executed; V15B authorizes a corrected
  template only for a successor.
- Independent custody remains 0/3.
- Source-state evidence is not screening benefit, superiority, transport or
  open-world success.

## Remaining NMI blockers and conversion gates

1. Reduce counted main text from approximately 15,289 to no more than 3,500
   words and confirm using both this transparent counter and the actual
   submission-system definition.
2. Rebuild the article into unheaded introduction, Results, Discussion and
   Methods order.
3. Implement the six-display plan and verify caption/figure readability at final
   journal size.
4. Split Data and Code availability.
5. Verify every remaining citation and keep the final bibliography within the
   journal expectation; the current mechanical count of 39 is not a reference
   correctness audit.
6. Maintain a bidirectional main-text/SI claim ledger so compression cannot
   promote an adverse, diagnostic, local, conformance or source-state result.
7. Rebuild from a clean checkout, inspect every affected page and resolve only
   warnings that matter to the submitted artifact.
8. Perform an independent scientific and journal-fit review after restructuring.

Until those gates pass, Paper 2 should be described as scientifically bounded
and structurally mapped for an NMI Article conversion, not ready for top-tier
peer review.
