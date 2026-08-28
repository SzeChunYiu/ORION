# P13C composed safety-efficacy protocol V1

**Status:** frozen BEFORE the composed benchmark is executed on this branch. This is the upward successor named for P13 by the resolution ledger: P13A proved exact responsibility-relative support on a randomized efficacy benchmark with **no adversary**, and P13B proved authenticated-certificate corruption safety on a registered 30-case panel with **no randomized families and no exactness matrix**. Neither parent established the conjunction. P13C composes both: the P13B certificate mechanism transplanted onto the P13A efficacy benchmark, over a strictly larger certificate class, under the full P13B corruption register interleaved by a frozen schedule.

This study does not alter any frozen parent artifact: `P13A_INDEPENDENT_RCS_EFFICACY_PROTOCOL_V1.md`, `P13A_RCS_SAFETY_COST_RESULT_RECEIPT_V1.json`, `run_p13a_rcs_efficacy_v1.py`, `P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_PROTOCOL_V1.md`, `P13B_GOLD_SUPPORT_SPEC_V1.json`, `P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_RESULT_V1.json`, `src/orion/study/p13/authenticated_successor.py`, and both active-claim-authority files are untouched (certificate functions are imported, not copied).

## 1. Registered gold specification (the reconciliation)

Parent gold conventions differ: P13B's spec demands `[x,m,r]` for INTERVENE (a registered finite-world convention), while P13A's truth model computes INTERVENE from `{x,m}` only. P13C resolves this by registering `P13C_COMPOSED_GOLD_SPEC_V1.json` — schema-identical to P13B's (`ORION.P13B.GoldSupportSpec.v1`, same six state forms, same subset rule `gold_support(Z,t) := requirements(t) ⊆ vars(Z)`) — with task_requirements equal to the **exact input sets of the P13A truth functions**: PREDICT `[x]`, DECIDE `[x]`, INTERVENE `[x,m]`, VERIFY `[x,m]`, REPAIR `[r]`. Under this spec the subset rule reproduces the P13A support semantics exactly, with the parent forms embedded as `Z5` (P13A Z1, variables `{x}`) and `Z1` (P13A Z2, variables `{x,m}`). Gate G1 verifies this equivalence live, including P13A's exhaustive responsibility matrix.

The certificate class is thereby **larger than either parent's**: six forms with support sizes {2,2,3,4,5,5} of five tasks, versus P13A's sampled two forms and P13B's fixed panel.

## 2. Certificate machinery (imported, not reimplemented)

`valid_certificate`, `validate_certificate`, `corrupt_certificate`, and `canonical_text` are imported unchanged from `src/orion/study/p13/authenticated_successor.py` and parameterized by the P13C spec. Issuer binding (`ORION_P13B_TRUST_ROOT_V1`), epoch (2), canonical-JSON SHA-256 digests, witness checks, and the four corruption worlds (OMITTED_SUPPORT, OVERBROAD_SUPPORT, FORGED_SUPPORT, STALE_EPOCH) are the parent P13B semantics verbatim.

## 3. Episode generator (parent P13A verbatim except the form class)

Seed `2026082113`; 24 families × 512 episodes = 12,288; per family `p_m, p_r ~ U(0.65, 0.95)`; per episode `x ∈ {−1,1}` uniform, `m = ±1` with `P(+1)=p_m`, `r = ±1` with `P(+1)=p_r`, `recover ~ Bernoulli(0.95)`, task uniform over the five, and **`z` uniform over all six forms `Z1..Z6`** (parent sampled two). Randomness is stdlib `random.Random(2026082113)` (distribution-identical to the parent's `numpy.default_rng` usage; the parent stream is not reproducible across the different form space, and stream identity is not claimed). Truth functions are the parent's: PREDICT/DECIDE `= x`, INTERVENE/VERIFY `= x·m`, REPAIR `= r`. Compact prediction from a form generalizes the parent's: the truth value when the task's inputs are contained in the form's variables, else the majority-map prediction (`x·map_m` for INTERVENE/VERIFY with `map_m = sign(p_m − 0.5)`, `map_r` for REPAIR).

## 4. Corruption schedule (frozen)

Let `i` be the global 0-based episode index (family-major). Episode `i` is **corrupted** iff `i mod 5 = 4` (exactly 2,457 of 12,288), with world `= WORLDS[(i // 5) mod 4]`. In a corrupted episode the form's valid certificate is replaced by `corrupt_certificate(valid, world, spec, z)`; the certificate is **not** re-validated before the arms act (that is the arms' job). Every scheduled corruption must be rejected by `validate_certificate` (gate G7).

