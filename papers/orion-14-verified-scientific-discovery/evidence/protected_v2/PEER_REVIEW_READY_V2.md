# ORION-14 Peer-Review-Ready Attestation — protected V2

**Terminal:** `ORION-14 = PEER_REVIEW_READY`

This attestation closes the scientific/reproducibility readiness gate for Paper IV. It does not claim that a TMLR submission has already been filed.

## Result

- repaired subject: `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`
- protected campaign: `31976589735`
- ORION false promotions: `0/360`
- strongest frozen comparator mechanism (ProvenAI-style): `180/360`
- clean promotions: `60/60` for both; clean false negatives `0` for both
- H1: **PASS**, effect `-0.50`, paired 95% CI `[-0.553,-0.447]`
- H2: **PASS**, clean-coverage effect `0`, CI `[0,0]`
- H3: **NOT_SUPPORTED**, correct-`CANNOT_CHECK` effect `0`, CI `[0,0]`
- typed authority panel: **PASS**
- independent headline reproduction: **PASS**
- scored candidate/comparator telemetry: zero protected-identifier hits and zero external-IP connections

## Publication

- exact publication source: `846a0573fb881c5f9b6caa8e98aede2e51090fca` — GitHub verified
- exact-main ordinary CI: `31978918884` — success
- exact-main TMLR audit: `31978918885` — success
- audited PDF: 11 pages, SHA-256 `562af78b7e634159317a002f8ac651ddc0180ea012712a5def555548b267d3db`
- permanent release tag: `orion-p4-v2-peer-review-ready`
- release target: exact publication source commit above
- release assets: audited PDF; safe V2 result bundle; exact-source supplement; SHA-256 manifest
- archive workflow: `31979303097` — success
- archive merge: `00c19ecd71071e1ad70a8820df4c198153e4da84` — GitHub verified
- archive-merge ordinary CI: `31979303114` — success
- archive-merge TMLR audit: `31979303109` — success

## Boundaries

- Comparator mechanisms are common-protocol reimplementations, not executions of external authors' original systems.
- The 39-case live-model arm is exploratory/non-authorizing and contributes no headline value.
- The older V1 protected campaign authorizes only its older frozen subject.
- Protected per-case gold and raw traces remain outside the public release.
- The result is bounded to this deterministic mechanical-gold hostile battery and does not establish universal evaluator security or naturalistic scientific fact-checking accuracy.
- If actual submission occurs after `2026-08-30`, refresh the nearest-work audit before upload.
- An OpenReview submission ID can only be inserted after the external submission is actually created; that operational action is outside the peer-review-readiness terminal.
