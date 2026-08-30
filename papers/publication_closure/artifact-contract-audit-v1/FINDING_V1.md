# The #1701 artifact contract is not satisfied — measured, in one pass

The #1701 section "Common artifact contract for every new empirical successor"
lists fourteen required artifacts as fourteen checkboxes. They are **one
contract**, not fourteen tasks: they are ticked when the successors satisfy
them. This audits that in a single pass.

## Result: `CONTRACT_NOT_SATISFIED`

**65** empirical successor directories found. **0** satisfy the full contract.

| contract item | dirs having it | of 65 |
|---|---|---|
| PROTOCOL | 50 | 77% |
| RESULT | 48 | 74% |
| CLAIM_DISPOSITION | 33 | 51% |
| independent checker | 22 | 34% |
| SHA256SUMS | 21 | 32% |
| EXPECTED_TERMINALS | 17 | 26% |
| RESOURCE_ACCOUNTING | 4 | 6% |
| QUESTION | 3 | 5% |
| ADVERSE_AND_CANNOT_CHECK | 2 | 3% |
| BASELINES | 1 | 2% |
| CORPUS_MANIFEST | 1 | 2% |
| INCLUSION_EXCLUSION | 1 | 2% |

So all fourteen contract boxes correctly remain **unchecked**, and this says why
with a number rather than an impression. The debt is not uniform: protocol and
result discipline is broadly present, while corpus definition
(`CORPUS_MANIFEST`, `INCLUSION_EXCLUSION`, `BASELINES`) is essentially absent —
those three sit at 1 of 65.

That shape is informative. The programme has been rigorous about *freezing what
it will do* and *recording what happened*, and thin on *defining the population
it did it over*. Corpus definition is exactly what an external referee checks
first, so this is the highest-leverage artifact debt in the portfolio.

## Why a tool rather than an inspection

Re-running this is one command, so the contract's status is answerable at any
point rather than re-derived by hand each time the question comes up.

## Controls

A synthetic directory containing all twelve detectable artifacts is audited on
every run and must score full; it does. Without that, a coverage report of all
zeros would be indistinguishable from a matcher that never fires — which, given
that three items really do sit at 1 of 65, is the failure mode that matters
here.

## Scope

Presence only. It does not read any artifact's contents, so a present-but-empty
`BASELINES.json` counts as present. It also cannot see the two contract items
that are not files — "outcome-free protocol commit" and "manuscript update only
after evidence terminal is fixed" — which are ordering properties over git
history, not artifacts, and are excluded from the twelve.

`grants_authority: NONE`.

**Terminal:** `CONTRACT_NOT_SATISFIED__0_OF_65__CORPUS_DEFINITION_IS_THE_DEBT`

---

## Correction V1.1 — the first version penalised correct behaviour

The audit above required all twelve artifacts of every candidate. That is wrong
for one class of directory, and the exemplar is what exposed it.

`papers/orion-25-orion-research-harness/experiments/external-trust-domain-v1`
holds **every** contract artifact except `RESULT` — because it is a **frozen
protocol that has not been executed yet**. The contract's own item
"outcome-free protocol commit" endorses exactly that state. Dinging it for the
absence of a result inverts the discipline the contract is trying to enforce.

The audit now splits by phase. `RESULT`, `ADVERSE_AND_CANNOT_CHECK` and
`CLAIM_DISPOSITION` are required only of directories that have executed;
frozen protocols are held to the nine pre-execution items.

**Corrected result:**

| phase | dirs | satisfy applicable contract |
|---|---|---|
| executed | 48 | **0** (of 12 items) |
| frozen (protocol-only) | 17 | **1** (of 9 items) |

So the headline moves from `0 of 65` to `1 of 65`, and the one is
`external-trust-domain-v1` — the single directory in the portfolio that
demonstrates what full pre-execution compliance looks like. It should be the
template for the rest.

The substantive finding is unchanged and, if anything, sharper: **no executed
successor satisfies the contract**, and the corpus-definition items
(`CORPUS_MANIFEST`, `INCLUSION_EXCLUSION`, `BASELINES`) remain at 1 of 65 each —
all three occurrences being that same exemplar. Every other empirical result in
the portfolio was produced without a machine-readable statement of the
population it ran over.

**Corrected terminal:** `CONTRACT_NOT_SATISFIED__1_OF_65__ORION25_TRUST_DOMAIN_IS_THE_TEMPLATE`
