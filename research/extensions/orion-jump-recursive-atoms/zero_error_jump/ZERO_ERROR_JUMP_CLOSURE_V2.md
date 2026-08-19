# Zero-error Jump benchmark closure V2

Date: 2026-08-19  
Issue: #501  
Supersedes: `ZERO_ERROR_JUMP_CLOSURE_V1.md`

## Candidate terminal

`REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE`

V1 is retained as research history but is **not an operative benchmark closure**. PR #558 review found a real pre-experiment leakage failure: `public_tension_kind` encoded the protected family, and menu operation kinds differed between positive/control cases. The protocol was therefore reopened rather than patched in place.

A pre-implementation V2 side-channel audit then found additional protected-class leakage in V1/V2-draft structure: P/C case-ID markers, different old-language public list sizes, and public cardinality differences in correspondence/validation fields. V2 removes those too.

The scientific hypothesis and terminal remain unchanged, but only V2 may supply evidence for them.

---

## 1. V2 pre-experiment public view

Candidate-visible cases no longer expose a family/tension class.

Every case has exactly the same public shape:

- opaque case ID with no positive/control or family marker;
- 3 opaque objects;
- 2 opaque relations;
- 4 public observations;
- exactly matching incumbent public predictions;
- 8 old-language public hypotheses;
- 2 opaque open-discriminator IDs;
- 2 equal-cost probe options;
- 2 correspondence obligations;
- 2 public validation interfaces;
- the same representation move library.

Both probe options use exactly:

`operation_kind = REGISTERED_PROBE`

One probe covers all two opaque open-discriminator IDs; the other covers none. The candidate chooses the unique maximum-overlap probe. This makes **experiment relevance** visible without exposing whether the outcome will support a representation change or an old-regime repair/solution.

The public object has no `family_id`, `is_jump_case`, `public_tension_kind`, gold move, protected full contract, protected consequence or old-language gold solution.

---

## 2. Evidence appears only after the registered probe

The selected probe outcome is the first candidate-visible event allowed to distinguish the structural response class.

Positive outcomes have an opaque structural evidence code `E0..E5`, each corresponding to one registered move class. Control outcomes use:

`pattern:OLD_SUFFICIENT:<opaque>`

and do not embed the control-family identity.

This is intentionally not cryptographic secrecy. It is a controlled process boundary: pre-experiment declared public fields are class-balanced and do not encode the protected benchmark label. A malicious reader of a public repository can still inspect implementation files, so this benchmark cannot claim secret test-set security.

---

## 3. Fixed-representation comparator fairness was also repaired

V1 fixed-representation arms used evaluator-side case state when deciding whether to keep the old regime or remain unresolved. V2 removes that shortcut.

`OLD_DSL_EXHAUSTIVE`, `M_OPEN_SAME_REPRESENTATION`, and `FIXED_REP_WORLD_MODEL` now:

1. receive the same public case as the strong parent and ORION;
2. select the same registered probe by public discriminator overlap;
3. consume its outcome;
4. keep the old regime when the outcome states old-regime sufficiency;
5. return `UNRESOLVED_REPRESENTATION_CEILING` when the outcome supports a representation move they are not permitted to execute.

They therefore use the registered evidence but retain their action-space limitation.

This changes their V2 `thought_experiment_success` bookkeeping to 24/24 positive probes per split while leaving positive Jump success at zero.

---

## 4. Exact old-language representation ceiling remains evaluator-side

Every V2 world has exactly 8 old-language hypotheses, all matching the public zero-error observation signature.

- Positive case: zero of the 8 satisfy the protected full contract.
- Control: at least one satisfies the full contract.
- `SEARCH_HARD_BUT_EXPRESSIBLE`: the valid old-language solution is deliberately placed last.

Thus registered representation insufficiency is still proven by exhaustive finite enumeration, not inferred from failed search.

The exact proof is evaluator-side and does not become a candidate-visible positive/control flag.

