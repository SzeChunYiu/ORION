# Paper 3 scientific ascent: epistemic portrait envelopes

**Date:** 2026-08-23  
**Scope:** Paper 3 only  
**Status:** scientific theory advanced; naturalistic successor remains
unexecuted  
**Non-negotiable:** historical failures, source identities, gold authorities,
and frozen protocols are immutable.

## 1. Why Paper 3 was not yet top-tier

Paper 3 had real assets but no single high-level scientific object joining
them.

1. **The manuscript's broad object and measured object diverged.** The title
   invoked a global knowledge portrait, while the strongest external result
   was a 32-case decision over already-structured pairs.
2. **The adverse partial-observation result was treated mainly as a failed
   repair gate.** Its strongest content was actually an identification
   theorem: same visible projections can require different source-grounded
   answers, so no rule over those projections can be uniformly correct.
3. **Missing information and algorithmic error were confounded.** A zero-harm
   target asks a decision rule to repair information destroyed upstream. The
   frozen 768-cluster successor correctly moved toward harm above an
   observation floor, but the manuscript lacked the mathematical object that
   made that endpoint inevitable.
4. **Nearest work was absorbed rhetorically but not as one formal stack.**
   Scientific IE, variable semantics, schema/ontology alignment, provenance,
   pluralism, partial identification, constraint consistency and robust
   decisions each solved part of the problem, but the manuscript did not say
   how their outputs compose or where authority changes hands.
5. **The ideal-product tie looked like a limitation rather than a theorem.**
   If two products carry the same identified set and use the same loss, a tie
   is required. The target is a sufficient scientific-identity interface, not
   permanent privilege for one implementation.
6. **No downstream decision estimand was defined.** The phrase "downstream
   utility" remained open-ended. It now has a loss interval, minimax floor and
   floor-adjusted excess-harm target.

These are scientific problems, not pytest problems. No pytest or CI was run in
this ascent pass.

## 2. Upward move

The new central object is the **epistemic portrait envelope**:

> the set of global scientific portraits compatible with the observed
> provenance-bound source projections and all licensed mapping constraints.

This object is wider than pairwise coordinate mapping while remaining
defensible. It permits general theorems over arbitrary scientific domains, but
does not pretend that the existing samples establish empirical generality.

The manuscript now separates:

- **scientific identification:** which query values are invariant across all
  source-compatible completions;
- **information acquisition:** which truthful refinement can shrink the
  envelope;
- **global composition:** whether all accepted mappings have a joint
  completion rather than only pairwise agreement; and
- **downstream action:** which merge, split or deferral minimises declared
  worst-case loss.

This also separates **plurality** from **uncertainty**. Plurality is multiple
source-valid views inside a feasible scientific portrait. Uncertainty is
variation across feasible portraits because evidence does not select one
completion. A plural portrait may be identified; unresolved state is not.

## 3. Formal claim stack

The additive ledger is
`papers/paper-03-global-knowledge-portrait/THEORY_CLAIM_LEDGER_V1.md`.

### 3.1 Fibre criterion (`P3.EPE.T1`)

For world set `Omega`, observation `O`, portrait map `G`, and query `q`, define

```text
Omega_y   = {omega : O(omega) = y}
E(y)      = {G(omega) : omega in Omega_y}
Theta_q(y)= {q(g) : g in E(y)}.
```

The query is point identified iff `q o G` is constant on `Omega_y`. If two
worlds have the same observation and different query values, every
observation-only deterministic rule is wrong in at least one.

This converts the A004 negative terminal into an impossibility result without
changing A004's identity or verdict.

### 3.2 Universal sufficient interface (`P3.EPE.T3`)

An interface `S(y)` is sufficient for query `q` when `Theta_q(y)` can be
decoded from it. The map `y -> Theta_q(y)` is the coarsest such interface:
every sufficient `S` factors onto it. Therefore information-equivalent
products must have the same robust loss table and minimax actions under a
common loss.

This is the principled reading of the 400/400 ideal-product tie. The exact
battery does not prove inherent expressivity or centralisation; it shows that
the strong product as frozen omitted authority conditions, while an
information-equivalent product can implement them.

### 3.3 Information refinement (`P3.EPE.T2`)

If `O2` refines `O1`, then every world with refined observation also belongs
to the corresponding coarse fibre. Hence the refined identified set is a
subset of the coarse one and minimax decision loss cannot increase.

This tells the research programme where real improvement comes from:

- extract or measure a missing load-bearing coordinate;
- acquire a source that distinguishes completions;
- retain provenance/observedness that a coarse interface discarded; or
- declare and test an assumption that removes worlds.

