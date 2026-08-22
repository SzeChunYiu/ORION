# ORION-QG external donor register V2 — the hostile pass

Date: 2026-08-22. Branch: `claude/orion-harness-verification-b17qdj`.
Supersedes `QG_EXTERNAL_DONOR_REGISTER_V1.md`, which is retained unmodified.
Authority: development record only. **This register lowers claims; it grants nothing.**
`novelty_authority: false`. NOT_R6.

Produced by lane QG-19 under `QG19_HOSTILE_NOVELTY_PROTOCOL_V1.md`, frozen at `aaf0987a`
before any search ran. Terminal: **`QG19_SUBSUMPTION_FOUND__NOVELTY_REDUCED`**.
Full verdicts: `QG19_HOSTILE_NOVELTY_RESULTS.json`. Full query log with result counts:
`QG19_QUERY_LOG.md`.

## 0. What changed between V1 and V2

V1 searched for context. V2 searched for a parent. The difference in outcome is not small.

V1 concluded that "no paper surfaced that produces the bundle" and that the intrinsic
support number "also found no parent". V2, running the same programme's claims against
three mandatory query families each — own vocabulary, donor-field translation, and an
inverted or survey query — found parents for five of six claims, two of them outright.

The single most consequential correction: **our headline structural criterion is a
textbook result under another name, and the textbook is coding theory.** V1 never
searched coding theory. Neither did the frozen QG-19 attack vector, which named algebraic
dynamic programming, bounded treewidth and fixed-parameter tractability. The killing
source was found by translating "conserved syndrome" into the field that already owns the
word.

**Retrieval caveat, stated once and applying to every entry below.** Direct document
retrieval was refused by the session's egress policy on all eleven attempts (arxiv.org,
en.wikipedia.org, handwiki.org, semanticscholar.org, mimuw.edu.pl, dl.acm.org,
link.springer.com, scispace.com). Every passage below is the text returned by the search
tool, not text read off the primary document. Nothing here is document-confirmed. A
successor lane with document access should re-verify each passage against its source
before any of these citations enters a paper.

## 1. Donors that subsume, newly found (D6–D12)

### D6 — Trellis decoding of linear block codes (**SUBSUMES C-A**)

*J. K. Wolf, "Efficient Maximum Likelihood Decoding of Linear Block Codes Using a
Trellis", IEEE Trans. Inform. Theory 24(1):76–80, 1978.*

> "It is shown that soft decision maximum likelihood decoding of any (n,k) linear block
> code over GF(q) can be accomplished using the Viterbi algorithm applied to a trellis
> with no more than q^{(n-k)} states."

This is C-A. The trellis state at position *i* is the partial syndrome `H·x_{1..i}` — the
image of a prefix under a homomorphism into a fixed finite abelian group. The Viterbi
recursion over it is min-plus composition of per-position local costs. The cost is linear
in the block length with a factor equal to the syndrome-space size; our
`O(C_ext·2^{2D}·n + n·A^L)` is that bound with `2^D = q^{n-k}`. Deciding optimality of a
given configuration is the same pass at the same order. Naive enumeration of `q^n` words is
our `Θ(A^{Ln})`. Every structural hypothesis C-A imposes is a hypothesis of this theorem,
and the theorem is stated for an arbitrary linear code rather than one hand-built family.

The word *syndrome* is not a coincidence of vocabulary. It is the same object.

Supporting, same donor: syndrome-trellis constructions place at most `2^{(1-r)·n}` states
per level, i.e. linear in blocklength and exponential in the number of parity checks — the
`n` versus `2^D` split C-A reports as a separation.

### D7 — The generalized distributive law (**SUBSUMES C-A, more generally**)

*S. M. Aji and R. J. McEliece, "The generalized distributive law", IEEE Trans. Inform.
Theory 46(2), 2000.*

