# ORION-04/05/06 final publication binding V1

This is a release-governance receipt, not scientific authority. It records the upload-facing package bytes bound by commit `978bb3ef2f5acc61458ba6875957f7b57025646e` after the publication-only closure of ORION-04, ORION-05, and ORION-06.

Scientific authority remains paper-local: ORION-04 is bounded by `CLAIM_LEDGER_V2.md` and `WAVE3_SCOPED_MANUSCRIPT_V2.md`; ORION-05 by publication `CLAIM_LEDGER_V4.md`; ORION-06 by publication `CLAIM_LEDGER_V4.md`. No optional successor experiment is authorized or reported by this receipt, and no negative, adverse, open, withheld, or `CANNOT_CHECK` terminal is promoted.

## Bound upload bytes

### ORION-04
- `manuscript.pdf` — `5aca9f37e7e9ebbd78bc101c777f345567aaf56bf907eef0fa5d224ed1b088cb`
- `source.zip` — `9bc42796af5621f9fc86033c6adb50f0c3586fac0af7373ed4e65983ef60da03`

### ORION-05
- `manuscript.pdf` — `f7c79d1f2e552cf306ed0f8bf651379d32dfd5ff15c2ef80c1c1b5e59fb91474`
- `arxiv-source.zip` — `cfe9c1f9c869b77215278ff9f044764239fa1f0abf750e078c9de29ba9a76610`

### ORION-06
- `main.pdf` — `9723ca3d02585e1886bc3e4f46e31f99da79ac75f57538ebc2b9c6fbf6964840`
- `anonymous-source.zip` — `da5c1f7c48733a662e5ba79404f23a4cdf85d0d08d089b952700513905514000`
- `anonymous-review-supplement.zip` — `3211bc6a358c4dee5ec69a421cfbb22c594fee357c8537d05e47b7162a902329`

## Required release check

The dedicated `ORION 04-06 publication closure` workflow must rebuild these exact tracked packages with zero byte diff, pass the claim-boundary and ORION-06 anonymity gates, pass PDF preflight/render controls, and leave the package-binding step with nothing to commit.

Terminal: `BOUND_BYTES_RECORDED__AWAIT_EXACT_HEAD_REVALIDATION__NO_SCIENCE_AUTHORITY_DELTA`