A new decision rule over unchanged evidence cannot cross the observation
floor.

### 3.4 Downstream decision bound (`P3.EPE.P1`)

For any nonempty licensed binary credal set `K_y`, define
`l_y = inf K_y` and `u_y = sup K_y`. The exact lower--upper risk interval
hulls are

```text
merge:      [c_FM * (1 - u_y), c_FM * (1 - l_y)]
separate:   [c_FS * l_y,       c_FS * u_y]
unresolved: [c_U,              c_U].
```

Thus the robust upper risks are `c_FM * (1 - l_y)`, `c_FS * u_y`, and `c_U`;
deferral is minimax exactly when `c_U` is no larger than both alternatives.
The full sharp interval `[p_lower,p_upper]` is the corollary
`(l_y,u_y)=(p_lower,p_upper)`; `[0,1]` gives the vacuous case when both binary
states remain feasible. If an interval is merely an outer bound on an unknown
smaller credal set, its merge/split values are conservative upper-risk bounds.
The deferral condition is exact for the deliberately enlarged outer-interval
problem, but those upper bounds cannot by themselves certify minimax deferral
for the unknown smaller set because the alternatives' true robust risks may be
lower. Witness: for `K_y={0.5}`, outer interval `[0,1]`,
`c_FM=c_FS=1`, and `c_U=0.75`, the enlarged problem selects unresolved while
each determinate action has true robust risk `0.5`.

All robust decisions are restricted to realised observations. An empty
observation fibre is an explicit invalid-model/interface terminal, not an
ordinary envelope over which a scientific loss is optimized. The fibre theory
is pointwise and set-theoretic; global measurable decoders or decision rules
require separate measurable-factorisation and conditional-law assumptions.

### 3.5 Global joint completion (`P3.EPE.P2`)

Each mapping contributes a constraint set `C_j` over admissible worlds. Global
glue requires a nonempty joint intersection. Pairwise nonempty intersections
are insufficient: `{1,2}`, `{2,3}`, and `{1,3}` intersect pairwise but have
empty triple intersection. This formalises why pairwise-only semantic
alignment can promote a globally inconsistent portrait.

## 4. Historical failure preserved exactly

### 4.1 Partial observation A004

The archived result remains `FAIL`.

- Mechanical redactions created 48 probes: 12 derivation, 8 held-out public,
  and 28 held-out exact.
- The current rule over-resolved all 48 because one-sided absence fell through
  as compatibility.
- Blanket observedness-aware abstention opened the channel but destroyed 29
  correct intact answers across the recorded corpora.
- The selective decisive-absence rule repaired the 9 determinate errors in the
  constructed record-gold corpus but destroyed 9 correct answers there; its
  zero-harm gate remained `FAIL`.
- Amendment 004 found 27 canonical observation orbits among 36 cases. Nine are
  two-case orbits with the same visible projections and different gold.
  Therefore the observation-only exact-agreement ceiling is 27/36.
- The current rule reaches 27/36 via 8 false merges and 1 false split.
- The selective unresolved rule avoids those determinate errors by abstaining
  on both cases in each ambiguous orbit, losing the nine answers the current
  rule happens to get right.

The corpus is constructed. It proves a finite observation-level lower bound;
it does not estimate missingness or harm prevalence in natural science.

### 4.2 Inert public-atlas coordinates

Removing referent, construct, measurement, or temporal context had zero effect
on the confirmatory public-reference holdout because the relevant cases did
not exercise them. This remains a coverage failure, neither necessity nor
dispensability evidence.

### 4.3 Ideal-product tie

The information-equivalent typed product tied 400/400. The tie is preserved
and elevated into the factorisation theorem. The upward question is which
minimal interface reconstructs the identified set, not how to keep a weaker
baseline weak.

## 5. Nearest work is inside the theory

