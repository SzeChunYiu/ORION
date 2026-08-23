# P2 open-world acquisition successor result — reproduction failed, no candidate claim

- **Record id**: `P2_OPEN_WORLD_ACQUISITION_RESULT`
- **Date**: 2026-08-22
- **Freeze it answers**: `../../protocol/P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.md`
  (twin `…_FREEZE_2026-08-22.json`, `parameters_sha256`
  `ad7e4c6afd66943693ae732b2dde9131aa5bddd13b5632dc97c38223149f769a`)
- **Machine-readable result**: `P2_OPEN_WORLD_ACQUISITION_RESULT_2026-08-22.json`
- **World content hash**: `4e5bdea6f6a7f4031f6f395f43f42484ea2a789e9e89b09c2c2eec963a9b7c2a`
- **World**: 9,575 documents, 280 tasks, seed `20260822`
- **Verdict**: **`REPRODUCTION_FAILED__NO_CANDIDATE_CLAIM`**
- **Claim scope**: `CONSTRUCTED_REPRODUCTION_ONLY__DEVELOPMENT_EVIDENCE`

The freeze document, its twin and the three modules were written, dated and hashed
before the world was generated and before any arm was executed. Every threshold
below was set there. Nothing was retuned after a number was seen, and nothing is
retuned now.

---

## 1. The blocking gate failed

**G1 REPRODUCTION**, on the primary `distinguishable` family:

| Quantity | Archived Dev-3R baseline | Required by G1 | Observed for B0 |
|---|---:|---:|---:|
| mean recall | 0.051422 | ≤ 0.12 | **0.5181** |
| zero-hit fraction | 0.7917 (19/24) | ≥ 0.60 | **0.0000** (0/120) |
| mean candidates returned | 20.0 | ≥ 18 | 20.0 |

The archived lexical baseline, reimplemented against this world, scored **ten
times** the recall it scored on the live slice and missed on **no** task. The
constructed `distinguishable` family therefore is **not** a reproduction of the
failure under repair, and by the frozen verdict rule no candidate claim may be
made over it. All other gates are reported below for completeness; none of them
can license anything while G1 fails.

The construction error is identifiable and is the author's, not the mechanic's.
Post-hoc: on the first 40 `distinguishable` tasks, the baseline's third call —
`BASE_BROAD`, a plain `OR` over six tokens — already placed 104 gold records
inside its own twenty results at **median rank 2**. The adjacent neighbourhood
was built to carry two of the topic's five terms against gold's three, on the
expectation that an additive BM25 score would not separate them; it separates
them easily. The two apparatus terms in the baseline's query (df/N 0.27 and 0.31)
did not cost it enough to matter.

---

## 2. Every arm, every family

Mean recall at the 20-candidate cap. Three provider calls per task, twenty
results per call, for every arm.

| Family | N | B0 archived | B1 shipped D1/D2/D3 | **S2 D5** | A1 D5 queries + round-robin | A2 D1 terms + coverage merge | A3 D5 without expansion |
|---|---:|---:|---:|---:|---:|---:|---:|
| `distinguishable` | 120 | 0.5181 | 0.7644 | **1.0000** | 1.0000 | 0.4814 | 1.0000 |
| `well_posed` | 40 | 1.0000 | 0.9917 | **1.0000** | 1.0000 | 1.0000 | 1.0000 |
| `variant_gap` | 40 | 0.0208 | 0.4483 | **0.4442** | 0.4442 | 0.0167 | 0.4442 |
| `no_bridge` | 40 | 0.0375 | 0.4704 | **0.4850** | 0.4850 | 0.0333 | 0.4850 |
| `undistinguished` | 40 | 0.0321 | 0.1775 | **0.0983** | 0.3450 | 0.1921 | 0.0983 |

Zero-hit fraction for B0: 0.000 / 0.000 / 0.875 / 0.775 / 0.850 in the same row
order. Every arm returned a full twenty candidates on every task in every family.

### The shipped derivations, measured honestly

