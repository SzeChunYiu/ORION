"""Protocol-matched baselines for the ORION-P1 hidden-formulation study.

The five baselines frozen in ``PROTOCOL_V1.json``. Every one of them is a
genuine attempt at the case rather than a foil, and the design enforces that
rather than promising it:

* **One perception layer.** ``extract_cues`` is shared verbatim by the
  baselines and by ORION. No system wins by *seeing* more of the prompt than
  another; what is compared is the decision policy over identical observations.
* **One budget table.** ``budget_for`` is keyed on ``PublicView.budget_class``
  and is the same for every system on a given case, so no system wins by
  spending more. The protocol's ``resource_policy`` requires exactly this.
* **Common agent competence.** Every baseline can acquire missing evidence and
  repair a broken execution, so both negative controls are winnable by all of
  them. A baseline that no-ops on controls would be a strawman on the very
  axis H2 measures.
* **They differ only in which formulation coordinate their policy can reach.**
  That is the frozen definition of each baseline, not a handicap added here.

``root_solved`` is never self-asserted. A system re-runs the shared detector
against its own post-repair state: a repair clears exactly the material cues
its policy targeted, and any strong cue that survives means the root task is
unsolved. A formulation cue is cleared only by a policy that actually changes
that coordinate, which is why attributing a representation defect to "missing
evidence" faithfully acquires the evidence and still fails.

Stale certainty is deliberately *not* folded into ``root_solved``. The protocol
measures ``stale_closure_survival_rate`` as its own secondary metric, and a
system that repairs the root defect while leaving a dependent conclusion
standing has done one thing right and one thing wrong. Collapsing the two would
confound the primary metric and would double-charge the same mistake. Surviving
stale closures are computed and recorded in ``notes`` for the grader.

**Scope of the mechanical arm — measured, not assumed.** The suite forbids the
gold vocabulary from every public field, so what is observable is the
*phenomenon* and never its name. Run against the frozen TEST split, all eleven
systems abstain on 47 of 48 cases: recovering a formulation responsibility from
symptoms and numbers requires world knowledge that a lexical detector does not
have, and the graded arm is the live provider.

That is the honest result and it is reported as abstention, which is the
distinction the frozen ``SystemTrace`` exists to preserve. It is emphatically
not scored as success — an earlier revision of this module treated "no residual
detected" as "nothing wrong" and reported these systems as flawless on exactly
the cases they cannot read.

Where a residual *is* legible, these systems answer at coordinate-axis
granularity: ``target_coordinates`` is a 1-tuple ``(axis,)`` where gold carries
``(axis, "<prefix>:<specific_target>")``. Naming the specific target is the
live provider's job, and inventing a plausible slug would fabricate a claim.

The mechanical arm therefore earns its keep by exercising the protocol, the
budget discipline, the reopen machinery and the harness deterministically, and
by establishing the policy-difference structure the graded run measures.

Resource accounting reports what the system actually did. Mechanical mode calls
no model, so ``model_tokens`` is 0 and ``wallclock_seconds`` is 0.0: these
systems perform no wall-clock-bearing external work, and recording the harness's
own CPU noise as system latency would be a fabricated cost (it would also break
seed reproducibility). The harness measures and archives elapsed time per run
separately, where it belongs. ``tool_calls`` and ``search_queries`` are real
counts of resource probes and variation rounds, capped by the shared budget.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from enum import Enum

from orion.core.residuals import Residual, ResidualKind, Responsibility

from .cases import PublicView
from .systems import ResourceUse, SystemTrace

# --------------------------------------------------------------------------
# Coordinates
# --------------------------------------------------------------------------

# Coarse axes, in the engine's own `Transition.changed_coordinates` namespace.
# Only `W.ACTIVE_DOMAINS` and `W.REPRESENTATIONS` are executable by
# `orion.engine.operators.reframe` today; the other four are gold-side axes the
# engine cannot yet emit. That gap is recorded per run rather than papered over
# (see `orion_system.ENGINE_EXECUTABLE_AXES`).
COORDINATE_BY_RESPONSIBILITY: dict[Responsibility, str] = {
    Responsibility.QUESTION: "FRAME.QUESTION",
    Responsibility.REPRESENTATION: "W.REPRESENTATIONS",
    # The suite labels a hidden *parent domain* with responsibility SEARCH; the
    # axis it moves is the active-domain set.
    Responsibility.SEARCH: "W.ACTIVE_DOMAINS",
    Responsibility.ROUTING: "W.ACTIVE_DOMAINS",
    Responsibility.DECOMPOSITION: "W.DECOMPOSITION",
    Responsibility.INTERFACE: "W.INTERFACE",
    Responsibility.MEASUREMENT: "M.MEASUREMENT",
    Responsibility.EVALUATOR: "M.EVALUATOR",
    Responsibility.METHOD: "M.METHOD",
}

# K-only revision: the one coordinate an information-state reviser can change.
CLAIM_COORDINATE = "K.CLAIMS"

# Responsibilities whose repair is a formulation change rather than acquisition
# or repair-in-place.
FORMULATION_RESPONSIBILITIES = frozenset(COORDINATE_BY_RESPONSIBILITY)

# Repairs any competent tool-using agent can perform without touching the
# formulation. Every baseline has these; withholding them would manufacture the
# control-case failures H2 is supposed to measure.
SURFACE_RESPONSIBILITIES = frozenset({Responsibility.EVIDENCE, Responsibility.EXECUTION})

_RESIDUAL_KIND_BY_RESPONSIBILITY: dict[Responsibility, ResidualKind] = {
    Responsibility.QUESTION: ResidualKind.CONTEXT_GAP,
    Responsibility.REPRESENTATION: ResidualKind.REPRESENTATION_FAILURE,
    Responsibility.ROUTING: ResidualKind.SEARCH_COVERAGE_FAILURE,
    Responsibility.SEARCH: ResidualKind.SEARCH_COVERAGE_FAILURE,
    Responsibility.DECOMPOSITION: ResidualKind.DECOMPOSITION_FAILURE,
    Responsibility.INTERFACE: ResidualKind.INTERFACE_FAILURE,
    Responsibility.MEASUREMENT: ResidualKind.MEASUREMENT_FAILURE,
    Responsibility.EVALUATOR: ResidualKind.EVALUATOR_FAILURE,
    Responsibility.METHOD: ResidualKind.METHOD_GAP,
    Responsibility.EVIDENCE: ResidualKind.MISSING_EVIDENCE,
    # There is no EXECUTION residual kind in the core taxonomy: an execution
    # defect is a repair-in-place, not an epistemic residual. UNCLASSIFIED is
    # the honest slot rather than borrowing a kind that means something else.
    Responsibility.EXECUTION: ResidualKind.UNCLASSIFIED,
}


# --------------------------------------------------------------------------
# Perception: one detector, shared by every system under test
# --------------------------------------------------------------------------


class CueStrength(str, Enum):
    """How much a surface signal licenses.

    STRONG is an explicit artifact or a stated defect — it discriminates
    between competing responsibility hypotheses. WEAK is a lexical hint: a
    hypothesis worth holding, never on its own a reason for a high-impact
    revision. The distinction is the entire content of DIAGNOSE's attribution
    rule (`orion.mechanics.diagnosis`), and checking it is what a mechanic
    self-audit does.
    """

    STRONG = "STRONG"
    WEAK = "WEAK"


@dataclass(frozen=True)
class Cue:
    """One observation extracted from the public view.

    `source` records whether the observation came from the prompt (a
    description of the failure happening now) or from a resource line (a past
    assumption a closure was taken under). The difference is the only
    discriminator available without world knowledge, and ORION uses it when two
    strong observations disagree.
    """

    cue_id: str
    responsibility: Responsibility
    coordinate: str
    strength: CueStrength
    marker: str
    evidence: str
    source: str = "prompt"

    @property
    def formulation(self) -> bool:
        return self.responsibility in FORMULATION_RESPONSIBILITIES

    @property
    def material(self) -> bool:
        """Only a discriminating observation is a residual."""

        return self.strength is CueStrength.STRONG


# Public phenomenon vocabulary. A case may declare an observable phenomenon as
# a resource `signal:<name>`; the name describes what is *seen* (a scale
# mismatch, a saturating response) and never what it is *called* in gold, so it
# leaks no hidden label. The phenomenon-to-responsibility knowledge lives here,
# in the systems, which is where a solver's competence belongs.
# --------------------------------------------------------------------------
# A refused design, recorded so it is not re-proposed
# --------------------------------------------------------------------------
#
# An earlier version of this detector read a declared `signal:<phenomenon>`
# resource and mapped it to a responsibility. The suite author measured it with
# `orion.benchmarks.degeneracy.probe_records` and the result was decisive:
#
#     frozen suite                      : CLEAN
#     frozen suite + signal: resource   : DEGENERATE
#       single_feature_determines_label : 'signal' determines the label for
#                                         every record (baseline 0.167)
#       blind_responder_ceiling         : 'signal_lookup' scores 1.000 while
#                                         reading no substantive content
#
# Token collisions with gold vocabulary were *not* the problem — there were
# none. The problem is structural, and it generalises past any renaming: a
# public token that is a deterministic function of the hidden label leaks it
# wherever the lookup table is stored. Any channel rich enough for a mechanical
# system to recover the responsibility is, by the same predicate, rich enough
# for a blind responder — so H1 and H2 become unmeasurable. It also violates
# `PROTOCOL_V1.json` `access_policy.hidden_labels`, which is DESIGN_FROZEN.
#
# The channel is therefore refused, and any resource declaring one is ignored
# rather than read, so a case that reintroduces it cannot silently degenerate
# the study. `test_a_declared_signal_channel_is_refused` guards this.
_REFUSED_RESOURCE_PREFIX = "signal:"

# (marker, responsibility, strength).
#
# Markers describe observable phenomena, not gold names: the suite forbids any
# token of a case's own gold vocabulary from appearing in its public fields, so
# a detector keyed on the gold term would by construction find nothing.
_MARKERS: tuple[tuple[str, Responsibility, CueStrength], ...] = (
    # --- representation / coordinate system -------------------------------
    ("unit mismatch", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("wrong units", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("units are", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("scale mismatch", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("expressed in", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("parameterized in", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("encoded as", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("change of basis", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("two different forms", Responsibility.REPRESENTATION, CueStrength.STRONG),
    ("units", Responsibility.REPRESENTATION, CueStrength.WEAK),
    ("basis", Responsibility.REPRESENTATION, CueStrength.WEAK),
    ("log scale", Responsibility.REPRESENTATION, CueStrength.WEAK),
    ("encoding", Responsibility.REPRESENTATION, CueStrength.WEAK),
    # --- hidden parent domain (suite responsibility: SEARCH) ---------------
    ("another discipline", Responsibility.SEARCH, CueStrength.STRONG),
    ("adjacent field", Responsibility.SEARCH, CueStrength.STRONG),
    ("unrelated field", Responsibility.SEARCH, CueStrength.STRONG),
    ("outside the field", Responsibility.SEARCH, CueStrength.STRONG),
    ("standard elsewhere", Responsibility.SEARCH, CueStrength.STRONG),
    ("never queried", Responsibility.SEARCH, CueStrength.STRONG),
    ("coverage gap", Responsibility.SEARCH, CueStrength.STRONG),
    ("discipline", Responsibility.SEARCH, CueStrength.WEAK),
    ("literature", Responsibility.SEARCH, CueStrength.WEAK),
    ("elsewhere", Responsibility.SEARCH, CueStrength.WEAK),
    # --- decomposition -----------------------------------------------------
    ("do not compose", Responsibility.DECOMPOSITION, CueStrength.STRONG),
    ("not independent", Responsibility.DECOMPOSITION, CueStrength.STRONG),
    ("assumed independent", Responsibility.DECOMPOSITION, CueStrength.STRONG),
    ("interact across", Responsibility.DECOMPOSITION, CueStrength.STRONG),
    ("split into", Responsibility.DECOMPOSITION, CueStrength.STRONG),
    ("stage boundaries", Responsibility.DECOMPOSITION, CueStrength.STRONG),
    ("subproblem", Responsibility.DECOMPOSITION, CueStrength.WEAK),
    ("component", Responsibility.DECOMPOSITION, CueStrength.WEAK),
    ("stage", Responsibility.DECOMPOSITION, CueStrength.WEAK),
    # --- interface ---------------------------------------------------------
    ("schema mismatch", Responsibility.INTERFACE, CueStrength.STRONG),
    ("handoff format", Responsibility.INTERFACE, CueStrength.STRONG),
    ("boundary between", Responsibility.INTERFACE, CueStrength.STRONG),
    ("contract states", Responsibility.INTERFACE, CueStrength.STRONG),
    ("format expected by", Responsibility.INTERFACE, CueStrength.STRONG),
    ("contract", Responsibility.INTERFACE, CueStrength.WEAK),
    ("schema", Responsibility.INTERFACE, CueStrength.WEAK),
    ("handoff", Responsibility.INTERFACE, CueStrength.WEAK),
    # --- measurement / operationalization ----------------------------------
    ("does not measure", Responsibility.MEASUREMENT, CueStrength.STRONG),
    ("proxy for", Responsibility.MEASUREMENT, CueStrength.STRONG),
    ("scored by", Responsibility.MEASUREMENT, CueStrength.STRONG),
    ("success is defined as", Responsibility.MEASUREMENT, CueStrength.STRONG),
    ("counted as", Responsibility.MEASUREMENT, CueStrength.STRONG),
    ("average hides", Responsibility.MEASUREMENT, CueStrength.STRONG),
    ("metric", Responsibility.MEASUREMENT, CueStrength.WEAK),
    ("measure", Responsibility.MEASUREMENT, CueStrength.WEAK),
    ("score", Responsibility.MEASUREMENT, CueStrength.WEAK),
    # --- evaluator / grader ------------------------------------------------
    ("the grader", Responsibility.EVALUATOR, CueStrength.STRONG),
    ("the judge", Responsibility.EVALUATOR, CueStrength.STRONG),
    ("acceptance test", Responsibility.EVALUATOR, CueStrength.STRONG),
    ("scoring function", Responsibility.EVALUATOR, CueStrength.STRONG),
    ("rubric", Responsibility.EVALUATOR, CueStrength.STRONG),
    ("grader", Responsibility.EVALUATOR, CueStrength.WEAK),
    ("judge", Responsibility.EVALUATOR, CueStrength.WEAK),
    # --- method (protected: Self-ORION territory) --------------------------
    ("the method itself", Responsibility.METHOD, CueStrength.STRONG),
    ("change the method", Responsibility.METHOD, CueStrength.STRONG),
    # --- evidence acquisition ----------------------------------------------
    ("no source", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("missing data", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("has not been retrieved", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("citation is missing", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("needs a source", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("unverified", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("not yet read", Responsibility.EVIDENCE, CueStrength.STRONG),
    ("citation", Responsibility.EVIDENCE, CueStrength.WEAK),
    ("source", Responsibility.EVIDENCE, CueStrength.WEAK),
    # --- execution repair --------------------------------------------------
    ("traceback", Responsibility.EXECUTION, CueStrength.STRONG),
    ("stack trace", Responsibility.EXECUTION, CueStrength.STRONG),
    ("off-by-one", Responsibility.EXECUTION, CueStrength.STRONG),
    ("indexerror", Responsibility.EXECUTION, CueStrength.STRONG),
    ("raises an exception", Responsibility.EXECUTION, CueStrength.STRONG),
    ("fails to run", Responsibility.EXECUTION, CueStrength.STRONG),
    ("syntax error", Responsibility.EXECUTION, CueStrength.STRONG),
    ("timed out", Responsibility.EXECUTION, CueStrength.STRONG),
    ("crashes", Responsibility.EXECUTION, CueStrength.STRONG),
    ("bug", Responsibility.EXECUTION, CueStrength.WEAK),
    ("broken", Responsibility.EXECUTION, CueStrength.WEAK),
)

# Deterministic ranking wherever a policy must choose between competing
# hypotheses. Shared, so no system gets a better tie-break than another.
_RESPONSIBILITY_ORDER: tuple[Responsibility, ...] = (
    Responsibility.EXECUTION,
    Responsibility.EVIDENCE,
    Responsibility.REPRESENTATION,
    Responsibility.SEARCH,
    Responsibility.ROUTING,
    Responsibility.DECOMPOSITION,
    Responsibility.INTERFACE,
    Responsibility.MEASUREMENT,
    Responsibility.EVALUATOR,
    Responsibility.QUESTION,
    Responsibility.METHOD,
)


def _fragment(text: str, marker: str) -> str:
    index = text.lower().find(marker)
    if index < 0:
        return ""
    start = max(0, index - 32)
    end = min(len(text), index + len(marker) + 32)
    return " ".join(text[start:end].split())


def readable_resources(view: PublicView) -> tuple[str, ...]:
    """Resources a system is willing to read.

    A declared `signal:` channel is dropped rather than parsed. See the refusal
    note above: reading it would hand every system the hidden label.
    """

    return tuple(
        item
        for item in view.observable_resources
        if not item.strip().lower().startswith(_REFUSED_RESOURCE_PREFIX)
    )


def extract_cues(view: PublicView) -> tuple[Cue, ...]:
    """Read the public view once, for every system, in the same way.

    Deliberately not per-system: if each system had its own detector, ORION
    could win by perceiving better rather than deciding better, and the
    protocol's matched-capability rule would be violated in a way no headline
    number would reveal.

    The prompt is scanned before the resource lines, so when the same
    responsibility is evidenced in both, the cue is attributed to the prompt —
    the description of the failure now, rather than of an assumption taken
    earlier.
    """

    resources = readable_resources(view)
    found: dict[tuple[Responsibility, CueStrength], Cue] = {}
    for source, text in (
        ("prompt", view.public_prompt),
        ("resource", "\n".join(resources)),
    ):
        lowered = text.lower()
        for marker, responsibility, strength in _MARKERS:
            if marker not in lowered:
                continue
            key = (responsibility, strength)
            if key in found:
                continue
            found[key] = Cue(
                cue_id=f"cue:{responsibility.value.lower()}:{strength.value.lower()}",
                responsibility=responsibility,
                coordinate=COORDINATE_BY_RESPONSIBILITY.get(responsibility, ""),
                strength=strength,
                marker=marker,
                evidence=_fragment(text, marker),
                source=source,
            )

    # A strong cue subsumes the weak cue for the same responsibility: keeping
    # both would double-count one observation.
    strong = {cue.responsibility for cue in found.values() if cue.material}
    cues = [
        cue for cue in found.values() if cue.material or cue.responsibility not in strong
    ]
    return tuple(
        sorted(
            cues,
            key=lambda item: (
                0 if item.material else 1,
                _RESPONSIBILITY_ORDER.index(item.responsibility),
            ),
        )
    )


def cue_to_residual(cue: Cue, *, case_id: str) -> Residual:
    """Lift a cue into the runtime's own typed residual."""

    return Residual(
        residual_id=f"residual:{case_id}:{cue.responsibility.value.lower()}",
        kind=_RESIDUAL_KIND_BY_RESPONSIBILITY[cue.responsibility],
        description=cue.evidence or cue.marker,
        material=cue.material,
        candidate_responsibilities=(cue.responsibility,),
        metadata=(("cue_id", cue.cue_id), ("strength", cue.strength.value)),
    )


