# ORION-23 — JAAMAS submission information sheet (V1)

JAAMAS requires a 1–2 page sheet with every submission, and returns submissions
whose sheet is incomplete or uninformative without review. It asks two questions
and warns that "We are the first to have done X" is not an acceptable answer to
the first without stating the importance of X.

## 1. What is the main claim, and why is it an important contribution?

**Claim.** State sufficiency is *responsibility-relative*. A compact state can be
current, provenanced and high-confidence with respect to the responsibility it
was built for, and still lack the distinctions a different responsibility
requires. Neither confidence continuity nor provenance continuity is evidence
that reuse is safe across such a change, and an explicit support/reopen contract
separates the cases where reuse is licensed from those where it is not.

**Why it matters for agents.** Agent systems reuse compact state across tasks
continuously — summaries, embeddings, extracted facts, cached certificates —
and the standard licences for that reuse are recency, provenance and confidence.
This paper's evidence is that all three can hold while reuse is unsound, and
that the failure is silent: nothing in the state signals its own insufficiency,
so the system does not abstain and no error surfaces until a downstream decision
is already wrong. That is a live failure mode in multi-agent memory and
tool-state, not a hypothetical one, and it is the reason responsibility must be
registered rather than inferred.

**What is not claimed.** Not universal workflow safety, not real-agent
deployment safety, and no clinical or high-stakes use. The bound is stated with
every result below.

## 2. What evidence is provided? Be precise.

**Real-data responsibility shift (17,970 episodes).** A state learned for a
parity responsibility, reused under an exact digit-identity responsibility:

| arm | exact-digit accuracy | unsupported exact-digit reuse |
|---|---|---|
| RCS | 0.9699 | **0** |
| confidence-only | 0.3957 | 0.7774 |
| provenance-only / unqualified | 0.2376 | **1.0** |

RCS reads 33 floats per episode against always-raw's 64 — a 48.4375% reduction —
while matching always-raw's task accuracies exactly (combined 0.9435,
exact-digit 0.9699, parity 0.9171). The saving is not bought with accuracy.
Provenance-only reuses without support in *every* episode.

**Donor-complete comparison (48 episodes, 4 cells × 12).** The question is
whether responsibility registration reduces to the provenance axis a
donor-complete memory already has. Both donor arms — including `D2_PLUS`, the
strongest demand-graded form — commit **12** unsupported reuses at **36/48**;
RCS and `COMPOSED` are **48/48** with zero, and `COMPOSED` is cheaper on reads
(5.0 vs 6.25). Protocol and gold dispositions frozen before the runner;
independent checker reports zero invariant failures.

**Drift-bounded certificate transport (60 cases, 20 per stratum).**
`UNCONDITIONAL` transports 40 certificates it has not earned (20 content-invalid,
20 unsound under the frozen predicate); `SIGNATURE_ONLY` refuses all 20 sound
redundant transports; `CONDITIONAL_DRIFT_BOUNDED` is exact — 0 unsound, 0
needless, 60/60 — and cheaper than re-issue on the redundant stratum (8.0 vs
12.0 mean literal reads). Two implementations agree byte-for-byte.

**Retained negative.** P13A's empirical safety-cost endpoint is
`WITHHELD`. Harm was scored by the same construction that produced the action,
so across all 3,840 enumerated points there were zero opportunities for harm to
move. A self-entailed endpoint cannot discriminate a safe system from an unsafe
one, so no reading of it — favourable or adverse — is licensed. It is retained
for what it does establish: that the endpoint's construction, not the system's
behaviour, is what the number measured.

**Scope of agreement.** Every "independent" check above is a second
implementation inside the same programme, not external adjudication. External
scientific adjudication has not occurred and is not claimed.
