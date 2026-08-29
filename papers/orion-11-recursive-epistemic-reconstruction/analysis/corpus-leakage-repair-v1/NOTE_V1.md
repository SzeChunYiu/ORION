# ORION-11 corpus leakage — revival V1

**Scope.** Measures whether a case's task family is recoverable from surface features a
blind responder can read, and repairs the channel that carries it. Binds no claim about
any case's science: no gold label, family assignment, or resource description was
changed. `grants_authority: NONE`.

**Headline.** The leak the audit found in resource paths is gone, and it was already gone
before this work started. The leak that is live sits somewhere else: **all eleven
DECOMPOSITION prompts end in the same sentence**, so the single word `diagnose` recovers
the family 11/11 at precision 1.00. Pooling the closing-instruction vocabulary across
DECOMPOSITION and EXECUTION drops every leaking feature below the reporting floor and puts
the corpus inside its own shuffle null.

---

## 1. Baseline reproduced before anything was changed

`MECHANICAL_SOLVABILITY_AUDIT_V1.md` reports probe 2 as 10/11 DECOMPOSITION, 0/55
elsewhere. Reproduced exactly:

```
rule /(proposal|trial)/ over path stems, audit snapshot
TP=10  FP=0  FN=1  TN=55   precision 1.00  recall 0.91   missed p1-c138
```

The snapshot is the audit's own `resource_lines` inside
`evidence/mechanical_solvability_audit_v1.json`, which records the paths it scored. That
matters: the live corpus no longer contains those paths, so a reproduction against `main`
would have silently measured a different corpus. `p1-c138` is the miss the audit itself
names, which is the tell that the reproduction is of the right bytes.

## 2. The audit's rule no longer fires on `main`

```
same rule, papers/orion-11-.../protocol/cases at 01a3861b:  0/11
```

An upstream rename replaced every leaking stem: `payments/timeout-trial.md` →
`payments/timeout-note.md`, `billing/skip-proposal.diff` → `billing/skip-diff.diff`, and
eight more. This was not visible from the audit, which still reads as current.

**A rename can move a leak instead of removing one**, so the path channel was re-measured
rather than assumed clean. See §4.

## 3. Mining, not probing

A hand-written probe answers "is this feature diagnostic?", never "which features are?".
`probe_corpus_leakage_v1.py` enumerates the feature space a `PublicView` exposes — path
tokens, extensions, path depth, resource counts, closure-resource counts, first/last
resource position, prompt words, prompt length, budget class — and scores every feature
against every family. Resource text after the em dash is content, not surface, and is
never read.

**The first version of this miner reported the known-leaking corpus clean.** Single tokens
`proposal` (5/11) and `trial` (5/11) each fall just under a recall floor of 0.5; their
union reaches 0.91. Leakage is normally a *convention* spread over several words, so the
miner searches greedy disjunctions as well as single features. That correction is the
reason anything below was found.

**Every run carries a shuffle null.** With 66 cases and ~2 000 candidate features, perfect
precision is cheap: greedy disjunction reconstructs an arbitrary 11-case grouping from
tokens alone. Without the null, a repair could be declared successful merely by moving
vocabulary around. The null re-mines the same space against permuted family labels.

## 4. The path channel is not separable from mining noise

```
CURRENT main, paths only:  999 features
  single features clearing precision>=0.9, recall>=0.5:  0   (null max 0)
  disjunction rules clearing the floors:                 5   (null max 5)
  observed max disjunction recall:  0.91
  shuffle null max recall:  mean 0.74,  p95 0.91,  max 1.00   (200 permutations)
```

The best surviving path rule — MEASUREMENT at precision 1.00, recall 0.91 — sits exactly at
the null's 95th percentile, and shuffled labels reach recall 1.00. It is a mining artifact.

This is a **tie, not a clearance**, and one confound is worth stating: the rename *raised*
the null. The pre-repair snapshot had 722 path features and a null rule-count max of 2; the
current corpus has 999 and a max of 5. More path vocabulary makes spurious perfect
disjunctions easier. The honest claim is therefore narrow: **no path rule is separable from
mining noise at this feature-space size** — not that the path channel is provably empty.

## 5. The live leak is the closing instruction

```
CURRENT main, paths and prompts:  1 929 features
  single features clearing the floors:  6   (null max 0)
```

| feature | family | precision | recall |
|---|---|---|---|
| `prompt_word:diagnose` | DECOMP | **1.00** | **1.00** |
| `prompt_word:specify` | DECOMP | **1.00** | **1.00** |
| `prompt_word:fix` | DECOMP | 0.92 | 1.00 |
| `prompt_word:find` | EXEC | 0.92 | 1.00 |
| `prompt_word:repair` | EXEC | 0.92 | 1.00 |
| `prompt_word:instrument` | EVID | 1.00 | 0.55 |

Against a null maximum of **0**, these are not artifacts.

