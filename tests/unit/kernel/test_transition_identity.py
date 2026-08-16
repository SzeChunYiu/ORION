from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, fields, replace
from math import copysign, inf, nan

import pytest

import orion.kernel as kernel
from orion.kernel.transition import (
    CANONICALIZATION_VERSION,
    MAX_CANONICAL_BYTES,
    MAX_CANONICAL_DEPTH,
    MAX_CANONICAL_NODES,
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    UNICODE_DATABASE_VERSION,
    UNICODE_POLICY,
    WORKFLOW_VERSION,
    CanonicalizationError,
    LedgerExpectation,
    ProgramProjection,
    TransitionKind,
    answer_record_hash,
    canonical_answer_record,
    canonical_digest,
    canonical_json_bytes,
    canonical_json_loads,
    canonical_mechanic_cell,
    projection_hash,
)
from orion.mechanics.model import (
    DimensionWaiver,
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.program import current_program_cells


def _full_cell(*, mechanic_id: str = "TEST.STEP", handoff_required: bool = True) -> MechanicCell:
    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose="exercise complete typed identity",
        scope="one transition atom",
        input_ids=("input:1",),
        output_ids=("output:1",),
        handoff_fields=(
            HandoffField(
                field_id="result",
                description="typed result",
                schema_ref="schema://result/v1",
                required=handoff_required,
            ),
        ),
        state_ids=("state:1",),
        observable_ids=("observation:1",),
        action_ids=("action:1",),
        transition_semantics=("pre -> post",),
        mathematical_semantics=("post = reduce(pre, action)",),
        invariant_ids=("invariant:1",),
        constraint_ids=("constraint:1",),
        objective_ids=("objective:1",),
        metrics=(
            MetricSpec(
                metric_id="metric:quality",
                description="non-compensatory quality gate",
                kind=MetricKind.QUALITY,
                direction=MetricDirection.NON_COMPENSATORY_GATE,
                unit="boolean",
                required_for_handoff=True,
                threshold_semantics="must equal true",
                uncertainty_semantics="unknown is CANNOT_CHECK",
            ),
        ),
        optimization_rules=("minimize residuals",),
        uncertainty_semantics=("preserve missingness",),
        resource_coordinates=("wall_time",),
        failure_signatures=("STATE_MISMATCH",),
        falsifiers=("post hash differs",),
        diagnosis_rules=("compare exact hashes",),
        storage_contracts=("atomic envelope",),
        provenance_contracts=("content-bound",),
        verification_contracts=("pure replay",),
        authority_boundaries=("appraisal is not authorization",),
        engineering_contracts=("fsync before acknowledgement",),
        dependency_ids=("dependency:1",),
        external_dependency_contract_ids=("external:1",),
        child_mechanic_ids=("TEST.CHILD",),
        reopen_triggers=("dependency revoked",),
        search_coverage_obligations=("challenge vocabulary",),
        parent_domain_hypotheses=("event sourcing",),
        saturation_criteria=("bounded hostile suite green",),
        empirical_open_coordinates=("crash injection",),
        provisional_dimensions=(MechanicDimension.STORAGE,),
        waivers=(
            DimensionWaiver(
                MechanicDimension.PARENT_DISCIPLINE,
                "parent search is outside this exact transition atom",
            ),
        ),
    )


def _projection(
    *cells: MechanicCell,
    records: tuple[AnswerRecord, ...] | None = None,
    active_record_ids: tuple[str, ...] | None = None,
    reopened_coordinates: tuple[tuple[str, str, str], ...] = (),
) -> ProgramProjection:
    if records is None:
        records = (_answer(mechanic_id=cells[0].mechanic_id),)
    if active_record_ids is None:
        active_record_ids = tuple(record.record_id for record in records)
    return ProgramProjection(
        schema_version=PROJECTION_SCHEMA_VERSION,
        workflow_version=WORKFLOW_VERSION,
        reducer_version=REDUCER_VERSION,
        seed_cells=tuple(cells),
        records=records,
        active_record_ids=active_record_ids,
        reopened_coordinates=reopened_coordinates,
    )


def _answer(
    *,
    record_id: str = "record:1",
    mechanic_id: str = "TEST.STEP",
    value: str = "fsync before acknowledgement",
    supersedes: str = "",
) -> AnswerRecord:
    return AnswerRecord(
        record_id=record_id,
        mechanic_id=mechanic_id,
        dimension=MechanicDimension.ENGINEERING,
        lane="candidate-only",
        evidence_refs=("evidence:1",),
        evidence_bindings=(("evidence:1", "e" * 64),),
        payload=(("engineering_contracts", (value,)),),
        supersedes=supersedes,
    )


