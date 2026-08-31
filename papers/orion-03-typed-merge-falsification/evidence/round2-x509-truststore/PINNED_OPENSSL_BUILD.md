# Pinned OpenSSL 3.6.4 build recipe

This recipe materializes the native engine required for a full Round-2 replay.
It does not run automatically and does not convert missing build tools into a
pass.

```sh
set -eu
url=https://github.com/openssl/openssl/releases/download/openssl-3.6.4/openssl-3.6.4.tar.gz
archive=openssl-3.6.4.tar.gz
prefix="$PWD/openssl-3.6.4-install"

curl -fL "$url" -o "$archive"
printf '%s  %s\n' \
  9bffaa1ad1e07b354c21bd3324ec02fa15579f45a7d0494b3e74bc449b7333ef \
  "$archive" | shasum -a 256 -c -

tar -xzf "$archive"
cd openssl-3.6.4
./Configure --prefix="$prefix" --openssldir="$prefix/ssl" no-shared
make -j2
make install_sw
"$prefix/bin/openssl" version -a
```

From the Round-2 evidence directory, replay with:

```sh
set -eu
prefix="${OPENSSL_PREFIX:-$PWD/openssl-3.6.4-install}"
evidence_dir="$PWD"
replay="$(mktemp -d "${TMPDIR:-/tmp}/orion03-r2-replay.XXXXXX")"
cleanup() {
  trap '' HUP INT TERM
  rm -rf "$replay"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

mkdir "$replay/frozen" "$replay/run"
cp TASK_MANIFEST_V2.json UPSTREAM_TABLE_V2.json \
  ROUND2_RESULTS_V2.json COST_ROUND2_V2.json "$replay/frozen/"
cp generate_tasks.py run_round2.py "$replay/run/"
ln -s "$evidence_dir/third_party" "$replay/run/third_party"
cd "$replay/run"
python generate_tasks.py
cmp "$replay/frozen/TASK_MANIFEST_V2.json" TASK_MANIFEST_V2.json
cmp "$replay/frozen/UPSTREAM_TABLE_V2.json" UPSTREAM_TABLE_V2.json
python run_round2.py --engine "$prefix/bin/openssl" \
  --results "$replay/frozen/ROUND2_RESULTS_V2.json" \
  --cost-out "$replay/frozen/COST_ROUND2_V2.json" \
  --check-final
```

Set `OPENSSL_PREFIX` only if the pinned installation was written elsewhere.

The replay runs in a disposable directory. The four published receipts are
copied once into its read-only comparison set before either Python program is
invoked; the generator and evaluator never run in the evidence directory. The
`cmp` steps reject generated task drift, while the only evaluator invocation
uses `--check-final` against the copied result and cost receipts. An interrupt
during the initial copy can therefore affect only the disposable directory,
not the published files, and cleanup never copies bytes back into the evidence
tree. A wrong-but-deterministic generator or engine fails against the published
snapshot rather than rebasing the check onto its own outputs.

`run_round2.py` checks the native engine version and fails closed if it is not
OpenSSL 3.6.4. The recipe does not certify that a host can build OpenSSL, and a
failed or unavailable build remains `CANNOT_CHECK`.
