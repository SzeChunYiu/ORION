# Does the papers' own code express the amplification scenario?

**Status:** `ASYMMETRIC_GAP_CONFIRMED__ONE_SIDE_COMPLICATED`
**Scientific authority delta:** `NONE`.

`AMPLIFICATION_CHECK_V1.json` states plainly that it checks *my* formalisation, not the
papers' implementations. This measures the papers' code directly, so that scope caveat
can be replaced by a fact.

## ORION-18 cannot express repair, and this is the direction that matters

Across all **12** ORION-18 Python files:

| | files |
|---|---|
| mentioning `repair` / `revalidat` / `reopen` | **1** |
| mentioning `obligation` / `authoriz` (control) | **11** |

The control fires strongly — up to 52 occurrences in a single file — so the measurement
discriminates. And the one repair-shaped hit is not a mechanism: it is the string
`"reopen_plan"` appearing in `check_benchmark_contracts_v2.py` as the *name of a hard
obligation*. ORION-18 obligates the existence of a reopen plan; it does not model
reopening.

**So the paper's own checker could not represent the counterexample.** Not because the
scenario is wrong, but because the vocabulary is absent. That is the honest closure of the
"my model versus their implementation" gap: they do not disagree — one of them cannot state
the question.

This is the direction that matters, because the attack is *repair promotes authority*, and
ORION-18 is the side that would have to notice.

## ORION-16's side is more complicated than its formal core suggested

Across all **20** ORION-16 Python files:

| | files |
|---|---|
| mentioning `authoriz` / `root_class` / `permission` | **10** |
| mentioning `repair` / `revalidat` / `certif` (control) | **17** |

Half its code touches authority vocabulary, while its `FORMAL_CORE_V2_1` mentions authority
only four times. **This partly complicates the "formally disjoint" claim** made in
`A6_COMPOSITION_ROUTE_V1.md`: the disjointness is real at the level of the formal cores,
but ORION-16's implementation already reaches across the seam that its theory does not.

I have **not** checked whether those mentions model authority or merely use the word, and I
am not going to assert either reading without looking. Two possibilities, with different
consequences:

- If the code genuinely models authority, the composition is **more tractable** than the
  formal cores suggest, because one side already has the vocabulary and the theory simply
  has not caught up.
- If the mentions are incidental, the disjointness claim stands unchanged.

Either way the ORION-18 side is unaffected, and the ORION-18 side is where the attack has
to be noticed.

## What this changes

The counterexample's status improves. It is no longer only *argued from definitions and
checked against my model*: the paper that would have to detect it demonstrably has no
vocabulary in which to do so, measured over its whole implementation with a control.

What it does not change: the counterexample still needs encoding against a repair-aware
authority model that the programme does not yet have. Building that model **is** the
composition work, and it is the same work either way.

## Open item, now settled — and it favours the papers

ORION-16's code **genuinely models permission and authority**. It is not incidental
vocabulary:

```
check_real_transition_audit_independent_v1.py
    deny = {k for k in ("generic_permission", "commit_authority") if not c[k]}
    if "generic_permission" in deny: return "DENIED"

run_real_transition_audit_v1.py
    if not c["generic_permission"]: return "DENIED"

check_theory_closure_v2.py
    if not guard_authorized:
        raise PermissionError("conditional guard is not authorized")

check_assumption_regressions_v2.py
    def self_authorization_countermodel(candidate_controls_policy, candidate_controls_evidence)
```

So ORION-16's implementation already carries `generic_permission`, `commit_authority`,
`DENIED` terminals, an `explicit_authorized_discharge` flag and a self-authorization
countermodel.

**`A6_COMPOSITION_ROUTE_V1.md`'s disjointness framing therefore needs amending, and in the
direction that helps.** The formal cores are disjoint — that measurement stands, 13-vs-4
and 29-vs-0. The *implementations* are not. ORION-16's code has been reaching across the
seam that its theory does not describe.

Three consequences:

1. **The composition is more tractable than the formal cores suggested.** One side already
   has permission vocabulary and a commit-authority notion; the theory simply has not
   caught up to the code.
2. **The amplification attack may be encodable against ORION-16's real transition audit**
   rather than only against my own model, because `generic_permission` and
   `commit_authority` are exactly the quantities the attack promotes. That is the next
   concrete step and it is now clearly worth taking.
3. **The asymmetry is the real finding.** ORION-18 models root classes and obligations but
   cannot express repair. ORION-16 models repair *and* permission but has no root classes.
   Each has two of the three ingredients the attack needs, and neither has all three.

---

## Closed, 2026-09-01

Consequence 2 above — "the amplification attack may be encodable against ORION-16's real
transition audit" — was taken up and is now done. See
`../a6-amplification-real-classifier-v1/FINDING_V1.md`.

The attack was run against the shipped `classify()`, imported by path and sha-pinned rather
than copied, so the objection this document raised against the earlier self-authored model
no longer applies. Four amplifying edges exist, none from the outer unknown layer, and five
are realized inside ORION-16's own case set. A one-coordinate guard closes them under a
metric controlled by the requirement that it still detect the attack unrepaired.

Two predictions failed along the way and both receipts are kept: that no real case pair
would realize the attack, and that the repair's first metric would report zero.