| Donor family | Role inside the envelope | Claim explicitly not owned |
|---|---|---|
| MUSE, SciER, scientific IE | Construct the observation operator from sources | Scientific extraction or structured KB construction |
| I-ADOPT, SciSchema | Type scientific variables, constructs, measurements and procedures | Variable semantics or expert schemas |
| Ontology/schema alignment, LLMatch | Propose correspondence constraints | Generic matching/alignment |
| SCOPE/SCION, Executable Schema Contracts | Induce/fuse evidence-linked schemas and executable constraints | Schema induction, conservative fusion, provenance-aware shared schemas |
| Provenance-enhanced statements / DEC | Preserve attribution and source-relative stance in the world/observation state | Provenance graphs or pluralism as such |
| Measurement-equivalence and construct-validity traditions | Supply domain-specific admissibility constraints | Discovery of measurement non-equivalence |
| Scientific pluralism | Licenses multiple source-valid views within a portrait | Philosophical diagnosis of plurality |
| Partial identification / imprecise probability | Represents the set of source-compatible portraits/query values | Partial-identification theory itself |
| Blackwell information order | Interprets truthful observation refinement | Comparison-of-experiments theory |
| Robust Bayes / statistical decision theory | Maps identified sets to action bounds under declared losses | Minimax or Bayesian decision theory |
| Constraint processing | Tests joint completion beyond pairwise alignment | CSP/global-consistency algorithms |
| OpenScholar, BioSage, literature-based discovery | Acquire candidate sources and refinements | RAG, cross-domain synthesis, or A--B--C discovery |

The surviving contribution is the **scientific-identity authority interface**:
donor outputs define observations and constraints; the envelope records what
they jointly identify; only then does a declared loss authorize downstream
action.

## 6. Existing evidence under the new theory

| Evidence | What it supports | What it cannot support |
|---|---|---|
| Public-reference confirmatory n=32 | Typed obstruction reduces false merges versus flat canonicalisation on frozen already-structured cases while meeting the declared false-split guard | Raw-text, broad coordinate necessity, naturalistic envelope calibration |
| 400 exact scientific-identity contracts | Authority conditions matter relative to the frozen strong product; pairwise-only and forced canonical choices fail; information-equivalent product ties | Live ontology-engine superiority, expert external generality |
| A004 partial-observation sequence | Same visible projection can hide different source relations; observation-only lower bound exists on the constructed corpus | Natural prevalence or downstream cost |
| Frozen 768-cluster successor | Design and planned power only | Any empirical outcome |

The manuscript's widest present claim is therefore theorem-level:

> Given a declared admissible-world class, observed source projections,
> licensed constraints and downstream loss, scientific identity should be
> represented by the query image of the epistemic portrait envelope; a
> canonical answer is uniformly sound only when that image is a singleton, and
> otherwise action is a separate robust decision problem.

The empirical claim remains attached to its samples. This is not narrowing to
pass; it is widening through proof while keeping empirical authority honest.

## 7. Frozen 768-cluster successor: do not mutate

The existing successor identity is
`P3.PARTIAL_IDENTIFICATION.EXCESS_HARM.V1`.

Frozen design:

- 16 strata;
- 48 independent source-artifact-family clusters per stratum;
- 768 planned independent units across four scientific domains;
- mandatory nonzero within-comparison contrast on referent, construct,
  measurement and temporal-context coordinates, with joint-coordinate support
  reported so marginal variation is not mistaken for separability;
- four primary comparators in one familywise intersection claim;
- planned effect 0.15 against superiority margin 0.05;
- familywise alpha 0.05 and target joint power 0.90 under its declared Sidak
  planning model;
- primary endpoint: avoidable false merge or downstream decision harm above
  the proven observation floor.

Missing external bindings:

1. source-disjoint multi-domain atlas with nonzero within-comparison contrast
   on all four historically inert coordinates and a joint-coordinate support
   matrix;
2. independent protected gold labels;
3. raw-text attack corpus; and
4. downstream-decision evaluator custody.

The protocol terminal remains
`P3_PARTIAL_IDENTIFICATION_READY_FOR_EXTERNAL_ATLAS_NOT_A_SCIENTIFIC_RESULT`.
Do not insert manuscript language that implies its planned 768 units have been
collected, annotated, attacked, or evaluated.

## 8. Every negative becomes a distinct research problem

| Research ID | Adverse result / gap | Upward discriminator | Positive terminal that would be meaningful |
|---|---|---|---|
| `P3.EPE.R1` | Referent/construct/measurement/time ablations inert | Independent atlas with nonzero within-comparison contrast, joint-coordinate support accounting and coordinate-targeted contrasts | Coordinate contributes decision value above strong donor stack in at least one protected stratum, with multiplicity controlled |
| `P3.EPE.R2` | Partial observation imposes a 27/36 ceiling | Paired coarse/refined source observations where the missing coordinate is independently source-grounded | Refinement shrinks identified set and reduces floor-adjusted harm, not just total error |
| `P3.EPE.R3` | Selective abstention pays irreducible cost | Stakeholder-approved asymmetric decision losses | Envelope rule is minimax or lowers excess harm relative to comparators at preserved coverage |
| `P3.EPE.R4` | Pairwise mappings may be globally inconsistent | Multi-source cycles/hyperedges with protected joint-completion gold | Joint-completion checking reduces inconsistent promotions without unacceptable clean loss |
| `P3.EPE.R5` | Ideal typed product ties | Minimal-interface analysis plus alternative implementation | Independent implementation reconstructs the same identified sets and ties, confirming implementation neutrality |
| `P3.EPE.R6` | No raw-text authority | Source-disjoint raw-text attack with stage-attributed errors | Valid envelope coverage survives extraction perturbation at declared sharpness |
| `P3.EPE.R7` | No downstream utility | Protected scientific decision task with frozen loss | Floor-adjusted decision harm improves over forced canonical and blanket abstention comparators |
| `P3.EPE.R8` | No reader recoverability | Blinded source-reconstruction task | Readers recover supporting and non-preserved source coordinates at predeclared fidelity |
| `P3.EPE.R9` | No naturalistic prevalence estimate | Outcome-blind external sampling of source clusters | Prevalence/width of partial identification estimated with cluster-level uncertainty, independent of system outputs |

