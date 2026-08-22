# The retrieval ceiling, confirmed independently and stated once

Date: 2026-08-22
Branch: `claude/orion-harness-verification-b17qdj`
Status: **environmental limitation, adjudicator-confirmed.** Not a lane defect.

---

## What every donor search on this branch has had to disclose

QG-19, QG-24 and QG-25 each ran their donor searches, each obtained bearing
results, and each recorded `document_level_verification: false` on every record,
with the note that every quoted passage is **search-snippet text rather than text
read in its source**. QG-19 reported eleven refused document fetches; QG-25
reported `EGRESS_BLOCKED` on `arxiv.org` and `www.scottaaronson.com`.

Three lanes reporting the same obstacle is either a real ceiling or three lanes
making the same excuse. Until now nothing distinguished those.

## The independent check

The adjudicator re-tested with a **different tool** than any lane used — the
session's own `WebFetch` — on three unrelated domains, chosen so that a
domain-specific or publisher-specific block would show up as a partial result:

| target | why chosen | result |
|---|---|---|
| `https://arxiv.org/abs/1702.00877` | QG-25's permutation-DFA source | `EGRESS_BLOCKED` |
| `https://www.cs.cmu.edu/~cdm/pdf/22-minimization.pdf` | a university course PDF, QG-25's Myhill–Nerode source | `EGRESS_BLOCKED` |
| `https://en.wikipedia.org/wiki/Myhill–Nerode_theorem` | a general-reference page, no publisher gate | `EGRESS_BLOCKED` |

Each returned the same structured refusal:

> `{"error_type":"EGRESS_BLOCKED","domain":"...","message":"Access to ... is blocked by the network egress proxy."}`

The proxy reports itself enabled and healthy (`recentRelayFailures: []`), so this
is policy, not breakage.

## What this establishes, and what it does not

**Established.** Document-level retrieval is unavailable in this environment,
across preprint servers, university hosts and general reference alike. The
`document_level_verification: false` flag on every donor record in this programme
is a **hard environmental ceiling**, independently reproduced with a tool no lane
used. It is not three lanes declining to do the work.

**Also established, and it cuts the other way.** `WebSearch` works. Snippet-level
retrieval is available and was used; the adjudicator independently re-ran QG-25's
two load-bearing queries and both reproduced. So the ceiling is specifically
between *finding* a passage and *reading it in its source*.

**Not established.** That any quoted passage is wrong. Nothing here impugns a
citation; snippets from search results are ordinarily faithful. The point is that
**this programme cannot currently certify one at document level**, and a citation
that has not been read in its source is a weaker object than one that has.

## The consequence for what may be claimed

Every donor verdict in this programme rests on snippet text. Under the
`corroboration` module's own distinction, that is closer to `PROVENANCE_ONLY`
than to `FROM_PRIMITIVES_VERIFIED`: it establishes that a search returned a
passage, not that the source says it in context. Two specific exposures follow,
and both are already recorded rather than newly discovered:

* A `SUBSUMED` verdict removes novelty on the strength of a passage nobody here
  has read in place. That is the safe direction — it costs us claims — which is
  why the lanes were allowed to stand.
* A `NEAREST_MISS` or `NO_PRIOR_ART_FOUND` verdict is the unsafe direction, and
  neither is a novelty grant in this programme by construction
  (`donor_search.describe`), so the exposure is bounded by design rather than by
  luck.

QG-19's one figure that did not reproduce (Bravyi, "64.7 %") remains recorded as
confirmed-in-direction, unconfirmed-at-the-number, and this ceiling is why it
cannot be resolved here.

## What would lift it

Document fetch reaching at least one host that serves the primary sources. Until
then, no lane in this environment may record `document_level_verification: true`,
and any lane that does should be disbelieved on that field alone.
