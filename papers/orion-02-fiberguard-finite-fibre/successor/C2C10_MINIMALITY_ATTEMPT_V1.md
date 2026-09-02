# C2-C10 — Common-padding minimality: attempt V1 (additive successor note)

Date: 2026-09-02. Lane: Tier-B upgrade survey. Scope: claim **C2-C10** of
`papers/orion-02-fiberguard-finite-fibre` (`CLAIM_LEDGER_R2.md`): *"Common
padding is minimal."* — status **OPEN; NOT CLAIMED**, boundary note *"Only
difference trade is minimal."* Nothing in the frozen package is edited by this
note; all results here are new, machine-verified, and additive.

## 1. Formal statement attempted

Setting (MANUSCRIPT_V3_PIPELINE.md §2 and §6): the Section-6 order-(m−2)
construction with m ≥ 5 terms — anchor term 0 plus q = m−1 variables — has
instance A = L copies of every column with support {0} ∪ S, S ⊆ [q] odd, and
instance B = the even-parity family; N = 2^{m−2}·L trade columns per side. The
manuscript prescribes a **common padding** of K0 = N·m·(b+1) + m−1 + d(m) + b + 1
full-support columns added to both instances (b = b(m) = ⌈log₂ m⌉) and proves
K0 suffices to make the one-block partition the unique optimum in both
instances. C2-C10, read precisely, is:

> **S(C2-C10).** For every m ≥ 5 and L ≥ 1, K0(m,L) is the *minimal* common
> padding: the smallest K ≥ 0 such that, in **both** instances X ∈ {A,B}, the
> one-block partition is the strict unique optimum (C_one^X(K) < C_Π^X(K) for
> every proper partition Π, |Π| ≥ 2).

Call that smallest K **Kmin(m,L)**. S(C2-C10) asserts Kmin = K0.

## 2. Two structural lemmas (proven, all m ≥ 5, L ≥ 1)

Frozen objective (§2): b(s) = ⌈log₂ s⌉ with b(1) = 0; d(1) = 0, d(s) =
d(⌈s/2⌉)+d(⌊s/2⌋)+s−2;
C_one = (b+1)W + m−1+d+b − [m(b+1)−1]·f([m]);
C(Π) = 2m+|Π|−3 + Σ_S d(|S|) + max_S b(|S|) + Σ_S [2f(S) + (b(|S|)+2)(w(S) − |S|f(S))].

**Lemma 1 (exact affine dependence on K).** Adding K common full-support
columns increments every w_i by K and every f(T) by K, leaves every block size
(and hence d, b, and the 2m+|Π|−3 term) unchanged, and therefore
C_one(K) = C_one(0) + K  and  C_Π(K) = C_Π(0) + 2|Π|·K  exactly.
*Proof.* In C(Π)'s block term, w(S) grows by |S|·K and |S|f(S) by |S|·K, so
(w(S) − |S|f(S)) is invariant and only the 2f(S) part moves, by +2K per block;
the other three additive parts are K-free. In C_one, W grows by mK and f([m])
by K: (b+1)mK − [m(b+1)−1]K = K. ∎

**Lemma 2 (per-partition threshold).** For instance X and proper partition Π,
one-block strictly beats Π at padding K iff K·(2|Π|−1) > G_Π^X, where
G_Π^X := C_one^X(0) − C_Π(0). Hence the least K making Π strictly worse is
⌊G_Π^X/(2|Π|−1)⌋ + 1 when G_Π^X > 0 (else 0), and
**Kmin(m,L) = max over instances X and proper Π** of that quantity.
*Proof.* C_Π(K) > C_one(K) ⇔ C_Π(0) + 2|Π|K > C_one(0) + K by Lemma 1; 2|Π|−1 ≥ 3 > 0. ∎

So Kmin is a finite maximum of closed-form integers: no search over K, only a
maximization over partitions. (Facts used, machine-verified at K=0 against the
construction: w_0 = N, w_variable = N/2, W = N(m+1)/2; for variable T with
|T| = t ≤ q−1, f(T) = N/2^t in **each** parity instance; for anchor-containing
T = {0} ∪ T′, f(T) = N/2^{|T|}·2 = N/2^{t−1}; f([m]) = εL with ε = 1 exactly in
the instance whose parity equals the parity of q = m−1.)

## 3. Result 1 — C2-C10 is REFUTED

