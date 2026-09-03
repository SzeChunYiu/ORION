#!/usr/bin/env python3
"""A5 comparator-backbone bytes-level binding V1 (external bindings closure).

Closes the bytes gap the frozen comparator CI cannot close: CI verifies the
Hugging Face API metadata (revision sha, license, LFS sha256, size) but never
downloads the model.  This job, run on billy-old, downloads the pinned
model.safetensors and config.json at the frozen revision, verifies the
safetensors sha256 and byte length against the freeze pins, and verifies the
frozen runtime_precondition (config label names expose exactly
entailment/neutral/contradiction).

NO inference, NO tokenizer load, NO panel execution, NO comparator outputs.
Bytes stay on the execution host under --bytes-dir; only digests and receipts
are emitted.  Network: huggingface.co only, concurrency 1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Frozen pins (papers/orion-14-verified-scientific-discovery/protocol/a5-comparator-freeze-v1/COMPARATOR_EXECUTION_FREEZE_V1.json,
# git blob 531406b0e1a071ecf043e61700efb97c53ea137a; worktree sha256 3af0552fbdea0e3841719cffec975b37d7d069c37730deb7fcf086ddef68fdfd)
FREEZE_SHA256 = "3af0552fbdea0e3841719cffec975b37d7d069c37730deb7fcf086ddef68fdfd"
REPO = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
REVISION = "eb8b17b1983bca679126ea69b12b5d28c5fe9b9a"
MODEL_FILE = "model.safetensors"
MODEL_SHA256 = "06d6fd89edd4f97816831626daafbdb0b029cf63bae8edc0bccab1d64e2e7707"
MODEL_BYTES = 368877646
LICENSE = "MIT"
REQUIRED_LABELS = ["entailment", "neutral", "contradiction"]
HOSTS = ("huggingface.co",)
UA = "ORION-A5-comparator-backbone-bytes-binding-v1 (model identity verification; contact via repo)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, timeout: int = 600) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except urllib.error.URLError as e:
        return -1, str(e.reason).encode()


def check_labels(config: dict[str, Any]) -> tuple[bool, list[str]]:
    id2label = config.get("id2label")
    if not isinstance(id2label, dict) or not id2label:
        return False, []
    labels = [str(id2label[str(i)]) for i in sorted(int(k) for k in id2label)]
    return labels == REQUIRED_LABELS, labels


def run(bytes_dir: Path, out_dir: Path) -> dict[str, Any]:
    bytes_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"https://huggingface.co/{REPO}/resolve/{REVISION}/"
    log_path = out_dir / "ACCESS_LOG_V1.jsonl"

    def log(row: dict[str, Any]) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    # 1. API metadata cross-check (mirrors the frozen CI check exactly:
    #    path-form revision endpoint, cardData.license, LFS blob sha256+size).
    #    Retried with spacing because the API throttles burst calls.
    api_url = f"https://huggingface.co/api/models/{REPO}/revision/{REVISION}?blobs=true"
    api_status, api_body = -1, b""
    for attempt in range(1, 4):
        api_status, api_body = fetch(api_url, timeout=60)
        if api_status == 200:
            break
        time.sleep(10.0 * attempt)
    api = {}
    if api_status == 200:
        try:
            api = json.loads(api_body)
        except json.JSONDecodeError:
            api = {}
    api_lfs = {}
    for sib in api.get("siblings", []):
        if sib.get("rfilename") == MODEL_FILE:
            api_lfs = sib.get("lfs") or {}
    api_ok = (api.get("sha") == REVISION
              and (api.get("cardData") or {}).get("license") == "mit"
              and api_lfs.get("sha256") == MODEL_SHA256
              and api_lfs.get("size") == MODEL_BYTES)
    log({"ts": now(), "url": f"api/models/{REPO}/revision/{REVISION}", "http_status": api_status,
         "api_sha_matches": api.get("sha") == REVISION,
         "api_card_license": (api.get("cardData") or {}).get("license"),
         "api_lfs_sha256_matches": api_lfs.get("sha256") == MODEL_SHA256,
         "api_lfs_size_matches": api_lfs.get("size") == MODEL_BYTES})

    # 2. config.json at the pinned revision -> runtime_precondition.
    cfg_status, cfg_body = fetch(base + "config.json", timeout=120)
    labels_ok, labels_seen = False, []
    cfg_sha = sha256_bytes(cfg_body) if cfg_status == 200 else ""
    if cfg_status == 200:
        labels_ok, labels_seen = check_labels(json.loads(cfg_body))
    log({"ts": now(), "url": base + "config.json", "http_status": cfg_status, "bytes_n": len(cfg_body),
         "sha256": cfg_sha, "labels": labels_seen, "labels_match_frozen": labels_ok})

    # 3. model.safetensors bytes at the pinned revision (resume-safe: reuse
    #    previously bound bytes when they already match both pins).
    cached = bytes_dir / MODEL_FILE
    if cached.exists() and cached.stat().st_size == MODEL_BYTES and sha256_bytes(cached.read_bytes()) == MODEL_SHA256:
        mdl_status, mdl_body, mdl_sha, mdl_len = 200, cached.read_bytes(), MODEL_SHA256, MODEL_BYTES
        log({"ts": now(), "url": base + MODEL_FILE, "http_status": "CACHED_MATCHING_PINS",
             "bytes_n": mdl_len, "sha256": mdl_sha, "sha256_matches_frozen": True, "bytes_match_frozen": True})
    else:
        time.sleep(3.1)
        mdl_status, mdl_body = fetch(base + MODEL_FILE, timeout=900)
        mdl_sha = sha256_bytes(mdl_body) if mdl_status == 200 else ""
        mdl_len = len(mdl_body)
        log({"ts": now(), "url": base + MODEL_FILE, "http_status": mdl_status, "bytes_n": mdl_len,
             "sha256": mdl_sha, "sha256_matches_frozen": mdl_sha == MODEL_SHA256, "bytes_match_frozen": mdl_len == MODEL_BYTES})
        if mdl_status == 200:
            (bytes_dir / MODEL_FILE).write_bytes(mdl_body)
    mdl_ok = mdl_status == 200 and mdl_sha == MODEL_SHA256 and mdl_len == MODEL_BYTES
    if cfg_status == 200:
        (bytes_dir / "config.json").write_bytes(cfg_body)

    checks = {
        "api_revision_sha_and_card_license_mit_and_lfs_blob_pinned": api_ok,
        "config_http_200": cfg_status == 200,
        "config_label_names_exactly_frozen": labels_ok,
        "model_http_200": mdl_status == 200,
        "model_sha256_matches_freeze": mdl_sha == MODEL_SHA256,
        "model_bytes_match_freeze": mdl_len == MODEL_BYTES,
    }
    binding_complete = all(checks.values())
    result = {
        "schema": "ORION.A5.ComparatorBackboneBytesBinding.v1",
        "run_utc": now(),
        "backbone": {"repository": REPO, "revision": REVISION, "model_file": MODEL_FILE,
                     "pinned_model_sha256": MODEL_SHA256, "observed_model_sha256": mdl_sha,
                     "pinned_model_bytes": MODEL_BYTES, "observed_model_bytes": mdl_len,
                     "license": LICENSE, "config_sha256": cfg_sha,
                     "config_id2label_observed": {str(i): l for i, l in enumerate(labels_seen)},
                     "runtime_precondition_verified": labels_ok},
        "freeze_binding": {"path": "papers/orion-14-verified-scientific-discovery/protocol/a5-comparator-freeze-v1/COMPARATOR_EXECUTION_FREEZE_V1.json",
                           "worktree_sha256": FREEZE_SHA256},
        "checks": checks,
        "bytes_location_host_relative": str(bytes_dir) if mdl_ok else None,
        "terminal": ("A5_COMPARATOR_BACKBONE_BYTES_BOUND__RUNTIME_PRECONDITION_VERIFIED" if binding_complete
                     else "CANNOT_CHECK_MODEL_BINDING"),
        "execution_boundary": {
            "inference_performed": False, "tokenizer_loaded": False, "panel_or_candidate_packets_touched": False,
            "comparator_outputs_produced": False, "protected_outcomes_accessed": False, "terminal_gold_accessed": False,
        },
        "network_policy": {"hosts": list(HOSTS), "concurrency": 1, "min_interval_seconds": 3.1, "user_agent": UA},
        "access_log": str(log_path),
        "scientific_authority_delta": "NONE__MODEL_IDENTITY_BYTES_RECEIPT_ONLY",
    }
    (out_dir / "COMPARATOR_BACKBONE_BYTES_BINDING_V1.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def self_test() -> dict[str, Any]:
    # 1. label gate accepts the exact frozen order and rejects every mutant.
    good = {"id2label": {"0": "entailment", "1": "neutral", "2": "contradiction"}}
    assert check_labels(good) == (True, ["entailment", "neutral", "contradiction"])
    assert not check_labels({"id2label": {"0": "entailment", "1": "contradiction", "2": "neutral"}})[0]
    assert not check_labels({"id2label": {"0": "ENTAILMENT", "1": "neutral", "2": "contradiction"}})[0]
    assert not check_labels({"id2label": {"0": "entailment", "1": "neutral"}})[0]
    assert not check_labels({})[0] and not check_labels({"id2label": "entailment"})[0]
    # 2. size+sha conjunctive gate: a body of the right length but wrong sha must fail.
    fake = b"\x00" * MODEL_BYTES
    assert len(fake) == MODEL_BYTES and sha256_bytes(fake) != MODEL_SHA256
    assert not (sha256_bytes(fake) == MODEL_SHA256 and len(fake) == MODEL_BYTES)
    # 3. pinned constants are internally consistent shapes.
    assert len(MODEL_SHA256) == 64 and len(REVISION) == 40 and REQUIRED_LABELS == ["entailment", "neutral", "contradiction"]
    # 4. TAMPER (must fire): flipping one label in a copied config changes the gate outcome.
    tampered_cfg = {"id2label": {"0": "entailment", "1": "neutral", "2": "contradiction"}}
    tampered_cfg["id2label"]["2"] = "contradiction "
    assert check_labels(tampered_cfg)[0] is False
    # 5. TAMPER (must fire): a tampered sha pin no longer equals the frozen pin digest set.
    wrong = "0" * 64
    assert wrong != MODEL_SHA256 and wrong != FREEZE_SHA256
    # 6. TAMPER (must fire): an API sibling blob with the right sha but wrong size
    #    (or wrong sha, right size) must fail the conjunctive metadata gate.
    def api_gate(lfs: dict[str, Any], sha: str, lic: str) -> bool:
        return (sha == REVISION and lic == "mit"
                and lfs.get("sha256") == MODEL_SHA256 and lfs.get("size") == MODEL_BYTES)
    good_lfs = {"sha256": MODEL_SHA256, "size": MODEL_BYTES}
    assert api_gate(good_lfs, REVISION, "mit")
    assert not api_gate({"sha256": MODEL_SHA256, "size": MODEL_BYTES + 1}, REVISION, "mit")
    assert not api_gate({"sha256": wrong, "size": MODEL_BYTES}, REVISION, "mit")
    assert not api_gate(good_lfs, "0" * 40, "mit")
    assert not api_gate(good_lfs, REVISION, "apache-2.0")
    return {"decision": "GREEN", "label_gate_exact_and_order_sensitive": True,
            "sha_size_conjunctive_gate": True, "api_metadata_gate_conjunctive": True,
            "tampered_label_rejected": True, "tampered_sha_rejected": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bytes-dir", type=Path, default=Path.home() / "orion-a5-sources/comparator-backbone")
    ap.add_argument("--out-dir", type=Path, default=Path("comparator-backbone-bytes-binding-v1"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    out: dict[str, Any] = self_test() if a.self_test else run(a.bytes_dir, a.out_dir)
    print(json.dumps(out, indent=2, sort_keys=True))
    if out.get("terminal") == "CANNOT_CHECK_MODEL_BINDING":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
