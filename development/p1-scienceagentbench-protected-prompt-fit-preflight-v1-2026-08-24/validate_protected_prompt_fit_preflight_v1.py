#!/usr/bin/env python3
"""Synthetic hostile validation for protected prompt-fit preflight V1.

Only invented nonbenchmark rows are supplied to the implementation.  The
suite opens no protected benchmark source, evaluator, rubric, gold, candidate,
outcome, manuscript, PDF, provider, model, scheduler, CI, or pytest route.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
IMPLEMENTATION_PATH = ROOT / "protected_prompt_fit_preflight_v1.py"
CONTRACT_PATH = ROOT / "PROTECTED_PROMPT_FIT_CONTRACT_V1.json"
RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"
MASK_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json"
)
PROMPT_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
)
DIRECT_CONTRACT_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
)

EXPECTED_UPSTREAM_HASHES = {
    "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json":
        "442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json":
        "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json":
        "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py":
        "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
}

ROW_FIELDS = {
    "instance_id",
    "domain",
    "task_inst",
    "output_fname",
    "domain_knowledge",
    "dataset_folder_tree",
    "dataset_preview",
}
SOURCE_VALUE_FIELDS = (
    "task_inst",
    "output_fname",
    "domain_knowledge",
    "dataset_folder_tree",
    "dataset_preview",
)
STATIC_PHASES = ("RR_PHASE0", "OS_PHASE1", "NR_PHASE0", "NR_PHASE1")
PHASE_TO_ARM = {
    "RR_PHASE0": "RR",
    "OS_PHASE1": "OS",
    "NR_PHASE0": "NR",
    "NR_PHASE1": "NR",
}
SEEDS = {"1": 101, "2": 202, "3": 303}
FROZEN_TOKENIZER_BINDING = {
    "model_repository": "unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF",
    "model_revision": "b17cb02dd882d5b6ab62fc777ad2995f19668350",
    "model_filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "model_bytes": 18556689568,
    "model_sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
    "inference_tokenizer_binding": "GGUF_BYTES",
    "llama_server_sha256": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
    "llama_cpp_version": "b10434",
    "llama_cpp_commit": "7e4c0a96880dae4fc4268ad441f8a6446bd5460a",
}


def load_module(path: Path, name: str):
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preflight = load_module(IMPLEMENTATION_PATH, "orion_protected_prompt_fit_preflight_v1")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def descriptor(value: Any, state: str) -> dict[str, Any]:
    raw = canonical_bytes(value)
    return {
        "state": state,
        "value_type": "null" if value is None else "string",
        "canonical_json_bytes": len(raw),
        "canonical_json_sha256": sha256_bytes(raw),
    }


def invented_rows() -> list[dict[str, Any]]:
    return [
        {
            "instance_id": "1",
            "domain": "Invented astronomy",
            "task_inst": "SYNTHETIC_SECRET_TASK_ALPHA_7f91",
            "output_fname": "invented_alpha.json",
            "domain_knowledge": "SYNTHETIC_SECRET_KNOWLEDGE_ALPHA_19e2",
            "dataset_folder_tree": "invented/alpha/input.csv",
            "dataset_preview": None,
        },
        {
            "instance_id": "2",
            "domain": "Invented materials",
            "task_inst": "SYNTHETIC_SECRET_TASK_BETA_4c61",
            "output_fname": "invented_beta.csv",
            "domain_knowledge": None,
            "dataset_folder_tree": "invented/beta/data.tsv",
            "dataset_preview": "SYNTHETIC_SECRET_PREVIEW_BETA_b398",
        },
    ]


def invented_manifest(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    chosen = copy.deepcopy(rows or invented_rows())
    records = []
    for row in chosen:
        fields = {
            name: descriptor(
                row[name],
                "VISIBLE_FROM_PHASE_0"
                if name in {"task_inst", "output_fname"}
                else "MASK_THEN_EXACT_RECOVER",
            )
            for name in SOURCE_VALUE_FIELDS
        }
        binding = {
            "instance_id": row["instance_id"],
            "domain": row["domain"],
            "fields": fields,
        }
        records.append(
            {
                **binding,
                "license_partition": "SYNTHETIC_NONBENCHMARK",
                "binding_sha256": sha256_bytes(canonical_bytes(binding)),
            }
        )
    return {
        "schema_version": "orion.p1.scienceagentbench.mask-manifest.v1",
        "manifest_id": "SYNTHETIC_NONBENCHMARK_MASK_MANIFEST",
        "authority": "SYNTHETIC_NONBENCHMARK_ONLY",
        "source": {
            "dataset": "invented/nonbenchmark",
            "revision": "synthetic-revision",
            "split": "synthetic",
            "verified_parquet_sha256": sha256_bytes(b"invented parquet identity"),
        },
        "records": records,
        "outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }


def invented_row_source(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "orion.p1.scienceagentbench.authorized-row-source.v1",
        "authority": "SYNTHETIC_NONBENCHMARK_VALIDATION_ONLY",
        "source": {
            "dataset": "invented/nonbenchmark",
            "revision": "synthetic-revision",
            "split": "synthetic",
            "verified_parquet_sha256": sha256_bytes(b"invented parquet identity"),
            "extraction_mode": "STRICT_JSON_AUTHORIZED_EXTRACTION",
            "official_outcomes_opened": False,
        },
        "rows": copy.deepcopy(rows or invented_rows()),
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class ProtectedPromptFitPreflightSyntheticTests(unittest.TestCase):
    def api(self, name: str):
        self.assertIsNotNone(preflight, "protected prompt-fit implementation is missing")
        value = getattr(preflight, name, None)
        self.assertTrue(callable(value), f"preflight API missing: {name}")
        return value

    def contract_and_prompt(self) -> tuple[dict[str, Any], dict[str, Any]]:
        self.assertTrue(CONTRACT_PATH.is_file(), "protected prompt-fit contract is missing")
        return load_json(CONTRACT_PATH), load_json(PROMPT_PATH)

    def build_receipt(
        self,
        *,
        rows: list[dict[str, Any]] | None = None,
        manifest: dict[str, Any] | None = None,
        ledger: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        contract, prompt = self.contract_and_prompt()
        chosen_rows = copy.deepcopy(rows or invented_rows())
        source = invented_row_source(chosen_rows)
        chosen_manifest = copy.deepcopy(manifest or invented_manifest(chosen_rows))
        source_bytes = canonical_bytes(source) + b"\n"
        receipt = self.api("build_preflight_receipt")(
            row_source=source,
            row_source_bytes=len(source_bytes),
            row_source_sha256=sha256_bytes(source_bytes),
            mask_manifest=chosen_manifest,
            mask_manifest_sha256=sha256_bytes(canonical_bytes(chosen_manifest)),
            prompt_bundle=prompt,
            prompt_bundle_sha256=file_sha256(PROMPT_PATH),
            direct_route_contract_sha256=file_sha256(DIRECT_CONTRACT_PATH),
            contract=contract,
            token_ledger=ledger,
            production=False,
        )
        return receipt, source, chosen_manifest, contract

    def assert_contract_error(self, operation, fragment: str) -> None:
        self.assertIsNotNone(preflight, "protected prompt-fit implementation is missing")
        error = getattr(preflight, "ContractError", None)
        self.assertTrue(isinstance(error, type), "preflight ContractError is missing")
        with self.assertRaises(error) as caught:
            operation()
        self.assertIn(fragment, str(caught.exception))

    def complete_ledger(
        self,
        receipt: dict[str, Any],
        contract: dict[str, Any],
        *,
        tokens: int = 100,
    ) -> dict[str, Any]:
        records = []
        for task in receipt["task_receipts"]:
            for record in task["state_independent_prompts"]:
                records.append(
                    {
                        "instance_id": task["instance_id"],
                        "phase_id": record["phase_id"],
                        "attempt": record["attempt"],
                        "prompt_sha256": record["prompt_sha256"],
                        "prompt_tokens": tokens,
                    }
                )
        return {
            "schema_version": "orion.p1.scienceagentbench.exact-gguf-token-ledger.v1",
            "authority": "OWNER_SUPPLIED_EXACT_GGUF_TOKENIZER_MEASUREMENT_ONLY__NO_OUTCOME_AUTHORITY",
            "tokenizer_binding": copy.deepcopy(contract["tokenizer_binding"]),
            "source_bindings": copy.deepcopy(receipt["source_bindings"]),
            "records": records,
            "official_outcomes_opened": 0,
            "scientific_authority_delta": "NONE",
        }

    def test_01_owned_artifacts_and_exact_upstream_bindings(self) -> None:
        self.assertTrue(IMPLEMENTATION_PATH.is_file(), "protected prompt-fit implementation is missing")
        contract, _ = self.contract_and_prompt()
        declared = {
            entry["path"]: entry["sha256"] for entry in contract["upstream_bindings"]
        }
        self.assertEqual(declared, EXPECTED_UPSTREAM_HASHES)
        for relative, expected in declared.items():
            self.assertEqual(file_sha256(REPO_ROOT / relative), expected)
        self.api("validate_production_bindings")(
            contract,
            load_json(MASK_PATH),
            load_json(PROMPT_PATH),
        )

    def test_02_canonical_json_is_strict_utf8_sorted_and_nonfinite_fails(self) -> None:
        canonical = self.api("canonical_json_bytes")
        self.assertEqual(canonical({"z": "å", "a": 1}), b'{"a":1,"z":"\xc3\xa5"}')
        self.assert_contract_error(lambda: canonical({"x": float("nan")}), "canonical")

    def test_03_packetizer_binds_every_source_value_and_exact_shapes(self) -> None:
        row = invented_rows()[0]
        manifest_record = invented_manifest([row])["records"][0]
        result = self.api("packetize_bound_row")(row, manifest_record)
        self.assertEqual(
            set(result),
            {"manifest_binding_sha256", "masked_packet", "recovered_packet"},
        )
        self.assertEqual(set(result["masked_packet"]), ROW_FIELDS)
        self.assertEqual(set(result["recovered_packet"]), ROW_FIELDS)
        self.assertEqual(result["masked_packet"]["task_inst"], row["task_inst"])
        self.assertEqual(result["recovered_packet"], row)
        for name in ("domain_knowledge", "dataset_folder_tree", "dataset_preview"):
            self.assertEqual(
                result["masked_packet"][name],
                {
                    "state": "MASKED_UNTIL_PHASE1",
                    "source_value_type": "null" if row[name] is None else "string",
                },
            )

    def test_04_packetizer_rejects_extra_missing_wrong_type_hash_domain_and_binding(self) -> None:
        row = invented_rows()[0]
        manifest_record = invented_manifest([row])["records"][0]
        cases: list[tuple[dict[str, Any], dict[str, Any], str]] = []
        extra = copy.deepcopy(row)
        extra["gold"] = "forbidden"
        cases.append((extra, manifest_record, "row fields"))
        missing = copy.deepcopy(row)
        del missing["dataset_preview"]
        cases.append((missing, manifest_record, "row fields"))
        wrong_type = copy.deepcopy(row)
        wrong_type["dataset_preview"] = 7
        cases.append((wrong_type, manifest_record, "type"))
        wrong_hash = copy.deepcopy(row)
        wrong_hash["task_inst"] += " mutated"
        cases.append((wrong_hash, manifest_record, "binding"))
        wrong_domain = copy.deepcopy(row)
        wrong_domain["domain"] = "Another domain"
        cases.append((wrong_domain, manifest_record, "domain"))
        bad_binding = copy.deepcopy(manifest_record)
        bad_binding["binding_sha256"] = "0" * 64
        cases.append((row, bad_binding, "manifest record binding"))
        for candidate, record, fragment in cases:
            self.assert_contract_error(
                lambda candidate=candidate, record=record: self.api("packetize_bound_row")(
                    candidate, record
                ),
                fragment,
            )

    def test_05_exact_static_matrix_and_rr_dynamic_boundary(self) -> None:
        receipt, _, _, _ = self.build_receipt()
        self.assertEqual(receipt["counts"]["tasks"], 2)
        self.assertEqual(receipt["counts"]["state_independent_prompt_records"], 24)
        self.assertEqual(receipt["counts"]["dynamic_rr_phase1_records"], 6)
        for task in receipt["task_receipts"]:
            static = task["state_independent_prompts"]
            self.assertEqual(
                [(entry["phase_id"], entry["attempt"]) for entry in static],
                [(phase, attempt) for phase in STATIC_PHASES for attempt in (1, 2, 3)],
            )
            for entry in static:
                self.assertEqual(entry["arm_id"], PHASE_TO_ARM[entry["phase_id"]])
                self.assertEqual(entry["seed"], SEEDS[str(entry["attempt"])])
                self.assertIsInstance(entry["prompt_bytes"], int)
                self.assertEqual(len(entry["prompt_sha256"]), 64)
            dynamic = task["dynamic_rr_phase1_prompts"]
            self.assertEqual([entry["attempt"] for entry in dynamic], [1, 2, 3])
            for entry in dynamic:
                self.assertEqual(
                    entry["fit_status"],
                    "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED",
                )
                self.assertIsNone(entry["prompt_bytes"])
                self.assertIsNone(entry["prompt_sha256"])
                self.assertIsNone(entry["prompt_tokens"])

    def test_06_rendered_prompt_hash_matches_frozen_template_bytes(self) -> None:
        rows = invented_rows()
        receipt, _, manifest, _ = self.build_receipt(rows=rows)
        prompt = load_json(PROMPT_PATH)
        packets = self.api("packetize_bound_row")(rows[0], manifest["records"][0])
        expected = prompt["templates"]["OS_PHASE1"]["text"]
        expected = expected.replace("{{ATTEMPT_ORDINAL}}", "1")
        expected = expected.replace(
            "{{RECOVERED_PACKET_JSON}}",
            canonical_bytes(packets["recovered_packet"]).decode("utf-8"),
        )
        self.assertTrue(expected.endswith("\n"))
        record = receipt["task_receipts"][0]["state_independent_prompts"][3]
        self.assertEqual(record["phase_id"], "OS_PHASE1")
        self.assertEqual(record["attempt"], 1)
        self.assertEqual(record["prompt_bytes"], len(expected.encode("utf-8")))
        self.assertEqual(record["prompt_sha256"], sha256_bytes(expected.encode("utf-8")))

    def test_07_receipt_retains_no_protected_packet_or_prompt_body(self) -> None:
        receipt, source, _, _ = self.build_receipt()
        raw = canonical_bytes(receipt)
        for row in source["rows"]:
            for name in SOURCE_VALUE_FIELDS:
                value = row[name]
                if isinstance(value, str):
                    self.assertNotIn(value.encode("utf-8"), raw)
        self.assertEqual(receipt["counts"]["packet_bodies_retained"], 0)
        self.assertEqual(receipt["counts"]["prompt_bodies_retained"], 0)
        for task in receipt["task_receipts"]:
            self.assertEqual(
                set(task),
                {
                    "instance_id",
                    "manifest_binding_sha256",
                    "masked_packet_binding",
                    "recovered_packet_binding",
                    "state_independent_prompts",
                    "dynamic_rr_phase1_prompts",
                    "static_prompt_fit_status",
                    "overall_prompt_fit_status",
                },
            )
            self.assertNotIn("packet", task["masked_packet_binding"])
            self.assertNotIn("packet", task["recovered_packet_binding"])

    def test_08_no_exact_tokenizer_ledger_keeps_all_counts_null(self) -> None:
        receipt, _, _, _ = self.build_receipt()
        self.assertEqual(
            receipt["tokenizer_measurement"]["status"],
            "CANNOT_CHECK_EXACT_GGUF_TOKEN_LEDGER_NOT_SUPPLIED",
        )
        self.assertIsNone(receipt["tokenizer_measurement"]["ledger_sha256"])
        for task in receipt["task_receipts"]:
            self.assertEqual(
                task["static_prompt_fit_status"],
                "CANNOT_CHECK_EXACT_GGUF_TOKEN_LEDGER_NOT_SUPPLIED",
            )
            self.assertEqual(
                task["overall_prompt_fit_status"],
                "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_AND_EXACT_GGUF_TOKEN_LEDGER_REQUIRED",
            )
            for record in task["state_independent_prompts"]:
                self.assertIsNone(record["prompt_tokens"])
                self.assertEqual(
                    record["fit_status"],
                    "CANNOT_CHECK_EXACT_GGUF_TOKEN_LEDGER_NOT_SUPPLIED",
                )

    def test_09_complete_bound_ledger_checks_static_fit_only(self) -> None:
        without, _, _, contract = self.build_receipt()
        ledger = self.complete_ledger(without, contract, tokens=100)
        receipt, _, _, _ = self.build_receipt(ledger=ledger)
        self.assertEqual(
            receipt["tokenizer_measurement"]["status"],
            "CHECKED_FROM_BOUND_OWNER_SUPPLIED_EXACT_GGUF_LEDGER",
        )
        self.assertTrue(receipt["tokenizer_measurement"]["all_state_independent_prompts_fit"])
        for task in receipt["task_receipts"]:
            self.assertEqual(task["static_prompt_fit_status"], "FIT_FROM_BOUND_TOKEN_LEDGER")
            self.assertEqual(
                task["overall_prompt_fit_status"],
                "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED",
            )
            self.assertTrue(all(record["prompt_tokens"] == 100 for record in task["state_independent_prompts"]))
            self.assertTrue(all(record["fit_status"] == "FIT_FROM_BOUND_TOKEN_LEDGER" for record in task["state_independent_prompts"]))

    def test_10_bound_ledger_overflow_is_retained_as_adverse_static_fit(self) -> None:
        without, _, _, contract = self.build_receipt()
        ledger = self.complete_ledger(without, contract, tokens=32768)
        receipt, _, _, _ = self.build_receipt(ledger=ledger)
        self.assertFalse(receipt["tokenizer_measurement"]["all_state_independent_prompts_fit"])
        self.assertTrue(
            all(
                task["static_prompt_fit_status"] == "DOES_NOT_FIT_FROM_BOUND_TOKEN_LEDGER"
                for task in receipt["task_receipts"]
            )
        )
        self.assertEqual(receipt["claim_boundary"]["production_admissibility"], "CANNOT_CHECK")

    def test_11_hostile_token_ledgers_fail_closed(self) -> None:
        without, _, _, contract = self.build_receipt()
        base = self.complete_ledger(without, contract)
        cases: list[tuple[dict[str, Any], str]] = []
        incomplete = copy.deepcopy(base)
        incomplete["records"].pop()
        cases.append((incomplete, "completeness"))
        duplicate = copy.deepcopy(base)
        duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
        cases.append((duplicate, "duplicate"))
        extra = copy.deepcopy(base)
        extra["records"].append(
            {
                "instance_id": "999",
                "phase_id": "OS_PHASE1",
                "attempt": 1,
                "prompt_sha256": "0" * 64,
                "prompt_tokens": 1,
            }
        )
        cases.append((extra, "unexpected"))
        wrong_hash = copy.deepcopy(base)
        wrong_hash["records"][0]["prompt_sha256"] = "0" * 64
        cases.append((wrong_hash, "prompt hash"))
        wrong_runtime = copy.deepcopy(base)
        wrong_runtime["tokenizer_binding"]["model_sha256"] = "0" * 64
        cases.append((wrong_runtime, "tokenizer binding"))
        wrong_source = copy.deepcopy(base)
        wrong_source["source_bindings"]["row_source_sha256"] = "0" * 64
        cases.append((wrong_source, "source bindings"))
        wrong_count = copy.deepcopy(base)
        wrong_count["records"][0]["prompt_tokens"] = True
        cases.append((wrong_count, "prompt_tokens"))
        negative_count = copy.deepcopy(base)
        negative_count["records"][0]["prompt_tokens"] = -1
        cases.append((negative_count, "prompt_tokens"))
        for ledger, fragment in cases:
            self.assert_contract_error(lambda ledger=ledger: self.build_receipt(ledger=ledger), fragment)

    def test_12_duplicate_missing_and_reordered_sources_fail_closed(self) -> None:
        rows = invented_rows()
        duplicated = [copy.deepcopy(rows[0]), copy.deepcopy(rows[0])]
        self.assert_contract_error(lambda: self.build_receipt(rows=duplicated), "duplicate")
        manifest = invented_manifest(rows)
        self.assert_contract_error(lambda: self.build_receipt(rows=[rows[0]], manifest=manifest), "task set")
        reversed_rows = list(reversed(rows))
        self.assert_contract_error(lambda: self.build_receipt(rows=reversed_rows, manifest=manifest), "order")

    def test_13_source_and_manifest_boundaries_are_strict(self) -> None:
        rows = invented_rows()
        manifest = invented_manifest(rows)
        source = invented_row_source(rows)
        contract, prompt = self.contract_and_prompt()
        source["source"]["official_outcomes_opened"] = True
        source_file = canonical_bytes(source) + b"\n"
        operation = lambda: self.api("build_preflight_receipt")(
            row_source=source,
            row_source_bytes=len(source_file),
            row_source_sha256=sha256_bytes(source_file),
            mask_manifest=manifest,
            mask_manifest_sha256=sha256_bytes(canonical_bytes(manifest)),
            prompt_bundle=prompt,
            prompt_bundle_sha256=file_sha256(PROMPT_PATH),
            direct_route_contract_sha256=file_sha256(DIRECT_CONTRACT_PATH),
            contract=contract,
            token_ledger=None,
            production=False,
        )
        self.assert_contract_error(operation, "outcomes")

        source = invented_row_source(rows)
        source["forbidden"] = "extra"
        source_file = canonical_bytes(source) + b"\n"
        operation = lambda: self.api("build_preflight_receipt")(
            row_source=source,
            row_source_bytes=len(source_file),
            row_source_sha256=sha256_bytes(source_file),
            mask_manifest=manifest,
            mask_manifest_sha256=sha256_bytes(canonical_bytes(manifest)),
            prompt_bundle=prompt,
            prompt_bundle_sha256=file_sha256(PROMPT_PATH),
            direct_route_contract_sha256=file_sha256(DIRECT_CONTRACT_PATH),
            contract=contract,
            token_ledger=None,
            production=False,
        )
        self.assert_contract_error(operation, "row source fields")

    def test_14_strict_json_rejects_duplicate_members_nonfinite_and_nonobject(self) -> None:
        parse = self.api("strict_json_object_from_bytes")
        self.assertEqual(parse(b'{"x":1}', "fixture"), {"x": 1})
        for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'[]', b'{} trailing'):
            self.assert_contract_error(lambda payload=payload: parse(payload, "fixture"), "strict")

    def test_15_output_is_absolute_exclusive_nofollow_and_rolls_back(self) -> None:
        write_new = self.api("write_new_canonical_json")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            existing = base / "existing.json"
            existing.write_bytes(b"sentinel\n")
            self.assert_contract_error(lambda: write_new(existing, {"x": 1}), "exists")
            self.assertEqual(existing.read_bytes(), b"sentinel\n")

            target = base / "target.json"
            target.write_bytes(b"target\n")
            linked = base / "linked.json"
            linked.symlink_to(target)
            self.assert_contract_error(lambda: write_new(linked, {"x": 1}), "exists")
            self.assertEqual(target.read_bytes(), b"target\n")

            fresh = base / "fresh.json"
            digest = write_new(fresh, {"x": 1})
            self.assertEqual(fresh.read_bytes(), b'{"x":1}\n')
            self.assertEqual(digest, sha256_bytes(fresh.read_bytes()))

            failed = base / "failed.json"
            with mock.patch.object(preflight.os, "write", side_effect=OSError("synthetic failure")):
                self.assert_contract_error(lambda: write_new(failed, {"x": 1}), "write")
            self.assertFalse(failed.exists())

            self.assert_contract_error(lambda: write_new(Path("relative.json"), {"x": 1}), "absolute")

    def test_16_cli_path_validation_rejects_aliases_hardlinks_and_symlinks(self) -> None:
        validate = self.api("validate_cli_paths")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            source = base / "source.json"
            mask = base / "mask.json"
            source.write_text("source")
            mask.write_text("mask")
            validate(
                {"source": source, "mask": mask},
                {"output": base / "fresh.json"},
                {},
            )
            hardlink = base / "hardlink.json"
            os.link(source, hardlink)
            self.assert_contract_error(
                lambda: validate(
                    {"source": source, "alias": hardlink},
                    {"output": base / "fresh2.json"},
                    {},
                ),
                "device/inode",
            )
            symlink = base / "symlink.json"
            symlink.symlink_to(source)
            self.assert_contract_error(
                lambda: validate(
                    {"source": symlink, "mask": mask},
                    {"output": base / "fresh3.json"},
                    {},
                ),
                "symlink",
            )
            self.assert_contract_error(
                lambda: validate(
                    {"source": source},
                    {"output": source},
                    {},
                ),
                "alias",
            )

    def test_17_production_mode_requires_exact_102_task_manifest(self) -> None:
        contract, prompt = self.contract_and_prompt()
        rows = invented_rows()
        source = invented_row_source(rows)
        manifest = invented_manifest(rows)
        source_file = canonical_bytes(source) + b"\n"
        self.assert_contract_error(
            lambda: self.api("build_preflight_receipt")(
                row_source=source,
                row_source_bytes=len(source_file),
                row_source_sha256=sha256_bytes(source_file),
                mask_manifest=manifest,
                mask_manifest_sha256=sha256_bytes(canonical_bytes(manifest)),
                prompt_bundle=prompt,
                prompt_bundle_sha256=file_sha256(PROMPT_PATH),
                direct_route_contract_sha256=file_sha256(DIRECT_CONTRACT_PATH),
                contract=contract,
                token_ledger=None,
                production=True,
                verified_upstream_sha256s=EXPECTED_UPSTREAM_HASHES,
            ),
            "production mask manifest",
        )

    def test_18_claim_boundary_and_billed_cost_remain_lower_bound(self) -> None:
        receipt, _, _, contract = self.build_receipt()
        self.assertEqual(
            receipt["claim_boundary"],
            {
                "production_admissibility": "CANNOT_CHECK",
                "semantic_choice_sensitivity": "NOT_ESTABLISHED",
                "billed_cost_usd": None,
                "billed_cost_status": "CANNOT_CHECK",
                "official_tasks_executed": 0,
                "official_outcomes_opened": 0,
                "scientific_authority_delta": "NONE",
            },
        )
        self.assertEqual(receipt["claim_boundary"], contract["claim_boundary"])

    def test_19_synthetic_validation_receipt_binds_final_core_artifacts(self) -> None:
        self.assertTrue(RECEIPT_PATH.is_file(), "synthetic validation receipt is missing")
        receipt = load_json(RECEIPT_PATH)
        self.assertEqual(receipt["status"], "PASS_SYNTHETIC_HOSTILE_VALIDATION")
        self.assertEqual(receipt["tests"], 26)
        self.assertEqual(receipt["official_tasks_opened"], 0)
        self.assertEqual(receipt["official_outcomes_opened"], 0)
        self.assertEqual(receipt["scientific_authority_delta"], "NONE")
        self.assertEqual(
            receipt["artifact_sha256"],
            {
                "PROTECTED_PROMPT_FIT_CONTRACT_V1.json": file_sha256(CONTRACT_PATH),
                "protected_prompt_fit_preflight_v1.py": file_sha256(IMPLEMENTATION_PATH),
                "validate_protected_prompt_fit_preflight_v1.py": file_sha256(Path(__file__)),
            },
        )

    def test_20_unhashable_task_ids_fail_as_contract_errors(self) -> None:
        rows = invented_rows()
        valid_manifest = invented_manifest(rows)
        bad_rows = copy.deepcopy(rows)
        bad_rows[0]["instance_id"] = ["not", "hashable"]
        self.assert_contract_error(
            lambda: self.build_receipt(rows=bad_rows, manifest=valid_manifest),
            "instance_id",
        )

        bad_manifest = copy.deepcopy(valid_manifest)
        bad_manifest["records"][0]["instance_id"] = ["not", "hashable"]
        self.assert_contract_error(
            lambda: self.build_receipt(rows=rows, manifest=bad_manifest),
            "instance_id",
        )

    def test_21_tokenizer_identity_is_hardcoded_not_mutable_contract_consensus(self) -> None:
        contract, _ = self.contract_and_prompt()
        validate = self.api("_contract_semantics")
        validate(contract)
        mutations = {
            "model_filename": "other.gguf",
            "model_bytes": FROZEN_TOKENIZER_BINDING["model_bytes"] + 1,
            "model_sha256": "0" * 64,
            "model_revision": "0" * 40,
        }
        for field, value in mutations.items():
            mutated = copy.deepcopy(contract)
            mutated["tokenizer_binding"][field] = value
            # A mutable ledger can agree with the same mutation; hardcoded
            # implementation identity must still reject the pair.
            self_consistent_ledger_binding = copy.deepcopy(mutated["tokenizer_binding"])
            self.assertEqual(
                self_consistent_ledger_binding[field], mutated["tokenizer_binding"][field]
            )
            self.assert_contract_error(
                lambda mutated=mutated: validate(mutated),
                "tokenizer binding",
            )
        self.assertEqual(contract["tokenizer_binding"], FROZEN_TOKENIZER_BINDING)

    def test_22_live_staging_receipt_and_descriptor_measurement_are_both_required(self) -> None:
        validate = self.api("validate_live_staging_binding")
        measurement = {
            "model_filename": FROZEN_TOKENIZER_BINDING["model_filename"],
            "live_model_bytes": FROZEN_TOKENIZER_BINDING["model_bytes"],
            "live_model_sha256": FROZEN_TOKENIZER_BINDING["model_sha256"],
            "measurement_method": "HELD_FILE_DESCRIPTOR_FSTAT_AND_FULL_SHA256",
        }
        staging = {
            "schema_version": "orion.p1.scienceagentbench.live-gguf-staging-receipt.v1",
            "authority": "INDEPENDENT_LIVE_GGUF_STAGING_MEASUREMENT__NO_TASK_OR_OUTCOME_AUTHORITY",
            "model_binding": copy.deepcopy(FROZEN_TOKENIZER_BINDING),
            "independent_verification": {
                "completed_before_preflight": True,
                "measurement_method": "FULL_FILE_SHA256_AND_BYTE_COUNT",
                "verifier_role": "INDEPENDENT_STAGING_PROCESS",
            },
            "live_measurement": copy.deepcopy(measurement),
            "source_receipt_sha256": "a" * 64,
            "official_tasks_opened": 0,
            "official_outcomes_opened": 0,
            "scientific_authority_delta": "NONE",
        }
        raw = canonical_bytes(staging) + b"\n"
        result = validate(
            staging_receipt=staging,
            staging_receipt_bytes=len(raw),
            staging_receipt_sha256=sha256_bytes(raw),
            live_model_measurement=measurement,
        )
        self.assertEqual(result["status"], "PASS_INDEPENDENT_RECEIPT_AND_LIVE_GGUF_MATCH")
        self.assertEqual(result["source_receipt_sha256"], "a" * 64)

        for changed in (
            {"live_model_bytes": FROZEN_TOKENIZER_BINDING["model_bytes"] + 1},
            {"live_model_sha256": "0" * 64},
        ):
            wrong_live = {**measurement, **changed}
            wrong_staging = copy.deepcopy(staging)
            wrong_staging["live_measurement"] = copy.deepcopy(wrong_live)
            wrong_raw = canonical_bytes(wrong_staging) + b"\n"
            self.assert_contract_error(
                lambda wrong_live=wrong_live, wrong_staging=wrong_staging, wrong_raw=wrong_raw: validate(
                    staging_receipt=wrong_staging,
                    staging_receipt_bytes=len(wrong_raw),
                    staging_receipt_sha256=sha256_bytes(wrong_raw),
                    live_model_measurement=wrong_live,
                ),
                "live GGUF",
            )

        receipt_only = copy.deepcopy(staging)
        receipt_only["live_measurement"]["live_model_sha256"] = "0" * 64
        receipt_only_raw = canonical_bytes(receipt_only) + b"\n"
        self.assert_contract_error(
            lambda: validate(
                staging_receipt=receipt_only,
                staging_receipt_bytes=len(receipt_only_raw),
                staging_receipt_sha256=sha256_bytes(receipt_only_raw),
                live_model_measurement=measurement,
            ),
            "live measurement",
        )

    def test_23_held_input_descriptor_survives_swap_and_detects_path_change(self) -> None:
        open_resources = self.api("open_cli_resources")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            source = base / "source.json"
            source.write_bytes(b"original-held-bytes\n")
            output = base / "output.json"
            with open_resources(
                {"source": source}, {"output": output}, {}
            ) as resources:
                displaced = base / "source-displaced.json"
                source.rename(displaced)
                source.write_bytes(b"attacker-replacement\n")
                self.assertEqual(
                    resources.read_input_bytes("source"), b"original-held-bytes\n"
                )
                self.assert_contract_error(
                    resources.verify_all_paths_unchanged,
                    "changed",
                )

    def test_24_output_openat_rejects_concurrent_parent_swap_and_rolls_back(self) -> None:
        open_resources = self.api("open_cli_resources")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            parent = base / "held-parent"
            parent.mkdir()
            output = parent / "receipt.json"
            with open_resources({}, {"receipt": output}, {}) as resources:
                displaced = base / "held-parent-displaced"
                real_open = preflight.os.open
                swapped = False

                def racing_open(path, flags, mode=0o777, *, dir_fd=None):
                    nonlocal swapped
                    if path == "receipt.json" and flags & os.O_CREAT and not swapped:
                        parent.rename(displaced)
                        parent.mkdir()
                        swapped = True
                    return real_open(path, flags, mode, dir_fd=dir_fd)

                with mock.patch.object(preflight.os, "open", side_effect=racing_open):
                    self.assert_contract_error(
                        lambda: resources.write_output_canonical_json("receipt", {"x": 1}),
                        "directory",
                    )
                self.assertTrue(swapped)
            self.assertFalse((displaced / "receipt.json").exists())
            self.assertFalse((parent / "receipt.json").exists())

    def test_25_input_swap_after_output_write_triggers_receipt_rollback(self) -> None:
        open_resources = self.api("open_cli_resources")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            source = base / "source.json"
            source.write_bytes(b"original\n")
            output = base / "receipt.json"
            with open_resources(
                {"source": source}, {"receipt": output}, {}
            ) as resources:
                actual_write = resources.outputs["receipt"].write_canonical_json

                def write_then_swap(value):
                    digest = actual_write(value)
                    source.rename(base / "source-displaced.json")
                    source.write_bytes(b"replacement\n")
                    return digest

                with mock.patch.object(
                    resources.outputs["receipt"],
                    "write_canonical_json",
                    side_effect=write_then_swap,
                ):
                    self.assert_contract_error(
                        lambda: resources.write_output_canonical_json("receipt", {"x": 1}),
                        "changed",
                    )
            self.assertFalse(output.exists())

    def test_26_output_name_swap_is_detected_without_deleting_replacement(self) -> None:
        open_resources = self.api("open_cli_resources")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            output = base / "receipt.json"
            displaced = base / "receipt-displaced.json"
            with open_resources({}, {"receipt": output}, {}) as resources:
                actual_write = resources.outputs["receipt"].write_canonical_json

                def write_then_replace(value):
                    digest = actual_write(value)
                    output.rename(displaced)
                    output.write_bytes(b"attacker-output-replacement\n")
                    return digest

                with mock.patch.object(
                    resources.outputs["receipt"],
                    "write_canonical_json",
                    side_effect=write_then_replace,
                ):
                    self.assert_contract_error(
                        lambda: resources.write_output_canonical_json("receipt", {"x": 1}),
                        "rollback could not be verified",
                    )
            self.assertEqual(output.read_bytes(), b"attacker-output-replacement\n")
            self.assertTrue(displaced.exists())


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ProtectedPromptFitPreflightSyntheticTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_PROTECTED_PROMPT_FIT_PREFLIGHT_V1_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} official_tasks=0 official_outcomes=0 "
        "production_admissibility=CANNOT_CHECK semantic_choice=NOT_ESTABLISHED"
    )