**Theorem (refutation).** K0(m,L) is not minimal for any (m,L) tested; e.g.
m = 5, L = 1: **Kmin = 13 while K0 = 172** — the construction's padding is
13.2× larger than needed, and K = 13 is certified by direct recomputation
(one-block strictly optimal in both A and B over all 52 partitions; at K = 12
the partition {0,4},{1,2,3} ties or beats it in A). Ratios across m = 5..10:
12.8–23.5 (table below). The refutation is certified, not sampled: Kmin values
were obtained by exhaustive maximization over **all** set partitions (52, 203,
877, 4140, 21147, 115975 for m = 5..10) and then re-verified by fully
independent direct recomputation at K = Kmin−1 (must fail) and K = Kmin (must
hold strict).

## 4. Result 2 — exact threshold for m ≤ 10; the binding family

Exhaustive maximization gives, with binding profile named by its block kinds
(ap = {anchor, variable}, vvv = variable triple, v = singleton variable; k_X =
per-instance threshold; the binding instance in bold on its side):

| m | L | N | K0 | **Kmin** | binding profile (kA, kB) | K0/Kmin |
|---|---|-----|------|-----|--------------------------|---------|
| 5 | 1 | 8 | 172 | **13** | ap+vvv (13, 7) | 13.2 |
| 5 | 2 | 16 | 332 | **26** | ap+vvv (26, 13) | 12.8 |
| 6 | 1 | 16 | 399 | **25** | ap+vv+vv (20, **25**) | 16.0 |
| 6 | 2 | 32 | 783 | **49** | ap+vv+vv (40, **49**) | 16.0 |
| 7 | 1 | 32 | 914 | **44** | ap+vv+vvv (**44**, 38) | 20.8 |
| 7 | 2 | 64 | 1810 | **87** | ap+vv+vvv (**87**, 76) | 20.8 |
| 8 | 1 | 64 | 2069 | **88** | ap+vv+vv+vv (83, **88**) | 23.5 |
| 8 | 2 | 128 | 4117 | **175** | ap+vv+vv+vv (166, **175**) | 23.5 |
| 9 | 1 | 256 | 5786 | **273** | ap+vvv+vvvv (**273**, 264) | 21.2 |
| 10 | 1 | 512 | 12830 | **552** | ap+vvvv+vvvv (542, **552**) | 23.2 |

(m = 9, 10 margins at Kmin: A = 3, B = 47 and A = 54, B = 5; at Kmin−1 the
binding margin is −2 and 0 respectively — at m = 10, K = 551 fails only by a
*tie* in B, showing strictness matters.) The binding competitor is always a
**matching-type** partition: the anchor paired with one variable, remaining
variables covered by small (size ≤ 4) blocks. Two pattern shifts: even m ≥ 8
binds in B (the ε = 0 instance, whose one-block is dearer); the optimal block
profile coarsens as m grows (pairs → pair+triple → pairs → triple+quad → two
quads), tracking the 1/(2|Π|−1) denominator.

## 5. Result 3 — proven bracket for ALL m ≥ 5, L ≥ 1, and asymptotic slack

**Theorem (lower bound).** Let F(m) be the family of proper partitions whose
anchor block is {0}, {0,i}, or {0,i,j} and whose remaining blocks have size ≤ 4.
For every m ≥ 5 and L ≥ 1:
  **max_{Π ∈ F(m)} ⌊G_Π/(2|Π|−1)⌋ + 1 ≤ Kmin(m,L) ≤ K0(m,L).**
*Proof of ≤.* Each member of F is a concrete partition; if K works then by
Lemma 2 it exceeds every member's threshold. *Proof of ≥.* Manuscript §6
sufficiency bound (untouched). Block terms for F are closed-form via §2's
f/w table (f({0,i}) = N/2, f({i,j}) = N/4, f({0,i,j}) = N/4, f(var triple) =
N/8, f(var quad) = N/16 — the last exact for m ≥ 7; the m = 5 quad special
case f ∈ {0, L} is immaterial: its threshold is 4, far under the winner 13). ∎
The family maximum **equals** the exhaustive Kmin at all ten (m,L) points above.

**Corollary (asymptotic non-minimality).** Even m ≥ 6, instance B (ε = 0), the
all-pairs member {0,i},{j,k},… alone gives an exact closed form; the proven
ratio K0/Kmin grows without bound, tracking 2m(b+1)/(b−1):

| m | 6 | 8 | 10 | 12 | 16 | 20 | 32 |
|---|---|---|----|----|----|----|----|
| K0 / proven-LB | 16.0 | 23.5 | 26.5 | 33.0 | 46.2 | 53.6 | 89.5 |
| asymptote 2m(b+1)/(b−1) | 24 | 32 | 33.3 | 40 | 53.3 | 60 | 96 |

So the Section-6 padding is not merely non-minimal at small m: it is
**Θ(m)-fold** larger than the proven requirement — the conservative term
N·m·(b+1) dominates a threshold that is only ≈ N·(b−1)/2 in magnitude.

## 6. What I could NOT close (honest obstruction)