def material_cues(cues: tuple[Cue, ...]) -> tuple[Cue, ...]:
    return tuple(cue for cue in cues if cue.material)


# --------------------------------------------------------------------------
# Budget: identical allocation for every system on a given case
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Budget:
    """The frozen per-case allocation from the protocol's `resource_policy`."""

    tool_calls: int
    search_queries: int
    model_tokens: int
    max_depth: int


# The suite freezes one budget class for every case in both splits: any
# per-family variation would be publicly visible through `PublicView` and would
# perfectly determine the family, breaking the hidden-label policy. The other
# entries exist so an unknown class resolves to something declared rather than
# to an implicit default.
BUDGETS: dict[str, Budget] = {
    "p1_standard_v1": Budget(
        tool_calls=16, search_queries=8, model_tokens=60_000, max_depth=4
    ),
    "standard": Budget(
        tool_calls=16, search_queries=8, model_tokens=60_000, max_depth=4
    ),
    "small": Budget(tool_calls=8, search_queries=4, model_tokens=30_000, max_depth=3),
    "extended": Budget(
        tool_calls=32, search_queries=16, model_tokens=120_000, max_depth=6
    ),
}

DEFAULT_BUDGET_CLASS = "p1_standard_v1"


def budget_for(view: PublicView) -> Budget:
    """Same budget for every system on this case; unknown classes fall back.

    A missing budget class is not silently treated as unlimited: it resolves to
    the frozen standard allocation, which keeps the comparison matched.
    """

    return BUDGETS.get(view.budget_class, BUDGETS[DEFAULT_BUDGET_CLASS])


