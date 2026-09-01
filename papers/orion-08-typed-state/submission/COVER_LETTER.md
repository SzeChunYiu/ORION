# Cover letter — ORION-08

To the Editors, Transactions on Machine Learning Research

**Manuscript:** Typed Epistemic State under Partial Knowledge: Six
Matched-Information Mechanism Studies

Dear Editors,

We submit the manuscript above for consideration in TMLR.

There is a recurring attribution problem in work on structured agent state. If
a typed system knows more than an untyped baseline, then a positive result
tells you about the extra information, not about the typing. Most comparisons
in this area do not control for it.

This paper is built around that control. Within each of six study families,
every non-oracle arm receives the same serialized visible state and differs only
in how it interprets or acts on that state. The strongest available comparison
gets first right of refusal, and each world contains a hostile regime designed
to expose the specific shortcut the proposed typing is meant to prevent. Worlds
are exact and synthetic, seeds are frozen, and decision paths are deterministic.

The headline result is that type-conditioned priors carry real weight when they
are the only difference: across 300 paired episodes the typed arm reaches 3.291
mean utility against 2.180 for the uniform-prior ablation, recovering about 71%
of the 4.612 oracle. The hostile arm behaves as the world requires, with blind
optimistic commitment driven to -13.619 and succeeding in only 19% of episodes.

We would draw reviewers' attention to two results that go the other way, because
they are reported at the same prominence in the manuscript and we think they
are the more informative half. In the costly-verification family, an ideal
allocator given the same typed facts matches our policy *exactly*, at solve rate
0.9866; the allocation-policy residual is therefore closed, not open. In the
model-selection family, the donor and the candidate tie at 0.9948 on the
original world, and only the narrower misspecified world separates them at
0.9844 against 0.9531. Neither of these is presented as a partial win.

The boundary is exact-synthetic mechanism isolation, and every terminal in the
evidence says so. These worlds are constructed. Nothing here measures a deployed
system, and we make no deployment claim. What the paper offers is a set of
deterministic worlds in which epistemic-state type and scope can be compared
without confounding state content with state interpretation, plus the honest
record of where that comparison found nothing.

We believe TMLR is the right venue precisely because the contribution should be
judged on whether the evidence supports the claim rather than on how impressive
the win is.

The manuscript is original and is not under consideration elsewhere.

Thank you for your consideration.

Sincerely,

*[Author names, affiliations, and corresponding-author contact to be supplied
at filing.]*
