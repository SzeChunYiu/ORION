# A6 — Coverage, degenerate cases, and what this pass could not check

`scientific_authority_delta = NONE` · detail file for
[`../THEOREM_PROOF_AUDIT_V1.md`](../THEOREM_PROOF_AUDIT_V1.md)

Recorded so a reader can judge how much of the surface this single
adversarial pass actually touched.

---

## Degenerate cases

| Case | Handled? | Where |
|---|---|---|
| No candidate passes selection | Yes | `P10_GENERATED_OCME_PROTOCOL_V1.md:117` retains `GENERATED_OCME_NOT_SUPPORTED` and forbids post-hoc grammar expansion |
| Origin solved but no transfer | Yes | same line, `GENERATED_EDIT_NO_TRANSFER` |
| Empty problem / no eligible transitions | Yes, and preserved as adverse | `P10_NATIVE_LEAN_CANNOT_CHECK_HANDOFF_V1.md`: 0 of 11,842 transitions eligible |
| Single primitive added | Vacuously minimal | [A4](AUDIT_A4_PRIMITIVE_MINIMALITY_V1.md) G-9 |
| Degenerate verifier domain | **Not addressed** | [A1](AUDIT_A1_FINITE_CLOSURE_V1.md) G-4: obstruction vanishes on `{-1,0,1}` |
| Unreachable goal *in the new closure* | **Not addressed** | Nothing states what happens if the certified edit still fails to reach the target; treated as impossible by construction |
| Non-terminating expansion / iterated edits | **Not addressed** | No termination or well-foundedness condition on repeated OCME rounds appears in either corpus |
| Verifier admitting false negatives | **Not addressed** | [A2](AUDIT_A2_EXHAUSTIVE_DOMINANCE_V1.md) G-14 |
| Control that solves the origin *from inside* the old closure | **Not exercised** | [A3](AUDIT_A3_CERTIFIED_EXPANSION_V1.md) G-6 |

## Checked and found nothing wrong

- **P10-T3 macro rejection.** The inlining argument is correct and
  complete; if `e∈Cl(L)`, behavioural closure is unchanged and only cost
  moves. No defect found.
- **P10-T1 as stated in the package.** The induction is valid and its
  restriction hypothesis is both stated and used. The defect lies in how
  the manuscript restates it, not in the theorem.
- **Setting A closure arithmetic.** *[recomputed]* affinity test, the
  32-function family, and majority's non-membership all check out.
- **Setting A selection determinism.** *[recomputed]* code 8 is the unique
  minimum-weight non-affine solver; reproducible from the frozen case file.
- **Setting B selection and wrappers.** *[recomputed]* CUBE is the unique
  exact fit; `(2,1)`, `(-1,2)`, `(0,3)`, `(-3,-2)` are arithmetically
  correct.
- **Setting B non-membership method.** All-triples collinearity is a valid
  exact affine-membership decision on a finite domain, and the committed
  independent checker implements it that way.
- **Held-out isolation during selection.** No held-out table is read by
  `select_bool` or `select_int`.
- **Preservation of adverse findings.** `CANNOT_CHECK_NATIVE_STATE_COVERAGE`
  and the 480 `CANNOT_CHECK` rows are stated plainly and are not softened
  in any artifact read during this pass.
- **Self-limitation discipline.** Both receipts explicitly deny autonomous
  invention and deny native superiority
  (`P10_OCME_FORMAL_RESULT_RECEIPT_V1.md:53`,
  `P10_GENERATED_OCME_RESULT_RECEIPT_V1.md:55-57`). That discipline is real
  and should be preserved verbatim.
- **`SHA256SUMS` currency at audit time.** `shasum -a 256 -c` passed 50 of
  50 entries with zero failures before any edit in this work window.

## Could not check in this pass

- Whether the CI runs cited in the receipts (`32645458392`, `32653800366`,
  `32655587097`) actually executed the committed code. Artifact ZIP hashes
  were not re-downloaded or re-verified against GitHub.
- Whether the two implementations are *structurally* independent in any
  sense stronger than "different membership algorithms, same repository,
  same language, same author". Independence is asserted, not demonstrated.
- Any claim requiring external mathematical adjudication of novelty. The
  repository's own external-novelty record is
  `INACCESSIBLE_WORK_MAY_ABSORB_CLAIM` with 75 of 75 atoms `CANNOT_CHECK`
  (`research/orion-epistemic-state-v1/results/DES-NOVELTY-01/P1_P15_EXTERNAL_NOVELTY_RECEIPTS_V1.json`).
- The `DES-T0..T15` calculus theorems on which `ORION-20-T5` depends. They
  are headline-only at
  `research/orion-epistemic-state-v1/DYNAMIC_EPISTEMIC_STATE_CALCULUS_V1.md:113-136`
  and were not audited here.
- Whether any Corpus B proof sketch, if expanded to full rigour, would
  survive. The sketches are one to three sentences each; this pass judged
  their *structure*, not a fully written-out derivation.
