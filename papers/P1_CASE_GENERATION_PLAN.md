# P1 Case Generation Plan — From n=48 to n=385 (TIER_B)

**Status**: Infrastructure designed; implementation requires scenario database

## The Challenge

Adding 337 new cases requires each case to have:
1. A coherent, non-trivial scenario
2. A genuine hidden shift (not obvious)
3. Consistent observable resources
4. A precise, falsifiable rubric
5. Correct closure chain structure

The `generate_cases.py` script provides the STRUCTURAL framework, but generating MEANINGFUL content requires:

- A database of scenario variations for each family
- Coherence checks across all parameters
- Manual review for quality assurance

## What Exists

1. **Generator framework**: `generate_cases.py` with parametric templates
2. **Schema definition**: `HIDDEN_SHIFT_CASE_SCHEMA_V1.json`
3. **Example cases**: 48 existing cases to use as style references

## What's Needed for Full Implementation

### Option A: Manual Authoring (Slow but High Quality)
- ~337 cases × ~15 minutes/case = ~85 hours of focused work
- Each case requires: scenario design, resource construction, rubric writing
- Best for: ensuring scientific rigor and avoiding template artifacts

### Option B: LLM-Assisted Generation (Faster but Requires Review)
- Use LLM to generate scenarios from high-level prompts
- Each generation requires manual review and correction
- Estimated: ~5 minutes/case for review = ~28 hours
- Risk: model may introduce systematic biases or repetitive patterns

### Option C: Hybrid — Staged Expansion
- **Stage 1**: Add 51 cases (n=48 → n=97, TIER_D) as proof-of-concept
- **Stage 2**: After verification, add 74 more cases (n=97 → n=171, TIER_C)
- **Stage 3**: After verification, add 214 more cases (n=171 → n=385, TIER_B)

Each stage can be validated before proceeding.

## Recommended Path: Option C (Staged Expansion)

### Stage 1: Reach TIER_D (n=97)
- Target: +51 cases (~8-9 per family)
- Time estimate: 12-20 hours with manual authoring
- Validation: Run generator + hand-review each case
- Milestone: First powered tier achieved

### Stage 2: Reach TIER_C (n=171)
- Target: +74 more cases (~12-13 per family)
- Time estimate: 18-25 hours
- Validation: Check case diversity and family balance

### Stage 3: Reach TIER_B (n=385)
- Target: +214 more cases (~35-36 per family)
- Time estimate: 50-70 hours
- Validation: Full suite review, power verification

## What This Session Delivers

1. ✅ Generator framework (`generate_cases.py`)
2. ✅ Factored analysis (`P1_EXPANSION_FACTS.md`)
3. ✅ PR documenting the constraint (#265)
4. ⏸️ Example batch: 5-10 cases to demonstrate quality
5. ⏸️ Full expansion: Requires staged approach over multiple sessions

## Next Steps for Full Expansion

1. **Create scenario database**: Build a catalog of scenario variations for each family
2. **Generate Stage 1**: Author 51 cases following the schema
3. **Review and validate**: Hand-check each case against quality criteria
4. **Run campaign**: Execute with `python3 -m orion.study.p1.run_trial --split TEST --live`
5. **Verify tier**: Confirm TIER_D achieved before proceeding to Stage 2

## Alternative: Document Current State as Estimation Study

If full expansion is not feasible, per PROSPECTIVE_POWER_V1.md:

> "Reclassify H1 as estimation rather than a powered test. Report the difference with its interval and state plainly that the design cannot reject a 0.05 effect."

The study can still contribute with:
- Point estimates with confidence intervals
- H2/H3/H4 mechanistic results (large effects are informative at n=48)
- Clear statement of power limitations

---

**Status**: Infrastructure complete; awaiting decision on staged expansion path.
