# N3 Lane Closure Packet: Issue #676 Successor Families A-D Executed

- Date: 2026-08-21
- Lane: ORION-Q N3 (issue #676, parent programme #633; immutable prior
  disposition #671 `QC3_DONOR_COLLAPSED_NO_DISTINCT_ORION_RESIDUAL`).
- Discipline: protocols were frozen BEFORE any outcome
  (N3_A/B/C/D `*_PROTOCOL.md` in this directory); supplied-grammar donors held
  first right of refusal in every arm; hostile controls in every family;
  exact-synthetic scope only; honest negatives were valid terminals.
- Authority of everything below:
  `exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority`.
  No P10, no novelty, no real-quantum claims are made or implied.

## Executed families and terminals

All four registered successor families (previously executed: NONE, per the
2026-08-21 audit comment on #676) were executed as deterministic
exact-synthetic studies under
`research/extensions/orion-q/nlanes/` (scripts `n3_*.py`, receipts
`N3_*_RESULTS.json`, single-line `ORIONQ_N3_*=` stdout receipts, exit 0,
in-process double-run determinism digests identical in every family).

### A. Finite optimum -> symbolic family induction
- Terminal: `N3A_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`; gates GA0-GA4 all true.
- Residual arm: BFS-proved optimal chain artifacts at n=2..5 (min lengths
  1,2,3,4) induced the unique schema tuple (1,0,1,1,1,-1); exact-verified at
  held-out n=8,10,12 while the concrete donor exhausted 200,000 BFS expansions
  per n at depth 3-4 without a hit and the trivial replay failed all three.
  Candidate cost: 6,710 constructed programs (budget 200,000).
- Donor refusal arm: supplied-parametric macro donor (CHAIN) matched all
  held-out n; candidate recorded parent_sufficient and claimed nothing.
- Hostile arm: spec mutates at n>=6; schema fit train but the exact verifier
  rejected all held-out n; no family claim leaked.

### B. Proof-obligation-driven grammar expansion
- Terminal: `N3B_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`; gates GB0-GB4 all true.
- Residual arm (Gray code over Z16): supplied grammar G0 was exhaustively
  enumerated (value-table dedup) through size 12 under the 2,000,000-eval
  donor budget without expressing the spec — a bounded inexpressibility proof,
  not a timeout. Candidate proposed the minimal extension {SHR1, XOR}
  (cost 2; synthesized expression size 4); all four cost-1 subsets proved
  insufficient at bound 7; trivial bloat baseline needed cost 4. Candidate
  total: 482,766 evals (budget 2,000,000).
- Donor refusal arm ((2x+3) mod 16): G0 expressed it at size 5; candidate
  proposed the EMPTY expansion.
- Hostile arm (fixed pseudorandom permutation table): absent from G0 and from
  every extension subset at the bound; candidate reported
  OBLIGATION_UNRESOLVED_AT_BOUND with no expansion claim.

### C. Cross-family operator induction
- Terminal: `N3C_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`; gates GC0-GC4 all true.
- The prefix-incremental affine fold law fit all three train families
  (F1 chain, F2 fan, F3 double layer) exactly. Held-out F4 (reverse fan with
  base), from atoms n=2..4 only, transferred and exact-verified at n=8,10;
  the concrete donor failed both at 200,000 BFS expansions each and trivial
  replay failed both. Candidate cost: 16 constructed programs.
- Donor refusal arm F5 (constant family): trivial replay matched all held-out
  sizes; parent_sufficient recorded; no operator value claim.
- Hostile arm F6 (correction gate appearing only at n>=5): fold law fit the
  supplied atoms but every unrolled prediction was rejected by the exact
  verifier; no transfer claim leaked.

### D. Representation variable synthesis
- Terminal: `N3D_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`; gates GD0-GD4 all true.
- Residual arm (chain hidden under i -> 3i mod n, train n=5,7): raw
  (supplied) representation induction failed; the library walk selected mul3
  at transport cost 1, recovering schema (1,0,1,1,1,-1); exact-verified at
  held-out n=11,13; concrete donor failed both at 200,000 BFS expansions
  (depth 3); trivial replay failed both. Candidate cost: 17 constructed
  programs.
- Donor refusal arm (plain chain): identity representation selected first at
  transport cost 0; parent_sufficient; no residual claim.
- Hostile arm (keyed pseudorandom permutations, seed 20260821): no library
  representation fit both train sizes; NO_VALID_REPRESENTATION reported; no
  family claim.
- Implementation note (recorded for honesty): the first implementation
  computed the frozen schema-fit predicate by naive grid enumeration and
  exceeded the frozen 200,000 budget (278,758), failing GD0 while GD1-GD4
  held. Revision r2 computes the mathematically identical predicate
  constructively (tokens at t=0,1 uniquely determine the coefficients; ranges
  and token-equality checks unchanged); no gate, world, budget, or mechanism
  definition was altered. The shipped receipt is from r2.

## Stop-rule assessment for #676

The registered stop rule: final negative only after >=3 materially different
higher-order successor families are executed/absorbed, or a registered
impossibility/lower bound closes the class; `DONOR_OWNS_PARAMETRIC_SYNTHESIS`
alone is not an allowed final terminal.

- The execution precondition is now receipt-satisfied in-repo: FOUR materially
  different successor families (all four registered in #676) have frozen
  protocols, deterministic runners, and receipts.
- However, the receipts do NOT support a final negative: all four families
  returned `*_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC` — in exact, enumerable,
  hostile-controlled synthetic worlds, each higher-order mechanism recovered
  verified families beyond matched-budget supplied-grammar donors, while
  correctly refusing to claim value wherever the donor sufficed and while the
  exact verifier caught every planted overgeneralization.
- Correct lane disposition under the receipts: #676 cannot be closed as
  `DONOR_OWNS_PARAMETRIC_SYNTHESIS` (still disallowed alone) NOR as a final
  negative (the executed families contradict it in-scope). The lane holds a
  bounded exact-synthetic residual signal; any stronger disposition (e.g. a
  claim about real parametric quantum synthesis) would require confirmatory
  work far outside this packet's authority and is explicitly NOT claimed here.

## Artifacts

- Protocols (frozen pre-outcome):
  `development/orion-q-nlane-closure/N3_{A,B,C,D}_*_PROTOCOL.md`
- Runners:
  `research/extensions/orion-q/nlanes/n3_{a,b,c,d}_*.py`
- Receipts:
  `research/extensions/orion-q/nlanes/N3_{A,B,C,D}_*_RESULTS.json`
- Total wall time of the four real runs: ~34 s (1.1 + 31.7 + 0.8 + 0.6).