def test_projection_hash_binds_complete_typed_state() -> None:
    first = _projection(_full_cell(handoff_required=True))
    changed_handoff = _projection(_full_cell(handoff_required=False))
    changed_metric = _projection(
        replace(
            _full_cell(),
            metrics=(replace(_full_cell().metrics[0], required_for_handoff=False),),
        )
    )
    changed_waiver = _projection(
        replace(
            _full_cell(),
            waivers=(
                DimensionWaiver(
                    MechanicDimension.PARENT_DISCIPLINE,
                    "different scoped waiver reason",
                ),
            ),
        )
    )
    changed_provisionality = _projection(
        replace(_full_cell(), provisional_dimensions=(MechanicDimension.VERIFICATION,))
    )

    hashes = {
        projection_hash(item)
        for item in (
            first,
            changed_handoff,
            changed_metric,
            changed_waiver,
            changed_provisionality,
        )
    }
    assert len(hashes) == 5


def test_projection_hash_binds_exact_seed_and_active_record_body() -> None:
    seed = _full_cell()
    first_record = _answer(value="first body")
    changed_record = _answer(value="changed body")
    first = _projection(seed, records=(first_record,))
    changed_active_body = _projection(seed, records=(changed_record,))
    changed_seed = _projection(
        replace(seed, engineering_contracts=("changed seed",)),
        records=(first_record,),
    )

    assert projection_hash(first) != projection_hash(changed_active_body)
    assert projection_hash(first) != projection_hash(changed_seed)
    assert first.seed_cells == (seed,)
    assert first.active_records == (first_record,)


def test_projection_hash_binds_record_catalog_and_active_tip() -> None:
    cell = _full_cell()
    root = _answer(record_id="record:0", value="old body")
    tip = _answer(record_id="record:1", value="first body", supersedes="record:0")
    first = _projection(
        cell,
        records=(root, tip),
        active_record_ids=("record:1",),
    )
    changed_root = _answer(record_id="record:0", value="changed old body")
    changed_catalog = _projection(
        cell,
        records=(changed_root, tip),
        active_record_ids=("record:1",),
    )
    second = _answer(
        record_id="record:2", value="new active body", supersedes="record:1"
    )
    changed_tip = _projection(
        cell,
        records=(root, tip, second),
        active_record_ids=("record:2",),
    )

    assert projection_hash(first) != projection_hash(changed_catalog)
    assert projection_hash(first) != projection_hash(changed_tip)


def test_semantically_unordered_projection_catalogs_encode_deterministically() -> None:
    first_cell = _full_cell(mechanic_id="A")
    second_cell = _full_cell(mechanic_id="B")
    first = _projection(
        first_cell,
        second_cell,
        records=(
            _answer(record_id="r1", mechanic_id="A"),
            _answer(record_id="r2", mechanic_id="B"),
        ),
        active_record_ids=("r1", "r2"),
    )
    reordered = _projection(
        second_cell,
        first_cell,
        records=(
            _answer(record_id="r2", mechanic_id="B"),
            _answer(record_id="r1", mechanic_id="A"),
        ),
        active_record_ids=("r2", "r1"),
    )

    assert projection_hash(first) == projection_hash(reordered)


def test_cell_encoder_is_explicit_json_data() -> None:
    payload = canonical_mechanic_cell(_full_cell())

    assert payload["mechanic_id"] == "TEST.STEP"
    assert payload["handoff_fields"][0]["required"] is True
    assert payload["metrics"][0]["kind"] == MetricKind.QUALITY.value
    assert payload["metrics"][0]["direction"] == MetricDirection.NON_COMPENSATORY_GATE.value
    assert payload["provisional_dimensions"] == [MechanicDimension.STORAGE.value]
    assert payload["waivers"][0]["dimension"] == MechanicDimension.PARENT_DISCIPLINE.value
    assert all(not callable(item) for item in payload.values())
    assert set(payload) == {item.name for item in fields(MechanicCell)}
    assert set(payload["handoff_fields"][0]) == {
        item.name for item in fields(HandoffField)
    }
    assert set(payload["metrics"][0]) == {item.name for item in fields(MetricSpec)}
    assert set(payload["waivers"][0]) == {
        item.name for item in fields(DimensionWaiver)
    }


