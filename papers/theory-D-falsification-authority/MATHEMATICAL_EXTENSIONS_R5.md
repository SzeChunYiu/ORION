# Mathematical Extensions R5 — License Noninterference and Prior-Art Recalibration

Date: 2026-08-25

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md` and `MATHEMATICAL_EXTENSIONS_R4.md`

Status: rigorous theorem and correction addendum. It narrows the novelty claim after a current primary-source check and develops results that depend essentially on typed license caps.

## 1. Prior-art correction

A paper submitted on 17 July 2026, R. B. Thapa and S. Staab, *Causality and Minimal Supports in Recursive Datalog*, studies inclusion-minimal endogenous supports for positive Datalog, organizes them as a support hypergraph, derives deletion robustness and responsibility, identifies reachability supports with paths and robustness with minimum cuts, and proves an NP-hardness calibration.

Accordingly, the generic parts of R4 Theorems D3–D5—minimal-support hypergraphs, blocker-as-hitting-set reasoning, and generic hardness of optimal deletion—must not be presented as residual novelty. They remain correct specializations of the frozen evidence-license semantics and useful for exposition, but the manuscript must cite this prior work and earlier causality/resilience literature.

The scientifically defensible residual is narrower:

1. typed powerset labels rather than untyped entailment;
2. rule caps that prevent license promotion;
3. exact coordinatewise retraction under direct refutation;
4. static noninterference and dominance relations between licenses; and
5. an executable policy layer that records evidence authority separately from reachability.

## 2. License projections

For a license `lambda`, define its syntactic projection by

`S_lambda={q: lambda in sigma(q)}`

and

`R_lambda={r: lambda in K_r}`.

Together with the common claim set, rule bodies and heads, and refutation set, this is the ordinary positive Horn program evaluated in R4 Theorem D1.

**Theorem D6 (strong license noninterference).** Consider two typed evidence systems with identical claim/rule shapes and the same direct-refutation set. If their `lambda` projections have the same seed set `S_lambda` and retained-rule set `R_lambda`, then every claim has `lambda` in one least-fixed-point label exactly when it has `lambda` in the other.

**Proof.** R4 Theorem D1 maps both systems to the same Boolean Horn program for `lambda`. Their least closures are identical. ∎

Thus changing other licenses, adding unrelated cap memberships, or relabeling evidence on a different coordinate cannot alter `lambda` authority unless it changes the `lambda` projection itself.

## 3. Static license quotient

Define the syntactic signature of a license by the bit vector

`sig(lambda)=(1[lambda in sigma(q)]_{q in Q}, 1[lambda in K_r]_{r in Rules})`.

**Corollary D7 (license compression).** Licenses with identical signatures have identical derived claim sets under every direct-refutation set. They may be evaluated once and expanded afterward.

This quotient can reduce evaluation work when a large policy vocabulary contains aliases or licenses that are operationally indistinguishable in the frozen graph. It is a sufficient syntactic quotient, not a claim that no coarser instance-specific semantic quotient exists.

## 4. A policy dominance preorder

Write

`lambda preceq mu`

when

`S_lambda subseteq S_mu`

and

`R_lambda subseteq R_mu`.

This relation is declared by the policy encoding; it is not assumed to be an inherent order on evidence types.

**Theorem D8 (projection dominance).** If `lambda preceq mu`, then for every direct-refutation set `R`,

`{q:lambda in Lic_R(q)} subseteq {q:mu in Lic_R(q)}`.

**Proof.** The Boolean Horn program for `mu` contains every seed and every rule of the program for `lambda`. Monotone least closure is preserved under addition of seeds and positive rules. Removing the same refuted claims from both programs preserves the inclusion. ∎

A policy designer can use this theorem as a static audit. If a declared stronger permission is intended never to survive without a weaker permission, the seed and cap projections must satisfy the corresponding inclusion.

## 5. Formal nonpromotion

**Corollary D9 (no authority from foreign coordinates).** If `S_lambda` is empty, then no claim receives `lambda`, regardless of the seeds or rule caps of any other license. More locally, if target `q` is not in the Horn closure of `S_lambda` using only `R_lambda`, then no amount of evidence carrying other licenses can give `q` the `lambda` label.

This is the exact nonpromotion guarantee that untyped reachability lacks. A post-outcome repair may restore an untyped conclusion while remaining unable to restore a prospective license because the prospective projection has no valid seed-founded path.

## 6. Worked policy fixture

Consider seeds `forecast`, `posthoc_fit`, and `independent_theorem`, and target `support_claim`.

- `forecast` carries `PROSPECTIVE` and `FORECAST_ONLY`.
- `posthoc_fit` carries `POST_OUTCOME` only.
- `independent_theorem` carries `THEOREM`.
- The forecast rule permits `PROSPECTIVE` and `FORECAST_ONLY`.
- The repair rule permits `POST_OUTCOME` but excludes `PROSPECTIVE`.
- A theorem rule permits `THEOREM`.

After directly refuting `forecast`, the untyped target may remain reachable through the repair and theorem paths. Corollary D9 nevertheless forces the prospective coordinate to disappear. The target may retain `POST_OUTCOME` and `THEOREM` while losing `PROSPECTIVE`. This is a domain-faithful example of why typed labels change the reportable scientific conclusion.

## 7. What remains of the complexity story

Evaluation remains linear per license by R4 Theorem D2. Optimal intervention remains hard in general, but that dichotomy is now treated as donor-overlapping context rather than the headline novelty. The new algorithmic consequence is orthogonal: identical license signatures can be quotient-compressed, and projection inclusions can be certified before any fixed-point run.

A future complexity contribution would need a genuinely typed question—for example, simultaneous removal of selected licenses under shared seed costs, or parameterized algorithms exploiting the license-signature quotient—together with a careful comparison against database resilience and provenance.

## 8. Verification

The R5 verifier constructs separate theorem, bounded-computation, unrelated, and prospective coordinates. It checks that unrelated-coordinate edits leave theorem authority unchanged and that a prospective cap without a prospective seed cannot manufacture prospective authority.

## 9. Atomic status

- Prior-art overlap correction: `VERIFIED` against the July 2026 primary paper.
- Strong license noninterference: `VERIFIED`.
- Static license quotient: `VERIFIED`.
- Projection dominance: `VERIFIED`.
- Nonpromotion corollary: `VERIFIED`.
- Generic novelty of support hypergraphs, hitting sets, robustness, or deletion hardness: `WITHDRAWN`.
- Typed cap-preserving authority semantics and application policy: retained as the residual contribution.

## 10. Remaining scientific frontier

Paper D should not accumulate more generic Horn/provenance lemmas. The next high-value step is an independently sourced application record with a real policy distinction—prospective versus post-outcome evidence, data-use licenses, or jurisdictional authority—and a comparison showing that untyped reachability gives an operationally wrong answer while the typed semantics gives the intended one. Without that record, the paper is a rigorous formal component but not yet a broad-impact systems result.
