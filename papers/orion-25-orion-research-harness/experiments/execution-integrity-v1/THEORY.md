# THEORY — execution integrity under independent trust domains (V1)

**Successor ID:** `ORION25.TRUST_DOMAIN_FRONTIER.v1`
**Parent authority (unchanged):** `../../P15_ACTIVE_CLAIM_AUTHORITY_V3.json`
**Reframe:** `../../TRUST_DOMAIN_REFRAME_V1.md`
**Status:** `PREREGISTERED_NOT_EXECUTED` · **scientific_authority_delta:** `NONE`

No result exists. There is deliberately no `RESULT.json` in this directory. Nothing
here promotes, demotes or reinterprets any bound ORION-25 terminal.

---

## 1. Question

Does execution-integrity strength come from the **number of independent trust
domains** `d` spanned by an acceptance rule, rather than from the **length** `k` of
the attestation chain — and what does buying `d > 1` cost in false rejection and
runtime?

## 2. Mechanisms under test

| | mechanism | prediction: detection vs `k` at fixed `d` | prediction: detection vs `d` at fixed `k` |
|---|---|---|---|
| M1 | chain length (incumbent reading) | improves | unchanged |
| M2 | trust-domain threshold law | **flat** | **steps** |

`k` and `d` are varied independently. This is the discriminator: the two mechanisms
disagree about which direction is flat, so no outcome is consistent with both.

## 3. Hypotheses

- **H1 (invariance in `k`).** At `d = 1`, key-compromise false promotion does not
  decrease as `k` grows from 1 to 5.
- **H2 (step in `d`).** At `k = 3`, key-compromise false promotion under an
  adversary limited to `c < d` domains falls to zero when `c < d`, and is
  unaffected by `k`.
- **H3 (frontier cost).** Raising `d` raises false rejection and runtime; the
  design must report both, not detection alone.
- **H4 (admission is not purchased).** Even at `d = 3` with zero key-compromise
  false promotion, `CHAIN_AS_SCIENCE` still false-promotes scientifically invalid
  content, because signature validity is not scientific validity.

H4 is the guard against the experiment being read as "more domains = valid
science". It is expected to hold and its failure would indicate an instrumentation
error, not a discovery.

## 4. Why the existing evidence cannot answer this

`P15_ACTIVE_CLAIM_AUTHORITY_V3.json` binds `full_key_compromise_signature_
detections = 0` at `k = 3`. Every role key in that study derives from one committed
constant in `run_attestation_composition_v2.py:71-73`, so `d = 1` throughout. The
bound corpus has **no variation in `d`** and therefore cannot separate M1 from M2.

A-SPLICE is not a partial `d` variation: it stipulates that the adversary declined
to use a key that was freely derivable from the same source. See
`../../TRUST_DOMAIN_REFRAME_V1.md` section 4.1.

## 5. Domain construction

A trust domain here is a host on which a role key is **generated locally and whose
private bytes never leave it**. Only the public key and the signature cross the
boundary. Three sites are verified reachable and carry independent
`cryptography` builds:

| domain | host | platform | python | cryptography |
|---|---|---|---|---|
| D-CI | GitHub Actions runner | linux x86_64 | per workflow image | per workflow image |
| D-OLD | `billy-old` (`billy-laptop-old`) | Linux x86_64 | 3.14.4 | 46.0.5 |
| D-HPC | `lunarc` (`cosmos2.int.lunarc`) | Linux x86_64 | 3.11.5 | 41.0.5 |

Version diversity is deliberate: byte-identical chain verification across three
library builds is a stronger replay claim than byte replay on one image.

**Independence is a claim to be audited, not assumed.** A1 in the reframe requires
no shared credential store, operator, image or root of trust. These three sites
share a human operator, which is a real common-mode path and must be recorded as a
declared residual, not hidden. The `COMMON_MODE_COLLAPSE` terminal exists for the
case where the audit finds a shared path that defeats separation.

## 6. Statistical sizing and why the numbers are what they are

No arbitrary constants. Every threshold below is derived, not chosen.

- **Per-arm trial count `n = 60`.** For an arm observing zero events, the exact
  one-sided 95% upper bound is `1 - 0.05^(1/n)` (rule of three, `≈ 3/n`). At
  `n = 60` that is `≈ 4.87%`. 60 is the smallest multiple of the 22-case corpus
  granularity that puts the zero-event ceiling below 5%.
- **Separation-gain threshold.** The separated arm counts as improving only if the
  95% CI on its false-promotion rate excludes the same-domain arm's point estimate.
  The bound same-domain estimate is `6/6 = 1.0` under full compromise, so any
  non-overlap is a genuine step, not a tuned margin.
- **False-rejection budget.** Inherited from the bound study, not re-chosen:
  chain-layer false rejections must stay `0/11` and disposition-level `0/5`, the
  exact denominators in `P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md`. Reusing
  these keeps the new numbers comparable to the bound ones.
- **Overhead budget.** Stated as a ratio to the no-attestation baseline measured in
  the same run on the same host, not as an absolute millisecond figure, because an
  absolute figure is not portable across the three sites.

## 7. What a negative would mean

If H2 fails — separated domains do not reduce false promotion under matched attack
after charging false rejection and overhead — then multi-root attestation
architectures should not be advertised as raising the compromise threshold in this
deployment class. That is a publishable boundary result and is enumerated as a
terminal. The design is built so that outcome is reachable.

## 8. Authority

Executing this protocol cannot promote ORION-25. A green outcome would support a
**successor** identity at bounded scope; `promotion_allowed=false` on
`P15_ACTIVE_CLAIM_AUTHORITY_V3.json` is untouched. Key custody remains an
unregistered premise of the scientific-admission layer at every `d`.
