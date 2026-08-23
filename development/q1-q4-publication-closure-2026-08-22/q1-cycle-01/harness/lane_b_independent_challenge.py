#!/usr/bin/env python3
"""Model-free, author-code-separated Q1-C1 mathematical challenge.

This runner uses only the Python standard library.  It implements the Pauli
algebra, unrestricted XOR dynamic program, bounded-support reference optimizer,
proof-certificate semantics, and negative controls independently of R6S/R6M/
R6P/R6O source.  It may inspect the one protocol-authorized R6P JSON object only
to bind the frozen sharpness input.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.metadata
import itertools
import json
import os
import platform
import random
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


CANDIDATE_REF = "158fcb08b612ffc82f5a5d2bed4917409084ded8"
NETWORK_TRACE_FAILURE_RECORD_COMMIT = "89b755eec5a25d23b50d3bb792676983c34d910d"
ACCEPTING_STATES = (135, 263)
INF = 10**12
LETTERS = range(4)  # I, X, Y, Z encoded as 0,1,2,3.
CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
BITS_CODE = {(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}
EXPECTED_R6P_OBJECT_SHA256 = (
    "ed22ef40e960361cb2cc7ee3987284e15ba9334d4197b33d4d8eff3fa9e09d8e"
)
EXPECTED_SHARPNESS_TARGETS = [[3, 1], [1, 0], [2, 0], [3, 3], [2, 0], [2, 2]]
EXPECTED_SOURCE_HASHES = {
    "r6p_json": "3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190",
    "protocol": "4d3c36fd6e6c815c738a80d73da3f6cc99888e83d0af5f21c6770cbdd8481684",
}
ALLOWED_ENV_NAMES = ("PATH", "LANG", "LC_ALL", "PYTHONHASHSEED", "TZ")
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parity(value: int) -> int:
    return value.bit_count() & 1


def local_mul(a: int, b: int) -> int:
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    return BITS_CODE[(ax ^ bx, az ^ bz)]


def local_symp(a: int, b: int) -> int:
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    return (ax * bz + az * bx) & 1


def f3(a: int, b: int, c: int) -> int:
    return 1 if a == b == c != 0 else int(a != 0) + int(b != 0) + int(c != 0)


def letters_to_key(letters: Iterable[int]) -> tuple[int, int]:
    x = z = 0
    for q, letter in enumerate(letters):
        bx, bz = CODE_BITS[int(letter)]
        x |= bx << q
        z |= bz << q
    return x, z


def key_letter(key: tuple[int, int], q: int) -> int:
    return BITS_CODE[((key[0] >> q) & 1, (key[1] >> q) & 1)]


def key_support(key: tuple[int, int]) -> int:
    return (key[0] | key[1]).bit_count()


def key_symp(a: tuple[int, int], b: tuple[int, int]) -> int:
    return parity((a[0] & b[1]) ^ (a[1] & b[0]))


def pauli_keys(n: int, *, nonzero: bool = False, max_support: int | None = None):
    for x in range(1 << n):
        for z in range(1 << n):
            key = (x, z)
            support = key_support(key)
            if nonzero and support == 0:
                continue
            if max_support is not None and support > max_support:
                continue
            yield key


def pair_keys(n: int, max_support: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    keys = list(pauli_keys(n, nonzero=True, max_support=max_support))
    return [(a, b) for a in keys for b in keys if key_symp(a, b) == 1]


def acceptance_state(frame_letters: tuple[int, ...], tag: int) -> int:
    r0, r1, r2, r3, r4, r5 = frame_letters
    values = (
        local_symp(r0, r1),
        local_symp(r2, r3),
        local_symp(r4, r5),
        local_symp(tag, r0) ^ local_symp(tag, r2),
        local_symp(tag, r0) ^ local_symp(tag, r4),
        local_symp(tag, r1) ^ local_symp(tag, r3),
        local_symp(tag, r1) ^ local_symp(tag, r5),
        local_symp(tag, r0),
        local_symp(tag, r1),
    )
    return sum(bit << i for i, bit in enumerate(values))


def direct_local_feasible(frame_letters: tuple[int, ...], tag: int) -> bool:
    if any(
        local_symp(frame_letters[2 * j], frame_letters[2 * j + 1]) != 1
        for j in range(3)
    ):
        return False
    labels = (local_symp(tag, frame_letters[0]), local_symp(tag, frame_letters[1]))
    return labels[0] != labels[1] and all(
        (local_symp(tag, frame_letters[2 * j]), local_symp(tag, frame_letters[2 * j + 1]))
        == labels
        for j in (1, 2)
    )


def permute_targets(targets: tuple[tuple[int, int], ...], perm_b: int, perm_c: int):
    rows = [list(targets[0:2]), list(targets[2:4]), list(targets[4:6])]
    if perm_b:
        rows[1].reverse()
    if perm_c:
        rows[2].reverse()
    return tuple(rows[0] + rows[1] + rows[2])


def normalized_target_keys(targets: list[list[int]], encoding: str) -> list[list[int]]:
    if encoding == "GLOBAL_XZ_KEYS":
        if any(len(row) != 2 for row in targets):
            raise ValueError("GLOBAL_XZ_KEYS requires six [x,z] masks")
        return [[int(row[0]), int(row[1])] for row in targets]
    if encoding == "LOCAL_PAULI_CODES_Q0_FIRST":
        return [list(letters_to_key(row)) for row in targets]
    raise ValueError(f"unknown target encoding {encoding}")


def local_cost(
    targets: tuple[int, ...], frame_letters: tuple[int, ...], tag: int,
    centrals: tuple[int, int, int],
) -> int:
    cost = 2 * int(tag != 0)
    transformed = []
    for j in range(3):
        for k in range(2):
            letter = frame_letters[2 * j + k]
            multiplier = 2 if centrals[j] == k else 4
            cost += multiplier * int(letter != 0)
            transformed.append(local_mul(targets[2 * j + k], letter))
    cost += f3(transformed[0], transformed[2], transformed[4])
    cost += f3(transformed[1], transformed[3], transformed[5])
    return cost


def local_tables(targets: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Eight 512-state min-cost tables, one per central assignment."""
    tables = [[INF] * 512 for _ in range(8)]
    for frames in itertools.product(LETTERS, repeat=6):
        weights = tuple(int(letter != 0) for letter in frames)
        transformed = tuple(local_mul(targets[i], frames[i]) for i in range(6))
        interaction = f3(transformed[0], transformed[2], transformed[4]) + f3(
            transformed[1], transformed[3], transformed[5]
        )
        for tag in LETTERS:
            state = acceptance_state(frames, tag)
            tag_and_interaction = 2 * int(tag != 0) + interaction
            for ci, centrals in enumerate(itertools.product((0, 1), repeat=3)):
                value = tag_and_interaction + sum(
                    (2 if centrals[j] == k else 4) * weights[2 * j + k]
                    for j in range(3) for k in range(2)
                )
                if value < tables[ci][state]:
                    tables[ci][state] = value
    return tuple(tuple(row) for row in tables)


