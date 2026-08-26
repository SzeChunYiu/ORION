# P8 native cross-system execution protocol V1

**Contract:** `P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1`
**Date frozen:** 2026-08-24
**Issue #1086 P8 box:** "Execute actual type-distinct native systems and ideal
typed-product baseline. Cover every ordered cross-system pair with clean and
hostile cases." (DENIED-vs-CANNOT_CHECK calibration is already separate, done in
#1096; this protocol presupposes it and does not re-derive it.)

**Execution status: `CANNOT_CHECK`.** The design below is frozen and
machine-checkable; the execution it specifies has not been run, because none of
the four native systems' tooling exists in this environment. Nothing in this
protocol is simulated, and no native-looking output has been produced.

---

## 1. Why a protocol, not a run

The P8 box asks for an *execution*: actual native systems, actually run, every
ordered pair, clean and hostile. An execution cannot be honestly reported from
a checkout that has none of the binaries. The two failure modes this document
exists to prevent are (a) silently narrowing the box to whatever the local
tooling can do, and (b) simulating a native system and reporting the simulation
as execution. Both are prohibited inferences (§7). What can be done honestly
today is to freeze the full test design --- systems, pairs, case templates,
verdict capture, acceptance criteria --- so that the execution, when an
environment with the tooling runs it, is a matter of filling slots and not of
re-deciding scope.

## 2. The four type-distinct native systems

The issue names the sources: OPA/Rego, Cedar, in-toto/SLSA, Sigstore. They are
type-distinct in exactly the sense P8's calculus needs: each one grounds
authorization in a *different evidence type*, so a hand-off between any two is a
genuine cross-type transport rather than a re-labelling.

| id | system | authorization evidence type | native verdict surface |
|----|--------|----------------------------|------------------------|
| `OPA`  | OPA / Rego       | policy decision over untyped JSON input (`data.allow`)      | boolean / defined-vs-undefined |
| `CDR`  | Cedar            | typed action permit on schema-typed entities               | `Allow` / `Deny` + errors |
| `ITT`  | in-toto / SLSA   | attestation-layout fulfillment by signed links             | layout verifies / not |
| `SIG`  | Sigstore / cosign| keyless signature over an identity (cert, SAN, bundle)     | signature verifies / not |

## 3. The ideal typed-product baseline

The baseline is the P8 authority calculus's typed derivation (contract
`P8.AUTHORITY.TERMINALS.V1`, #1096): each system's native verdict is first
coerced into the calculus's terminal set `AUTHORIZED | DENIED | CANNOT_CHECK`,
and the *ideal* verdict for a chain is the componentwise typed product, with no
cross-system coercion other than the calculus's declared ones. "Ideal" means
exactly this and nothing stronger: the baseline is the product construction the
paper defines, not a claim that it equals any native system's internals.

## 4. Every ordered cross-system pair

Four systems give twelve ordered pairs (emitter → consumer). Each pair carries
exactly two case classes, `clean` and `hostile`, for twenty-four case slots in
all. Each slot's id is fixed here; the pair→hostile-mechanism assignment is
part of the freeze.

| # | pair | clean case id | hostile case id | hostile mechanism (laundering family) |
|---|------|---------------|-----------------|----------------------------------------|
| 1 | `OPA`→`CDR` | `P8.NC.OPA_CDR.CLEAN`  | `P8.NC.OPA_CDR.HOSTILE`  | untyped policy allow presented as a typed action permit: type-confused principal |
| 2 | `CDR`→`OPA` | `P8.NC.CDR_OPA.CLEAN`  | `P8.NC.CDR_OPA.HOSTILE`  | schema-typed entity name reused as an untyped Rego role string: role-name collision |
| 3 | `OPA`→`ITT` | `P8.NC.OPA_ITT.CLEAN`  | `P8.NC.OPA_ITT.HOSTILE`  | allow decision replayed as a step fulfillment: no artifact-digest binding |
| 4 | `ITT`→`OPA` | `P8.NC.ITT_OPA.CLEAN`  | `P8.NC.ITT_OPA.HOSTILE`  | attestation fed as policy input although not signed for this consumer |
| 5 | `OPA`→`SIG` | `P8.NC.OPA_SIG.CLEAN`  | `P8.NC.OPA_SIG.HOSTILE`  | policy grant presented as a signing identity: no keyless identity proof |
| 6 | `SIG`→`OPA` | `P8.NC.SIG_OPA.CLEAN`  | `P8.NC.SIG_OPA.HOSTILE`  | certificate SAN presented as a policy principal outside its scope |
| 7 | `CDR`→`ITT` | `P8.NC.CDR_ITT.CLEAN`  | `P8.NC.CDR_ITT.HOSTILE`  | typed permit presented as a layout step completion: no link metadata |
| 8 | `ITT`→`CDR` | `P8.NC.ITT_CDR.CLEAN`  | `P8.NC.ITT_CDR.HOSTILE`  | unverified link fields forged into Cedar entity attributes |
| 9 | `CDR`→`SIG` | `P8.NC.CDR_SIG.CLEAN`  | `P8.NC.CDR_SIG.HOSTILE`  | policy-local principal presented as a signature identity |
| 10 | `SIG`→`CDR` | `P8.NC.SIG_CDR.CLEAN`  | `P8.NC.SIG_CDR.HOSTILE`  | cosign identity presented as an entity the schema does not declare |
| 11 | `ITT`→`SIG` | `P8.NC.ITT_SIG.CLEAN`  | `P8.NC.ITT_SIG.HOSTILE`  | attestation bundle presented as a signature over the artifact bytes |
| 12 | `SIG`→`ITT` | `P8.NC.SIG_ITT.CLEAN`  | `P8.NC.SIG_ITT.HOSTILE`  | artifact signature presented as a step-execution link |

