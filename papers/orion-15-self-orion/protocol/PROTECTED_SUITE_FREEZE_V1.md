# ORION-ORION-15 protected hidden-cause suite freeze V1

This procedure is the host-side bridge between the design-frozen protocol and a later `EXECUTION_FROZEN` run. It does **not** publish a hidden-cause benchmark into the repository and it does **not** produce empirical evidence.

## Custody rule

The protected input is held outside challenger write authority. It contains:

- all eight protected root-cause labels;
- a unique 256-bit opening nonce per case;
- the **competing cause set** of each case, which names two or three candidates *including the answer*;
- full fresh-task payloads;
- protected evaluator artifact hash;
- protected surfaces and scoring/harm rubrics;
- every declared negative/null/harmful variant payload.

Do not commit that input, its opening nonces, competing cause sets, fresh payloads, evaluator internals, or protected rubrics to a candidate-readable branch.

This list and the *Freeze command* list below are **complements**, and that is one rule rather than two lists that happen not to overlap. Every field of a protected case is exactly one of:

| classification | fields | where it appears |
| --- | --- | --- |
| published | `case_id`, `visible_symptom`, `candidate_visible_context`, `motivating_tasks`, `replay_tasks`, `allowed_change_surface` | verbatim in the candidate packet |
| published as identifier | `fresh_tasks`, `negative_variant_ids` | `task_id`, `changed_axes` and `variant_id` in the manifest; payloads and `content_hash` sealed |
| sealed | `protected_root_cause`, `root_cause_nonce`, `competing_cause_set`, `protected_surface`, `success_rubric`, `harm_rubric` | never, in any freeze artifact |

The three lists are `freeze.PUBLISHED_CASE_FIELDS`, `freeze.PUBLISHED_IDENTIFIER_CASE_FIELDS` and `freeze.SEALED_CASE_FIELDS`, so a disagreement between this document and the freeze is a diff rather than an argument. A field in none of the three is a field whose custody nobody decided: `freeze.require_case_fields_classified` refuses it, so the next schema addition has to be classified here before it can be frozen. `competing_cause_set` was that field until this revision — carried in the protected suite, emitted by nothing, named by neither list. Publishing it would have broken no stated rule; in `PROTECTED_SUITE_V1` its first element is the answer in 24 of 24 cases, so it would have cut the root-cause commitment's domain from eight candidates to one.

## Freeze command

```bash
PYTHONPATH=src python -m orion.study.p5 \
  --protected-suite /protected/p5-suite.json \
  --candidate-packet artifacts/p5-candidate-packet.json \
  --commitment artifacts/p5-protected-commitment.json
```

The command validates the private suite and emits only:

1. a **candidate packet** with visible symptom/context, motivating/replay task identities and allowed change surfaces; and
2. a **commitment manifest** binding the full private suite, evaluator, motivating/replay split, fresh split, negative variants, protected surfaces and rubrics without publishing the protected payloads.

The manifest publishes `task_id`, `changed_axes` and `variant_id` verbatim beside each commitment, and that is deliberate: a split nobody can check is not a split, and a fresh-transfer claim rests on the reader being able to see which axes moved. The cost of publishing them is that they are then bound by the same rule as `allowed_change_surface` — **no published field may be a function of the sealed root cause** (see *Published-field independence*). A generator that chose `changed_axes` per family would satisfy every other line of this document and put the answer key in the clear.

Before returning, `freeze_protected_suite` reads its own output back: `freeze.published_surface_leaks` searches the emitted packet and manifest for every sealed value of every case and fails the freeze closed on a hit. The split is therefore enforced by content and not only by which keys the emitter happens to write.

## Fail-closed conditions

Freeze is rejected if any of the following holds:

