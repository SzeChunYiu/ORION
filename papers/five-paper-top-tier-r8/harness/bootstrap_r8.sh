#!/usr/bin/env bash
set -euo pipefail
WS="${1:-.orion-five-paper-r8}"
rm -rf "$WS"
orion-harness mechanics-coverage > papers/five-paper-top-tier-r8/harness/mechanics-coverage.json
orion-harness execution-coverage > papers/five-paper-top-tier-r8/harness/execution-coverage.json
orion-harness init "$WS" --project-root . --allow-process-tools

orion-harness problem-add "$WS" AB-R8-TOP-TIER \
  "Determine whether the consolidated normal-form/certificate theory has a faithful non-Q1 production realization and a contribution surviving current nearest-work subtraction." \
  --scope "AB consolidated theory; exclude Q1 authority and physical-resource claims" \
  --domain exact-optimization --domain parity-compilation --domain rewriting \
  --criterion "Audit every theorem and omitted premise adversarially." \
  --criterion "Find a complete external move inventory or preserve CANNOT_CHECK." \
  --criterion "Do not infer generic runtime or novelty from the toy XOR grammar."

orion-harness problem-add "$WS" C-R8-TOP-TIER \
  "Determine whether FiberGuard's exact three-domain collisions and refinement experiment constitute a scalable, correctly positioned representation-safety contribution for learned combinatorial optimization." \
  --scope "graph colouring, set cover, 2-CNF; representation-only targets" \
  --domain machine-learning --domain combinatorial-optimization --domain decision-theory \
  --criterion "Independently replay every finite count and endpoint." \
  --criterion "Compare full primary sources, not abstracts only." \
  --criterion "Test at least one scaling boundary before an all-size interpretation."

orion-harness problem-add "$WS" D-R8-TOP-TIER \
  "Determine the exact residual contribution of typed authority and merge safety after recursive-Datalog/provenance subtraction, and obtain a real domain-policy validation if possible." \
  --scope "finite positive capped rule systems; no negation/probability/compliance inference" \
  --domain datalog --domain provenance --domain agent-safety --domain policy \
  --criterion "Withdraw donor-owned support/hitting-set novelty." \
  --criterion "Replay the hostile merge census independently." \
  --criterion "Require domain-expert confirmation for a real policy case."

orion-harness problem-add "$WS" NQ-R8-TOP-TIER \
  "Establish clean-room authority for the exact early generalized Davenport constants and attack the first lift-aware 27-diagonal source stratum without overclaiming D4." \
  --scope "C_5^3 exact D2/D3, short spectrum, 27-diagonal lift-aware solver" \
  --domain additive-combinatorics --domain exact-computation --domain formal-verification \
  --criterion "Two structurally independent finite engines." \
  --criterion "Every UNSAT has a certificate or independent complete replay." \
  --criterion "D4 remains open unless every remaining stratum is closed."

for P in AB-R8-TOP-TIER C-R8-TOP-TIER D-R8-TOP-TIER NQ-R8-TOP-TIER; do
  set +e
  orion-harness solve "$WS" "$P" --max-iterations 1 --max-recursion-depth 4 --max-recursive-nodes 24 --max-children-per-problem 10 --max-children-per-residual 10 > "papers/five-paper-top-tier-r8/harness/${P}.initial.json"
  rc=$?
  set -e
  if [[ $rc -ne 0 && $rc -ne 2 ]]; then
    echo "unexpected harness exit $rc for $P" >&2
    exit "$rc"
  fi
done
orion-harness pending "$WS" > papers/five-paper-top-tier-r8/harness/pending-initial.json
orion-harness handoff "$WS" > papers/five-paper-top-tier-r8/harness/HOST_HANDOFF_INITIAL.md
