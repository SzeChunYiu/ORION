# P1-U GPT-R3 — deterministic source-universe campaign

Parent: #649  
Campaign: #716  
Base: `main@8c6a2d56b0ddcea24667da97df4445df5c714dae`

## Why R3 exists

R2 reached `CANNOT_CHECK_ACQUISITION_COVERAGE`: the frozen first-eight, domain-specific web queries could not populate mandatory routes without stretching domain labels or scanning deeper than preregistered. No ORION/B3 held-out outcome was generated.

R3 changes only the acquisition object. The R2 candidate/comparator policy and decision rule remain frozen and donor-complete.

## Fresh held-out universe

Primary: sources published in calendar year **2022** only.  
Replication if primary passes: calendar year **2021** only.

All sources opened during R2 and every result from the single exploratory 2024 R3-development query are ineligible.

## Acquisition principle

Queries target scientific responsibility classes rather than disciplines. Actual scientific/workflow domain is assigned from source metadata/evidence after source selection and cannot be forced to match query wording.

For each frozen query:
1. execute it verbatim and individually;
2. inspect at most 50 ranked results;
3. scan in returned order;
4. log every skipped result and an objective disqualification reason;
5. admit the first qualifying, nonexcluded, source-disjoint primary/publisher/official record;
6. if none qualifies, record `NO_QUALIFYING_SOURCE` for that query;
7. never run ORION or B3 until all forty query dispositions are frozen.

A query can legitimately produce no case. Corpus admissibility is determined only after all query dispositions are frozen.

## Qualification

A case must:
- be a distinct 2022 scientific/workflow episode;
- have a publicly auditable tension/failure/control visible before resolution;
- have source evidence sufficient to encode all six generic probe outcomes as SUPPORT/REFUTE/INCONCLUSIVE;
- have source evidence for the evaluator disposition or for genuine non-identifiability;
- not require private author intent;
- not be an R2/development-excluded source;
- be independent of already admitted source identities.

## Frozen corpus quotas

After all forty query dispositions are frozen, the admitted primary corpus must have:
- at least 35 distinct episodes;
- at least five actual scientific/workflow domains;
- at least four cases for each substantive class: SEARCH_OR_EVIDENCE, REPRESENTATION_OR_INTERFACE, IMPLEMENTATION_OR_ENVIRONMENT, MEASUREMENT_OR_EVALUATOR, OBJECTIVE_OR_MODEL_CLASS, PROBLEM_BOUNDARY;
- at least four NO_HIGH_LEVEL_REFORMULATION controls;
- at least four UNRESOLVED cases.

Failure of any quota is `CANNOT_CHECK_SOURCE_UNIVERSE`; no extra query may be added after acquisition begins.

## Candidate/comparator

R3 imports the byte-frozen R2 policy from `research/claim_expansion/p1/gpt_r2/policy.py`.

Primary comparator: `B3_HORIZON2_DONOR_COMPLETE`.
Candidate: `ORION_R2` responsibility-ordered ARD.
Full-information ideal product remains analysis ceiling only.

No source-specific tuning, keyword changes, likelihood changes, budget changes, or policy edits are allowed.

## Decision rule

Reuse R2 unchanged:
- paired GRS gain >= +0.10;
- paired-bootstrap 95% stability lower bound > 0;
- every actual domain ORION-B3 >= -0.10;
- unnecessary high-level reformulation <= B3 and <= 0.05 absolute;
- zero harmful lower-level skips;
- zero false resolution of gold UNRESOLVED;
- zero evaluator/source/gold leakage.

If primary passes, freeze a 2021 disjoint-source replication using an independently implemented scorer and direct reconstruction before #649 may close.

## No-outcome mutation boundary

Once the query plan and R3 evaluator tests are green, acquisition begins. From that point:
- query text/order/scan limit cannot change;
- R2 policy/protocol cannot change;
- R3 evaluator/quota/decision rule cannot change;
- sources/cases cannot be dropped based on policy outcomes;
- ORION/B3 cannot be executed until acquisition is sealed.
