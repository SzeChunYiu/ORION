# P13+P14 live-Git acquisition increment V1

Status: `FROZEN_BEFORE_ANY_ACQUISITION_OUTPUT`. Successor of the frozen
acquisition pilot (`development/p13-p14-public-lifecycle-v1/`), which named
this increment: *"A later acquisition must use live Git, retain
command-receipt digests, verify object existence/direct-parent
ancestry/license blob bytes, and bind the exact protocol, runner, source
commit and environment. Manifest-only equality is prohibited as objective
gold."* This increment does exactly that and nothing more: it produces
acquisition receipts, derives no gold, evaluates no policy, and adds no
scientific authority (`scientific_authority_delta: NONE`). The issue #1086
external-campaign gate stays `OPEN`.

## Corpus/pilot split (recorded, not resolved)

Two frozen subject lists exist in this family: the pilot's 30 acquisition
targets (26 organizations) and the pinned corpus's 45 entries (22
organizations, 31 gold-eligible). They overlap by 8 repositories. The frozen
gold-derivation contract restricts gold to corpus entries at their pinned
shas; the 22 non-overlap pilot targets can therefore never yield gold under
the current contract. This increment acquires BOTH lists under their
applicable observation sets and records the split; it widens neither freeze.

## Fail-closed semantics

Any predicate error, timeout, or partial evidence yields `CANNOT_CHECK` for
that observation. Two planted violations (forged head sha, forged license
digest) are routed through the same predicates as real records and must
fire; otherwise the run terminal is `CANNOT_CHECK__CONTROL_FAILURE` and
nothing observed is evidence.

## Embedded rule of record (verbatim, as required by its status note)

```markdown
# P13+P14 lifecycle-contract gold-derivation rule (V1)

Status: **PROSPECTIVE_PROTOCOL_RULE (additive note)**. As of 2026-08-24 no
frozen external lifecycle-contract campaign design exists in this repository —
the frozen P14 external artifacts
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

Any external lifecycle-contract campaign conducted for the consolidated P13+P14
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