> "It includes as special cases the Baum-Welch algorithm, the fast Fourier transform (FFT)
> on any finite Abelian group, the Gallager-Tanner-Wiberg decoding algorithm, Viterbi's
> algorithm, the BCJR algorithm, Pearl's 'belief propagation' algorithm, the
> Shafer-Shenoy probability propagation algorithm, and the turbo decoding algorithm. …
> This algorithm is guaranteed to give exact answers only in certain cases (the 'junction
> tree' condition), and the power of the GDL lies in the fact that it applies to
> situations in which additions and multiplications are generalized. A commutative
> semiring is a good framework for explaining this behavior."

C-A is the (min,+) instance of the GDL on a chain — the simplest junction tree there is.
The GDL quantifies over all commutative semirings and all junction-tree factorizations.

Two more general statements of the same content were also retrieved and must be cited
alongside it:

- **Bucket elimination** — R. Dechter, Artif. Intell. 113(1–2):41–85, 1999: "The time and
  space complexity of Adaptive-consistency is O(n·exp(w\*(d))), where w\*(d) represents the
  induced-width. … problems having bounded induced-width for some constant can be solved in
  polynomial time." `O(n·exp(w*))` with `w*` frozen *is* "linear in n with a constant factor
  exponential in a structural dimension".
- **Courcelle's theorem and its optimization extension** — "Courcelle showed that every
  problem definable in Monadic Second-Order Logic (MSO) can be solved in linear time on
  graphs with bounded treewidth. … The result has been extended to cover optimization
  problems."

### D8 — Gomory's group relaxation (**SUBSUMES C-A in the nonnegative-cost sub-domain**)

*R. E. Gomory (1965); J. F. Shapiro, Oper. Res. 16 (1968) 103–131 and 928–947, as
reported through arXiv 2602.13494 and the Springer "Gomory group minimization problem"
entry.*

> "By relaxing the nonnegativity constraints on a set of basic variables, an integer
> programming problem can be reduced to a shortest route problem over a finite Abelian
> group. … The classical approach for solving group relaxations leverages the
> nonnegativity of cost vectors to reduce the group relaxation to finding the shortest
> path in a Cayley directed graph."

Minimizing a sum of per-item costs subject to a residue constraint in a fixed finite
abelian group, solved as a shortest path whose node set is the group. That is C-A's
optimization problem verbatim, with the group order in place of `2^D`. Sub-domain:
nonnegative cost vectors. Outside it, D6 and D7 apply without sign restriction.

Shapiro's 1968 papers themselves could not be retrieved beyond bibliographic data and are
recorded `CANNOT_ASSESS`.

### D9 — Algebraic Dynamic Programming (**general form of C-A's hypotheses**)

*R. Giegerich and C. Meyer, ADP / Bellman's GAP line.*

> "Algebraic dynamic programming is a method for developing and reasoning about dynamic
> programming algorithms, in which yield grammars and evaluation algebras constitute
> abstract specifications of dynamic programming algorithms. … An ADP problem can be
> solved in polynomial time and space by the yield parser only under the condition known
> as Bellman's Principle of Optimality."

C-A's three structural hypotheses are a restatement of the ADP admissibility condition.
ADP formalizes the question "when does this DP argument apply"; C-A answers it for one
grammar.

### D10 — Support size of integer optimal solutions (**C-B is an instance**)

*I. Aliev, J. De Loera, F. Eisenbrand, T. Oertel, R. Weismantel, "The Support of Integer
Optimal Solutions", SIAM J. Optim. 28(3):2152–2157, 2018.*

> "Sparsity-type results study the size of support of solutions to integer programs. The
> support of a vector is the number of nonzero-components. … given an integral m × n matrix
> A, the integer linear optimization problem has an optimal solution whose support is
> bounded by 2m log(2√m‖A‖∞) … They furthermore provide a nearly matching asymptotic lower
> bound on the support of optimal solutions."

"An optimal solution whose support is bounded by B" plus "a nearly matching lower bound" is
exactly the two-sided support budget κ. And *Y. Dubey and S. Liu, arXiv:2307.08826*: "They
give an upper bound on the smallest support size as a function of A … The bound is
asymptotically tight". **"Smallest support size" is the field's name for our κ.**

Distinguished, and only this far: Carathéodory-rank results bound *representations* by
generators, not the support of a cost-optimal solution — the same distinction V1 drew
against D1's normal forms.

### D11 — The negative/null-results taxonomy programme (**C-E is an instance**)

*K. Maheshwari, D. Katz, S. D. Olabarriaga, J. Wozniak, D. Thain, "Report on the first
workshop on negative and null results in eScience", Concurrency Computat. Pract. Exper.,
2017, doi 10.1002/cpe.3908.*

> "One of the outcomes of the panel discussion was a call for a taxonomy of negative and
> null results in eScience … The workshop also addressed broader issues, such as whether
> negative results or methods to obtain them can be patented, whether incremental
> competitive results should be considered negative, and what happens to positive results
> obtained before further investigation leads to their negation."

The object `orion.kernel.negative` implements was explicitly called for in 2017, in this
field. Reinforced by *arXiv:2606.04220, "Dead Science Walking"* (2026-06), which proposes
"a structured schema for null results … including hypothesis, protocol, outcome, effect
size, confidence interval, preregistration link, and provenance" precisely so an automated
research pipeline can retrieve what failed — our design rationale, two months earlier. Its
failure mode "confident rediscovery" names what `DONOR_SUBSUMPTION` exists to catch.

Also bearing: *arXiv:2406.03980, "Position: Embracing Negative Results in Machine
Learning"* (a two-category typology, NMNR/EMNR) and the survey of 23 provenance, assertion
and evidence ontologies (PMC12376154).

### D12 — Governance laundering (**SUBSUMES C-F**)

*E. Meyman, "Governance Laundering: A Taxonomy of Failure Modes in AI Compliance
Architectures", SSRN 6293818, February 2026 (Zenodo 10.5281/zenodo.18328587).*

> "Governance laundering is a structural failure in which governance artifacts, such as
> logs, dashboards, attestations, certificates, or policy records, are treated as
> governance evidence even though they cannot support independent verification of a
> specific AI decision. … The paper distinguishes governance artifacts from governance
> evidence, defines seven evidence-grade governance requirements, and maps those
> requirements to seven failure-mode families: policy theater, vendor-dependent
> verification, trace-artifact mimicry, delegated authorization, post-hoc signature
> injection, custody gaps, and semantic drift. … a reproducible method for distinguishing
> evidence-grade governance from monitoring-grade systems and artifact-only compliance
> records, and for identifying where the authorization artifact gap is being obscured by
> replay-insufficient records."

This is C-F, generalized, six months earlier. Our AGREE-on-a-defective-receipt is
"artifacts treated as evidence even though they cannot support independent verification".
Our failure is "custody gaps" and "trace-artifact mimicry". Our
deterministic-replay-proves-nothing is "replay-insufficient records". Our
`corroboration.py` fail-closed type check is "distinguishing evidence-grade from
artifact-only records" via typed requirements — seven grades where we have three.

The phenomenon also already carries a name in the research-pipeline setting:
**replication laundering**, one of the four governance failure modes in arXiv:2606.04220.

Supporting, all independently sufficient for the first half of C-F:

- *J. T. Leek and R. D. Peng, "Reproducible research can still be wrong: Adopting a
  prevention approach", PNAS 112(6):1645–1646, 2015.* The title is the claim.
- *SLSA specification, slsa.dev*: "SLSA does not tell you whether the developers writing the
  source code followed secure coding practices. Additionally, SLSA doesn't tell you if the
  source code has vulnerabilities. … SLSA measures specific aspects of supply chain
  security, particularly those that can be fully automated; other aspects, such as
  developer trust and code quality, are out of scope."
- *ACM Policy on Artifact Review and Badging*: "ACM recommends three separate badges …
  Artifacts Available, Artifacts Evaluated (Functional or Reusable), and Results Validated
  (Reproduced or Replicated)." A typed, graded corroboration-strength property in
  production since 2016, existing so that a weaker grade cannot be presented as a stronger
  one. `FROM_PRIMITIVES_VERIFIED` is ACM's "Results Reproduced" — independently, without
  the author artifact.
- *Reproducible Builds*: scoped to "verify that no flaws have been introduced during the
  build process", silent on the correctness of the input.

## 2. Nearest misses, newly found (D13–D15)

### D13 — Equality saturation and e-graph extraction (narrows C-C)

*M. Willsey et al., "egg: Fast and Extensible Equality Saturation", 2021; R. Tate et al.,
LMCS 2011.*

> "A cost function is local when the cost of a term can be computed from the function
> symbol and the costs of the children. With such cost functions, extracting an optimal
> term can be efficiently done with a fixed-point traversal over the e-graph that selects
> the minimum cost e-node from each e-class. … The extracted term is a global optimum if
> saturation was reached in the exploration phase."

Three of our five components at once — a complete rule set, a local cost model, and a
decidable certificate of global optimality — for arbitrary term languages. **Distinguishing
property, and the only one:** equality saturation does not give a structural predicate over
*inputs* that says, without running the extractor, where the optimum lives; nor a
prospective forecast. V1's D1 correction ("optimum-attaining, not equational completeness")
must now be paired with this one, because equality saturation is precisely the place where
a complete rule set *does* yield an optimum.

### D14 — Phase transitions in quantum-circuit compilation (narrows C-C)

*A. De Girolamo, D. Rattacaso, S. Notarnicola, I. Siloi, S. Montangero, arXiv:2608.00189,
2026-07-31.*

> "Quantum-circuit compilation aims at finding an optimized realization of a target circuit
> under given constraints … The compilation process is connected with the thermodynamics of
> a many-body spin system: circuit infidelity plays the role of the energy function and
> low-temperature states correspond to compiled circuits. … The ensemble probes not only
> the optimum, but also the organization of near-optimal configurations, distinguishing
> disordered, clustered, and ordered regimes."

A regime map of where a compilation family's optimum lives, published three weeks before
this lane ran, by statistical-mechanics order parameters rather than exact predicates.
"Regime" next to "compilation" is an occupied phrase as of this month.

### D15 — Dominance rules (C-C's donor-optimal region is an instance)

> "A dominance rule consists of identifying, based on a certain property, a subset of
> solutions that contains at least one optimal solution. One can then solve the original
> problem by exploring only the reduced set of solutions."

"A structural property identifying a subset guaranteed to contain an optimum" is what QG
calls a donor-optimal region with a sufficiency bound. QG-7e's per-block target-permutation
domination argument is a dominance rule.

## 3. C-D: the rank/κ mismatch is formulation-dependence

No source was found stating C-D's specific content, and Q27's four sub-searches across the
ZX-calculus and stabilizer-simplification literature returned nothing naming the
phenomenon for circuit invariants. What was found is the general fact of which C-D is an
instance, in two fields:

- **Reformulation in integer programming**: "Typically, one reformulates integer and mixed
  integer programs so as to obtain stronger linear programming relaxations, and hence
  better bounds… Polyhedral outer approximations in a higher dimensional space can often be
  much stronger than approximations in the original space." Bound strength is a function of
  the formulation, not of the object.
- **The log-rank gap**: "A simple upper bound is that communication complexity is at most
  the rank, which is exponentially worse than what is conjectured by the log-rank
  conjecture." The canonical example of a rank invariant that bounds a true measure soundly
  but not tightly, with the gap itself an open object — the same shape as QG-6's sound-but-
  loose rank 5 against κ=1.
- Adjacent, in our own donor domain: "Finding minimum weight generators for stabilizer
  codes … is, in general, NP-hard. … The choice of stabilizer generators for a given
  stabilizer state is not unique."

QG-20 already self-declared H1 `CANDIDATE_RELATION_FROM_TWO_POINTS__NOT_A_LAW__NOT_A_THEOREM`.
The correction is presentational: it is an instance of formulation-dependence, not a
phenomenon the programme uncovered.

## 4. Hostile sources recorded under G5

Sources that *contradict* rather than anticipate, kept rather than filed as off-topic:

1. **arXiv:2310.05958, "Optimising quantum circuits is generally hard"** — "Many gate
   optimization problems for approximately universal quantum circuits are NP-hard,
   including optimizing the T-count or T-depth in Clifford+T circuits… Optimizing the
   number of CNOT gates or Hadamard gates in a Clifford+T circuit is also NP-hard."
   Does not contradict C-A as conditioned, but contradicts any reading of C-A as a
   statement about compilation.
2. **arXiv:2510.16420, "Exact Quantum Circuit Optimization is co-NQP-hard"** — same effect,
   with the lattice-surgery and braiding NP-hardness results alongside it.
3. **arXiv:2105.02291 (Quantum 5, 580), Bravyi et al.** — "finds circuits that are only
   0.2% away from optimal for 6 qubits and reduces the two-qubit gate count in circuits
   with up to 64 qubits by 64.7% on average, compared to the Aaronson–Gottesman canonical
   form." A 64.7% average reduction against the canonical construction is evidence that in
   the Clifford setting the donor-exact picture the QG families exhibit does not hold on
   real workloads. This bears directly on the wave-2 record's own admission that the
   machinery has not yet beaten the simple construction on a real instance.

The same paper is also a **donor for C-A's method in our own application domain**: "a
symbolic peephole optimization method works by projecting the full circuit onto a small
subset of qubits and optimally recompiling the projected subcircuit via dynamic
programming."

## 5. Status of V1's donors after the hostile pass

| V1 donor | status in V2 |
|---|---|
| D1 complete equational theories | stands as V1 recorded it; the required "optimum-attaining, not equational-completeness" correction is reinforced, and must now be paired with D13, where a complete rule set *does* yield an optimum |
| D2 exact synthesis | stands; unchallenged |
| D3 undecidability of phase ordering | stands; unchallenged, and QG-22's own `how_the_statement_fails` already cites it |
| D4 optimal function inlining (ASPLOS 2022) | **not re-retrieved in this run.** G6 forbids retrieval laundering, so D4 is `CANNOT_ASSESS` in QG-19's ledger. V1's record of it is unaffected and it remains a required citation from V1 |
| D5 global binary symplectic simplification | stands; unchallenged |

## 6. What V1 got wrong, stated plainly

V1's section "What survived the check" asserted that the intrinsic support number framing
"also found no parent". It has one: the smallest-support-size-of-an-optimal-solution
quantity, with a decade of tight bounds (D10). V1 ran ~10 queries across two backends and
read the absence of a hit as weak evidence of absence, which was the correct reading; V2
ran 52 queries across three mandatory families and found the parent by translating the
vocabulary rather than repeating it.

The general lesson for the programme, which is the only methodological content this
register is entitled to assert: **the query family that finds the parent is almost never
the one phrased in your own vocabulary.** C-A's own-vocabulary family (Q1–Q3) returned
nothing decisive. The donor-field family found a 1978 theorem that contains it.

## 7. What this register does not establish

- It is still not peer review. Every passage is search-tool text, not a document read.
- `novelty_authority: false` and `physical_quantum_advantage_claim: false` remain correct
  in every receipt and must not be flipped on the strength of this document, which moves
  only in the subtracting direction.
- No prior receipt is altered. Subsumptions are recorded here and in
  `QG19_HOSTILE_NOVELTY_RESULTS.json`; the original receipts stand as issued with the
  subsumption scored against them.
- Absence of a hit remains weak evidence of absence, and is recorded as a statement about
  the searches run — `QG19_QUERY_LOG.md` section 3 lists, verbatim, the searches that came
  back empty so that a reader can attack them.
