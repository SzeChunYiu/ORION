# A1 — Finite closure

`scientific_authority_delta = NONE` · detail file for
[`../THEOREM_PROOF_AUDIT_V1.md`](../THEOREM_PROOF_AUDIT_V1.md)

**Statement audited** (`PAPER_THEOREM_PACKAGES_V1.md:439-441`, proof
`PAPER_THEOREM_PROOFS_V1.md:227`): `Cl(L)` is the least behavioural closure
of method language `L` under a frozen information/access/resource model. If
`t∉Cl(L)`, no search, repair, synthesis or evolution *restricted to `L`*
can reach `t`, regardless of search effort.

**Precise enough to be false?** Yes, and it is true. The proof is a one-line
induction on derivations: every derivation restricted to `L` lands in
`Cl(L)`. Correct and complete for what it states.

**Assumptions stated and used?** The load-bearing hypothesis is *restricted
to `L`* — the procedure's output range is `Cl(L)`. Stated, and used.

---

## G-1 (major) — the theorem is a closure tautology, not a search result

It says nothing about any procedure that is not range-restricted to
`Cl(L)`. Every real donor named in the manuscript — proof repair, premise
retrieval, program synthesis, evolutionary code search — is not so
restricted. The theorem cannot support any comparative statement about
those systems. Carried forward into A2/G-15.

## G-2 (major) — "decidable" is asserted, not proved

`TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md:19` states *"exact finite
reachability and obstruction are decidable."* Decidability needs (i)
`Cl(L)` finite or effectively enumerable and (ii) a terminating membership
procedure. Neither is stated as a hypothesis nor discharged anywhere. The
proved theorem is *unreachability*, which is a different proposition.

## G-3 (major, verified) — Setting B's closure is not finite

- `P10_OCME_MANUSCRIPT_ADDENDUM_V1.md:48` — "in both registered **finite**
  closures".
- `P10_GENERATED_OCME_RESULT_RECEIPT_V1.md:49` — "in both registered
  **finite** settings".

Setting A's closure *is* finite: 32 affine Boolean functions on four
inputs. Setting B's closure is `a*x+b` over the **rationals**
(`P10_GENERATED_OCME_PROTOCOL_V1.md:60`) — an infinite two-parameter
family. Non-membership there comes from an algebraic collinearity argument,
not enumeration; `P10_OCME_FORMAL_NONVACUITY_PROTOCOL_V1.md:53` states this
correctly ("without arbitrary coefficient search bound"). The mathematics
is sound. The word *finite* applied to Setting B is wrong and should read
"exactly decidable" or "algebraically closed".

## G-4 (major, verified by recomputation) — the Setting B obstruction is domain-relative

The obstruction is a property of the *(target, domain)* pair, and the
domain is a free protocol parameter with no stated selection criterion.

- On the frozen verifier domain `{-4..4}`, `x³+2x+1` is not affine.
- On the sub-domain `{-1,0,1}` it **is** affine — *[recomputed]* the points
  `(-1,-2)`, `(0,1)`, `(1,4)` are exactly collinear (it equals `3x+1`
  there), so the obstruction vanishes entirely.

The defensible statement is existential — *there exists a verifier domain
on which the target lies outside the closure* — which is much weaker than
the universal reading the prose invites. This assumption is used but never
stated.

## Degenerate-case fragility (minor, verified) — single-triple collinearity

Because a cubic can be collinear on a badly chosen triple (above), any
non-membership checker sampling one triple rather than all can emit a false
`KNOWN_COMPOSITION`. The committed independent checker does use an
all-triples test (`check_generated_ocme_independent_v1.py`, `collinear`),
so the hazard is avoided *in this implementation* — but the protocol text
does not require it, so a re-implementation could reintroduce it.

## Checked, no defect found

- The affinity test used for binary Boolean functions — XOR of the four
  truth-table entries equals 0 — is *[recomputed]* exactly the correct
  characterisation of a two-variable affine Boolean function.
- The 32-element affine family on four Boolean inputs is correct, and
  three-input majority is genuinely outside it.
- All-triples collinearity is a valid exact affine-membership decision
  procedure on a finite domain.