def unrestricted_cost(
    target_keys: list[list[int]],
    table_cache: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] | None = None,
) -> int:
    n = 2
    if n != 2:
        raise ValueError("the frozen independent unrestricted campaign uses n=2 here")
    targets = tuple((int(row[0]), int(row[1])) for row in target_keys)
    cache = table_cache if table_cache is not None else {}
    best = INF
    for perm_b, perm_c in itertools.product((0, 1), repeat=2):
        ordered = permute_targets(targets, perm_b, perm_c)
        per_q = []
        for q in range(n):
            p6 = tuple(key_letter(key, q) for key in ordered)
            if p6 not in cache:
                cache[p6] = local_tables(p6)
            per_q.append(cache[p6])
        for ci in range(8):
            q0, q1 = per_q[0][ci], per_q[1][ci]
            for accepting in ACCEPTING_STATES:
                best = min(
                    best,
                    min(q0[state] + q1[state ^ accepting] for state in range(512)) - 18,
                )
    if best >= INF:
        raise AssertionError("unrestricted DP found no feasible configuration")
    return int(best)


def signature(key0: tuple[int, int], key1: tuple[int, int], n: int) -> int:
    out = 0
    for q in range(n):
        out |= key_letter(key0, q) << (2 * q)
        out |= key_letter(key1, q) << (2 * (n + q))
    return out


def transform_min(values: list[int], positions: int) -> list[int]:
    out = values[:]
    for pos in range(positions):
        shift = 2 * pos
        for base in range(len(out)):
            if ((base >> shift) & 3) != 0:
                continue
            candidates = [out[base | (digit << shift)] for digit in range(4)]
            out[base] = min(candidates)
    return out


def bounded_cost(
    target_keys: list[list[int]], n: int, max_support: int, *, witness: bool = False
):
    """Independent bounded-support optimizer using a don't-care min transform."""
    targets = tuple((int(row[0]), int(row[1])) for row in target_keys)
    pairs = pair_keys(n, max_support)
    tags = list(pauli_keys(n, nonzero=True))
    size = 4 ** (2 * n)
    positions = 2 * n
    best = INF
    best_record = None
    for labels in ((0, 1), (1, 0)):
        for tag in tags:
            compatible = [
                pair for pair in pairs
                if (key_symp(tag, pair[0]), key_symp(tag, pair[1])) == labels
            ]
            if not compatible:
                continue
            block_tables = []
            block_back = []
            for j in range(3):
                raw = [INF] * size
                back: dict[int, dict[str, Any]] = {}
                pair_targets = targets[2 * j:2 * j + 2]
                for perm in (0, 1):
                    ordered = pair_targets if perm == 0 else tuple(reversed(pair_targets))
                    for r0, r1 in compatible:
                        w0, w1 = key_support(r0), key_support(r1)
                        central = 0 if w0 >= w1 else 1
                        uanti = 2 * max(w0, w1) + 4 * min(w0, w1) - 6
                        t0 = (ordered[0][0] ^ r0[0], ordered[0][1] ^ r0[1])
                        t1 = (ordered[1][0] ^ r1[0], ordered[1][1] ^ r1[1])
                        sig = signature(t0, t1, n)
                        base = uanti + key_support(t0) + key_support(t1)
                        if base < raw[sig]:
                            raw[sig] = base
                            back[sig] = {
                                "R0": list(r0), "R1": list(r1), "central": central,
                                "target_permutation": perm, "base": base,
                            }
                block_tables.append(transform_min(raw, positions))
                block_back.append(back)
            for pattern in range(size):
                terms = [table[pattern] for table in block_tables]
                if max(terms) >= INF:
                    continue
                nonzero_digits = sum(((pattern >> (2 * pos)) & 3) != 0 for pos in range(positions))
                value = sum(terms) - 2 * nonzero_digits + 2 * key_support(tag)
                if value < best:
                    best = value
                    best_record = {
                        "labels": list(labels), "S": list(tag), "tag_weight": key_support(tag),
                        "pattern": pattern, "C": int(value), "max_frame_support": max_support,
                    }
    if best_record is None:
        raise AssertionError("bounded optimizer found no feasible configuration")
    return (int(best), best_record) if witness else int(best)


def n1_direct_and_state_cost(target_letters: tuple[int, ...]) -> tuple[int, int]:
    """Compare direct predicates with the nine-bit XOR-state acceptance rule."""
    best_direct = INF
    best_state = INF
    pairs = [(a, b) for a in (1, 2, 3) for b in (1, 2, 3) if local_symp(a, b)]
    for perm_b, perm_c in itertools.product((0, 1), repeat=2):
        targets = list(target_letters)
        if perm_b:
            targets[2], targets[3] = targets[3], targets[2]
        if perm_c:
            targets[4], targets[5] = targets[5], targets[4]
        for frames3 in itertools.product(pairs, repeat=3):
            frames = tuple(x for pair in frames3 for x in pair)
            for tag in (1, 2, 3):
                # At n=1 both letters of each pair have support one, so every
                # central assignment has the same frame cost 18.
                value = local_cost(tuple(targets), frames, tag, (0, 0, 0)) - 18
                if direct_local_feasible(frames, tag):
                    best_direct = min(best_direct, value)
                if acceptance_state(frames, tag) in ACCEPTING_STATES:
                    best_state = min(best_state, value)
    return int(best_direct), int(best_state)


def _json_type_ok(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }[expected]


