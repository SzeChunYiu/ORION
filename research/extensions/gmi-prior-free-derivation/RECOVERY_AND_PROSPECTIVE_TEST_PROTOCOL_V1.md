# Prior-free GMI: recovery and prospective prediction protocol v1

## 0. Purpose

Representation coverage is cheap. If a formal vocabulary is expressive enough, a known architecture can almost always be described after the fact. That is not evidence that the theory derived the form.

This protocol separates four increasingly strong claims:

1. **coverage** — a form can be mapped into the frozen operational vocabulary;
2. **retrodictive recovery** — a form's operational region is derived from obligation, ecology, and resources without using its architecture label or implementation details as inputs to that derivation;
3. **time-held-out recovery** — the derivation is frozen before the form is inspected or before the form exists in the accessible literature;
4. **prospective prediction** — the theory freezes an operational region with no known inhabitant under a registered search, and a later construction or external discovery inhabits that region.

Only (3) and (4) provide strong evidence against post-hoc architecture fitting.

---

## 1. Frozen objects

A recovery experiment must bind the following objects before the held-out form is inspected.

### 1.1 Theory state

Freeze a commit or content digest containing:

- the current formal core;
- the operational reduction vocabulary;
- the declared gauge/probe equivalence;
- the resource coordinates;
- every theorem used to derive morphology constraints.

Write this bundle as

\[
\mathsf T_0.
\]

### 1.2 Problem specification

Freeze

\[
\mathsf P
=
(C,\Omega,\mathcal E,\Theta,B,\mathcal B),
\]

where \(\mathcal B\) is the declared machine/composition boundary. If any of these change after prediction, the run is a successor experiment, not the same recovery claim.

### 1.3 Derivation procedure

Freeze the map or proof procedure

\[
\mathsf D_{\mathsf T_0}:\mathsf P\mapsto\widehat R,
\]

where \(\widehat R\) is a set of admissible operational signatures or profile constraints.

The procedure may output a region rather than one point. It must not accept a named architecture as an argument.

### 1.4 Prediction record

The prediction record must contain only architecture-neutral statements such as:

- required persistence structure;
- channel topology and cut constraints;
- routing dependence;
- update locality;
- information-placement requirements;
- resource scaling inequalities;
- reachable/non-reachable morphology coordinates;
- phase boundaries over substrate parameters.

Statements such as "Transformer", "Mamba", "Bayesian learner", "RAG", or "symbolic" are prohibited from the prediction field. Labels may appear later only in the reveal/evaluation field.

---

## 2. Leakage model

Let \(K\) be a candidate held-out architecture family.

Define a leakage set \(L_K\) containing every fact about \(K\) that could materially constrain the predicted operational region, including:

- architecture label and aliases;
- diagrams or module descriptions;
- implementation code;
- asymptotic resource claims;
- benchmark behaviour diagnostic of internal organization;
- papers that explicitly reveal the relevant operational mechanism.

A run is **strictly held out** only when the derivation team does not inspect \(L_K\) between the theory freeze and the prediction freeze.

### Historical contamination flag

If \(K\) was known while the vocabulary or formal theory was being designed, a leave-one-family-out experiment is only **retrospective recovery** even if its row is hidden during final scoring. It cannot be promoted to prospective evidence.

This flag is permanent. Later procedural blindness cannot erase historical exposure.

---

## 3. Architecture-neutral premise test

Before a recovery result can be scored, every premise used in \(\mathsf D\) must pass the operational-invariance test.

Let \(M\sim_G N\) mean that \(M\) and \(N\) are indistinguishable under the declared operational probes/gauge relation at the theorem's boundary.

A static premise functional \(f\) is admissible only if

\[
M\sim_G N
\Longrightarrow
f(M)=f(N).
\]

A resource model that says, for example, "attention operations cost one" or "neural parameters are cheap" fails unless those terms have first been defined as operationally measurable substrate events independent of architecture naming.

For developmental/search claims, the search transition law must either be equivariant under the same equivalence or the result must be labeled **search-prior-sensitive**.

---

## 4. Recovery levels

### R0 — representation coverage

After inspecting architecture \(K\), construct

\[
\chi(K).
\]

Pass condition: the form maps into the frozen vocabulary without adding a new primitive.

Interpretation: vocabulary coverage only.

### R1 — retrospective blinded recovery

The family was historically known during theory construction, but its reduction row is hidden from the final derivation pass.

Freeze \(\widehat R\), reveal \(K\), then compute \(\chi(K)\).

Pass condition:

\[
\chi(K)\in\widehat R.
\]

Interpretation: resistance to immediate label fitting, but not genuine prospective evidence.

### R2 — time-held-out recovery

Freeze \(\mathsf T_0,\mathsf P,\mathsf D,\widehat R\) before the team inspects a form first published or first made available after the freeze.

Pass condition:

\[
\chi(K_{\mathrm{new}})\in\widehat R
\]

under the frozen reduction vocabulary.

Any vocabulary extension required after reveal counts as failure for the original run and may seed a successor theory.

### R3 — prospective empty-region prediction

Before searching for a realization, freeze a nonempty region

\[
R_{\mathrm{new}}\subseteq\widehat R
\]

and a registered census showing no known inhabitant in the declared search universe at the freeze time.

Then perform a construction/search campaign or wait for an external discovery.

Pass condition: a later machine \(K_*\) satisfies

\[
\chi(K_*)\in R_{\mathrm{new}}
\]

without revising the frozen region.

This is the preferred strong GMI test.

---

## 5. Empty-region census

A claim that a region is unoccupied requires more than "we do not know one".

