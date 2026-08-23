"""Point the comparator-response instrument at P9's shipped D1 transfer archive.

The numbers audited here are the ones the manuscript quotes. They are read from
``research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json``
and the committed ``result_digest`` is rebuilt from the committed bytes before
any claim is transcribed, for the reason ``orion.study.p7.closure_premises`` and
``orion.study.p8.authority_terminals`` do the same: an instrument that only ever
runs on its own fixture is the failure it was written to catch.

The view-collapse measurement below needs no fitted model and no scikit-learn. A
``DictVectorizer`` learns its vocabulary on train and drops every key it did not
see, so the number of *distinct in-vocabulary feature signatures* a split
presents is an upper bound on how many different answers any estimator in the
grid can give --- computable from the frozen dataset alone, before a single fit.

That upper bound is one for ``TRANSCRIPT_BAG``, and the survival count alone
does not say why, so it is reported with the controls that decide. ``512 of 515
protected keys are missing`` is consistent with three different worlds, and each
has a different repair --- or none.

*The vocabulary was fitted on the wrong corpus.* :func:`d1_view_collapse_report`
refits it on a same-size corpus the same generator draws from the protected
split's *own* domain and counts what comes back: zero for ``TRANSCRIPT_BAG``,
nineteen for ``TYPED_SERIALIZED_BAG``, whose value alphabet really is
domain-scoped.

*The key space is minted per instance.* It is: ``_surface_tokens`` seeds every
action symbol on the instance that emitted it, so 1,152 of the 1,155 fitted keys
occur in exactly one training row. That was reported as the cause, and it is not
the cause. ``D1_PROTOCOL_V1.json`` declares ``surface_remint`` without saying at
what *scope* a reminted name is reused, so the corpus is rebuilt under the other
reading --- one alphabet per split, keyed by the mechanic --- and measured. Every
per-instance key disappears (1,152 of 1,155 becomes 0 of 11) and the protected
denominator does not move. See :attr:`ViewCollapse.repaired_by_remint_scope`.

*The remint does not carry across the holdout.* This one is the protocol, not the
implementation: reminting surface names across splits is what the view is for,
and it is why no minting scope gives this arm a second row. The reason reported
is therefore ``SURFACE_REMINTED_ACROSS_SPLITS``, which says a reader should stop
looking for a better minting scheme.

The three keys that do survive are arity counts and take ``(2, 2, True)`` on all
128 protected cases, so the denominator is one for a fourth and independent
reason as well.

The margins above are read off the archive rather than re-run, which raises the
question of whether the archive comes back. :func:`d1_reproduction_report` calls
the same entry point the official execution called and compares every arm. Three
of the four return their selected configuration and their protected accuracy
exactly. ``TYPED_SERIALIZED_BAG`` does not: same dataset digest, same selected
``logistic-C1``, protected accuracy 0.75 against the archived 0.5 --- and where
the archived arm emitted one label on all 128 protected cases, the re-run emits
two. So ``COMPARATOR_CONSTANT`` on the published margin against that arm is a
fact about the archived run rather than about the representation. The recorded
execution environment is not this one, so the verdict is ``CANNOT_CHECK`` with
the departures named; under the recorded environment the same divergence would
be a ``FAIL``.

Everything above is measured on a *regenerated* dataset, which raises the
question of which dataset. Protocol v1.2's dependency-mutation correction is
installed by importing :mod:`orion.study.p9.d1_data_runtime`, which rebinds
``d1._mutated_value`` at module scope --- so ``generate_d1_dataset`` returns the
v1.1 corpus or the v1.2 corpus according to what else the process happened to
import. Run on its own, this audit regenerated the **v1.1** dataset
(``sha256:ff4a3d38...``) and reported on it, while the result under audit was
produced on the v1.2 dataset (``sha256:27752984...``). The numbers agree on both,
which is why nothing caught it. :func:`frozen_d1_dataset` now imports the adapter
explicitly and refuses to return a dataset whose digest is not the shipped one,
and :func:`d1_dataset_provenance` reports what was measured rather than leaving a
silent pass to be trusted.

:func:`d1_oracle_identity` asks the other question a zero cannot answer on its
own. ``0 divergent`` between the exact typed relational comparator and evaluator
gold has three causes --- the comparator is gold, it reads gold, or it is asked
where nothing could differ --- and only the third is repaired by widening the
space. So the space is widened: the comparator is re-run on 1,280 method pairs
the D1 generator never builds, and the branch is exercised against a register of
comparators a reader can read and agree are wrong. Both answers come back at
once: the branch rejects all six wrong comparators, and it still cannot fire,
because the rule it grades is :func:`orion.study.p9.d1.classify_methods`
re-expressed through the typed projection. That is an identity, and it is
reported as one.

An identity reported is still a claim withdrawn, and it leaves the branch's
actual question --- *is evaluator gold on the 128 protected cases what D1's
specification says it is?* --- unasked rather than answered. It is asked here.
``D1_PROTOCOL_V1.json`` declares the comparison coordinates and the label set,
``D1_PROTOCOL_V1_1.json`` declares what equality means coordinate by coordinate,
and the ``P9.D1Typed.v1`` payload is the surface the arm consumes; that is a
specification, so :func:`protocol_declared_comparator` implements it a second
time. It reads the declaration off the frozen protocol files at run time,
digest-bound in both directions, and never calls ``classify_methods``, never
reads ``instance.label``, and never imports the evaluator's coordinate tuple.

It is independent in the only sense that counts: it *does* disagree.
:func:`d1_independent_oracle` measures 384 of the 1,280 widened pairs on which
it and the shipped comparator answer differently, so the agreement it reports
elsewhere is a measurement rather than a restatement. And it agrees on all 512
frozen cases and all 128 protected ones, which is what the branch was supposed
to establish and never could: ``D1_EVALUATOR_FAILURE`` is reachable for a
conforming comparator and does not fire on the artifact as shipped.

The 384 are reported, not repaired. Every one of them is a pair in which a
comparison coordinate the declaration admits only as *an exact semantic value or
an explicit UNKNOWN* carries neither --- no value, and no unknown marking.
``classify_methods`` compares the absent value like any other and answers
OBSTRUCTION, so D1's evaluator will report a *decided* structural obstruction
against a coordinate no source ever stated, which is the thing
``unknown_holdout.force_unknown_not_fabricated`` exists to forbid. D1 never
built that shape --- ``unresolved_method`` nulls ``reconstruction_map`` and marks
it unknown in the same step --- so no published number moves. Adopting the
evaluator's reading here would close the gap and make this an identity again,
which is why the divergence is carried in the verdict instead.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from orion.programme.comparator_response import (
    ComparatorResponse,
    CompositionSensitivity,
    ContrastMargin,
    measure_composition_sensitivity,
    measure_contrast_margin,
    score_comparator,
)
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    FalseTheory,
    MechanizedCheck,
    RefutationCapacity,
    TheoryDivergence,
    divergence_of,
    measure_refutation_capacity,
)
from orion.transfer.v2.canonical import content_digest

_REPO_ROOT = Path(__file__).resolve().parents[4]

D1_RESULT_PATH = (
    _REPO_ROOT
    / "research"
    / "extensions"
    / "p9-structured-neural"
    / "execution"
    / "D1_EXECUTION_RESULT_V1_2.json"
)

D1_RESULT_DIGEST = "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a"

_P9_EXTENSION = _REPO_ROOT / "research" / "extensions" / "p9-structured-neural"

#: The declared protocol surface an independent comparator is written against.
#:
#: ``D1_PROTOCOL_V1.json`` declares the comparison coordinates and the label set;
#: ``D1_PROTOCOL_V1_1.json`` declares what equality *means* per coordinate;
#: ``D1_PROTOCOL_V1_2.json`` corrects the dependency-mutation generator and
#: declares the comparison rule unchanged. Together they are the specification,
#: and they are read at runtime rather than paraphrased into code so that
#: "written against the declaration" is checkable instead of asserted.
D1_PROTOCOL_PATHS: Mapping[str, Path] = {
    "P9.D1MethodTransferProtocol.v1": _P9_EXTENSION / "D1_PROTOCOL_V1.json",
    "P9.D1MethodTransferProtocol.v1.1": _P9_EXTENSION / "D1_PROTOCOL_V1_1.json",
    "P9.D1MethodTransferProtocol.v1.2": _P9_EXTENSION / "D1_PROTOCOL_V1_2.json",
}

#: Content digests of the declaration, so a comparator written against it fails
#: closed rather than silently implementing some other text.
D1_PROTOCOL_DIGESTS: Mapping[str, str] = {
    "P9.D1MethodTransferProtocol.v1": (
        "sha256:f34a682ed4cf86f5ab832cf47d746ce2b7aa14e791d5798a63a20ebceef2f98a"
    ),
    "P9.D1MethodTransferProtocol.v1.1": (
        "sha256:635568d6c070821b5bebd6bd9e9cd584e26f09d3c237e4e1fa3320a72aaec74d"
    ),
    "P9.D1MethodTransferProtocol.v1.2": (
        "sha256:3f5b48780a81f3d4c21ba6d184ff89b2dfca989c3b200380c3ee00fc51c84405"
    ),
}

D1_TREATED_ARM = "TYPED_RELATIONAL"

# The three arms the manuscript reports differences against, in the order its
# results paragraph names them.
D1_COMPARATOR_ARMS = ("TRANSCRIPT_BAG", "UNTYPED_PAIR", "TYPED_SERIALIZED_BAG")

_ARM_RESPONSE_DEFINITION: Mapping[str, str] = {
    "TRANSCRIPT_BAG": (
        "surface action tokens reminted per instance --- no token occurs in two instances "
        "anywhere in the corpus --- plus three arity counts, fitted on the numerical and "
        "graph domains and scored on transactional workflows"
    ),
    "UNTYPED_PAIR": (
        "per-coordinate presence, unknown flag and length for both methods plus a dependency "
        "topology match, fitted on two domains and scored on a third"
    ),
    "TYPED_SERIALIZED_BAG": (
        "a canonical token sequence over the same typed coordinate values, fitted on two "
        "domains and scored on a third"
    ),
    "TYPED_RELATIONAL": (
        "per-coordinate equality and unknown flags over the typed method coordinates, fitted "
        "on two domains and scored on a third"
    ),
}


def load_shipped_d1_result() -> dict[str, Any]:
    """Load the archived D1 result and rebuild its published digest from its bytes."""

    data = json.loads(D1_RESULT_PATH.read_text(encoding="utf-8"))
    published = data.get("result_digest")
    if published != D1_RESULT_DIGEST:
        raise ValueError(f"unexpected D1 result digest: {published!r}")
    body = {key: value for key, value in data.items() if key != "result_digest"}
    rebuilt = content_digest(body)
    if rebuilt != D1_RESULT_DIGEST:
        raise ValueError(
            f"D1 archive does not reproduce its own digest: {rebuilt} != {D1_RESULT_DIGEST}"
        )
    return data


def _arm_rows(result: Mapping[str, Any], arm: str) -> list[Mapping[str, Any]]:
    arms = result["results"]
    if arm not in arms:
        raise KeyError(f"D1 archive carries no arm {arm!r}")
    rows = arms[arm]["test_predictions"]
    # Every arm scored the same protected cases; sorting by instance id is what
    # makes the vectors paired rather than merely equal in length.
    return sorted(rows, key=lambda row: str(row["instance_id"]))


def d1_arm_responses(result: Mapping[str, Any] | None = None) -> dict[str, ComparatorResponse]:
    """Score every archived D1 arm on what it did with the 128 protected cases."""

    data = result if result is not None else load_shipped_d1_result()
    responses: dict[str, ComparatorResponse] = {}
    for arm in (D1_TREATED_ARM, *D1_COMPARATOR_ARMS):
        rows = _arm_rows(data, arm)
        responses[arm] = score_comparator(
            arm,
            gold=[str(row["target"]) for row in rows],
            predicted=[str(row["prediction"]) for row in rows],
            response_definition=_ARM_RESPONSE_DEFINITION[arm],
        )
    return responses


def d1_contrast_margins(result: Mapping[str, Any] | None = None) -> tuple[ContrastMargin, ...]:
    """The three published D1 differences, each with its comparator's response attached."""

    data = result if result is not None else load_shipped_d1_result()
    responses = d1_arm_responses(data)
    return tuple(
        measure_contrast_margin(
            f"D1 {D1_TREATED_ARM} minus {arm}",
            treated=responses[D1_TREATED_ARM],
            comparator=responses[arm],
        )
        for arm in D1_COMPARATOR_ARMS
    )


