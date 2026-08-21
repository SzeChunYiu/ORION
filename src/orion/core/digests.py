"""The two SHA-256 representations this repository uses, told apart.

Both are the same 32 bytes. They are written differently, and the difference is
load-bearing at every boundary where they meet:

``RAW_HEX``
    64 lowercase hex characters, no prefix. What the research harness reports for
    state endpoints, and what the 22 independently-written hex-64 predicates
    under ``src/orion/`` accept --- ``programme.identity.is_sha256``,
    ``providers.development.base``, the ``self_orion`` preflights, and so on.

``PREFIXED``
    ``sha256:`` followed by those same 64 characters. What
    ``orion.transfer.v2.canonical.content_digest`` returns, and therefore what
    every transfer-v2 receipt, responsibility hypothesis, interface-adequacy
    check and revision-gate assessment carries.

Nothing in the repository named these apart before, and joining a harness value
to a transfer-v2 value is a normal thing to want to do. The P1-U R6 native
primary did it, validated both with one raw-hex predicate, and rejected 100% of
its scored rows --- for a day, as a scientific ``CANNOT_CHECK``. See
``research/failures/2026-08-digest-representation-boundary-mixup/``.

The design decision that follows from that record
-------------------------------------------------
:func:`require_form` **raises**. It does not return ``False``.

This is the whole point of the module and it is worth being explicit about, since
a predicate would have been the smaller API. Where a check can fail either
because a value is wrong *or* because it is the right value in the wrong
representation, a boolean makes those two outcomes indistinguishable in the
return --- and the second then gets counted as the first. That is not a
hypothetical: it is exactly how an engineering defect entered a campaign record
as evidence. A crossed boundary is a caller error, it is always fixable by the
caller, and it says nothing about the data. So it is an exception, and the
message names both forms and the conversion that fixes it.

Predicates are still available for genuine content validation
(:func:`is_raw_hex`, :func:`is_prefixed`, :func:`is_digest`), because "is this
field a digest at all?" is a real question with a real boolean answer.

This module deliberately does not import from ``orion.transfer.v2.canonical`` or
``orion.programme.identity``, and neither of those is changed to import this one.
Both are other lanes' surfaces under ``AGENTS.md``, and the constant they would
share is seven characters long. What this module offers is the vocabulary; a lane
adopts it when it next touches the boundary.
"""

from __future__ import annotations

from enum import Enum

CANONICAL_PREFIX = "sha256:"
DIGEST_HEX_LENGTH = 64

_HEX = frozenset("0123456789abcdef")


class DigestForm(str, Enum):
    """How a SHA-256 value is written."""

    RAW_HEX = "RAW_HEX"
    PREFIXED = "PREFIXED"


class DigestFormError(ValueError):
    """A digest crossed a representation boundary, or is not a digest at all.

    Deliberately a ``ValueError`` subclass: callers that already guard a boundary
    with ``except ValueError`` keep working, and callers that want to distinguish
    this case can.
    """


def _hex_body(value: object) -> str | None:
    """The 64-hex body of ``value`` in either form, or ``None`` if it has none."""

    if not isinstance(value, str):
        return None
    body = value[len(CANONICAL_PREFIX) :] if value.startswith(CANONICAL_PREFIX) else value
    if len(body) != DIGEST_HEX_LENGTH:
        return None
    if any(character not in _HEX for character in body):
        return None
    return body


def digest_form(value: object) -> DigestForm | None:
    """Which form ``value`` is written in, or ``None`` if it is not a digest.

    Note that ``sha256:`` followed by 64 hex is ``PREFIXED`` and bare 64 hex is
    ``RAW_HEX``; there is no third state and no ambiguity, because a bare digest
    cannot begin with a colon.
    """

    if _hex_body(value) is None:
        return None
    assert isinstance(value, str)  # _hex_body already rejected every other type
    return DigestForm.PREFIXED if value.startswith(CANONICAL_PREFIX) else DigestForm.RAW_HEX


def is_digest(value: object) -> bool:
    """True if ``value`` is a SHA-256 digest in *either* form."""

    return _hex_body(value) is not None


def is_raw_hex(value: object) -> bool:
    return digest_form(value) is DigestForm.RAW_HEX


def is_prefixed(value: object) -> bool:
    return digest_form(value) is DigestForm.PREFIXED


def to_raw_hex(value: object, *, label: str = "digest") -> str:
    """Return ``value`` as bare 64-hex, accepting either form.

    Raises :class:`DigestFormError` if ``value`` is not a digest at all --- which
    is a different failure from crossing the boundary, and is reported as such.
    """

    body = _hex_body(value)
    if body is None:
        raise DigestFormError(f"{label} is not a SHA-256 digest in either form: {value!r}")
    return body


def to_prefixed(value: object, *, label: str = "digest") -> str:
    """Return ``value`` as ``sha256:<64-hex>``, accepting either form."""

    return CANONICAL_PREFIX + to_raw_hex(value, label=label)


def require_form(value: object, form: DigestForm, *, label: str = "digest") -> str:
    """Return ``value`` unchanged if it is already in ``form``; otherwise raise.

    The two failures are reported differently on purpose. A value that is not a
    digest is bad data. A value that is a digest in the other representation is a
    caller error with a one-call fix, and the message says which call::

        require_form(content_digest(x), DigestForm.RAW_HEX, label="pre_state_hash")
        # DigestFormError: pre_state_hash is a PREFIXED SHA-256 digest, but this
        # boundary requires RAW_HEX; convert it with to_raw_hex()

    Written as a literal block rather than a doctest: the message wraps, and a
    doctest that only passes when nobody runs it is worse than a comment.
    """

    actual = digest_form(value)
    if actual is None:
        raise DigestFormError(f"{label} is not a SHA-256 digest in either form: {value!r}")
    if actual is not form:
        converter = "to_raw_hex()" if form is DigestForm.RAW_HEX else "to_prefixed()"
        raise DigestFormError(
            f"{label} is a {actual.value} SHA-256 digest, but this boundary "
            f"requires {form.value}; convert it with {converter}"
        )
    assert isinstance(value, str)
    return value


def same_digest(left: object, right: object) -> bool:
    """Representation-independent equality.

    ``sha256:abc…`` and ``abc…`` are the same digest. Comparing them with ``==``
    says otherwise, which is the same mistake as the validator this module exists
    for, one operator further along.
    """

    left_body = _hex_body(left)
    if left_body is None:
        return False
    return left_body == _hex_body(right)


def normalize_all(values: object, form: DigestForm, *, label: str = "digests") -> tuple[str, ...]:
    """Convert an iterable of digests to one form, naming the offender on failure.

    Digest *lists* are where this goes wrong quietly --- ``mechanic_digests`` and
    ``assessment_digests`` in the R6 row were both lists, and an ``all(...)`` over
    them reports one ``False`` for any number of reasons at any index.
    """

    if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
        raise DigestFormError(f"{label} must be an iterable of digests, got {values!r}")
    convert = to_raw_hex if form is DigestForm.RAW_HEX else to_prefixed
    return tuple(
        convert(value, label=f"{label}[{index}]") for index, value in enumerate(values)
    )


__all__ = [
    "CANONICAL_PREFIX",
    "DIGEST_HEX_LENGTH",
    "DigestForm",
    "DigestFormError",
    "digest_form",
    "is_digest",
    "is_prefixed",
    "is_raw_hex",
    "normalize_all",
    "require_form",
    "same_digest",
    "to_prefixed",
    "to_raw_hex",
]
