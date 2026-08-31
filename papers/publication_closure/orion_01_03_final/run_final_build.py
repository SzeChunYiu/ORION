#!/usr/bin/env python3
from __future__ import annotations

import dataclasses
import subprocess
import sys
import tempfile
from pathlib import Path

import build_final_packages as b

_original_publication_markdown = b.publication_markdown
_original_pandoc_fragment = b.pandoc_fragment
_original_mathify_code = b.mathify_code


def publication_markdown(spec: b.Spec) -> str:
    text = _original_publication_markdown(spec)
    if spec.key == "ORION-02":
        text = text.replace(
            "The first counted revival attempt, the first study, asked",
            "The first counted held-out revival study asked",
        )
        text = text.replace(
            "The second counted attempt, the second study, evaluated",
            "The second counted held-out certificate study evaluated",
        )
        text = text.replace(
            "Against a corrected exact-cell parent",
            "Against the corrected exact-cell parent method",
        )
        text = text.replace(
            "Across both counted attempts the same negative control was at least as strong on the recorded criteria as the specified geometry.",
            "Across both counted attempts the same outcome-independent negative control was at least as strong as the specified geometry on the recorded criteria.",
        )
        text = text.replace(
            "A subsequent diagnostic on the same committed records",
            "A subsequent diagnostic on the same frozen records",
        )
        text = text.replace(
            "The preserved the second study result illustrates",
            "The preserved second-study result illustrates",
        )
        text = text.replace("The the second study corpus", "The second-study corpus")
        text = text.replace("Jin and Ren (2024)", "Jin and Ren (2025)")
    if spec.mode == "quantum" and "## Author contributions" not in text:
        marker = "\n## References\n"
        contribution = (
            "\n## Author contributions\n\n"
            "Sze Chun Yiu is the sole listed author and performed the authorship contributions represented in this manuscript, including the formal analysis, computational verification, and manuscript preparation.\n"
        )
        if marker not in text:
            raise SystemExit(f"missing References marker for Quantum author contribution insertion: {spec.key}")
        text = text.replace(marker, contribution + marker, 1)
    return text


def pandoc_fragment(markdown: str, *, shift: bool = False) -> str:
    return _original_pandoc_fragment(markdown, shift=shift).replace("\\tightlist\n", "")


def mathify_code(text: str) -> str:
    rendered = _original_mathify_code(text)
    return rendered.replace(r"\A_post", r"\setminus A_post")


def _sanitized_checker(source: Path, *, old_schema: str, new_schema: str, old_protocol: str, new_protocol: str) -> str:
    text = source.read_text(encoding="utf-8")
    text = text.replace(old_schema, new_schema)
    text = text.replace(old_protocol, new_protocol)
    text = text.replace("THEORY_STEP_COMPLETE__PROMOTION_NOT_YET_EARNED", "FINITE_CHECK_COMPLETE__NO_SCIENTIFIC_PROMOTION")
    text = text.replace("PROMOTION_FAILED_AT_THEORY_STEP", "FINITE_CHECK_FOUND_A_VIOLATION")
    return text


def prepare_orion02_public_artifact() -> Path:
    root = Path(tempfile.mkdtemp(prefix="orion02-public-artifact-"))
    paper = b.PAPERS / "orion-02-fiberguard-finite-fibre"
    floor_src = paper / "experiments/fibre-diameter-floor-v1/check_fibre_diameter_floor.py"
    refine_src = paper / "experiments/refinement-to-certifiability-v1/check_refinement_to_certifiability.py"

    floor = root / "check_fibre_diameter_floor.py"
    floor.write_text(
        _sanitized_checker(
            floor_src,
            old_schema="ORION.ORION02.FibreDiameterFloor.Result.v1",
            new_schema="FibreDiameterFloor.PublicResult.v1",
            old_protocol="ORION02.FIBRE_DIAMETER_FLOOR.v1",
            new_protocol="FIBRE_DIAMETER_FLOOR_PUBLIC.v1",
        ),
        encoding="utf-8",
    )
    refine = root / "check_refinement_to_certifiability.py"
    refine.write_text(
        _sanitized_checker(
            refine_src,
            old_schema="ORION.ORION02.RefinementToCertifiability.Result.v1",
            new_schema="RefinementToCertifiability.PublicResult.v1",
            old_protocol="ORION02.REFINEMENT_TO_CERTIFIABILITY.v1",
            new_protocol="REFINEMENT_TO_CERTIFIABILITY_PUBLIC.v1",
        ),
        encoding="utf-8",
    )

    for script, result_name in (
        (floor, "expected_fibre_diameter_floor.json"),
        (refine, "expected_refinement_to_certifiability.json"),
    ):
        proc = subprocess.run(
            [sys.executable, str(script)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(f"public reproducibility checker failed: {script.name}\n{proc.stdout}\n{proc.stderr}")
        (root / result_name).write_text(proc.stdout, encoding="utf-8")

    (root / "README.md").write_text(
        "# Finite hostile verification artifact\n\n"
        "This anonymous supplementary artifact contains the two deterministic checkers used for the finite verification statements in the manuscript. Run:\n\n"
        "```text\npython3 check_fibre_diameter_floor.py\npython3 check_refinement_to_certifiability.py\n```\n\n"
        "The corresponding `expected_*.json` files are the frozen outputs produced by this package build. The scripts use only the Python standard library. They search for finite counterexamples and include planted-violation controls so an all-clear result is not accepted from a checker that cannot fire. These computations corroborate implementation and transcription only; the manuscript proofs carry the general finite theorem authority.\n",
        encoding="utf-8",
    )
    return root


b.publication_markdown = publication_markdown
b.pandoc_fragment = pandoc_fragment
b.mathify_code = mathify_code

_orion02_artifact = prepare_orion02_public_artifact()
b.SPECS = [
    dataclasses.replace(spec, ancillary=_orion02_artifact) if spec.key == "ORION-02" else spec
    for spec in b.SPECS
]

if __name__ == "__main__":
    raise SystemExit(b.main())