@dataclass
class ProbeLedger:
    """Honest accounting of the work a system actually performed."""

    budget: Budget
    tool_calls: int = 0
    search_queries: int = 0
    truncated: bool = False

    def probe(self, count: int = 1) -> int:
        granted = max(0, min(count, self.budget.tool_calls - self.tool_calls))
        if granted < count:
            self.truncated = True
        self.tool_calls += granted
        return granted

    def query(self, count: int = 1) -> int:
        granted = max(0, min(count, self.budget.search_queries - self.search_queries))
        if granted < count:
            self.truncated = True
        self.search_queries += granted
        return granted

    @property
    def usage(self) -> ResourceUse:
        return ResourceUse(
            # 0.0 by construction: a mechanical system performs no
            # wall-clock-bearing external work. The harness archives measured
            # elapsed time per run; reporting harness CPU noise here would be a
            # fabricated system cost and would break seed reproducibility.
            wallclock_seconds=0.0,
            # 0 by construction: no model was called in mechanical mode.
            model_tokens=0,
            tool_calls=self.tool_calls,
            search_queries=self.search_queries,
        )


def deterministic_rng(system_id: str, view: PublicView, seed: int) -> random.Random:
    """Seed from content, never from `hash()`.

    `hash(str)` is salted per interpreter process, so a study reproduced
    tomorrow would silently disagree with the archive.
    """

    digest = hashlib.sha256(f"{system_id}|{view.case_id}|{seed}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


# --------------------------------------------------------------------------
# Public closures: what a reframe may have staled
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PublicClosure:
    """A conclusion the public view says is already closed.

    `dependency_coordinates` is the **transitive** basis: a closure closed
    under another closure inherits that parent's basis, because the paper's
    rule is `z in D*(c)`, not `z in D(c)`. `own_coordinates` keeps the directly
    declared part so the inherited part stays inspectable.
    """

    closure_id: str
    dependency_coordinates: tuple[str, ...]
    stage: int
    own_coordinates: tuple[str, ...] = ()
    parent_ids: tuple[str, ...] = ()


_CLOSURE_PREFIXES = ("closure:", "conclusion:")


def _coordinate_tokens(raw: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for token in raw.replace("|", ",").replace(";", ",").split(","):
        candidate = token.strip()
        if candidate and "." in candidate and candidate == candidate.upper():
            tokens.append(candidate)
    return tuple(dict.fromkeys(tokens))


def _closure_slug(body: str) -> tuple[str, str]:
    """Split `<slug> <rest of the resource line>`."""

    head, _, rest = body.strip().partition(" ")
    slug = head.strip().strip(".,;:—-")
    return slug, rest.strip()


def public_closures(view: PublicView) -> tuple[PublicClosure, ...]:
    """Parse declared closures and the coordinates they were closed under.

    The suite names every reopenable closure in `observable_resources` as
    ``closure:<kebab-slug>`` with the rest of the line stating what it was
    closed under, so a system can name what it reopens in the gold's own
    namespace. Dependency coordinates are taken, in order of authority, from:

    1. explicit coordinate tokens on the resource line
       (``closure:baseline-fit W.REPRESENTATIONS,M.MEASUREMENT``);
    2. cues extracted from the "closed under ..." clause of that line;
    3. cues from the prompt sentence that names the slug.

    When all three yield nothing, the dependency basis is empty: unknown is
    recorded as unknown, and a dependency-directed policy correctly reopens
    nothing rather than guessing.
    """

    closures: list[PublicClosure] = []
    sentences = [item.strip() for item in view.public_prompt.split(".") if item.strip()]
    for resource in view.observable_resources:
        text = resource.strip()
        lowered = text.lower()
        prefix = next(
            (item for item in _CLOSURE_PREFIXES if lowered.startswith(item)), ""
        )
        if not prefix:
            continue
        slug, rest = _closure_slug(text[len(prefix) :])
        if not slug:
            continue
        declared = _coordinate_tokens(rest)
        if not declared:
            declared = _coordinates_from_text(rest)
        if not declared:
            declared = _coordinates_from_text(
                " ".join(item for item in sentences if slug.lower() in item.lower())
            )
        closures.append(
            PublicClosure(
                closure_id=f"{prefix}{slug}",
                dependency_coordinates=declared,
                stage=len(closures),
                own_coordinates=declared,
                parent_ids=_parent_ids(rest),
            )
        )
    return _with_transitive_basis(tuple(closures))


def _parent_ids(text: str) -> tuple[str, ...]:
    """Closures named inside another closure's line are its parents."""

    parents: list[str] = []
    for token in text.split():
        cleaned = token.strip().strip(".,;:()—-")
        lowered = cleaned.lower()
        prefix = next(
            (item for item in _CLOSURE_PREFIXES if lowered.startswith(item)), ""
        )
        if prefix and len(cleaned) > len(prefix):
            parents.append(f"{prefix}{cleaned[len(prefix):]}")
    return tuple(dict.fromkeys(parents))


def _with_transitive_basis(
    closures: tuple[PublicClosure, ...],
) -> tuple[PublicClosure, ...]:
    """Propagate each closure's basis down its dependency chain.

    The paper's reopen rule is transitive: a conclusion is stale when the
    changed coordinate is anywhere in the basis it was ultimately closed under.
    A closure closed under another closure declares no coordinate of its own,
    so without propagation it could never be reopened and reopen recall would
    collapse to the head of every chain — precisely on the deep cases H3 is
    there to measure.

    Cycles are tolerated rather than raised: a malformed public view is the
    suite's problem to fix, and a system should not crash on one.
    """

    by_id = {item.closure_id: item for item in closures}
    resolved: dict[str, tuple[str, ...]] = {}

    def basis(closure_id: str, seen: frozenset[str]) -> tuple[str, ...]:
        if closure_id in resolved:
            return resolved[closure_id]
        item = by_id.get(closure_id)
        if item is None or closure_id in seen:
            return ()
        collected = list(item.own_coordinates)
        for parent in item.parent_ids:
            collected.extend(basis(parent, seen | {closure_id}))
        answer = tuple(dict.fromkeys(collected))
        resolved[closure_id] = answer
        return answer

    return tuple(
        PublicClosure(
            closure_id=item.closure_id,
            dependency_coordinates=basis(item.closure_id, frozenset()),
            stage=item.stage,
            own_coordinates=item.own_coordinates,
            parent_ids=item.parent_ids,
        )
        for item in closures
    )


def _coordinates_from_text(text: str) -> tuple[str, ...]:
    """Coordinates hinted at by a fragment.

    Weak cues count here: naming what a closure rests on is a dependency hint,
    not a license to revise anything.
    """

    if not text.strip():
        return ()
    probe = PublicView(
        case_id="fragment",
        public_prompt=text,
        observable_resources=(),
        budget_class=DEFAULT_BUDGET_CLASS,
    )
    return tuple(
        dict.fromkeys(cue.coordinate for cue in extract_cues(probe) if cue.coordinate)
    )


def descendants_of(
    closures: tuple[PublicClosure, ...], roots: tuple[str, ...]
) -> tuple[str, ...]:
    """Every closure derived, transitively, from an identified closure.

    The paper's rule is `z in D*(c)`. `_with_transitive_basis` implements it in
    *coordinate* space, which works only when the head of a chain declares a
    coordinate basis. On the frozen suite it does not: 37 of 44 hidden-shift
    cases have no closure with any publicly inferable coordinate, so a purely
    coordinate-keyed reopen stales nothing and scores reopen F1 0.000.

    This is the same rule in *graph* space, keyed on the closure a reframe
    invalidates rather than on a coordinate string. Identifying that closure is
    a reasoning act — the live provider's job, and not something the public
    view hands over — but once it is identified, expansion is mechanical and
    exact: measured against the frozen gold it recovers the reopen set with
    F1 1.000 on all 44 hidden-shift cases, because gold is exactly one closure
    component and survivor chains are disconnected from it.

    Nothing here is fitted to gold. The rule is the paper's; the measurement
    only confirms the suite is consistent with it.
    """

    known = {item.closure_id: item for item in closures}
    children: dict[str, list[str]] = {key: [] for key in known}
    for item in closures:
        for parent in item.parent_ids:
            if parent in children:
                children[parent].append(item.closure_id)

    staled: list[str] = []
    frontier = [item for item in roots if item in known]
    seen: set[str] = set()
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        staled.append(current)
        frontier.extend(children.get(current, ()))
    return tuple(dict.fromkeys(staled))


def stage_reopen(
    closures: tuple[PublicClosure, ...], changed: tuple[str, ...]
) -> tuple[str, ...]:
    """Reopen by plan stage: everything from the first affected stage onward.

    A real dependency story that is simply the wrong one — coarse in exactly
    the way the paper predicts, staling correct conclusions that happen to sit
    later in plan order.
    """

    if not changed:
        return ()
    changed_set = set(changed)
    first = next(
        (
            item.stage
            for item in closures
            if changed_set.intersection(item.dependency_coordinates)
        ),
        None,
    )
    if first is None:
        return ()
    return tuple(item.closure_id for item in closures if item.stage >= first)


# --------------------------------------------------------------------------
# Shared repair semantics
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RepairOutcome:
    acted_on: Responsibility | None
    cleared: tuple[Cue, ...]
    remaining: tuple[Cue, ...]
    changed_coordinates: tuple[str, ...]


def apply_repairs(
    cues: tuple[Cue, ...],
    *,
    surface: frozenset[Responsibility],
    reachable_coordinates: frozenset[str],
) -> RepairOutcome:
    """Clear exactly the material cues this policy can actually repair.

    Surface repairs (acquire the source, fix the crash) clear surface cues.
    A formulation cue is cleared only by a policy that changes that coordinate.
    Nothing here consults gold: the check is whether the system's own detector
    still fires on its own post-repair state.
    """

    cleared: list[Cue] = []
    remaining: list[Cue] = []
    changed: list[str] = []
    for cue in cues:
        if not cue.material:
            remaining.append(cue)
            continue
        if cue.formulation:
            if cue.coordinate and cue.coordinate in reachable_coordinates:
                cleared.append(cue)
                changed.append(cue.coordinate)
            else:
                remaining.append(cue)
            continue
        if cue.responsibility in surface:
            cleared.append(cue)
        else:
            remaining.append(cue)

    acted: Responsibility | None = None
    for candidate in _RESPONSIBILITY_ORDER:
        if any(cue.responsibility is candidate for cue in cleared):
            acted = candidate
            break
    # Report the coordinate-changing action when there was one: that is the
    # decision this study is about.
    formulation_acted = [cue for cue in cleared if cue.formulation]
    if formulation_acted:
        acted = formulation_acted[0].responsibility
    return RepairOutcome(
        acted_on=acted,
        cleared=tuple(cleared),
        remaining=tuple(remaining),
        changed_coordinates=tuple(dict.fromkeys(changed)),
    )


def stale_closures_survive(
    closures: tuple[PublicClosure, ...],
    *,
    changed: tuple[str, ...],
    reopened: tuple[str, ...],
) -> tuple[str, ...]:
    """Closures that materially depended on a changed coordinate and were kept.

    Stale certainty is a root-task failure, not a bookkeeping blemish: the
    system is still asserting a conclusion whose assumptions it just changed.
    """

    if not changed:
        return ()
    changed_set = set(changed)
    opened = set(reopened)
    return tuple(
        item.closure_id
        for item in closures
        if changed_set.intersection(item.dependency_coordinates)
        and item.closure_id not in opened
    )


def axis_answer(changed: tuple[str, ...]) -> tuple[str, ...]:
    """Report the coordinate axis only.

    Gold carries ``(axis, "<prefix>:<specific_target>")``. A mechanical system
    can identify the axis from the phenomenon but cannot name the specific
    target, because the suite forbids the gold vocabulary from every public
    field. Emitting a 1-tuple states exactly that: axis identified, specific
    target not claimed. Inventing a plausible-looking second element would
    fabricate a claim the system never made.
    """

    return changed[:1]


def planned_rounds(cues: tuple[Cue, ...], budget: Budget) -> int:
    """How many decision rounds every system gets on this case.

    Computed from the shared perception layer *before* any policy branching, so
    it is identical for all eleven systems. This is what makes the comparison
    matched in fact rather than only in cap: a system cannot win by taking more
    turns than another, and an ablation cannot lose by taking fewer.

    One round per material residual plus one to verify the result, bounded by
    the budget's depth.
    """

    return min(budget.max_depth, max(1, len(material_cues(cues)) + 1))


def _probe_resources(view: PublicView, ledger: ProbeLedger) -> None:
    """Read the observable resources, and hold one slot for self-verification.

    Every system reads every resource, and every system checks its own result
    at the end — that is how `root_solved` is computed for all of them. Both
    costs are therefore charged identically, so the ledger difference between
    two systems can only come from what their policies did.
    """

    ledger.probe(len(view.observable_resources) + 1)


def acted(
    cues: tuple[Cue, ...],
    remaining: tuple[Cue, ...],
    changed: tuple[str, ...] = (),
) -> bool:
    """Did the system do anything — repair a residual or move a coordinate?"""

    return bool(changed) or len(material_cues(remaining)) < len(material_cues(cues))


def abstains(
    cues: tuple[Cue, ...],
    remaining: tuple[Cue, ...] = (),
    changed: tuple[str, ...] = (),
) -> bool:
    """The system declined: it saw no residual and took no action.

    Abstention is about conduct, not only perception. A system that varies a
    coordinate has acted and owns the answer, even if it never localised a
    residual — which is why `SystemTrace` treats a reframe by an abstainer as
    malformed. A system that saw nothing and did nothing has genuinely
    declined.
    """

    return not material_cues(cues) and not acted(cues, remaining, changed)


def solved(cues: tuple[Cue, ...], remaining: tuple[Cue, ...]) -> bool:
    """Root success requires having seen a residual and then cleared it.

    This is the single most consequential rule in the module. A system that
    localises no material residual has *not* solved the task — it has failed to
    see it. Treating "nothing detected" as "nothing wrong" scored the
    mechanical systems 100% on precisely the hidden-formulation cases they
    cannot read, which would have inverted the study's headline result.
    """

    return bool(material_cues(cues)) and not material_cues(remaining)


# --------------------------------------------------------------------------
# Baseline 1 — static ReAct-style tool workflow
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class StaticReactToolWorkflow:
    """Plan, act, observe, repeat. Never rewrites the question.

    A competent tool-using agent: it acquires missing evidence and repairs
    broken execution, and it does both well. Its structural limit is that every
    residual is attributed to evidence or execution, because those are the only
    two things its action space can change.
    """

    system_id: str = "static_react_tool_workflow"

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        budget = budget_for(view)
        ledger = ProbeLedger(budget)
        cues = extract_cues(view)
        _probe_resources(view, ledger)
        ledger.query(planned_rounds(cues, budget))
        outcome = apply_repairs(
            cues,
            surface=SURFACE_RESPONSIBILITIES,
            reachable_coordinates=frozenset(),
        )
        unresolved = material_cues(outcome.remaining)
        acted = outcome.acted_on
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=False,
            responsibility_family=acted.value if acted else "",
            target_coordinates=(),
            reopened=(),
            root_solved=solved(cues, outcome.remaining),
            abstained=abstains(cues, outcome.remaining),
            max_recursion_depth=1 if outcome.cleared else 0,
            resources=ledger.usage,
            notes=(
                "attributed to evidence/execution; unresolved="
                + ",".join(cue.cue_id for cue in unresolved)
            ),
        )


# --------------------------------------------------------------------------
# Baseline 2 — tree-search / iterative research
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class TreeSearchIterativeResearch:
    """Retry with variation over a publicly enumerable candidate set.

    Deliberately strong: its variations range over *any* coordinate the public
    view hints at, weak hints included, so it can reach a representation or a
    parent domain that a static workflow never will.

    What it never does is type the responsibility, and that has a consequence
    it cannot escape: having explored several branches it has no attribution
    with which to prefer one, so the branch it commits to is drawn from those
    it explored. Exploration order decides the answer. On a case with a single
    plausible coordinate it lands it every time; on a case with a decoy it
    lands it at the rate chance allows, which is exactly what the protocol's
    five stochastic repeats are there to measure. It also varies the
    formulation on negative controls, and having no dependency model it leaves
    closures standing whose assumptions it just changed.
    """

    system_id: str = "tree_search_iterative_research"

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        budget = budget_for(view)
        ledger = ProbeLedger(budget)
        rng = deterministic_rng(self.system_id, view, seed)
        cues = extract_cues(view)
        _probe_resources(view, ledger)

        candidates = list(
            dict.fromkeys(
                cue.coordinate for cue in cues if cue.formulation and cue.coordinate
            )
        )
        rng.shuffle(candidates)

        # A real frontier: branches are expanded in search order and never
        # re-expanded. The limit is the shared round budget, so on a case where
        # the public view hints at more coordinates than there are rounds, the
        # branch it never reaches is the one it never tries — which is what
        # having no attribution costs.
        rounds = planned_rounds(cues, budget)
        varied: list[str] = []
        remaining = cues
        for index in range(rounds):
            if not ledger.query(1):
                break
            # Surface repair happens every round whether or not a branch is
            # left to expand: an agent with nothing to vary still fixes the
            # crash in front of it.
            branch = candidates[index] if index < len(candidates) else ""
            if branch:
                varied.append(branch)
            outcome = apply_repairs(
                remaining,
                surface=SURFACE_RESPONSIBILITIES,
                reachable_coordinates=frozenset({branch} if branch else ()),
            )
            remaining = outcome.remaining

        closures = public_closures(view)
        branches = len(varied)
        # The variation was applied whether or not it repaired anything: on a
        # control that is an unnecessary reframe, and it is recorded as one.
        varied = list(dict.fromkeys(varied))
        stale = stale_closures_survive(closures, changed=tuple(varied), reopened=())
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=bool(varied),
            # No typed responsibility, by construction.
            responsibility_family="",
            target_coordinates=(),
            reopened=(),
            root_solved=solved(cues, remaining),
            abstained=abstains(cues, remaining, tuple(varied)),
            max_recursion_depth=branches,
            resources=ledger.usage,
            notes=(
                f"variations={branches} explored={varied} "
                f"unreached={candidates[branches:]} stale_survivors={sorted(stale)}"
            ),
        )


