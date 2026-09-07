# ORION-26 — The pointed polynomial method for generalized Davenport constants of `C_p^3`

New paper opened on lane `claude/orion-research-frontier-3ck9yt`.

- `MANUSCRIPT_V1.md` — the draft.
- `CLAIM_LEDGER.md` — per-claim evidence and status (proved / verified-range / external / open).
- Evidence packet: `research/experiments/davenport-c7-frontier/`.

**Headline.** `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5` and `D_3(C_7^3) = 36`, with Olson's theorem as the only external input; both obtained with a *pointed* form of the Chevalley–Warning counting identity that is strictly stronger than the symmetric form on two-sided length windows.

**Not yet submittable.** Two gates remain and neither can be cleared from the authoring host.

1. **Prior art — narrowed to five references.** **arXiv:1407.1966**
   (Marchan–Ordaz–Santos–Schmid, JCTA 2015) was the highest-risk candidate and has now been
   **read in full**. It does *not* overlap: its elementary-`p`-group results are for the **fully
   weighted** constant `D_{A,m}`, `A = {1,…,exp(G)−1}`, which equals the classical `D_m` only at
   `p = 2`; its explicit values cover rank at most two plus `C_3^3`; and its cap-set link is to
   the weighted problem. Two earlier readings of the prior-art position — both written from
   search snippets, both wrong — are logged in `CLAIM_LEDGER.md`. References 1–5 remain unread:
   every scholarly host is refused by this host's egress policy.
2. **Independent mathematical review** of the `D_3(C_7^3)` argument. The step-5 enumeration is
   double-implemented but by the same author, which is not independent replication.

**Relation to ORION-04.** ORION-04 is the conditional `C_5^3` analysis settling `D_4(C_5^3)` to one bit under two hypotheses. This paper is disjoint in content: `D_2` for all primes and `D_3` at `p = 7`, unconditional.

skills-applied: academic-writing + nature-shared/core/atomic-claim-verification, from the
upstream **`SzeChunYiu/academic-paper-skills`** repository at rev `756d938`, cloned and read as
written protocol (the skills are not installed in this session; axes: paper_type=**theory/proof**,
section=full manuscript, language=en, journal=generic).

**Divergence note.** `papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md` mandates the *vendored* copy at
`papers/skills/nature/`, pinned at source rev `93bb0f9`. Upstream has since been restructured:
it is now journal-agnostic and archetype-aware, the canonical entry point is `academic-writing`
rather than `nature-writing`, and it carries 22 skills against the vendored subset. This pass used
upstream at the operator's direction. The vendored pin and the protocol's skill names are
therefore stale; refreshing them (or re-pointing the protocol at the upstream repository) is a
separate, unmade change — flagged here rather than done silently, since the protocol is an
operator mandate.
