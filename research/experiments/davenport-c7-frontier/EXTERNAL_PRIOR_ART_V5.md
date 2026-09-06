# External prior-art search — V5 (partial: search yes, full text no)

Status: **partially cleared.** A previous statement in this lane — that the external prior-art gate cannot be attempted from this host — was **wrong**, and is corrected here.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Correction: what this host can and cannot reach

Earlier records and a cross-lane comment stated the host has no external network access, on the strength of `curl https://arxiv.org` returning a 403 policy denial at the proxy gateway. That test was real but the conclusion drawn from it was too broad.

| capability | status |
|---|---|
| `curl` / direct HTTPS to arxiv.org | **blocked** (403 CONNECT denial at the proxy) |
| `WebFetch` (fetch and read a page) | **blocked for every domain tried**: `arxiv.org`, `www.combinatorics.org`, `cfc.nankai.edu.cn` — all `EGRESS_BLOCKED` |
| `WebSearch` | **works** |

So a literature *search* is possible; reading the primary texts is not. This changes the gate from "cannot be attempted" to "can be searched, cannot be verified". The distinction matters and the earlier over-claim is withdrawn.

## 2. References identified

These replace placeholders in the manuscript. **Identified by search only — none has been read**, so the exact statements this programme attributes to them remain unverified against the primary text.

| # | Reference | Bearing on this work |
|---|---|---|
| 1 | J. E. Olson, *A combinatorial problem on finite abelian groups*, J. Number Theory (1969) | `D(C_p^r) = r(p−1)+1`; the only external input to our theorems |
| 2 | M. Freeze, W. A. Schmid, *Remarks on a generalization of the Davenport constant*, arXiv:0905.4248 | establishes `D_k(G) = D_0(G) + k·exp(G)` for large `k`; source of the recurrence and lower-bound line used in this programme |
| 3 | Y. Fan, W. Gao, G. Wang, Q. Zhong, J. Zhuang, *On short zero-sum subsequences of zero-sum sequences*, Electron. J. Combin. **19**(3) (2012) #P31; arXiv:1108.2866 | the "Fan et al." `η`/short-zero-sum results cited in this programme |
| 4 | B. Girard, W. A. Schmid, *Direct zero-sum problems for certain groups of rank three*, J. Number Theory **197** (2019) 297–316; arXiv:1806.07636 | **the nearest prior work**: determines `η` and the multiwise Davenport constants for rank-three groups — see §3 |
| 5 | B. Girard, W. A. Schmid, *Inverse zero-sum problems for certain groups of rank three*, Acta Math. Hungar. (2019); arXiv:1809.03178 | companion inverse results |

Still unpinned: the "Zhao Lemma 4.4" and "Zhang `s_{≤12}(C_7^3) = 26`" donors quoted in earlier records. Neither is needed any more — `SHORT_ATOM_BOUND_UNIFORM_V4.md` discharged both — so they are now historical rather than load-bearing.

## 3. The nearest prior work does not collide

Girard–Schmid (ref. 4) is the closest match found: rank three, multiwise Davenport constants, and recent. It determines those constants for groups of the form

`G ≃ C_2 ⊕ C_{n_2} ⊕ C_{n_3}` with `2 | n_2 | n_3`,

i.e. rank-three groups of **even** exponent containing a `C_2` factor. `C_p^3` for odd prime `p` is not of that form, so the overlap is empty. Two further search findings point the same way:

- multiwise Davenport constants are reported as studied for elementary `p`-groups of **rank at most two**, and for `C_3^3` — leaving `C_p^3`, `p ≥ 5` uncovered;
- the frequently repeated remark that "exact values are known for rank at most three" is about elementary **2**-groups `C_2^r`, not about odd `p`.

No search result states `D_3(C_7^3) = 36`, or `D_2(C_p^3) = (9p−5)/2` for general `p`, or a short-atom bound of the form `(3p−1)/2`.

## 4. What this does and does not establish

**Does:** the five references above are now identified rather than placeholders; the nearest prior work is located and shown to be on a disjoint family of groups; nothing found asserts our results.

**Does not:** absence of a search hit is weak evidence, especially for a result that might appear inside a paper on a different headline topic. And because no primary text could be read, every attribution in §2 is unverified — in particular the exact form of Freeze–Schmid's recurrence, which earlier records lean on.

