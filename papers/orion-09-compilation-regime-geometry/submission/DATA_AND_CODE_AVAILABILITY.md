# Data, code, and reproducibility — ORION-09

## Data availability

| Artifact | Supports | SHA-256 |
|---|---|---|
| `research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json` | The StabPrep refutation: zero error unachievable at any budget, error floor 43 over the 1,146-instance exhaustive domain, 12 mixed feature cells | `d3353ce926b1f2ff2ecab3da68c4fbd545ec820a9e372d6f288ec9daed1b6e82` |
| `research/extensions/orion-qg/QG10_INTERVAL_GEOMETRY_RESULTS.json` | Interval and support-bound geometry underpinning the tightening ladder | `61768d29d9e4a740e0900f50a41a8d723487a1945eeb85a6647376fd947eeb61` |
| `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` | The all-`n` composition receipt for the founding support result | `b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875` |
| `papers/orion-09-compilation-regime-geometry/CLAIM_LEDGER_V2.md` | The claim ceiling this manuscript is written to | `50105ed70e6c57e86704e392532c5a282261ba821aab622d0527d51a3cfc005d` |

Analyzers and results for the mapping programme are committed under
`research/extensions/orion-qg/`, with frozen lane protocols under
`development/orion-qg-regime-geometry/`. The founding results additionally bind
to receipts under `research/extensions/orion-q/`.

## Code availability

`research/extensions/orion-qg/qg15b_predicate_language.py` generates the
predicate-language result, and `qg10_interval_geometry.py` the interval
geometry. Both are deterministic under their recorded caps; the per-cell node
budget for the predicate search is recorded in the result file.

## Reproducibility statement

1. Reproduce the tightening ladder in order. A first valid support bound is not
   assumed tight, and the paper's point is that a semantics-derived bound was
   loose by a large factor. Recovering only the final number loses the result.
2. Reproduce the cross-family transfer, then the refutation. The third family is
   not an appendix: it is what converts the claim from a boundary law into a
   mapping discipline.
3. Confirm that zero error remains unachievable at any budget on the frozen
   vocabulary, and that the floor is attributable to mixed feature cells rather
   than to search truncation. The result file records that cells were truncated;
   the floor claim is a lower bound on error, which truncation cannot weaken.

## Scope of the digests

These digests bind exact, machine-checked, finite-domain measurements under
stated grammars and objectives. They carry no physical quantum-advantage claim,
and the refutation explicitly forbids reading any of the positive transfers as a
universal low-order law.
