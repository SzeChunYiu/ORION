# X1-B k=4 — 116 rank-3 completions collapse to three `GL(3,5)` forbidden-set classes

Parent: #900.
Input: all rank-3 zero-sum-free residual lifts.
Committed before ten-prefix existence tests for these classes.

## Canonicalization method

For each forbidden set S (containing 0 and spanning `F_5^3`), enumerate every ordered independent triple from `S\{0}`. For each triple, apply the unique invertible linear map sending it to the standard basis and serialize the transformed set lexicographically. The minimum serialization is a complete canonical form for linear equivalence: corresponding ordered bases transport under every `GL(3,5)` equivalence.

## Exact class collapse

All 116 rank-3 completions fall into exactly **three** canonical classes.

### Class R3-10 — 10 forbidden values

Multiplicity: **12 completions**
- `942777`: 8
- `1470123`: 4

Canonical set:

```text
(0,0,0)
(0,0,1) (0,0,2)
(0,1,0) (0,1,1)
(1,0,0) (1,0,1)
(1,4,1)
(2,4,4)
(4,1,2)
```

### Class R3-11 — 11 forbidden values

Multiplicity: **40 completions**
- `942777`: 16
- `1470123`: 24

Canonical set:

```text
(0,0,0)
(0,0,1) (0,0,2)
(0,1,0) (0,1,1) (0,4,3)
(1,0,0) (1,0,1)
(1,1,0) (1,1,4)
(1,2,2)
```

### Class R3-12 — 12 forbidden values

Multiplicity: **64 completions**
- `942777`: 32
- `1470123`: 32

Canonical set:

```text
(0,0,0)
(0,0,1) (0,0,2)
(0,1,0) (0,1,1) (0,2,3) (0,4,3)
(1,0,0) (1,0,1)
(1,1,0) (1,1,4)
(1,4,2)
```

## Consequence

For rank-3 bilinear completions, ten-prefix existence is invariant under invertible kernel-coordinate change. Therefore complete classification of all 116 rank-3 lifts reduces to **three exact forbidden-subset-sum extremal problems**.

The unique rank-2 completion remains a separate realization family because radical coordinates invisible to B can change its forbidden set.