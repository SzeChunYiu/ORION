# P2 successor-mechanic freeze: lexical-echo-resistant candidate generation

- **Record id**: `P2_LEXICAL_ECHO_SUCCESSOR_FREEZE`
- **Date frozen**: 2026-08-21
- **Status at freeze time**: written before any corpus was generated, any mechanic was executed, and
  any outcome was observed. Every constant below was chosen from the *named mechanism* in the stage
  attribution, not from a result. Nothing had been run when this file was written.
- **Gate served**: `P2-U-T5` — *"A negative/tied family has generated and validated at least one
  stronger successor search mechanic."* (`src/orion/programme/superiority_terminals.py`,
  `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`, issue #650)
- **Machine-readable twin**: `P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21.json`. It carries the same
  parameter block plus its sha256. The runner recomputes that digest from its own constants and
  refuses to execute on a mismatch, so the numbers cannot drift from this document silently.

---

## 1. The negative this successor is built for

Three archived artifacts define the negative. **None of them is edited by this work.**

| Artifact | What it establishes |
|---|---|
| `evidence/external_results/AUTORESEARCHBENCH_DEEP_ID_PROBE_V1.json` | `target_hits: 0` over 600 Deep tasks, 600 provider requests, `mean_predicted_count: 11.13` |
| `evidence/external_results/DEEP_JUDGE_CONTROL_2026-08-17.json` | `CONTROL_PASSED 9/9` (6 positives accepted, 3 negatives rejected) — the judge was working |
| `evidence/external_results/DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json` | judge-free: 564 items with reference and candidates, 10,850 candidate titles, **0** exact-title recoveries, **0** substring recoveries, **8** token-overlap ≥ 0.5 recoveries (0.0142) |

The attribution's conclusion is the *premise* of this work and is not re-diagnosed: candidate
**generation** is the failing stage, and the named mechanism is

> "needle questions whose surface lexicon echoes in wrong papers, e.g. 'supplementary' in the
> question retrieving a title containing 'Supplementary Orbit'"

i.e. **lexical echo** — a term that is *incidental vocabulary* in the question (document-apparatus
words: *supplementary*, *appendix*, *figure*, *panel*, *addendum*, *caption*) is treated by the
retrieval mechanic as a *content* term, so the provider returns documents matching the incidental
term rather than the topic.

Three properties of the real failure are what this construction must carry over, and each drives a
design decision below:

1. **The apparatus word is frequent; the content word is not unique.** A Deep question's content
   vocabulary is ordinary scientific vocabulary shared by thousands of papers, so no content term
   alone identifies the needle.
2. **The needle does not contain the apparatus word.** The question says *supplementary* because
   that is where the number sits, not because the paper is about supplements. So the needle is
   exactly the document that cannot match the query's most heavily weighted terms.
3. **The wrong paper matches on apparatus + one content word.** "Supplementary Orbit" is not a
   random document; it is the shape that beats the needle under equal term weighting.

## 2. What this study can and cannot be

The official probe cannot be re-run here and no attempt is made to re-run, emulate or simulate it:

- the frozen `official_input.jsonl` is not in the repository (only its sha256
  `46fd5500859dd1c8f2853316e186b6921b80d90cde7ba12ba1b8a5bbf86b9ef6` is recorded), and
- arXiv and OpenAlex both return `CONNECT tunnel failed, response 403` at this environment's proxy.

The validation is therefore on a **constructed reproduction of the named failure mode**, offline and
deterministic. The claim scope is fixed *now*, before any number exists:

> **CONSTRUCTED_REPRODUCTION_ONLY.** A pass validates the successor mechanic against the
> lexical-echo mechanism named in the stage attribution, on an authored corpus in which that
> mechanism is present by construction and the denominator is complete. It does **not** validate the
> successor on AutoResearchBench Deep, does **not** revive
> `AUTORESEARCHBENCH_DEEP_ID_PROBE_V1`, and licenses **no** statement about `target_hits` on the
> official benchmark. The strongest sentence a pass permits is: *the mechanism named by the stage
> attribution is sufficient, on its own, to drive a lexical candidate generator to near-zero
> recovery, and a discriminativeness-grounded generator is not driven to zero by it.*

