# Amendment 1 — the stratifier cannot be the feature the refinement adds

## The defect

`PROTOCOL_V1.md` says *"Records are stratified by `workflow_class`"* and defines the
refinement as `license → (license, workflow_class)`.

Those are the same variable. **Within a stratum where `workflow_class` is constant,
`(license, workflow_class)` induces exactly the partition `license` induces**, so
the refinement is the identity map there and no stratum can ever show value. The
first run returned `CANNOT_CHECK_NO_CONTRAST` with all twelve strata predicting and
observing no value and `regret_coarse == regret_refined` to the digit in every one
— which is the signature of a refinement that does nothing, not of a theorem that
fails.

**This is an a priori fact and needed no data.** Conditioning on a variable removes
it as a source of variation; a refinement that adds only that variable therefore
adds nothing under that conditioning. I did not see it when writing the protocol
and found it from the outcome, which is worth recording plainly: the design was
checkable before it ran, and I did not check it.

## What changes

The stratifier becomes a property carried by the observation but used by **neither**
binding, so the refinement remains a real refinement inside each stratum:

**`n_tags` band** — `0`, `1–2`, `3–5`, `6+`. Tag count is registry metadata, is not
`license` and is not `workflow_class`, and partitions the corpus into groups of
usable size.

## What does not change

The utility matrix, the threshold `0.1111`, the coarse and refined bindings,
`MIN_MASS = 1`, the in-sample scoring rule, the degeneracy gate, the arms, the split
seed and every terminal stand exactly as committed.

## The global result was already computed and is not re-run

The first run's whole-corpus numbers are unaffected by the stratifier, which only
governs the contrast requirement, and they are reported as they came out:

- 1,533 records, 0 fetch errors, usable rate **0.5806**
- coarse fibres 22, refined 76, singleton fraction **0.342** (gate passes)
- prediction from the training half: **value**; observed: **value**; agrees
- regret **0.1031 → 0.0065**; `attempt_all` **0.1097**
- out-of-sample **0.1076 → 0.0137**

Those numbers stand whether or not the stratification is repaired. The amendment
decides only whether the study may assign a terminal, not what the measurement says.