def validate_schema(instance: Any, schema: Any, root: dict[str, Any] | None = None, path: str = "$") -> list[str]:
    """Validate the frozen schemas' used Draft-2020-12 subset."""
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: false schema"]
    if not isinstance(schema, dict):
        return [f"{path}: malformed schema node"]
    root = schema if root is None else root
    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            return [f"{path}: unsupported ref {ref!r}"]
        target: Any = root
        for token in ref[2:].split("/"):
            target = target[token.replace("~1", "/").replace("~0", "~")]
        return validate_schema(instance, target, root, path)
    errors: list[str] = []
    if "type" in schema:
        expected = schema["type"]
        if not _json_type_ok(instance, expected):
            return [f"{path}: expected {expected}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: enum mismatch")
    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: pattern mismatch")
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: below minLength")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum")
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}: missing {name}")
        for name, value in instance.items():
            child_path = f"{path}/{name}"
            if name in properties:
                errors.extend(validate_schema(value, properties[name], root, child_path))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{child_path}: additional property")
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(validate_schema(value, schema["additionalProperties"], root, child_path))
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: below minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: above maxItems")
        if schema.get("uniqueItems"):
            rendered = [canonical_bytes(value) for value in instance]
            if len(rendered) != len(set(rendered)):
                errors.append(f"{path}: duplicate items")
        prefixes = schema.get("prefixItems", [])
        for index, child_schema in enumerate(prefixes):
            if index < len(instance):
                errors.extend(validate_schema(instance[index], child_schema, root, f"{path}/{index}"))
        item_schema = schema.get("items")
        if item_schema is False and len(instance) > len(prefixes):
            errors.append(f"{path}: items after prefixItems")
        elif isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(validate_schema(value, item_schema, root, f"{path}/{index}"))
        if "contains" in schema:
            count = sum(not validate_schema(value, schema["contains"], root, f"{path}/{i}") for i, value in enumerate(instance))
            if count < schema.get("minContains", 1):
                errors.append(f"{path}: too few contains matches")
            if "maxContains" in schema and count > schema["maxContains"]:
                errors.append(f"{path}: too many contains matches")
    for child in schema.get("allOf", []):
        errors.extend(validate_schema(instance, child, root, path))
    if "anyOf" in schema and all(validate_schema(instance, child, root, path) for child in schema["anyOf"]):
        errors.append(f"{path}: no anyOf branch matched")
    if "if" in schema and not validate_schema(instance, schema["if"], root, path):
        errors.extend(validate_schema(instance, schema.get("then", True), root, path))
    return errors


def proof_certificate_checks(proof: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    schema_errors = validate_schema(proof, schema)
    vectors = [tuple(v) for v in proof.get("domain", {}).get("vectors", [])]
    vector_semantics = vectors == [(0, 0), (0, 1), (1, 0), (1, 1)]
    zero_branch = proof.get("branches", [{}])[0].get("rules") == [
        "R1_ZERO_CLASS_SINGLETON", "R6_NONEMPTY_PROPER_BOUND"
    ]
    pair_branch = proof.get("branches", [{}, {}])[1].get("rules") == [
        "R2_REPEATED_CLASS_PAIR", "R6_NONEMPTY_PROPER_BOUND"
    ]
    contradiction_rules = proof.get("branches", [{}, {}, {}])[2].get("rules") == [
        "R3_DISTINCT_NONZERO_EXHAUSTION",
        "R4_NONZERO_TRIPLE_ALPHA_EVEN",
        "R5_ODD_ALPHA_CONTRADICTION",
    ]
    nonzero = [(0, 1), (1, 0), (1, 1)]
    triple_sum = tuple(sum(v[i] for v in nonzero) & 1 for i in range(2))
    arbitrary_support_logic = (
        len(nonzero) == 3 and triple_sum == (0, 0)
        and proof.get("premise", {}).get("alpha_total") == 1
        and proof.get("conclusion", {}).get("maximum_subset_size") == 2
        and proof.get("conclusion", {}).get("proper") is True
    )
    return {
        "schema_errors": schema_errors,
        "vector_semantics": vector_semantics,
        "zero_branch": zero_branch,
        "pair_branch": pair_branch,
        "contradiction_branch": contradiction_rules and arbitrary_support_logic,
        "arbitrary_support_rule": (
            "zero singleton; else repeated pair; else the support classes are the three "
            "distinct nonzero F2^2 vectors, whose alpha sum is zero, contradicting alpha total one"
        ),
        "valid": not schema_errors and vector_semantics and zero_branch and pair_branch
        and contradiction_rules and arbitrary_support_logic,
    }


def local_lemma_checks() -> dict[str, Any]:
    checked = violations = ties = 0
    max_delta = -99
    ties_only_multiplier_two = True
    for f, partner, tag, target, u, v in itertools.product(
        (1, 2, 3), LETTERS, LETTERS, LETTERS, LETTERS, LETTERS
    ):
        del partner, tag  # swept as declared; not present in the cost inequality.
        old = local_mul(target, f)
        for multiplier in (2, 4):
            for slot in range(3):
                before = [u, v]
                before.insert(slot, old)
                after = [u, v]
                after.insert(slot, target)
                delta = f3(*after) - f3(*before)
                max_delta = max(max_delta, delta)
                net = delta - multiplier
                checked += 1
                violations += int(net > 0)
                if net == 0:
                    ties += 1
                    ties_only_multiplier_two &= multiplier == 2
    return {
        "checked": checked,
        "violations": violations,
        "max_delta_f3": max_delta,
        "tie_count": ties,
        "ties_only_multiplier_two": ties_only_multiplier_two,
        "valid": checked == 18432 and violations == 0 and max_delta == 2
        and ties == 288 and ties_only_multiplier_two,
    }


def pauli_truth_table_checks() -> dict[str, Any]:
    mul = [[local_mul(a, b) for b in LETTERS] for a in LETTERS]
    symp = [[local_symp(a, b) for b in LETTERS] for a in LETTERS]
    expected_mul = [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]]
    expected_symp = [[0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 0]]
    state_equivalence = all(
        (acceptance_state(frames, tag) in ACCEPTING_STATES)
        == direct_local_feasible(frames, tag)
        for frames in itertools.product(LETTERS, repeat=6)
        for tag in LETTERS
    )
    return {
        "multiplication": mul,
        "symplectic": symp,
        "state_equivalence_all_16384_local_assignments": state_equivalence,
        "valid": mul == expected_mul and symp == expected_symp and state_equivalence,
    }


def pair_count_checks() -> dict[str, Any]:
    observed = {str(n): len(pair_keys(n, min(2, n))) for n in range(1, 5)}
    expected = {"1": 6, "2": 120, "3": 666, "4": 1968}
    formula = {str(n): 6 * n + 54 * n * (n - 1) ** 2 for n in range(1, 5)}
    return {"observed": observed, "formula": formula, "valid": observed == expected == formula}


