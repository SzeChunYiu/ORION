# A6 Phase 1 — donor matrix V3

**Status:** `SIX_UNDISPOSITIONED_FIELDS_CLOSED__DONOR_SUBTRACTION_ONLY`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. Like V2, this matrix can only narrow
novelty. Nothing here promotes a claim.

V2 covered five donor fields. ORION-18's own journal-readiness plan
(`papers/orion-18-epistemic-authority-autonomous-science/JOURNAL_READINESS.md`,
§2 "Nearest-work closure") requires eleven. V3 dispositions the six that no A6
document addressed.

## Integrity finding that motivated V3

A keyword sweep over all seventeen A6 documents reported the
research-integrity / scientific-authority field as covered in 17 of 17 files.
Every one of those matches was the boilerplate header line
`**Scientific authority delta:** NONE`. The field was covered in **zero**
documents. Coverage counted by keyword is not coverage; the sweep was re-run
against match context before any field below was called closed, and each field
here was confirmed absent from the corpus by reading the surrounding text, not
by counting hits.

## Fields dispositioned in V3

| Required donor field | Primary donor objects checked | What the donor already supplies | A6 consequence |
|---|---|---|---|
| information flow / non-interference | Goguen & Meseguer, *Security Policies and Security Models*, IEEE Symposium on Security and Privacy (1982); Rushby, *Noninterference, Transitivity, and Channel-Control Security Policies*, SRI CSL-92-02 (1992); Sabelfeld & Myers, *Language-Based Information-Flow Security*, IEEE Journal on Selected Areas in Communications (2003) | the definition of one domain not influencing another; intransitive variants that permit controlled downgrading through named channels; static enforcement by typing | This is the nearest parent to ORION-18's cross-domain authority laundering, and it is a **closer** parent than the authorization logics V2 named. "Effects of domain A must not reach domain B except through a declared channel" is donor, and intransitive non-interference already owns the declassification case. A6 may only own the constraint that the declared channel must itself carry a fresh authority-bearing premise. |
| evidence-backed permission graphs | Zhang et al., *FAVA: Formal Authorization for Verified Agents with Evidence-Backed Permission Graphs*, arXiv:2607.27267 (2026); *AID-Guard: Stateful Authorization for Delegated Agent Effects*, arXiv:2608.21159 (2026) | runtime permission decisions bound to evidence rather than to static tool scopes; permission state that evolves with observed data flow; delegated-effect authorization with explicit state | Binding a permission to the evidence that justifies it is donor, and recent enough that ORION-18 must cite it rather than present the idea as new. A6 retains only the repair-driven case: what happens when the evidence a permission rests on is *regenerated* rather than newly acquired. |
| policy cards / runtime governance | Mavračić, *Policy Cards: Machine-Readable Runtime Governance for Autonomous AI Agents*, arXiv:2510.24383 (2025), Zenodo DOI 10.5281/zenodo.17464706; *Deontic Policies for Runtime Governance of Agentic AI Systems*, arXiv:2606.19464 (2026) | a deployment-layer normative artifact carrying allow/deny rules, obligations and evidentiary requirements, with crosswalks to NIST AI RMF, ISO/IEC 42001 and the EU AI Act | Machine-readable obligation attached to a deployed agent is donor. ORION-18 must not present "the authority object travels with the agent" as new. A6 keeps only the typed-epoch semantics under which such an object becomes stale. |
| selective prediction / abstention | Chow, *On Optimum Recognition Error and Reject Tradeoff*, IEEE Transactions on Information Theory (1970); El-Yaniv & Wiener, *On the Foundations of Noise-Free Selective Classification*, JMLR 11 (2010); Liu et al., *AgentAbstain: Do LLM Agents Know When Not to Act?*, arXiv:2607.10059 (2026); *Agentic Abstention: Do Agents Know When to Stop Instead of Act?*, arXiv:2606.28733 (2026) | the reject option and its risk–coverage tradeoff; the sequential agentic form in which a system may answer, abstain, or gather more information | ORION-18's `CANNOT_CHECK` is the reject option. Calling it a distinct epistemic state does not make it one. A6 may only own the claim that `CANNOT_CHECK` is **non-compensatory** — that it cannot be traded against confidence elsewhere in the obligation — which the risk–coverage framing does not express. The calibration result must be reported against a plain abstention baseline or it measures nothing. |
| shielding / behavioural bounds | Bloem, Könighofer, Könighofer & Wang, *Shield Synthesis: Runtime Enforcement for Reactive Systems*, TACAS (2015); Alshiekh et al., *Safe Reinforcement Learning via Shielding*, AAAI (2018) | a synthesised runtime monitor that corrects or blocks actions so a temporal-logic safety property holds, with a correctness argument for the shield itself | Runtime enforcement of a behavioural bound is donor, including the guarantee that the enforcer is correct by construction. A6 must not claim novelty for "the authority check cannot be bypassed". What remains is that a shield enforces an *action* property, whereas the non-amplification constraint is a property of the *authority premise*, which no shield formulation targets. |
| research integrity / scientific authority | Committee on Publication Ethics (COPE) Core Practices; ICMJE *Recommendations for the Conduct, Reporting, Editing, and Publication of Scholarly Work in Medical Journals*; Wilkinson et al., *The FAIR Guiding Principles for Scientific Data Management and Stewardship*, Scientific Data (2016) | institutional definitions of authorship, accountability and correction; the obligation to retract rather than silently amend; machine-actionable provenance and identity requirements for scientific artifacts | Normative scientific authority is donor at the *institutional* level and is not formalised there. A6's contribution cannot be "science needs authority"; it can only be a machine-checkable semantics for the correction obligation these bodies state in prose. This field is a **positioning** parent, not a technical one, and must be cited as such rather than used to inflate a formal gap. |

## Effect on the surviving-claim tally

V2 recorded `DONOR` 6, `SPECIALIZATION` 5, `SURVIVING_NEW_CONSEQUENCE` 1 over
the twelve results it examined. V3 adds no result-level rows and therefore does
not change that tally. It changes the *risk* to the single survivor: the
intransitive non-interference parent (Rushby 1992) is closer to the
cross-domain laundering result than anything V2 checked, and the survivor must
be re-tested against it before it is defended. That re-test is not performed
here.

## What V3 does not close

- ORION-18 §2 also requires deontic / input-output / action logic and
  ETAS / effect-system dispositions. Both are partially present in earlier A6
  documents; neither has been checked for the delegation-revocation case, which
  `A6_PROPOSITION14_DONOR_CHECK_V1.md` treats only in passing.
- "Hostile exact-composition search" and "two no-material-change rounds"
  remain open. V3 is a first pass over six fields and cannot satisfy a
  stability criterion by itself.
- The `#287` novelty certificate is not refreshed by this document.

## Boundary

This is a donor matrix, not a priority certificate. Every entry can only
subtract from what ORION-18 may claim. If a source not listed here states the
composed repair/non-amplification result directly, this matrix must be amended
rather than the claim defended by terminology.

**Citation provenance.** The four recent arXiv donors (FAVA 2607.27267,
AID-Guard 2608.21159, Policy Cards 2510.24383, AgentAbstain 2607.10059) and the
Shield Synthesis, Goguen & Meseguer, and El-Yaniv & Wiener entries were located
and checked against published records for this document. The remaining entries
are standard references cited by title, venue and year only; volume, issue and
DOI were deliberately omitted rather than asserted from recollection, and must
be completed from the record before any of them enters a manuscript
bibliography.
