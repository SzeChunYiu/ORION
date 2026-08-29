# Latest-main and audit identity reconciliation

Reviewed `main`: `e19a3b7cd0140d1f413e802a1188a2948726df6f`.

## Uploaded audit binding

| SHA256 | Use |
|---|---|
| `1477fda33938858efdfe4cf322a547331e732006dd3dbfb460934d9c67c54b02` | Canonical recursive-closure audit. Its ORION titles align with the current series. |
| `146e2f8408bda7da466f3fcb6712f72d8987a7d6a7964ea7347701ccaced9ccd` | Reviewer rubric only. Its ORION-number/title mapping does not align with current canonical identities, so its paper-local A/B grades are not imported. |

Examples of the mismatch in the rejected per-paper mapping: ORION-06 is described there as multi-agent bargaining, ORION-07 as tractography/clinical trajectories, and ORION-08 as audit-aware sequential decisions; current `papers/PAPER_ALIASES.md` maps them to Recursive Recovery, Dual Instrument, and Typed State.

## Current-main changes after the uploaded 703b87d audit base

`main` advanced during this audit to `e19a3b7cd0140d1f413e802a1188a2948726df6f` via PR #1754, reconciling the ORION-11 R4 digest and removing ORION-11 from the live drift baseline. This is integrity reconciliation, not new scientific authority.

The latest main adds scientifically relevant interpretation/validation work that the uploaded baseline cannot know about: ORION-11 arm-discrimination disclosure, ORION-13 null/baseline battery and claim narrowing, plus ORION-16/17 alias-aware binding repairs. Those are treated as already landed and are not duplicated by this packet.

## Branch-only evidence policy

A branch can supply a candidate or diagnosis, not authority by existence. Diverged branch content is re-evaluated against current main before reuse. In particular:

- `science/o05-obstruction-basis-v1`: implementation seed, but its control estimand is defective.
- `wk/orion17-density-lane`: preserves a genuine prospective 5/5 packet, but the “density, not size” interpretation is too strong because module count and edge count also separate all eight observed projects.
- `science/orion24-paired-evidence-interpretation-20260829`: useful exact paired interpretation, still branch-only.
- `wk/top-tier-gap-audit-20260829`: strongest all-25 audit diagnosis found, but branch-only and based on 703b87d; this packet carries forward its verified corrections onto the current identity map.

No bulk adoption is authorized.