---

## 5. Strong-parent comparison remains fully matched

`VERIFIED_REGIME_REVISION_PARENT` and `ORION_JUMP` receive identical:

- public case bytes;
- probe menu and one-probe budget;
- representation move library;
- one-proposal budget;
- correspondence obligations;
- validation interfaces.

Both policies choose the probe through the same public relevance information, observe the same outcome, and are allowed the same representation move.

The V2 protected expectation remains, per split:

- 42/42 structurally correct;
- 24/24 positive regime transitions;
- 18/18 no-Jump controls;
- zero false Jumps;
- 24/24 exact old-regime-insufficiency recognitions;
- 24/24 correspondence successes;
- 24/24 protected consequence successes;
- 24/24 informative probes;
- zero authority violations.

Their complete decision vectors and metrics must be identical on both primary and replication. Frozen ORION incremental gap remains zero.

---

## 6. Hard controls remain load-bearing

### No correspondence

`ORION_NO_CORRESPONDENCE` may consume the correct probe, choose the correct move, and derive the expected consequence token. It still gets zero positive Jump successes because the correspondence/preservation gate is incomplete.

### Always Jump

`OVERJUMP_ALWAYS` requests a bridge representation on every case. It false-jumps on all 18 controls and only accidentally has the correct move on the four bridge-family positives. The other 20 positive proposals are rejected.

### Fixed representation

The three fixed/same-representation arms can consume the evidence and recognize a ceiling but cannot cross the registered representation type. They therefore remain correct on all 18 controls and unresolved on all 24 positives.

---

## 7. Primary + disjoint replication

Seeds remain unchanged from the original pre-outcome design:

- primary `202608190501`;
- replication `202608190502`.

Each split has 42 worlds = 24 positives + 18 controls. V2 case IDs, objects, relations and consequence tokens are seed-derived opaque values; the two split identity sets are disjoint.

The parent-vs-ORION terminal must agree across both splits.

---

## 8. Independent implementation-path reconstruction

V2 has a separately versioned verifier:

`zero_error_jump_independent_v2.py`.

It regenerates the V2 worlds, executes policies, and independently reconstructs:

- exact old-regime insufficiency counts;
- every protected arm metric;
- parent-vs-ORION decision equality;
- parent-vs-ORION metric equality;
- final terminal.

It does not call/import the main V2 `score_split()` or main aggregate report builder.

This remains implementation-path independence, not external human or laboratory replication.

---

## 9. V2 post-freeze saturation was reset

V1 saturation is not reused as closure evidence after the material leakage reopen.

### V2 Round 1 — contamination / search-time leakage

Recent benchmark research explicitly pressures public benchmark contamination and search-time recovery of benchmark metadata/context. V2 maps this to its opaque, class-balanced pre-experiment public projection and controlled non-cryptographic scope. No new candidate field or success gate was required.

Result: `NO_MATERIAL_CHANGE`.

### V2 Round 2 — strongest scientific-discovery parents

Mechanistic world models, M-open model discovery, verified self-revising representation systems, and representation-grounded abduction map to the existing fixed-representation, M-open, and fully resourced verified-regime-revision comparator slots.

No stronger matched comparator or new success gate was required.

Result: `NO_MATERIAL_CHANGE`.

---

## 10. Operative closure rule

Only V2 may earn #501's bounded terminal.

Close #501 at:

`REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE`

only after:

- V2 exact-head tests pass;
- V2 independent reconstruction matches;
- no new unresolved review leakage/fairness finding remains;
- #539 and its dependencies integrate first;
- #558 is retargeted/rechecked on fresh `main`;
- required repository CI and candidate CI are green.

The V2 result, if green, means the finite benchmark demonstrates a registered representation ceiling and validated regime transition, while the strongest verified regime-revision parent still matches ORION exactly. It does not establish open-ended scientific creativity or ORION-specific Jump novelty.