Negative terminals remain publishable scientific information. A positive
successor must have a material new observation, endpoint, comparator or
authority; it may not be obtained by weakening a failed threshold.

## 9. Execution sequence from here

### Phase A — theorem hardening (no protected outcomes)

1. Ask a mathematically separated reviewer to attack the definitions,
   factorisation statement, minimax bound and global-composition logic.
2. State admissible-world assumptions per domain. The envelope is only as
   valid as this model class.
3. Specify finite representations for envelopes: exact set, constraint system,
   interval/query oracle, or sampled outer approximation.
4. Define coverage and sharpness for set-valued portraits before any new
   empirical output.

### Phase B — execute the already frozen 768-cluster successor

1. Acquire sources outcome-blind and freeze source revisions.
2. Deduplicate at the source-artifact-family cluster, not annotation or pair.
3. Obtain independent protected gold and keep comparator outputs unavailable
   to annotators/adjudicators.
4. Verify nonzero within-comparison opportunity on all four inert coordinates
   before system scoring, publish the joint-coordinate support matrix, and do
   not treat between-cluster variation as separability; zero-opportunity strata
   cannot authorize a claim.
5. Run raw-text attacks and stage-attributed error analysis.
6. Evaluate the frozen primary endpoint and all four contrasts exactly as
   declared; preserve a negative terminal if any intersection member fails.

### Phase C — downstream decision study under a new identity

This must not be retrofitted into the frozen successor after outcomes. Freeze a
new protocol for `P3.EPE.H4` with:

- a concrete decision and stakeholders;
- elicited or justified `c_FM`, `c_FS`, and `c_U` ranges;
- source-disjoint cases and evaluator custody;
- envelope validity/coverage as a gate before sharpness;
- forced-canonical, blanket-abstain, calibrated probabilistic and strongest
  donor-stack comparators;
- floor-adjusted regret and sensitivity across the loss range; and
- a terminal that permits null, harmful, and cannot-check outcomes.

## 10. Reviewer-facing falsifiers

The wider theory fails or must change if any of the following occurs:

1. A claimed observation-only rule is correct on two verified worlds with the
   same frozen observation and different query truth. That would show the
   observation was not actually the same or the query/gold was inconsistent.
2. A purported refinement enlarges the identified set under unchanged
   admissible-world assumptions. That would show it is not a refinement.
3. Two interfaces reconstruct the same identified sets and use the same loss
   but yield different robust loss tables. That would falsify an implementation
   or the factorisation binding.
4. The naturalistic envelope excludes independent gold above its declared
   tolerance. Sharpness cannot rescue invalid coverage.
5. Joint-completion checking does not reduce any protected globally
   inconsistent promotion, or its clean-composition loss breaches the frozen
   guard.
6. The 768-cluster endpoint does not improve against every frozen primary
   comparator. The successor is then negative; no subset is promoted as the
   original intersection claim.

## 11. Files changed in this ascent

