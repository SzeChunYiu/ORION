# Paper Card — Instance Space Analysis for Algorithm Testing

**Source mode:** primary ACM full HTML/metadata record with substantial article text available.  
**Context mode:** externally verified conceptual-parent check.  
**Checked:** 2026-08-21.

## 01. Bibliographic position
Kate Smith-Miles, Mario Andrés Muñoz. **Instance Space Analysis for Algorithm Testing: Methodology and Software Tools.** *ACM Computing Surveys* 55(12), Article 255, 1–31 (2023). DOI `10.1145/3572895`.

## 02. Research question
How can algorithm testing move beyond average benchmark performance to understand how structural instance properties determine algorithm strengths, weaknesses, applicability and robustness?

## 03. Background route
The paper explicitly extends Rice's 1976 Algorithm Selection Problem by representing instances through features, building an interpretable instance space, learning performance footprints and using them for algorithm testing/selection.

## 04. Prior-work / field context
ISA is mature methodology rather than a single application. It includes feature selection, 2-D projection, theoretical/experimental boundary construction, algorithm footprints, machine-learning prediction, benchmark-diversity assessment and iterative generation of missing instances/features.

## 05. Pain point
Average performance over a benchmark can hide regional strengths/weaknesses and benchmark bias. Trust in algorithm conclusions depends on whether test instances cover relevant structural regions.

## 06. Core insight
Construct a feature-conditioned instance space in which algorithm performance footprints and gaps become visible, then iterate the metadata/instance/feature set until the representation is informative.

## 07. Method / module logic
The article describes six core ISA stages: collect feature/performance metadata; construct the instance space; train performance/selection models; generate footprints/metrics; analyze sufficiency/bias; add instances/features/algorithms if needed and repeat.

It names PRELIM, SIFTED, PILOT and CLOISTER as core construction methods.

## 08. Essential formulas
Full formulas exist in the source, but ORION-09 does not need to reproduce ISA mathematics. The key conceptual variables are instance features `F`, algorithm performance `Y`, projected coordinates and good-performance footprints.

## 09. Experiment-to-claim evidence
The tutorial presents a timetabling case study and describes multi-domain use. The article's claim is methodological: ISA reveals structural performance relationships and benchmark gaps that averages can hide.

## 10. Main conclusions
ISA supports objective algorithm testing, scrutiny of benchmark diversity, automated algorithm selection and generation of additional instances/features where the current space is insufficient.

## 11. Conclusion boundaries
ISA already owns broad claims that:
- instance structure affects algorithm performance;
- feature spaces can reveal regions/footprints of algorithm strength;
- feature insufficiency can motivate adding features;
- benchmark gaps can be filled by generating instances.

ORION-09 may not present those ideas as new simply because its application is quantum compilation.

## 12. Author-stated limitations
The article emphasizes that insight quality depends on metadata quality, instance diversity and whether selected features adequately capture performance variation. It explicitly discusses adding features when predictions remain contradictory.

## 13. Critical analysis
This paper is a **stronger novelty threat to ORION-09 than a generic quantum-compilation paper** because ORION-09's vocabulary of “regions,” “structural predicates” and “feature failure” overlaps conceptually with ISA. ORION-09 survives only if it clearly identifies additional exact compiler objects: feasible transformation witnesses, theorem/tightness authority, proof-derived versus intrinsic support, objective certificate cones and exact mixed-cell representation refutations.

## 14. Learned knowledge
ISA itself treats feature insufficiency as a meaningful diagnostic and iteratively augments features. Therefore QG15c-style vocabulary enlargement is not novel in the generic sense. The potentially new part is an exact compiler setting where mixed cells prove **zero error impossible within the frozen vocabulary**, combined with exact compiler witness/theorem structure.

## 15. Knowledge connections
Rice algorithm selection; algorithm portfolios; benchmark design; automated feature selection; active instance generation; QG regime maps and StabPrep mixed-cell diagnosis.

## 16. Testable research ideas
- Compare QG exact regime labels with conventional ISA projections to test what explanatory information is lost by 2-D footprints.
- Use QG exact counterexample generators as targeted instance-space fillers.
- Study whether theorem-derived structural coordinates improve ISA boundary determination in compiler families.

## ORION claim effect
**Mandatory parent status:** ISA must be named as ORION-09's primary conceptual ancestor.  
**Claims removed from ORION-09 novelty:** generic feature→performance mapping, algorithm footprints, benchmark-gap discovery, and feature augmentation.  
**Residual preserved:** exact/witness-carrying compiler expressivity, theorem/tightness separation, objective certificate regions, and frozen-vocabulary impossibility results.
