# ORION research-revival programme infrastructure

Parent issue: [#284](https://github.com/SzeChunYiu/ORION/issues/284).

This directory is **programme audit scaffolding**. It does not implement child science, does not promote novelty, and does not tick #284 child-terminal checkboxes. Green tests here are not scientific completion.

## Contents

| Path | Role |
|---|---|
| `PROGRAMME_TRACKER_V1.json` | Machine-readable status of children #278–#283 and #285–#288: allowed terminals, current state, next discriminator, `CANNOT_CHECK` list. |
| `CONSTITUTIONAL_DOCTRINE_V1.json` | Checked protocol: never tune outcomes positive; one-stage attribution; freeze discriminator before repair; new immutable protocol; preserve negative history. |
| `NOVELTY_HYPOTHESES_V1.json` | N1–N4 as certificates-to-be (pointers). `claimed_novelty` is false. |
| `CORRECTIONS_V1.json` | Current-main facts: P4 V2 `PEER_REVIEW_READY`; P1 H1 n=385 vs H2 n=2401; no post-outcome margin relaxation; P5 attribution 21/24. |
| `REVIVAL_BACKLOG_SUCCESSOR_V1.md` | Cites duplicate PRs #272 (preferred) and #273 rather than copying `REVIVAL_BACKLOG_V1.md`. |
| `tracker.py` | Validator. Rejects illegal transitions such as `MECHANISM_SUPPORTED` without a #283 `verification_record_id`. |

## Check

```bash
python research/revival/tracker.py
```

A child box on #284 may be ticked only when that child has reached a scientific terminal **on main**, with evidence. This scaffolding PR does not do that.