# --------------------------------------------------------------------------
# Baseline 3 — AREX-like recursive audit and follow-up
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArexLikeRecursiveAuditFollowup:
    """Audit the declared constraints; follow up on the one that fails.

    Genuinely recursive: it re-audits after each repair and keeps going while a
    constraint still fails. Its follow-up targets the failing constraint, which
    is right when the constraint itself is the defect — a violated interface
    contract is repaired properly here, and this baseline wins those cases
    outright. It is wrong when the failing constraint is a symptom of a
    formulation defect elsewhere: it patches the constraint, re-audits, and the
    same class of failure is still standing.
    """

    system_id: str = "arex_like_recursive_audit_followup"

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        budget = budget_for(view)
        ledger = ProbeLedger(budget)
        cues = extract_cues(view)
        _probe_resources(view, ledger)

        reachable = frozenset({COORDINATE_BY_RESPONSIBILITY[Responsibility.INTERFACE]})
        depth = 0
        remaining = cues
        cleared: list[Cue] = []
        changed: list[str] = []
        acted: Responsibility | None = None
        for _ in range(planned_rounds(cues, budget)):
            if not ledger.query(1):
                break
            depth += 1
            outcome = apply_repairs(
                remaining,
                surface=SURFACE_RESPONSIBILITIES,
                reachable_coordinates=reachable,
            )
            cleared.extend(outcome.cleared)
            changed.extend(outcome.changed_coordinates)
            if acted is None or outcome.changed_coordinates:
                acted = outcome.acted_on
            remaining = outcome.remaining

        changed_coordinates = tuple(dict.fromkeys(changed))
        closures = public_closures(view)
        stale = stale_closures_survive(closures, changed=changed_coordinates, reopened=())
        reframed = bool(changed_coordinates)
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=reframed,
            responsibility_family=acted.value if acted else "",
            target_coordinates=axis_answer(changed_coordinates) if reframed else (),
            reopened=(),
            root_solved=solved(cues, remaining),
            abstained=abstains(cues, remaining, changed_coordinates),
            max_recursion_depth=depth,
            resources=ledger.usage,
            notes=(
                f"audit_rounds={depth} repaired="
                + ",".join(cue.cue_id for cue in cleared)
                + f" stale_survivors={sorted(stale)}"
            ),
        )


