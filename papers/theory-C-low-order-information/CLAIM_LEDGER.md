# Paper C claim ledger

| ID | Claim | Evidence | Status / boundary |
|---|---|---|---|
| C-C1 | For every `m>=5`, unary optimality is equivalent to pair nonpositivity plus two-disjoint-pair clauses; maximum clause support is four indices. | C1 analytic proof + dual machine corroboration. | PROVEN-ALL-M for the frozen partition compiler. |
| C-C2 | The threshold is sharp: the registered `m=4` instance satisfies all clauses but has `C_U=27 > 23=C_single`. | Exact C1 counterexample. | PROVEN-EXACT. |
| C-C3 | Complete ordered weights and complete labeled pair gains do not determine exact value: gap `2t-1` is unbounded. | C2 scalable gadget proof + finite exact checks. | PROVEN-ALL-T. |
| C-C4 | Complete pair information does not determine whether an optimal triple block exists. | C2 forced optimizer-structure theorem. | PROVEN-ALL-T. |
| C-C5 | For every `m>=5,L>=1`, all labeled common factors through order `m-2` can agree while exact improvement differs by `[m(ceil(log2 m)+1)-1]L`. | C3 analytic parity construction + finite exact checks. | PROVEN-ALL-M,L for frozen grammar. |
| C-C6 | Any nonzero integer trade preserving every proper upper marginal is `delta(S)=(-1)^(q-|S|)c`. | Boolean-lattice Möbius inversion, Theorem 2; bounded reconstruction checks `q<=8`. | PROVEN-ALL-Q. |
| C-C7 | Such a trade touches all `2^q` cells and has positive/negative mass `2^(q-1)|c|`; primitive parity trade is sharp. | C-C6 + parity count. | PROVEN-EXACT. |
| C-C8 | C3's common padding is minimal. | none | OPEN; explicitly not claimed. |
| C-C9 | The separation is multiplicative or transfers to all objectives/grammars. | none | OPEN / not claimed. |
| C-C10 | Markov bases, marginal fibers, Möbius inversion or generic lower-order insufficiency are new. | algebraic-statistics donor literature | DONOR-OWNED. |

## Headline decision proof

**Question:** can low-order information be complete for deciding whether optimization helps while being incomplete for the value and structure of the optimizer?  
**Answer:** yes: a four-index decision theorem coexists with unbounded pair/value and arbitrary-order/value separations.  
**Strongest alternative:** C3 looks large only because the witness construction is inefficient.  
**Resolution:** Möbius inversion proves every nonzero proper-marginal-preserving trade is a parity multiple and therefore has exponential difference support.  
**Boundary:** common-padding minimality and cross-objective transfer remain open.
