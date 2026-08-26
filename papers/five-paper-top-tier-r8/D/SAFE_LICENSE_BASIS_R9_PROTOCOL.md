# Minimum Safe License Basis R9 Replay Protocol

## Frozen files

- `SAFE_LICENSE_BASIS_R9_ADDENDUM.md`
- `SAFE_LICENSE_BASIS_PRIOR_ART_R9.json`
- `verify_safe_license_basis_r9.py`
- `SAFE_LICENSE_BASIS_R9_RESULTS.json`

## Command

```bash
python papers/five-paper-top-tier-r8/D/verify_safe_license_basis_r9.py
```

The verifier uses the Python standard library only and must reproduce the registered JSON byte-for-byte.

## Required controls

1. The SET COVER construction uses acyclic depth-one unary Horn rules with singleton caps.
2. Reachability-derived coverage equals the source set family on every registered instance.
3. Bitmask dynamic programming equals exhaustive basis enumeration.
4. The greedy basis satisfies the registered harmonic bound whenever a safe basis exists.
5. Every set system is exhausted for universe sizes one through three.
6. Every family of at most six distinct nonempty subsets is exhausted for universe size four.
7. The deterministic larger panel contains exactly 4,000 generated instances at seed `20260826`.
8. Unsafe-license filtering raises the registered optimum from two to three.
9. An instance whose only cover reaches a forbidden claim is reported infeasible.
10. All mismatch and bound-violation counters remain zero.

## Structurally independent replay

An independent implementation should encode the selected-license problem as 0-1 ILP, SAT, or CP-SAT, compute typed reachability with a relational/Datalog engine, and regenerate small set systems independently. It must compare optima, infeasibility, greedy certificates, source-family recovery, and the full result digest.

## Authority ceiling

A PASS corroborates the reduction and algorithms on the frozen bounded panels. NP-completeness and the exact reduction rest on the analytic proof. The artifact grants no real-policy utility, novelty over classical SET COVER, or journal authority.
