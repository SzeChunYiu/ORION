# ORION bounded frontier experiment — generalized Davenport constants of `C_7^3`

Status: **ACTIVE / A7 refuted; B7 one-split neighbourhood closed**  
Branch: `shadow/c7-davenport-frontier-20260903-sol`  
Scope: isolated domain-neutral ORION research-harness experiment; this does **not** alter the scope-locked `ORION-frontier-problems` programme.

## Research panel

The experiment separates three responsibilities.

- **Zero-sum theory:** choose implications that actually bear on generalized Davenport constants and keep donor results attributed.
- **Finite geometry / construction:** exploit the geometry of `C_p^3` to construct or exclude extremal sequences rather than launch an unstructured search.
- **Exact-computation / ORION control:** freeze atomic claims, run independent exact predicates and hostile controls, retain negative results, and keep scientific authority narrower than execution evidence.

## Frozen atom A7

Let `short` mean length at most `exp(C_7^3)=7`.  Freeze the bidirectional gate

> **A7.** Does there exist a zero-sum sequence `S` over `C_7^3` with `|S|=44` and no nonempty short zero-sum subsequence?

This is the direct analogue of the length-31 obstruction eliminated in ORION-04 for `C_5^3`.  A `NO` would have supplied a strong new short-zero theorem; a `YES` proves that the ORION-04 reduction cannot simply be transported from `p=5` to `p=7`.

**Disposition: YES, by an explicit exact witness.**

## Donor-owned construction and derived witness

The donor is

Y. Edel, C. Elsholtz, A. Geroldinger, S. Kubertin, L. Rackham, *Zero-sum problems in finite abelian groups and affine caps*, Quarterly Journal of Mathematics 58 (2007), 159–186, DOI `10.1093/qmath/ham003`.

Its Lemma 3.4 gives, for every odd `n>=3`, the nine support points

```text
(1,0,0) (1,0,2) (1,2,0) (1,2,2) (2,0,1)
(2,1,0) (2,1,2) (2,2,1) (3,1,1)
```

with every point repeated `n-1`, and proves that the resulting sequence has no zero-sum subsequence of length `n`.  Lemma 2.2(2) says that after selecting a point `h` of multiplicity `n-1`, deleting those copies, and translating every remaining point by `-h`, the remainder has no nonempty short zero-sum subsequence.

Specialize to `n=7` and choose `h=(2,0,1)`.  The resulting 48-term short-zero-free sequence has the eight support points

```text
(6,0,6) (6,0,1) (6,2,6) (6,2,1)
(0,1,6) (0,1,1) (0,2,0) (1,1,0)
```

with multiplicity six each.  Its total sum is `(3,5,0)`.  Delete one copy of `(0,2,0)` and three copies of `(1,1,0)`; those four deleted terms also sum to `(3,5,0)`.  The remainder is therefore the explicit sequence

```text
(6,0,6)^6 (6,0,1)^6 (6,2,6)^6 (6,2,1)^6
(0,1,6)^6 (0,1,1)^6 (0,2,0)^5 (1,1,0)^3.
```

It has length `44`, total sum zero, and remains short-zero-free because it is a subsequence of the 48-term short-zero-free sequence.

The repository verifier does **not** rely only on that prose implication: it independently checks the 48-term and 44-term sequences by two exact algorithms.

## Exact bounded consequences of A7

`verify_c7_44.py` establishes all of the following in the frozen finite object:

1. the donor support, anchor deletion and translation reconstruct the declared 48-term sequence;
2. a term-level reachable-sum dynamic program finds no zero sum of weight `1..7`;
3. an independently structured support-multiplicity enumeration finds no zero-sum submultiset of size `1..7`;
4. the 44-term sequence has total sum zero;
5. hostile positive controls (seven equal terms and an opposite pair) are rejected by both exact predicates, and a wrong four-term deletion is rejected by the total-sum gate;
6. five declared disjoint zero-sum blocks of lengths `8,8,8,8,12` exactly cover the witness.

Because every nonempty zero-sum subsequence of the witness has length at least eight, six disjoint zero-sums would require at least 48 terms.  The explicit five-block cover therefore proves

```text
zz(S) = 5.
```

Thus the bounded scientific conclusion is

```text
44 not in C_0(C_7^3).
```

This is a **derived bounded fact**.  Its priority in the mathematical literature has not been exhaustively certified and remains `CANNOT_CHECK`; no `first` or `novel` claim is authorized.

## Diagnosis: what A7 changes

