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
python generate_tasks.py
python run_round2.py --engine "$prefix/bin/openssl"
python run_round2.py --engine "$prefix/bin/openssl" --check-final
```

`run_round2.py` checks the native engine version and fails closed if it is not
OpenSSL 3.6.4. The recipe does not certify that a host can build OpenSSL, and a
failed or unavailable build remains `CANNOT_CHECK`.
