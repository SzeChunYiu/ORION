# ORION-20 theorem/proof audit V1 — CORE

```text
scientific_authority_delta = NONE
audit_kind                 = SINGLE_ADVERSARIAL_PASS
audit_basis                = COMMITTED_ARTIFACTS_PLUS_INDEPENDENT_RECOMPUTATION
verdict                    = STATEMENT_AND_CITATION_DEFECTS_FOUND__NO_PROVED_THEOREM_REFUTED
```

**What this is.** One adversarial reading of the five formal objects the
Wave-2 disposition assigns to ORION-20
(`papers/publication_closure/wave2/WAVE2_DISPOSITION_V1.json`): finite
closure, exhaustive-search dominance, certified expansion, primitive
minimality, exact input contract. Statements were audited from committed
text. The generating search/proof code was read only to check whether the
implementation computes what the prose says it computes — never as evidence
that a claim is true. Facts marked *[recomputed]* were derived by an
independent script written for this audit, not by importing any ORION-20
module.

**What this is not.** Not an external specialist audit, not a referee
report, not machine-checked verification. A single reader can miss a whole
defect class. [A6](audit/AUDIT_A6_COVERAGE_AND_LIMITS_V1.md) lists what was
checked and what could not be checked so coverage can be judged.

---

## 1. Corpus map — the objects live in two places, and they disagree

| Corpus | Location | Contains |
|---|---|---|
| **A. Manuscript headlines** | `TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md:19-23` | `ORION-20-T1..T5`, one line each, **no proof** |
| **B. Formal package + proofs** | `research/orion-foundations-v3/PAPER_THEOREM_PACKAGES_V1.md:433-476`, `PAPER_THEOREM_PROOFS_V1.md:223-249` | `P10-T1..T6`, statement + proof sketch |
| **C. Hand-declared study** | `top_tier/P10_OCME_FORMAL_*` | AND2 / SQUARE non-vacuity |
| **D. Generated study** | `top_tier/P10_GENERATED_OCME_*` | code-8 / CUBE selection |

### F-1 (major) — Corpus A and Corpus B are not the same theorems

Five entries versus six; different titles; different content; **no mapping
recorded anywhere**.

| Corpus A headline | Nearest Corpus B theorem | Relationship |
|---|---|---|
| T1 "exact finite reachability and obstruction are **decidable**" | P10-T1 "if `t∉Cl(L)`, no search restricted to `L` reaches `t`" | **Different proposition.** B proves *unreachability*; A asserts *decidability*. No decision procedure, finiteness hypothesis, or termination argument exists for A-T1. |
| T2 "**no selector exceeds** complete affordable exhaustive verification" | — | **No counterpart. No proof anywhere.** |
| T3 "expansion requires target outside old closure, edit outside old reducibility, target inside new closure" | P10-T2 + P10-T3 | Broadly aligned; necessity half unproved (G-5) |
| T4 "every **strictly weaker registered edit** must fail" | P10-T4 "**inclusion**-minimal" | **Different order.** Strength preorder vs set inclusion; the preorder is never defined. |
| T5 "invention requires **donor conservativity** plus hidden transferable extension" | P10-T5 "transfer condition" | B addresses transfer only; the conservativity conjunct is never proved. |
| — | P10-T6 "synthesis/checking separation" | **Orphaned.** No Corpus A counterpart. |

`research/orion-epistemic-state-v1/THEOREM_LEDGER_V1.json` records the P10
range as `"P10-T1..P10-T5"` (five) while the proofs file carries six, and
its own status field reads
`THEOREM_STATEMENTS_COMPLETE__PROOFS_AND_EXECUTION_SEPARATELY_GATED`.

**Consequence.** A referee cannot tell which proposition "exhaustive-search
dominance" denotes, and **three of the five Corpus A statements have no
proof in the repository** (T1 decidability, T2 dominance, T5's
conservativity conjunct). This is the most important finding of this pass.
It is a *statement-and-citation* defect: it does not show that any Corpus B
proof is wrong.

---

## 2. Findings register

Severity is this auditor's judgement. Detail and evidence in the linked file.

