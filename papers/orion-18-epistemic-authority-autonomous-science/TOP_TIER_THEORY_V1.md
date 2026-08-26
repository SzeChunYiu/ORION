# P8 top-tier theory V1 — Scientific authorization beyond action authorization

**Programme:** #977  
**Boundary:** per-action permission, obligations, delegation, provenance, freshness and evidence-bound grants are donor-owned. P8's object is whether typed scientific evidence discharges a named target scientific obligation.

## T8.1 — action/scientific authorization separation

Let a donor-complete action authorization judgment consume

\[
A=(principal,action,args,policy,delegation,budget,provenance,freshness,evidence\ reference)
\]

and output whether the action may execute.

Let a scientific target obligation additionally have type

\[
O=(domain,kind,scope,content,epoch).
\]

Construct two cases with identical `A` and identical action decision `PERMIT`, but with different target obligations `O1,O2` such that the supplied scientific evidence discharges `O1` and does not discharge `O2` (for example because content, scope or epoch differs).

Any decision function restricted to `A` must return the same scientific judgment for both cases and is therefore wrong on at least one. Distinguishing the pair requires adding information equivalent to target scientific-obligation/discharge typing.

Thus:

\[
\text{action authorization}\not\Rightarrow\text{scientific authorization}
\]

under the declared interface.

This does not imply that authorization systems *cannot be extended* with scientific typing; if they are, the expected result is semantic equivalence/assimilation.

## T8.2 — full-type coercion composition

A scientific judgment of type

\[
J=(d,k,s,c,e)
\]

may discharge a target obligation `O=(d',k',s',c',e')` directly when the full type matches, or through a registered protected coercion

\[
\gamma:J\Rightarrow O.
\]

A coercion record binds source type, target type, transformation semantics, validity conditions, issuer/checker identity and epoch.

### Composition

For `gamma1:J0=>J1` and `gamma2:J1=>J2`, composition is valid only if:

- the exact target type of `gamma1` equals the exact source type consumed by `gamma2`;
- both coercions are valid at the relevant epochs/contexts;
- no protected field transformation is silently widened between records;
- the composed transformation is independently registered/derivable under the coercion policy.

If source/target types do not meet exactly, or coercion identity/validity is missing or ambiguous, the scientific terminal is `CANNOT_CHECK`, not implicit promotion.

### Non-compensation

Confidence, utility, action permission or provenance quality cannot compensate for a failed hard type/obligation condition unless the scientific policy prospectively registers a coercion that explicitly licenses that transformation.

## T8.3 — support-family revocation under delegated authority

Let a claim have independent support derivations

\[
D=\{d_1,\ldots,d_n\},
\]

where each derivation records its sources/authorities and typed discharge path.

Revoking one source/authority removes exactly the derivations depending on it. The claim may remain scientifically authorized iff at least one surviving derivation independently discharges the target obligation under current type/epoch conditions.

A coarse claim-level revocation rule can therefore false-deny a still-supported claim, while a rule that ignores derivation dependency can false-authorize a claim after all valid support paths are gone.

### Monotonicity boundary

Adding an independent valid derivation can restore authorization; adding confidence to an invalid derivation cannot. Authority is therefore non-monotone in time/revocation but monotone in the set of simultaneously valid independent discharge derivations under a fixed target obligation.

## August 2026 donor pressure

Current per-action authorization and verifier/freshness standards are explicitly donor-owned, including AADP, principal/verifier binding, AAE and signed succession/authorization evidence recorded in `P7_P9_TOP_TIER_LITERATURE_DELTA_2026-08-23.md`.

P8 therefore cannot use rich evidence-bound action permission as novelty. Its protected discriminator must keep the physical/tool action fixed and vary only whether the scientific target obligation is actually discharged.

## Remaining external gate

Top-tier promotion still requires protected formal, empirical and evidence-based agent-action domains with independent scientific gold authority. This theory file cannot self-certify correctness/novelty of those domain claims.