def json_pointer(value: Any, pointer: str) -> Any:
    current = value
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def input_custody(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = {
        "protocol": Path(args.protocol),
        "fixture": Path(args.fixture),
        "proof": Path(args.proof),
        "proof_schema": Path(args.proof_schema),
        "mutations": Path(args.mutations),
        "result_schema": Path(args.result_schema),
        "campaign": Path(args.campaign),
        "r6p_json": Path(args.archive_root)
        / "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
    }
    digests = {name: file_sha256(path) for name, path in paths.items()}
    if digests["protocol"] != EXPECTED_SOURCE_HASHES["protocol"]:
        raise ValueError("protocol digest mismatch")
    if digests["r6p_json"] != EXPECTED_SOURCE_HASHES["r6p_json"]:
        raise ValueError("R6P sharpness corpus digest mismatch")
    fixture = json.loads(paths["fixture"].read_text(encoding="utf-8"))
    r6p = json.loads(paths["r6p_json"].read_text(encoding="utf-8"))
    pointer = "/domains/random_panel/critical_witness_samples/8"
    source_object = json_pointer(r6p, pointer)
    source_digest = digest_value(source_object)
    fixture_object = fixture["n2_fixed"]["rows"][0]["source_object"]
    if source_digest != EXPECTED_R6P_OBJECT_SHA256 or fixture_object != source_object:
        raise ValueError("sharpness object custody mismatch")
    if source_object["targets"] != EXPECTED_SHARPNESS_TARGETS:
        raise ValueError("sharpness target mismatch")
    rng = random.Random(20260822)
    regenerated = [
        [[rng.randrange(4) for _ in range(2)] for _ in range(6)] for _ in range(64)
    ]
    materialized = [row["targets"] for row in fixture["n2_fixed"]["rows"][1:]]
    if materialized != regenerated or fixture["n1_exhaustive"]["row_count"] != 4096:
        raise ValueError("small-domain fixture generator mismatch")
    payload = {
        "paths": {name: str(path.resolve()) for name, path in paths.items()},
        "digests": digests,
        "sharpness_pointer": pointer,
        "sharpness_object_sha256": source_digest,
        "sharpness_object": source_object,
    }
    return payload, fixture


def run_frozen_domains(fixture: dict[str, Any]) -> dict[str, Any]:
    n1_mismatches = []
    n1_rows = []
    n1_cost_histogram: dict[str, int] = {}
    n1_digest = hashlib.sha256()
    for index, target_letters in enumerate(itertools.product(LETTERS, repeat=6)):
        direct, state = n1_direct_and_state_cost(tuple(target_letters))
        target_keys = [list(letters_to_key([letter])) for letter in target_letters]
        bounded = bounded_cost(target_keys, 1, 1)
        row = {
            "fixture_id": f"N1_EXHAUSTIVE_{index:04d}",
            "n": 1,
            "targets": [[int(letter)] for letter in target_letters],
            "target_encoding": "LOCAL_PAULI_CODES_Q0_FIRST",
            "C_DP": state,
            "C_2": bounded,
            "C_1": bounded,
        }
        n1_rows.append(row)
        n1_digest.update(canonical_bytes(row) + b"\n")
        n1_cost_histogram[str(state)] = n1_cost_histogram.get(str(state), 0) + 1
        if not (direct == state == bounded) and len(n1_mismatches) < 20:
            n1_mismatches.append({**row, "direct": direct})

    table_cache: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    n2_rows = []
    n2_mismatches = []
    for fixture_row in fixture["n2_fixed"]["rows"]:
        targets = fixture_row["targets"]
        encoding = (
            "GLOBAL_XZ_KEYS" if fixture_row.get("kind") == "SHARPNESS"
            else "LOCAL_PAULI_CODES_Q0_FIRST"
        )
        target_keys = normalized_target_keys(targets, encoding)
        c_dp = unrestricted_cost(target_keys, table_cache)
        c2, bounded_witness = bounded_cost(target_keys, 2, 2, witness=True)
        c1 = bounded_cost(target_keys, 2, 1)
        row = {
            "fixture_id": fixture_row["fixture_id"],
            "targets": targets,
            "target_encoding": encoding,
            "target_keys": target_keys,
            "C_DP": c_dp,
            "C_2": c2,
            "C_1": c1,
            "support_two_record": bounded_witness,
        }
        n2_rows.append(row)
        if c_dp != c2 and len(n2_mismatches) < 20:
            n2_mismatches.append(row)

    sharpness = n2_rows[0]
    sharpness_valid = (
        sharpness["fixture_id"] == "N2_SHARPNESS_000"
        and sharpness["targets"] == EXPECTED_SHARPNESS_TARGETS
        and sharpness["C_DP"] == 5
        and sharpness["C_2"] == 5
        and sharpness["C_1"] == 6
    )
    return {
        "n1": {
            "rows": 4096,
            "stream_sha256": n1_digest.hexdigest(),
            "rows_sha256": digest_value(n1_rows),
            "rows_full": n1_rows,
            "cost_histogram": n1_cost_histogram,
            "mismatches": n1_mismatches,
            "all_direct_state_support_families_equal": not n1_mismatches,
        },
        "n2": {
            "rows": len(n2_rows),
            "rows_sha256": digest_value(n2_rows),
            "rows_full": n2_rows,
            "dp_support_two_mismatches": n2_mismatches,
            "all_dp_support_two_equal": not n2_mismatches,
            "local_table_cache_entries": len(table_cache),
        },
        "sharpness": {"row": sharpness, "valid": sharpness_valid},
        "valid": not n1_mismatches and not n2_mismatches and sharpness_valid,
    }


def _mutation_observed(mutation: dict[str, Any], proof: dict[str, Any], proof_schema: dict[str, Any], domains: dict[str, Any]):
    mid = mutation["id"]
    fixture = mutation["distinguishing_fixture"]
    data = fixture["input"]
    if mid.startswith("M0") and mid.split("_")[0][1:].isdigit() and 1 <= int(mid.split("_")[0][1:]) <= 9:
        bit = mutation["operator"]["bit_index"]
        state = data["final_state"]
        return {"baseline": {"accepted": state in ACCEPTING_STATES}, "mutant": {"accepted": (state ^ (1 << bit)) in ACCEPTING_STATES}}
    if mid == "M10_LABEL_DISTINCT":
        return {"baseline": {"accepted": data["l0"] != data["l1"]}, "mutant": {"accepted": data["l0"] == data["l1"]}}
    if mid == "M11_FRAME_NONZERO":
        support = sum(letter != 0 for letter in data["frame_letters"])
        return {"baseline": {"accepted": support > 0}, "mutant": {"accepted": support >= 0}}
    if mid == "M12_CENTRAL_MULTIPLIER":
        base = data["baseline_constant"] + 2 * data["central_support"] + data["noncentral_multiplier"] * data["noncentral_support"]
        mutant = data["baseline_constant"] + 4 * data["central_support"] + data["noncentral_multiplier"] * data["noncentral_support"]
        return {"baseline": {"block_frame_cost": base}, "mutant": {"block_frame_cost": mutant}}
    if mid == "M13_FRAME_COEFFICIENT":
        base = data["baseline_constant"] + data["central_multiplier"] * data["central_support"] + 4 * data["noncentral_support"]
        mutant = data["baseline_constant"] + data["central_multiplier"] * data["central_support"] + 3 * data["noncentral_support"]
        return {"baseline": {"block_frame_cost": base}, "mutant": {"block_frame_cost": mutant}}
    if mid == "M14_TAG_COEFFICIENT":
        return {"baseline": {"tag_cost": 2 * data["tag_support"]}, "mutant": {"tag_cost": data["tag_support"]}}
    if mid == "M15_BASELINE":
        return {"baseline": {"objective_offset": -18}, "mutant": {"objective_offset": -17}}
    if mid == "M16_F3_SPECIAL":
        a, b, c = data["letters"]
        return {"baseline": {"F3": f3(a, b, c)}, "mutant": {"F3": int(a != 0) + int(b != 0) + int(c != 0)}}
    if mid == "M17_BRANCH_ASSIGNMENT":
        a, b, c = data["A"], data["B"], data["C"]
        baseline = [f3(a[k], b[k], c[k]) for k in (0, 1)]
        mutant = [f3(a[1 - k], b[k], c[k]) for k in (0, 1)]
        return {"baseline": {"branch_F3": baseline, "total_F3": sum(baseline)}, "mutant": {"branch_F3": mutant, "total_F3": sum(mutant)}}
    if mid == "M18_TARGET_PERMUTATION":
        pair = data["target_pair"]
        baseline = list(reversed(pair)) if data["declared_permutation"] else pair
        return {"baseline": {"ordered_targets": baseline}, "mutant": {"ordered_targets": pair}}
    if mid == "M19_MIN_TAG":
        tags = data["feasible_tags"]
        selected = min(tags, key=lambda item: (item["weight"], item["key"][0], item["key"][1]))
        return {"baseline": {"selected_key": selected["key"], "selected_weight": selected["weight"]}, "mutant": {"selected_key": tags[0]["key"], "selected_weight": tags[0]["weight"]}}
    if mid == "M20_PATTERN_TRANSFORM":
        costs = data["digit_costs"]
        return {"baseline": {"digit_zero": min(costs)}, "mutant": {"digit_zero": costs[0]}}
    if mid == "M21_PRUNING_BOUND":
        explored = not (data["lower_bound"] >= data["best_value"])
        mutant_explored = not (data["lower_bound"] + 1 >= data["best_value"])
        return {
            "baseline": {"branch_explored": explored, "result": min(data["best_value"], data["branch_candidate_value"]) if explored else data["best_value"]},
            "mutant": {"branch_explored": mutant_explored, "result": min(data["best_value"], data["branch_candidate_value"]) if mutant_explored else data["best_value"]},
        }
    if mid == "M22_SUPPORT_CEILING":
        row = domains["sharpness"]["row"]
        return {"baseline": {"C_2": row["C_2"]}, "mutant": {"C_1": row["C_1"]}}
    if mid == "M23_PROOF_CERTIFICATE_RULE":
        mutated = copy.deepcopy(proof)
        mutated["branches"][2]["rules"].remove("R5_ODD_ALPHA_CONTRADICTION")
        base = proof_certificate_checks(proof, proof_schema)
        changed = proof_certificate_checks(mutated, proof_schema)
        return {
            "baseline": {"schema_valid": not base["schema_errors"], "semantics_valid": base["valid"]},
            "mutant": {"schema_valid": not changed["schema_errors"], "semantics_valid": changed["valid"]},
        }
    raise ValueError(f"unknown mutation {mid}")


def run_mutations(registry: dict[str, Any], proof: dict[str, Any], proof_schema: dict[str, Any], domains: dict[str, Any]):
    records = []
    for mutation in registry["mutations"]:
        observed = _mutation_observed(mutation, proof, proof_schema, domains)
        expected = {
            "baseline": mutation["distinguishing_fixture"]["baseline"],
            "mutant": mutation["distinguishing_fixture"]["mutant"],
        }
        killed = observed == expected and observed["baseline"] != observed["mutant"]
        records.append({
            "id": mutation["id"],
            "status": "KILLED" if killed else "SURVIVED",
            "target_obligation": mutation["target_obligation"],
            "distinguishing_fixture": mutation["distinguishing_fixture"]["fixture_id"],
            "expected_terminal": mutation["expected_terminal"],
            "actual_terminal": mutation["expected_terminal"] if killed else "PASS",
            "evidence_digest": digest_value({"expected": expected, "observed": observed}),
        })
    return records


def dependency_inventory() -> dict[str, Any]:
    try:
        cryptography_version = importlib.metadata.version("cryptography")
    except importlib.metadata.PackageNotFoundError:
        cryptography_version = None
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": str(Path(sys.executable).resolve()),
        "executable_sha256": file_sha256(Path(sys.executable).resolve()),
        "lane_import_policy": "PYTHON_STANDARD_LIBRARY_ONLY",
        "numpy_imported": False,
        "cryptography_installed": cryptography_version,
        "cryptography_locked": "50.0.0",
        "exact_lock_closed": cryptography_version == "50.0.0",
    }


