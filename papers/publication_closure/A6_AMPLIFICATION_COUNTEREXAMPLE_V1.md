# A6 composed system — candidate counterexample: repair is an authority-amplification channel

**Status:** `CANDIDATE_COUNTEREXAMPLE__ARGUED_FROM_DEFINITIONS__NOT_MACHINE_CHECKED`
**Scientific authority delta:** `NONE`. Nothing is claimed proved. This is an attack on a
claim neither paper currently makes, and it should be attacked in turn.

`A6_COMPOSITION_ROUTE_V1.md` proposed attempting the counterexample before the proof,
because two of three earlier candidates fell. Here is the counterexample, and it appears to
work.

## The target

> Selective revalidation is not an authority-amplification channel: repair cannot promote
> `CANNOT_CHECK` to `AUTHORIZED` without new protected evidence.

## The three facts it is built from

All are in the papers as written.

1. **Obligations are domain-scoped, not derivation-scoped.** ORION-18 writes `O_h` and
   Definition 21 gives `OBLIGATION_FREE` as *"a domain-level root for a domain with
   `O_h = ∅`"*. So which obligations apply is a property of the domain a claim is grounded
   in.
2. **Protection is effect-relative, not root-intrinsic.** Proposition 15's proof is
   explicit: *"the same root may be protected relative to `e` and unprotected relative to
   `e'`."* Root class is evaluated against a candidate effect, not fixed once.
3. **Repair produces new certificates.** ORION-16's certificate-aware repair re-certifies
   affected claims after a change. Each re-certification is a new derivation with a new
   certificate.

## The counterexample

Let claim `q` be grounded in domain `h` with a live obligation `o ∈ O_h` whose required
judgment type names evidence that is unavailable. By Definition 10 clause 1 and
Proposition 12's construction, the effect `e` committing `q` has

```
Perm(e) = CANNOT_CHECK
```

Now change some `x` on which `q` depends. `q ∈ Aff_D(E, x)`, so ORION-16's repair reopens
and re-certifies it. Suppose the re-certification grounds `q` in a domain `h'` with
`O_{h'} = ∅` — an `OBLIGATION_FREE` root, which Definition 21 explicitly admits and
Proposition 16 says covers *"the majority of `DELEGATED_GRANT` and `OBLIGATION_FREE`
cases"*.

Every obligation in `O_{h'}` is now vacuously discharged, because there are none. If no
blocker is `UNDETERMINED` for the new effect `e'`, Definition 10 clause 1 is satisfied and

```
Perm(e') = AUTHORIZED
```

**The unavailable evidence is still unavailable.** Nothing was supplied. The promotion came
from *re-grounding*, not from discharging.

## Why neither paper prevents this

ORION-16 has **no authority vocabulary at all** — zero mentions of authority or
authorization in its formal core — so it places no constraint on the root class or domain
of a repair-generated certificate. It cannot: it does not know root classes exist.

ORION-18 has **no repair vocabulary at all** — zero mentions of repair, revalidation or
reopening — so its non-amplification reasoning never considers a mechanism that manufactures
new candidate effects. Proposition 14 governs *revocation* of premises, which is demotion.
It says nothing about *replacement* of premises, which is what repair does.

The gap sits exactly on the seam. Each paper is sound about its own half.

## Why this is an attack rather than a feature

One could argue the re-grounded certificate is legitimate: if `q` genuinely follows from an
obligation-free domain, the obligation was never needed. That reading fails for a specific
reason.

**An adversary who can induce the change controls the promotion.** The attacker does not
need to satisfy `o`, forge evidence, or touch the deciding policy. They need only perturb
some `x` upstream of `q` in a way that causes repair to re-derive `q` through an
obligation-free route. Repair is triggered by change, and change is the cheapest thing to
supply.

This is precisely the fail-open pattern ORION-18 names in Proposition 14's discussion —
authority appearing without the evidence that was supposed to license it — arriving through
a door that paper does not watch.

## What would refute this

Stated plainly, so it can be killed:

1. **A domain-preservation constraint on repair.** If ORION-16's re-certification is
   required to ground `q` in the same domain `h`, then `O_h` is unchanged and the attack
   fails. I find no such constraint stated, but it may be intended and unwritten.
2. **A monotonicity requirement on root classes.** If a repair-generated certificate may
   not use a root class weaker than the original derivation's, the attack fails.
   Definition 21 gives no ordering over the four classes, so "weaker" is currently undefined
   — which is itself a gap worth closing.
3. **A freshness or binding clause that forbids re-grounding.** Definition 14's transport
   rules govern certificates across epochs; if they also govern derivation paths within an
   epoch, they may already forbid this.

If any of the three holds, this counterexample dies and the composed claim survives — which
would be the better outcome for the papers and is worth checking first.

## Why this is worth a top-tier attempt either way

If the counterexample stands, the composed system has a named vulnerability that **neither
donor field would have found**: truth maintenance never asks by what authority a
re-derivation licenses anything, and deontic logic never models a mechanism that
manufactures candidate effects. The paper then reports an attack and its repair.

If one of the three refutations holds, the composed claim is a theorem and the paper reports
that instead.

Both are stronger than the current position, in which the question is not asked because the
two papers do not share a vocabulary in which to ask it.

## Honesty

This is argued from the definitions as written, not machine-checked, and I constructed both
the claim and the attack on it. ORION-18's hostile-mutation machinery is the right tool to
settle it, and the counterexample should be encoded as a mutation case before any of this is
written into a manuscript.
