#!/bin/sh
# Fetch the campaign's own import-graph builder. It is NOT vendored here: the
# single source of truth stays in the campaign packet, and this script records
# exactly which revision was used.
#
# Provenance of the builder used for COHORT_V1.json:
#   branch : origin/shadow/orion17-density-v2-recovery-20260829
#   path   : papers/orion-17-epistemic-navigation-open-worlds/transitions/measure_p7_closure_retention_v1.py
#
# The density packet (theory/density-prospective-v1/) is NOT on main; it lives on
# that shadow branch. o17_density.py in that packet has sha256
#   dd642ecd92704fecc156cd197b074a42de26d0100b98efcd094ab4bd5f777c02
set -eu
BRANCH="${1:-origin/shadow/orion17-density-v2-recovery-20260829}"
SRC="papers/orion-17-epistemic-navigation-open-worlds/transitions/measure_p7_closure_retention_v1.py"
git show "$BRANCH:$SRC" > measure_p7.py
echo "wrote measure_p7.py from $BRANCH:$SRC"