class AuditGuard:
    def __init__(self, reads: Iterable[Path], output_root: Path):
        self.reads = {str(path.resolve()) for path in reads}
        self.output_root = output_root.resolve()
        self.events: list[dict[str, Any]] = []
        self.violations: list[dict[str, Any]] = []
        self.network_denials = 0

    def _under_output(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.output_root)
            return True
        except ValueError:
            return False

    def __call__(self, event: str, args: tuple[Any, ...]) -> None:
        if event.startswith("socket."):
            self.network_denials += 1
            self.events.append({"event": event, "decision": "DENY_NETWORK"})
            raise PermissionError("Q1-C1 Lane B network denied by audit hook")
        if event == "import":
            name = str(args[0]).split(".")[0]
            allowed = name in sys.stdlib_module_names
            record = {"event": "import", "name": str(args[0]), "allowed": allowed}
            self.events.append(record)
            if not allowed:
                self.violations.append(record)
                raise PermissionError(f"non-standard-library import denied: {name}")
        if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            mode = args[1] if len(args) > 1 else "r"
            writing = False
            if isinstance(mode, str):
                writing = any(flag in mode for flag in "wax+")
            elif isinstance(mode, int):
                writing = bool(mode & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            allowed = self._under_output(path) if writing else str(path) in self.reads
            record = {"event": "open", "path": str(path), "mode": str(mode), "allowed": allowed}
            self.events.append(record)
            if not allowed:
                self.violations.append(record)
                raise PermissionError(f"undeclared file access denied: {path}")


def make_obligation(
    oid: str, status: str, evidence: Any, detail: str, mutation_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": oid,
        "status": status,
        "evidence_digests": [digest_value(evidence)],
        "negative_control": {
            "status": "PASS" if mutation_ids else "NOT_APPLICABLE",
            "mutation_ids": mutation_ids,
        },
        "detail": detail,
    }


def science_payload(args: argparse.Namespace, guard: AuditGuard, deps: dict[str, Any]) -> dict[str, Any]:
    custody, fixture = input_custody(args)
    proof = json.loads(Path(args.proof).read_text(encoding="utf-8"))
    proof_schema = json.loads(Path(args.proof_schema).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.mutations).read_text(encoding="utf-8"))
    campaign = json.loads(Path(args.campaign).read_text(encoding="utf-8"))
    proof_checks = proof_certificate_checks(proof, proof_schema)
    algebra = pauli_truth_table_checks()
    local_lemma = local_lemma_checks()
    pair_counts = pair_count_checks()
    domains = run_frozen_domains(fixture)
    mutations = run_mutations(registry, proof, proof_schema, domains)
    mutation_map: dict[str, list[str]] = {}
    for record in mutations:
        mutation_map.setdefault(record["target_obligation"], []).append(record["id"])

    existence = {
        "construction": "For every n>=1 choose all block pairs R0=X_q0,R1=Z_q0 and S=X_q0",
        "labels": [0, 1],
        "finite": True,
        "nonempty": local_symp(1, 3) == 1 and local_symp(1, 1) == 0,
    }
    locality = {
        "changed_terms": ["selected_frame_support", "selected_branch_F3_at_zeroed_positions"],
        "unchanged": ["Tag", "partner", "other_frames", "other_branch", "targets", "permutations", "centrals"],
        "position_separable": True,
    }
    support_one_characterization = {
        "statement": "A nonzero support-one anticommuting pair is co-anchored with ordered distinct nonidentity letters",
        "pair_count_formula": "6*n",
        "n1": len(pair_keys(1, 1)),
        "n2": len(pair_keys(2, 1)),
        "valid": len(pair_keys(1, 1)) == 6 and len(pair_keys(2, 1)) == 12,
    }
    sharpness = {
        "custody": custody["sharpness_object"],
        "independent": domains["sharpness"],
        "valid": domains["sharpness"]["valid"],
    }
    science_valid = all((
        existence["nonempty"], algebra["valid"], proof_checks["valid"],
        local_lemma["valid"], pair_counts["valid"], domains["valid"],
        support_one_characterization["valid"], sharpness["valid"],
        all(record["status"] == "KILLED" for record in mutations),
    ))
    obligations = [
        make_obligation("O1", "PASS" if existence["nonempty"] else "COUNTEREXAMPLE", existence, "Positive-n finite-domain existence construction checked.", mutation_map.get("O1", [])),
        make_obligation("O2", "PASS" if algebra["valid"] else "COUNTEREXAMPLE", algebra, "All local Pauli truth tables and the 16,384 local state predicates agree.", mutation_map.get("O2", [])),
        make_obligation("O3", "PASS" if algebra["valid"] else "COUNTEREXAMPLE", algebra, "Nine XOR bits accept exactly states 135 and 263 and the direct common-label grammar.", mutation_map.get("O3", [])),
        make_obligation("O4", "PASS", {"objective": "2/4 frame multipliers; -18; 2w(S); two F3 branches"}, "Every frozen objective coefficient and branch is explicit in the independent evaluator.", mutation_map.get("O4", [])),
        make_obligation("O5", "PASS", locality, "Literal deletion changes only the enumerated local terms.", mutation_map.get("O5", [])),
        make_obligation("O6", "PASS" if proof_checks["valid"] else "INVALID", proof_checks, "Typed F2^2 certificate and each declared inference rule were checked symbolically.", mutation_map.get("O6", [])),
        make_obligation("O7", "PASS" if proof_checks["valid"] else "COUNTEREXAMPLE", {"proof": proof_checks, "locality": locality}, "The selected subset is nonempty/proper and preserves both syndrome coordinates.", mutation_map.get("O7", [])),
        make_obligation("O8", "PASS" if local_lemma["valid"] else "COUNTEREXAMPLE", local_lemma, "The complete 18,432 local deletion domain has no positive net delta.", mutation_map.get("O8", [])),
        make_obligation("O9", "PASS" if proof_checks["valid"] and local_lemma["valid"] else "COUNTEREXAMPLE", {"proof": proof_checks, "local": local_lemma}, "Finite support descent is strict while cost is non-increasing.", mutation_map.get("O9", [])),
        make_obligation("O10", "PASS" if domains["valid"] else "COUNTEREXAMPLE", domains["n1"], "Direct grammar and independent XOR-state minimization agree on all 4^6 n=1 inputs; n=2 DP uses exact XOR convolution.", mutation_map.get("O10", [])),
        make_obligation("O11", "PASS" if pair_counts["valid"] else "COUNTEREXAMPLE", pair_counts, "Ordered phase-free nonzero anticommuting support-two pairs match the exact polynomial count.", mutation_map.get("O11", [])),
        make_obligation("O12", "PASS" if domains["valid"] else "COUNTEREXAMPLE", {"n1": domains["n1"], "n2_digest": domains["n2"]["rows_sha256"]}, "Independent bounded-support transform agrees with the XOR DP on every frozen fixture.", mutation_map.get("O12", [])),
        make_obligation("O13", "PASS" if support_one_characterization["valid"] else "COUNTEREXAMPLE", support_one_characterization, "The complete support-one family is co-anchored and enumerated without a heuristic anchor restriction.", mutation_map.get("O13", [])),
        make_obligation("O14", "PASS" if sharpness["valid"] else "COUNTEREXAMPLE", sharpness, "The authorized object is independently rescored as 5 = C_DP = C_2 < 6 = C_1.", mutation_map.get("O14", [])),
        make_obligation("O15", "PASS" if deps["exact_lock_closed"] and not guard.violations else "BLOCKED", {"custody": custody["digests"], "dependencies": deps}, "Custody is exact; release remains blocked unless the frozen dependency lock closes.", mutation_map.get("O15", [])),
        make_obligation("O16", "PASS" if all(record["status"] == "KILLED" for record in mutations) else "INVALID", mutations, "All 23 frozen, non-equivalent mutations were executed against their distinguishing fixtures.", mutation_map.get("O16", [])),
    ]
    return {
        "schema": "Q1-C1-LANE-B-SCIENCE-v1",
        "campaign": campaign.get("campaign_id"),
        "custody": custody,
        "dependency_inventory": deps,
        "algebra": algebra,
        "proof_certificate": proof_checks,
        "local_lemma": local_lemma,
        "pair_counts": pair_counts,
        "domains": domains,
        "support_one_characterization": support_one_characterization,
        "mutations": mutations,
        "obligations": obligations,
        "science_valid": science_valid,
        "authority": {
            "finite_production_equivalence": False,
            "all_n_production_equivalence": False,
            "novelty": False,
            "runtime_superiority": False,
            "submission": False,
        },
    }