- one of the eight registered root-cause families is absent;
- a hidden root label has no 256-bit opening nonce, or its nonce is one a cheap enumeration finds (see *Low-entropy truth commitment* below);
- a declared fresh content hash does not match the evaluator-held payload;
- a fresh task changes only DATA/TOOL rather than at least one of TASK/DOMAIN/MODEL/ENVIRONMENT;
- motivating/replay task IDs overlap a fresh task ID;
- fresh or negative payloads are missing, duplicated or orphaned;
- an allowed candidate write surface is also a protected surface;
- the evaluator artifact hash is missing/invalid;
- the suite was not declared frozen before outcome access;
- the root-cause family is readable off the case ordinal (see *Ordinal independence* below);
- a case carries a field the custody rule classifies as neither published, published-as-identifier nor sealed;
- a field the freeze publishes names or determines the root-cause family (see *Published-field independence* below);
- one authorised opening of a case would open another of that case's commitments (see *One opening nonce per commitment kind* below);
- the emitted candidate packet or commitment manifest contains a sealed value.

## Ordinal independence

The case ordinal is published. It is the position of the case in the candidate packet, which `freeze_protected_suite` emits in sorted `case_id` order, and no commitment covers it. So if the root-cause family is a function of the ordinal, the commitments protect nothing: the candidate reads the answer key off the packet and never opens a case.

`PROTECTED_SUITE_V1` is that suite. Its twenty-four cases are the eight families in eight consecutive blocks of three, so `family = order[(ordinal - 1) // 3]` reproduces all twenty-four labels. Its nonces were separately broken and the freeze now refuses them; had they been sound, nothing in this document or in `validate_protected_suite` would have stopped it.

"Not recoverable from the ordinal" is not decidable — every assignment is *some* function of the ordinal — so the condition is shaped the way the rest of this programme shapes its guards: declare the adversary, then check that the suite defeats it. `freeze.ordinal_reading_rules` declares forty rules at twenty-four cases, each mapping an ordinal to a family using only the ordinal, the suite length and the eight public labels:

- four family orderings — alphabetical and first-appearance, each read forwards and backwards;
- for each ordering, every block size dividing the suite length up to half of it, and every stride coprime with the family count.

Each ordering is charged the openings it needs. Alphabetical order is free: the labels are a public enum. First-appearance order costs one opening per family, and those positions are excluded from scoring — without that exclusion the check is vacuous, because reading families off their own first appearances reproduces any assignment while predicting none of it.

A suite is rejected if any rule is right on **every case it was not shown**, and the rejection names the rule. On `PROTECTED_SUITE_V1`, `first-appearance/blocks-of-3` buys eight openings and gets the remaining sixteen right.

A second condition covers realised correlation rather than a stated rule: when every family appears the same number of times *k*, no aligned block of *k* consecutive ordinals may repeat a family. An adversary handed one opening inside such a block predicts the rest of it above chance, whatever drew the order. This rejects most honest uniform draws — eight families of three put two in a block about five times in six — and the remedy is to redraw, not to argue that a particular draw was innocent. `sound_hidden_cause_suite.assign_families` rejection-samples on exactly this predicate, so a generator cannot emit an assignment the validator would refuse.

Surviving these rules is not a proof of independence. It is a measurement against a declared adversary, and that is all it is claimed to be.

## Published-field independence

The ordinal is not the only published number the answer can be a function of. `allowed_change_surface` is on the publishable list, and in `PROTECTED_SUITE_V1` it names the answer: `src/retrieval/index.py` for `RETRIEVAL_MISS`, `src/causal/representation.py` for `REPRESENTATION_GAP`, `src/measurement/spec.py` for `MEASUREMENT_SPECIFICATION_GAP`. The manifest's `task_id`, `changed_axes` and `variant_id` are the same hazard one step removed. A field like that is a commitment that opens itself.

"Does this path name this family" is not decidable, so the condition is shaped like *Ordinal independence*: declare the reader, charge it for what it was told, and reject a suite it reads above what it was shown. `freeze.published_field_reading_rules` declares thirty-five readers, each using only the published surface and the eight public labels:

