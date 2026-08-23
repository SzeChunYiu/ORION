# Structural Accessibility Theory V2

Status: **EXACT CONTROLLED THEOREMS — NO EMPIRICAL OUTCOME DEPENDENCE**

Date: 2026-08-20

This note deepens the controlled mathematical mechanism behind the P9/P10 structural-accessibility experiments. It is not a theorem about transformers or Lean.

## 1. Setup

Let odd `k=2m+1`. Draw independent uniform signs

`x,c in {-1,+1}^k`.

Define relation coordinates

`r_i=x_i c_i`,

sum

`S_k=sum_i r_i`,

and signed label

`Z=sign(S_k) in {-1,+1}`.

Because k is odd, `S_k` is never zero.

The binary target used in the experiments is `Y=1[Z=+1]`.

## 2. Both representations contain the full target information

Let

- flat representation `F=(x,c)`;
- relational representation `R=(x,r)`.

The map between them is bijective because `c_i=x_i r_i`.

Moreover `Y` is a deterministic function of either representation. The distribution is balanced under global sign reversal of `r`, so `H(Y)=1` bit. Therefore

`I(Y;F)=I(Y;R)=H(Y)=1 bit`.

Thus the controlled flat-versus-relational experiments do not compare different amounts of target information in the Shannon sense.

## 3. Flat coordinates expose no first-order label correlation

### Theorem 1

For every i,

`E[Z x_i]=0`

and

`E[Z c_i]=0`.

### Proof

For `E[Z x_i]`, globally negate `c`. This transformation preserves the uniform distribution, sends every `r_j` to `-r_j`, hence sends `Z` to `-Z`, while leaving `x_i` fixed. Therefore `Z x_i` is paired with its negative under a measure-preserving involution and its expectation is zero.

The proof for `E[Z c_i]` is identical after globally negating `x`. QED.

This does not say the flat representation lacks information. It says the target has no **first-order linear correlation** with any raw flat coordinate.

## 4. Relation coordinates expose positive first-order signal

### Theorem 2

For every i,

`E[Z r_i] = E[|S_k|]/k`.

### Proof

By permutation symmetry all `E[Z r_i]` are equal to a common value `a_k`. Summing over i,

`k a_k = E[Z sum_i r_i]`

`      = E[Z S_k]`

`      = E[|S_k|]`.

Hence `a_k=E|S_k|/k`. QED.

### Theorem 3 — closed form for odd k

For `k=2m+1`,

`E[Z r_i] = C(2m,m)/2^(2m)`.

Equivalently,

`E[|S_{2m+1}|] = (2m+1) C(2m,m)/2^(2m)`.

### Proof sketch

The expected absolute displacement of a symmetric simple random walk after `2m+1` steps is

`(2m+1) C(2m,m)/2^(2m)`.

Substitute into Theorem 2. This identity may also be obtained by pairing adjacent binomial probabilities or the standard recurrence for expected absolute random-walk displacement. QED.

By Stirling's approximation,

`E[Z r_i] ~ 1/sqrt(pi m) ~ sqrt(2/(pi k))`.

Each individual relational coordinate therefore carries a positive first-order signal whose magnitude decays as `Theta(k^-1/2)`, while the exact sum of all relation coordinates still gives a perfect degree-1 separator.

## 5. Invertible block obfuscation analytically thins first-order signal

Partition the relation vector into consecutive blocks of maximum length b. In each block encode

- first position: `u_1=r_1`;
- later positions: `u_j=r_j r_{j-1}`.

The previous theorem note proves exact invertibility and `r_j=product_{i=1}^j u_i` within a block.

### Theorem 4 — non-leading encoded coordinates have zero first-order label correlation

For every non-leading position j in a block,

`E[Z u_j]=E[Z r_j r_{j-1}]=0`.

### Proof

Apply global negation `r -> -r`. The distribution is preserved and `Z -> -Z`, but

`u_j=(-r_j)(-r_{j-1})=r_j r_{j-1}`

is unchanged. Thus `Z u_j` is paired with its negative and has zero expectation. QED.

### Theorem 5 — block-leading coordinates retain the canonical relation signal

A block-leading encoded coordinate is simply one original relation coordinate, so

`E[Z u_lead] = a_k = C(k-1,(k-1)/2)/2^(k-1)`.

If the length-k vector is partitioned into `B=ceil(k/b)` blocks, exactly B encoded coordinates retain this positive first-order label correlation and the remaining `k-B` have zero first-order correlation.

Hence the Euclidean norm of the vector of first-order label correlations is

`||E[Z u]||_2 = a_k sqrt(B)`.

For canonical coordinates b=1, B=k and the norm is `a_k sqrt(k)`. The ratio is therefore

`sqrt(B/k) = sqrt(ceil(k/b)/k)`.

For large k divisible by b this is approximately

`1/sqrt(b)`.

So the invertible encoding preserves **all target information** while analytically reducing the amount of target signal visible to a first-order linear statistic by a factor of roughly `b^-1/2` in norm.

This is a precise mechanistic accessibility statement, not a general theorem about the optimal classification accuracy of every linear threshold.

## 6. The target-sufficient state is exact

Let the minimal state be the relation vector `r`.

Because

`Y = 1[sum_i r_i > 0]`,

we have

`H(Y|r)=0`.

For any additional world coordinates W, including `x`, `c`, or independently sampled nuisance state `z`,

`I(Y;W|r)=0`

because conditioning on r already determines Y exactly.

Thus the predictive-state compression experiment has an exact target-sufficiency interpretation:

- `r` is sufficient for Y;
- `(x,r)` retains extra world information but no additional target information conditional on r;
- independently generated nuisance coordinates add neither target information nor latent-world information relevant to Y.

This experiment is intentionally different from the full-state same-information comparisons: the compact arm is **lossy about the world but lossless about the target**.

## 7. Three distinct mathematical axes

The controlled programme should keep these quantities separate:

1. **Shannon target information**: `I(Y;representation)`; equal and maximal for bijective flat/relational full-state encodings.
2. **first-order accessibility**: correlations or other statistics visible to a restricted learner; zero in raw flat coordinates and positive in relation coordinates here.
3. **interaction/access degree**: degree required to express the exact decision after coordinate transformation; degree 1 relational, degree 2 flat, and progressively higher explicit inverse degrees in the block chain.

The experiments show that equality on axis 1 does not force equality on axes 2 or 3.

## 8. Relation to empirical results

The exact theorems predict the qualitative pattern already tested prospectively:

- relational linear learning should be easy because all relation coordinates expose aligned first-order signal and their sum is an exact separator;
- flat linear logistic learning has no first-order coordinate-label signal;
- flat quadratic expansion can reconstruct pairwise relation terms but at generic feature/sample cost;
- invertible block obfuscation reduces directly visible first-order signal as block length grows;
- increasing polynomial interaction degree can recover latent coordinates up to the tested access degree;
- removing target-irrelevant coordinates can reduce finite-sample burden even when the removed information is real world information.

The empirical results remain necessary: these theorems do not determine finite-sample logistic-regression accuracy, regularization effects, optimization behavior, or transformer/Lean performance.

## 9. Claim boundary

The strongest exact mathematical conclusion is:

> Equal target information can coexist with sharply different first-order signal exposure and interaction order under bijective coordinate changes; a target-sufficient statistic can also discard world information without discarding any information about the target.

No universal computational lower bound, transformer scaling law, or theorem-proving utility follows without separate evidence.