**Therefore the prior-art gate is reduced, not cleared.** A person with library access must confirm §2 and §3 before submission. That is a smaller and better-specified task than before: read five identified papers and check two questions — is `D_3(C_7^3)` known, and is a short-atom bound near `D/2` for `C_p^3` known.

## Claim ceiling

Search-only pass. No priority claim follows. The negative findings in §3 are bounded by what a general-purpose web search surfaces and by the searcher's queries, both of which are recorded here so the pass can be repeated and criticised.

---

## V6 addendum: a web-search pass on the witness criterion (2026-09-05)

`WebSearch` works from this host (`WebFetch` does not), so this is a snippet-level pass, not a
literature read. It **narrows** the open novelty question; it does not close it.

**Established, and it positions the packet favourably.**

- The rank-two value `D_k(C_m ⊕ C_n) = m + kn − 1` is standard, and the literature states
  explicitly that it **fails for elementary 2- and 3-groups of rank ≥ 3** — exactly the regime
  this packet works in. It also records that computing `D_k(G)` is "quite more complicated than
  for `D(G)`, in particular for (elementary) `p`-groups". The hard cases here are
  acknowledged-hard, not overlooked.
- For elementary `p`-groups, `D_k` is linked to **linear-code parameters and cap sets** in
  projective spaces. That is a bridge this packet hit blind: a length-17 sequence over `C_3^5`
  with no zero-sum of length `≤ 6` has in particular no three terms summing to zero, i.e. is a
  cap set in `AG(5,3)`. Worth citing rather than rediscovering.

**One false alarm cleared.** "The Davenport constant of a box" sounded like a direct collision,
since the criterion has `b` ranging over a box `[0,m]`. It is a different notion — there the
*ambient group* is a box. No overlap.

**Not settled.** Whether Theorem W is known. Nothing in the snippets states it, but that is weak
evidence either way. `D_2(C_p^3) = (9p−5)/2` also did not surface, though the packet attributes it
to a Zhao preprint this host cannot fetch.

