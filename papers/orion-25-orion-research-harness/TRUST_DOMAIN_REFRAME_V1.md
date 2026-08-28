# ORION-25 — trust-domain reframe V1

**Stable ID:** `ORION25.TRUST_DOMAIN_FRONTIER.v1`
**Created:** 2026-08-28 (wave-2, issue #1609 ORION-25 box; successor candidate from PR #1615 Priority 5)
**Status:** `HYPOTHESIS_ONLY` — candidate law, not a result.
**scientific_authority_delta:** `NONE`

This document does not promote, demote, reinterpret or extend any bound ORION-25
terminal. `P15_ACTIVE_CLAIM_AUTHORITY_V3.json` remains the active authority and
`promotion_allowed=false` remains in force. Nothing here is evidence.

---

## 1. What this reframes

The bound V2 attestation study composes **three** signed links (execution,
environment, publication), each signing the previous link's digest. Its frozen
adverse boundary is that under full key-set compromise the signature layer
detects nothing:

| bound finding (`P15_ACTIVE_CLAIM_AUTHORITY_V3.json`) | value |
|---|---|
| `attestation_base_chain_verification_rate` | `1.0` |
| `attestation_chain_plus_sei_gold_agreement` | `22/22` |
| `attestation_valid_workload_false_rejections` | `0` |
| `full_key_compromise_signature_detections` | `0` |
| `full_key_compromise_false_promotions` | `6` |

The manuscript already declares the qualitative boundary. `manuscript/chapters/
02-threat-model.tex` (out-of-scope threats) states the contract "does not protect
a fully compromised trust root", and `P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md`
states the study is "a composition-semantics experiment, **not** a key-management
or hardware-attestation claim".

**The reframe adds a name, a governing variable and a measurement to a boundary
the paper already declared in words.** It does not discover a defect, and it must
not be written as one. The threat model says *a* trust root, singular; the law
below makes the *count* of roots the variable that governs detection.

---

## 2. Candidate threshold law

### 2.1 Statement

Partition the attestations required by an acceptance rule into
**independently compromisable trust domains**. A trust domain is a set of signing
authorities that an adversary can compromise **as a unit**: one custody boundary,
one compromise event.

For an acceptance rule `R`, define its **compromise threshold** `T(R)` as the
minimum number of trust domains (or minimum attack cost over domains) whose
compromise suffices to construct a record that `R` accepts.

> **Law (candidate).** `T(R)` is determined by the number of independent trust
> domains `d` spanned by `R`, and is **invariant under chain length `k`** at
> fixed `d`. A serial `k`-link chain whose signing authorities share one
> compromise domain has `T = 1` for every `k`.

For an AND rule over `d` genuinely independent domains with per-domain compromise
probabilities `q_1..q_d`, the idealized false-promotion probability from key
compromise is `prod_d q_d`; with benign per-domain failure probabilities `f_d`,
the availability-side false-rejection probability is `1 - prod_d (1 - f_d)`.
Threshold (`t`-of-`k`) rules trade along that frontier.

### 2.2 Assumptions the law requires

| # | Assumption | Failure mode if violated |
|---|---|---|
| A1 | Domain independence: no shared credential store, host, operator, build pipeline, CI identity or root of trust. | Common-mode compromise; `prod_d q_d` collapses toward `max_d q_d`. |
| A2 | Compromise is atomic per domain: compromising a domain yields all its signing capability. | Partial-capability compromise makes `T` non-integral. |
| A3 | The acceptance rule genuinely requires all `d` domains (AND), not any-of. | An OR rule has `T = 1` regardless of `d`. |
| A4 | Verification is itself outside the compromised domains. | A compromised verifier accepts anything; `T` is undefined. |
| A5 | Benign domain failures are independent. | Correlated outage inflates false rejection beyond `1 - prod_d (1 - f_d)`. |

### 2.3 Boundary that survives the law

No cryptographic statement here establishes fact truth or scientific validity.
Raising `T` from 1 to `d` reduces false promotion **from key compromise**; it does
not admit science. A semantic admission layer (SEI) remains separately necessary,
and — per the bound V3 boundary — inherits key custody as a premise regardless of
`d`.

---

## 3. What the law predicts that "longer chain = more secure" does not

Chain length `k` and domain count `d` are **independently varyable**. The two
accounts diverge on the flat direction:

| | chain-length account | trust-domain law |
|---|---|---|
| detection vs `k` at fixed `d` | improves with `k` | **flat in `k`** |
| detection vs `d` at fixed `k` | unchanged | **steps with `d`** |
| a 3-link chain, one domain | "3x harder" | `T = 1`, identical to 1 link |
| a 1-link-per-domain, 3 domains | "no better than 1 link" | `T = 3` |
| cost vs `k` | rises | rises (cost is not flat in `k`) |

The decisive signature is therefore an **asymmetry**: cost scales in `k`, detection
does not. That asymmetry is measurable and is the point of the Phase-3 design.

The bound evidence is already consistent with the law and inconsistent with the
chain-length account: at `k = 3` the signature layer detects full key compromise
`0/6`. A chain-length account predicts that composing three signed links raises
the bar; it did not raise it at all.

---

## 4. How many independent trust domains does ORION-25 actually have?

**Answer: one nominal signing domain; zero custody-separated domains. `d = 1`,
`T = 1`, at `k = 3`.**

Traceable basis:

1. `top_tier/run_attestation_composition_v2.py:71-73` derives every role key from a
   committed constant:
   `seed = sha256(b"P15-ATTESTATION-COMPOSITION-V2-KEY-" + role + case_id)`,
   `Ed25519PrivateKey.from_private_bytes(seed)`.
   The three role keys are distinct **values** but share one origin: anyone with
   repository read access regenerates all three. There is no custody boundary
   between them, so no adversary must cross one.
2. `P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md` declares these "fixed test-only
   seeds" and disclaims key management — the design is scoped this way on purpose.
3. All three links are produced by one process, on one host, in one CI job
   (run `32664075763`; replay `32665597624`). One host compromise yields all
   three roles.

### 4.1 A-SPLICE is not a second data point — do not read it as one

A-SPLICE compromises the environment and publication keys, leaves the execution
key unused, and is detected 100%. This is **not** evidence that a second domain
resisted. The arm *stipulates* that the attacker declined to use the execution
key, which on this setup was freely derivable from the same committed constant.
It varies **how many keys the attacker elected to use**, all inside one domain —
it does not vary the number of domains.

Reading A-SPLICE together with A-COMPROMISE-FULL as a dose-response over trust
domains would be an overclaim. The corpus contains **no** variation in `d`.
That is precisely why the Phase-3 experiment is needed: `d` has never been varied,
so the law's central prediction has never been tested.

### 4.2 Where a second domain would have to come from

A genuine second domain requires a key whose private bytes are generated on, and
never leave, a host under separate control — not a second key derived from the
same source constant. Three sites are verified reachable (see
`experiments/execution-integrity-v1/PROTOCOL.json`), which makes `d = 3`
constructible.

---

## 5. Strongest falsifier

> **Falsifier.** Construct the `d = 3` custody-separated deployment and show that,
> under a matched attack model and after charging false rejection and overhead,
> its false-promotion resistance is **not** better than the `d = 1`, `k = 3`
> chain — either because a shared compromise path exists (common mode: shared CI
> identity, shared operator, shared image, shared secret store), or because the
> separated arm's confidence interval on false promotion overlaps the same-domain
> arm's.

Either outcome narrows the design claim rather than the law's scope, and both are
enumerated as terminals in `EXPECTED_TERMINALS.json`. A common-mode finding is the
more interesting negative: it would say that in this deployment class, nominal
domain separation does not purchase threshold, which directly limits what any
multi-root attestation architecture should be advertised as providing.

Secondary falsifier: if detection **does** improve with `k` at fixed `d = 1`, the
invariance clause is false as stated and the law must be withdrawn or amended.

---

## 6. Authority boundary

`scientific_authority_delta: NONE`. This document defines a candidate law and a
falsifier. It reports no outcome, changes no bound terminal, and creates no
`RESULT.json`. The `d = 1` count in section 4 is a reading of committed source and
protocol text, not a new measurement. Until
`experiments/execution-integrity-v1/` executes, the law is `HYPOTHESIS_ONLY` and
may not be cited as an ORION-25 finding.
