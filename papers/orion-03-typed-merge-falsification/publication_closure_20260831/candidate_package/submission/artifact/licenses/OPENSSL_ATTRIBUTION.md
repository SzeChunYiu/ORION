# Third-party source: OpenSSL test certificates and verify table

All vendored material in `third_party/openssl-3.6.4-testcerts/` originates
from the OpenSSL Project official repository
(https://github.com/openssl/openssl), release tag `openssl-3.6.4`
(commit `d3c1b1169b3569ff3069e5b399f47b2b28e03d79`).

  Copyright (c) 1998-2026 The OpenSSL Project Authors
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use these files except in compliance with the License.
  You may obtain a copy of the License at
  https://www.openssl.org/source/license.html

Vendored bytes are UNMODIFIED. Selection is content-based (see
PROTOCOL_V2.md section 2): every file containing at least one
CERTIFICATE / TRUSTED-CERTIFICATE / X509-CRL PEM block and no private-key
block was copied verbatim; all other files are listed with reasons in
`third_party/openssl-3.6.4-testcerts/EXCLUDED_FILES.txt`. Per-file identity
bindings are in `SOURCE_BINDING_V2.json`.

The pinned engine (OpenSSL 3.6.4) is built from the same sha256-verified
tarball. The fail-closed build and replay commands are recorded in
`PINNED_OPENSSL_BUILD.md` and `README.md`.