The freeze asked for the shipped `arb_runtime` derivations' own number. On the
primary family **B1 scored 0.7644**, well above the archived baseline's 0.5181
and far above anything the live campaign saw. `D1`/`D2`/`D3` are not weak here.
Their weakness in the live campaign is therefore not reproduced by this world
either, which is the same finding as §1 from the other side.

---

## 3. What the ablations say about the candidate, and it is not flattering

`D5_GROUNDED_SPECIFICITY_LADDER` bundles three departures from the shipped
mechanic. The ablations separate them, and two of the three earned nothing.

**The query half carries everything.** On `distinguishable`, `variant_gap` and
`no_bridge`, `S2 = A1 = A3` to four decimal places. A1 is S2's queries under the
*archived* round-robin merge and A3 is S2 without grounded expansion. The entire
difference from the baselines is produced by term **grounding**, the **document-
frequency gate** and the **satisfiability-bounded conjunction width** — the query
side. Worked case `ACQ-0000` shows it directly: the baseline's second call is
`all:protocol AND all:nephron`, pairing a df/N = 0.31 apparatus word with a
content term; the candidate's first rung is `all:nephron AND all:chondrite`, two
terms at df/N ≈ 0.018.

**The coverage-first merge is unsupported and once harmful.** It was neutral in
four families. In the fifth it cost 0.2467 recall: on `undistinguished`, A1 (same
queries, round-robin) scored **0.3450** against S2's **0.0983**. The merge is a
bet that gold agrees with more distinct query terms than its neighbourhood does;
where that bet is wrong the bet is expensive, and `undistinguished` is the family
built to make it wrong. This run provides no evidence for the merge and one
concrete case against it.

**Grounded expansion never fired.** `S2 = A3` in all five families, expansion
contribution exactly 0.0000 everywhere, including `variant_gap` where bridge
records exist by construction. Post-hoc, the mechanism failed upstream of
retrieval: the mean number of expansion terms formed on `variant_gap` was
**0.05**, and of the 85 variant-only gold records across that family, rung 3
retrieved **0** and **0** survived into the cap.

The cause is a design defect in the candidate, and it is worth naming precisely
because it is not obvious from the code: `D5` selects its pseudo-relevance
feedback set with the *same* coverage-first rule it uses for the final merge. The
bridge records — the only records carrying both vocabularies — agree with at most
two core query terms, while the twenty-four adjacent records agree with two and
repeat them, so the feedback slots fill with records that use only vocabulary the
query already has. Coverage-first maximises agreement with the vocabulary you
already hold, which is exactly the wrong objective for a component whose purpose
is to find vocabulary you do not. A second defect compounds it: the merge counts
coverage over core terms only, so a record reachable *solely* through expansion
vocabulary scores coverage 0 and is demoted below every core-matching candidate,
i.e. out of the cap. The expansion rung and the merge work against each other.

Neither defect is repaired here. Repairing a mechanic after seeing its ablation
is the post-outcome optimisation this programme's stop rules forbid; naming and
measuring it is not.

---

## 4. Gate table, for completeness

| Gate | Blocking | Outcome | Numbers |
|---|---|---|---|
| **G1 REPRODUCTION** | yes | **FAILED** | B0 recall 0.5181 (≤ 0.12 required), zero-hit 0.0000 (≥ 0.60 required), candidates 20.0 |
| **G2 CANDIDATE** | yes | passed | S2 1.0000 vs B0 0.5181, gain +0.4819; sign test 120 wins / 0 losses, p = 1.50e-36; bootstrap 95% CI [0.4644, 0.4992] |
| **G3 MARGIN OVER SHIPPED** | yes | passed | S2 1.0000 vs B1 0.7644, margin +0.2356 |
| **G4 NO HARM** | yes | passed, non-vacuous | `well_posed`: reference 1.0000, S2 1.0000, loss 0.0000 |
| **G5 BRIDGE SPECIFICITY** | no | passed | `no_bridge`: S2 0.4850, A3 0.4850, gain 0.0000 — but see §3: expansion is inert everywhere, so this gate is uninformative rather than confirmatory |
| **G6 UNDISTINGUISHED CEILING** | no | passed | `undistinguished`: B0 0.0321, S2 0.0983, gain +0.0663 |