def _protected_compositions(gold: Sequence[str]) -> tuple[tuple[int, ...], ...]:
    """Sub-multisets of the frozen protected split, declared by label mix.

    Nothing here is a new case. The D1 protocol's 1:1:1:1 mix of aligned,
    single-corruption, unresolved and double-corruption test instances is a free
    protocol choice --- no part of the transfer claim fixes it --- so these are
    the splits the same experiment could equally have been frozen against.
    """

    positions: dict[str, list[int]] = {}
    for index, label in enumerate(gold):
        positions.setdefault(label, []).append(index)
    mixes = (
        ("as-frozen", {"ALIGNED": 32, "OBSTRUCTION": 64, "UNRESOLVED": 32}),
        ("balanced", {"ALIGNED": 32, "OBSTRUCTION": 32, "UNRESOLVED": 32}),
        ("aligned-heavy", {"ALIGNED": 32, "OBSTRUCTION": 2, "UNRESOLVED": 2}),
        ("aligned-dominant", {"ALIGNED": 32, "OBSTRUCTION": 1, "UNRESOLVED": 1}),
        ("obstruction-heavy", {"ALIGNED": 2, "OBSTRUCTION": 64, "UNRESOLVED": 2}),
        ("unresolved-heavy", {"ALIGNED": 2, "OBSTRUCTION": 2, "UNRESOLVED": 32}),
    )
    built: list[tuple[int, ...]] = []
    for _name, mix in mixes:
        selection: list[int] = []
        for label, count in sorted(mix.items()):
            selection.extend(positions.get(label, ())[:count])
        built.append(tuple(selection))
    return tuple(built)


def d1_composition_sensitivity(
    result: Mapping[str, Any] | None = None,
) -> dict[str, CompositionSensitivity]:
    """Re-score the archived predictions on re-composed protected splits.

    No model is refitted, no representation is touched and no case is invented,
    so whatever moves is a property of the split.
    """

    data = result if result is not None else load_shipped_d1_result()
    treated_rows = _arm_rows(data, D1_TREATED_ARM)
    gold = [str(row["target"]) for row in treated_rows]
    treated = [str(row["prediction"]) for row in treated_rows]
    compositions = _protected_compositions(gold)
    out: dict[str, CompositionSensitivity] = {}
    for arm in D1_COMPARATOR_ARMS:
        out[arm] = measure_composition_sensitivity(
            f"D1 {D1_TREATED_ARM} minus {arm}",
            gold=gold,
            treated=treated,
            comparator=[str(row["prediction"]) for row in _arm_rows(data, arm)],
            compositions=compositions,
        )
    return out


D1_SEED = "p9-d1-method-transfer-v1"

#: Suffix for the in-domain vocabulary control's generator seed.
#:
#: A different seed from the frozen dataset's, so the control corpus is a
#: genuinely different sample of the *same* domain rather than the protected
#: cases handed back to the vectoriser under another name.
_IN_DOMAIN_CONTROL_SUFFIX = "in-domain-vocabulary-control"

#: The dataset digest the shipped D1 result names.
#:
#: ``D1_EXECUTION_RESULT_V1_2.json`` carries this as ``dataset_manifest_digest``.
#: Every number this module reports is about a *regenerated* dataset, so the
#: regenerated one has to be that one or the report describes some other corpus.
D1_SHIPPED_DATASET_MANIFEST_DIGEST = (
    "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"
)


class D1DatasetProvenanceError(RuntimeError):
    """Raised when the regenerated D1 dataset is not the one the result was run on."""


def _v12_generator_installed() -> bool:
    """Is protocol v1.2's dependency-mutation correction the one in force?

    It is applied by *importing* :mod:`orion.study.p9.d1_data_runtime`, which
    rebinds ``d1._mutated_value`` and ``d1.mutate_method`` at module scope. So
    whether ``generate_d1_dataset`` returns the v1.1 corpus or the v1.2 corpus
    depends on whether something, anywhere in the process, has imported that
    module first --- and until this check existed nothing looked. Running
    ``python -m orion.study.p9.transfer_audit`` on its own regenerated the
    **v1.1** dataset (``sha256:ff4a3d38...``) and reported view-collapse and
    oracle-divergence numbers about it, while the result under audit was
    produced on the v1.2 dataset (``sha256:27752984...``). The numbers agree on
    both corpora, which is why this went unnoticed; agreeing by luck is not the
    same as measuring the right thing.
    """

    from . import d1 as _d1

    return getattr(_d1._mutated_value, "__name__", "") == "_mutated_value_v12"


def frozen_d1_dataset() -> Any:
    """Regenerate the dataset the shipped D1 result was produced on, or refuse.

    Imports the v1.2 adapter explicitly rather than relying on some other
    module's import having installed it, then checks the digest. A caller that
    gets a dataset back has the frozen one; a caller that does not gets an
    exception rather than a plausible number about the wrong corpus.
    """

    from . import d1_data_runtime as _v12_adapter  # noqa: F401  installs v1.2
    from .d1 import generate_d1_dataset

    dataset = generate_d1_dataset(seed=D1_SEED)
    if dataset.manifest_digest != D1_SHIPPED_DATASET_MANIFEST_DIGEST:
        raise D1DatasetProvenanceError(
            "regenerated D1 dataset is not the one the shipped result names: "
            f"regenerated {dataset.manifest_digest}, shipped "
            f"{D1_SHIPPED_DATASET_MANIFEST_DIGEST}; every margin, collapse count and "
            "divergence below would be about a different corpus"
        )
    return dataset


def d1_dataset_provenance() -> dict[str, Any]:
    """What corpus this module measured, and what it would have measured alone.

    Reported rather than only guarded: a check that silently passes leaves a
    reader unable to tell that the guard was ever needed. ``unadapted_digest``
    is what ``generate_d1_dataset`` returns with no adapter installed, and it is
    reported precisely because it is *not* the shipped digest.
    """

    from .d1 import _mutated_value as _current  # noqa: F401  presence, not value

    installed = _v12_generator_installed()
    dataset = frozen_d1_dataset()
    return {
        "shipped_dataset_manifest_digest": D1_SHIPPED_DATASET_MANIFEST_DIGEST,
        "measured_dataset_manifest_digest": dataset.manifest_digest,
        "v12_generator_installed_before_this_call": installed,
        "v12_generator_installed_now": _v12_generator_installed(),
        "generator_correction_is_an_import_side_effect": True,
        "note": (
            "protocol v1.2's dependency-mutation correction is installed by importing "
            "orion.study.p9.d1_data_runtime, so which corpus generate_d1_dataset returns "
            "depends on import order. frozen_d1_dataset imports the adapter explicitly "
            "and fails closed on the digest."
        ),
    }


