# ORION25.CUSTODY_THRESHOLD_LAW.v1

## Question

For a `q`-of-`n` authorization/attestation rule distributed across genuinely independent governance domains, what threshold is simultaneously sufficient for compromise safety and availability liveness?

## Model

There are `n` independently governed custody domains. Authorization requires approvals from at least `q` distinct domains.

- At most `f` domains may be compromised and can approve an invalid object arbitrarily.
- At most `a` domains may be unavailable, while every available honest domain can approve a valid object.

The unit is a **governance domain**, not a key, process, replica or server. Multiple credentials controlled by one principal count as one domain for this theorem.

## Theorem 1 — compromise safety

Invalid authorization by compromised domains alone is impossible for every compromise set of size at most `f` **iff**

`q > f`.

### Proof

If `q > f`, at most `f` compromised approvals cannot form a quorum. If `q <= f`, choose any `q` compromised domains; they form a quorum and can authorize an invalid object. QED.

## Theorem 2 — availability liveness

Every valid object can still reach quorum after loss of any at most `a` domains **iff**

`q <= n - a`.

### Proof

After `a` unavailable domains, at least `n-a` domains remain. If `q <= n-a`, the available honest domains can form quorum. If `q > n-a`, an unavailable set of size `a` leaves too few possible approvals. QED.

## Theorem 3 — simultaneous safety and liveness

There exists a threshold satisfying both guarantees **iff**

`f + 1 <= n - a`,

or equivalently

`n >= f + a + 1`.

When feasible, the complete admissible interval is

`f + 1 <= q <= n - a`.

This interval is sharp by Theorems 1 and 2.

## Corollary 3.1 — minimum-domain design

For target compromise tolerance `f` and unavailability tolerance `a`, at least `f+a+1` independent governance domains are necessary and sufficient for some threshold rule to provide both guarantees. At the minimum `n=f+a+1`, the threshold is forced to `q=f+1=n-a`.

## Corollary 3.2 — governance quotient, not key count

Let many cryptographic keys or services be partitioned by common controlling principal. Collapse them to their governance quotient before applying the theorem.

A nominal `3-of-5` key threshold, for example, gives no one-domain compromise tolerance if three of the five keys share one control principal: compromising that principal may yield three signatures at once. Counting correlated credentials as independent domains therefore overstates safety.

This directly complements ORION-25's existing full-key-compromise adverse result: signatures can provide integrity only relative to a custody model. Threshold multiplicity does not create independent custody by itself.

## Corollary 3.3 — threshold cryptography cannot establish scientific validity

The theorem concerns authorization integrity and availability. Even a perfectly satisfied quorum does not prove the factual truth of an attested scientific proposition, protocol validity, evaluator competence, or scientific authority. Those require separate evidence channels.

## Successor design consequence

A real-system ORION-25 successor should freeze **before outcomes**:

1. the governance-domain partition and evidence that domains are independently controlled;
2. target `(f,a)`;
3. threshold `q` chosen inside the theorem's admissible interval;
4. invalid-object compromise attacks and valid-object availability failures;
5. a separate scientific-validity endpoint that cannot be passed merely by obtaining signatures.

Cosign/TUF/in-toto or other native systems may instantiate the mechanics, but the scientific unit is the independently governed trust domain.

## Claim boundary

Earned deductive claim:

> A `q`-of-`n` rule over independent custody domains is safe against `f` compromised domains iff `q>f`, live against `a` unavailable domains iff `q<=n-a`, and can satisfy both iff `n>=f+a+1`.

Not earned:

- that current ORION-25 keys represent independent institutions;
- a real-system trust-domain result;
- scientific truth from signatures;
- population or production reliability.

`scientific_authority_delta: NONE`