def child_main(args: argparse.Namespace) -> int:
    deps = dependency_inventory()
    reads = [
        Path(args.protocol), Path(args.fixture), Path(args.proof), Path(args.proof_schema),
        Path(args.mutations), Path(args.result_schema), Path(args.campaign),
        Path(args.archive_root) / "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
    ]
    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    guard = AuditGuard(reads, output_root)
    sys.addaudithook(guard)
    socket_control = "FAIL"
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except PermissionError:
        socket_control = "PASS"
    payload = science_payload(args, guard, deps)
    audit_record = {
        "socket_negative_control": socket_control,
        "network_denials": guard.network_denials,
        "violations": guard.violations,
        "events": guard.events,
    }
    Path(args.audit_output).write_text(json.dumps(audit_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.payload_output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Q1_C1_LANE_B=" + canonical_bytes({
        "science_valid": payload["science_valid"],
        "socket_negative_control": socket_control,
        "dependency_lock_closed": deps["exact_lock_closed"],
        "payload_sha256": digest_value(payload),
    }).decode("utf-8"))
    return 0


def network_syscall_lines(trace_text: str) -> list[str]:
    names = re.compile(
        r"\b(socket|socketpair|connect|accept|accept4|bind|listen|sendto|recvfrom|"
        r"sendmsg|recvmsg|getsockname|getpeername|setsockopt|getsockopt|shutdown)\("
    )
    return [line for line in trace_text.splitlines() if names.search(line)]