The `p=5` ORION-04 route won by converting the `D_4` ambiguity into a length-31 total-zero short-zero-free obstruction and then proving that obstruction impossible.  A7 shows that the literal `p=7` analogue is false: length 44 already contains an explicit total-zero short-zero-free object.

The failure localizes responsibility.  The next search should **not** spend resources trying to reproduce the 31-term saturation proof at `p=7` without a new ingredient.

The A7 witness also does not itself refute the candidate Freeze–Schmid-tight value `D_4(C_7^3)=43`: its exact packing number is five, whereas a zero-sum witness relevant to raising the fourth generalized Davenport constant would need packing number at most four.

## Reframed frontier atom B7

The falsification atom is

> **B7.** Is there a zero-sum sequence `B` over `C_7^3` with `|B|=44` and `zz(B)<=4`?

The standard zero-sum characterization used in ORION-04 is

```text
D_k(G) = max{|B| : B is zero-sum and zz(B) <= k}.
```

Consequently, a `YES` to B7 would immediately give `D_4(C_7^3)>=44` and refute tightness of the Freeze–Schmid candidate `43`.  A global `NO` would still need an independently justified upper corridor before claiming `D_4=43`.

## B7-S1 — exact closure of the canonical one-split neighbourhood

Before launching a global length-44 search, take the specialized Freeze–Schmid lower-bound witness

```text
S0 = e1^6 e2^6 e3^20 (e1+e2)^3 (e1+e3)^3 (e2+e3)^4,
```

which has length 42 and total sum `(5,6,6)`.  Append `h=(2,1,1)=-sigma(S0)` to obtain the canonical zero-sum length-43 sequence

```text
B43 = e1^6 e2^6 e3^20 (e1+e2)^3 (e1+e3)^3 (e2+e3)^4 h.
```

`verify_b7_one_split.py` independently enumerates the complete bounded zero-sum substate lattice of `B43` and verifies

```text
zz(B43) = 4.
```

It then freezes the minimum semantic edit that could raise the length while preserving total sum:

```text
replace one occurrence v by two nonzero terms a,b with a+b=v.
```

For each of the seven support types there are exactly 171 unordered nonzero splits, hence 1197 labelled one-term split moves.

The naive approach would recompute a maximum zero-sum packing 1197 times.  The exact closure uses the packing structure instead.  If a split sequence has five zero-sum blocks, `a` and `b` must lie in different blocks; otherwise merging them back to `v` would give five blocks in `B43`, contradicting `zz(B43)=4`.  Merging the two distinct blocks gives a four-block factorization of `B43`.  Conversely, if the corresponding base block can be split after `v -> a+b`, a five-block partition is obtained.

The complete finite base calculation has:

```text
479 zero-sum substates,
159 minimal zero-sum atoms.
```

The counts of zero-sum base blocks `U` containing each source type and leaving a complement that admits three zero-sum blocks are

```text
e1:          144
e2:          143
e3:          144
e1+e2:      119
e1+e3:      119
e2+e3:      127
completion:   79
```

For every source type, after removing the source copy from all eligible `U`, the union of exact submultiset-sum reachability sets covers

```text
343 / 343
```

group elements.  Therefore `-a` is covered for every possible nonzero first split term `a`, and the verifier constructs and checks an explicit five-block zero-sum partition for **every one of the 1197 moves**.

The merge-back argument supplies the matching upper bound `zz<=5` for every one-split sequence.  Hence the bounded result is

```text
all 1197 canonical B43 one-term split moves have exact zz = 5.
```

So the entire one-split neighbourhood contains **no B7 witness**.  This is a real bounded negative result; it is not promoted to a global `NO` for B7.

The scientific diagnosis is that the Freeze–Schmid extremal object is locally packing-rigid under the smallest length-preserving-sum perturbation.  The next useful frontier move must leave this one-edit basin: multi-term exchanges, a different extremal orbit/family, or a global structural exclusion.

## Reproduction and ORION harness binding

Direct bounded checks:

```bash
python research/extensions/orion-math-c7-davenport/verify_c7_44.py
python research/extensions/orion-math-c7-davenport/verify_b7_one_split.py
```

The companion GitHub Actions workflow initializes the canonical `orion-research-harness`, registers the bounded atoms, issues the exact verifiers through the harness `PYTHON` host-capability path, services them locally under explicit process-tool opt-in, and compares the digest-bound harness results with separate direct executions.  The workspace receipts are uploaded as CI artifacts.

This use of the harness grants execution provenance, not novelty or peer-review authority.
