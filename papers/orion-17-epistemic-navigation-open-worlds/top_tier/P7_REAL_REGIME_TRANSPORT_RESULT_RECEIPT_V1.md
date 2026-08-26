# ORION-17 real regime transport result receipt V1

**Run:** GitHub Actions `32657074362`  
**Artifact:** `p7-real-regime-transport-v1`, artifact ID `9498189106`  
**Artifact ZIP SHA-256:** `28094f89578e03d1bae41ed80334505f3e3f4d7e96c403036e4bf3f8a0e84f03`  
**Primary terminal:** `P7_REAL_REGIME_TRANSPORT_V1_SUPPORTED`  
**Independent terminal:** `P7_REAL_REGIME_TRANSPORT_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** `P7_REAL_REGIME_TRANSPORT_TWO_IMPLEMENTATIONS_AGREE`

## Exact binding

- protocol SHA-256: `cca4f2daf259a1b42e55f93e0474f0c443e14dba51049c7b5bb0a57d79257340`
- frozen source record SHA-256: `9ef55a0b2864eaf554a264c0ed91e7cbaf715dec7b3e8b580dd174495d7e950e`
- primary receipt SHA-256: `84e8999ad903d4fc6e66eb29b968fa2453b752cd1c086bcfb2fa0a1b97fb59e1`
- independent receipt SHA-256: `c303aefcb523324405970329973cedbdd47af2523f94965bed372b2d5662e905`
- deterministic primary replay: GREEN
- independent implementation agreement: GREEN

## Domain A — real public standard transition

The study uses the public RO-Crate `1.2 -> 1.3` transition. Four Bioschemas workflow terms changed canonical URI bindings while ordinary value-level JSON usage can appear unchanged.

Across 14 frozen standard-transition cases:

- witness-aware transport: `1.0` exact accuracy, `0` false closure, `0` unnecessary reopen, `4` correct `CANNOT_CHECK`;
- value-only transport: `0.428571...` exact accuracy and `8` false-closure decisions;
- always-reopen: `0.285714...` exact accuracy and `6` unnecessary reopen decisions.

The second implementation independently reproduces all 14 dispositions, the four changed terms, two unchanged controls, eight value-only false closures and six always-reopen unnecessary reopens.

## Domain B — real dataset ontology/responsibility transition

The study uses the 178-example UCI Wine recognition data bundled by scikit-learn. The original responsibility has three fine class identities; the coarse responsibility is `class0_vs_other`. The reverse coarse->fine map is non-injective because coarse value `0` merges fine classes `1` and `2`.

Across 712 protected transport rows:

- witness-aware transport: `1.0` exact accuracy and `238` correct `CANNOT_CHECK` dispositions;
- value-only transport: `0.665730...` exact accuracy and `238` false-closure decisions;
- always-reopen: `0.0` exact accuracy and `474` unnecessary reopen decisions.

There are `119` ambiguous coarse-0 examples, and the sequential support-history construction yields `119` cases where locally well-formed representation changes require different scientific dispositions depending on retained refinement/support history.

## Scientific disposition

ORION-17 now has non-synthetic evidence in two qualitatively distinct regime-change domains: a real evolving public standard and a real observed dataset with ontology/responsibility coarsening/refinement. The result supports the claim that value preservation alone is weaker than evidence/support/closure transport, while always reopening is unnecessarily conservative.

This result does **not** establish universal scientific-regime transport across arbitrary world-model, objective or research-agent changes. Those broader claims remain subject to the final manuscript scope and donor refresh.