def test_answer_encoder_binds_every_proposal_field_without_granting_authority() -> None:
    record = _answer(supersedes="record:0")
    payload = canonical_answer_record(record)

    assert payload == {
        "record_id": "record:1",
        "mechanic_id": "TEST.STEP",
        "dimension": MechanicDimension.ENGINEERING.value,
        "lane": "candidate-only",
        "evidence_refs": ["evidence:1"],
        "evidence_bindings": [["evidence:1", "e" * 64]],
        "payload": [["engineering_contracts", ["fsync before acknowledgement"]]],
        "handoff_payload": [],
        "waiver_reason": "",
        "supersedes": "record:0",
    }
    assert answer_record_hash(record) == (
        "73d72d5a795df74c8168ab76908d42e196949bc1c73dc29b6fd8fd343dc94da6"
    )


def test_answer_hash_normalizes_semantically_unordered_record_fields() -> None:
    first = replace(
        _answer(),
        evidence_refs=("evidence:2", "evidence:1"),
        evidence_bindings=(
            ("evidence:2", "f" * 64),
            ("evidence:1", "e" * 64),
        ),
    )
    reordered = replace(
        first,
        evidence_refs=tuple(reversed(first.evidence_refs)),
        evidence_bindings=tuple(reversed(first.evidence_bindings)),
    )
    handoff = AnswerRecord(
        record_id="handoff",
        mechanic_id="TEST.STEP",
        dimension=MechanicDimension.HANDOFF,
        lane="candidate-only",
        evidence_refs=("evidence:1",),
        evidence_bindings=(("evidence:1", "e" * 64),),
        handoff_payload=(
            HandoffField("z", "z field", "schema://z"),
            HandoffField("a", "a field", "schema://a"),
        ),
    )

    assert answer_record_hash(first) == answer_record_hash(reordered)
    assert answer_record_hash(handoff) == answer_record_hash(
        replace(handoff, handoff_payload=tuple(reversed(handoff.handoff_payload)))
    )


def test_answer_hash_rejects_duplicate_structured_fields() -> None:
    duplicate_payload = replace(
        _answer(),
        payload=(
            ("engineering_contracts", ("first",)),
            ("engineering_contracts", ("second",)),
        ),
    )
    handoff_field = HandoffField("same", "field", "schema://field")
    duplicate_handoff = AnswerRecord(
        record_id="handoff",
        mechanic_id="TEST.STEP",
        dimension=MechanicDimension.HANDOFF,
        lane="candidate-only",
        evidence_refs=("evidence:1",),
        evidence_bindings=(("evidence:1", "e" * 64),),
        handoff_payload=(handoff_field, handoff_field),
    )

    with pytest.raises(CanonicalizationError, match="payload fields"):
        answer_record_hash(duplicate_payload)
    with pytest.raises(CanonicalizationError, match="handoff fields"):
        answer_record_hash(duplicate_handoff)


def test_canonical_digest_is_domain_separated_and_version_fields_are_bound() -> None:
    payload = {"value": [1, "one", True, None]}
    assert canonical_digest(payload, domain="orion.test.a") != canonical_digest(
        payload, domain="orion.test.b"
    )

    projection = _projection(_full_cell())
    for field_name, value in (
        ("reducer_version", "orion.reducer.experimental"),
        ("workflow_version", "orion.workflow.experimental"),
        ("schema_version", "orion.projection.experimental"),
    ):
        with pytest.raises(ValueError, match=field_name):
            replace(projection, **{field_name: value})


def test_canonical_profile_is_versioned_and_preserves_type_identity() -> None:
    assert CANONICALIZATION_VERSION == "orion.typed-canonical.v1"
    assert UNICODE_POLICY == "orion.unicode.ucd3.2-nfc-assigned.v1"
    assert UNICODE_DATABASE_VERSION == "3.2.0"
    assert canonical_digest([1], domain="orion.test.types") != canonical_digest(
        (1,), domain="orion.test.types"
    )
    assert canonical_digest(True, domain="orion.test.types") != canonical_digest(
        1, domain="orion.test.types"
    )
    assert canonical_digest(0.0, domain="orion.test.types") != canonical_digest(
        -0.0, domain="orion.test.types"
    )
    encoded_float = canonical_json_bytes({"value": 1.5})
    assert CANONICALIZATION_VERSION.encode() in encoded_float
    assert b"float64-bits" in encoded_float


