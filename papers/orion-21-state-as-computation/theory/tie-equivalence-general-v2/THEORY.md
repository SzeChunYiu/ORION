# ORION21.TIE_EQUIVALENCE_GENERAL.v2 — general-p decision theorem

**Parent:** `theory/tie-equivalence-quotient-v1/`  
**Status:** `GENERAL_P_IMPOSSIBILITY_PROVED_FOR_COMPLETE_SIGN_ROW_READOUT`  
**Scientific authority delta:** `NONE`

V1 exhaustively enumerated \(p\le5\) and certified that, inside that finite
scope, no invariant can be both representative-independent on tie-equivalence
classes and decision-determining for the complete sign-row prediction readout.
It explicitly left domain size open.

The domain-size restriction is removable by proof. The proof below uses only
the definitions already frozen in V1; it does not replay NR07, reopen the
tie-robust phase experiment, or import any measured magnitude from those lanes.

## 1. Frozen definitions

For \(p\ge1\), a screening state is \(x=(c,r)\) with
\(c\in\mathbb Z^p\) and \(1\le r\le p\). Let `boundary` be the \(r\)-th
largest \(|c_i|\), let

\[
F=\{i:|c_i|>\mathrm{boundary}\},\qquad
T=\{i:|c_i|=\mathrm{boundary}\},
\]

and let \(k=r-|F|\). The admissible top-\(r\) supports are

\[
S(x)=\{F\cup U:U\subseteq T,\ |U|=k\}.
\]

For a support \(s\in S(x)\) and a complete sign row
\(b\in\{-1,+1\}^p\),

\[
\operatorname{score}_s(b)=\sum_{i\in s} b_i\,\operatorname{sign}(c_i),
\qquad
P_s(b)=\mathbf 1[\operatorname{score}_s(b)>0].
\]

The complete prediction readout is the vector \(P_s\) over all \(2^p\) rows.
An invariant is representative-independent when it is constant over all
\(s\in S(x)\).

## 2. Theorem — exact benign/binding characterization

For every \(p,c,r\):

> A tie-equivalence class has one common prediction stream for all
> \(s\in S(x)\) **iff** either it is a singleton or
> `boundary = 0`.

Equivalently, every non-singleton class with positive boundary is
decision-binding under the complete sign-row bank, and every non-singleton
zero-boundary class is decision-benign.

### Proof: zero boundary is benign

Assume `boundary = 0`. Every feature whose membership can vary across
\(S(x)\) lies in \(T\), so it has \(c_i=0\) and
\(\operatorname{sign}(c_i)=0\). All supports contain the same fixed set \(F\);
changing the selected subset of \(T\) therefore adds or removes only zero
terms. Hence every admissible support has the same score, and thus the same
prediction, on every row. ∎

### Proof: positive boundary is binding

Assume `boundary > 0` and choose two distinct admissible supports \(s,s'\).
Set

\[
A=s\setminus s',\quad B=s'\setminus s,\quad C=s\cap s'.
\]

Because both supports have size \(r\), \(|A|=|B|=m\ge1\). Positive boundary
implies every selected correlation is nonzero, so for each selected feature we
may independently choose the transformed sign

\[
u_i=b_i\,\operatorname{sign}(c_i)\in\{-1,+1\}.
\]

Choose \(u_i=+1\) on \(A\) and \(u_i=-1\) on \(B\). On the common set \(C\),
choose signs whose sum \(q\) is \(0\) when \(|C|\) is even and \(1\) when
\(|C|\) is odd. Such a choice always exists. Then

\[
\operatorname{score}_s=q+m>0,
\qquad
\operatorname{score}_{s'}=q-m\le0.
\]

(The only tight case is \(q=m=1\), where the second score is exactly zero and
the frozen rule uses the strict test `score > 0`.) Since all selected
correlations are nonzero, each chosen \(u_i\) corresponds to a legal
\(b_i=u_i\operatorname{sign}(c_i)\in\{-1,+1\}\). Fill unselected row entries
arbitrarily. This row makes \(P_s=1\) and \(P_{s'}=0\). ∎

## 3. Corollary — general-p impossibility

For every \(p\ge2\), the full screening-state domain contains a
decision-binding tie class. Take

\[
r=1,\qquad c=(1,1,0,\ldots,0).
\]

Then `boundary = 1` and both \(\{0\}\) and \(\{1\}\) are admissible. By the
theorem their prediction streams differ.

Now let \(f(x,s)\) be any representative-independent invariant and suppose a
decision readout \(V(x,s)\) were determined by it, \(V=g(f)\). Constancy of
\(f\) on every tie class would force \(V\) to be constant on every tie class.
The witness above has non-constant prediction readout, contradiction.

Therefore, for every fixed \(p\ge2\), over the complete integer screening-state
domain and complete \(\{-1,+1\}^p\) row bank:

> **No invariant of any size or language can be both
> representative-independent and determine the prediction stream on all
> realized outcomes.**

The same applies to V1's canonical-label `accuracy_numerator`: the canonical
support agrees with its own labels on all \(2^p\) rows, while a support with a
different prediction stream must disagree on at least one row.

This removes V1's `p <= 5` restriction from the structural impossibility.

## 4. What becomes theorem-grade from V1

V1 reported empirically within scope that every benign non-singleton class had
boundary zero and every positive-boundary non-singleton class was binding. That
observation is now proved for arbitrary \(p\), arbitrary integer correlation
magnitudes, every support size \(r\), and the complete sign-row readout.

The eight V1 survivor invariants remain representative-independent for the
definitional reason already given there. The new theorem does not say they
disappear; it says no representative-independent invariant can determine a
readout that changes inside one equivalence class.

## 5. Hard boundary — what this still does not prove

The complete sign-row bank is load-bearing. V1 already showed that a restricted
test bank can avoid the disagreement rows and make a binding tie look benign.
Accordingly this theorem does **not** establish:

- the historical NR07 width law;
- any result for NR07's realized or registered finite bank;
- that every restricted bank exposes every positive-boundary tie;
- production superiority, magnitude, or empirical prevalence;
- any transfer from the quarantined post-outcome positive.

It is a general structural theorem about the complete readout defined by V1.
The controlling NR07 and tie-robust-phase terminals remain unchanged.

## 6. Executable regression

`check_general_tie_equivalence_theorem_v2.py` is not the proof. It independently
derives admissible supports by the subset predicate (not V1's fixed/tied
constructor), exhaustively verifies the benign/binding biconditional for
\(p=2,\ldots,6\) over \(c\in\{-1,0,+1\}^p\), and checks the explicit witness for
every \(p=2,\ldots,12\). It exists to catch statement/implementation drift.