Freeze:

1. search date;
2. bibliographic databases and repositories searched;
3. query families;
4. architecture families explicitly checked;
5. synonyms and adjacent fields checked;
6. exclusion criteria;
7. unresolved ambiguous candidates.

The result is one of:

- **NO-KNOWN-INHABITANT within registered census**;
- **AMBIGUOUS**;
- **OCCUPIED**.

Only the first may support an R3 launch. It is a bounded literature claim, not an all-literature theorem.

---

## 6. Prediction granularity

A prediction can be vacuously broad. Therefore freeze its granularity before reveal.

Let the reduction chart have coordinates \(R_0,\ldots,R_8\). For each coordinate, mark:

- exact value/class;
- allowed finite set;
- interval/partial order bound;
- unconstrained.

Define the predicted cell

\[
\widehat R
=
\prod_i \widehat R_i
\]

subject to any cross-coordinate constraints.

A prediction with every coordinate unconstrained is coverage, not recovery.

### Specificity report

Record at least:

\[
S
=
-\log \nu(\widehat R),
\]

for a declared reference counting/volume measure \(\nu\) on the finite/discretized test chart, or an alternative preregistered specificity measure.

The measure is used only to report how restrictive the prediction was. It is not a probability prior over environments.

---

## 7. Scoring

After reveal, map the held-out form under the already frozen reduction protocol.

### Exact hit

\[
\chi(K)\in\widehat R.
\]

### Partial hit

Some constrained coordinates match but at least one constrained coordinate fails.

Partial hits are reported coordinate-wise. They are not converted into exact recovery by relaxing \(\widehat R\) after reveal.

### Miss

\[
\chi(K)\notin\widehat R.
\]

A miss remains a negative result. The successor theory must identify which premise, theorem, resource model, or vocabulary boundary was responsible.

### Novel primitive event

If \(K\) cannot be represented without extending the frozen operational vocabulary, record

\[
\texttt{VOCABULARY\_BREACH}.
\]

This is scientifically stronger than an ordinary miss because it challenges representation completeness.

---

## 8. Independent reduction

The team that derives \(\widehat R\) should not be the sole authority that maps the revealed architecture into the chart.

Preferred protocol:

1. derivation team freezes \(\widehat R\);
2. reduction team receives only the frozen vocabulary and the revealed architecture;
3. reduction team produces \(\chi(K)\) with evidence;
4. discrepancies are adjudicated before the prediction is unsealed for scoring.

If one team performs both roles, record that dependence explicitly.

---

## 9. Physical closure gate

Recovery of an operational signature is not physical morphology closure.

For substrate condition \(\theta\), maintain:

\[
\mathfrak X_{\mathrm{inner}}(\theta)
\subseteq
\mathfrak X_{\mathrm{phys}}(\theta)
\subseteq
\mathfrak X_{\mathrm{outer}}(\theta),
\]

where:

- `inner` consists of explicit constructions;
- `outer` is proved from necessity/lower-bound theorems;
- `phys` is the unknown true realizable set.

A profile-frontier region is certified only when the constructive nondominated envelope meets and dominates the entire necessary outer envelope at the declared profile level.

An exact morphology claim additionally requires identification of the morphology fiber over that profile.

---

## 10. Developmental closure gate

Even a physically optimal form need not be reachable by a declared development/search process.

Freeze a development process \(\mathcal D\), initialization law, and budget \(B\). The developmental claim must state either:

- a proved reachability statement;
- a finite-budget success probability under randomness internal to \(\mathcal D\);
- a lower/upper bound;
- or `OPEN`.

If \(\mathcal D\) privileges syntax or architecture names inside one operational equivalence class, mark the result

\[
\texttt{SEARCH\_PRIOR\_SENSITIVE}.
\]

Do not call such a result architecture-prior-free.

---

## 11. Failure-preserving preregistration record

Every R2/R3 run should freeze a machine-readable record containing at least:

```text
run_id
freeze_commit
freeze_time
problem_spec_digest
theory_digest
reduction_vocabulary_digest
derivation_procedure_digest
prediction_region
specificity_measure
machine_boundary
resource_model
search/development_model
heldout_rule
literature_census_digest (R3)
falsification_conditions
allowed_postfreeze_operations
```

After reveal append rather than overwrite:

```text
reveal_time
candidate_identity
independent_reduction
score
vocabulary_breach
responsibility_diagnosis
successor_run_id
```

The prediction region and falsification conditions are immutable.

---

## 12. Immediate programme consequence

`KNOWN_FORM_REDUCTION_V1.md` is R0 evidence. Because the principal known architecture families were already known during construction of the R0--R8 vocabulary, it must not be described as prospective recovery.

The next strong experiment must therefore be either:

1. an R2 time-held-out architecture appearing after a frozen cutoff; or
2. an R3 empty-region prediction followed by targeted construction or later external discovery.

The preferred route is R3 because it tests whether the top-down theory can specify useful morphology before an implementation is supplied.

---

## 13. Closure criterion for the architecture programme

The architecture-recovery programme is not closed by counting how many known forms fit the vocabulary.

A serious terminal requires all of:

1. no vocabulary breach on a registered held-out panel;
2. at least one non-vacuous R2 recovery;
3. at least one preregistered R3 region with a later inhabitant;
4. negative/missed predictions preserved;
5. architecture-neutral premise audit passed;
6. physical/resource claim strength limited to regions where necessity and construction envelopes meet;
7. developmental claims separately gated.

Until then, the correct status is:

\[
\boxed{\text{formal core strengthened; representation coverage broad; prospective GMI prediction OPEN.}}
\]