### 4.1 Clean case template

A well-typed hand-off: the emitter produces evidence *valid in its own type
system*, the evidence is translated faithfully into the form the consumer's
type system expects, and the translation is the calculus's declared coercion
(none hidden). Expected: the consumer's native verdict coerces to `AUTHORIZED`,
and the typed-product baseline is `AUTHORIZED`. A clean case that fails is a
*conservatism finding*, recorded, not retried.

### 4.2 Hostile case template

The laundering family: evidence that is valid under the emitter's types but
carries a claim the consumer's types do not ground (the mechanism column
above). Required outcome: the consumer's native system must **not** coerce to
`AUTHORIZED` --- it must deny, error, or otherwise coerce to `DENIED` /
`CANNOT_CHECK` --- and the typed-product baseline must also refuse. Any hostile
slot whose native verdict coerces to `AUTHORIZED` is recorded as a *laundering
finding*; findings are never discarded, only classed.

## 5. Execution requirements (what `CANNOT_CHECK` blocks)

- Actual binaries, pinned: `opa` (Rego eval, offline bundle), `cedar-cli`
  (authorize against a schema), `in-toto-verify` (layout + links), `cosign`
  (verify-blob / verify with locally generated key material --- offline,
  Fulcio/Rekor absent, which is itself recorded as a deviation).
- Offline fixtures per slot: input bundle, translation artifact, expected
  native command, captured stdout/exit, parsed verdict.
- One record per slot in the result file named
  `P8_NATIVE_CROSS_SYSTEM_RESULTS.json` (schema in §6), committed as data.
- Verification observed 2026-08-24 in the producing lane: `opa`, `cedar`,
  `cosign`, `in-toto-verify`, `in_toto`, `slsa-verifier` are all absent from
  `PATH`; no Docker; no network installation is permitted by the lane's
  constraints. That absence --- not a result --- is why execution is
  `CANNOT_CHECK`.

## 6. Record schema (frozen)

```
{
  "case_id": "P8.NC.<PAIR>.<CLEAN|HOSTILE>",
  "pair": {"emitter": "OPA", "consumer": "CDR"},
  "class": "clean" | "hostile",
  "mechanism": "<hostile mechanisms only>",
  "input_bundle_sha256": "...",
  "native_command": ["opa", "eval", ...],
  "native_exit": 0,
  "native_verdict_raw": "...",
  "native_verdict_coerced": "AUTHORIZED" | "DENIED" | "CANNOT_CHECK",
  "baseline_verdict": "AUTHORIZED" | "DENIED" | "CANNOT_CHECK",
  "divergence_class": "AGREE" | "NATIVE_STRICTER" | "BASELINE_STRICTER" | "FINDING"
}
```

## 7. Acceptance criteria and prohibited inference

The P8 box is discharged by an execution only when: all twenty-four slots carry
records produced by the pinned binaries; zero hostile slots coerce to
`AUTHORIZED`; every divergence is classed; and the results file is committed.

Prohibited: simulating any native system and reporting it as execution;
reporting the ideal baseline as any native system's behaviour; using this
protocol's existence as evidence of execution; re-deriving the DENIED vs
`CANNOT_CHECK` calibration (that is #1096's, already merged); treating a
partial run (some pairs) as coverage of "every ordered cross-system pair".

The machine-readable twin of this document is
`formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_2026-08-24.json`; the cross-artifact
binding is enforced by `formal/check_p8_native_protocol_binding_v1.py`
(contract `P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1`).