**Known transfer limitation, stated in advance.** The successor needs corpus-level document
frequencies. Offline these are exact. Against a real provider they must come from a result-count
endpoint or a sampled index, which is an additional engineering dependency this study does not
discharge.

## 3. The constructed world

One world, seed **20260821**, generated once. There is no second seed and no re-draw.

### 3.1 Vocabulary strata (disjoint, authored, frozen)

| Stratum | Size | Contents | Role |
|---|---|---|---|
| Incidental | 6 | `supplementary appendix figure panel addendum caption` | Document-apparatus words. Zero topical content. The class the attribution names. Kept small deliberately: apparatus words are few and ubiquitous in real corpora. |
| Domain | 80 | ordinary scientific content words (`orbit`, `resonance`, `manifold`, …) | Content terms are drawn from here, so each is shared across ~11 tasks and roughly a hundred documents. Property 1 of §1. |
| Neutral | 24 | connective scientific filler (`analysis`, `value`, `model`, …) | Appears in every document of every stratum, so surface length and generic vocabulary discriminate nothing. |

### 3.2 Documents

Per task `t`: four content terms `c1..c4` drawn from the domain lexicon, two incidental terms
`i1, i2` drawn from the incidental lexicon, all by the frozen seed.

- **1 needle.** Title: two of `c1..c4` (seed-chosen, *not* chosen to be the ones the baseline keeps)
  plus neutral words. Abstract: each of `c1..c4` exactly once, plus neutral words. The needle
  carries **no incidental term anywhere** — property 2 of §1.
- **6 topical neighbours.** One per distinct pair of `{c1..c4}`. Title carries the first term of the
  pair; abstract carries both plus two unrelated domain words and neutral words. These are the
  honest competition: the successor must place the needle above documents that really do share half
  the topic.
- **6 echo distractors** (echo family only). Title is exactly the shape the attribution names —
  `"{Incidental} {ContentWord}"`, e.g. *"Supplementary Orbit"*. Abstract repeats the incidental term
  three times and the content term once, plus neutral words. Three distractors use `i1`, three use
  `i2`; the content word cycles over `c1..c4`. Property 3 of §1.
- **500 background fillers.** Title: two domain words plus a neutral word. Abstract: three domain
  words plus neutral words.
- **Incidental density.** Every non-needle document (neighbours, distractors, fillers) carries two
  further incidental terms with probability 0.6, drawn by seed from the pool of 6. This is what
  makes apparatus words genuinely high-document-frequency corpus-wide (target ≈ 0.20 of the corpus
  per apparatus word) rather than an artefact of the distractor blocks, while a content word sits at
  ≈ 0.04. Needles are the only documents excluded.

**Construction precondition (checked by the runner before any arm executes).** The world is a
reproduction of the named mechanism only if apparatus words really are non-discriminative and content
words really are discriminative. The runner therefore requires, on the generated world:
median `df/N` over the 6 apparatus words **>= 0.12**, and median `df/N` over the 80 domain words
**<= 0.05**. A world violating either bound does not have the intended structure; the run aborts and
says so rather than reporting arm numbers over a world that is not the one specified. This check is
on the *corpus*, not on any outcome, and is evaluated before a single query is issued.

Corpus size: 220 needles + 1320 neighbours + 720 echo distractors + 500 fillers = **2760 documents**.
Relevance and the target of each task are decided by an authored rule over the world, reusing
`orion.study.p2.corpus.Document`, `Topic`, `DiscoveryWorld` and `sha256_digest`, so the denominator
is complete by construction.

### 3.3 Task families and question templates

Templates are fixed verbatim here. `{cN}` and `{iN}` are substituted; nothing else varies.

| Family | n | Template |
|---|---|---|
| `echo` | 120 | `Which analysis gives the {c1} {c2} {c3} {c4} value? The number I need is not in the main text: it appears in the {i1} material, and the {i1} section presents it as a {i2}, with the {i2} note stating the uncertainty.` |
| `no_echo` | 60 | `Which analysis gives the {c1} {c2} {c3} {c4} value? The number I need is stated in the main text of the paper itself, with its uncertainty.` |
| `paraphrase_gap` | 40 | the `echo` template verbatim, but the task's needle and neighbours are written with `sigma(c)` in place of every `c`, where `sigma` is the fixed fixed-point-free permutation `index -> (index + 37) mod 80` of the domain lexicon (37 is coprime with 80, so the map is a single 80-cycle), so question and needle share **no** content token. |