- **label-token** readers match the words of a published string against the words of a family's own label — exactly, or on a shared prefix of 4, 5 or 6 characters, which is what carries `metrics` to `METRIC` and `dependencies` to `DEPENDENCY`. One reader per published author-named field (`case_id`, `motivating_tasks`, `replay_tasks`, `allowed_change_surface`, `task_id`, `variant_id`) and one over all of them together. They are charged **nothing**, because `ROOT_CAUSES` is a public enum, so every case such a reader gets right is a case whose commitment protects nothing. A tie between two families abstains.
- **signature-leave-one-out** readers are told the family of every other case sharing a published field's exact value, and predict the case left out when those agree. This is the reader that would catch a family-dependent `changed_axes`. It abstains on a field constant across the suite (the cases it was told disagree) and on a field unique to each case (there is nothing to be told), and fires exactly when the published value partitions the suite along family lines.

`changed_axes` is read only by the second family. Its vocabulary is a fixed six-element public enum that overlaps the family enum by construction — `ENVIRONMENT` is both an axis and a family word — so a token reader over it would charge an author for using the axis this document tells them to use. What must not happen is that the *choice* of axes tracks the family.

A suite is rejected when any reader is right about any case it was not told, and the rejection names the reader and the count. On `PROTECTED_SUITE_V1` the readers disclose **12 of 24 cases and 7 of 8 families** with nothing opened: `label-token-prefix-4/all-published-fields` reads 12 of the 14 cases it predicts, `label-token-prefix-4/allowed_change_surface` alone reads 11 of 13, and `label-token-exact/allowed_change_surface` reads 6 of 7. `IMPLEMENTATION_BUG` is the one family no declared reader recovers; the number is reported rather than tuned until it is eight. The generated sound suite, whose surfaces are named after the case ordinal and never after the mechanism, discloses 0 of 24.

`visible_symptom` and `candidate_visible_context` are deliberately out of scope, and this is where the rule stops rather than where it is satisfied. A symptom is the one published field that *must* be informative about the hidden cause — a case whose symptom carried no signal would not be a case — so a token reader over it would reject every real suite and measure nothing. On `PROTECTED_SUITE_V1` that field is where the largest leak actually is (*"Retrieval system returns empty results…"*). How much a symptom may say is a case-authoring question, and the instrument for it is an identifiability audit over symptom content, which nothing here provides.

## One opening nonce per commitment kind

A freeze publishes seven kinds of commitment per case — the case artifact, the root cause, each fresh payload, each negative variant, the protected surface, and both rubrics — and every one of them used the case's single `root_cause_nonce`. That costs two different things, and only one of them is about entropy.

**Enumeration.** An adversary opens the cheapest kind, not the one the probes attack. The root-cause commitment's domain is eight public labels; the rubric payloads of `PROTECTED_SUITE_V1` are `SECRET_SUCCESS_RUBRIC_{ordinal}` and `SECRET_HARM_RUBRIC_{ordinal}`, a domain of one. `hidden_cause_custody.audit_commitment_kind_domains` declares a payload-candidate generator per kind and prices each against the nonce the cheapest declared probe finds. On `PROTECTED_SUITE_V1`: the 24 root-cause commitments cost **108 digests** — the custody audit's own number, re-derived from the other end — while the 24 harm-rubric commitments and the 24 success-rubric commitments each open in **24 digests, one apiece**, and 22 of 24 protected surfaces are reproduced by a template over the *published* `allowed_change_surface`. The cheapest kind is the price of the case: one digest per case rather than the four and a half the root-cause probe averages, and 24 for the suite against 108.

**Disclosure.** This cost is unconditional and no nonce entropy repairs it: opening one commitment means releasing the nonce that opens it, and a shared nonce releases the other six with it. A host that shows an auditor a harm rubric has disclosed the root cause.

The repair is a per-kind opening nonce, derived by domain separation from the one 256-bit secret the case already stores: `freeze.opening_nonce(case_nonce, kind=…)`. The protected-suite schema does not change — a case still stores one nonce — and the commitment manifest's *shape* does not change either. What moves is the digest value of six of the seven commitments a future freeze emits, and what an opening releases. No shipped artifact moves: `PROTECTED_SUITE_V1` cannot be frozen at all, and no commitment manifest is committed anywhere in this repository.