class ViewCollapseReason(str, Enum):
    """Why a view can or cannot tell the protected cases apart.

    The three failing members are the point: each names a *different* mechanism
    behind the same "N of M keys survive" line, and they are not interchangeable
    because only one of them is repairable by fitting on more or better data.
    """

    VIEW_RESPONDED = "VIEW_RESPONDED"
    #: Keys are missing because the fitted corpus came from other domains, and
    #: refitting on the protected split's own domain restores them.
    HOLDOUT_SCOPED_KEY_SPACE = "HOLDOUT_SCOPED_KEY_SPACE"
    #: Keys are missing because each one is minted per instance, so no corpus
    #: --- including one drawn from the protected domain --- ever contained them.
    PER_INSTANCE_KEY_SPACE = "PER_INSTANCE_KEY_SPACE"
    #: The keys that do survive take one value on every protected case.
    SURVIVING_KEYS_CONSTANT = "SURVIVING_KEYS_CONSTANT"
    #: Keys are missing because the protocol remints surface names and the remint
    #: does not carry across the holdout. Minting them per split instead of per
    #: instance removes every per-instance key and the denominator does not move,
    #: so no reminting scope makes this view a comparator on a whole-domain
    #: holdout. Strictly more informative than ``PER_INSTANCE_KEY_SPACE``, and
    #: reported instead of it when the repair control has been run and failed.
    SURFACE_REMINTED_ACROSS_SPLITS = "SURFACE_REMINTED_ACROSS_SPLITS"

    @property
    def blocks(self) -> bool:
        return self is not ViewCollapseReason.VIEW_RESPONDED


@dataclass(frozen=True)
class ViewCollapse:
    """One representation family's protected denominator, and why it is that size.

    ``distinct_protected_rows`` is the denominator: a ceiling on how many
    different answers *any* estimator in the grid can give, computable from the
    frozen dataset with no fit. One row is not a hard case, it is not a
    measurement --- the arm's protected accuracy is then the prior of whichever
    label the solver happened to emit.

    ``restored_by_in_domain_refit`` is what separates the two ways a key goes
    missing. The same generator mints a training corpus of the same size over the
    protected split's *own* domain; keys the holdout hid come back, and keys that
    are minted per instance do not. Without it, ``3 of 515 survive`` reads like a
    holdout artifact that more training data would fix.
    """

    view: str
    train_rows: int
    train_vocabulary: int
    train_keys_in_one_train_row: int
    protected_rows: int
    test_keys: int
    test_keys_in_train_vocabulary: int
    distinct_protected_rows: int
    in_domain_train_rows: int
    in_domain_train_vocabulary: int
    test_keys_in_in_domain_vocabulary: int
    distinct_protected_rows_in_domain: int
    constant_surviving_keys: int
    remint_scope_train_vocabulary: int
    remint_scope_train_keys_in_one_train_row: int
    remint_scope_test_keys: int
    remint_scope_test_keys_in_train_vocabulary: int
    remint_scope_distinct_protected_rows: int

    @property
    def missing_keys(self) -> int:
        return self.test_keys - self.test_keys_in_train_vocabulary

    @property
    def restored_by_in_domain_refit(self) -> int:
        """Missing protected keys that a same-size in-domain corpus brings back."""

        return max(
            0, self.test_keys_in_in_domain_vocabulary - self.test_keys_in_train_vocabulary
        )

    @property
    def hapax_share(self) -> float:
        """Fraction of the fitted vocabulary that occurs in exactly one training row.

        A key that never repeats cannot be a feature: it identifies its row and
        nothing else. A view whose vocabulary is almost all hapax is a
        memorisation channel, and it is empty the moment the rows change.
        """

        return (
            self.train_keys_in_one_train_row / self.train_vocabulary
            if self.train_vocabulary
            else 0.0
        )

    @property
    def recoverable_by_refitting(self) -> bool:
        """Would a vocabulary fitted on the protected domain give this view a second row?

        The question a reader actually has when they read ``3 of 515 survive``.
        It is answered by refitting rather than by argument, because "the corpus
        was wrong" and "no corpus would have helped" are the same sentence
        otherwise.
        """

        return self.distinct_protected_rows_in_domain > 1

    @property
    def surviving_keys_all_constant(self) -> bool:
        """The second, independent way a denominator reaches one.

        Even a vocabulary that lost nothing leaves a single row when everything
        it kept takes one value, so a view has to clear both this and
        :attr:`recoverable_by_refitting` before its protected accuracy is a
        measurement.
        """

        return (
            self.test_keys_in_train_vocabulary > 0
            and self.constant_surviving_keys == self.test_keys_in_train_vocabulary
        )

    @property
    def repaired_by_remint_scope(self) -> bool:
        """Does minting one alphabet per split instead of per instance help?

        ``D1_PROTOCOL_V1.json`` declares ``surface_remint`` but never says at what
        scope a reminted name is reused, so "minted per instance" is an
        implementation reading rather than a protocol requirement. This rebuilds
        the corpus under the other reading --- same action, same opaque name
        throughout a split, a different one in every other split --- and asks
        whether the denominator moves.

        For ``TRANSCRIPT_BAG`` it does not. The repair removes every per-instance
        key (1,152 of 1,155 hapax keys become 0 of 11) and the protected
        denominator stays at one, because the remint is still disjoint *across*
        splits and that is what the protocol asks for. So the per-instance minting
        is a real defect and not the operative cause, and reporting it as the
        cause invites the reader to think a better minting scheme would give this
        arm a measurement. Nothing would.
        """

        return self.remint_scope_distinct_protected_rows > 1

    @property
    def reason(self) -> ViewCollapseReason:
        if self.distinct_protected_rows > 1:
            return ViewCollapseReason.VIEW_RESPONDED
        if self.missing_keys and not self.restored_by_in_domain_refit:
            if not self.repaired_by_remint_scope:
                return ViewCollapseReason.SURFACE_REMINTED_ACROSS_SPLITS
            return ViewCollapseReason.PER_INSTANCE_KEY_SPACE
        if self.restored_by_in_domain_refit:
            return ViewCollapseReason.HOLDOUT_SCOPED_KEY_SPACE
        return ViewCollapseReason.SURVIVING_KEYS_CONSTANT

    @property
    def outcome(self) -> Outcome:
        """``CANNOT_CHECK``: one protected row is an unmeasured arm, not a bad one."""

        return Outcome.CANNOT_CHECK if self.reason.blocks else Outcome.PASS

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def mechanism(self) -> str:
        """The sentence a reader needs in order not to misread the survival count."""

        if not self.reason.blocks:
            return (
                f"{self.test_keys_in_train_vocabulary} of {self.test_keys} protected keys "
                f"survive the fitted vocabulary and present "
                f"{self.distinct_protected_rows} distinct rows, so the arm's protected "
                "answers are a function of the cases"
            )
        parts = [
            f"{self.missing_keys} of {self.test_keys} protected feature keys are absent "
            f"from the vocabulary fitted on {self.train_rows} training rows"
        ]
        if self.missing_keys:
            parts.append(
                f"refitting on {self.in_domain_train_rows} rows minted by the same "
                f"generator over the protected split's own domain restores "
                f"{self.restored_by_in_domain_refit} of them"
                + (
                    ", so the absence is the whole-domain holdout"
                    if self.restored_by_in_domain_refit
                    else ", so no corpus drawn from the protected domain would have "
                    "contained them either"
                )
            )
            parts.append(
                f"{self.train_keys_in_one_train_row} of {self.train_vocabulary} fitted "
                f"keys occur in exactly one training row"
            )
            parts.append(
                "reminting the surface alphabet once per split instead of once per "
                f"instance takes that to {self.remint_scope_train_keys_in_one_train_row} "
                f"of {self.remint_scope_train_vocabulary} and still presents "
                f"{self.remint_scope_distinct_protected_rows} distinct protected row(s)"
                + (
                    ", so the minting scope was the constraint"
                    if self.repaired_by_remint_scope
                    else ", so the per-instance minting is real and is not what holds "
                    "the denominator down: the protocol remints across splits, and no "
                    "minting scope survives that"
                )
            )
        parts.append(
            f"the {self.test_keys_in_train_vocabulary} key(s) that do survive take one "
            f"value on all {self.protected_rows} protected cases"
            if self.constant_surviving_keys == self.test_keys_in_train_vocabulary
            else f"{self.constant_surviving_keys} of the "
            f"{self.test_keys_in_train_vocabulary} surviving key(s) take one value on "
            f"all {self.protected_rows} protected cases"
        )
        return "; ".join(parts)

    def as_json(self) -> dict[str, Any]:
        return {
            "view": self.view,
            "train_rows": self.train_rows,
            "train_vocabulary": self.train_vocabulary,
            "train_keys_in_one_train_row": self.train_keys_in_one_train_row,
            "hapax_share": self.hapax_share,
            "protected_rows": self.protected_rows,
            "test_keys": self.test_keys,
            "test_keys_in_train_vocabulary": self.test_keys_in_train_vocabulary,
            "distinct_in_vocabulary_test_signatures": self.distinct_protected_rows,
            "in_domain_train_rows": self.in_domain_train_rows,
            "in_domain_train_vocabulary": self.in_domain_train_vocabulary,
            "test_keys_in_in_domain_vocabulary": self.test_keys_in_in_domain_vocabulary,
            "distinct_in_domain_test_signatures": self.distinct_protected_rows_in_domain,
            "restored_by_in_domain_refit": self.restored_by_in_domain_refit,
            "constant_surviving_keys": self.constant_surviving_keys,
            "surviving_keys_all_constant": self.surviving_keys_all_constant,
            "recoverable_by_refitting": self.recoverable_by_refitting,
            "reason": self.reason.value,
            "outcome": self.outcome.value,
            "mechanism": self.mechanism,
        }


def _vocabulary(rows: Sequence[Mapping[str, Any]]) -> set[str]:
    return set().union(*(set(row) for row in rows)) if rows else set()


def _distinct_rows(rows: Sequence[Mapping[str, Any]], vocabulary: set[str]) -> int:
    return len(
        {
            tuple(sorted((key, str(row[key])) for key in set(row) & vocabulary))
            for row in rows
        }
    )


def _keys_in_one_row(rows: Sequence[Mapping[str, Any]]) -> int:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(row.keys())
    return sum(1 for occurrences in counts.values() if occurrences == 1)


def _constant_keys(rows: Sequence[Mapping[str, Any]], keys: set[str]) -> int:
    # A key missing from a row vectorises to 0, exactly as ``DictVectorizer``
    # fills it, so absence is a value rather than a gap.
    return sum(1 for key in keys if len({row.get(key, 0) for row in rows}) == 1)