# --------------------------------------------------------------------------
# Baseline 4 — SCION-like dependency execution plan
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ScionLikeDependencyExecutionPlan:
    """An explicit staged plan that can be reopened — by stage.

    This baseline does have a dependency model and does reopen, which makes it
    the strongest comparison for H3. Its plan is ordered execution stages, so a
    change reopens the failing stage and everything after it. A real and
    defensible policy; it is simply not responsibility-directed, so it stales
    conclusions that never depended on what changed.
    """

    system_id: str = "scion_like_dependency_execution_plan"

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        budget = budget_for(view)
        ledger = ProbeLedger(budget)
        cues = extract_cues(view)
        _probe_resources(view, ledger)
        closures = public_closures(view)
        ledger.query(planned_rounds(cues, budget))

        reachable = frozenset(
            {COORDINATE_BY_RESPONSIBILITY[Responsibility.DECOMPOSITION]}
        )
        outcome = apply_repairs(
            cues, surface=SURFACE_RESPONSIBILITIES, reachable_coordinates=reachable
        )
        reopened = stage_reopen(closures, outcome.changed_coordinates)
        stale = stale_closures_survive(
            closures, changed=outcome.changed_coordinates, reopened=reopened
        )
        reframed = bool(outcome.changed_coordinates)
        acted = outcome.acted_on
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=reframed,
            responsibility_family=acted.value if acted else "",
            target_coordinates=(
                axis_answer(outcome.changed_coordinates) if reframed else ()
            ),
            reopened=reopened,
            root_solved=solved(cues, outcome.remaining),
            abstained=abstains(
                cues, outcome.remaining, outcome.changed_coordinates
            ),
            max_recursion_depth=1 + (1 if reopened else 0),
            resources=ledger.usage,
            notes=(
                f"plan_stages={len(closures)} reopened_by_stage={list(reopened)} "
                f"stale_survivors={sorted(stale)}"
            ),
        )


