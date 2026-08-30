# Cover letter — Journal of Automated Reasoning

Dear Editors,

I submit **"Typed Falsification-Aware Scientific Authority as a Least Fixed
Point"** for consideration at the Journal of Automated Reasoning.

## What the paper contributes

The paper introduces a finite typed authority calculus for positive conjunctive
scientific rule systems. Claims carry licenses drawn from a finite universe;
rules transmit only the intersection of their premises' licenses, capped
explicitly; directly refuted claims are fixed at the empty label. The resulting
monotone operator has a least fixed point on the finite powerset lattice.

Six results are proven: finite convergence; rule-order independence; a typed
proof-tree theorem (a license reaches a claim exactly when some finite untainted
proof tree carries that license through every leaf seed and every rule cap);
unsupported cycles remain bottom while seeded cycles propagate; added
refutations can only remove licenses; and post-outcome repair cannot manufacture
prospective authority when the cap excludes it.

The motivating observation is that Boolean dependency graphs answer only whether
a claim remains derivable, not whether the surviving derivation licenses a
theorem, an exact finite statement, a prospective claim, or a post-outcome
repair. The cap mechanism internalises non-promotion rather than leaving it to
convention.

## What the paper deliberately does not claim

I would rather state the boundaries here than have a referee discover them.

- **Least fixed points, semiring and annotated provenance, minimal supports, and
  deletion robustness are explicitly donor-owned** and are not claimed as new.
  A hostile novelty subtraction is included in the submission, and it records
  that the typed-retraction result's generic minimality content is
  donor-adjacent and should not carry a standalone broad-novelty claim.
- **Arbitrary negation, probability, and inconsistency are open**, not solved.
- **No broad human-science usability claim is made.** There is no user study and
  no cross-institution deployment.
- The round-2 empirical section reports `precision = recall = 1.0` for the typed
  witness. **This is an analytic identity, not detector performance**, and the
  manuscript says so explicitly: once the typed method's decision is fixed equal
  to parent authorization, those values follow from the formal semantics. The
  paper separates this from the empirical statements rather than presenting it
  as a measurement.

## Empirical grounding

The formal work is instantiated against third-party material rather than
constructed examples: 46 hybrid obstruction cases occur among 1,962 X.509
trust-store merge tasks (~2.3%) derived from OpenSSL, over 268 digest-bound
files pinned to an exact upstream commit. Method-dependent costs are reported
per policy, and three corpus invariants that could have failed did not.

## Declarations

The author declares no competing interests. No funding was received for this
work. Generative AI tools were used for drafting and editing assistance; the
author is responsible for all scientific content.

Yours sincerely,

Sze Chun Yiu
sze-chun.yiu@fysik.su.se
