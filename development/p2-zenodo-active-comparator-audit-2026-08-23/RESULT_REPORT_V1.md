# P2 Zenodo V2 post-outcome active-comparator audit

## Exact terminal

`P2_ZENODO_V2_ACTIVE_COMPARATOR_TIES_OR_WINS_REQUIRES_CONTROLLER_SUCCESSOR`

The retained V2 candidate reproduced exactly, including order SHA-256
`ef00a1c9e31aa11379067765b230ca396ffbfc28d488a865ee0c46ac4114110a`,
recall@10% `0.7034085878707392`, and WSS@95 `0.7447442625518915`.
All source, retained-failure, V2, pinned-archive and selected donor-source
bindings passed.

## Result

The original V2 contrast was against two **passive** baselines: random order
and a fixed seed-centroid ranking. This successor froze two active comparators
before opening either comparator outcome. Both use the pinned ASReview ELAS
configuration components, the same repaired 25,534-record pool, the same
complete-label-informed positive/negative warm seed, the same text fields and
the same 52-record feedback cadence as the candidate. They are cadence-matched
component reproductions, not exact executions of the ASReview application's
default one-record query cadence.

| Arm | R@5% | R@10% | R@20% | Fraction screened for 95% recall | WSS@95 |
|---|---:|---:|---:|---:|---:|
| V2 active logistic candidate | 0.406375 | 0.703409 | 0.945994 | 0.205256 | 0.744744 |
| ASReview ELAS u4, cadence-matched | 0.414343 | 0.722444 | 0.948207 | 0.203219 | 0.746781 |
| ASReview ELAS u3, cadence-matched | 0.369190 | 0.667109 | 0.917220 | 0.236704 | 0.713296 |

ELAS u4 was the strongest registered active comparator at both the primary
endpoint and WSS@95. The candidate-minus-u4 differences were `-0.0190349712`
at recall@10% and `-0.0020365004` at WSS@95. The frozen `+0.05` primary
margin and nonnegative WSS-dominance gates therefore failed. The result does
not erase the large V2 contrast against passive baselines; it changes its
interpretation. On this one pool, sequential feedback is useful, but the V2
logistic controller is not superior to the stronger registered active family.

## Scientific boundary and next discriminator

This is a post-V2, public-label, one-pool robustness audit. It is not
prospective confirmation, an exact ASReview application reproduction,
independent replay, cold-start evidence, population transport, ORION-specific
novelty, route invention, closure evidence, or software-system comparison.
The smallest admissible successor is not further tuning on this observed
pool. It is a prospectively frozen, source-disjoint multi-review family with
protected seed selection and labels, independent custody, and a comparator
registry that includes the active u4 family before outcomes are opened.

## Frozen artifacts

- `PROTOCOL_FREEZE_V1.json` SHA-256:
  `39a2bbee8c2630a46ee4a13d87fbc89548a0d622ce9a910b2bae75315a05db76`
- `IMPLEMENTATION_FREEZE_V1.json` SHA-256:
  `b4b889e2ae9722583f76700d76f2d61bb074305c14f029af2817ac6c9ab011d5`
- `run_active_comparator_audit_v1.py` SHA-256:
  `ffed82db49d30f5b1ff856b020c9824767fc183fc688ebb808fb4656737b66a2`
- `RESULT_V1.json` SHA-256:
  `fd8a6f446a689cd2376e1948b6399acb35a113937b406188d992f15f1c1b0acf`
- pinned ASReview archive SHA-256:
  `d7023ed8c12cbc3690af1c7db6f907d7c179061253a5a1007c6290e46ecef912`

No post-outcome controller change, test suite, CI, independent replay, commit,
rebase or merge was performed in this lane.