- `papers/paper-03-global-knowledge-portrait/manuscript/main.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/bibliography.bib`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/00-abstract.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/10-introduction.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/20-related-work.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/30-method.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/36-partial-identification-theory.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/56-p3x-successor.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/06-results.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/07-limitations.tex`
- `papers/paper-03-global-knowledge-portrait/manuscript/sections/08-conclusion.tex`
- `papers/paper-03-global-knowledge-portrait/THEORY_CLAIM_LEDGER_V1.md`
- `development/p3-scientific-ascent-2026-08-23/DEVELOPMENT_PACKET.md`

## 12. Current publication judgment

The paper is scientifically stronger because it now has:

- a general object rather than a pairwise-rule slogan;
- theorem-level scope independent of the tiny empirical samples;
- a proof that the negative partial-observation terminal exposes irreducible
  information loss;
- a universal sufficient-interface result that explains the ideal tie;
- explicit decision bounds and a floor-adjusted empirical estimand;
- a global-composition theorem; and
- a research programme in which every adverse result has a distinct identity
  and discriminator.

It is **not yet top-tier empirically**. The missing decisive contribution is
execution of the independent naturalistic atlas and downstream decision study.
The correct route is not to shrink the claim until the old evidence passes; it
is to keep the general theorem, acquire the information the theorem says is
necessary, and let the new protected hypotheses succeed or fail under their
own identities.

## 13. Public OAEI development discriminator

The V1 public OAEI execution failed before reference access because
fragment-only keys were non-injective and one AML pair lay outside the frozen
signature.  That identity is retained without a result.  A distinct V2
document-aware successor froze 68,187 cases and 477,309 predictions before the
public reference join.  AML ran 19/20 pairs with byte-identical replay; test
206 remained unparsable.

V2 then failed the two gates that make a harm comparison interpretable.
Candidate-universe recall was 1,335/1,434 (0.930962), and envelope coverage was
0.995542 with 304 failures.  Although candidate-minus-AML floor-adjusted harm
was negative in all three frozen regimes, those directions cannot promote an
invalid evaluation universe.  The preserved terminal is
`PUBLIC_CANDIDATE_UNIVERSE_INVALID__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY`;
protected and frozen-768 authority remains `CANNOT_CHECK`.

The failure advances the theory by separating disagreement from shared
evidence failure.  A successor must enumerate cross-construct referents, treat
missing/non-expressible public relations as `CANNOT_CHECK`, attain envelope
coverage 1.0 under an information-equivalent ideal, and transfer to multiple
untouched ontology families before any comparative claim.  The bounded result
is archived at
`development/p3-oaei-public-development-execution-2026-08-23/RESULT_V2.json`
with SHA-256
`5f5edee08aca44d34e5748d16f1923fba88f3eb47bf2e591c49eea37ee83fdef`.

## 14. Cross-construct V3 coverage--harm boundary

V3 is a distinct, post-public-gold-informed development successor and does not
rewrite V2. It freezes 193,305 input-only cases, including 125,262
cross-construct cases. The licensed binary scoring census contains 117,914
cases; 75,391 are retained as `CANNOT_CHECK` because the reference member is
missing, the pair lies outside the member's observed domain, or the relation is
non-binary. All 1,399 binary equivalence pairs are present, including 64
cross-construct pairs excluded by V2, and all 35 ordered relations are mapped
to `CANNOT_CHECK`.

The full binary identification envelope reaches coverage 1.0 and ties its
information-equivalent ideal. It is unresolved on every scorable case, however,
and candidate-minus-AML harm is `+0.224799`, `+0.224732`, `+0.193522`.
Therefore the composite terminal is
`PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY`.
The predecessor agreement-to-point rule remains falsified on 333 public
equivalences. This is a coverage mechanics pass and a comparative adverse
result, not superiority.

Artifacts are under
`development/p3-oaei-cross-construct-successor-2026-08-23/`; `RESULT_V3.json`
has SHA-256
`2c9e59dc323cf65200152ffc259341131e60bb040175f9f109872f35d5d468d4`.
The next discriminator is a proper selective subenvelope on multiple untouched
ontology families with binary coverage 1.0, harm noninferiority in every frozen
regime, current strong comparators, and cluster-level replication. Protected
source-disjoint multi-family authority remains `CANNOT_CHECK`.

## 15. V4 feasibility stop and V5 direct-certificate calibration

The outcome-blind V4 source/comparator audit remains immutable. Zero of seven
candidate OAEI families passed its complete rights, immutable-identity,
binary-negative and source-disjoint-replication gate; AML, LogMap and BERTMap
identities were bound but 0/3 were execution-ready. No V4 outcome was opened.
This does not prove global source deficits; it records that the frozen V4 frame
could not license binary truth or execution.

V5 opened a new identity to test the logically prior direct-certificate
semantics. Three immutable rights-audited families passed the new unchanged
gate: ENVO, FIBO Foundations and W3C PROV-O. All 61 Git blobs matched;
11,076,252 bytes parsed into 121,589 triples. The conflict-free registry has
4,838 point-identified pairs: 4,789 `GLUE` (4,780 same-IRI identities and nine
direct named equivalences) and 49 direct named `OBSTRUCTION` certificates.
There were zero conflicts, and neither absence nor reasoner inference supplied
a label. The general completion-class corollary follows: direct certificates
point-identify their finite cells, uncertified cells remain
`{GLUE, OBSTRUCTION}`, and conflict-free certificate addition refines the
identified sets monotonically.

Exact terminal:
`PUBLIC_V5_DIRECT_CERTIFICATE_SEMANTICS_CALIBRATION_PASS__NO_COMPARATOR_PERFORMANCE_EXECUTED__NO_NATURALISTIC_TRANSPORT`.
The result does not repair the V3 harm terminal, the V4 0/7 source-admission
terminal, or the 0/3 comparator-readiness boundary. Each V5 family uses
byte-identical views; no naturalistic cross-ontology transport or matcher
performance was measured. The integrated packet is
`development/p3-authoritative-negative-semantics-v5-2026-08-23/`.

The next discriminator is an outcome-blind native-artifact preflight for all
three comparators, followed by at least three independently governed and
independently authored ontology-pair families with the unchanged rights,
identity, explicit-negative and conflict gates before any matcher output is
opened.

### V6 native preflight: two smoke surfaces close, BERTMap remains CANNOT_CHECK

AML v3.2 exited zero and emitted one parseable three-cell native RDF alignment.
LogMap 4.0 exited zero and emitted three equivalent RDF/TSV mappings; its
upstream RDF header duplicates ontology 1, so row namespace and RDF--TSV
equivalence remain mandatory. BERTMap/DeepOnto matched its exact model weight,
loaded both 16-class fixtures and built 108 training plus 12 validation records,
then failed before training because the pinned Transformers 4.51.3 constructor
uses `eval_strategy` while the pinned DeepOnto source passes
`evaluation_strategy`. Zero of five required BERTMap artifacts existed.

Exact terminal:
`P3_V6_TWO_OF_THREE_NATIVE_SMOKE_READY__BERTMAP_PINNED_LOCK_API_INCOMPATIBILITY_CANNOT_CHECK__V5_SCIENTIFIC_READINESS_UNCHANGED_ZERO_OF_THREE`.
Two of three toolchains are native-smoke ready, but scientific comparator
readiness remains 0/3: no gold, protected case, scoring, harm or naturalistic
transport was opened. A V7 dependency tuple is frozen but unexecuted. The
integrated packet is
`development/p3-comparator-native-preflight-v6-2026-08-23/`.

## 16. V7T authority-augmented composition boundary

The V7T theory successor moves P3 upward from content-only partial
identification to claim-relative scientific authority without widening any
empirical result.  For a frozen claim, its source, rights, executable,
population, reference and custody predicates are placed inside an
authority-augmented query whose new terminal lies outside the scientific truth
codomain.  An authorized claim is point identified exactly when all gates are
true and the substantive query is constant throughout the observation fibre.

The finite discriminator uses two worlds with identical local artifacts and
all local preflight gates true.  Only an unobserved cross-stage scientific-
identity relation changes, so the global identified set remains `{0,1}`.
Local readiness therefore does not compose automatically.  This result
formalizes why AML/LogMap smoke, a BERTMap dependency stop, and a set of passed
source checks cannot be summed into comparator performance or superiority.

Exact terminal:
`P3_V7T_AUTHORITY_AUGMENTED_FIBRE_CRITERION_PROVED__LOCAL_READINESS_NONCOMPOSITION_COUNTERMODEL_PASS__V6_SCIENTIFIC_READINESS_UNCHANGED_ZERO_OF_THREE__NOVELTY_CANNOT_CHECK`.
The integrated packet is
`development/p3-authority-composition-theory-v7t-2026-08-23/`.  It contains a
32/32 same-lane validation and checksum manifest.  Distinct theorem novelty,
independent review, naturalistic multi-family truth, complete 3/3 comparator
execution and external custody all remain `CANNOT_CHECK`; P3 remains
`NOT_SUBMISSION_READY`.


## 17. V7 BERTMap constructor and closed-parser binding

The outcome-blind V7 packet under
`development/p3-bertmap-execution-binding-v7-2026-08-23/` binds the canonical
BERTMap paper source at `ce848402b40e2f9513bf2d004894d3f82635022c` and
maintained DeepOnto 0.9.3 at `74ca8d47f01bad0b8739f19ee2c392bdf6d9c090`.
A 26-distribution Python-3.10 lock using Transformers 4.46.3 accepts the
DeepOnto `evaluation_strategy` constructor call, so the V6 mismatch becomes
`DEPENDENCY_API_CONSTRUCTOR_PASS`. A closed five-artifact parser passes 7/7
synthetic contract checks.

The next source stage fails independently when a nonempty `EntityMapping` table
is read with a truthy threshold: the reader uses `dp["Score"]` on a pandas
`itertuples` namedtuple, reproducing `TypeError: tuple indices must be integers
or slices, not str`. A falsey threshold short-circuits the defective
comparison, so V7 must not be read as an all-nonempty failure. No native
BERTMap artifact was produced; the required count remains 0/5, native-smoke
readiness remains 2/3 and scientific comparator readiness remains 0/3. The
Python/JVM runtime, bundled-component rights/SBOM, source reader, fresh no-gold
smoke and independent rights-valid evaluation remain unbound.

Exact terminal:
`P3_V7_BERTMAP_PAPER_SOURCE_AND_DEPENDENCY_CONSTRUCTOR_COMPATIBILITY_BOUND__CLOSED_FIVE_ARTIFACT_PARSER_BOUND__NONEMPTY_SOURCE_TABLE_READER_DEFECT_AND_FULL_NATIVE_SMOKE_CANNOT_CHECK__NATIVE_READINESS_TWO_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE`.
The packet passes 63/63 validation and 23/23 checksums. It contains no ontology,
model, benchmark, gold, protected output, training, prediction, repair or
scoring result. P3 remains `NOT_SUBMISSION_READY`.

## 18. V8 BERTMap truthy-threshold table-reader repair

The prospective V8 packet under
`development/p3-bertmap-table-reader-repair-v8-2026-08-23/` targets the single
downstream V7 root cause without opening any comparator outcome. Against exact
DeepOnto `mapping.py` SHA-256
`9cf0dce1c5bd142e4175f628f8f3267f54ed6deac9f31e165a25b4a073eedff0`,
the Apache-2.0 patch changes only `dp["Score"]` to `dp.Score`. Patch SHA-256 is
`412050c5d3a0e7891a21744a9690d3e4ba06886ea51eec273b6045bff688e42b`;
the repaired source SHA-256 is
`d0b3b6cfdee45019783707c4bd623cc76f8325142828cf1e10ebb74ad628d70f`.

Eight of eight outcome-blind synthetic cases pass. Empty and falsey-threshold
nonempty behavior is unchanged. With threshold 0.5, the pinned source
reproduces the namedtuple `TypeError`, while the repaired source applies the
existing threshold rule and retains only the score-0.9 row. Missing and
nonnumeric scores, stale source, reference mode and external fixtures fail
closed. After normalizing only the frozen access, the method AST is unchanged.
The exact V7 parser accepts a temporary five-file authored shape, but those
files were deleted and do not count as native BERTMap artifacts.

Exact terminal:
`P3_V8_BERTMAP_TABLE_READER_MINIMAL_REPAIR_SOURCE_HASH_AND_SYNTHETIC_EMPTY_NONEMPTY_EXECUTION_BOUND__MALFORMED_STALE_AND_PROHIBITED_CASES_FAIL_CLOSED__V7_PARSER_SYNTHETIC_COMPATIBILITY_BOUND__NATIVE_SMOKE_AND_SCIENTIFIC_READINESS_UNCHANGED`.
The packet passes 42/42 scientific validation checks and 14/14 checksums;
`RESULT_V8.json` SHA-256 is
`6ccd4b9ab8dafe8dbf8bcf0c33cb76006ab043c0df34bd5e0d0595ef2d03138b`.
Actual artifacts remain 0/5, native-smoke readiness remains 2/3 and scientific
readiness remains 0/3. Complete Python/JVM rights/SBOM, a content-addressed
repaired runtime, the fresh no-gold five-artifact smoke and independent
evaluation remain unbound. P3 remains `NOT_SUBMISSION_READY`.

## 19. V9 complete-runtime native attempt and localized repair stop

The prospectively frozen V9 packet under
`development/p3-repaired-native-runtime-v9-2026-08-23/` closes the previously
shared complete-runtime and component-rights root. Its Python/JVM gate passes
30/30 before one authorized offline attempt. OpenJDK 17.0.19 starts; BERT
fine-tuning, global prediction, extension and filtering complete in 241.890
seconds. The V8 `dp.Score` repair is reached natively without the prior
truthy-threshold `TypeError`.

Four of five required regular artifacts are retained: `raw_mappings.json`,
`raw_mappings.tsv`, `extended_mappings.tsv` and `filtered_mappings.tsv`.
`repaired_mappings.tsv` is absent. LogMap 4.0 binds OWLAPI 4.1.3 and Guice 4.0;
Guice cglib raises `InaccessibleObjectException` under Java 17 because
`java.base/java.lang` is not open to the unnamed module. DeepOnto fails to
propagate that child exit and then raises a secondary `FileNotFoundError` for
the absent repair output. The unchanged V7 parser therefore preserves
`CANNOT_CHECK_NATIVE_ARTIFACT_CONTRACT_FAILURE`. There is no retry or
post-result patch.

Exact terminal:
`P3_V9_COMPLETE_RUNTIME_RIGHTS_PASS__SINGLE_NATIVE_ATTEMPT_REACHED_FOUR_OF_FIVE_ARTIFACTS__LOGMAP_JAVA17_GUICE4_MODULE_ACCESS_CANNOT_CHECK__NO_RETRY__NATIVE_READINESS_TWO_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE`.
Native readiness remains 2/3 and scientific readiness 0/3. No gold, reference
alignment, protected output, correctness, performance, harm, coverage or
transport score was opened.

The resource-efficient successor is not another full training run. First
freeze a repair-only, no-gold LogMap microgate with the exact V9 Java/JAR/input
hashes and add only `--add-opens=java.base/java.lang=ALL-UNNAMED` before
`-jar`. It must expose the child exit directly and require a regular repair
output. Only a microgate pass authorizes a separately frozen full successor.
The V9 validator passes 33/33; validation-receipt SHA-256 is
`2a6c329587266859de77b1ec164be9055636c8e9b45ab321f3962707be74ffe7`.
Cleanup released approximately 5.42 GB and retained a 9.1 MB packet.

## 20. V10 under-bound Java microgate

V10 keeps the exact V9 Java, LogMap JAR, ontology and filtered-input hashes and
runs one repair-only child with the sole
`--add-opens=java.base/java.lang=ALL-UNNAMED` delta. It exits one in 0.133503
seconds because the retained thin JAR has 0/90 manifest dependencies; OWLAPI is
missing before the Guice site is reached. The flag's efficacy therefore remains
`CANNOT_CHECK`, V10 is not retried, and no full successor is authorized from
this identity. Packet:
`development/p3-java17-add-opens-microgate-v10-2026-08-23/`.

## 21. V11 exact LogMap classpath closure

V11 reconstructs all 90 adjacent JARs (25,337,399 bytes), matches every V9 Java
SBOM hash, and executes one repair child with the same five launch identities.
The child exits zero in 0.429010 seconds and emits a regular 16-row repair file.
This authorizes a distinct full successor but establishes runtime/interface
conformance only; all row roles visibly retain `Optional.of(...)` wrappers.
Packet: `development/p3-logmap-manifest-classpath-v11-2026-08-23/`.

## 22. V12 one full native attempt

V12 passes 15/15 pre-execution identity gates and runs exactly one offline,
no-gold BERTMap attempt. It finishes in 231.909885 seconds, propagates direct
LogMap exit zero, and emits 5/5 regular artifacts. Native execution readiness
therefore reaches 3/3. All 16 source and 16 target repair fields remain wrapped
and fail literal universe membership, so the unchanged parser returns
`CANNOT_CHECK`; raw bytes are preserved. Packet:
`development/p3-full-native-runtime-v12-2026-08-23/`.

## 23. V13 typed Optional decoder

V13 performs no retraining or Java execution. Its anchored typed grammar passes
12/12 adversarial cases, decodes all 16 source and 16 target strings injectively
to exact role-specific universe members, and passes the unchanged structural
parser. Decoded SHA-256 is
`c67ee88d541013f41984b239f9cdeaebdcd81573f2080d8af24c7688207dd0f3`;
the raw V12 artifact stays byte-identical. This closes structural conformance,
not mapping truth. Packet:
`development/p3-optional-wrapper-typed-decoder-v13-2026-08-23/`.

## 24. V14 provider-native reference authority gate

V14 checks 21 OAEI inventory units, 21 ontology-member hashes and 19 reference
hashes in 0.001180 seconds. The frozen V12/V13 pair is an authored synthetic
fixture; neither ontology hash nor local `urn:orion` IRI matches the provider
registry, and no exact Bio-ML version/rights/reference identity packet exists.
V14 therefore opens no gold and computes no precision, recall, F1 or comparator
score. Scientific readiness remains 0/3. Receipt SHA-256 is
`b7477e2472b1ab5580beb8191124fe6f3a94c6500642084694c9372f24bf1f8b`;
result SHA-256 is
`fc1f1d35668604e72bc63edd397988eb85c035145b0e6025b848d7c5d3c96314`.
The next valid discriminator is a separately frozen provider-native exact
identity packet before one prospective matcher run. Packet:
`development/p3-public-reference-alignment-v14-2026-08-23/`.