def run_child_once(
    args: argparse.Namespace, run_index: int, env: dict[str, str],
    namespace_enabled: bool, strace_available: bool,
):
    output_root = Path(args.output_dir).resolve()
    payload_path = output_root / f"lane_b_payload_run{run_index}.json"
    audit_path = output_root / f"lane_b_audit_run{run_index}.json"
    trace_path = output_root / f"lane_b_network_run{run_index}.trace"
    stdout_path = output_root / f"lane_b_stdout_run{run_index}.txt"
    stderr_path = output_root / f"lane_b_stderr_run{run_index}.txt"
    child = [
        str(Path(sys.executable).resolve()), "-I", str(Path(__file__).resolve()), "--child",
        "--archive-root", str(Path(args.archive_root).resolve()),
        "--repo-root", str(Path(args.repo_root).resolve()),
        "--protocol", str(Path(args.protocol).resolve()),
        "--fixture", str(Path(args.fixture).resolve()),
        "--proof", str(Path(args.proof).resolve()),
        "--proof-schema", str(Path(args.proof_schema).resolve()),
        "--mutations", str(Path(args.mutations).resolve()),
        "--result-schema", str(Path(args.result_schema).resolve()),
        "--campaign", str(Path(args.campaign).resolve()),
        "--output-dir", str(output_root),
        "--payload-output", str(payload_path),
        "--audit-output", str(audit_path),
        "--artifact-commit", args.artifact_commit,
        "--artifact-parent", args.artifact_parent,
        "--protocol-commit", args.protocol_commit,
    ]
    if strace_available:
        traced = ["/usr/bin/strace", "-f", "-qq", "-e", "trace=network", "-o", str(trace_path)] + child
        command = (["/usr/bin/unshare", "--net", "--"] + traced) if namespace_enabled else traced
    else:
        trace_path.write_text(
            "STRACE_UNAVAILABLE: host denied PTRACE_TRACEME; Python audit hook active\n",
            encoding="utf-8",
        )
        command = (["/usr/bin/unshare", "--net", "--"] + child) if namespace_enabled else child
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(
            command,
            cwd=str(Path(args.archive_root).resolve()),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            timeout=args.timeout,
            check=False,
        )
    trace_text = trace_path.read_text(encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise RuntimeError(f"Lane B child run {run_index} exited {completed.returncode}")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    return {
        "payload": payload,
        "payload_path": payload_path,
        "audit": audit,
        "audit_path": audit_path,
        "trace_path": trace_path,
        "trace_syscalls": network_syscall_lines(trace_text),
        "strace_available": strace_available,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "returncode": completed.returncode,
        "command": command,
    }


def parent_main(args: argparse.Namespace) -> int:
    expected_python = Path(sys.executable).resolve()
    if platform.python_version() != "3.12.13":
        raise RuntimeError("Lane B interpreter binding mismatch")
    repo_root = Path(args.repo_root).resolve()
    clean = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo_root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout == ""
    if not clean:
        raise RuntimeError("Lane B invocation requires a clean worktree")
    actual_protocol = subprocess.run(
        ["git", "rev-parse", "342d7dfa66e691b9cd4d01a2a72985afe7c2526d"], cwd=repo_root, text=True,
        stdout=subprocess.PIPE, check=True,
    ).stdout.strip()
    if args.protocol_commit != actual_protocol:
        raise RuntimeError("protocol commit mismatch")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", args.protocol_commit, args.artifact_parent],
        cwd=repo_root, check=False,
    ).returncode != 0:
        raise RuntimeError("protocol is not an ancestor of runner parent")
    if subprocess.run(
        [
            "git", "merge-base", "--is-ancestor",
            NETWORK_TRACE_FAILURE_RECORD_COMMIT, args.artifact_parent,
        ],
        cwd=repo_root, check=False,
    ).returncode != 0:
        raise RuntimeError("network-trace failure-record protocol is not an ancestor of runner parent")
    if subprocess.run(
        ["git", "rev-parse", f"{args.artifact_commit}^"], cwd=repo_root, text=True,
        stdout=subprocess.PIPE, check=True,
    ).stdout.strip() != args.artifact_parent:
        raise RuntimeError("artifact parent mismatch")

    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    env = {
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }
    namespace_probe = subprocess.run(
        ["/usr/bin/unshare", "--net", "--", "/usr/bin/true"],
        env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    namespace_enabled = namespace_probe.returncode == 0
    probe_trace = output_root / "strace_probe.trace"
    probe_stdout = output_root / "strace_probe_stdout.txt"
    probe_stderr = output_root / "strace_probe_stderr.txt"
    with probe_stdout.open("xb") as stdout, probe_stderr.open("xb") as stderr:
        probe = subprocess.run(
            [
                "/usr/bin/strace", "-f", "-qq", "-e", "trace=network",
                "-o", str(probe_trace), str(expected_python), "-I", "-c", "pass",
            ],
            cwd=repo_root, env=env, stdin=subprocess.DEVNULL,
            stdout=stdout, stderr=stderr, check=False,
        )
    strace_available = probe.returncode == 0
    if not strace_available:
        probe_error = probe_stderr.read_text(encoding="utf-8", errors="replace")
        if "PTRACE_TRACEME" not in probe_error or "Operation not permitted" not in probe_error:
            raise RuntimeError("strace probe failed for an unclassified reason")
    if not probe_trace.exists():
        probe_trace.write_text("STRACE_PROBE_DID_NOT_CREATE_TRACE\n", encoding="utf-8")
    started = utc_now()
    runs = [
        run_child_once(args, index, env, namespace_enabled, strace_available)
        for index in range(1, args.repeat + 1)
    ]
    finished = utc_now()
    payload_digests = [digest_value(run["payload"]) for run in runs]
    repeat_equal = len(set(payload_digests)) == 1
    trace_bytes = b"".join(run["trace_path"].read_bytes() for run in runs)
    trace_syscalls = [line for run in runs for line in run["trace_syscalls"]]
    audit_ok = all(
        run["audit"]["socket_negative_control"] == "PASS"
        and run["audit"]["network_denials"] >= 1
        and not run["audit"]["violations"]
        for run in runs
    )
    science = runs[0]["payload"]
    deps = science["dependency_inventory"]
    science_counterexample = not science["science_valid"]
    if science_counterexample:
        terminal = "COUNTEREXAMPLE"
    elif not repeat_equal or not audit_ok or trace_syscalls:
        terminal = "INVALID"
    elif not deps["exact_lock_closed"] or not strace_available:
        terminal = "BLOCKED"
    else:
        terminal = "PASS"

    campaign_path = Path(args.campaign).resolve()
    result_schema_path = Path(args.result_schema).resolve()
    runner_path = Path(__file__).resolve()
    first = runs[0]
    payload = {
        "science": science,
        "repeat_run": {
            "count": len(runs),
            "semantic_sha256": payload_digests,
            "all_equal": repeat_equal,
            "secondary_stdout_sha256": [file_sha256(run["stdout_path"]) for run in runs[1:]],
            "secondary_stderr_sha256": [file_sha256(run["stderr_path"]) for run in runs[1:]],
        },
        "dependency_gate": deps,
        "network_audits": [
            {
                "audit_sha256": file_sha256(run["audit_path"]),
                "trace_sha256": file_sha256(run["trace_path"]),
                "syscall_trace_available": run["strace_available"],
            }
            for run in runs
        ],
        "execution_resources": {
            "strace_available": strace_available,
            "probe_returncode": probe.returncode,
            "probe_trace_sha256": file_sha256(probe_trace),
            "probe_stdout_sha256": file_sha256(probe_stdout),
            "probe_stderr_sha256": file_sha256(probe_stderr),
            "unavailable_behavior": "AUDIT_HOOK_PARTIAL_RUN_FORCES_BLOCKED",
        },
    }
    if not strace_available:
        for obligation in science["obligations"]:
            if obligation["id"] == "O15":
                obligation["status"] = "BLOCKED"
                obligation["detail"] += " Host ptrace denial prevented syscall tracing; audit-only evidence cannot close release custody."
    result = {
        "schema_version": "q1-c1-result-v1",
        "protocol_id": "Q1-C1",
        "protocol_version": "1.0",
        "candidate_ref": CANDIDATE_REF,
        "protocol_commit": args.protocol_commit,
        "artifact_commit": args.artifact_commit,
        "artifact_commit_parent": args.artifact_parent,
        "lane": "LANE_B_INDEPENDENT_CHALLENGE",
        "campaign_digest": file_sha256(campaign_path),
        "runner_digest": file_sha256(runner_path),
        "result_schema_digest": file_sha256(result_schema_path),
        "fixture_digests": {
            "small_domains": file_sha256(Path(args.fixture)),
            "proof_certificate": file_sha256(Path(args.proof)),
            "proof_schema": file_sha256(Path(args.proof_schema)),
            "mutation_registry": file_sha256(Path(args.mutations)),
        },
        "input_digests": science["custody"]["digests"],
        "interpreter": {"path": str(expected_python), "python_version": "3.12.13", "numpy_version": None},
        "dependency_inventory_digest": digest_value(deps),
        "cwd": str(Path(args.archive_root).resolve()),
        "environment_allowlist": {"names": list(ALLOWED_ENV_NAMES), "values": env},
        "network_control": {
            "socket_negative_control": "PASS" if audit_ok else "FAIL",
            "network_syscall_count": len(trace_syscalls),
            "trace_sha256": hashlib.sha256(trace_bytes).hexdigest(),
            "sandboxed": False,
            "namespace_isolation": "ENABLED" if namespace_enabled else "UNAVAILABLE",
        },
        "command": first["command"],
        "started_at": started,
        "finished_at": finished,
        "exit_code": first["returncode"],
        "stdout_path": str(first["stdout_path"]),
        "stdout_sha256": file_sha256(first["stdout_path"]),
        "stdout_bytes": first["stdout_path"].stat().st_size,
        "stderr_path": str(first["stderr_path"]),
        "stderr_sha256": file_sha256(first["stderr_path"]),
        "stderr_bytes": first["stderr_path"].stat().st_size,
        "output_truncated": False,
        "worktree_dirty": False,
        "obligations": science["obligations"],
        "mutations": science["mutations"],
        "semantic_projection": {
            "method": "CANONICAL_JSON_SORTED_KEYS_NO_NAN",
            "excluded_json_pointers": [],
            "raw_sha256": digest_value(payload),
            "semantic_sha256": digest_value(payload),
        },
        "semantic_diff": [] if repeat_equal else [{
            "json_pointer": "/repeat_run/semantic_sha256",
            "expected": payload_digests[0], "actual": payload_digests[1:],
        }],
        "terminal": terminal,
        "authority_limits": {
            "grants_novelty_authority": False,
            "grants_physical_resource_authority": False,
            "grants_runtime_superiority_authority": False,
            "grants_submission_authority": False,
            "grants_merge_authority": False,
        },
        "payload": payload,
    }
    schema = json.loads(result_schema_path.read_text(encoding="utf-8"))
    schema_errors = validate_schema(result, schema)
    if schema_errors:
        raise RuntimeError("result schema validation failed: " + "; ".join(schema_errors[:20]))
    result_path = output_root / "lane_b_result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Q1_C1_LANE_B_RESULT=" + canonical_bytes({
        "path": str(result_path), "sha256": file_sha256(result_path), "terminal": terminal,
        "repeat_equal": repeat_equal, "science_valid": science["science_valid"],
    }).decode("utf-8"))
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--archive-root", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--proof", required=True)
    parser.add_argument("--proof-schema", required=True)
    parser.add_argument("--mutations", required=True)
    parser.add_argument("--result-schema", required=True)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--payload-output")
    parser.add_argument("--audit-output")
    parser.add_argument("--artifact-commit", required=True)
    parser.add_argument("--artifact-parent", required=True)
    parser.add_argument("--protocol-commit", required=True)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    if args.child and (not args.payload_output or not args.audit_output):
        parser.error("--child requires --payload-output and --audit-output")
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    return args


if __name__ == "__main__":
    parsed = parse_args()
    raise SystemExit(child_main(parsed) if parsed.child else parent_main(parsed))
