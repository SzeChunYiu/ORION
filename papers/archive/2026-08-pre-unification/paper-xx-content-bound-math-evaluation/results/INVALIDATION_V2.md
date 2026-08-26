# P10 Mathlib transfer V2 — invalidated result

The generated `MATHLIB_TRANSFER_V2` artifacts are retained as negative history
and support **no scientific claim**.

After the outcome was generated, a hostile parser audit found that the inherited
source projector ended theorem/lemma blocks only at the next theorem/lemma. A
block could therefore span intervening top-level definitions, instances,
sections, namespaces or other commands and attribute unrelated tactic-like text
to the preceding proof.

On the exact frozen corpus:

- projected trajectories: 4,861;
- trajectories crossing at least one intervening top-level command: 1,289
  (26.52%);
- leaked top-level boundaries: 3,903.

`PARSER_CONTAMINATION_AUDIT_V2.json` is the machine-readable receipt. The V2
numerical gate's apparent pass is invalid. The required repair is to stop every
projected declaration at the next recognized top-level command, add hostile
boundary tests, freeze a V2.1 protocol amendment, and rerun the complete study.