def _in_domain_vocabulary_control(dataset: Any) -> tuple[Any, ...]:
    """A training corpus the same size as the frozen one, over the protected domain.

    This is not a new case, a new representation or a new experiment: it is the
    control that decides which of two sentences the survival count supports ---
    "the vocabulary was fitted somewhere else" or "no vocabulary could have
    contained these keys".
    """

    from .d1 import D1Split, _split_instances

    domains = tuple(sorted({row.domain for row in dataset.test}, key=lambda item: item.value))
    variants_per_index = 4  # aligned, single, unresolved, double
    per_base_pair = max(1, len(dataset.train) // (variants_per_index * len(domains)))
    return _split_instances(
        seed=f"{dataset.seed}|{_IN_DOMAIN_CONTROL_SUFFIX}",
        split=D1Split.TRAIN,
        domains=domains,
        instances_per_base_pair=per_base_pair,
        include_double=True,
    )


def _remint_scope_control() -> Any:
    """The frozen corpus rebuilt with one surface alphabet per split.

    Not a new experiment: the same cases, the same labels, the same instance ids,
    with the one implementation choice the protocol left open taken the other
    way. It answers the question ``PER_INSTANCE_KEY_SPACE`` cannot answer on its
    own --- whether a better minting scheme would give the view a denominator.
    """

    from .d1 import SurfaceRemintScope, generate_d1_dataset

    frozen_d1_dataset()  # installs the v1.2 correction and checks the digest
    return generate_d1_dataset(
        seed=D1_SEED, surface_remint_scope=SurfaceRemintScope.PER_SPLIT
    )


def d1_view_collapse_report() -> dict[str, ViewCollapse]:
    """How many protected cases each view can still tell apart, and why that number.

    A feature key absent from the training split is dropped at transform time, so
    a view whose surviving keys take one value across the protected split presents
    a single row to every estimator in the grid. That arm's prediction is then a
    constant for structural reasons, before any solver, seed or library version
    is chosen.
    """

    # Local: importing d1_experiment at module scope would drag scikit-learn into
    # every caller of the archive readers above, which need none of it.
    from .d1_experiment import D1FeatureFamily, features

    dataset = frozen_d1_dataset()
    control = _in_domain_vocabulary_control(dataset)
    repaired = _remint_scope_control()
    report: dict[str, ViewCollapse] = {}
    for family in D1FeatureFamily:
        train = [features(row, family) for row in dataset.train]
        test = [features(row, family) for row in dataset.test]
        in_domain = [features(row, family) for row in control]
        repaired_train = [features(row, family) for row in repaired.train]
        repaired_test = [features(row, family) for row in repaired.test]
        repaired_vocabulary = _vocabulary(repaired_train)
        repaired_test_keys = _vocabulary(repaired_test)
        vocabulary = _vocabulary(train)
        in_domain_vocabulary = _vocabulary(in_domain)
        test_keys = _vocabulary(test)
        report[family.value] = ViewCollapse(
            view=family.value,
            train_rows=len(train),
            train_vocabulary=len(vocabulary),
            train_keys_in_one_train_row=_keys_in_one_row(train),
            protected_rows=len(test),
            test_keys=len(test_keys),
            test_keys_in_train_vocabulary=len(test_keys & vocabulary),
            distinct_protected_rows=_distinct_rows(test, vocabulary),
            in_domain_train_rows=len(in_domain),
            in_domain_train_vocabulary=len(in_domain_vocabulary),
            test_keys_in_in_domain_vocabulary=len(test_keys & in_domain_vocabulary),
            distinct_protected_rows_in_domain=_distinct_rows(test, in_domain_vocabulary),
            constant_surviving_keys=_constant_keys(test, test_keys & vocabulary),
            remint_scope_train_vocabulary=len(repaired_vocabulary),
            remint_scope_train_keys_in_one_train_row=_keys_in_one_row(repaired_train),
            remint_scope_test_keys=len(repaired_test_keys),
            remint_scope_test_keys_in_train_vocabulary=len(
                repaired_test_keys & repaired_vocabulary
            ),
            remint_scope_distinct_protected_rows=_distinct_rows(
                repaired_test, repaired_vocabulary
            ),
        )
    return report


def d1_view_collapse() -> dict[str, dict[str, Any]]:
    """The view-collapse report as plain JSON-safe rows."""

    return {view: item.as_json() for view, item in d1_view_collapse_report().items()}


#: The environment ``RESULT_EXECUTION_ENVIRONMENT_V1.md`` records for the official
#: D1 execution lane. A reproduction that disagrees under a *different* environment
#: has not shown the archive wrong; one that disagrees under this one has.
D1_RECORDED_ENVIRONMENT: Mapping[str, str] = {
    "python": "3.12.13",
    "numpy": "2.5.2",
    "scikit-learn": "1.9.0",
    "scipy": "1.18.0",
}


def d1_observed_environment() -> dict[str, str]:
    """The versions this process is actually running."""

    import platform

    import numpy
    import scipy
    import sklearn

    return {
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "scikit-learn": sklearn.__version__,
        "scipy": scipy.__version__,
    }


def d1_environment_departures() -> tuple[str, ...]:
    """Which recorded dependency versions this process does not match."""

    observed = d1_observed_environment()
    return tuple(
        f"{name}: recorded {recorded}, observed {observed.get(name, 'absent')}"
        for name, recorded in sorted(D1_RECORDED_ENVIRONMENT.items())
        if observed.get(name) != recorded
    )


class ArmReproductionReason(str, Enum):
    """What re-running the frozen protocol said about one archived arm."""

    ARM_REPRODUCED = "ARM_REPRODUCED"
    #: The re-run's model selection picked a different configuration, so the two
    #: accuracies are not comparable and the divergence is upstream of scoring.
    SELECTION_DIVERGED = "SELECTION_DIVERGED"
    #: Same configuration, same dataset digest, different protected accuracy.
    SCORE_DIVERGED = "SCORE_DIVERGED"

    @property
    def blocks(self) -> bool:
        return self is not ArmReproductionReason.ARM_REPRODUCED


@dataclass(frozen=True)
class ArmReproduction:
    """One archived arm, re-run under the frozen protocol and compared.

    The audit above measures whether each archived comparator *responded*. It
    never asked whether the archived numbers come back, and three of P9's four
    arms do while the fourth does not --- the fourth being the one whose collapse
    drives a published ``CANNOT_CHECK``. Reading a margin off an archive without
    that check is trusting a number because it is committed.

    The verdict is not "the archive is wrong". A disagreement under an
    environment that is not the recorded one is a ``CANNOT_CHECK`` with the
    departures named, because two things changed and only one was measured.
    """

    arm_id: str
    archived_config_id: str
    reproduced_config_id: str
    archived_accuracy: float
    reproduced_accuracy: float
    archived_distinct_predictions: int
    reproduced_distinct_predictions: int
    environment_departures: tuple[str, ...]

    @property
    def reason(self) -> ArmReproductionReason:
        if self.archived_config_id != self.reproduced_config_id:
            return ArmReproductionReason.SELECTION_DIVERGED
        if self.archived_accuracy != self.reproduced_accuracy:
            return ArmReproductionReason.SCORE_DIVERGED
        return ArmReproductionReason.ARM_REPRODUCED

    @property
    def blocker(self) -> str | None:
        """The named reason this arm's divergence cannot be scored, if it cannot."""

        if self.reason.blocks and self.environment_departures:
            return "environment_identity_is_not_the_recorded_one"
        return None

    @property
    def outcome(self) -> Outcome:
        if not self.reason.blocks:
            return Outcome.PASS
        # Agreement under a different environment is stronger evidence than
        # agreement under the same one; disagreement under a different one is
        # weaker, and is not licensed to convict the archive. The blocker is
        # spelled at the site so the CANNOT_CHECK inventory can read it off here
        # rather than recording an unexamined one.
        return (
            Outcome.CANNOT_CHECK
            if self.blocker == "environment_identity_is_not_the_recorded_one"
            else Outcome.FAIL
        )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def detail(self) -> str:
        if not self.reason.blocks:
            return (
                f"{self.archived_config_id} selected again and scored "
                f"{self.reproduced_accuracy} again"
            )
        if self.reason is ArmReproductionReason.SELECTION_DIVERGED:
            return (
                f"the re-run selected {self.reproduced_config_id} where the archive "
                f"selected {self.archived_config_id}"
            )
        parts = [
            f"{self.archived_config_id} was selected again on the same dataset digest "
            f"and scored {self.reproduced_accuracy} against the archived "
            f"{self.archived_accuracy}",
            f"distinct protected predictions {self.archived_distinct_predictions} "
            f"archived, {self.reproduced_distinct_predictions} reproduced",
        ]
        if self.environment_departures:
            parts.append(
                "the recorded execution environment is not this one ("
                + "; ".join(self.environment_departures)
                + "), so this does not convict the archive"
            )
        return "; ".join(parts)

    def as_json(self) -> dict[str, Any]:
        return {
            "arm_id": self.arm_id,
            "archived_config_id": self.archived_config_id,
            "reproduced_config_id": self.reproduced_config_id,
            "archived_accuracy": self.archived_accuracy,
            "reproduced_accuracy": self.reproduced_accuracy,
            "archived_distinct_predictions": self.archived_distinct_predictions,
            "reproduced_distinct_predictions": self.reproduced_distinct_predictions,
            "environment_departures": list(self.environment_departures),
            "blocker": self.blocker,
            "reason": self.reason.value,
            "outcome": self.outcome.value,
            "detail": self.detail,
        }


def d1_reproduction_report(
    result: Mapping[str, Any] | None = None,
) -> dict[str, ArmReproduction]:
    """Re-run the frozen D1 protocol and compare every arm to the archive.

    Costs about eight seconds and one scikit-learn import, which is why it is a
    function rather than module state. It regenerates nothing by hand: it calls
    the same entry point the official execution called.
    """

    from .d1_runtime import run_d1

    archived = result if result is not None else load_shipped_d1_result()
    frozen_d1_dataset()  # digest guard before anything is fitted
    fresh = run_d1(subject_sha="orion.study.p9.transfer_margins.d1_reproduction_report")
    if fresh["dataset_manifest_digest"] != archived["dataset_manifest_digest"]:
        raise D1DatasetProvenanceError(
            "the re-run built a different dataset from the archived one: "
            f"{fresh['dataset_manifest_digest']} != {archived['dataset_manifest_digest']}"
        )
    departures = d1_environment_departures()
    report: dict[str, ArmReproduction] = {}
    for arm in sorted(archived["results"]):
        old, new = archived["results"][arm], fresh["results"][arm]
        report[arm] = ArmReproduction(
            arm_id=arm,
            archived_config_id=str(old["selected"]["config_id"]),
            reproduced_config_id=str(new["selected"]["config_id"]),
            archived_accuracy=float(old["test"]["accuracy"]),
            reproduced_accuracy=float(new["test"]["accuracy"]),
            archived_distinct_predictions=len(
                {str(row["prediction"]) for row in old["test_predictions"]}
            ),
            reproduced_distinct_predictions=len(
                {str(row["prediction"]) for row in new["test_predictions"]}
            ),
            environment_departures=departures,
        )
    return report


D1_ORACLE_THEORY_ID = "D1 exact typed relational comparator vs D1 evaluator gold"

D1_EVALUATOR_GOLD_ID = "D1 evaluator gold (orion.study.p9.d1.classify_methods)"

D1_EVALUATOR_BRANCH = "D1_EVALUATOR_FAILURE"


def _d1_evaluator_gold(instance: Any) -> str:
    """The rule the D1 evaluator labels with, read off the method pair itself."""

    from .d1 import classify_methods

    return classify_methods(instance.left, instance.right).value


def d1_oracle_divergence() -> TheoryDivergence:
    """Ask whether D1's ``D1_EVALUATOR_FAILURE`` branch could ever be taken.

    ``run_d1`` emits that terminal when its "exact typed relational comparator"
    scores below 1.0. The comparator recomputes the evaluator's own gold rule
    over the same coordinates, so this is P6's question and P6's instrument
    answers it; it is measured here rather than re-implemented.
    """

    from .d1_experiment import exact_relational_comparator

    dataset = frozen_d1_dataset()
    return divergence_of(
        exact_relational_comparator,
        theory_id=D1_ORACLE_THEORY_ID,
        reference=_d1_evaluator_gold,
        space=(*dataset.train, *dataset.dev, *dataset.test),
    )


class OracleVerdict(str, Enum):
    """What a zero-divergence count between comparator and gold actually says.

    Three states, because "0 divergent" has three causes and only one of them is
    a result. ``IDENTITY_BY_CONSTRUCTION`` is the one this audit found, and
    printing it as an agreement measurement is the defect: an identity reported
    as a comparison reads as corroboration that the evaluator was checked.
    """

    COMPARATOR_DIVERGED = "COMPARATOR_DIVERGED"
    AGREEMENT_ONLY_ON_THE_FROZEN_SPACE = "AGREEMENT_ONLY_ON_THE_FROZEN_SPACE"
    IDENTITY_BY_CONSTRUCTION = "IDENTITY_BY_CONSTRUCTION"


@dataclass(frozen=True)
class OracleIdentity:
    """The ``D1_EVALUATOR_FAILURE`` branch, measured as an identity and as a check.

    Two questions, deliberately separate, because they have opposite answers here
    and reporting either one alone is misleading.

    *Is this comparator capable of disagreeing with gold?*
    ``frozen_space``/``protected_space``/``widened_space`` answer it. The last is
    the one that matters: agreement on a corpus a single generator built is weak
    evidence, so the comparator is re-run on method pairs that generator never
    makes --- every subset of the eight compared coordinates perturbed at once,
    values emptied and nulled rather than extended, and unknown markings on the
    left method, on both methods, and on a coordinate the evaluator does not
    compare at all. Zero divergence there too is an identity, not a coincidence
    of the frozen split.

    *Is the branch itself a real check?* ``capacity`` answers it with P6's
    instrument: a register of comparators a reader can read and agree are wrong,
    each of which the branch does reject. So the branch is well-formed, and it is
    still unreachable --- because the rule it was pointed at is the rule it
    grades against, re-expressed through the typed projection.
    """

    comparator_id: str
    reference_id: str
    branch: str
    frozen_space: TheoryDivergence
    protected_space: TheoryDivergence
    widened_space: TheoryDivergence
    compared_coordinates: tuple[str, ...]
    comparator_read_coordinates: tuple[str, ...]
    widened_gold_labels: tuple[tuple[str, int], ...]
    capacity: RefutationCapacity

    def __post_init__(self) -> None:
        if len(self.widened_gold_labels) < 2:
            raise ValueError(
                f"{self.comparator_id}: the widened space carries "
                f"{len(self.widened_gold_labels)} gold label(s); a space on which the "
                "reference itself is constant cannot show a comparator disagreeing"
            )

    @property
    def verdict(self) -> OracleVerdict:
        if self.protected_space.applied or self.frozen_space.applied:
            return OracleVerdict.COMPARATOR_DIVERGED
        if self.widened_space.applied:
            return OracleVerdict.AGREEMENT_ONLY_ON_THE_FROZEN_SPACE
        return OracleVerdict.IDENTITY_BY_CONSTRUCTION

    @property
    def is_identity(self) -> bool:
        return self.verdict is OracleVerdict.IDENTITY_BY_CONSTRUCTION

    @property
    def widened_space_is_varied(self) -> bool:
        """The widening is only worth reporting if gold moves across it."""

        return len(self.widened_gold_labels) > 1

    @property
    def reads_every_compared_coordinate(self) -> bool:
        """The structural half of the identity: same inputs, not just same answers."""

        return set(self.comparator_read_coordinates) == set(self.compared_coordinates)

    @property
    def branch_reachable(self) -> bool:
        """Could ``D1_EVALUATOR_FAILURE`` have been emitted by the artifact as run?"""

        return not self.is_identity

    @property
    def outcome(self) -> Outcome:
        """``CANNOT_CHECK`` for an identity: nothing could have differed.

        Not ``FAIL``. A comparator that *did* disagree with gold would refute the
        archive's ``exact_typed_relational_comparator.accuracy == 1.0``, and that
        is the only reading of this branch that deserves ``FAIL``. Both block.
        """

        if self.verdict is OracleVerdict.COMPARATOR_DIVERGED:
            return Outcome.FAIL
        return Outcome.CANNOT_CHECK

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "comparator_id": self.comparator_id,
            "reference_id": self.reference_id,
            "branch": self.branch,
            "verdict": self.verdict.value,
            "is_identity": self.is_identity,
            "branch_reachable": self.branch_reachable,
            "reads_every_compared_coordinate": self.reads_every_compared_coordinate,
            "widened_gold_labels": [list(item) for item in self.widened_gold_labels],
            "widened_space_is_varied": self.widened_space_is_varied,
            "compared_coordinates": list(self.compared_coordinates),
            "comparator_read_coordinates": list(self.comparator_read_coordinates),
            "frozen_space": self.frozen_space.as_json(),
            "protected_space": self.protected_space.as_json(),
            "widened_space": self.widened_space.as_json(),
            "capacity": self.capacity.as_json(),
            "outcome": self.outcome.value,
        }


