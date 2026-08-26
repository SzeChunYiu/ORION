# ORION-23+ORION-24 objective-gold derivation contract (V1)

Companion protocol doc for `P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json`
(schema `ORION.P13P14.ObjectiveGoldDerivationContract.v1`). The JSON is the
machine-checkable contract of record; this doc explains it and embeds the
binding rule verbatim as that rule requires.

Status: **FROZEN_DERIVATION_CONTRACT**. No gold has been derived, no campaign
has executed, no outcome has been accessed (`results_exist`,
`campaign_executed`, `outcome_accessed` are all `false` in the JSON). This
artifact must never be cited as evidence that any lifecycle-contract campaign
passed.

## What this freezes

Issue #1086 (consolidated ORION-23+ORION-24) requires: *derive gold only from objective
facts: object/hash existence, ancestry, tag/signature, test exit and timestamp
order.* This contract turns that requirement into five admissible fact classes,
each with a single machine-checkable predicate and a closed label set, plus
fail-closed semantics: any predicate error, ambiguity, timeout or partial
evidence yields `CANNOT_CHECK` for that fact. No label is ever inferred from
absence of evidence, from model or author opinion, or by interpolating between
recorded facts.

Derivation preconditions (full text in the JSON):

- the subject repository must be an entry of
  `P13_P14_PINNED_REPOSITORY_CORPUS_V1.json` at its recorded `pinned_sha`;
- the entry's license must be `VERIFIED_WITH_URL_AND_DATE` — `CANNOT_CHECK__LICENSE_UNCLEAR`
  entries are pinned for record only and yield no gold;
- gold is derived only inside a clone whose HEAD equals the pinned sha,
  asserted before and after derivation.

## Binding

The contract JSON binds
`P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md` by SHA-256 and operationalises
its five numbered items; nothing in the contract relaxes, widens or reinterprets
the rule. The rule's own status note requires verbatim embedding in any frozen
design artifact of this campaign family; the rule is therefore embedded below
exactly as it stands at the bound hash.

## Embedded rule of record (verbatim)

```markdown
# ORION-23+ORION-24 lifecycle-contract gold-derivation rule (V1)

Status: **PROSPECTIVE_PROTOCOL_RULE (additive note)**. As of 2026-08-24 no
frozen external lifecycle-contract campaign design exists in this repository —
the frozen ORION-24 external artifacts
(`top_tier/P14_EXTERNAL_GOVERNANCE_PROTOCOL_V1.md`,
`top_tier/external_v1/P14_EXTERNAL_PILOT_PROTOCOL_V1.md`,
`P14D_BLINDED_EXTERNAL_VALIDATION_ACQUISITION_PROTOCOL_V1.md`) are
governance-judgment and external-validation acquisition contracts, not a
lifecycle-contract campaign design. The 30–50 pinned repositories from at
least five unrelated organizations required by issue #1086 therefore remains
an **OPEN** campaign requirement. When such a campaign design is frozen, this
rule must be embedded in that frozen design artifact verbatim; until then this
note is the binding rule of record for any such campaign.

## Rule

Any external lifecycle-contract campaign conducted for the consolidated ORION-23+ORION-24
scope (issue #1086 decision D7) must derive gold **only** from objective,
machine-checkable facts:

1. **object/hash existence** — the referenced object (commit, blob, tree,
   artifact) exists and its content digest matches the claimed digest;
2. **ancestry** — parent/child relations (commit ancestry, merge structure,
   derivation chains) hold as claimed;
3. **tag/signature** — the claimed tag, signed tag or signature exists, is
   well-formed, and resolves to the claimed object;
4. **test exit** — the recorded test/CI exit status is the recorded status for
   the recorded revision, with no post-hoc mutation;
5. **timestamp order** — event timestamps are internally ordered as claimed
   (freeze before execution, protocol before result, etc.).

Gold derived from anything else — semantic quality judgments, responsibility
or social appropriateness judgments, model- or author-authored opinions about
whether a decision was *correct* — is inadmissible as gold. Those judgments
remain **CANNOT_CHECK** at the campaign layer unless adjudicated under the
blinded external protocol with two independent experts plus a
tie-break/custodian.

## Non-bypass boundaries (inherited from the portfolio disposition)

- ORION itself must **never** be used as an external subject of its own
  lifecycle-contract campaign.
- Public online data does not create independent adjudication.
- An AI session, a local hash, same-owner replay or same-owner CI does not
  create protected confirmation.
- Missing license, gold, comparator, custody or semantic authority remains
  CANNOT_CHECK.

This rule adds no scientific authority; it constrains how future gold may be
constructed (`scientific_authority_delta: NONE`).
```

## Boundary

Freezing these predicates adds no scientific authority
(`scientific_authority_delta: NONE`). Broader correct-governance or
social-responsibility claims remain CANNOT_CHECK without two independent
experts plus tie-break/custodian; ORION is never a subject of its own campaign;
public data and local hashes do not create independent adjudication.
