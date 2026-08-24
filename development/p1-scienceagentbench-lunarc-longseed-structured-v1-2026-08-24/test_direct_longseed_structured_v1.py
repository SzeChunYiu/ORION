#!/usr/bin/env python3
"""Focused unit tests for the frozen structured-output discriminator."""

import importlib.util
import json
import pathlib
import unittest


HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "direct_longseed_structured_v1", HERE / "direct_longseed_structured_v1.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

MARKERS = [
    "MK0_7b91c2",
    "MK1_a46fd8",
    "MK2_19e3ab",
    "MK3_c58071",
    "MK4_ef268d",
    "MK5_34da90",
]
ALLOWED = {"amber", "cobalt", "delta", "ember", "fjord", "glyph", "harbor", "iris"}


def content(markers=MARKERS, choice="amber", **extra):
    value = {"markers": markers, "sampling_choice": choice}
    value.update(extra)
    return json.dumps(value, separators=(",", ":"))


class StructuredContentTests(unittest.TestCase):
    def test_accepts_exact_schema_content(self):
        result = MODULE.validate_structured_content(content(), MARKERS, ALLOWED)
        self.assertEqual(result["parsed"], {"markers": MARKERS, "sampling_choice": "amber"})
        self.assertTrue(result["raw_content_strict_json_parse"])
        self.assertTrue(result["exact_keys"])
        self.assertTrue(result["marker_order_exact"])
        self.assertTrue(result["sampling_choice_allowed"])
        self.assertTrue(result["exact_schema_no_extra_text_or_keys"])

    def test_rejects_prefix_text_without_reparsing(self):
        result = MODULE.validate_structured_content("preface\n" + content(), MARKERS, ALLOWED)
        self.assertIsNone(result["parsed"])
        self.assertFalse(result["raw_content_strict_json_parse"])
        self.assertFalse(result["exact_schema_no_extra_text_or_keys"])

    def test_rejects_extra_key(self):
        result = MODULE.validate_structured_content(content(extra="forbidden"), MARKERS, ALLOWED)
        self.assertTrue(result["raw_content_strict_json_parse"])
        self.assertFalse(result["exact_keys"])
        self.assertFalse(result["exact_schema_no_extra_text_or_keys"])

    def test_rejects_wrong_marker_array(self):
        result = MODULE.validate_structured_content(content(markers=MARKERS[:-1]), MARKERS, ALLOWED)
        self.assertTrue(result["raw_content_strict_json_parse"])
        self.assertTrue(result["exact_keys"])
        self.assertFalse(result["marker_order_exact"])
        self.assertFalse(result["exact_schema_no_extra_text_or_keys"])

    def test_rejects_disallowed_choice(self):
        result = MODULE.validate_structured_content(content(choice="violet"), MARKERS, ALLOWED)
        self.assertTrue(result["raw_content_strict_json_parse"])
        self.assertFalse(result["sampling_choice_allowed"])
        self.assertFalse(result["exact_schema_no_extra_text_or_keys"])


class CompletionBodyTests(unittest.TestCase):
    def test_adds_only_frozen_json_schema_field(self):
        sampling = {"temperature": 0.8, "n_predict": 128}
        schema = {"type": "object", "additionalProperties": False}
        body = MODULE.build_completion_body(sampling, "PROMPT", 101, schema)
        self.assertEqual(
            body,
            {
                "temperature": 0.8,
                "n_predict": 128,
                "prompt": "PROMPT",
                "seed": 101,
                "cache_prompt": False,
                "json_schema": schema,
            },
        )


if __name__ == "__main__":
    unittest.main()
