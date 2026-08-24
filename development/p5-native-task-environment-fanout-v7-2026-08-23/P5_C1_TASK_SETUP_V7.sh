#!/bin/sh
set -eu

EXPECTED_ARCHIVE_SHA256="f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08"
MUTABLE_RELATIVE_PATH="src/main/java/org/apache/commons/lang3/math/NumberUtils.java"

if [ "$#" -ne 2 ]; then
  echo "usage: $0 SOURCE_ARCHIVE EMPTY_TASK_ROOT" >&2
  exit 64
fi

archive=$1
task_root=$2

actual_sha256=$(python3 - "$archive" <<'PY'
import hashlib, pathlib, sys
p = pathlib.Path(sys.argv[1])
h = hashlib.sha256()
with p.open("rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
print(h.hexdigest())
PY
)

if [ "$actual_sha256" != "$EXPECTED_ARCHIVE_SHA256" ]; then
  echo "source archive SHA-256 mismatch" >&2
  exit 65
fi

if [ -e "$task_root" ]; then
  echo "task root must not exist before setup" >&2
  exit 66
fi

mkdir -p "$task_root"
tar -xzf "$archive" --strip-components=1 -C "$task_root"

if [ ! -f "$task_root/$MUTABLE_RELATIVE_PATH" ]; then
  echo "required mutable file missing after extraction" >&2
  exit 67
fi

# Candidate task setup is offline.  The host runner separately enforces the
# V4 write-surface receipt.  These modes make every existing member read-only
# except the single declared source file, without granting directory creation.
find "$task_root" -type d -exec chmod 0555 {} +
find "$task_root" -type f -exec chmod 0444 {} +
chmod 0644 "$task_root/$MUTABLE_RELATIVE_PATH"

printf '%s\n' "P5_C1_TASK_SETUP_V7_OK"
