# Digest-representation boundary mix-up blocked the P1-U R6 primary

**Observed:** 2026-08-21, auditing why issue #649 (P1-U) reports `CANNOT_CHECK`.

## Failure

The P1-U R6 native-runtime trial executed its frozen primary and then rejected
**every** scored native row. The rejection was recorded as campaign evidence
(PR #730, "preserve exact engineering-failure evidence") and read, from outside,
as one more `CANNOT_CHECK` in a sequence of four.

It was not a scientific outcome. `_native_row_valid` in
`research/claim_expansion/p1/gpt_r6_native_primary.py` validated one row
containing two different SHA-256 **representations** with a single raw-hex
predicate:

- `runtime.pre_state_hash` / `post_state_hash` / `final_state_digest` come from
  the research harness as bare 64-character hex;
- `responsibility_digest`, `interface_digest`, `revision_gate_digest`,
  `mechanic_digests` and `assessment_digests` come from
  `orion.transfer.v2.canonical.content_digest`, which returns
  `"sha256:" + hexdigest`.

`_is_hex64` is length-64-and-hex. A `sha256:`-prefixed value is 71 characters, so
the predicate was unsatisfiable for every assessment digest the adapter can
produce. The arm could not have passed for any input.

Reproduced in isolation from `origin/codex/p1-r6-current-main-fix-20260821`
(`git archive` into a scratch tree, private venv, per `AGENTS.md`):

```text
canonical transfer-v2 digest : sha256:a55d6a88…48e13
harness raw state hash       : aaaa…aaaa

row_valid, digests AS THE ADAPTER PRODUCES THEM : False
row_valid, same digests with prefix stripped    : True
```

## Failure class

`DIGEST_REPRESENTATION_BOUNDARY_MIXUP`

A sibling of `EXECUTION_IDENTITY_BOUNDARY_MIXUP`
(`research/failures/2026-08-git-object-ref-identity-mixup/`): distinct object
identities with different admissible transitions were treated as one type at a
boundary. There, tree/commit/ref; here, two encodings of the same hash.

Two properties made it expensive rather than trivial:

1. **The repository has no vocabulary separating the representations.** There are
   22 independently written raw-hex-64 predicates under `src/orion/` (in
   `providers/`, `self_orion/`, `programme/`, `benchmarks/`) and 9 modules
   asserting the `sha256:` prefix, with nothing naming the two apart. Any code
   joining a harness value to a transfer-v2 value meets this. `identity.py`
   already records a neighbouring defect in its own docstring: three
   `canonical_bytes` definitions that do not agree.
2. **The boundary error was reported as a negative result.** The predicate
   returned `False`, which is exactly what "this row failed validation" looks
   like. A crossed type boundary and a failed scientific check were
   indistinguishable in the output, so the campaign preserved an engineering
   defect as evidence.

## Correct response

1. Diagnose before recursing. The R6 corrective step (#723) correctly identified
   that R2-R5 never instantiated `OrionRuntime`, and re-ran natively; the *next*
   failure was one layer down and needed its own diagnosis rather than another
   campaign round.
2. Fix the boundary, not the caller. `gpt_r6_native_primary_schema_fix.py`
   (PR #732) monkey-patches `primary._native_row_valid`, deep-copies each row and
   strips prefixes. That unblocks this run and leaves the trap armed: the next
   module joining the two representations meets it again.
3. Give the two representations names and one conversion, and make a crossed
   boundary **raise** rather than return `False` — see
   `src/orion/core/digests.py`.
4. Record the responsibility class on the blocked terminal so the next reader can
   see that #649 is blocked on implementation, not on evidence.

## General lesson candidate

**A validator that answers `False` at a type boundary manufactures negative
results.** Where a predicate can fail either because the value is wrong *or*
because it is the right value in the wrong representation, those two outcomes
must be distinguishable in the return, or the second will be counted as the
first. The cost is asymmetric: a loud refusal costs one debugging session, a
silent `False` costs a campaign round and enters the record as evidence.

There is a sharper, self-referential form here, and it is the reason this record
exists rather than a one-line patch note.

P1's scientific claim is precisely that a system should **discriminate which
responsibility class is load-bearing before escalating** — `SEARCH_OR_EVIDENCE`
vs `REPRESENTATION_OR_INTERFACE` vs `IMPLEMENTATION_OR_ENVIRONMENT`, the taxonomy
frozen in `development/p1-u-gpt-r2-naturalistic/DEVELOPMENT_PACKET.md`. The P1
campaign was itself blocked by an `IMPLEMENTATION_OR_ENVIRONMENT` failure that
presented as a scientific `CANNOT_CHECK`, and the misattribution survived four
campaign rounds of human attention.

This is P1's own thesis holding against P1. It is not evidence *for* P1 — a
system's authors misattributing a responsibility class says nothing about whether
the system would — but it is a genuine naturalistic instance of the confusion
P1 exists to prevent, generated inside this repository, and #663/#649 both ask
for exactly such cases. Its status is a **candidate case**, not a scored one:
promoting it into P1's corpus after the fact would be the post-hoc freeze that
`HC-SUP-POST-HOC-FREEZE` refuses.