G2–G4 are **not** promotable. The frozen verdict rule makes G1 blocking precisely
so that a large gain over a baseline that is not failing cannot be reported as a
repair. A gain measured against a baseline scoring 0.5181 is not evidence about a
baseline that scored 0.0514.

---

## 5. A post-hoc observation, explicitly not converted into a result

Three of the four non-primary families *did* land in the archived band:

| Family | B0 mean recall | B0 zero-hit | B0 candidates |
|---|---:|---:|---:|
| archived Dev-3R live slice | 0.0514 | 0.7917 | 20.0 |
| `undistinguished` | 0.0321 | 0.8500 | 20.0 |
| `variant_gap` | 0.0208 | 0.8750 | 20.0 |
| `no_bridge` | 0.0375 | 0.7750 | 20.0 |

This is recorded because suppressing it would be worse than recording it, and it
is **not** used. G1 was defined on `distinguishable` in the freeze; re-designating
a primary family after seeing which one reproduced the signature is the
outcome-dependent slice change the V2 stop rule exists to forbid, and it is the
specific error that produced `DEV3R_FINAL_NON_ELIGIBLE`'s prohibition on a Dev-4.

The observation is nonetheless the most interesting thing in this run, for one
reason. The family whose baseline profile matches the live slice most closely is
`undistinguished` — the family built so that gold is **not** separable from
adjacent literature by surface-lexical evidence — and it is the one family where
the candidate does **not** repair anything (S2 0.0983 against B0 0.0321, inside
the pre-committed +0.10 ceiling, and *worse* than both B1 and its own A1
ablation). If the live AutoResearchBench Wide gold is undistinguished in that
sense, no query-derivation upgrade moves it and the archived negative is a
property of the benchmark rather than of the mechanic. This run cannot tell which
case the live benchmark is in: the bundle is absent from this environment and the
providers are unreachable. Settling it needs a separately frozen campaign, and
the discriminating measurement is a lexical-separability probe on the benchmark's
own gold, not another acquisition arm.

---

## 6. What this run does and does not establish

**Establishes.**

1. `D5_GROUNDED_SPECIFICITY_LADDER` exists, runs, is deterministic, spends
   exactly the archived campaign's budget (3 calls × 20 results, 20-candidate
   cap), reads only the question text and index document frequencies, and never
   touches a gold set, concept tag or access key. It is pinned by 44 contract
   tests.
2. Its query-side components — grounding, the inherited df gate, and the
   satisfiability-bounded conjunction width — are the whole of its effect in
   every family measured here.
3. Its two novel components, the coverage-first merge and grounded expansion, are
   **not** supported by this run: the first never helped and once cost 0.2467
   recall; the second never fired, for a reason now diagnosed.

**Does not establish.**

1. Anything about mean recall on the official AutoResearchBench Wide benchmark.
   No provider was called; none is reachable.
2. That `D5` repairs the archived failure. G1 failed, so this world never posed
   that failure.
3. L1 `P2_EXTERNAL_MECHANISM_SUPPORTED` or L2 `P2_EXTERNAL_DISCOVERY_SUPPORTED`.
   Neither is opened, and offline synthetic evidence could not promote them in any
   case.
4. Any revision of `P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18` or of
   `JOURNAL_READINESS_V2.md`. That terminal stands.

**The authorized scientific terminal remains `P2_NARROWED`, unchanged.**

---

## 7. One run, and it is spent

The freeze committed to one world, one seed, one execution. That has been used.
The failure was structural rather than stochastic — a different seed re-draws the
term assignments but not the three-of-five against two-of-five stratum design that
made the baseline succeed — so a second seed under this freeze would fail
identically and was not taken.

A further attempt requires a further prospective freeze **written by someone who
has not seen §5**, or written with §5's observation declared as the prior it now
is. Whichever is chosen, the fact that a further attempt was taken must be
reported alongside it.
