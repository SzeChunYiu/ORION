# ORION-17 donor matrix V1 — atomic dispositions for the ten required families

**Status:** `TEN_REQUIRED_FIELDS_DISPOSITIONED__DONOR_SUBTRACTION_ONLY`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This matrix can only narrow novelty.
Nothing here promotes a claim.

`JOURNAL_READINESS.md` §2 ("Nearest-work closure") requires ten parent families
dispositioned with atomic receipts. `submission/publication-ready-20260831/NOVELTY_AND_DONOR_BOUNDARY.md`
is a nineteen-line **boundary statement**, not a disposition: it contains one
`DONOR` token, zero `SPECIALIZATION` and zero `SURVIVING_NEW_CONSEQUENCE`, and
names no family. The families appear in `CLAIM_LEDGER_V1/V2.md` as prose
context, which is mention, not disposition. This document supplies the missing
per-family layer.

It does **not** supersede the boundary statement, whose scientific-authority
ceiling and adversarial exclusions stand unchanged.

## How a file is added to this bound package

ORION-17 is a `DIRECT_BOUND_PAPER`, so adding a file is not a one-step edit, and
the two obvious partial routes both fail in ways that look like a freeze
blocker:

1. add the file alone → `148 of 149 files are bound`;
2. add it and bind it in `CONTENT_MANIFEST_V2.json` → `1 of 149 bound files
   changed`, naming `CONTENT_MANIFEST_V2.json` itself as the drifted file.

Step 2's failure is not self-reference in the manifest, which binds neither
itself nor `CONTENT_MANIFEST_V2.json`. The binding lives one directory down, in
`content_binding_v2/SHA256SUMS`, which carries the manifest's digest. The
complete route is therefore **three files**:

| file | change |
|---|---|
| the new document | added |
| `CONTENT_MANIFEST_V2.json` | one `{path, sha256}` entry appended |
| `content_binding_v2/SHA256SUMS` | the manifest's digest line rewritten |

