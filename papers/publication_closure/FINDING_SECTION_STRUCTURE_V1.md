# Section structure: two real findings, and a scan that mostly lied

The requirement is that every paper share a folder structure with each section in its own `.tex` file.

## The scan that did not work

A keyword scan for canonical section names (`abstract`, `introduction`, `related`, `method`, `result`, `discussion`, `limitation`, `conclusion`) flagged **13 of 21 papers** as missing at least one. Almost all of that is false.

- ORION-14 was reported missing `discussion`. It has `06-threat-model-limitations-and-interpretation.tex` and `11-ablation-interpretation.tex`.
- ORION-21 was reported missing `result`. It has `04-dense-controlled-studies.tex` and `08-limitations-discussion-conclusion.tex`.
- ORION-22 was reported missing `method`. It has `04-protected-benchmark.tex` and `06-accounting-and-statistics.tex`.

Papers name sections for what they contain. A theory paper's argument section is not called "Methods", and demanding the word is a template check wearing the costume of a completeness check. The scan's output is not usable as a defect list.

## Finding 1: ORION-25 is monolithic

`papers/orion-25-*/manuscript/` contains a `main.tex` and **zero section files**. Every other paper with LaTeX source splits into 8 to 17 sections. This is the one genuine violation of the shared-structure requirement, and it is the only paper where the keyword scan's alarm was real.

## Finding 2: ORION-12's section files are inconsistently named

Every other paper uses ordered numeric prefixes (`01-introduction.tex`, `02-related-work.tex`). ORION-12 uses:

```
acquisition_authority.tex
acquisition_authority-envelope.tex
formalism.tex
methods.tex
results.tex
availability.tex
structure-conditioned-discovery-interface.tex
05a-public-screening-transport.tex
p2x_unresolved_route_successor.tex
```

Mixed conventions: underscores and hyphens, one numeric prefix among eight unprefixed names, and no reading order. **`p2x_unresolved_route_successor.tex` carries an internal programme code in the filename itself** --- a class of leak not covered by any content audit here, since those read file contents rather than names.

A submitted `.tex` bundle exposes its filenames to reviewers, so this matters for venues that take source.

## Not done

Renaming section files requires updating every `\input{}` and re-binding digests, and for ORION-12 also rebuilding its journal package. That is mechanical but not trivial, and it was not attempted in the same pass as an audit whose primary output turned out to be noise.
