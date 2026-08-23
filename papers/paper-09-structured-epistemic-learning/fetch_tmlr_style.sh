#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/manuscript"
COMMIT="7bf90efe3a0debbba703c05c43f3ff7e4d4a2992"
STY_BLOB="c0c62d03c6e2383c688b20965de03800dc15c79c"
BST_BLOB="310ed3e74455269ad97d0b30639851af72cec965"
REPO="https://github.com/JmlrOrg/tmlr-style-file.git"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git -C "$TMP" init -q
git -C "$TMP" remote add origin "$REPO"
git -C "$TMP" fetch -q --depth 1 origin "$COMMIT"
git -C "$TMP" checkout -q FETCH_HEAD -- tmlr.sty tmlr.bst

actual_sty="$(git -C "$TMP" hash-object tmlr.sty)"
actual_bst="$(git -C "$TMP" hash-object tmlr.bst)"

if [[ "$actual_sty" != "$STY_BLOB" ]]; then
  echo "TMLR style blob mismatch: $actual_sty != $STY_BLOB" >&2
  exit 1
fi
if [[ "$actual_bst" != "$BST_BLOB" ]]; then
  echo "TMLR bibliography blob mismatch: $actual_bst != $BST_BLOB" >&2
  exit 1
fi

cp "$TMP/tmlr.sty" "$OUT/tmlr.sty"
cp "$TMP/tmlr.bst" "$OUT/tmlr.bst"

echo "TMLR_STYLE_COMMIT=$COMMIT"
echo "TMLR_STY_BLOB=$actual_sty"
echo "TMLR_BST_BLOB=$actual_bst"
