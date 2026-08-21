"""Tests for the SHA-256 representation boundary.

The regression fixture at the bottom is the one that matters: it is the exact row
shape from the P1-U R6 native primary, which rejected 100% of its scored rows
because one raw-hex predicate met two representations. See
``research/failures/2026-08-digest-representation-boundary-mixup/``.
"""

from __future__ import annotations

from hashlib import sha256

import pytest

from orion.core.digests import (
    CANONICAL_PREFIX,
    DigestForm,
    DigestFormError,
    digest_form,
    is_digest,
    is_prefixed,
    is_raw_hex,
    normalize_all,
    require_form,
    same_digest,
    to_prefixed,
    to_raw_hex,
)

RAW = sha256(b"an assessment object").hexdigest()
PREFIXED = CANONICAL_PREFIX + RAW


def test_the_two_forms_are_distinguished() -> None:
    assert digest_form(RAW) is DigestForm.RAW_HEX
    assert digest_form(PREFIXED) is DigestForm.PREFIXED
    assert is_raw_hex(RAW) and not is_raw_hex(PREFIXED)
    assert is_prefixed(PREFIXED) and not is_prefixed(RAW)
    assert is_digest(RAW) and is_digest(PREFIXED)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "nope",
        RAW[:-1],
        RAW + "a",
        RAW.upper(),
        CANONICAL_PREFIX,
        CANONICAL_PREFIX + RAW[:-1],
        "sha256:" + "g" * 64,
        b"a" * 64,
        None,
        64,
        ["a" * 64],
    ],
)
def test_non_digests_are_rejected_in_both_forms(value: object) -> None:
    assert digest_form(value) is None
    assert is_digest(value) is False


def test_conversion_is_total_over_both_forms_and_idempotent() -> None:
    for value in (RAW, PREFIXED):
        assert to_raw_hex(value) == RAW
        assert to_prefixed(value) == PREFIXED
    assert to_raw_hex(to_prefixed(RAW)) == RAW
    assert to_prefixed(to_raw_hex(PREFIXED)) == PREFIXED


def test_a_crossed_boundary_raises_rather_than_returning_false() -> None:
    """The whole reason this module exists.

    A boolean would make "wrong representation" indistinguishable from "failed
    validation", which is how an engineering defect became campaign evidence.
    """

    with pytest.raises(DigestFormError) as crossed:
        require_form(PREFIXED, DigestForm.RAW_HEX, label="pre_state_hash")
    message = str(crossed.value)
    assert "pre_state_hash" in message
    assert "PREFIXED" in message and "RAW_HEX" in message
    assert "to_raw_hex()" in message

    with pytest.raises(DigestFormError, match="to_prefixed"):
        require_form(RAW, DigestForm.PREFIXED, label="responsibility_digest")


def test_bad_data_is_reported_differently_from_a_crossed_boundary() -> None:
    with pytest.raises(DigestFormError, match="not a SHA-256 digest in either form"):
        require_form("nope", DigestForm.RAW_HEX, label="x")


def test_require_form_returns_the_value_untouched_when_it_already_matches() -> None:
    assert require_form(RAW, DigestForm.RAW_HEX) is RAW
    assert require_form(PREFIXED, DigestForm.PREFIXED) is PREFIXED


def test_equality_is_representation_independent() -> None:
    assert same_digest(RAW, PREFIXED)
    assert same_digest(PREFIXED, RAW)
    assert RAW != PREFIXED, "the raw == comparison is exactly what same_digest replaces"
    other = sha256(b"different").hexdigest()
    assert not same_digest(RAW, other)
    assert not same_digest(RAW, "nope")
    assert not same_digest("nope", RAW)


def test_normalize_all_names_the_offending_index() -> None:
    assert normalize_all([RAW, PREFIXED], DigestForm.RAW_HEX) == (RAW, RAW)
    assert normalize_all([RAW, PREFIXED], DigestForm.PREFIXED) == (PREFIXED, PREFIXED)
    with pytest.raises(DigestFormError, match=r"mechanic_digests\[1\]"):
        normalize_all([RAW, "nope"], DigestForm.RAW_HEX, label="mechanic_digests")
    with pytest.raises(DigestFormError, match="iterable"):
        normalize_all(RAW, DigestForm.RAW_HEX)


def test_normalize_all_accepts_an_empty_iterable() -> None:
    """Emptiness is the caller's business; this function only converts."""

    assert normalize_all([], DigestForm.RAW_HEX) == ()


# --- the R6 regression fixture ------------------------------------------------


def _r6_native_row() -> dict[str, object]:
    """The P1-U R6 row shape: harness raw hex beside transfer-v2 prefixed digests."""

    assessment = PREFIXED  # what transfer-v2 content_digest() actually returns
    state_hash = RAW  # what the research harness actually reports
    arm = {
        "responsibility_digest": assessment,
        "interface_digest": assessment,
        "revision_gate_digest": assessment,
        "mechanic_digests": [assessment],
        "assessment_digests": [assessment],
    }
    return {
        "runtime": {
            "pre_state_hash": state_hash,
            "post_state_hash": state_hash,
            "final_state_digest": state_hash,
        },
        "base": dict(arm),
        "ard": dict(arm),
    }


def test_one_raw_predicate_over_the_r6_row_rejects_every_valid_row() -> None:
    """Pin the original defect, so the fix cannot be quietly reverted."""

    row = _r6_native_row()
    arm = row["base"]
    assert isinstance(arm, dict)
    # This is `_is_hex64` from gpt_r6_native_primary.py, verbatim in behaviour.
    assert is_raw_hex(row["runtime"]["pre_state_hash"]) is True  # type: ignore[index]
    assert is_raw_hex(arm["responsibility_digest"]) is False
    assert all(not is_raw_hex(value) for value in arm["mechanic_digests"])


def test_the_r6_row_validates_once_each_field_is_required_in_its_own_form() -> None:
    row = _r6_native_row()
    runtime = row["runtime"]
    assert isinstance(runtime, dict)
    for key in ("pre_state_hash", "post_state_hash", "final_state_digest"):
        assert require_form(runtime[key], DigestForm.RAW_HEX, label=key)
    for arm_name in ("base", "ard"):
        arm = row[arm_name]
        assert isinstance(arm, dict)
        for key in ("responsibility_digest", "interface_digest", "revision_gate_digest"):
            assert require_form(arm[key], DigestForm.PREFIXED, label=f"{arm_name}.{key}")
        for key in ("mechanic_digests", "assessment_digests"):
            assert normalize_all(arm[key], DigestForm.PREFIXED, label=f"{arm_name}.{key}")


def test_the_crossed_boundary_message_would_have_named_the_r6_defect() -> None:
    """A campaign hitting this today gets told what went wrong, not `False`."""

    row = _r6_native_row()
    arm = row["base"]
    assert isinstance(arm, dict)
    with pytest.raises(DigestFormError) as error:
        require_form(
            arm["responsibility_digest"],
            DigestForm.RAW_HEX,
            label="base.responsibility_digest",
        )
    assert "base.responsibility_digest" in str(error.value)
    assert "to_raw_hex()" in str(error.value)