def test_canonical_profile_orders_maps_without_erasing_sequence_types() -> None:
    first = {"z": [1, 2], "a": (1, 2)}
    reordered = {"a": (1, 2), "z": [1, 2]}

    assert canonical_json_bytes(first) == canonical_json_bytes(reordered)
    assert canonical_json_bytes({"value": [1, 2]}) != canonical_json_bytes(
        {"value": (1, 2)}
    )


def test_canonical_map_order_is_utf8_not_jcs_utf16() -> None:
    private_use = "\ue000"
    old_italic_letter = "\U00010300"
    encoded = canonical_json_bytes({old_italic_letter: 1, private_use: 2})

    assert encoded.index(private_use.encode("utf-8")) < encoded.index(
        old_italic_letter.encode("utf-8")
    )


def test_canonical_profile_is_ambient_integer_limit_independent() -> None:
    enormous = 1 << 20000
    encoded = canonical_json_bytes(enormous)

    assert b"int-sign-magnitude" in encoded
    assert canonical_json_loads(encoded) == enormous


def test_canonical_codec_matches_frozen_golden_vector_and_round_trips() -> None:
    value = {"b": (True, -0.0), "a": 1}
    expected = (
        b'["orion-typed-canonical","orion.typed-canonical.v1",'
        b'"orion.unicode.ucd3.2-nfc-assigned.v1","3.2.0",["map",'
        b'[[["str","a"],["int-sign-magnitude",[0,"01"]]],'
        b'[["str","b"],["tuple",'
        b'[["bool",true],["float64-bits","8000000000000000"]]]]]]]'
    )

    assert canonical_json_bytes(value) == expected
    assert canonical_digest(value, domain="orion.test.golden") == (
        "9b51befae76a6a888863ebdf73fd2c7e3dd3c6efafa9cec77f31bde2975b6d88"
    )
    decoded = canonical_json_loads(expected)
    assert decoded == value
    assert type(decoded["b"]) is tuple
    assert copysign(1.0, decoded["b"][1]) == -1.0


def test_canonical_decoder_rejects_unknown_profiles_tags_and_noncanonical_bytes() -> None:
    valid = canonical_json_bytes({"a": 1, "b": 2})
    unknown_profile = valid.replace(
        b"orion.typed-canonical.v1", b"orion.typed-canonical.v9"
    )
    unknown_unicode_policy = valid.replace(
        b"orion.unicode.ucd3.2-nfc-assigned.v1", b"orion.unicode.unknown.v9"
    )
    unknown_unicode_database = valid.replace(b'"3.2.0"', b'"9.9.9"', 1)
    unknown_tag = valid.replace(
        b'["int-sign-magnitude",[0,"01"]]', b'["decimal","1"]'
    )
    noncanonical_spacing = valid.replace(b",", b", ", 1)

    with pytest.raises(CanonicalizationError, match="version"):
        canonical_json_loads(unknown_profile)
    with pytest.raises(CanonicalizationError, match="Unicode policy"):
        canonical_json_loads(unknown_unicode_policy)
    with pytest.raises(CanonicalizationError, match="Unicode database"):
        canonical_json_loads(unknown_unicode_database)
    with pytest.raises(CanonicalizationError, match="tag"):
        canonical_json_loads(unknown_tag)
    with pytest.raises(CanonicalizationError, match="canonical byte"):
        canonical_json_loads(noncanonical_spacing)


def test_unicode_database_version_is_part_of_the_public_kernel_contract() -> None:
    assert kernel.UNICODE_DATABASE_VERSION == UNICODE_DATABASE_VERSION


def test_canonical_boundaries_reject_subclassed_text_and_hostile_json_integers() -> None:
    class TextSubclass(str):
        pass

    with pytest.raises(CanonicalizationError, match="domain"):
        canonical_digest({"value": 1}, domain=TextSubclass("orion.test.domain"))

    hostile = (
        b'["orion-typed-canonical","orion.typed-canonical.v1",'
        b'"orion.unicode.ucd3.2-nfc-assigned.v1","3.2.0",'
        b'["int-sign-magnitude",['
        + (b"9" * 5000)
        + b',"00"]]]'
    )
    with pytest.raises(CanonicalizationError):
        canonical_json_loads(hostile)


def test_canonical_decoder_installs_bounded_numeric_token_hooks(monkeypatch) -> None:
    original_loads = json.loads
    observed: dict[str, object] = {}

    def guarded_loads(source: str, **kwargs: object) -> object:
        observed.update(kwargs)
        return original_loads(source, **kwargs)

    monkeypatch.setattr(json, "loads", guarded_loads)
    assert canonical_json_loads(canonical_json_bytes(1)) == 1
    assert callable(observed.get("parse_int"))
    assert callable(observed.get("parse_float"))
    assert callable(observed.get("parse_constant"))


