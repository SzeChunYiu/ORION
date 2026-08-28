#!/usr/bin/env python3
"""Independent ORION-03 Round 2 model-based receipt reproduction."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


PROTOCOL_ID = "ORION-03-Round2-TrustStoreMerge-V2"
ENGINE_PREFIX = "OpenSSL 3.6.4"
DEFAULT_ATTIME = 1759276800
TIMEOUT_SECONDS = 30


class ReproductionError(Exception):
    pass


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ReproductionError(f"cannot read required input {path.name}: {exc}") from exc


def load_json(path):
    try:
        value = json.loads(read_bytes(path))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReproductionError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReproductionError(f"top level of {path.name} is not an object")
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def receipt_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=1, ensure_ascii=True) + "\n").encode()


def one_line_version(engine, env):
    try:
        proc = subprocess.run(
            [str(engine), "version"], capture_output=True, env=env,
            timeout=TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReproductionError(f"engine version check failed: {exc}") from exc
    if proc.returncode != 0:
        raise ReproductionError("engine version command returned nonzero")
    try:
        lines = proc.stdout.decode("utf-8", "strict").splitlines()
    except UnicodeDecodeError as exc:
        raise ReproductionError("engine version output is not UTF-8") from exc
    if not lines or not lines[0].startswith(ENGINE_PREFIX):
        raise ReproductionError(f"engine version must start with {ENGINE_PREFIX!r}")
    return lines[0]


def validate_options(opts):
    if not isinstance(opts, list) or not all(isinstance(x, str) and x for x in opts):
        raise ReproductionError("task opts must be a list of nonempty strings")
    no_arg = {"-partial_chain"}
    one_arg = {"-auth_level", "-verify_depth", "-attime"}
    i = 0
    seen = set()
    while i < len(opts):
        flag = opts[i]
        if flag in seen or flag not in no_arg | one_arg:
            raise ReproductionError(f"duplicate or unsupported task option {flag!r}")
        seen.add(flag)
        if flag in one_arg:
            if i + 1 >= len(opts) or not opts[i + 1].isdigit():
                raise ReproductionError(f"malformed value for task option {flag!r}")
            i += 2
        else:
            i += 1
    return tuple(opts), "-attime" in seen


def pem_kinds(data):
    return (
        b"-----BEGIN CERTIFICATE-----" in data
        or b"-----BEGIN TRUSTED CERTIFICATE-----" in data,
        b"-----BEGIN X509 CRL-----" in data,
    )


def load_and_validate_inputs(root):
    # The outcome-isolated implementation was developed with the allowed
    # inputs under ``evidence/``.  In the repository it is packaged beside
    # those inputs, so accept exactly those two layouts and no search path.
    if (root / "SOURCE_BINDING_V2.json").is_file():
        evidence = root
    else:
        evidence = root / "evidence"
    binding_path = evidence / "SOURCE_BINDING_V2.json"
    manifest_path = evidence / "TASK_MANIFEST_V2.json"
    protocol_path = evidence / "PROTOCOL_V2.md"
    binding = load_json(binding_path)
    frozen = binding.get("frozen_artifacts")
    if not isinstance(frozen, dict):
        raise ReproductionError("source binding lacks frozen_artifacts")
    for name, path in (("PROTOCOL_V2.md", protocol_path),
                       ("TASK_MANIFEST_V2.json", manifest_path)):
        expected = frozen.get(name)
        if not isinstance(expected, str) or len(expected) != 64:
            raise ReproductionError(f"source binding lacks valid hash for {name}")
        if sha256_bytes(read_bytes(path)) != expected:
            raise ReproductionError(f"frozen hash mismatch for {name}")
    # The bound protocol document plus its manifest identifier form the frozen
    # protocol identity; the prose document does not carry the machine token.
    read_bytes(protocol_path)
    manifest = load_json(manifest_path)
    if manifest.get("protocol") != PROTOCOL_ID:
        raise ReproductionError("manifest protocol identity mismatch")
    if manifest.get("frozen_attime") != DEFAULT_ATTIME:
        raise ReproductionError("manifest frozen attime disagrees with protocol")

    declared = binding.get("vendored_files")
    if not isinstance(declared, dict) or not declared:
        raise ReproductionError("source binding has no vendored_files map")
    corpus = evidence / "third_party" / "openssl-3.6.4-testcerts"
    materials = {}
    for rel, expected in sorted(declared.items()):
        if not isinstance(rel, str) or not rel.startswith("test/certs/") or ".." in Path(rel).parts:
            raise ReproductionError(f"invalid vendored material path {rel!r}")
        if not isinstance(expected, str) or len(expected) != 64:
            raise ReproductionError(f"invalid vendored hash for {rel}")
        data = read_bytes(corpus / rel)
        if sha256_bytes(data) != expected:
            raise ReproductionError(f"vendored hash mismatch for {rel}")
        short = rel[len("test/certs/"):]
        if short in materials:
            raise ReproductionError(f"duplicate vendored material identity {short}")
        materials[short] = (data, pem_kinds(data))
    recipe = binding.get("vendored_recipe")
    if not isinstance(recipe, dict):
        raise ReproductionError("source binding lacks vendored_recipe")
    for rel, expected in sorted(recipe.items()):
        data = read_bytes(corpus / rel)
        if sha256_bytes(data) != expected:
            raise ReproductionError(f"vendored recipe hash mismatch for {rel}")
    excluded = binding.get("excluded_list")
    if not isinstance(excluded, dict):
        raise ReproductionError("source binding lacks excluded_list")
    for rel, expected in sorted(excluded.items()):
        data = read_bytes(corpus / rel)
        if sha256_bytes(data) != expected:
            raise ReproductionError(f"excluded-list hash mismatch for {rel}")
    if manifest.get("vendored_files") != len(declared):
        raise ReproductionError("manifest vendored file count mismatch")
    return binding, manifest, materials


def resolve_material(name, materials):
    if not isinstance(name, str) or not name or "/" in name or "\\" in name:
        raise ReproductionError(f"malformed material identity {name!r}")
    candidates = [name]
    if not name.endswith(".pem"):
        candidates.append(name + ".pem")
    hits = [candidate for candidate in candidates if candidate in materials]
    if len(hits) != 1:
        raise ReproductionError(f"missing or ambiguous material {name!r}")
    return hits[0]


def normalize_role(values, materials, task_id, role):
    if not isinstance(values, list):
        raise ReproductionError(f"{task_id}: {role} is not a list")
    names = tuple(resolve_material(x, materials) for x in values)
    if len(names) != len(set(names)):
        raise ReproductionError(f"{task_id}: duplicate/overlapping members in {role}")
    names = tuple(sorted(names))
    for name in names:
        has_cert, has_crl = materials[name][1]
        if not has_cert:
            qualifier = "CRL-only" if has_crl else "certificate-free"
            raise ReproductionError(f"{task_id}: unexpected {qualifier} store member {name}")
    return names


def normalize_tasks(manifest, materials):
    tasks = manifest.get("tasks")
    families = manifest.get("families")
    if not isinstance(tasks, list) or not isinstance(families, dict) or not families:
        raise ReproductionError("manifest tasks/families metadata is malformed")
    seen = set()
    normalized = []
    actual_family = {name: 0 for name in families}
    for raw in tasks:
        if not isinstance(raw, dict):
            raise ReproductionError("task is not an object")
        task_id = raw.get("task_id")
        family = raw.get("family")
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise ReproductionError(f"duplicate or malformed task ID {task_id!r}")
        seen.add(task_id)
        if family not in actual_family:
            raise ReproductionError(f"{task_id}: undeclared family {family!r}")
        leaf = resolve_material(raw.get("leaf"), materials)
        if not materials[leaf][1][0]:
            raise ReproductionError(f"{task_id}: leaf is not certificate-bearing")
        purpose = raw.get("purpose")
        if not isinstance(purpose, str):
            raise ReproductionError(f"{task_id}: malformed purpose")
        opts, has_attime = validate_options(raw.get("opts"))
        states = []
        for key in ("state_a", "state_b"):
            state = raw.get(key)
            if not isinstance(state, dict) or set(state) != {"trusted", "untrusted"}:
                raise ReproductionError(f"{task_id}: malformed {key}")
            states.append((normalize_role(state["trusted"], materials, task_id, key + ".trusted"),
                           normalize_role(state["untrusted"], materials, task_id, key + ".untrusted")))
        actual_family[family] += 1
        normalized.append((task_id, family, leaf, purpose, opts, has_attime, states[0], states[1]))
    for family, count in actual_family.items():
        meta = families[family]
        if not isinstance(meta, dict) or meta.get("tasks") != count:
            raise ReproductionError(f"family task count mismatch for {family}")
    if sum(actual_family.values()) != len(tasks):
        raise ReproductionError("aggregate task count inconsistency")
    parity = families.get("PARITY_PARTITION")
    if parity is not None:
        parity_tasks = [x for x in normalized if x[1] == "PARITY_PARTITION"]
        leaves = {x[2] for x in parity_tasks}
        if parity.get("leaves") != len(leaves):
            raise ReproductionError("PARITY_PARTITION leaf metadata mismatch")
        if parity_tasks:
            a_sizes = {len(x[6][0]) for x in parity_tasks}
            b_sizes = {len(x[7][0]) for x in parity_tasks}
            if a_sizes != {parity.get("origin_a_size")} or b_sizes != {parity.get("origin_b_size")}:
                raise ReproductionError("PARITY_PARTITION origin-size metadata mismatch")
    return sorted(normalized), actual_family


class EngineRunner:
    def __init__(self, engine, env, materials, tempdir):
        self.engine = engine
        self.env = env
        self.materials = materials
        self.tempdir = tempdir
        self.bundle_cache = {}
        self.verdict_cache = {}

    def bundle(self, role, names):
        if not names:
            return None
        key = (role, names)
        if key not in self.bundle_cache:
            digest = sha256_bytes(canonical([role, list(names)]))
            path = self.tempdir / (role + "-" + digest + ".pem")
            with path.open("wb") as handle:
                for name in names:
                    data = self.materials[name][0]
                    handle.write(data)
                    if not data.endswith(b"\n"):
                        handle.write(b"\n")
            self.bundle_cache[key] = path
        return self.bundle_cache[key]

    def verify(self, leaf, purpose, opts, has_attime, state):
        trusted, untrusted = state
        key = (leaf, purpose, opts, has_attime, trusted, untrusted)
        if key in self.verdict_cache:
            return self.verdict_cache[key]
        command = [str(self.engine), "verify", "-auth_level", "1"]
        if purpose:
            command += ["-purpose", purpose]
        command += list(opts)
        if not has_attime:
            command += ["-attime", str(DEFAULT_ATTIME)]
        command += ["-no-CAfile", "-no-CApath", "-no-CAstore"]
        trusted_path = self.bundle("trusted", trusted)
        untrusted_path = self.bundle("untrusted", untrusted)
        if trusted_path is not None:
            command += ["-trusted", str(trusted_path)]
        if untrusted_path is not None:
            command += ["-untrusted", str(untrusted_path)]
        leaf_path = self.tempdir / ("leaf-" + sha256_bytes(leaf.encode()) + ".pem")
        if not leaf_path.exists():
            leaf_path.write_bytes(self.materials[leaf][0])
        command.append(str(leaf_path))
        try:
            proc = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  env=self.env, timeout=TIMEOUT_SECONDS, check=False)
        except subprocess.TimeoutExpired as exc:
            raise ReproductionError("engine verification timed out") from exc
        except OSError as exc:
            raise ReproductionError(f"engine verification failed to start: {exc}") from exc
        verdict = proc.returncode == 0
        self.verdict_cache[key] = verdict
        return verdict


def method_decisions(v_a, v_b, v_u, v_i):
    return {"M1_flat_union": v_u, "M2_intersection": v_i,
            "M3_reject_all": False, "M4_ours_preference_B": v_b,
            "M5_typed_origin_witness": v_a or v_b}


def aggregate(records, family_names):
    buckets = {"overall": records}
    buckets.update({family: [r for r in records if r["family"] == family]
                    for family in sorted(family_names)})
    measures = {}
    for bucket, rows in buckets.items():
        methods = {}
        for method in method_decisions(False, False, False, False):
            allows = unsafe = needless = 0
            for row in rows:
                decision = method_decisions(row["vA"], row["vB"], row["vU"], row["vI"])[method]
                hybrid = row["vU"] and not row["vA"] and not row["vB"]
                parent = row["vA"] or row["vB"]
                allows += int(decision)
                unsafe += int(decision and hybrid)
                needless += int((not decision) and parent)
            methods[method] = {"allows": allows, "unsafe_merges": unsafe,
                               "needless_rejections": needless}
        measures[bucket] = methods
    return measures


def reproduce(root, engine_arg, engine_lib):
    binding, manifest, materials = load_and_validate_inputs(root)
    tasks, family_counts = normalize_tasks(manifest, materials)
    engine = Path(engine_arg).expanduser().resolve()
    if not engine.is_file():
        raise ReproductionError("--engine is not a file")
    env = os.environ.copy()
    if engine_lib is not None:
        lib = Path(engine_lib).expanduser().resolve()
        if not lib.is_dir():
            raise ReproductionError("--engine-lib is not a directory")
        env["LD_LIBRARY_PATH"] = str(lib)
        env["DYLD_LIBRARY_PATH"] = str(lib)
    version = one_line_version(engine, env)
    with tempfile.TemporaryDirectory(prefix="orion03-independent-") as tmp:
        runner = EngineRunner(engine, env, materials, Path(tmp))
        records = []
        for task_id, family, leaf, purpose, opts, has_attime, state_a, state_b in tasks:
            union = (tuple(sorted(set(state_a[0]) | set(state_b[0]))),
                     tuple(sorted(set(state_a[1]) | set(state_b[1]))))
            intersection = (tuple(sorted(set(state_a[0]) & set(state_b[0]))),
                            tuple(sorted(set(state_a[1]) & set(state_b[1]))))
            values = [runner.verify(leaf, purpose, opts, has_attime, state)
                      for state in (state_a, state_b, union, intersection)]
            records.append(dict(zip(("task_id", "family", "vA", "vB", "vU", "vI"),
                                    (task_id, family, *values))))
    hybrids = sorted(r["task_id"] for r in records
                     if r["vU"] and not r["vA"] and not r["vB"])
    parents = sum(r["vA"] or r["vB"] for r in records)
    unions = sum(r["vU"] for r in records)
    methods = aggregate(records, family_counts)
    if len(records) != sum(family_counts.values()) or len(hybrids) != methods["overall"]["M1_flat_union"]["unsafe_merges"]:
        raise ReproductionError("aggregate consistency assertion failed")
    digest_records = [{k: r[k] for k in ("task_id", "family", "vA", "vB", "vU", "vI")}
                      for r in sorted(records, key=lambda x: x["task_id"])]
    return {
        "schema": "orion03_independent_reproduction_r2_v1",
        "label": "independent_model_based_reimplementation",
        "scope": "Frozen task decisions and headline aggregates only; excludes C1-C6 and structural localization.",
        "scientific_authority_delta": "NONE",
        "external_peer_review_claimed": False,
        "journal_authority": False,
        "submission_authority": False,
        "bindings": {
            "protocol": {"identity": PROTOCOL_ID,
                         "sha256": binding["frozen_artifacts"]["PROTOCOL_V2.md"]},
            "input": {"task_manifest_sha256": binding["frozen_artifacts"]["TASK_MANIFEST_V2.json"],
                      "source_commit": binding["source"]["commit"],
                      "source_tag": binding["source"]["tag"]},
            "engine": {"version_line": version,
                       "source_commit": binding["source"]["commit"],
                       "source_tag": binding["source"]["tag"],
                       "tarball_sha256": binding["source"]["tarball_sha256"]},
            "reproducer_sha256": sha256_bytes(read_bytes(Path(__file__).resolve())),
        },
        "task_counts": {"total": len(records), "families": dict(sorted(family_counts.items()))},
        "methods": methods,
        "hybrid_tasks": {"count": len(hybrids), "task_ids": hybrids},
        "authorization_totals": {"parent_authorized": parents, "union_authorized": unions},
        "task_decisions_sha256": sha256_bytes(canonical(digest_records)),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, metavar="PATH")
    parser.add_argument("--engine-lib", metavar="DIR")
    parser.add_argument("--output", default="INDEPENDENT_REPRO_R2.json", metavar="PATH")
    parser.add_argument("--check-final", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    try:
        result = reproduce(root, args.engine, args.engine_lib)
        encoded = receipt_bytes(result)
        output = Path(args.output)
        if args.check_final:
            try:
                existing = output.read_bytes()
            except OSError as exc:
                raise ReproductionError(f"cannot read final output for comparison: {exc}") from exc
            if existing != encoded:
                raise ReproductionError("re-executed receipt differs byte-for-byte from --output")
        else:
            output.write_bytes(encoded)
    except ReproductionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
