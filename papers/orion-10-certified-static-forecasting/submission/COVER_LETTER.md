# Cover letter — ORION-10

To the Editors, _Quantum_

**Manuscript:** Theorem-Backed Static Cost Forecasting with Refutable
Explanations for Quantum Compilation
**Article type:** Regular research article

Dear Editors,

We submit the manuscript above for consideration in _Quantum_.

A static cost forecast for a compiler is usually presented as one thing: a
formula that predicts the optimum, validated by a table showing it agrees with
an exact search. This paper argues that this is at least five things, and that
conflating them is how forecasting work goes wrong.

We separate the exact cost theorem, the implementation check of an evaluator
against the unrestricted dynamic program, the human-readable regime model that
explains *why* the cost is what it is, the prospective prediction evidence, and
the row-level verification authority. Each layer can fail independently. The
paper's evidence is that they do.

The concrete demonstration is a refutation of our own explanation. A static
evaluator, backed by the cost theorem, achieves zero error against the
unrestricted optimum on 9,547 compared instances with no unrestricted call in
its forecast path. A repaired regime explanation layered on top of it is then
defeated by hostile search, with 64 exact witnesses across 10,481 compared
instances. The cost certificate survives this untouched, because it never
depended on the explanation. That is precisely the point: without the layered
contract, a reader would have been entitled to conclude that the refutation
falsified the forecast, and it does not.

We have deliberately kept the claim hierarchy explicit and ordered: theorem,
then finite benchmark, then unresolved explanation. The explanation layer is
still open, and we report it as open rather than presenting a repaired version
whose refutation is recorded only in a supplement.

We would ask reviewers to weigh the Reproducibility section as part of the
argument. It requires re-establishing the original forecast failure before
verifying the evaluator, because a reproduction that begins after the failure
cannot see what the layering is for. A final zero-error table would be true and
would misrepresent the work.

All statements are bounded to the frozen grammar and objective, and no physical
quantum-advantage claim is made.

We note for the editors that two related manuscripts from the same research
programme are being routed to _Quantum_ in the same period; they are distinct
contributions, and we are happy to stagger them or clarify the relationship.

The manuscript is original and is not under consideration elsewhere.

Thank you for your consideration.

Sincerely,

*[Author names, affiliations, and corresponding-author contact to be supplied
at filing.]*