def _widened_oracle_space() -> tuple[Any, ...]:
    """Method pairs the D1 generator never builds, for the comparator to differ on.

    The frozen corpus perturbs one or two coordinates with a single mutation
    operator that only ever *extends* a sequence or *replaces* a scalar, and it
    marks a coordinate unknown on the right method only. A comparator that agreed
    with gold there could be agreeing with the generator. These are that
    generator's blind spots, enumerated rather than sampled: all 2**8 subsets of
    the compared coordinates perturbed at once, crossed with five unknown
    regimes, including one that marks a coordinate the evaluator does not compare.
    """

    from orion.transfer.v2.p1_method_realization import build_method_realization

    from .d1 import (
        COMPARISON_COORDINATES,
        D1Domain,
        D1Instance,
        D1Split,
        classify_methods,
    )

    shared: dict[str, Any] = {
        "source_digest": content_digest({"p9-d1-widened-oracle-space": "v1"}),
        "source_version": "p9-d1-widened-oracle-space-v1",
        "authority_boundary": "REPRESENTATION_ONLY",
        "target_role": "widened_probe",
        "assumptions": ("a1",),
        "resources": ("r1",),
        "representation_in": "in",
        "representation_out": "out",
        "mechanics": ("alpha", "beta"),
        "lineage": ("donor:widened",),
    }
    reference_values: dict[str, Any] = {
        "preconditions": ("p1", "p2"),
        "invariants": ("i1",),
        "effects": ("e1",),
        "progress_measure": "pm",
        "terminal_condition": "tc",
        "reconstruction_map": "rm",
        "failure_modes": ("f1", "f2"),
        "dependencies": (("alpha", "beta"),),
    }
    # Shapes the D1 mutation operator never produces: emptied sequences, nulled
    # scalars, a dropped dependency edge, a shortened failure-mode list.
    perturbed_values: dict[str, Any] = {
        "preconditions": ("p1", "p3"),
        "invariants": (),
        "effects": ("e1", "e2"),
        "progress_measure": None,
        "terminal_condition": "tc2",
        "reconstruction_map": None,
        "failure_modes": ("f2",),
        "dependencies": (),
    }
    unknown_regimes = (
        ("none", (), ()),
        # D1 only ever marks the right method unknown.
        ("left-only", ("progress_measure",), ()),
        ("right-only", (), ("terminal_condition",)),
        ("both-sides", ("dependencies",), ("dependencies",)),
        # ``mechanics`` is a realization coordinate the evaluator does not
        # compare: gold must ignore it, and so must the typed projection.
        ("outside-the-compared-set", (), ("mechanics",)),
    )

    space: list[Any] = []
    for regime, left_unknown, right_unknown in unknown_regimes:
        left = build_method_realization(
            method_id=f"widened-left-{regime}",
            unknown_coordinates=left_unknown,
            **shared,
            **reference_values,
        )
        for mask in range(1 << len(COMPARISON_COORDINATES)):
            changed = tuple(
                coordinate
                for index, coordinate in enumerate(COMPARISON_COORDINATES)
                if mask >> index & 1
            )
            values = dict(reference_values)
            for coordinate in changed:
                values[coordinate] = perturbed_values[coordinate]
            right = build_method_realization(
                method_id=f"widened-right-{regime}-{mask}",
                unknown_coordinates=right_unknown,
                **shared,
                **values,
            )
            instance = D1Instance(
                instance_id=f"widened-{regime}-{mask}",
                domain=D1Domain.WORKFLOW,
                split=D1Split.TEST,
                left=left,
                right=right,
                label=classify_methods(left, right),
                mutation_coordinates=changed,
                surface_left=("widened-left-0", "widened-left-1"),
                surface_right=("widened-right-0", "widened-right-1"),
                surface_role_left="widened-left-role",
                surface_role_right="widened-right-role",
            )
            instance.verify()
            space.append(instance)
    return tuple(space)