Roles: `echo` is **primary** (reproduces the named mode). `no_echo` is the **harm guard** (the
successor must not damage questions that never had echo). `paraphrase_gap` is the **specificity
control** — the successor is a lexical mechanic and is *not* expected to repair a semantic gap; if
it does, the world is not isolating the echo mechanism and the claim must be narrowed further.

## 4. Arms

All arms see the same question, the same world and the same candidate budget. Candidate list length
is **k = 11**, matching the probe's `mean_predicted_count: 11.13`; the primary outcome is read at
**k = 10** inside that budget. Ties are broken by `doc_id` ascending in every arm, deterministically.
No arm sees the gold set, the target, or the family label.

### B0 — the current mechanic (baseline; this is what produced the negative)

1. **Query derivation:** `orion.study.p2.arb_runtime.derive_current_vocabulary_query(question,
   limit=6)`, reused verbatim — rule `D1_CURRENT_VOCABULARY`: rank the question's content tokens by
   within-question frequency, ties by first appearance, keep the top 6.
2. **Ranking:** unweighted surface match,
   `score(d) = SUM over t in Q of tf(t, title(d) + " " + abstract(d))`, every query term weighted
   equally. This is the "treat every query term as a content term" behaviour the attribution names.
   No length normalisation: all documents are of comparable length by construction, so ranking is
   not driven by length.

### B1 — strongest existing lexical baseline (reference arm)

Same `D1` query, ranked by `orion.study.p2.baselines.Bm25Scorer` reused verbatim (Okapi BM25 with
Robertson/Sparck Jones IDF). **B1 exists because BM25's document-side IDF is the obvious objection to
the successor.** If BM25 alone repairs the world, the successor's marginal contribution is small, and
this freeze commits in advance to reporting exactly that.

### S1 — the successor: `D4_DISCRIMINATIVE_TERM_GATING`

Uses only index statistics. Never the gold set, never the target, never the family label.

1. **Same tokenizer as B0.** `arb_runtime._content_tokens`, byte-identical, so no part of any gain
   can come from a different tokenizer.
2. **Incidental gate.** Drop a question token `t` if `df(t) == 0` (it matches nothing) or if
   `df(t) / N > 0.05`. *Rationale, a priori:* a term occurring in more than one document in twenty
   cannot by itself identify a needle; admitting such a term as a content term **is** the defect the
   attribution names. The construction places apparatus words at ≈ 0.20 and content words at ≈ 0.04,
   so the threshold is not knife-edge — but it is a threshold, and it is fixed here.
3. **Discriminative selection.** Rank the surviving tokens by `idf(t)` alone and keep the top **6** —
   the *same* query width as B0, so the comparison is not a budget gift. *Rationale:* B0's salience
   proxy is within-question repetition, which is exactly what promotes a twice-mentioned apparatus
   word over a once-mentioned content word. Selection by `idf(t) * count(t)` was considered and
   rejected at freeze time on paper, because doubling the count of a low-idf term can still outrank a
   high-idf term; corpus discriminativeness alone is the property that separates the strata.
4. **Discriminativeness-weighted, saturating scoring.**
   `score(d) = SUM over t in Q' of idf(t) * tf(t,d) / (tf(t,d) + 1.2)`. *Rationale:* the weight makes
   a match on a rare content term worth more than a match on a common one; the saturation stops a
   document that merely repeats one term (an abstract that says *supplementary* four times) from
   outranking a document that matches several distinct terms.
5. **Topical-agreement admission.** A document is admitted only if it matches **at least 2 distinct
   terms of `Q'`**. Non-admitted documents are ranked strictly *below* every admitted document —
   **demoted, not deleted**, so this rule cannot inflate recall at large `k`. *Rationale:* the named
   failure is a document that agrees with the query on one apparatus token plus one content token and
   disagrees topically; requiring agreement on two discriminative terms is the smallest rule that
   rejects it.

`idf(t)` comes from `baselines.Bm25Scorer.inverse_document_frequency` (reused, not reimplemented), so
B1 and S1 share one definition of discriminativeness and cannot differ because of it.

### A1, A2 — ablations (reported, non-blocking)