`CONTENT_MANIFEST_V1.json` and the top-level `SHA256SUMS` are **not** touched:
`SHA256SUMS` is validated against V1, whose identity is frozen and digest-pinned,
and `inspect_paper` globs `CONTENT_MANIFEST_V*.json`, so V2 alone is sufficient
coverage. This is the same route by which ORION-16 adopted `FINAL_V6` (#2086)
and ORION-18 adopted `FINAL_V4` (#2089).

Binding tests after all three changes: **48 passed**, and no digest was
regenerated to match bytes that moved — which is what the drift ratchet forbids.

**Consequence for §7.** "Full-text related-work section with atomic donor
dispositions" edits the manuscript inside this package, and that edit is
reachable by the route above. §7 is **not** blocked by #1634.

## Dispositions

| Required family | Primary donor objects checked | What the donor already supplies | ORION-17 consequence |
|---|---|---|---|
| graph / knowledge-graph navigation | Hart, Nilsson & Raphael, *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*, IEEE Trans. SSC (1968); Xiong, Hoang & Wang, *DeepPath*, EMNLP (2017); Das et al., *Go for a Walk and Arrive at the Answer*, ICLR (2018) | heuristic best-first traversal with admissibility guarantees; learned multi-hop walks over an incomplete graph where the answer path is not given | Traversing a partially known graph toward a goal is **donor**, including the learned and multi-hop cases. ORION-17 may not claim navigation itself. What remains is that the traversal carries an *obligation contract* that survives composition, which no path-finding formulation represents. |
| exploratory search / information foraging | Bates, *The Design of Browsing and Berrypicking Techniques*, Online Review (1989); Pirolli & Card, *Information Foraging*, Psychological Review (1999); Marchionini, *Exploratory Search: From Finding to Understanding*, CACM (2006) | patch-leaving decisions under diminishing returns; evolving rather than fixed information need; the distinction between lookup and open-ended investigation | Information scent, patch-leaving and the evolving-need model are **donor**, and they already predict the breadth/concentration tradeoff ORION-17 measures. The benchmark's breadth metrics must therefore be reported against a foraging-style baseline or they measure a known effect. |
| POMDP / active information acquisition | Howard, *Information Value Theory*, IEEE Trans. SSC (1966); Kaelbling, Littman & Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence (1998) | acting under partial observability with belief-state planning; the expected value of an observation, and hence when acquiring information is worth its cost | Deciding what to observe next under uncertainty is **donor**, with an optimality criterion ORION-17 does not improve on. The `CANNOT_CHECK` outcome is not a new epistemic state here; it is an unresolved belief. ORION-17 may only own the case where the obligation to resolve it is **non-discretionary** — value of information does not model an obligation that cannot be traded away. |
| planning abstraction / homomorphism | Sacerdoti, *Planning in a Hierarchy of Abstraction Spaces*, Artificial Intelligence (1974); Ravindran & Barto, *Model Minimization in Markov Decision Processes*, AAAI (2002); Li, Walsh & Littman, *Towards a Unified Theory of State Abstraction for MDPs*, ISAIM (2006) | abstraction hierarchies with refinement between levels; homomorphisms that preserve solution structure; a taxonomy of abstractions by what they preserve | This is the **closest structural parent** to the atlas/chart construction. "A map that preserves what matters and forgets the rest, with a stated preservation property" is exactly the MDP-homomorphism contract. §3's requirement that donor mappings *prove conservative embedding where feasible* is therefore the right gate, and it must be executed against this family specifically rather than against navigation generally. |
| learned / adaptive planning representation | Tamar et al., *Value Iteration Networks*, NeurIPS (2016); Ha & Schmidhuber, *World Models* (2018); Hafner et al., *Dream to Control* (2020) | planning computation embedded in a learned representation; latent dynamics learned from experience and planned over directly | Learning the representation one plans in is **donor**. ORION-17 must not present an adaptive atlas as new on the grounds that the chart is learned rather than given. |
| deep-search agent planning and stopping | *To Search or Not to Search: Aligning the Decision Boundary of Deep Search Agents via Causal Intervention*, arXiv:2602.03304 (2026); *Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents*, arXiv:2608.01913 (2026); *DeepSearchQA*, arXiv:2601.20975 (2026); *S1-DeepResearch*, arXiv:2606.15367 (2026) | over-search and under-search as a mis-set decision boundary; the empirical finding that accuracy tracks cumulative retrieval recall rather than search effort; dynamic stopping as an explicit evaluation target | **Premature stopping is an actively worked donor problem, not an ORION-17 discovery.** §6's premature-stop and false-independence rates must be reported against one of these baselines. Note a distinction these sources make and ORION-17 currently conflates: DeepSearchQA stops on *exhaustiveness of a set*, the others on *sufficiency for one answer*. ORION-17's obligation coverage is the first target and its root-task success the second; reporting them under one stopping notion would blur the only place the obligation contract can show an effect. |
| model revision / world-model / replanning | Alchourrón, Gärdenfors & Makinson, *On the Logic of Theory Change*, Journal of Symbolic Logic (1985); Ghallab, Nau & Traverso, *Automated Planning and Acting* (2016), on plan repair and replanning | rationality postulates for revising a corpus on new information, including minimal change and recovery; repairing rather than regenerating a plan when the world diverges | Revising beliefs on contradiction and repairing rather than replanning are **donor**, and AGM already fixes what a well-behaved revision must satisfy. ORION-17's reopening semantics must be checked *against* the AGM postulates: if it satisfies them it is an instance, and if it violates one it owes an argument for why. |
| goal / objective revision and evolution | Klenk, Molineaux & Aha, *Goal-Driven Autonomy for Responding to Unexpected Events* (2013); Aha, Cox & Muñoz-Avila, *Goal Reasoning: Research Survey*; Kondrakunta & Cox, *Autonomous Goal Selection and Operations* (2021) | explicit goal representation, formulation of new goals from a trigger, and management of the resulting goal set — goal selection, change, delegation and monitoring | Goal reasoning already owns "the agent changes its own objectives when the world surprises it", including the operations vocabulary. ORION-17's reframe events are **donor** at that level, and the unnecessary-reframe rate must be measured against a goal-reasoning baseline rather than against no reframing at all. |
| ontology / schema evolution and preservation maps | Noy & Klein, *Ontology Evolution: Not the Same as Schema Evolution*, Knowledge and Information Systems (2004); Stojanovic, *Methods and Tools for Ontology Evolution* (2004) | change operations over a conceptual model with explicit preservation of instance data; the argued distinction between schema and ontology change | Preservation maps between successive conceptual states are **donor**, and Noy & Klein already make the point that the ontology case is not reducible to the schema case. ORION-17 must cite this rather than re-derive the distinction. |
| scientific exploration breadth / concentration | Lehman & Stanley, *Abandoning Objectives: Evolution Through the Search for Novelty Alone*, Evolutionary Computation (2011); Pugh, Soros & Stanley, *Quality Diversity: A New Frontier for Evolutionary Computation* (2016) | search driven by behavioural novelty rather than an objective; explicit maintenance of a diverse archive trading coverage against quality | Deliberately seeking structural breadth instead of optimising an objective is **donor**, and quality-diversity already formalises the coverage/quality tradeoff. "Useful structural breadth" in §6 is not a new quantity; it needs a quality-diversity comparator. |

## Net effect

Every one of the ten families is **DONOR** at the level ORION-17 currently
invokes it. No family yields a `SURVIVING_NEW_CONSEQUENCE` on its own. The
residue this matrix leaves is exactly the residue the boundary statement already
admits — an obligation contract that composes associatively — and that residue
now has a sharper defence and a sharper threat:

- **Sharper defence.** None of the ten donors carries a non-discretionary
  obligation through composition. Value of information trades observations
  against cost; goal reasoning may drop a goal; foraging leaves a patch. An
  obligation that cannot be traded away is not expressible in any of them.
- **Sharper threat.** Planning abstraction/homomorphism is closer than the
  boundary statement acknowledges. If the atlas is a homomorphism in the
  Ravindran–Barto sense, the composition law may be a corollary of homomorphism
  composition rather than a new result. **This is not settled here.** §3's
  conservative-embedding proof must be executed against that family before the
  composition law is defended.

## What this does not close

- §2 also requires a hostile exact-composition search and two no-material-change
  rounds. A first pass over ten families cannot satisfy a stability criterion.
- The `#287` novelty certificate is not refreshed by this document.
- §7's "full-text related-work section with atomic donor dispositions" needs the
  manuscript edited. This matrix is the input to that section, not the section.

## Citation provenance

The four 2026 deep-search sources and the goal-reasoning entries were located
and checked against published records for this document. The remaining entries
are standard references cited by title, venue and year only; volume, issue and
DOI were deliberately omitted rather than asserted from recollection, and must
be completed from the record before any of them enters a manuscript
bibliography.

## Boundary

This is a donor matrix, not a priority certificate. Every entry can only
subtract from what ORION-17 may claim. If a source not listed here states the
obligation-carrying composition law directly, this matrix must be amended rather
than the claim defended by terminology.
