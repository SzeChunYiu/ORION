# ORION-P5 protected hidden-cause suite freeze V1

This procedure is the host-side bridge between the design-frozen protocol and a later `EXECUTION_FROZEN` run. It does **not** publish a hidden-cause benchmark into the repository and it does **not** produce empirical evidence.

## Custody rule

The protected input is held outside challenger write authority. It contains:

- all eight protected root-cause labels;
- a unique 256-bit opening nonce per case;
- full fresh-task payloads;
- protected evaluator artifact hash;
- protected surfaces and scoring/harm rubrics;
- every declared negative/null/harmful variant payload.

Do not commit that input, its opening nonces, fresh payloads, evaluator internals, or protected rubrics to a candidate-readable branch.

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
- the root-cause family is readable off the case ordinal (see *Ordinal independence* below).

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
- its cases are emitted in eight consecutive blocks of three, so the label is the case ordinal divided by three whatever the nonce is.

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

How the construction differs, and each difference is one of the three defects named above:

- **Opening nonces** are drawn per case from `mint_root_cause_nonce()`. Nothing else in the generator produces a nonce.
- **Families are assigned by a keyed shuffle** under a 256-bit CSPRNG seed drawn separately from every nonce, rejected and redrawn until no ordinal block repeats a family. The seed is **sealed**, not published: the permutation is a deterministic function of it, so a seed published beside the packet would make `family(ordinal)` computable from the manifest — the shipped defect reached by a longer route. Only `assignment_seed_commitment(seed)` is published, so an authorised opening can be checked to reproduce the order that was emitted.
- **The published surface is exactly the candidate packet and the commitment manifest.** The sealed half is held in process memory, is never serialised by the module, and is not committed anywhere. `sealed_material_in()` and `label_pairings_in()` search the published surface and the audit report for it; the tests require both to be empty, and require both to fire when a leak is injected.

### This grants no authority

It is an instrument demonstration and nothing else. The cases carry no authored symptom — a placeholder that says so occupies `visible_symptom` — because writing twenty-four diagnostically valid hidden-cause cases is the campaign lane's work, and inventing them here would manufacture a benchmark rather than demonstrate an instrument. **No hidden-cause campaign has been run against this suite.** It produces no attribution score, promotes no P5 claim, closes no gate, and its report declares `grants_authority: NONE` and `is_scientific_result: false`. The manuscript's 21/24 is a measurement on the *shipped* suite and is unaffected in either direction. The audit's exit status stays the shipped suite's: a demonstration that a sound suite is buildable does not make a broken one less broken.

### Two limits of the identifiability instrument, and where this document runs out

The demonstration's roll-up is `CANNOT_CHECK`, not `PASS`, and the reason is in the instrument rather than in the suite. Both limits are recorded rather than repaired, because repairing either means redefining a cue whose `FAIL` on the shipped suite is the evidence the contrast rests on.

- `nonce-ordinal-block` reads `(int(nonce, 16) - 1) // 3`. Against 256-bit CSPRNG nonces every case has its own signature, the fitted rule abstains on every eval case, and informedness is undefined — which `audit_label_identifiability` reports as `NO_PROBE_SCORED` and `CANNOT_CHECK`. **No correctly salted suite can pass that audit.** Nothing was recovered; the probe was in no position to recover anything, and the instrument cannot tell those apart.
- `default_fit_case_ids` takes the first case of each family. For the block cue to be scoreable on every eval case those eight first occurrences must land in eight distinct ordinal blocks — and a family whose first occurrence is in the last block has all three of its cases there, because only three slots remain. Full coverage therefore *forces* a monofamily final block, which the block probe then recovers at informedness 1.0. Full coverage and a clean ordinal are mutually exclusive under that split, so the audit is also run against `block_covering_fit_case_ids()` — one authorised opening per ordinal block, all of distinct families, which is more than a sound freeze discloses to anybody — where the cue scores all sixteen eval cases and recovers none.

Six places where the custody rule above did not reach, found by trying to build a suite from it. The largest — the emission order — is now the tenth fail-closed condition above and is recorded in `sound_hidden_cause_suite.CUSTODY_RULE_GAPS_CLOSED`. Five remain open, in `sound_hidden_cause_suite.CUSTODY_RULE_GAPS`:

1. The withheld list is under *Custody rule* and the publishable list under *Freeze command*; neither says the two are complements. The only place the split is stated as one rule is `freeze_protected_suite` itself.
2. `competing_cause_set` is in neither list. It names two or three candidates including the answer, so a freeze that published it would cut the commitment's domain from eight to three while breaking no stated rule.
3. `allowed_change_surface` is on the publishable list, and in the shipped suite it names the answer: `src/retrieval/index.py` for `RETRIEVAL_MISS`, `src/causal/representation.py` for `REPRESENTATION_GAP`, `src/measurement/spec.py` for `MEASUREMENT_SPECIFICATION_GAP`. Neither the freeze nor the custody audit looks at it.
4. The manifest is described as binding the fresh split "without publishing the protected payloads", and it does publish `task_id`, `changed_axes` and `variant_id` verbatim. Defensible, and unstated: a generator that made `changed_axes` depend on the family would put the label in the clear while following the text.
5. One nonce per case is reused across seven commitment kinds — case artifact, root cause, each fresh payload, each negative variant, the protected surface and both rubrics. The seven disclosure probes attack only the root-cause commitment, so whichever of the other six has the smallest guessable domain is the real cost of opening a case, and nothing measures it.

## Authority boundary

The candidate artifact declares `empirical_authority = NONE`; the commitment declares `empirical_authority = CANNOT_CHECK`. A suite commitment proves only that protected inputs were bound prospectively. It cannot establish causal-attribution accuracy, transfer benefit, integrity benefit, or permission to merge/promote a candidate.

## Transition to execution freeze

After the real hidden-cause cases, fresh payloads and protected evaluator are created under this custody rule, the host must still bind the exact final subject revision, provider/model identities, baseline config hashes, split hashes and evaluation epoch in the publication execution manifest. Only then may `PROTOCOL_V1.json` be promoted from `DESIGN_FROZEN` to a fully bound `EXECUTION_FROZEN` state. Partial binding is not valid.