**Freeze–Schmid, pinned (this sharpens the positioning materially).**
*Remarks on a generalization of the Davenport constant*, Discrete Math. 310 (2010) 3373–3389
([arXiv:0905.4248](https://arxiv.org/pdf/0905.4248)) — already a donor statement for this packet:

- It determines `D_k(G)` exactly for elementary **2**-groups of **rank four and five**, noting
  rank `≤ 3` was already known. So the detailed higher-rank work in the literature is at `p = 2`;
  **odd `p` at rank `≥ 4` — `C_3^5`, `C_3^6`, `C_5^4`, `C_7^4`, `C_5^5` — is where this packet's
  improved bounds sit.** That is a real gap, not an oversight, and it is the right way to position
  those five results.
- It proves `(D_k(G))_{k∈ℕ}` is **eventually an arithmetic progression with difference `exp(G)`**.
  That is exactly the `M*_k = M*_2 + (k−2)p` relation recorded in `WITNESS_CRITERION_V6.md` §9a.
  §9a has been corrected to attribute it: the relation is that theorem viewed from inside the
  construction class, not a new observation. Presenting it as new would have been an error.

**The gate is now one target, not five.**

> `arXiv:2410.22245` — *Disjoint zero-sum subsets in Abelian groups and its application — survey*
> (2024). Squarely on this subject and recent enough to cite the current state. Read it, plus
> whichever reference it gives for the rank-three `D_2(C_p^3)` value.

That is an hour with library access, and it decides whether Theorem W is a contribution or a
restatement. Everything else in the packet stands on its own regardless of the answer.

Priority remains CANNOT_CHECK from this host.

---

## V7 addendum: the gate paper, identified — and replaced (2026-09-05)

The V6 addendum reduced the prior-art gate to a single target and called it "an hour with library
access". That hour was spent, as far as this host permits. The result is not what was expected:
**the gate was pointed at the wrong paper.** A different and much sharper target has taken its
place.

### What this host can and cannot do

Recorded so the pass is reproducible and its ceiling is explicit. Direct fetch of scholarly hosts
is refused by this session's egress policy, not by the remote services:

| host | result |
|---|---|
| `arxiv.org` | CONNECT rejected, gateway 403 (policy denial, logged in the proxy's `recentRelayFailures`) |
| `export.arxiv.org` | tunnel refused |
| `www.sciencedirect.com` | tunnel refused |
| `link.springer.com` | tunnel refused |
| `www.semanticscholar.org` | tunnel refused |

Per the proxy's own instructions a policy denial is reported, not routed around. So this remains a
**snippet-level pass**: search results and search-engine summaries, never a primary text. Nothing
below is a reading of a paper.

### The gate paper is not about this invariant

`arXiv:2410.22245` is **Sylwia Cichacz, *Disjoint zero-sum subsets in Abelian groups and its
application — survey*** (math.CO, October 2024).

The identification is solid: a search result paired that exact title with both
`arxiv.org/pdf/2410.22245` and `arxiv.org/html/2410.22245`. The subject description that follows is
snippet-level and weaker.

Its subject is the **zero-sum partition** property — splitting a group's *elements* (each used once)
into subsets that each sum to zero — applied to the Friedlander–Gordon–Tannenbaum conjecture on
orthomorphisms, and onward to graph labelling. That is a *different invariant* from `D_k(G)`, which
is an extremal function over **sequences** (repetition allowed) asking for `k` disjoint zero-sum
**subsequences**. The two share the phrase "disjoint zero-sum" and little else: no extremal length
function, no elementary `p`-group rank asymptotics, no packing number.

So the V6 gate — "read this, and it decides whether Theorem W is a contribution or a restatement" —
**was mis-aimed.** Theorem W cannot be in that survey, because that survey is not about `D_k`. The
gate as posed is cleared, and clearing it establishes much less than V6 hoped it would.

This is worth stating plainly as a method failure: V6 narrowed five candidates to one on the
strength of a title, and the title matched on the wrong sense of "disjoint zero-sum". Narrowing a
literature search by keyword resemblance, without a single primary text, produced a confident
pointer to an irrelevant paper.

### The gate that should have been there

The same searches surfaced a target that *is* on this invariant, in this regime, using this
packet's own bridge:

> **L. E. Marchan, O. Ordaz, I. Santos, W. A. Schmid, *Multi-wise and constrained fully weighted
> Davenport constants and interactions with coding theory*, [arXiv:1407.1966](https://arxiv.org/abs/1407.1966),
> J. Combin. Theory Ser. A (2015).**

Why this is the real risk, point by point:

- Their **`m`-wise Davenport constant with weights `W`** is "the smallest `n` such that each
  sequence over `G` of length `n` has at least `m` disjoint zero-subsums with weights `W`". At the
  trivial weight set `W = {1}` that is **exactly `D_m(G)`** — this packet's invariant, not an
  adjacent one.
- They work **for elementary `p`-groups specifically**.
- They link the constants to **linear-code parameters and cap sets in projective spaces** — the
  identical bridge recorded in the V6 addendum, where a length-17 sequence over `C_3^5` with no
  short zero-sum is a cap set in `AG(5,3)`.
- The abstract summary says they "obtain **various explicit results on the values of these
  constants**" for elementary `p`-groups. Explicit values, in the same regime, by a route this
  packet also travels.

That is the collision surface for the five improved `D_2` lower bounds (`C_3^5 ≥ 17`, `C_3^6 ≥ 20`,
`C_5^4 ≥ 26`, `C_7^4 ≥ 37`, `C_5^5 ≥ 31`) and potentially for `D_2(C_3^5) = 17` itself. Schmid is a
co-author here and of Freeze–Schmid, so this is the same line of work that owns the rank-4/5
elementary **2**-group values; the natural question is how far the coding-theoretic route already
carried odd `p`.

**Unchanged by any of this:** Theorem W is a *criterion* (an exact biconditional characterising
`z(S) ≤ 1`, and `W_t` for all `t`), not a value. A paper computing values by cap-set bounds could
overlap the five bounds without containing the criterion. But that has to be checked, not assumed —
which is precisely the mistake V6 made.

### Gate, restated

| # | target | question it decides |
|---|---|---|
| 1 | `arXiv:1407.1966` (Marchan–Ordaz–Santos–Schmid) | Are any of the five improved `D_2` bounds, or `D_2(C_3^5)`, already known via linear codes / cap sets? |
| 2 | whatever §1 gives for `D_k(C_p^r)` at odd `p`, rank `≥ 4` | Is the criterion, or an equivalent, already in that chain? |
| 3 | the Zhao preprint for `D_2(C_p^3) = (9p−5)/2` | Still unfetchable; still an unverified donor statement. |

`arXiv:2410.22245` is **struck from the gate** — cite it if at all as adjacent background, never as
the novelty test.

Priority remains **CANNOT_CHECK** from this host, and the reason is now recorded as a policy denial
with per-host evidence rather than a general statement that fetching does not work.
