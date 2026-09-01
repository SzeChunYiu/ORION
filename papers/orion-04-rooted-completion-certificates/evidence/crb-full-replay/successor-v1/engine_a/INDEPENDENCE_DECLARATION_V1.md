# engine_a — independence declaration

**Status:** `INDEPENDENT_ROUTE_UNDER_CONSTRUCTION__NO_D4_OUTCOME`
**Scientific authority delta:** `NONE`. No D4 instance has been evaluated.
`d4_rounds_consumed` remains `0`.

## Why a second engine exists at all

`PROOF_OBJECT_CONTRACT_V1.md` requires the lower bound `D_4 >= 30` to be closed by **two
independent proof routes**, and refuses the cheap substitutes by name: *"same encoder
different random seeds"* and *"two solvers consuming the same generated CNF"* do not
count.

`engine_b` is the **L-A certificate route**. Its directory carries
`EXTERNAL_DRUP_CHECKER_PROTOCOL.json`, `batch_external_drup.py` and a `python-sat`
install log, so it reduces the question to a declarative encoding and discharges it with a
solver plus a checkable unsatisfiability certificate.

`engine_a` is therefore the **L-B independently derived route**, and its whole value is
being *unlike* `engine_b`.

## What engine_a must not touch, stated before it is written

Per the contract's independence boundary, `engine_a` may not consume any of:

- `engine_b`'s normalised candidate stream;
- its learned clauses;
- its orbit table;
- its decision trace;
- any CNF it generated.

Permitted shared core, also per the contract: the **primitive semantic specification**
(what `C_5^3`, a zero-sum subsequence and `D_k` mean) and **cryptographic hash utilities**,
whose correctness is not the mathematical claim under test.

The practical consequence is that `engine_a` derives its state representation and
transition rules directly from group semantics and reads nothing from `../engine_b/`.

**The check for this is machine-run, and the obvious version of it is wrong.** A grep for
`engine_b` in this directory returns 3, and all three are prose: two in the module
docstring explaining the independence, one in the key `"consumes_engine_b": False` that
reports it. A substring search cannot separate *describing* a dependency from *having*
one, so `independence_check()` uses the abstract syntax tree instead and asserts three
properties:

1. no `import` or `from ... import` naming `engine_b`;
2. no string constant that is a path into `../engine_b/`;
3. the import set is standard library only — in particular **no SAT or CNF library**,
   which is what distinguishes this route from `engine_b`'s.

Property 3 is the one that matters most, because an L-B route that quietly reached for the
same solver would satisfy the first two and still not be a second route.

## Order of work, and why calibration comes first

The contract mandates a frozen small-instance calibration suite *"whose exact answers are
already independently established"*, exercised **before** the D4 outcome is accessed.
That suite exists at `../../d4-proof-handoff-v1/calibration-suite-v1/`, with ground truth
taken from the published rank-≤2 closed forms `D_k(C_n) = k n` and
`D_k(C_m ⊕ C_n) = m + k n − 1`.

So `engine_a` is validated against answers it could not have produced, on instances small
enough to check by hand, before it is pointed at anything unknown. An engine that cannot
reproduce `D_2(C_3) = 6` has no business being trusted on `D_4(C_5^3)`.

This ordering is not bureaucratic. It is the only way a sole researcher obtains external
verification of a search implementation: the closed forms are the external party.

## What this file does not do

It authorises no execution. The one-shot remains gated by
`../../d4-proof-handoff-v1/AUTHORIZED_EXECUTION_GATE.md`, whose preconditions include this
engine existing *and* a standalone upper-bound verifier that is still absent.
