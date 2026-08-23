# ResponsibilityCarryingState contract

An RCS contains compact state plus a fail-closed contract binding raw/source evidence identity; compiler/transform identity and version; exact supported responsibility set; independent witness/certificate identity; intentionally omitted coordinates/information classes; required-same context coordinates; reopen-on-change coordinates; raw recovery/reconstruction availability and freshness; recovery/reopen cost; resource envelope; evaluator identity; authority owner; and an explicit declaration that the object grants no scientific/novelty self-authority.

At reuse time the contract returns:

- `USE_COMPILED` when requested responsibility is supported and all bound conditions hold;
- `REOPEN_REQUIRED` when support does not hold but richer state can be recovered;
- `CANNOT_CHECK` when support is absent and recovery/verification cannot establish a safe route.

`CANNOT_CHECK` is a correct scientific disposition, not an error to hide.