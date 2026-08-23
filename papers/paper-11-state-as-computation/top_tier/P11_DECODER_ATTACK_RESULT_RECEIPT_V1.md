# P11 decoder-attack frontier result receipt V1

**Run:** GitHub Actions `32661293913 (conclusion: success)`  
**Artifact:** `p11-decoder-attack-v1`, artifact ID `9498921681`  
**Artifact ZIP SHA-256:** `a474c322b9a598b4f387751bc1b86a13b11714fde43085566459f690bdef5715`  
**Terminal:** `P11_DECODER_ATTACK_V1_GREEN` + `P11_DECODER_ATTACK_V1_INDEPENDENT_GREEN`  
**Replay:** byte-replay green for both the runner and the independent checker

## Exact binding

- protocol SHA-256: `08c4deef4171f71f144410a60a4b9df773ec793d297168753be466679ca9e128`
- frozen gold SHA-256: `2e9814fe7d04b7909d7d3c8cd67d094f2c90455a3e3e06fadf14cd4d1120205a`
- freeze commit: `1724b07a1258f4b84ac0c5fe2b34bf33fb525d27` (precedes all machinery and outcomes)
- pull request: #993

## Protected result

On the frozen T11.2 witness (parity_k over {±1}^k, k ∈ {2,3,4}), verified by
exhaustive enumeration (runner) AND exact Fourier-spectrum re-derivation
(independent checker, `Fraction` arithmetic), with byte-replay determinism:

| family | size at k=4 | realizes parity_4 | minimal realizing size |
|---|---:|---|---|
| constants | 2 | no | — |
| signed single coordinates | 8 | no | — |
| characters (= GF(2)-affine) | 32 | **unique**: ∏ z_j | degree 4 |
| odd-majority thresholds | 8 | no | — |
| axis decision lists (len ≤ 3) | 8,736 | no | **none at any length** (prefix-fixing argument) |
| decision trees | — | yes | **exactly 2^k leaves** (Kraft, exact) |

At every k the first-node witness was extracted for 100% of enumerated lists,
and every proper subcube (fewer than k fixed coordinates) carries non-constant
labels — the finite content of the tree-minimality argument.

## Scientific disposition

This closes the exact finite decoder frontier on the frozen witness,
absorbing and extending two existing strands: the T11.2 two-family witness
(constants, signed singles) and the empirical hostile-decoder studies
P11C–P11G (sparse/tree decoder attacks with scaling thresholds). The composite
claim is now family-relative and quantitative: no-answer-laundering fails for
every non-compositional family tested at any size (lists), holds for
composition at exactly the algebraic degree (character degree k) and exactly
2^k leaves (trees). The boundary statement C7 upgrades the manuscript claim
from an example to a mapped frontier.

## Not earned here

- The frontier is exact for the parity family of targets; other label classes
  (majority targets, mixed spectra) are not covered by this study.
- Decision-list non-realization beyond length 3 rests on the registered
  prefix-fixing argument (verified on all enumerated lists and by witness
  extraction), not on exhaustive enumeration at every length.
- No external promotion: internal evidence only, under no-self-authority
  (#977 §2.3).