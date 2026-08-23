# X1-B k=4 — complete rank-2 radical census collapses to two new forbidden-set classes

Parent: #900.
Frozen protocol: `X1B_K4_RANK2_RADICAL_MINIMAL_FORBIDDEN_PROTOCOL.md`.
Normalization: `X1B_K4_RANK2_RADICAL_NORMALIZATION_2026-08-22.md`.
Committed before ten-prefix testing of the final two classes.

## Complete normalized enumeration

Each surviving quotient orbit has exactly

`12,207,032`

shear/scaling-normalized radical assignments.

### Quotient orbit `942777`

- normalized assignments processed: `12,207,032`
- distinct forbidden signatures: **6,620**
- inclusion-minimal signatures: **574**
- SHA-256 of the sorted distinct 64-bit signature stream:
  `3594959ad720f599d31404e16821e49cf7e026a895ecd7cdb3ae30f57fa57f7e`
- SHA-256 of the sorted inclusion-minimal signature stream:
  `4e3533064ee7e92aee66a6a284c1a6896780465971d31398cbe75effae09e39d`

Distinct forbidden-set size histogram:

```text
7:1 10:2 11:2 12:3 13:7 14:21 15:68 16:89 17:184 18:308
19:531 20:965 21:1464 22:1342 23:879 24:499 25:200 26:50 27:5
```

### Quotient orbit `1470123`

- normalized assignments processed: `12,207,032`
- distinct forbidden signatures: **5,776**
- inclusion-minimal signatures: **597**
- SHA-256 of the sorted distinct signature stream:
  `cd2cc897b0b16c454841b9d7547b0688727810e6da85a035c3f392bac69e1557`
- SHA-256 of the sorted inclusion-minimal stream:
  `aacdb428225eda22ed263f5dda1a65792704a68b1527996a57485c340dec5def`

Distinct forbidden-set size histogram:

```text
7:1 10:1 11:4 12:2 13:2 14:25 15:61 16:93 17:122 18:337
19:479 20:894 21:1304 22:1074 23:752 24:386 25:184 26:50 27:5
```

## Union and inclusion-minimal reduction

Across both quotient orbits:

- distinct signatures in the union: **8,984**
- inclusion-minimal signatures in the union: **639**

An exact `GL(3,5)` canonicalization of those 639 minima gives 216 linear-equivalence classes before using already-closed subconfigurations.

## Containment in previously closed forbidden patterns

For each inclusion-minimal radical forbidden set S, test exact linear containment of the four independently closed patterns:

1. the seven-point planar `S_bad`;
2. R3-10;
3. R3-11;
4. R3-12.

Containment is tested without heuristic canonicalization: fix a basis of the smaller pattern, enumerate every independent image basis in S, and check exact image-set inclusion.

Using first-match accounting:

- **418** minima contain a linear image of the seven-point planar obstruction;
- **218** additional minima contain a linear image of R3-10;
- **0** additional minima require R3-11;
- **0** additional minima require R3-12;
- only **3** raw minima remain uncovered.

Thus **636/639 inclusion-minimal radical forbidden signatures are already NO** by monotonicity from independently confirmed earlier prefix theorems.

## Three raw uncovered minima

### Raw minimum A — size 11

Signature: `0x485216a1`

Representative normalized radical assignment (orbit `1470123`):

`r=(0,0,0,1,1,0,0,1,1,4,4,1,1)`.

Point set:

```text
(0,0,0)
(0,1,0) (0,1,2) (0,1,4)
(0,3,0) (0,3,2)
(2,1,2)
(2,3,0) (2,3,2)
(3,1,2)
(4,0,0)
```

### Raw minimum B — size 11

Signature: `0xa09096a1`

Representative normalized radical assignment (orbit `942777`):

`r=(0,0,0,1,1,1,1,2,2,4,4,3,3)`.

Point set:

```text
(0,0,0)
(0,1,0) (0,1,2) (0,1,4)
(0,3,0) (0,3,2)
(2,1,0)
(2,3,0) (2,3,3)
(3,1,4)
(4,0,1)
```

Exact `GL(3,5)` canonicalization shows A and B are linearly equivalent. Their common canonical serialization is

`(0,1,2,5,6,10,25,26,46,65,111)`.

Hence they form **one** new 11-point class, called R2R-11.

### Raw minimum C — size 12

Signature: `0x104a516a1`

Representative normalized radical assignment (orbit `942777`):

`r=(0,0,0,1,1,2,2,3,3,3,3,2,0)`.

Point set:

```text
(0,0,0)
(0,1,0) (0,1,2) (0,1,4)
(0,3,0) (0,3,2)
(2,1,1) (2,1,3)
(2,3,1) (2,3,3)
(3,1,1)
(4,0,2)
```

This is not linearly equivalent to R2R-11. Its canonical serialization is

`(0,1,2,5,6,10,25,26,30,34,53,107)`.

Call this class **R2R-12**.

## Strong reduction

The entire rank-2 radical realization family is therefore reduced to exactly **two genuinely new ten-prefix problems**:

- R2R-11;
- R2R-12.

If both are NO, every one of the 24,414,064 normalized radical realizations is eliminated, and the complete rank-2 radical branch of k=4 closes.

## Authority boundary

This packet is a complete finite reduction, not yet a C15 theorem. The two final prefix problems are prospectively untouched at this point and must be frozen/tested before k=4 closure.