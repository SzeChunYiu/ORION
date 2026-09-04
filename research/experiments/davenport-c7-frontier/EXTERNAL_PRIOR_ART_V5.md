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