`freeze.require_opening_separation` checks it against the digests the freeze has just built rather than against the helper that built them: every commitment is re-derived under every other kind's opening nonce, and a match fails the freeze closed. Releasing one opening used to disclose all **7 of 7** commitments of its case; it now discloses **1 of 7**. The root cause is the declared exception and still discloses 7 of 7 — it is the answer, it is opened last, and making it the master opening is what lets the other six be opened without it. The stated cost of that exception is that a host cannot open the label while keeping a fresh payload sealed for reuse; deriving that one too would move the scheme this document publishes and the scheme model `hidden_cause_custody.FREEZE_CANARY` pins.

One thing the derivation cannot repair: `case_artifact_commitment` binds the whole case object, and the case object contains `root_cause_nonce`. An authorised opening of the case artifact therefore hands over the master secret and with it all seven commitments, whatever the derivation does. `freeze.require_opening_separation` does not see this — it models nonce derivation and assumes payloads are already known — and the repair would be to bind the case with its nonce removed, which changes what "binding the full private suite" means.

The derivation does **not** change the enumeration numbers above. An adversary who can guess the case nonce derives every kind's nonce from it. Per-kind nonces are a repair for authorised openings; the repair for guessing is `mint_root_cause_nonce()`.

## Low-entropy truth commitment

A raw SHA-256 of `protected_root_cause` would be unsafe because the label has only eight possible values and can be enumerated. The manifest therefore commits to `{protected_root_cause, nonce}`. The nonce remains only in protected custody until any authorized post-study opening.

The message space cannot be enlarged: the label the candidate must produce is one of eight registered families by definition, so testing any nonce guess costs at most eight digests forever. Every bit of protection the scheme has is therefore carried by the nonce, which makes the nonce a per-case salt in everything but name. Draw it from `orion.study.p5.freeze.mint_root_cause_nonce()` — 256 bits from the OS CSPRNG, one per case, released only at opening.

Requiring the nonce to be non-zero was not that requirement, and neither is requiring it to be numerically large: `f"{2**255 + ordinal:064x}"` is 64 hex characters, non-zero, unique per case, and 2^191 times above any magnitude floor, and it opens to the same single guess an ordinal does. `validate_protected_suite` therefore rejects the *shapes a declared cheap adversary generates*, not the values that look small:

- counters and ordinals up from zero, and counters run down from 2^256;
- constant padding — a run of 32 or more identical hex characters;
- a short alphabet — fewer than twelve distinct bytes in the 32;
- a repeated block, and the fixed placeholders a generator leaves behind;
- any SHA-256, truncated SHA-512 or canonical-JSON derivation of a field the manifest publishes beside the commitment (case id, case ordinal, visible symptom, suite id);
- one salt shared across the suite, or one salt with a per-case offset — nonces that agree in their first or last 16 hex characters are rejected, because opening either case then opens both.

`orion.study.p5.hidden_cause_custody` builds its disclosure probes from the same generators, so a nonce the freeze accepts is by construction one the declared adversary cannot enumerate, and a nonce a probe can reach is one the freeze refuses. Running `PYTHONPATH=src python -m orion.study.p5.hidden_cause_custody --suite <suite>` attacks the commitments a freeze of `<suite>` would publish and exits non-zero if any opens. Do that before the manifest is published, not after.

## The shipped suite is not a protected artifact

`evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json` does not satisfy the custody rule above and never did. It is a candidate-visible fixture, and the sealing of its root causes is void:

- it publishes `protected_root_cause`, `root_cause_nonce`, `success_rubric`, `harm_rubric` and `protected_surface` in plaintext, which the *Custody rule* section forbids;
- its nonces are the case ordinal, `0…01` through `0…018`, so the 24 commitments a freeze of it would publish open in 108 SHA-256 evaluations;
- its cases are emitted in eight consecutive blocks of three, so the label is the case ordinal divided by three whatever the nonce is;
- its `allowed_change_surface` names the family for 11 of its 24 cases and its published task ids for 10 more, so a reader that costs nothing recovers 12 cases and 7 of the 8 families without opening anything (*Published-field independence*);
- its rubric payloads are `SECRET_SUCCESS_RUBRIC_{ordinal}`, so the cheapest of its seven commitment kinds opens for all 24 cases in 24 digests, one apiece, where the root-cause probe spends 108 (*One opening nonce per commitment kind*).