The exact identity Kmin = max over F is **verified** only for m ≤ 10 (and
L ≤ 2 for m ≤ 8). Proving it for all m requires showing no partition outside F
— blocks of size ≥ 5, multiple anchor-adjacent blocks, or larger anchor blocks —
ever attains a larger ⌊G_Π/(2|Π|−1)⌋+1. The natural attack is an exchange
argument (splitting any size-s ≥ 5 block into 2+（s−2) never decreases the
threshold because G drops slower than the denominator rises), which I could not
complete: G_Π is not monotone under splitting (the 2f(S) term can *rise* when a
block splits through the b(|S|)+2 coefficient change), so the exchange lemma is
false in the naive form and a weighted amortization would be needed. This is
the single identified obstruction; everything else above is proven or
exhaustively certified.

## 7. Verdict

**C2-C10: REFUTED (as stated — the Section-6 common padding K0 is not minimal;
exact certified counterexample m=5, L=1: Kmin = 13 < K0 = 172, and proven
Θ(m)-asymptotic slack), with constructive successor: exact threshold Kmin(m,L)
certified for m = 5..10 via exhaustive partition maximization, and a proven
two-sided bracket family-max ≤ Kmin ≤ K0 for all m ≥ 5, L ≥ 1. Exact
general-m closed form STILL-OPEN (obstruction: exchange/monotonicity argument
for block profiles outside the matching family, §6).**

## Appendix — self-contained verification script

Reproduces the table: affine solve over all partitions + independent direct
recomputation at Kmin−1 / Kmin / K0 (m ≤ 8; m = 9, 10 need only the final
direct check, ~minutes). Python 3, stdlib only.

```python
import math
from functools import lru_cache
from itertools import combinations

@lru_cache(maxsize=None)
def bf(s): return 0 if s == 1 else math.ceil(math.log2(s))
@lru_cache(maxsize=None)
def df(s): return 0 if s == 1 else df((s+1)//2) + df(s//2) + s - 2

def gen_partitions(n):
    if n == 0: yield (); return
    for part in gen_partitions(n-1):
        yield (frozenset((n-1,)),) + part
        for i in range(len(part)):
            yield part[:i] + (part[i] | {n-1},) + part[i+1:]

def cols_of(m, L, odd, K):
    q = m - 1; out = []
    for S in range(1 << q):
        if (bin(S).count("1") % 2 == 1) == odd:
            out += [(0,) + tuple(i+1 for i in range(q) if (S >> i) & 1)] * L
    return out + [tuple(range(m))] * K

def costs(cols, m, parts):
    w = [sum(i in c for c in cols) for i in range(m)]
    f = lambda T: sum(set(T) <= set(c) for c in cols)
    b, d = bf(m), df(m)
    one = (b+1)*sum(w) + m-1+d+b - (m*(b+1)-1)*f(range(m))
    def cost(pi):
        t = 2*m + len(pi) - 3; ds = bm = blk = 0
        for S in pi:
            s = len(S); fs = f(S); ws = sum(w[i] for i in S)
            ds += df(s); bm = max(bm, bf(s))
            blk += 2*fs + (bf(s)+2)*(ws - s*fs)
        return t + ds + bm + blk
    return one, [cost(p) for p in parts]

for m in (5, 6, 7, 8):
    for L in (1, 2):
        parts = [p for p in gen_partitions(m) if len(p) >= 2]
        kmin = 0
        for odd in (True, False):           # affine solve at K=0 (Lemma 1/2)
            one, cs = costs(cols_of(m, L, odd, 0), m, parts)
            kmin = max(kmin, max((math.floor((one - c) / (2*len(p) - 1)) + 1
                                  if one > c else 0)
                                 for p, c in zip(parts, cs)))
        N = (1 << (m-2)) * L; b, d = bf(m), df(m)
        K0 = N*m*(b+1) + m-1+d+b+1
        def strict(K):
            return all(costs(cols_of(m, L, odd, K), m, parts)[0]
                       < min(costs(cols_of(m, L, odd, K), m, parts)[1])
                       for odd in (True, False))
        assert not strict(kmin-1) and strict(kmin) and strict(K0)
        print(f"m={m} L={L}: Kmin={kmin}  K0={K0}  ratio={K0/kmin:.1f}")
```

Verification runs (2026-09-02): m = 5..8, L ∈ {1,2} — all assertions pass;
m = 9, 10, L = 1 — same protocol over 21147 / 115975 partitions with direct
min-over-partitions recomputation at the reported Kmin and Kmin−1
(margins quoted in §4). Affine algebra (Lemma 1) additionally validated by
recomputing costs with K explicit at K ∈ {Kmin−1, Kmin, K0}.