## 5. Arms (five)

| Arm | Decision rule |
|---|---|
| `UNQUALIFIED` | always REUSE (ignores the certificate) |
| `CONFIDENCE_ONLY` | parent's rule verbatim (ignores certificates; REUSE iff confidence ≥ 0.80, where confidence is 1 on supported tasks, `max(p, 1−p)` on the raw variable otherwise) |
| `UNVERIFIED_RCS` | REUSE iff `declared_support[task]` — trusts declarations without validation |
| `AUTHENTICATED_RCS` | validate the certificate; if **invalid** → REOPEN if `recover` else CANNOT_CHECK (never reuse); if **valid** → REUSE iff declared (which equals gold), else REOPEN/CANNOT_CHECK by `recover` |
| `ALWAYS_RAW` | parent verbatim (REOPEN if `recover` else CANNOT_CHECK) |

Costs are the parent's unchanged: REUSE 1.0, REOPEN 6.0, CANNOT_CHECK 0.5. Validation is not surcharged (disclosed; this favors the authenticated arm by at most the validation cost, which the parent P13B likewise did not charge).

Metrics (parent definitions verbatim): unsafe reuse = REUSE on a gold-unsupported task; verified correct = REUSE-with-correct-prediction or REOPEN; unnecessary reopen = REOPEN on a gold-supported task; cannot-check counted separately.

## 6. Frozen gates

The runner fails closed unless ALL hold, reporting full counts:

1. **G1 gold/truth consistency.** The P13C spec's subset rule reproduces P13A's support sets under the parent form mapping, and the exhaustive responsibility matrix over the full `(x,m,r)` support cube matches the expected exact matrix for every registered form.
2. **G2 authenticated zero unsafe reuse, overall.** Zero gold-false reuses across all 12,288 episodes, corrupted included.
3. **G3 authenticated zero unnecessary reopen on the valid-certificate panel.**
4. **G4 authenticated verified-correct ≥ ALWAYS_RAW − 0.01** (parent noninferiority margin).
5. **G5 authenticated verified-correct ≥ UNVERIFIED_RCS − 0.01** (authentication costs at most 1 pp of correctness versus blind trust — the composition's efficacy-preservation clause against the strongest trusting comparator).
6. **G6 authenticated mean cost ≤ 0.70 × ALWAYS_RAW, overall** (corrupted episodes included).
7. **G7 every scheduled corrupted certificate rejected** by `validate_certificate`; count reported exactly.
8. **G8 unverified live violations.** UNVERIFIED_RCS has unsafe reuse > 0 in each of OVERBROAD, FORGED, STALE_EPOCH, and unnecessary reopen > 0 in OMITTED (the omitted world attacks efficacy, not safety — parent P13B observed the same split).
9. **G9 authenticated cannot-check exactness.** The authenticated arm's CANNOT_CHECK count equals the independently recounted stream expectation: #(valid ∧ gold-false ∧ ¬recover) + #(invalid ∧ ¬recover).
10. **G10 parent-form subpanel reproduction.** On the valid-certificate subpanel restricted to the parent forms {Z5, Z1}, the authenticated arm reproduces the P13A gates: zero unsafe reuse, zero unnecessary reopen, mean cost ≤ 0.70 × ALWAYS_RAW on the same subpanel.
11. **G11 byte-identical replay.** Two fresh subprocesses produce byte-identical cores (parent P13B supervisor pattern).

Terminal on all gates green: `P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED`; otherwise `P13C_COMPOSED_SAFETY_EFFICACY_GATE_NOT_MET`. Both outcomes are publishable; neither edits any parent artifact.

## 7. Authority boundary

Registered composed finite world: seeded randomized families, six-form certificate class, four-world corruption register at a frozen 1-in-5 schedule. No external validation, real-agent safety, population generalization, certificate-authority independence, or deployment authority is claimed or granted; the parent boundaries are inherited unchanged and neither parent's forbidden-promotions list is extended by this study.
