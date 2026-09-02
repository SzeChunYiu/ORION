# Question

Starting from ORION-14 and descending through ORION-10, which issue #1701
obligations can be closed or made integration-ready without re-running completed
science, importing a diverged branch wholesale, changing manuscript bytes, or
overstating external authority?

## Decision rule

- recover only additive, source-bound evidence directories whose live-main paths
  are absent;
- mark already-landed evidence as canonical rather than duplicating it;
- preserve every null, adverse, instrument-fault and `CANNOT_CHECK` state;
- treat a closeout package as filing-valid only for the exact source bytes that
  generated it;
- leave optional successor science under a separate identity.
