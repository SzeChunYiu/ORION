#!/usr/bin/env python3
"""P4 V13 edge-91 fresh-compile discriminator (ORION-14.NAT.M6...V12 successor).

V12 terminal: PINNED_COMPILER_RUNTIME_UNAVAILABLE_NO_BUILD_EXECUTED. The pinned
compiler identity is the Eclipse Temurin OpenJDK 17.0.14+7 build (javac 17.0.14,
java 17.0.14+7); V12 attempted to obtain it only as an OCI image, and the OCI route
failed for environmental reasons (no daemon; disposable VM ENOSPC). This probe
obtains the SAME pinned compiler build through its native Adoptium distribution
channel (not a substitute compiler), verifies the distributor checksum, and executes
V12's frozen compile command verbatim:

    find java/src -type f -name '*.java' -print0 | LC_ALL=C sort -z | xargs -0 javac -d /out

against the immutable GitHub codeload checkout of authenticated revision
aa021231cdafb6d74ce9ab5f55f824a3032058a4, then compares every emitted .class file
byte-for-byte against the V12 checksum-bound archive manifest (JAR_PROJECTION_V12.json
observed_manifest), which already proved exact containment of all 106 archive-only
classes in the tracked java/jPAI.jar.

Falsifiable outcome: exact reproduction of all 106 class files upgrades the V12
FRESH_COMPILE_CANNOT_CHECK to a completed compile discriminator; any difference or
failure is recorded as the observed build-reproducibility verdict. Either way this
does NOT close edge 91: the named terminal additionally requires provider-native
build attestation and mode authority, which no local compile can supply.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
V12_JAR_PROJECTION = (ROOT / ".." / "p4-exact-edge-build-provenance-v12-2026-08-24" / "JAR_PROJECTION_V12.json").resolve()
UA = "ORION-P4-public-source-feasibility/1.0 (bounded metadata audit)"
PINNED_VERSION = "jdk-17.0.14+7"
SOURCE_REVISION = "aa021231cdafb6d74ce9ab5f55f824a3032058a4"
ARCH_MAP = {"x86_64": "x64", "aarch64": "aarch64"}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())


def download(url: str, destination: pathlib.Path) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=900) as resp:
        final_url = resp.geturl()
        with destination.open("wb") as handle:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                handle.write(chunk)
    return {"url": url, "final_url": final_url, "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination), "downloaded_at": now()}


def run(cmd: list[str], **kwargs) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return {"cmd": cmd, "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}


def main() -> None:
    machine = platform.machine()
    arch = ARCH_MAP.get(machine)
    if arch is None:
        raise SystemExit(f"unsupported architecture: {machine}")
    os_name = "linux" if platform.system() == "Linux" else "mac"

    log: dict = {"schema_version": "orion.p4.exact-edge.compile-probe.v13.v1",
                 "started_at": now(), "pinned_version": PINNED_VERSION,
                 "source_revision": SOURCE_REVISION, "os": os_name, "arch": arch,
                 "public_development_evidence_only": True, "outcomes_accessed": False}

    # 1. Pin-check the exact Temurin build through its native channel.
    version_quoted = urllib.parse.quote(PINNED_VERSION, safe="")
    assets_url = (f"https://api.adoptium.net/v3/assets/version/{version_quoted}"
                  f"?architecture={arch}&os={os_name}&image_type=jdk")
    assets = fetch_json(assets_url)
    asset = assets[0] if isinstance(assets, list) else assets
    binaries = asset["binaries"] if "binaries" in asset else [asset["binary"]]
    binary = next(b for b in binaries if b.get("architecture") == arch and b.get("os") == os_name)
    pkg = binary["package"]
    log["adoptium_asset"] = {
        "release_name": asset.get("release_name"),
        "version": binary.get("version", {}),
        "vendor": binary.get("vendor"),
        "package_name": pkg["name"],
        "package_sha256": pkg["checksum"],
        "package_bytes": pkg["size"],
        "jvm_impl": binary.get("jvm_impl"),
        "project": binary.get("project"),
    }
    if asset.get("release_name") != PINNED_VERSION:
        raise SystemExit(f"adoptium release_name {asset.get('release_name')} != pin {PINNED_VERSION}")

    workdir = pathlib.Path(tempfile.mkdtemp(prefix="pai_v13_"))
    # 2. Download + verify the pinned JDK package checksum.
    jdk_pkg = workdir / pkg["name"]
    log["jdk_download"] = download(pkg["link"], jdk_pkg)
    if log["jdk_download"]["sha256"] != pkg["checksum"]:
        raise SystemExit("jdk package checksum mismatch")
    with tarfile.open(jdk_pkg) as tf:
        tf.extractall(workdir, filter="data")
    jdk_home = next(p for p in workdir.iterdir() if p.is_dir() and p.name.startswith("jdk-"))
    javac = jdk_home / "bin" / "javac"

    # 3. Immutable source checkout at the authenticated revision.
    src_tgz = workdir / "source.tar.gz"
    log["source_download"] = download(
        f"https://codeload.github.com/NutritionalLungImmunity/PAI/tar.gz/{SOURCE_REVISION}", src_tgz)
    src_root = workdir / "src"
    src_root.mkdir()
    with tarfile.open(src_tgz) as tf:
        tf.extractall(src_root, filter="data")
    repo_dir = next(p for p in src_root.iterdir() if p.is_dir())
    java_src = repo_dir / "java" / "src"
    log["source_layout"] = {
        "repo_dir": repo_dir.name,
        "java_src_exists": java_src.is_dir(),
        "java_file_count": sum(1 for p in java_src.rglob("*.java")) if java_src.is_dir() else 0,
    }

    # 4. Version check, then the frozen compile command verbatim.
    log["javac_version"] = run([str(javac), "-version"])
    log["java_version"] = run([str(jdk_home / "bin" / "java"), "-version"])
    out_dir = workdir / "out"
    out_dir.mkdir()
    log["frozen_command"] = ("find java/src -type f -name '*.java' -print0 | LC_ALL=C sort -z "
                             "| xargs -0 javac -d " + str(out_dir))
    find = subprocess.run(["find", "java/src", "-type", "f", "-name", "*.java", "-print0"],
                          cwd=repo_dir, capture_output=True)
    sorted_files = sorted(find.stdout.split(b"\0"))
    sorted_files = [f for f in sorted_files if f]
    args = [str(javac), "-d", str(out_dir)]
    file_list = []
    for f in sorted_files:
        file_list.append(str(repo_dir / f.decode()))
    log["compile"] = run(args + file_list)
    log["compile"]["input_file_count"] = len(file_list)

    # 5. Byte-exact comparison against the V12 checksum-bound archive manifest.
    projection = json.loads(V12_JAR_PROJECTION.read_text())
    observed = projection["observed_manifest"]
    class_targets = [e for e in observed if e["normalized_path"].startswith("java/bin/")
                     and e["normalized_path"].endswith(".class")]
    results = {"matching": [], "hash_mismatch": [], "missing_from_compile": []}
    compiled: dict[str, str] = {}
    for p in out_dir.rglob("*.class"):
        compiled[str(p.relative_to(out_dir))] = sha256_file(p)
    extra = sorted(set(compiled) - {e["normalized_path"][len("java/bin/"):] for e in class_targets})
    for entry in class_targets:
        rel = entry["normalized_path"][len("java/bin/"):]
        got = compiled.get(rel)
        if got is None:
            results["missing_from_compile"].append(rel)
        elif got == entry["sha256"]:
            results["matching"].append(rel)
        else:
            results["hash_mismatch"].append({"path": rel, "expected": entry["sha256"], "observed": got})
    log["class_projection_v13"] = {
        "expected_class_count": len(class_targets),
        "matching_count": len(results["matching"]),
        "hash_mismatch": results["hash_mismatch"],
        "missing_from_compile": results["missing_from_compile"],
        "extra_classes_beyond_archive": sorted(extra),
        "exact": (len(results["matching"]) == len(class_targets)
                  and not results["hash_mismatch"]
                  and not results["missing_from_compile"]),
    }
    log["finished_at"] = now()
    (ROOT / "COMPILE_PROJECTION_V13.json").write_bytes(
        (json.dumps(log, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps({"pinned": asset.get("release_name"),
                      "compile_rc": log["compile"]["returncode"],
                      "compiled_class_count": len(compiled),
                      "projection": {k: v if not isinstance(v, list) else len(v)
                                     for k, v in log["class_projection_v13"].items()}}, indent=2))
    shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
