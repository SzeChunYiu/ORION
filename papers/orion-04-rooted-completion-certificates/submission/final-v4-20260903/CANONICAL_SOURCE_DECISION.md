# ORION-04 V4 publication source decision

**Canonical scientific source:** `../../WAVE3_SCOPED_MANUSCRIPT_V4.md` (per
`../../WAVE3_PUBLICATION_DISPOSITION_V4.json`, terminal
`ORION04_LOCAL_SCIENCE_COMPLETE__EXTERNAL_REVIEW_DEFERRED`), carrying the
unconditional theorem \(D_4(C_5^3)=30\) and the Freeze–Schmid Theorem 4.1
lower-bound attribution (merged 2026-09-02).

**Claim authority:** `../../CLAIM_LEDGER_V3.md` remains controlling, as the V4
disposition records.

**Supersedes as filing surface:** every earlier package under `submission/`
(the top-level conditional-corridors PDF and `final-20260831/`, which builds
from V2) — see `../README.md`. Those packages predate the unconditional
theorem and must not be uploaded.

**Build:** `build_package.py` in this directory (adapted from the
final-20260831 builder: manuscript pointer V3→V4, front-matter prefix V3→V4;
deterministic zip/PDF settings unchanged). Built artifacts
(`manuscript.pdf`, `source.zip`, `SHA256SUMS`) are produced by the dedicated
CI workflow `orion-04-v4-package-build.yml` and imported from its artifact —
no local TeX toolchain is assumed.

**Venue routing:** fit-first specialist per ORION-paper#49 A1 (E-JC /
Eur. J. Comb. / Discrete Math class); the JCTA-stretch case leads with the
upper-bound method and the \(p=3\)/\(p=5\) tightness-threshold contrast.
Portal actions remain human.