The mechanism is visible on inspection: **all eleven DECOMPOSITION prompts end in the
identical sentence** "Diagnose the defect and specify the fix.", and all eleven EXECUTION
prompts end in a variant of "name the defect and give the repair". Stripping the final
sentence takes the six leaking features to **one**, which attributes the failure to a
single stage: the per-family closing-instruction template.

Its origin is in the generator. `protocol/cases/generate_cases.py:246` gives
`HIDDEN_DECOMPOSITION_OR_INTERFACE` a `scenario_template` ending in that fixed sentence,
one such template per family.

## 6. Repair: pool the vocabulary, do not flatten it

The two closers are synonyms — "diagnose the defect and specify the fix" and "name the
defect and give the repair" request the same deliverable in disjoint words. The split
carries no meaning, so mixing the vocabularies costs the corpus nothing. Flattening all 66
to one sentence would instead erase a distinction other families genuinely have
(MEASUREMENT asks the solver to *report whether* something holds), changing the task rather
than removing the shortcut. The standard is the audit's own: naming a remedy artefact is
legitimate, the *perfect* correlation is the defect.

Four phrasings, assigned round-robin **within each family** so every phrasing appears in
both. `instrument` is swapped for synonyms across the six EVIDENCE prompts that endorse the
measurement approach; the endorsement is what makes those cases controls and survives.

`repair_corpus_leakage_v1.py` changed **22 of 66 prompts** (17 pooled closers, 5 synonym
swaps) and rewrites only the terminal imperative clause — EXECUTION prompts carry an
endorsement prefix ("The working position: …") that marks them as negative controls, and
replacing the whole sentence would delete the framing `reframe_required` is about.

It re-reads both trees after writing and asserts that `protected_gold`, `task_family`,
`adjudication_status`, `observable_resources`, `case_id` and `budget_class` are unchanged:
**0 violations**. Removing a shortcut must not move an answer.

## 7. Post-repair: every probe collapses

| probe | family | pre-repair | current `main` | repaired |
|---|---|---|---|---|
| `/(proposal\|trial)/` path stem | DECOMP | p 1.00 r 0.91 | r 0.00 | r 0.00 |
| `/(proposal\|trial\|bus)/` path stem | DECOMP | **p 1.00 r 1.00** | p 1.00 r 0.18 | p 1.00 r 0.18 |
| `diagnose` | DECOMP | — | **p 1.00 r 1.00** | p 0.50 r 0.27 |
| `specify` | DECOMP | — | **p 1.00 r 1.00** | p 0.50 r 0.27 |
| `fix` | DECOMP | — | p 0.92 r 1.00 | p 0.43 r 0.27 |
| `find` | EXEC | — | p 0.92 r 1.00 | p 0.79 r 1.00 |
| `repair` | EXEC | — | p 0.92 r 1.00 | p 0.69 r 0.82 |
| `instrument` | EVID | — | p 1.00 r 0.55 | p 1.00 r 0.09 |

The audit's own rule was not the strongest one available: extending it by the token
covering `p1-c138` gives **11/11 at precision 1.00** on the pre-repair snapshot. The leak
was total, not 10/11.

```
REPAIRED, paths and prompts:  1 936 features
  single features clearing the floors:  0   (was 6; null max 0)
  disjunction rules:                    6   (null max 6)
  VERDICT: WITHIN_NULL          probe exit code 0
```

## 8. What still leaks, stated plainly

- **`instrument` keeps precision 1.00** at recall 0.09 (one EVIDENCE case). Above the
  precision bar, far below any recall that makes it a shortcut. Not repaired further,
  because driving a single retained word to zero would mean deleting the endorsement.
- **`find` at precision 0.79 and `repair` at 0.69** are the highest surviving prompt words.
  Both are under the 0.9 bar and both now appear in more than one family.
- **The path channel is a tie against its null, not a clearance** (§4).
- **Six disjunction rules survive at precision 1.00 and recall up to 1.00**, and are
  reported rather than hidden. They sit at the null maximum, and shuffled labels reach the
  same recall, so they are mining artifacts on this evidence — but that is an argument
  from a null, not a proof of absence.

## 9. Not done here

- **The generator is unrepaired.** `generate_cases.py:246` still holds the per-family
  closing template, so a regeneration reintroduces the leak. It was left alone
  deliberately: the committed prompts have diverged from it ("The reading so far:" where
  the template says "The approach on the table:"), so regenerating would discard hand-edited
  content, and the audit records a concurrent agent rewording prompts in this tree.
- **The repaired corpus is a candidate, not a promotion.** It sits in `repaired-cases/`;
  `protocol/cases/` is byte-identical to `main` (66/66 digests verified after the run).
  Promoting it needs coordination with whoever is editing prompts.
- **No regression test is wired in.** The audit asked for the probes to become tests that
  must fail, and their absence is why this leak survived. The harness is ready:
  `probe_corpus_leakage_v1.py --cases-root <dir>` exits 1 on leakage, 0 when clean.
