# Correction to the refinement strictness criterion

**Date:** 2026-09-01
**Disposition:** `EARLIER_UNDERSPECIFIED_WORDING_WITHDRAWN__CORRECT_CRITERION_PROVED_AND_CHECKED`

The historical theory packet stated that a refinement decreases risk strictly
"exactly when it splits a positive-mass coarse fibre whose worlds share no
optimal action." That wording is too broad. A refinement can split an impure
coarse fibre in a way that leaves every refined subfibre with the same optimal
aggregate action, in which case risk does not decrease.

For a finite decision problem, let a coarse fibre `F` be partitioned by the
refined binding into positive-mass subfibres `G`. Define

```text
L_G(a) = sum_{x in G} p(x) loss(x,a)
O_G    = argmin_a L_G(a).
```

The refined risk is strictly smaller on `F` exactly when

```text
intersection over refined subfibres G within F of O_G is empty.
```

If the intersection is nonempty, one action minimizes every subfibre and hence
also the coarse sum, so refinement adds no value. If it is empty, no coarse
action attains all subfibre minima simultaneously, so the minimum of the sum is
strictly larger than the sum of the minima.

This is the criterion implemented by the OpenML-CC18 and Defects4J runners when
they compare optimal refined-subfibre actions inside each coarse fibre. Their
same-distribution agreement is therefore an algebraic instantiation and an
implementation check, not independent empirical confirmation of a theorem.
Held-out behavior remains a separate empirical question and is mixed.

The correction narrows the theory wording and the interpretation of the
historical experiment terminals. It deletes no result file, amendment, adverse
outcome or `CANNOT_CHECK` terminal.
