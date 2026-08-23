from pathlib import Path

from orion.programme.top_tier_promotion import (
    PAPER_SPECS,
    PROGRAMME_FILE,
    assert_top_tier_promotion_contract,
    audit_top_tier_promotion,
)


ROOT = Path(__file__).resolve().parents[3]


def test_top_tier_promotion_contract_is_structurally_complete() -> None:
    assert_top_tier_promotion_contract(ROOT)


def test_promotion_wave_covers_exactly_p6_through_p15() -> None:
    assert [number for number, _, _ in PAPER_SPECS] == list(range(6, 16))


def test_programme_contract_explicitly_denies_text_only_scientific_authority() -> None:
    text = (ROOT / PROGRAMME_FILE).read_text(encoding="utf-8")
    assert "No text-only edit may move a paper between levels." in text
    assert "No self-authority" in text
    assert "Negative-history rule" in text


def test_each_paper_protocol_remains_non_self_promoting() -> None:
    findings = audit_top_tier_promotion(ROOT)
    assert not [f for f in findings if f.code == "TT-SELF-PROMOTION-FORBIDDEN"]

    for _, directory, _ in PAPER_SPECS:
        text = (
            ROOT / "papers" / directory / "TOP_TIER_PROMOTION_V1.md"
        ).read_text(encoding="utf-8")
        assert "**Top-tier state:** `TOP_TIER_SUBMISSION_READY`" not in text
        assert "## Maximum claim to earn" in text
        assert "## Top-tier promotion gate" in text