- **A1** = steps 1–3 only (gated, discriminatively selected query) scored with **B0's unweighted**
  ranking. Isolates query-term *selection*.
- **A2** = **B0's ungated `D1` query** scored with S1's weighted saturating ranking, no admission
  rule. Isolates *scoring*.

## 5. Primary outcome and pre-committed gates

**Primary outcome:** `hit@10` on the `echo` family — the fraction of `echo` tasks whose target
document appears in the top 10 of the arm's candidate list. Chosen to mirror the archived
measurement: the probe returned ~11 candidates per task and the attribution asked whether the
reference was recoverable from that candidate set at all.

**Secondary outcomes, all reported whichever way they fall:** `hit@1`, `MRR@50`, per-family
breakdowns, the median rank of the target, and the median rank of the best echo distractor.

**Statistic:** exact two-sided McNemar (binomial) test on paired per-task `hit@10` outcomes.

| Gate | Statement | Consequence if it fails |
|---|---|---|
| **G1 REPRODUCTION** | B0 `hit@10` on `echo` **≤ 0.05** | The construction did not reproduce the failure mode. That is reported and the study stops; no successor claim is made. Reference point: judge-free recoverability in the real probe was 8/564 = 0.0142. |
| **G2 SUCCESSOR** | on `echo`: `S1 hit@10 − B0 hit@10 ≥ 0.30` **and** `S1 hit@10 ≥ 0.50` **and** McNemar `p < 0.01` | The successor is reported as **NOT validated**. That is a real negative and is recorded as one, with no retuning. |
| **G3 HARM** | on `no_echo`: `S1 hit@10 ≥ B0 hit@10 − 0.05` | The successor is reported as **harmful off-mode** and G2 alone does not license it. *Vacuity check:* if B0 `hit@10` on `no_echo` < 0.30 the guard is declared vacuous and said to be so. |
| **G4 MARGINAL-OVER-BM25** | on `echo`: `S1 hit@1 ≥ B1 hit@1 + 0.10` | Non-blocking for G2. On failure the recorded finding is that the repair is *corpus-grounded term weighting per se*, already available in BM25, and that the successor's extra machinery is not carrying the result. |
| **G5 SPECIFICITY** | on `paraphrase_gap`: `S1 hit@10 − B0 hit@10 < 0.10` | Non-blocking. On failure the world is not isolating the echo mechanism, and the claim scope in §2 is narrowed in the result record. |

**Verdict rule, fixed now:** the successor is called
**`VALIDATED_ON_CONSTRUCTED_REPRODUCTION`** iff G1 **and** G2 **and** G3 all pass. Any other
combination gets its own verdict string and **no** successor claim is entered against `P2-U-T5`.

## 6. Anti-tuning commitments

1. Every constant in §3–§5 — seed `20260821`; family sizes 120/60/40; 6/80/24 lexicon sizes;
   6 neighbours and 6 echo distractors per task; 500 fillers; incidental density 0.6 with 2 draws;
   permutation offset 37; `k = 11` and primary `k = 10`; query width 6; df fraction 0.05; saturation
   1.2; admission threshold 2; and all five gate thresholds — is fixed by this document and hashed
   into the JSON twin. The runner recomputes that digest and aborts on mismatch.
2. The corpus is generated once from the frozen seed. No second seed, no re-draw, no "we tried a few
   worlds".
3. If an arm's number is disappointing, the number is reported. No parameter in §3–§5 is changed
   after an outcome is seen. If any parameter is ever changed, this file is superseded by a new dated
   freeze that states what changed and why, and the old result stands beside the new one.
4. No existing P2 result, receipt, or archived probe artifact is modified by this work. Only new
   files are added.

## 7. Outputs this freeze commits to producing

- `src/orion/study/p2/echo_world.py` — the constructed world and its tasks
- `src/orion/study/p2/echo_mechanics.py` — B0, B1, S1, A1, A2 and the metrics
- `src/orion/study/p2/echo_campaign.py` — the runner (`main(argv)`, `argv` required)
- `papers/paper-02-open-world-scientific-discovery/evidence/successor_results/P2_LEXICAL_ECHO_SUCCESSOR_RESULT_2026-08-21.json`
- `tests/unit/study/p2_open_world/test_p2_lexical_echo_successor.py`