def declared_false_comparators() -> tuple[FalseTheory, ...]:
    """Comparator rules a reader can read and agree are wrong.

    The register the ``D1_EVALUATOR_FAILURE`` branch is exercised against. Its
    job is to keep "the branch never fired" from being read two ways at once: a
    branch that rejects none of these is vacuous, and a branch that rejects all
    of them is a real check that happened to be pointed at its own reference.
    """

    from .d1 import COMPARISON_COORDINATES, D1Label
    from .d1_experiment import D1FeatureFamily, features

    def row(instance: Any) -> Mapping[str, Any]:
        return features(instance, D1FeatureFamily.TYPED_RELATIONAL)

    def unknown_anywhere(cells: Mapping[str, Any]) -> bool:
        return any(bool(cells[f"{name}:unknown"]) for name in COMPARISON_COORDINATES)

    def unequal_anywhere(cells: Mapping[str, Any]) -> bool:
        return any(not bool(cells[f"{name}:equal"]) for name in COMPARISON_COORDINATES)

    def always_aligned(_instance: Any) -> str:
        return D1Label.ALIGNED.value

    def modal_label(_instance: Any) -> str:
        return D1Label.OBSTRUCTION.value

    def unknown_ignored(instance: Any) -> str:
        cells = row(instance)
        return (
            D1Label.OBSTRUCTION.value if unequal_anywhere(cells) else D1Label.ALIGNED.value
        )

    def obstruction_before_unresolved(instance: Any) -> str:
        cells = row(instance)
        if unequal_anywhere(cells):
            return D1Label.OBSTRUCTION.value
        if unknown_anywhere(cells):
            return D1Label.UNRESOLVED.value
        return D1Label.ALIGNED.value

    def preconditions_only(instance: Any) -> str:
        cells = row(instance)
        if unknown_anywhere(cells):
            return D1Label.UNRESOLVED.value
        if not bool(cells["preconditions:equal"]):
            return D1Label.OBSTRUCTION.value
        return D1Label.ALIGNED.value

    def cardinality_only(instance: Any) -> str:
        cells = row(instance)
        if unknown_anywhere(cells):
            return D1Label.UNRESOLVED.value
        for name in COMPARISON_COORDINATES:
            left = cells.get(f"{name}:left_length")
            right = cells.get(f"{name}:right_length")
            if left is not None and right is not None and left != right:
                return D1Label.OBSTRUCTION.value
        return D1Label.ALIGNED.value

    return (
        FalseTheory(
            theory_id="always-aligned",
            breaks="every method pair is substitutable: obstruction and source "
            "insufficiency are never reported at all",
            rule=always_aligned,
        ),
        FalseTheory(
            theory_id="modal-label",
            breaks="the comparator answers the protected split's most common label "
            "instead of reading the pair",
            rule=modal_label,
        ),
        FalseTheory(
            theory_id="unknown-ignored",
            breaks="a coordinate the source never stated is graded as though it had "
            "been, so UNRESOLVED is never reported",
            rule=unknown_ignored,
        ),
        FalseTheory(
            theory_id="obstruction-before-unresolved",
            breaks="a pair that is both source-insufficient and unequal is reported as "
            "a decided obstruction rather than as unresolved",
            rule=obstruction_before_unresolved,
        ),
        FalseTheory(
            theory_id="preconditions-only",
            breaks="seven of the eight compared coordinates are ignored, so a "
            "corruption anywhere else reads as aligned",
            rule=preconditions_only,
        ),
        FalseTheory(
            theory_id="cardinality-only",
            breaks="coordinates are graded by how many entries they have, so a "
            "same-length rewrite and a scalar substitution read as aligned",
            rule=cardinality_only,
        ),
    )


def d1_oracle_identity() -> OracleIdentity:
    """Decide which of the three causes of ``0 divergent`` this branch has.

    A comparator can agree with gold everywhere because it *is* gold, because it
    reads gold, or because it is being asked on a space where nothing could
    differ. The three are told apart here by widening the space and by exercising
    the branch against wrong comparators, not by reading the count.
    """

    from .d1 import COMPARISON_COORDINATES
    from .d1_experiment import D1FeatureFamily, exact_relational_comparator, features

    # ``frozen_d1_dataset``, not ``generate_d1_dataset``: protocol v1.2's
    # correction is an import side effect, and a protected split drawn from the
    # v1.1 corpus would be a divergence count about a different 128 cases.
    dataset = frozen_d1_dataset()
    protected = tuple(dataset.test)
    widened = _widened_oracle_space()

    read = {
        key.split(":", 1)[0]
        for key in features(protected[0], D1FeatureFamily.TYPED_RELATIONAL)
        if key.endswith((":equal", ":unknown"))
    }

    check = MechanizedCheck(
        check_id=D1_EVALUATOR_BRANCH,
        asserts=(
            "run_d1 emits D1_EVALUATOR_FAILURE unless the exact typed relational "
            f"comparator reproduces evaluator gold on all {len(protected)} protected cases"
        ),
        accepts=lambda rule: all(rule(row) == _d1_evaluator_gold(row) for row in protected),
    )

    return OracleIdentity(
        comparator_id=D1_ORACLE_THEORY_ID,
        reference_id=D1_EVALUATOR_GOLD_ID,
        branch=D1_EVALUATOR_BRANCH,
        frozen_space=d1_oracle_divergence(),
        protected_space=divergence_of(
            exact_relational_comparator,
            theory_id=f"{D1_ORACLE_THEORY_ID} (protected split only)",
            reference=_d1_evaluator_gold,
            space=protected,
        ),
        widened_space=divergence_of(
            exact_relational_comparator,
            theory_id=f"{D1_ORACLE_THEORY_ID} (pairs the D1 generator never builds)",
            reference=_d1_evaluator_gold,
            space=widened,
        ),
        compared_coordinates=tuple(COMPARISON_COORDINATES),
        comparator_read_coordinates=tuple(sorted(read)),
        widened_gold_labels=tuple(
            sorted(Counter(_d1_evaluator_gold(row) for row in widened).items())
        ),
        capacity=measure_refutation_capacity(
            check,
            reference=_d1_evaluator_gold,
            reference_id=D1_EVALUATOR_GOLD_ID,
            theories=declared_false_comparators(),
            space=protected,
        ),
    )


# --------------------------------------------------------------------------
# A second implementation of the same specification
# --------------------------------------------------------------------------

D1_PROTOCOL_COMPARATOR_ID = (
    "D1 protocol-declared comparator (D1_PROTOCOL_V1 + V1_1 declared surface)"
)

D1_SHIPPED_COMPARATOR_ID = (
    "D1 exact typed relational comparator "
    "(orion.study.p9.d1_experiment.exact_relational_comparator)"
)


class D1ProtocolDeclarationError(RuntimeError):
    """Raised when the declared D1 surface is not the text this comparator implements."""


class DeclaredComparison(str, Enum):
    """What ``D1_PROTOCOL_V1_1.json`` says comparing one coordinate *means*.

    One member per distinct ``coordinate_semantics`` sentence in the protocol.
    The mapping from sentence to member is spelled out in
    :data:`_DECLARED_COMPARISON` and is looked up rather than inferred, so a
    protocol whose declared semantics changed would raise instead of quietly
    being graded by the old reading.
    """

    SORTED_SEMANTIC_VALUES = "SORTED_SEMANTIC_VALUES"
    SEMANTIC_VALUE_OR_EXPLICIT_UNKNOWN = "SEMANTIC_VALUE_OR_EXPLICIT_UNKNOWN"
    DEPENDENCY_TOPOLOGY_OVER_ROLE_INDICES = "DEPENDENCY_TOPOLOGY_OVER_ROLE_INDICES"


_DECLARED_COMPARISON: Mapping[str, DeclaredComparison] = {
    "exact sorted semantic values": DeclaredComparison.SORTED_SEMANTIC_VALUES,
    "exact semantic value or explicit UNKNOWN": (
        DeclaredComparison.SEMANTIC_VALUE_OR_EXPLICIT_UNKNOWN
    ),
    "directed dependency graph over method-local mechanic role indices after "
    "deterministic local mechanic ordering; surface mechanic/action names are not "
    "compared as semantic identity": (
        DeclaredComparison.DEPENDENCY_TOPOLOGY_OVER_ROLE_INDICES
    ),
}