def test_canonical_codec_has_explicit_resource_bounds() -> None:
    assert MAX_CANONICAL_BYTES == 8_388_608
    assert MAX_CANONICAL_DEPTH == 128
    assert MAX_CANONICAL_NODES == 100_000
    nested: object = None
    for _ in range(MAX_CANONICAL_DEPTH + 1):
        nested = [nested]

    with pytest.raises(CanonicalizationError, match="depth"):
        canonical_json_bytes(nested)
    with pytest.raises(CanonicalizationError, match="byte"):
        canonical_json_bytes("x" * MAX_CANONICAL_BYTES)
    hostile = b"[" * (MAX_CANONICAL_DEPTH + 1000)
    with pytest.raises(CanonicalizationError):
        canonical_json_loads(hostile)


def test_current_mechanics_program_fits_the_canonical_projection_bound() -> None:
    projection = ProgramProjection(
        schema_version=PROJECTION_SCHEMA_VERSION,
        workflow_version=WORKFLOW_VERSION,
        reducer_version=REDUCER_VERSION,
        seed_cells=current_program_cells(),
    )

    digest = projection_hash(projection)

    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)


def test_canonical_profile_requires_normalized_unicode_and_exact_domain() -> None:
    with pytest.raises(CanonicalizationError, match="NFC"):
        canonical_digest("e\u0301", domain="orion.test.unicode")
    for domain in ("", " padded", "padded "):
        with pytest.raises(CanonicalizationError, match="domain"):
            canonical_digest({"value": 1}, domain=domain)
    with pytest.raises(CanonicalizationError, match="assigned"):
        canonical_digest("\u0378", domain="orion.test.unicode")
    with pytest.raises(CanonicalizationError, match="assigned"):
        canonical_digest("\U0001fae8", domain="orion.test.unicode")


def test_set_like_provisional_dimensions_have_order_independent_identity() -> None:
    first_cell = replace(
        _full_cell(),
        provisional_dimensions=(
            MechanicDimension.STORAGE,
            MechanicDimension.VERIFICATION,
        ),
    )
    reordered = replace(
        first_cell,
        provisional_dimensions=tuple(reversed(first_cell.provisional_dimensions)),
    )

    assert projection_hash(_projection(first_cell)) == projection_hash(
        _projection(reordered)
    )


@pytest.mark.parametrize("value", (nan, inf, -inf, {"not-json"}, lambda: None))
def test_canonical_digest_rejects_ambiguous_or_unsupported_values(value: object) -> None:
    with pytest.raises(CanonicalizationError):
        canonical_digest({"value": value}, domain="orion.test.invalid")


def test_projection_rejects_duplicate_or_dangling_identity() -> None:
    cell = _full_cell()
    with pytest.raises(ValueError, match="mechanic"):
        _projection(cell, cell)
    with pytest.raises(ValueError, match="record"):
        _projection(
            cell,
            records=(
                _answer(record_id="record:1"),
                _answer(record_id="record:1", value="different"),
            ),
        )
    with pytest.raises(ValueError, match="unknown active"):
        _projection(
            cell,
            active_record_ids=("missing",),
        )
    with pytest.raises(ValueError, match="unknown mechanic"):
        _projection(cell, records=(_answer(mechanic_id="missing"),))
    with pytest.raises(ValueError, match="missing supersession parent"):
        _projection(
            cell,
            records=(_answer(record_id="record:2", supersedes="missing"),),
        )
    with pytest.raises(ValueError, match="branch"):
        _projection(
            cell,
            records=(
                _answer(record_id="record:0"),
                _answer(record_id="record:1", value="left", supersedes="record:0"),
                _answer(record_id="record:2", value="right", supersedes="record:0"),
            ),
            active_record_ids=("record:1", "record:2"),
        )


