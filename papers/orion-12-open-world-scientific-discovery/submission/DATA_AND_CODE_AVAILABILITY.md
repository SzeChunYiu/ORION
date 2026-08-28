# Data, code, and reproducibility — ORION-12

The manuscript carries its own Data and code availability section, which lists
every artifact path and digest the results depend on. This file is the
submission-side summary and does not replace it.

## Data availability

| Artifact | Supports | SHA-256 |
|---|---|---|
| `protocol/CLAIM_LEDGER_V1.json` | Sentence-level binding of every ledgered claim to its evidence, with numeric bindings re-derived at check time | `ccbea5c574c86adf4cbc92e29c7c69a6a226f53f3fdd52160181fe7592c5d5aa` |
| `evidence/P2_INTEGRATED_CLAIM_BINDINGS_V1.json` | Source-derived facts behind the integrated claims, including the 96,241-row five-review comparison | `7c0887293666853559e8c4a2324f7d9975ac7d6c8cef50a53dde8a2dea8670cb` |
| `journal_package/current_revision/manuscript.pdf` | The 47-page PDF compiled from the submitted source | `1906953b90f760551f56b8688bc1bbdaf11061e6ad459cff19e01f779d84f09e` |

Prospective protocols, measurement plans, statistical plans, and the external
access audit are committed under `protocol/`. The offline complete-gold
companion, external benchmark artifacts, and the public screening transport
records are listed with their own digests in the manuscript's availability
section.

## Code availability

Four checkers under `scripts/` are the operative verification path:

- `check_claim_ledger.py --check` — verifies that every ledgered sentence is
  still present, that its bound numbers still match the evidence artifacts they
  cite, and that no outcome is asserted in the abstract or conclusion without a
  ledger entry. It reports clean at the submitted revision.
- `check_p2_assimilation.py` — validates the assimilation ledger and holds
  saturation as not claimed.
- `check_p2_v2.py` — validates that the widening surface is structurally
  fail-closed.
- `check_manuscript_typography.py` — render-side typography audit, run against a
  build log.

The journal package inventory is validated by
`research/paper-programme-v1/journal_package/check_journal_package.py`, and the
render closure state is regenerated, not hand-maintained, by
`scripts/write_render_closure_state.py`.

## Reproducibility statement

1. Run the four checkers above. The claim ledger check is the important one: it
   is what prevents a manuscript number from drifting away from the evidence it
   cites.
2. Recompile the manuscript and confirm 47 pages with no undefined references
   and no overfull boxes.
3. Reproduce the adverse results, not only the positive ones. The public
   screening comparison must reproduce the candidate losing to its donor on both
   endpoints in all five reviews. The external matched campaign must reproduce
   as a failed provider-validity gate, and must not be recorded as a null.

A reproduction that recovers the 400/400 exact-contract result and stops has
reproduced the part of this paper that is easiest to like and none of the part
that sets its boundary.

## Scope of the digests

The digests bind evidence and chronology. They do not establish an open-world
benefit, which the paper explicitly reports as unconfirmed, and they do not
grant the package current submission authority, which remains an open claim in
the package manifest.