@dataclass(frozen=True)
class D1ProtocolDeclaration:
    """The D1 comparison specification, as the frozen protocol files declare it.

    Everything the comparator below needs comes from here, and everything here
    comes from the protocol JSON: the coordinate list, the label set, the
    per-coordinate meaning of equality, and the rule that an unstated coordinate
    is marked rather than fabricated. Nothing is read from
    :mod:`orion.study.p9.d1`, which is the point --- a comparator that imported
    the evaluator's coordinate tuple would already share half its definition.
    """

    comparison_coordinates: tuple[str, ...]
    labels: tuple[str, ...]
    coordinate_comparison: Mapping[str, DeclaredComparison]
    unknown_holdout_coordinate: str
    unknown_must_be_marked_not_fabricated: bool
    typed_payload_schema: str
    digests: Mapping[str, str]

    def kind(self, coordinate: str) -> DeclaredComparison:
        return self.coordinate_comparison[coordinate]

    @property
    def scalar_coordinates(self) -> tuple[str, ...]:
        """The coordinates the protocol says may carry an *explicit UNKNOWN*.

        Exactly the three the declaration gives two admissible states: an exact
        semantic value, or an explicit UNKNOWN. A payload that presents neither
        is outside the declared surface, and what the evaluator does with it is
        the divergence :class:`OracleIndependence` measures.
        """

        return tuple(
            coordinate
            for coordinate in self.comparison_coordinates
            if self.kind(coordinate)
            is DeclaredComparison.SEMANTIC_VALUE_OR_EXPLICIT_UNKNOWN
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "comparison_coordinates": list(self.comparison_coordinates),
            "labels": list(self.labels),
            "coordinate_comparison": {
                coordinate: kind.value
                for coordinate, kind in sorted(self.coordinate_comparison.items())
            },
            "scalar_coordinates": list(self.scalar_coordinates),
            "unknown_holdout_coordinate": self.unknown_holdout_coordinate,
            "unknown_must_be_marked_not_fabricated": (
                self.unknown_must_be_marked_not_fabricated
            ),
            "typed_payload_schema": self.typed_payload_schema,
            "digests": dict(sorted(self.digests.items())),
        }


def d1_protocol_declaration() -> D1ProtocolDeclaration:
    """Read D1's declared comparison surface off the frozen protocol files.

    Digest-bound in both directions. Each protocol file must reproduce the
    digest pinned in :data:`D1_PROTOCOL_DIGESTS`, and every declared
    ``coordinate_semantics`` sentence must be one :data:`_DECLARED_COMPARISON`
    implements. A declaration that moved, or a coordinate whose declared meaning
    this module never implemented, raises rather than being graded by whatever
    reading happens to be coded here.
    """

    documents: dict[str, Mapping[str, Any]] = {}
    for schema, path in D1_PROTOCOL_PATHS.items():
        document = json.loads(path.read_text(encoding="utf-8"))
        digest = content_digest(document)
        if digest != D1_PROTOCOL_DIGESTS[schema]:
            raise D1ProtocolDeclarationError(
                f"{path.name} is not the declaration this comparator implements: "
                f"{digest} != {D1_PROTOCOL_DIGESTS[schema]}"
            )
        if document["schema"] != schema:
            raise D1ProtocolDeclarationError(
                f"{path.name} declares schema {document['schema']!r}, expected {schema!r}"
            )
        documents[schema] = document

    v1 = documents["P9.D1MethodTransferProtocol.v1"]
    v11 = documents["P9.D1MethodTransferProtocol.v1.1"]
    v12 = documents["P9.D1MethodTransferProtocol.v1.2"]

    # v1.2 corrects the generator, not the comparison. If it ever stopped saying
    # so, the coordinate semantics below would be the wrong version's.
    if "protected test rule" not in set(v12["unchanged"]):
        raise D1ProtocolDeclarationError(
            "D1_PROTOCOL_V1_2 no longer declares the protected test rule unchanged"
        )

    semantics = v11["coordinate_semantics"]
    coordinates = tuple(str(name) for name in v1["comparison_coordinates"])
    comparison: dict[str, DeclaredComparison] = {}
    for coordinate in coordinates:
        if coordinate not in semantics:
            raise D1ProtocolDeclarationError(
                f"D1_PROTOCOL_V1_1 declares no comparison semantics for {coordinate!r}"
            )
        declared = str(semantics[coordinate])
        if declared not in _DECLARED_COMPARISON:
            raise D1ProtocolDeclarationError(
                f"{coordinate!r} declares a comparison this module does not implement: "
                f"{declared!r}"
            )
        comparison[coordinate] = _DECLARED_COMPARISON[declared]

    unknown_holdout = v1["unknown_holdout"]
    return D1ProtocolDeclaration(
        comparison_coordinates=coordinates,
        labels=tuple(str(label) for label in v1["labels"]),
        coordinate_comparison=comparison,
        unknown_holdout_coordinate=str(unknown_holdout["coordinate"]),
        unknown_must_be_marked_not_fabricated=bool(
            unknown_holdout["force_unknown_not_fabricated"]
        ),
        typed_payload_schema="P9.D1Typed.v1",
        digests=dict(D1_PROTOCOL_DIGESTS),
    )


def _declared_unstated(
    side: Mapping[str, Any], coordinate: str, kind: DeclaredComparison
) -> bool:
    """Does this side of the pair state a value for this coordinate at all?

    Two ways not to. The coordinate is listed in the payload's
    ``unknown_coordinates`` --- the declaration's *explicit UNKNOWN* --- or the
    declaration allows only "exact semantic value or explicit UNKNOWN" for this
    coordinate and the payload carries neither. D1's own untyped payload draws
    exactly this line: ``present`` is ``value is not None`` for a scalar and
    unconditionally true for a sequence, so an empty sequence is a stated value
    and an absent scalar is not.
    """

    if coordinate in set(side["unknown_coordinates"]):
        return True
    if kind is DeclaredComparison.SEMANTIC_VALUE_OR_EXPLICIT_UNKNOWN:
        return side[coordinate] is None
    return False


def _declared_value(
    side: Mapping[str, Any], coordinate: str, kind: DeclaredComparison
) -> Any:
    """The coordinate reduced to what the declaration says is compared."""

    value = side[coordinate]
    if kind is DeclaredComparison.SORTED_SEMANTIC_VALUES:
        return tuple(sorted(map(str, value)))
    if kind is DeclaredComparison.DEPENDENCY_TOPOLOGY_OVER_ROLE_INDICES:
        return tuple(sorted(tuple(int(node) for node in edge) for edge in value))
    return value


def protocol_declared_comparator(instance: Any) -> str:
    """Decide a D1 pair from the declared surface, without consulting the evaluator.

    A second implementation of D1's specification rather than a second expression
    of its implementation. It reads :attr:`orion.study.p9.d1.D1View.TYPED` --- the
    payload schema the protocol declares and the arm actually consumes --- loops
    over the coordinates ``D1_PROTOCOL_V1.json`` declares, compares each one the
    way ``D1_PROTOCOL_V1_1.json`` declares it is compared, and answers with a
    label from the declared label set. It never calls
    :func:`orion.study.p9.d1.classify_methods`, never reads ``instance.label``,
    and never imports the evaluator's coordinate tuple.

    Where the declaration underdetermines the mapping, it is resolved from the
    declaration and not from the evaluator, which is the whole point:

    *Precedence.* ``unknown_holdout.force_unknown_not_fabricated`` says a
    coordinate the source never stated is marked, not invented. A pair carrying
    one cannot be *decided*, so UNRESOLVED is answered before OBSTRUCTION.

    *What counts as unstated.* The declared states of a scalar coordinate are
    "exact semantic value" and "explicit UNKNOWN". A payload presenting neither
    --- no value, no unknown marking --- states nothing about that coordinate, so
    there is nothing to compare and the pair is unresolved. The evaluator instead
    compares the absent value like any other, and reports a *decided* obstruction
    against a coordinate no source ever stated. That is the one place the two
    implementations part, and :func:`d1_independent_oracle` measures it rather
    than tuning it away.

    ``model_payload`` verifies the instance before projecting it, which is an
    admissibility check on the input; the comparator reads only the projection.
    """

    from .d1 import D1View

    declaration = d1_protocol_declaration()
    payload = instance.model_payload(D1View.TYPED)
    if payload["schema"] != declaration.typed_payload_schema:
        raise D1ProtocolDeclarationError(
            f"typed payload declares schema {payload['schema']!r}, expected "
            f"{declaration.typed_payload_schema!r}"
        )
    left = payload["left"]
    right = payload["right"]

    for coordinate in declaration.comparison_coordinates:
        kind = declaration.kind(coordinate)
        if _declared_unstated(left, coordinate, kind) or _declared_unstated(
            right, coordinate, kind
        ):
            return "UNRESOLVED"
    for coordinate in declaration.comparison_coordinates:
        kind = declaration.kind(coordinate)
        if _declared_value(left, coordinate, kind) != _declared_value(
            right, coordinate, kind
        ):
            return "OBSTRUCTION"
    return "ALIGNED"


class IndependenceVerdict(str, Enum):
    """What a second comparator bought, in the only three states it can be in."""

    NOT_INDEPENDENT = "NOT_INDEPENDENT"
    DIVERGED_ON_THE_SHIPPED_CORPUS = "DIVERGED_ON_THE_SHIPPED_CORPUS"
    INDEPENDENT_AND_AGREED = "INDEPENDENT_AND_AGREED"