| ID | Sev | Finding | Detail |
|---|---|---|---|
| F-1 | major | Two incompatible theorem schemes; three A-statements unproved | this file |
| G-1 | major | Finite-closure theorem is a range restriction; cannot bound unrestricted donors | [A1](audit/AUDIT_A1_FINITE_CLOSURE_V1.md) |
| G-2 | major | "Decidable" asserted without finiteness hypothesis or decision procedure | [A1](audit/AUDIT_A1_FINITE_CLOSURE_V1.md) |
| G-3 | major | Setting B closure called "finite"; it is infinite (rational affine) | [A1](audit/AUDIT_A1_FINITE_CLOSURE_V1.md) |
| G-4 | major | Setting B obstruction is domain-relative; **vanishes on `{-1,0,1}`** | [A1](audit/AUDIT_A1_FINITE_CLOSURE_V1.md) |
| G-14 | major | A-T2 quantifier order and "complete affordable" undefined; verifier decisiveness unstated | [A2](audit/AUDIT_A2_EXHAUSTIVE_DOMINANCE_V1.md) |
| G-15 | major | "Exhaustive-search dominance" comparison is **not information-matched** | [A2](audit/AUDIT_A2_EXHAUSTIVE_DOMINANCE_V1.md) |
| G-5 | major | Necessity half of certified expansion proved by "intended meaning" | [A3](audit/AUDIT_A3_CERTIFIED_EXPANSION_V1.md) |
| G-6 | major | Outside-closure filter eliminates **zero** candidates in both studies | [A3](audit/AUDIT_A3_CERTIFIED_EXPANSION_V1.md) |
| G-7 | major | `6/6` held-out transfer is deductively entailed, not measured | [A3](audit/AUDIT_A3_CERTIFIED_EXPANSION_V1.md) |
| G-8 | major | `false_expansion = 0` restates the case file; hardcoded literal in the "independent" checker | [A3](audit/AUDIT_A3_CERTIFIED_EXPANSION_V1.md) |
| G-13 | moderate | Own falsifier "candidate grammar encodes the answer" not discharged | [A3](audit/AUDIT_A3_CERTIFIED_EXPANSION_V1.md) |
| G-9 | major | A-T4 ("strictly weaker edit") is not the proved theorem | [A4](audit/AUDIT_A4_PRIMITIVE_MINIMALITY_V1.md) |
| G-10 | moderate | Minimality tie-break inert in Setting B, two-way in Setting A | [A4](audit/AUDIT_A4_PRIMITIVE_MINIMALITY_V1.md) |
| G-11 | moderate | Minimality relative to an experimenter-supplied complexity order | [A4](audit/AUDIT_A4_PRIMITIVE_MINIMALITY_V1.md) |
| G-12 | major | Donor-conservativity conjunct of A-T5 nowhere defined or proved | [A5](audit/AUDIT_A5_INPUT_CONTRACT_V1.md) |

---

## 3. The single most important substantive finding

**"Exhaustive-search dominance" is not a comparison against an
information-matched baseline.** The searches quantified over are
*definitionally denied* the candidate grammar the ORION generator was
handed. Give a plain enumerator the same 16 truth tables (Setting A) or 5
unary candidates (Setting B) plus the same frozen composition template, and
it solves the task immediately — indeed the ORION "generator" **is** that
enumerator. Under matched information there is no dominance in either
direction, only a definitional partition between a grammar containing a
fitting primitive and one that does not. Full argument in
[A2](audit/AUDIT_A2_EXHAUSTIVE_DOMINANCE_V1.md).

The defensible claim, which the paper is entitled to make: *once a target
is certified outside a registered closure, no procedure whose output range
is that closure can reach it, at any budget.* That is a statement about
closure, not about search quality, and not a comparison with any deployed
system.

## 4. What survives unscathed

Stated explicitly because an approval is worth less than a precise gap, and
a reader deserves to know the audit was not uniformly negative:

- **P10-T3 macro rejection** is correct and complete as proved.
- **P10-T1 as stated in the package** is a valid induction with its
  hypothesis stated and used.
- **The exact input contract** — 480 cases, 4 domains, 9 arms, 3 seeds, 80
  controls, 12,960 planned cells, **0 executed**, 480 `CANNOT_CHECK` — is
  exact, traceable, and needs no empirical support to stand. It is the
  strongest artifact in the paper. See
  [A5](audit/AUDIT_A5_INPUT_CONTRACT_V1.md).
- **All arithmetic in both finite studies** reproduced *[recomputed]*
  without discrepancy.
- **Adverse findings are preserved and unsoftened** throughout.

## 5. Detail files

- [A1 — finite closure](audit/AUDIT_A1_FINITE_CLOSURE_V1.md)
- [A2 — exhaustive-search dominance](audit/AUDIT_A2_EXHAUSTIVE_DOMINANCE_V1.md)
- [A3 — certified expansion](audit/AUDIT_A3_CERTIFIED_EXPANSION_V1.md)
- [A4 — primitive minimality](audit/AUDIT_A4_PRIMITIVE_MINIMALITY_V1.md)
- [A5 — exact input contract](audit/AUDIT_A5_INPUT_CONTRACT_V1.md)
- [A6 — coverage and limits](audit/AUDIT_A6_COVERAGE_AND_LIMITS_V1.md)
