#!/usr/bin/env python3
"""Capture the V4/V4A official source routes without case or outcome access.

This is a rerun utility. Mutable-page byte drift must be treated as a new
capture, not silently equated with the receipt in this packet.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LANE = Path(__file__).resolve().parent
TMP = LANE / ".capture_tmp"
UA = "orion-p1-construct-audit/4.0 (+public-scientific-provenance; no-case-access)"
ROUTES = [
    ("NISO_CREC_RP45_LANDING.html", "https://www.niso.org/publications/rp-45-2024-crec"),
    ("NISO_CREC_RP45_PDF.pdf", "https://groups.niso.org/higherlogic/ws/public/download/30869/NISO_RP-45-2024_CREC.pdf"),
    ("CROSSREF_CROSSMARK.html", "https://www.crossref.org/documentation/crossmark/"),
    ("CROSSREF_POLICY_PAGE.html", "https://www.crossref.org/documentation/crossmark/crossmark-policy-page/"),
    ("CROSSREF_RELATIONSHIPS.html", "https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/relationships/"),
    ("NLM_JATS_RELATED_ARTICLE.html", "https://jats.nlm.nih.gov/publishing/tag-library/1.4/element/related-article.html"),
    ("COPE_RETRACTION_GUIDELINES.html", "https://publicationethics.org/retraction-guidelines"),
    ("COPE_RETRACTION_GUIDELINES_PDF.pdf", "https://publicationethics.org/media/848/download?attachment"),
    ("ICMJE_CORRECTIONS_ROUTE.html", "https://www.icmje.org/recommendations/browse/publishing-and-editorial-issues/corrections-retractions-republications-and-version-control.html"),
]


def main() -> None:
    TMP.mkdir(exist_ok=False)
    rows = []
    for filename, url in ROUTES:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                body = response.read()
                status = response.status
                final_url = response.geturl()
                headers = dict(response.headers)
        except urllib.error.HTTPError as error:
            body = error.read()
            status = error.code
            final_url = error.geturl()
            headers = dict(error.headers)
        path = TMP / filename
        path.write_bytes(body)
        rows.append({
            "filename": filename,
            "requested_url": url,
            "final_url": final_url,
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "http_status": status,
            "content_type": headers.get("Content-Type"),
            "content_length_bytes": len(body),
            "response_sha256": hashlib.sha256(body).hexdigest(),
            "last_modified": headers.get("Last-Modified"),
            "etag": headers.get("ETag"),
        })
    for stem in ("NISO_CREC_RP45_PDF", "COPE_RETRACTION_GUIDELINES_PDF"):
        subprocess.run(
            ["pdftotext", str(TMP / f"{stem}.pdf"), str(TMP / f"{stem}.txt")],
            check=True,
        )
    (TMP / "CAPTURE_METADATA.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "CAPTURED", "routes": len(rows), "temporary_directory": str(TMP)}, sort_keys=True))
    print("Run build_v4.py to produce bounded artifacts and delete temporary source bytes.")


if __name__ == "__main__":
    main()
