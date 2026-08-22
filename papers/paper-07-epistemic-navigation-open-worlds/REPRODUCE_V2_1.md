# P7 reproduce V2.1

Run from repository root:

```bash
PYTHONPATH=src python papers/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py
PYTHONPATH=src python papers/paper-07-epistemic-navigation-open-worlds/formal/check_contract_manifest_v2.py
```

Expected sentinels:

```text
P7 THEORY CLOSURE V2: PASS
theory_closure_terminal: CANNOT_CHECK
P7 CONTRACT MANIFEST V2: PASS
```

The first command checks the closed theorems/countermodels. Its `PASS` banner reports assertion status only — every finite witness in the file held — and `theory_closure_terminal` is the verdict on what those witnesses establish. It is `CANNOT_CHECK`, and `check_support_transport` is why: the check enumerates all 64 transport-coordinate combinations and **decides 1 of them** from the witness coordinates alone (a complete witness transports closure). The other 63 turn on Definition 14 target-ambiguity, which the six-coordinate `Transport` model does not carry, so it reports the premise and what the premise is decided from rather than a case count. The 64 is the size of the enumeration; it is not a count of decided cases, and earlier versions of this file read it as one. The second command executes all 8 frozen prospective contract cases, including harmful-reframe and non-retrieval experimental-design transfer controls.

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
  --output papers/paper-07-epistemic-navigation-open-worlds/formal/mechanized/P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json
PYTHONPATH=src python -m orion.study.p7.donor_stack_as_transformation_family --repo-root . \
  --date 2026-08-22 \
  --output papers/paper-07-epistemic-navigation-open-worlds/formal/mechanized/P7_DONOR_STACK_AS_TRANSFORMATION_FAMILY_2026-08-22.json
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