def test_projection_rejects_cycles_cross_coordinate_edges_and_wrong_tips() -> None:
    cell = _full_cell()
    cycle_left = _answer(record_id="left", supersedes="right")
    cycle_right = _answer(record_id="right", value="right", supersedes="left")
    with pytest.raises(ValueError, match="cycle"):
        _projection(
            cell,
            records=(cycle_left, cycle_right),
            active_record_ids=(),
        )

    root = _answer(record_id="root")
    cross_coordinate = replace(
        _answer(record_id="cross", value="cross", supersedes="root"),
        dimension=MechanicDimension.STORAGE,
        payload=(("storage_contracts", ("cross",)),),
    )
    with pytest.raises(ValueError, match="coordinate"):
        _projection(
            cell,
            records=(root, cross_coordinate),
            active_record_ids=("cross",),
        )

    tip = _answer(record_id="tip", value="tip", supersedes="root")
    with pytest.raises(ValueError, match="tips"):
        _projection(
            cell,
            records=(root, tip),
            active_record_ids=("root",),
        )

    second_coordinate = replace(
        _answer(record_id="storage", value="storage"),
        dimension=MechanicDimension.STORAGE,
        payload=(("storage_contracts", ("storage",)),),
    )
    with pytest.raises(ValueError, match="tips"):
        _projection(
            cell,
            records=(root, second_coordinate),
            active_record_ids=("root",),
        )


def test_reopened_coordinate_retains_history_but_has_no_active_tip() -> None:
    cell = _full_cell()
    record = _answer()
    coordinate = (
        cell.mechanic_id,
        MechanicDimension.ENGINEERING.value,
        "dependency revoked",
    )
    reopened = _projection(
        cell,
        records=(record,),
        active_record_ids=(),
        reopened_coordinates=(coordinate,),
    )

    assert reopened.records == (record,)
    assert reopened.active_records == ()
    assert reopened.active_record_tips == ()
    assert reopened.seed_hash == (
        "0b4a59116196985340ba0bbfa2c1ce4b0dd35200969bd712a73189484b6e3e5a"
    )
    assert projection_hash(reopened) == (
        "641e2b6fa430fe048749d0e153025377b15ac5a51ee5fe75ac94280275a642d6"
    )
    with pytest.raises(ValueError, match="reopened"):
        _projection(
            cell,
            records=(record,),
            active_record_ids=(record.record_id,),
            reopened_coordinates=(coordinate,),
        )


def test_projection_and_expectation_are_immutable() -> None:
    projection = _projection(_full_cell())
    expectation = LedgerExpectation(
        ledger_head=None,
        research_state_hash=projection_hash(projection),
        authority_revision="c" * 64,
        support_revision="d" * 64,
    )

    with pytest.raises(FrozenInstanceError):
        projection.seed_cells = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        expectation.authority_revision = "e" * 64  # type: ignore[misc]


@pytest.mark.parametrize("invalid_digest", (7, b"a" * 64))
def test_ledger_expectation_rejects_non_string_digests_with_value_error(
    invalid_digest: object,
) -> None:
    with pytest.raises(ValueError, match="research_state_hash"):
        LedgerExpectation(
            ledger_head=None,
            research_state_hash=invalid_digest,  # type: ignore[arg-type]
            authority_revision="c" * 64,
            support_revision="d" * 64,
        )


def test_ledger_expectation_rejects_string_subclass_digests() -> None:
    class DigestSubclass(str):
        pass

    with pytest.raises(ValueError, match="research_state_hash"):
        LedgerExpectation(
            ledger_head=None,
            research_state_hash=DigestSubclass("b" * 64),
            authority_revision="c" * 64,
            support_revision="d" * 64,
        )


def test_projection_rejects_mutable_container_aliases_recursively() -> None:
    cell = _full_cell()
    record = _answer()
    base = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "workflow_version": WORKFLOW_VERSION,
        "reducer_version": REDUCER_VERSION,
        "seed_cells": (cell,),
        "records": (record,),
        "active_record_ids": (record.record_id,),
    }

    with pytest.raises(ValueError, match="seed_cells.*tuple"):
        ProgramProjection(**{**base, "seed_cells": [cell]})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="records.*tuple"):
        ProgramProjection(**{**base, "records": [record]})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="active_record_ids.*tuple"):
        ProgramProjection(
            **{**base, "active_record_ids": [record.record_id]}  # type: ignore[arg-type]
        )
    mutable_cell = replace(cell, input_ids=["mutable"])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="input_ids.*tuple"):
        ProgramProjection(**{**base, "seed_cells": (mutable_cell,)})
    mutable_record = replace(
        record, evidence_refs=["evidence:1"]  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match="evidence_refs.*tuple"):
        ProgramProjection(**{**base, "records": (mutable_record,)})


def test_transition_kinds_are_explicit_and_non_authoritative() -> None:
    assert {item.value for item in TransitionKind} == {
        "ANSWER",
        "REVALIDATE",
        "REOPEN",
        "AUTHORITY_SUPPORT_UPDATE",
    }
