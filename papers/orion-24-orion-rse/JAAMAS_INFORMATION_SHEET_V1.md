# ORION-24 — JAAMAS submission information sheet (V1)

JAAMAS requires a 1–2 page sheet with every submission, and returns submissions
whose sheet is incomplete or uninformative without review. It asks two questions
and warns that "We are the first to have done X" is not an acceptable answer to
the first without stating the importance of X.

## 1. What is the main claim, and why is it an important contribution?

**Claim.** Research generation and scientific promotion are separable, and the
separation can be specified independently of the system being judged and then
audited. ORION-RSE is a fail-closed recursive scientific-governance contract in
which a candidate system may produce hypotheses, evidence and interpretations
freely while a separately frozen specification decides what those outputs
warrant.

**Why it matters for agents.** Research agents already generate hypotheses,
retrieve literature, run code and revise artifacts faster than they can
determine what any of it scientifically warrants, and the tempting fix is to let
the generating system also score itself. That is a governance question with an
agents-specific shape: the judge is inside the loop it judges, so its
approvals are not evidence. This paper's contribution is showing the separation
is *specifiable* — the policy never sees the gold field, the specification is
authored independently of the implementation, and six ablations establish which
components carry the conformance rather than asserting it.

**What is not claimed.** This is not evidence that ORION improves real science.
The specification is internal to the programme, not a human external-adjudication
dataset, so P14C evaluates conformance to a separately frozen specification and
not truth about scientific governance. Broader correct-governance or
social-responsibility claims require two independent experts plus a
tie-break/custodian and remain `CANNOT_CHECK`.

## 2. What evidence is provided? Be precise.

**P14C, the sole central empirical authority.** 28 explicit frozen cases — four
precedence variants of each of seven semantic strata. **The inference unit is
the stratum, not the case**: the 28 are not independent draws and no interval is
computed as if they were, so accuracy here is a conformance count against a
frozen specification, not a rate over a sampled population.

| policy | disposition accuracy | false promotion | useful-discovery recall |
|---|---:|---:|---:|
| **ORION_RSE_FULL** | **1.0000** | **0.0000** | **1.0000** |
| `MULTI_REVIEW` | 0.857143 | 0.142857 | 1.0000 |
| `DONOR_AWARE_REVIEW` | 0.714286 | 0.285714 | 1.0000 |
| `REFLECTION_CHECKLIST` | 0.571429 | 0.428571 | 1.0000 |
| `RAW_POSITIVE` | 0.428571 | 0.535714 | 1.0000 |

Useful-discovery recall is reported precisely so the method cannot win by
blanket abstention — a policy that refuses everything scores perfectly on false
promotion and is useless.

**Construction controls.** Before every policy call the harness strips
`gold_disposition`, `rationale`, `case_id` and `stratum`; the policy receives
only factual booleans. Policies are implemented independently of the case table.
Six ablations separately remove evidence-integrity, freeze, identifiability,
donor, interaction and negative-history checks, and **all six lower disposition
accuracy**. Two independent evaluations produce an identical canonical SHA-256.

**Retained predecessors, neither carrying the claim.** P14A is a *measurement*,
not a comparative negative: its gates were unreachable under the frozen support,
so no reading of it in either direction is licensed. P14B is retained as
diagnostic because it reused gold it had a hand in producing. P14C is sole
central authority precisely because neither predecessor can carry an empirical
claim.

**External validation is blocked, not pending.** The P14D acquisition preflight
records all eight required artifacts absent and no trusted external custody
verifier, so the only admissible terminal is
`P14D_EXTERNAL_ACQUISITION_BLOCKED` and no external-validation authority exists.
