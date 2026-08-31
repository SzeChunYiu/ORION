# FiberGuard R24 arm-conditional boundary fibres — result

Date: 2026-08-28

Attempt: `ORION02-REVIVAL-002-R24-ARM-CONDITIONAL-BOUNDARY-FIBRES`

Scientific terminal: `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`

Accounting: counted adverse attempt 2 of 100; 98 remain

Paper freeze: withheld

## Result

The arm-conditioned construction repaired the R23 coverage failure: full-state
coverage rose from `32/44 = 0.727272727273` to `44/44 = 1.0`, meeting the
registered `0.95` coverage gate.  The matched no-geometry lexical control also
covered `44/44`.

The certificate did not survive held-out evaluation.  The primary R24 policy
had `20/44 = 0.454545454545` strict violations of its exact selected-fibre
maximum, above the registered maximum rate `0.10`.  Terminal precedence
therefore stops at `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`.

The R24 primary has mean paired excess difference `-0.008448463125` against
the R23 parent, but its 20,000-bootstrap 95% interval
`[-0.018359034781, 0.000107770719]` crosses zero.  Against the matched lexical
control, its mean difference is `+0.000323174048`, interval
`[0.0, 0.000969522145]`; geometry does not supply value on this frozen corpus.

## Verification amendment and custody

Job `3550275` completed both scientific processes with byte-identical result,
parent and terminal files, then exited `1:0` at independent verification A.
The sole mismatch was schema-level: the frozen R23 parent summary contains
`fallback_fraction` and `backoff_fraction`, while the common R24 summary helper
did not rebuild those two extra legacy fields.  All common fields were equal.

Amendment A added an independent R23-parent schema adapter and changed no
protocol, executor, scientific result, comparator, metric, tolerance, gate or
terminal.  Verification-only LUNARC job `3550317` then passed the amended
independent verifier on both preserved results and all byte-identity checks.
The result SHA-256 is
`b21f54b9aad939b60e9600fc11ba856e8942bc81c73f84b3e28161667a20df54`;
the parent remains byte-identical to frozen R23 SHA-256
`cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77`.

## Paired strict-violation interpretation correction

A later publication-closure draft incorrectly stated that only aggregate R24
strict-violation counts had been serialized and therefore marked the comparator
margin `CANNOT_CHECK`.  The frozen `folds` object in fact retains the geometry
fold's selected primary arm and per-dataset `violation_strict` flags for that arm
under both the geometry and lexical-control policies.  The deterministic
`verify_r24_strict_violation_comparator.py` reconstruction gives 20/44 versus
14/44, with paired contingency `(both, geometry only, control only, neither) =
(14, 6, 0, 24)` and exact two-sided McNemar `p = 0.03125`.

The false `CANNOT_CHECK` interpretation is retracted in
`R24_COMPARATOR_CANNOT_CHECK_RETRACTION_V1.md`; it remains preserved there as
historical provenance.  Both policies exceed the registered 0.10 maximum and
remain adverse.  The corrected endpoint supplies no geometry-superiority claim
and, because both certificates are invalid on one outcome-exposed pinned corpus,
does not establish broad lexical superiority.  No raw result, protocol,
comparator, tolerance, terminal, or earlier negative result changed.

## Disposition

This is a genuine, counted negative revival.  It localizes the remaining
failure to held-out calibration rather than sparse coverage: tau-good
development members do not make their raw selected maximum a valid held-out
certificate, and the geometry policy does not beat the matched lexical
control.  The next prospective discriminator is a cross-fitted,
risk-calibrated upper bound that retains arm-conditioned coverage and the same
lexical control.

All earlier null/adverse evidence remains immutable.  This same-team,
outcome-exposed pinned-corpus result grants no external independence, novelty,
submission, top-tier, or paper-freeze authority.  `unsolvable` remains empty.
