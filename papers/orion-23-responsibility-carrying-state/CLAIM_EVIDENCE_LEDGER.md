# ORION-23 Claim–Evidence Ledger

**Stable ID:** ORION-23  
**Issues:** #666, #668

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| sufficiency is relative to a named downstream responsibility in the registered world | SUPPORTED / EXACT | equivalence-class support matrix | exact constructed-world result |
| historical P14A combined gate passed | **NEGATIVE / FALSE** | `0.0556640625 > 0.05` | never relabel positive |
| historical exact ladder itself matches intended Z1/Z2/Z3 responsibilities | SUPPORTED / EXACT | full enumeration | mathematical/control construction only |
| RCS has zero unsafe reuse in P13A | **AUTHORITY WITHHELD / CANNOT_CHECK** | `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` | self-scored zero over zero reachable harm opportunities |
| confidence-only has zero unsafe reuse | FALSE | 0.215576 unsafe rate | cannot claim confidence is equivalent |
| provenance-only has zero unsafe reuse | FALSE | 0.396159 unsafe rate | cannot claim provenance is equivalent |
| RCS verified correctness is 0.980713 | SUPPORTED | P13A | registered benchmark |
| RCS cost is materially below always raw | SUPPORTED | 2.8747 vs 5.7319 | controlled cost units; ~49.8% lower |
| RCS degenerates to always reopen | DESCRIPTIVE FALSE | frozen action table | not an independently graded safety endpoint |
| RCS emits CANNOT_CHECK on certificate-declared unsupported/nonrecoverable cases | CONDITIONAL INTERFACE INVARIANT | frozen rule; 237 historical cases | conditional on certificate correctness |
| V1 runner alone satisfied every protocol gate | **FALSE / CORRECTED** | hostile PR review | replay gate was omitted from terminal path |
| exact frozen P13A runner is byte-identical across two fresh executions | **SUPPORTED / REPLAY-ADJUDICATED** | V2 adjudicator | both SHA-256 = `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f` |
| responsibility-carrying state eliminates unsafe reuse while avoiding always-reopen cost in the controlled benchmark | **NOT AUTHORIZED** | `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` | P13B requires independently graded support and matched frontier |
| authenticated RCS rejects omitted, overbroad, forged and stale certificates without gold-scored unsafe reuse in the registered finite panel | **SUPPORTED / CONTROLLED P13B** | `P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_RESULT_V1.json` | 30 live mutation opportunities per world; zero authenticated unsafe reuse; valid-panel cost ratio 0.6111 vs always raw |
| composed authenticated RCS has zero unsafe reuse, rejects every scheduled corruption, stays correct and pays 0.539x always-raw cost in the registered composed finite world | **SUPPORTED / CONTROLLED P13C** | `P13C_COMPOSED_RESULT_V1.json`; receipt `P13C_COMPOSED_RESULT_RECEIPT_V1.md`; 11/11 gates green; terminal `P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED` | 12,288 episodes (seed 2026082113), 2,457 scheduled corruptions all rejected; verified correct 0.97933 (noninferior to always-raw 0.95247 and unverified RCS 0.98063); zero unnecessary reopens on the 9,831 valid-certificate episodes; 254 exact `CANNOT_CHECK`; byte-identical two-subprocess replay SHA-256 `645961cf01afe15f1b5976244b76b846c31d3c6119af4fbbc031e4b2a3611e57` |
| the trusting comparator unverified RCS commits unsafe reuse under the same corruption register | **SUPPORTED / CONTROLLED P13C** | `P13C_COMPOSED_RESULT_V1.json` `summary.arms.UNVERIFIED_RCS` | 330 unsafe reuses (FORGED 66, OVERBROAD 87, STALE 177; rate 0.0269) plus 123 adversary-induced unnecessary reopens under omitted support — registered composed finite world only |
| broader correct-governance / social-responsibility claims for lifecycle contracts | **CANNOT_CHECK** | `P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json` (issue #1086 decision D7) | requires two independent experts plus tie-break/custodian; no artifact in this repository provides them |
| external lifecycle-contract campaign gold derivation | **PROSPECTIVE RULE / OPEN** | `P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md` | gold only from object/hash existence, ancestry, tag/signature, test exit, timestamp order; never ORION as external subject; 30–50 pinned repositories from >=5 unrelated organizations remains OPEN |
| real-agent / safety-critical superiority | OPEN | no external domain result | not authorized |

## Evidence correction

`P13_ACTIVE_CLAIM_AUTHORITY_V1.json` remains the historical P13A boundary.
Current `P13_ACTIVE_CLAIM_AUTHORITY_V2.json` retains the exact core, preserves the
P13A self-scored failure, and activates the bounded P13B result. Active terminal:
`P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED`.
Active authority is split. `P13_ACTIVE_CLAIM_AUTHORITY_V1.json` keeps
`ORION-23.EXACT.RESPONSIBILITY_RELATIVE_SUPPORT` as `SUPPORTED_EXACT` and sets
`P13A.EMPIRICAL.SAFETY_COST_SUPERIORITY` to `CANNOT_CHECK`. Active terminal:
`P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`.

**V3 correction (2026-08-24, issue #1086 ORION-23–ORION-25 lane):**
`P13_ACTIVE_CLAIM_AUTHORITY_V3.json` activates the composed P13C leaf on top of
the unchanged V2 leaves; V2 remains the active authority for the P13B leaf (the
recursive-resolution ledger continues to pin its ORION-23.B item to V2). V3 active
terminal: `P13_CONTROLLED_COMPOSED_SAFETY_EFFICACY_AUTHORITY_SUPPORTED`. V3 adds
no external authority: the P13C leaf is scoped to the registered composed finite
world, and `EXTERNAL_VALIDATION`, `REAL_AGENT_SAFETY`,
`POPULATION_GENERALIZATION`, `P13C_COMPOSED_RESULT_AS_EXTERNAL_VALIDATION` and
`P13C_COMPOSED_RESULT_AS_POPULATION_EVIDENCE` remain forbidden promotions.
Under issue #1086 decision D7 the paper's supported scope is narrowed to
machine-verifiable lifecycle contracts (manuscript section 8.1); broader
correct-governance and social-responsibility claims stay CANNOT_CHECK.

The original P13A runner evaluated the frozen scientific efficacy/safety/cost gates but did not include the protocol's byte-identical replay requirement in its terminal decision. The V1 runner terminal is therefore **non-authoritative alone**. This does not alter the benchmark or any result.

`verify_p13a_protocol_adjudication_v2.py` runs the exact unchanged V1 executable twice in fresh subprocess directories, hashes the entire canonical payload, verifies all frozen scientific gates, and then adjudicates the protocol terminal. Both runs reproduce SHA-256 `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`. No task, seed, threshold, comparator, recovery rule, resource cost or outcome was changed.

## Donor subtraction

- Statistical sufficiency/state abstraction own task-relative information preservation.
- Selective prediction owns confidence/abstention gating.
- Provenance/evidence-tracing systems own lineage and execution provenance.
- STALE-style work owns memory invalidation after later observations.
- Proof-carrying agent/action systems own certificate-bearing runtime governance.

## Residual novelty

The supported residual is the exact, conditional **responsibility-scoped state
authority** interface plus P13B's controlled authenticated-certificate corruption
result. The gold is separate from the certificate but locally authored, so
external safety authority remains open. `PROVENANCE_ONLY` and `UNQUALIFIED` are
authority** interface. The efficacy claim is prospective: it requires a P13B
certificate whose declared support can disagree with independently graded gold,
plus a matched cost/correctness frontier. `PROVENANCE_ONLY` and `UNQUALIFIED` are
identical policies in P13A and cannot count as two comparisons.

## Strongest authorized headline

> P13A's self-scored zero-harm claim remains withheld. In the prospectively frozen
> P13B finite panel, all four certificate corruptions have live denominators,
> authenticated RCS makes zero gold-scored unsafe reuses, and valid-panel cost is
> 0.6111 times always raw.
> The registered finite construction proves that sufficiency is
> responsibility-relative and the RCS interface conditionally refuses reuse
> outside declared support. P13A's empirical zero-harm claim is withheld because
> its harm predicate is entailed by the action rule; P13B must grade against
> independently defined gold support.
