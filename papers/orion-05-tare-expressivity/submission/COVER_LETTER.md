# Cover letter — ORION-05

To the Editors, _Quantum_

**Manuscript:** Support-Two Exactness and Regime Geometry of Shared-Tag TARE
Compilation
**Article type:** Regular research article

Dear Editors,

We submit the manuscript above for consideration in _Quantum_.

Shared-Tag Tag-and-Restore compilation couples four design choices at once:
auxiliary anticommuting frames, target assignments, shared Tags, and Restore
factoring. Work in this area has tended to report a closed-form rule for the
optimum and then discover that the rule was fitted to the instances that
produced it. This paper separates the part of that design space that is settled
from the part that is not, and it does so in a way a referee can check.

The settled part is a structural theorem. We prove, with machine-checked
composition valid for every `n`, that auxiliary frame support of three or more
never strictly pays, so the unrestricted exact optimum always lies in the
support-at-most-two family. A theorem-backed static evaluator of that family
carries the result into practice: it has zero error against the unrestricted
dynamic-programming optimum on all 9,547 compared instances, with no
unrestricted call anywhere in its forecast path. A complete local audit over
688,041,472 configurations returns zero violations and explains why extra frame
support is expensive.

The unsettled part is reported as such, and we think it is the more useful half
of the paper. The audit prospectively declared that it did not cost the repair
of a shared Tag after frame anchors move. Exact search then found counterexamples
precisely in that declared gap, and it kept finding them: Tag-anchor splitting,
a central frame-for-Tag borrow, an out-of-support phantom borrow, and finally a
weight-two-Tag plus phantom-borrow hybrid witnessed 64 times. Each successive
closed form was frozen before evaluation and was allowed to fail; each failure
is retained in the manuscript rather than removed. The current all-`n`
finite-basis argument remains one pinned lemma short of closure, and we say so.

We want to be explicit about what this is not. Every statement is bounded to
the frozen grammar and its unit support-count objective. We claim no
full-circuit result, no hardware result, and no global block-encoding
optimality. The natural weight-one donor family is exactly optimal on the
recorded H4, equilibrium-N2, and prospectively staged Benzene matchings under
that frozen objective, and we do not extend that beyond the matchings we ran.

We believe _Quantum_ is the right home for this work because the contribution
is an exact, checkable structural result presented together with the
refutations that bound it, rather than a performance claim. The full
verification chain, including every refuting witness, is available as described
in the Data and Code Availability statement.

The manuscript is original, is not under consideration elsewhere, and all
computational claims resolve to committed, replayable artifacts.

Thank you for your consideration.

Sincerely,

*[Author names, affiliations, and corresponding-author contact to be supplied
at filing.]*