The plaintext labels are the binding defect: a digest cannot withhold a value that is published beside it, so no nonce repairs this file. Redrawing its nonces now would also not repair it, for a reason that has nothing to do with entropy — the run has been scored, the answers are known, and a commitment issued by a party that already knows the answer is not a commitment. **This suite must not be re-sealed and must not be reused as a protected suite.** Re-establishing a prospective hidden-cause result requires new cases, authored under the custody rule, with CSPRNG nonces, emitted in an order independent of the family, and run before the labels are seen.

Nothing above changes the one number this suite produced. The 21/24 GLM-5.2 attribution score is reported throughout the manuscript as a descriptive diagnostic scored against locally visible gold labels (`sections/09-results-attribution.tex`, `sections/10-limitations.tex`), it is explicitly not offered as protected-evaluator evidence, and no published table or claim rests on the commitment scheme. What the defect voids is the word *protected* as applied to this file, not the diagnostic.

The failure record is `research/failures/2026-08-invertible-commitment-vacuous-custody/`.

## A suite the probes cannot open, and what it is not

The section above establishes that the shipped suite is not a protected artifact and cannot be made into one. That left the custody audit with nothing but a broken artifact to report on: the scheme was repaired, and no sound suite used it. `orion.study.p5.sound_hidden_cause_suite` builds one, under the *Custody rule* above, and attacks it with the instruments the shipped suite fails.

```bash
# the contrast: both artifacts, one instrument, the shipped suite's verdict
PYTHONPATH=src python -m orion.study.p5.sound_hidden_cause_suite

# the same demonstration attached to the custody audit itself
PYTHONPATH=src python -m orion.study.p5.hidden_cause_custody --contrast-sound-suite
```

Measured, on one 24-case draw:

| | shipped suite | sound suite |
| --- | --- | --- |
| `ordinal-nonce` | **24 / 24 opened**, 108 digests | 0 / 24, 192 digests |
| all seven disclosure probes | FAIL, `SECRET_DISCLOSED` | **PASS, `WITHHELD_UNDER_ENUMERATION`, 0 of 24 in 4 734 336 digests, none exhausting the 5 000 000 budget** |
| nonces `validate_protected_suite` refuses | 24 of 24 | 0 of 24 |
| families recovered by a competence-free cue | **8 of 8** at informedness 1.0 | **0 of 8**, on both fit splits |
| cases whose family a published field names | **12 of 24**, 7 of 8 families, 0 openings | **0 of 24**, same 35 readers |
| cheapest commitment kind to open | harm rubric, **24 digests for 24 cases** (root cause: 108) | nothing opens: 0 of 24 nonces are enumerable |
| commitments one authorised opening discloses | 7 of 7, every kind | 1 of 7 (root-cause opening: 7 of 7, by declaration) |

How the construction differs, and each difference is one of the three defects named above:

- **Opening nonces** are drawn per case from `mint_root_cause_nonce()`. Nothing else in the generator produces a nonce.
- **Families are assigned by a keyed shuffle** under a 256-bit CSPRNG seed drawn separately from every nonce, rejected and redrawn until no ordinal block repeats a family. The seed is **sealed**, not published: the permutation is a deterministic function of it, so a seed published beside the packet would make `family(ordinal)` computable from the manifest — the shipped defect reached by a longer route. Only `assignment_seed_commitment(seed)` is published, so an authorised opening can be checked to reproduce the order that was emitted.
- **The published surface is exactly the candidate packet and the commitment manifest.** The sealed half is held in process memory, is never serialised by the module, and is not committed anywhere. `sealed_material_in()` and `label_pairings_in()` search the published surface and the audit report for it; the tests require both to be empty, and require both to fire when a leak is injected.

### This grants no authority

It is an instrument demonstration and nothing else. The cases carry no authored symptom — a placeholder that says so occupies `visible_symptom` — because writing twenty-four diagnostically valid hidden-cause cases is the campaign lane's work, and inventing them here would manufacture a benchmark rather than demonstrate an instrument. **No hidden-cause campaign has been run against this suite.** It produces no attribution score, promotes no ORION-15 claim, closes no gate, and its report declares `grants_authority: NONE` and `is_scientific_result: false`. The manuscript's 21/24 is a measurement on the *shipped* suite and is unaffected in either direction. The audit's exit status stays the shipped suite's: a demonstration that a sound suite is buildable does not make a broken one less broken.