@dataclass(frozen=True)
class OracleIndependence:
    """``D1_EVALUATOR_FAILURE``'s claim, checked by a comparator that could deny it.

    :class:`OracleIdentity` establishes that the comparator the *artifact* ran
    cannot make the branch fire. That does not settle whether the branch's claim
    --- evaluator gold on the 128 protected cases is what D1's specification says
    it is --- is true, only that D1 never checked it. This does.

    Three quantities, and the reader needs all three.

    ``against_shipped_comparator`` is the independence evidence: the number of
    admissible pairs on which the protocol-declared comparator answers something
    the shipped one does not. Zero there and this is a second identity, which is
    the thing being replaced, so it is a ``NOT_INDEPENDENT`` verdict rather than
    a pass.

    ``frozen_space`` and ``protected_space`` are the measurement: given that the
    comparator *can* disagree, what it does on the corpus the archive was
    produced on is a fact about D1's gold rather than about its own definition.

    ``widened_space`` is where the two implementations actually part, reported
    with the shape that causes it. Reported and not repaired: the declaration
    underdetermines that shape, and closing the gap by adopting the evaluator's
    reading would make this an identity again.
    """

    comparator_id: str
    reference_id: str
    shipped_comparator_id: str
    branch: str
    declaration: D1ProtocolDeclaration
    frozen_space: TheoryDivergence
    protected_space: TheoryDivergence
    widened_space: TheoryDivergence
    against_shipped_comparator: TheoryDivergence
    divergent_label_pairs: tuple[tuple[tuple[str, str], int], ...]
    divergence_shape: str
    witness: Mapping[str, Any]
    capacity: RefutationCapacity

    def __post_init__(self) -> None:
        counted = sum(count for _, count in self.divergent_label_pairs)
        if counted != self.widened_space.points_changed:
            raise ValueError(
                f"{self.comparator_id}: {counted} labelled divergences against "
                f"{self.widened_space.points_changed} counted; the breakdown is not "
                "the measurement"
            )

    @property
    def is_independent(self) -> bool:
        """Can this comparator answer differently from the one the artifact ran?"""

        return self.against_shipped_comparator.applied

    @property
    def branch_reachable(self) -> bool:
        """Is ``D1_EVALUATOR_FAILURE``'s condition satisfiable by a conforming rule?"""

        return self.is_independent

    @property
    def branch_fires(self) -> bool:
        """Does it fire on the corpus the shipped artifact was scored on?"""

        return self.protected_space.applied

    @property
    def verdict(self) -> IndependenceVerdict:
        if not self.is_independent:
            return IndependenceVerdict.NOT_INDEPENDENT
        if self.frozen_space.applied or self.protected_space.applied:
            return IndependenceVerdict.DIVERGED_ON_THE_SHIPPED_CORPUS
        return IndependenceVerdict.INDEPENDENT_AND_AGREED

    @property
    def outcome(self) -> Outcome:
        """``PASS`` only when a comparator that could have denied the claim did not.

        ``FAIL`` when the second implementation contradicts gold on the corpus
        the archive was scored on: that would put the archive's
        ``exact_typed_relational_comparator.accuracy == 1.0`` in dispute.
        ``CANNOT_CHECK`` when the second comparator turns out to be the first
        under another name, because then nothing was measured.
        """

        if self.verdict is IndependenceVerdict.DIVERGED_ON_THE_SHIPPED_CORPUS:
            return Outcome.FAIL
        # Compared against the spelled blocker rather than the verdict, and in
        # the returning statement rather than above it, so the CANNOT_CHECK
        # inventory reads an examined site here instead of one carrying no
        # extractable reason.
        return (
            Outcome.CANNOT_CHECK
            if self.blocker == "insufficient_evidence_the_comparator_could_not_disagree"
            else Outcome.PASS
        )

    @property
    def blocker(self) -> str | None:
        """Why this independence check produced nothing, when it produced nothing.

        A comparator that turns out to be the first one under another name did
        not measure anything: there was no verdict it could have returned other
        than the one it did.
        """

        if self.verdict is IndependenceVerdict.NOT_INDEPENDENT:
            return "insufficient_evidence_the_comparator_could_not_disagree"
        return None

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "comparator_id": self.comparator_id,
            "reference_id": self.reference_id,
            "shipped_comparator_id": self.shipped_comparator_id,
            "branch": self.branch,
            "verdict": self.verdict.value,
            "is_independent": self.is_independent,
            "branch_reachable": self.branch_reachable,
            "branch_fires": self.branch_fires,
            "declaration": self.declaration.as_json(),
            "frozen_space": self.frozen_space.as_json(),
            "protected_space": self.protected_space.as_json(),
            "widened_space": self.widened_space.as_json(),
            "against_shipped_comparator": self.against_shipped_comparator.as_json(),
            "divergent_label_pairs": [
                {"evaluator": pair[0], "protocol_declared": pair[1], "points": count}
                for pair, count in self.divergent_label_pairs
            ],
            "divergence_shape": self.divergence_shape,
            "witness": dict(self.witness),
            "capacity": self.capacity.as_json(),
            "outcome": self.outcome.value,
        }


def _divergence_witness(space: Sequence[Any], declaration: D1ProtocolDeclaration) -> dict[str, Any]:
    """One named pair a reader can check by hand, not just a count.

    A count of 384 is a claim about a mechanism nobody can see. This returns the
    *simplest* pair the two implementations part on --- fewest perturbed
    coordinates, then instance id --- so the witness is a pair that differs in
    one coordinate only, and that coordinate is the one carrying no value.
    """

    from .d1 import D1View

    def simplicity(row: Any) -> tuple[int, str]:
        return (len(row.mutation_coordinates), str(row.instance_id))

    for instance in sorted(space, key=simplicity):
        declared = protocol_declared_comparator(instance)
        gold = _d1_evaluator_gold(instance)
        if declared == gold:
            continue
        payload = instance.model_payload(D1View.TYPED)
        unstated = [
            {
                "coordinate": coordinate,
                "side": side_name,
                "value": payload[side_name][coordinate],
                "marked_unknown": coordinate
                in set(payload[side_name]["unknown_coordinates"]),
            }
            for coordinate in declaration.scalar_coordinates
            for side_name in ("left", "right")
            if payload[side_name][coordinate] is None
        ]
        return {
            "instance_id": instance.instance_id,
            "perturbed_coordinates": list(instance.mutation_coordinates),
            "evaluator_gold": gold,
            "protocol_declared": declared,
            "coordinates_carrying_no_value": unstated,
        }
    return {}


def d1_independent_oracle() -> OracleIndependence:
    """Check ``D1_EVALUATOR_FAILURE``'s claim with a comparator that can deny it.

    Same three spaces :func:`d1_oracle_identity` uses, so the two verdicts are
    read side by side and the difference between them is the difference between
    "the artifact never checked this" and "this is what the check would have
    said".
    """

    from .d1_experiment import exact_relational_comparator

    declaration = d1_protocol_declaration()
    dataset = frozen_d1_dataset()
    protected = tuple(dataset.test)
    frozen = (*dataset.train, *dataset.dev, *dataset.test)
    widened = _widened_oracle_space()

    parted: Counter[tuple[str, str]] = Counter()
    for instance in widened:
        declared = protocol_declared_comparator(instance)
        gold = _d1_evaluator_gold(instance)
        if declared != gold:
            parted[(gold, declared)] += 1

    check = MechanizedCheck(
        check_id=D1_EVALUATOR_BRANCH,
        asserts=(
            "run_d1 emits D1_EVALUATOR_FAILURE unless the comparator reproduces "
            f"evaluator gold on all {len(protected)} protected cases"
        ),
        accepts=lambda rule: all(rule(row) == _d1_evaluator_gold(row) for row in protected),
    )

    return OracleIndependence(
        comparator_id=D1_PROTOCOL_COMPARATOR_ID,
        reference_id=D1_EVALUATOR_GOLD_ID,
        shipped_comparator_id=D1_SHIPPED_COMPARATOR_ID,
        branch=D1_EVALUATOR_BRANCH,
        declaration=declaration,
        frozen_space=divergence_of(
            protocol_declared_comparator,
            theory_id=f"{D1_PROTOCOL_COMPARATOR_ID} (frozen D1 space)",
            reference=_d1_evaluator_gold,
            space=frozen,
        ),
        protected_space=divergence_of(
            protocol_declared_comparator,
            theory_id=f"{D1_PROTOCOL_COMPARATOR_ID} (protected split only)",
            reference=_d1_evaluator_gold,
            space=protected,
        ),
        widened_space=divergence_of(
            protocol_declared_comparator,
            theory_id=f"{D1_PROTOCOL_COMPARATOR_ID} (pairs the D1 generator never builds)",
            reference=_d1_evaluator_gold,
            space=widened,
        ),
        against_shipped_comparator=divergence_of(
            protocol_declared_comparator,
            theory_id=f"{D1_PROTOCOL_COMPARATOR_ID} vs {D1_SHIPPED_COMPARATOR_ID}",
            reference=exact_relational_comparator,
            space=widened,
        ),
        divergent_label_pairs=tuple(sorted(parted.items())),
        divergence_shape=(
            "every divergence is a pair in which a comparison coordinate the "
            "declaration allows only as an exact semantic value or an explicit "
            "UNKNOWN carries neither: no value, and no unknown marking. The "
            "evaluator compares the absent value like any other and reports a "
            "decided OBSTRUCTION; the declared reading has nothing to compare and "
            "reports UNRESOLVED. The D1 generator never builds that shape --- "
            "unresolved_method nulls a coordinate and marks it in the same step --- "
            "so the two readings coincide on every case D1 was ever scored on"
        ),
        witness=_divergence_witness(widened, declaration),
        capacity=measure_refutation_capacity(
            check,
            reference=protocol_declared_comparator,
            reference_id=D1_PROTOCOL_COMPARATOR_ID,
            theories=declared_false_comparators(),
            space=protected,
        ),
    )


__all__ = [
    "D1_COMPARATOR_ARMS",
    "D1_EVALUATOR_BRANCH",
    "D1_EVALUATOR_GOLD_ID",
    "D1_ORACLE_THEORY_ID",
    "D1_PROTOCOL_COMPARATOR_ID",
    "D1_PROTOCOL_DIGESTS",
    "D1_PROTOCOL_PATHS",
    "D1_RESULT_DIGEST",
    "D1_RESULT_PATH",
    "D1_SEED",
    "D1_SHIPPED_COMPARATOR_ID",
    "D1_SHIPPED_DATASET_MANIFEST_DIGEST",
    "D1DatasetProvenanceError",
    "D1ProtocolDeclaration",
    "D1ProtocolDeclarationError",
    "DeclaredComparison",
    "IndependenceVerdict",
    "OracleIdentity",
    "OracleIndependence",
    "OracleVerdict",
    "ViewCollapse",
    "ViewCollapseReason",
    "d1_arm_responses",
    "d1_composition_sensitivity",
    "d1_contrast_margins",
    "d1_dataset_provenance",
    "d1_independent_oracle",
    "d1_oracle_divergence",
    "d1_oracle_identity",
    "d1_protocol_declaration",
    "d1_view_collapse",
    "d1_view_collapse_report",
    "declared_false_comparators",
    "frozen_d1_dataset",
    "load_shipped_d1_result",
    "protocol_declared_comparator",
]