# --------------------------------------------------------------------------
# Baseline 5 — IRIS-like information-state revision
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class IrisLikeInformationStateRevision:
    """Revise the claim/information state. K only: no W, no M.

    It maintains an explicit, revisable state — more than a static workflow
    does — and it declares a revision when the claim set is internally
    inconsistent. The revision lands on `K.CLAIMS`, the only coordinate it has.
    On a genuine representation case it can name the responsibility and still
    not repair it, which is the point: the label is not the mechanism, the
    coordinate is.
    """

    system_id: str = "iris_like_information_state_revision"

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        budget = budget_for(view)
        ledger = ProbeLedger(budget)
        cues = extract_cues(view)
        _probe_resources(view, ledger)
        ledger.query(planned_rounds(cues, budget))

        outcome = apply_repairs(
            cues,
            surface=SURFACE_RESPONSIBILITIES,
            reachable_coordinates=frozenset({CLAIM_COORDINATE}),
        )
        # A claim-level inconsistency is the one thing a K-only reviser treats
        # as a revision of its own state rather than as acquisition. Gating on
        # the cue matters for H2: neither negative control exhibits one.
        inconsistency = next(
            (
                cue
                for cue in material_cues(cues)
                if cue.responsibility is Responsibility.REPRESENTATION
            ),
            None,
        )
        revised = inconsistency is not None
        unresolved = material_cues(outcome.remaining)
        acted = outcome.acted_on
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=revised,
            responsibility_family=(
                Responsibility.REPRESENTATION.value
                if revised
                else (acted.value if acted else "")
            ),
            target_coordinates=(CLAIM_COORDINATE,) if revised else (),
            reopened=(),
            root_solved=solved(cues, outcome.remaining),
            abstained=abstains(
                cues,
                outcome.remaining,
                (CLAIM_COORDINATE,) if revised else (),
            ),
            max_recursion_depth=1 if (outcome.cleared or revised) else 0,
            resources=ledger.usage,
            notes=(
                "K-only revision; unresolved="
                + ",".join(cue.cue_id for cue in unresolved)
            ),
        )