### Two limits of the identifiability instrument, and where this document runs out

The demonstration's roll-up is `CANNOT_CHECK`, not `PASS`, and the reason is in the instrument rather than in the suite. Both limits are recorded rather than repaired, because repairing either means redefining a cue whose `FAIL` on the shipped suite is the evidence the contrast rests on.

- `nonce-ordinal-block` reads `(int(nonce, 16) - 1) // 3`. Against 256-bit CSPRNG nonces every case has its own signature, the fitted rule abstains on every eval case, and informedness is undefined — which `audit_label_identifiability` reports as `NO_PROBE_SCORED` and `CANNOT_CHECK`. **No correctly salted suite can pass that audit.** Nothing was recovered; the probe was in no position to recover anything, and the instrument cannot tell those apart.
- `default_fit_case_ids` takes the first case of each family. For the block cue to be scoreable on every eval case those eight first occurrences must land in eight distinct ordinal blocks — and a family whose first occurrence is in the last block has all three of its cases there, because only three slots remain. Full coverage therefore *forces* a monofamily final block, which the block probe then recovers at informedness 1.0. Full coverage and a clean ordinal are mutually exclusive under that split, so the audit is also run against `block_covering_fit_case_ids()` — one authorised opening per ordinal block, all of distinct families, which is more than a sound freeze discloses to anybody — where the cue scores all sixteen eval cases and recovers none.

Six places where the custody rule above did not reach, found by trying to build a suite from it. All six are now fail-closed conditions or emission-time checks, recorded with their repair and their number in `sound_hidden_cause_suite.CUSTODY_RULE_GAPS_CLOSED`:

1. The withheld list and the publishable list were in different sections and neither said they were complements. → The three-way classification under *Custody rule*, enforced by `freeze.require_case_fields_classified`.
2. `competing_cause_set` was in neither list. → Sealed by name, and `freeze_protected_suite` now searches its own output for every sealed value. Its first element is the answer in 24 of 24 shipped cases: publishing it would have cut the domain to one.
3. `allowed_change_surface` names the answer in the shipped suite. → *Published-field independence*: 35 declared readers, 12 of 24 cases and 7 of 8 families disclosed on `PROTECTED_SUITE_V1`, 0 of 24 on the sound suite.
4. The emission order was in neither list. → *Ordinal independence*, the tenth condition.
5. The manifest publishes `task_id`, `changed_axes` and `variant_id` verbatim, defensibly and unstated. → Stated under *Freeze command*, enforced by the signature-leave-one-out readers; a suite whose axes are a function of the family is read 24 of 24 and refused.
6. One nonce per case was one nonce for seven commitment kinds. → *One opening nonce per commitment kind*: the cheapest kind measured at 24 digests against the root cause's 108, and one opening now discloses 1 of 7 commitments instead of 7 of 7.

Closing the third opened one that is still open, and it is recorded in `sound_hidden_cause_suite.CUSTODY_RULE_GAPS`: the published-field readers do not run over `visible_symptom` or `candidate_visible_context`, and on the shipped suite that is where the largest leak is. Nothing here measures how much a symptom may say.

## Authority boundary

The candidate artifact declares `empirical_authority = NONE`; the commitment declares `empirical_authority = CANNOT_CHECK`. A suite commitment proves only that protected inputs were bound prospectively. It cannot establish causal-attribution accuracy, transfer benefit, integrity benefit, or permission to merge/promote a candidate.

## Transition to execution freeze

After the real hidden-cause cases, fresh payloads and protected evaluator are created under this custody rule, the host must still bind the exact final subject revision, provider/model identities, baseline config hashes, split hashes and evaluation epoch in the publication execution manifest. Only then may `PROTOCOL_V1.json` be promoted from `DESIGN_FROZEN` to a fully bound `EXECUTION_FROZEN` state. Partial binding is not valid.
