# ORION-17 reproduce V2.1

Run from repository root:

```bash
PYTHONPATH=src python papers/orion-17-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py
PYTHONPATH=src python papers/orion-17-epistemic-navigation-open-worlds/formal/check_contract_manifest_v2.py
```

Expected sentinels:

```text
ORION-17 THEORY CLOSURE V2: PASS
theory_closure_terminal: PASS
ORION-17 CONTRACT MANIFEST V2: PASS
```

The first command checks the closed theorems/countermodels. Its `PASS` banner reports assertion status only — every finite witness in the file held — and `theory_closure_terminal` is the verdict on what those witnesses establish.

`theory_closure_terminal` is now `PASS`, and `check_support_transport` is why it was not. That check enumerated the 64 transport-coordinate combinations and could decide **1** of them from the witness coordinates alone (a complete witness transports closure); the other 63 turned on Definition 14 target-ambiguity, which the six-coordinate `Transport` model did not carry, so the check reported `CANNOT_CHECK` naming the premise rather than a case count. It now enumerates an admissible target completion class beside each witness — the 15 non-empty classes over a fixed four-completion pool, 7 of them ambiguous — and decides target-ambiguity per case with `extension_ambiguous`, the Definition 14 decider this file already shipped. The enumeration is therefore **960 cases** (64 × 15) and the check reports `support_transport: PASS (960 checked)`.

**The 960 is not a bigger 64.** 64 was the size of an enumeration standing downstream of a premise nothing decided, of which 1 case was decided; 960 counts cases whose premise the check itself decides. Any earlier reading of the 64 as a count of decided cases was wrong, and so is reading the 960 as the same quantity grown.

What the 960 establishes: on every case the terminal Theorem 6 assigns is the terminal computed from the witness's completeness and from Definition 14 applied to that case's own completion class, with nothing about ambiguity supplied by the caller; and on the 945 cases with an incomplete witness the terminal changes when ambiguity does, so the premise is consumed and not carried past. What it does not establish: the other 15 pair the one complete witness with each class, where Theorem 6 is `TRANSFER_CLOSURE` whatever ambiguity is — those cases decide the premise but do not test the terminal's dependence on it. Nor is this a proof over Definition 14: the classes are a finite family over a fixed pool, not every completion class a target model could admit. `PYTHONPATH=src python -m orion.study.p7.premise_audit` measures all of that against this file and exits `0`; it reports the same premise over the six coordinates alone, where it is still undecidable in that model, and the floor under the verdict — 945 of the 960 cases exclude a value of the premise from the terminal assertions alone, leaving 2**15 ambiguity rules where 2**64 survived before.

The second command executes all 8 frozen prospective contract cases, including harmful-reframe and non-retrieval experimental-design transfer controls.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py tests/unit/candidates/test_p6_p8_theory_closure_v21.py
```

The contract manifest is a reference-policy oracle and prospective instrument preflight. It does not constitute a live-agent performance result.

## Mechanized formal core (V4)

The composition and unit laws, and the reading of the donor stack that makes the
committed composition rows instances of them, are regenerated from source. The
second takes a required `--date`: its artifact is content-bound and nothing in it
reads the clock.

```bash
PYTHONPATH=src python -m orion.study.p7.composition_calculus_smt --repo-root . \
  --output papers/orion-17-epistemic-navigation-open-worlds/formal/mechanized/P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json
PYTHONPATH=src python -m orion.study.p7.donor_stack_as_transformation_family --repo-root . \
  --date 2026-08-22 \
  --output papers/orion-17-epistemic-navigation-open-worlds/formal/mechanized/P7_DONOR_STACK_AS_TRANSFORMATION_FAMILY_2026-08-22.json
```

Both exit `0` only when every theorem is `PROVED`; `UNKNOWN` is not a pass, and a
solver timeout exits `3`. The second additionally exits `3` if a frame condition
turns out to be inert, if the published counts are not reproduced through the
committed `carries`/`compose`, if any of `compose`'s eight argument triples is
left unreached, or if a wrong contract assignment escapes both the counts and the
theorems. These need the `z3-solver` package; without it the modules raise rather
than reporting a pass they did not earn.

```bash
PYTHONPATH=src pytest -q tests/unit/study/p7
```