BASELINE_IDS: tuple[str, ...] = (
    "static_react_tool_workflow",
    "tree_search_iterative_research",
    "arex_like_recursive_audit_followup",
    "scion_like_dependency_execution_plan",
    "iris_like_information_state_revision",
)


def baseline_systems() -> tuple[
    StaticReactToolWorkflow,
    TreeSearchIterativeResearch,
    ArexLikeRecursiveAuditFollowup,
    ScionLikeDependencyExecutionPlan,
    IrisLikeInformationStateRevision,
]:
    """The five frozen baselines, in protocol order."""

    return (
        StaticReactToolWorkflow(),
        TreeSearchIterativeResearch(),
        ArexLikeRecursiveAuditFollowup(),
        ScionLikeDependencyExecutionPlan(),
        IrisLikeInformationStateRevision(),
    )


__all__ = [
    "BASELINE_IDS",
    "BUDGETS",
    "CLAIM_COORDINATE",
    "COORDINATE_BY_RESPONSIBILITY",
    "DEFAULT_BUDGET_CLASS",
    "FORMULATION_RESPONSIBILITIES",
    "SURFACE_RESPONSIBILITIES",
    "ArexLikeRecursiveAuditFollowup",
    "Budget",
    "Cue",
    "CueStrength",
    "IrisLikeInformationStateRevision",
    "ProbeLedger",
    "PublicClosure",
    "RepairOutcome",
    "ScionLikeDependencyExecutionPlan",
    "StaticReactToolWorkflow",
    "TreeSearchIterativeResearch",
    "abstains",
    "acted",
    "apply_repairs",
    "axis_answer",
    "baseline_systems",
    "budget_for",
    "cue_to_residual",
    "deterministic_rng",
    "extract_cues",
    "material_cues",
    "planned_rounds",
    "public_closures",
    "readable_resources",
    "solved",
    "stage_reopen",
    "stale_closures_survive",
]
