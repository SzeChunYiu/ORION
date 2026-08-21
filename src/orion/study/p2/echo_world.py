"""Constructed reproduction of the lexical-echo candidate-generation failure.

`DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json` attributes the 0/600 Deep
zero-hit to candidate generation and names the mechanism:

    "needle questions whose surface lexicon echoes in wrong papers, e.g.
     'supplementary' in the question retrieving a title containing
     'Supplementary Orbit'"

This module builds the smallest world in which that sentence is literally true,
so a successor mechanic can be measured against the mechanism rather than
against a story about it. Every parameter is fixed by
`papers/paper-02-open-world-scientific-discovery/protocol/P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21.md`
and hashed into its JSON twin; `PARAMETERS` below is the block that gets hashed.

Three properties of the real failure are carried over, and each one is a design
decision here rather than an accident of generation:

1. *The apparatus word is frequent, the content word is not unique.* Content
   terms come from an 80-word domain lexicon shared across tasks, so no single
   content term identifies a needle. Apparatus words come from a 6-word pool
   sprayed across 60% of non-needle documents, so they are genuinely
   high-document-frequency corpus-wide.
2. *The needle does not contain the apparatus word.* A needle question says
   "supplementary" because that is where the number sits, not because the paper
   is about supplements. Needles are the only documents that never carry an
   incidental term, which is exactly what makes them unreachable by a mechanic
   that weights the apparatus word like a content word.
3. *The wrong paper matches on apparatus plus one content word.* Echo
   distractors are titled ``"{Incidental} {Content}"`` — the "Supplementary
   Orbit" shape — and repeat the apparatus word in their abstract.

The world reuses `orion.study.p2.corpus` (`Document`, `Topic`, `DiscoveryWorld`,
`sha256_digest`) rather than standing up a parallel corpus type: the completeness
argument for the denominator is that module's, and it should not be re-argued.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from .corpus import Document, DiscoveryWorld, Topic, sha256_digest

ECHO_WORLD_SCHEMA_VERSION = "orion.p2.lexical-echo-world.v1"

# --------------------------------------------------------------------------
# Frozen parameters. This exact object is hashed and compared against the
# digest recorded in the freeze document's JSON twin before any arm runs.
# --------------------------------------------------------------------------

FROZEN_SEED = 20260821

#: Document-apparatus words. Small pool on purpose: apparatus vocabulary is few
#: words used everywhere, which is what makes it non-discriminative.
INCIDENTAL_LEXICON: tuple[str, ...] = (
    "supplementary",
    "appendix",
    "figure",
    "panel",
    "addendum",
    "caption",
)

#: Ordinary scientific content words. A task's content terms are drawn from here,
#: so each is shared by roughly a dozen tasks and a hundred documents.
DOMAIN_LEXICON: tuple[str, ...] = (
    "orbit", "resonance", "manifold", "spectral", "turbulence",
    "lattice", "dendrite", "plasmon", "entropy", "cortex",
    "enzyme", "isotope", "quasar", "polymer", "glacier",
    "neutrino", "ribosome", "magnetar", "catalyst", "aerosol",
    "phonon", "synapse", "sediment", "corona", "tectonic",
    "protein", "hadron", "chloride", "nebula", "gradient",
    "capsid", "boson", "alloy", "meson", "biofilm",
    "fermion", "plankton", "quark", "epitope", "vortex",
    "soliton", "axion", "chirality", "dielectric", "mycelium",
    "permafrost", "radiance", "spinor", "tokamak", "viscosity",
    "wavelet", "xylem", "zeolite", "anomaly", "bifurcation",
    "coherence", "diffusion", "eigenmode", "fluorescence", "geodesic",
    "helicity", "impedance", "kurtosis", "luminosity", "monolayer",
    "nucleation", "oscillator", "percolation", "quadrupole", "relaxation",
    "sublimation", "thermocline", "ultrafast", "valence", "waveguide",
    "excimer", "yttrium", "zwitterion", "adsorbate", "brillouin",
)

#: Connective scientific filler present in every stratum, so generic vocabulary
#: and document length discriminate nothing.
NEUTRAL_LEXICON: tuple[str, ...] = (
    "analysis", "value", "number", "model", "estimate", "framework",
    "regime", "procedure", "setting", "evaluation", "comparison", "summary",
    "discussion", "background", "section", "material", "text", "note",
    "uncertainty", "presents", "context", "review", "outcome", "measurement",
)

FAMILY_ECHO = "echo"
FAMILY_NO_ECHO = "no_echo"
FAMILY_PARAPHRASE = "paraphrase_gap"

FAMILY_SIZES: dict[str, int] = {
    FAMILY_ECHO: 120,
    FAMILY_NO_ECHO: 60,
    FAMILY_PARAPHRASE: 40,
}

CONTENT_TERMS_PER_TASK = 4
INCIDENTAL_TERMS_PER_TASK = 2
NEIGHBOURS_PER_TASK = 6
ECHO_DISTRACTORS_PER_ECHO_TASK = 6
BACKGROUND_FILLERS = 500
NEUTRALS_PER_ABSTRACT = 6
INCIDENTAL_DENSITY = 0.6
INCIDENTAL_DRAWS_PER_DOCUMENT = 2
#: Fixed-point-free permutation of the domain lexicon used by `paraphrase_gap`.
#: 37 is coprime with 80, so the map is a single 80-cycle and no term maps to itself.
PARAPHRASE_OFFSET = 37

ECHO_QUESTION_TEMPLATE = (
    "Which analysis gives the {c1} {c2} {c3} {c4} value? The number I need is not in the "
    "main text: it appears in the {i1} material, and the {i1} section presents it as a "
    "{i2}, with the {i2} note stating the uncertainty."
)
NO_ECHO_QUESTION_TEMPLATE = (
    "Which analysis gives the {c1} {c2} {c3} {c4} value? The number I need is stated in the "
    "main text of the paper itself, with its uncertainty."
)

#: Precondition on the generated world, checked before any arm runs. The world is
#: only a reproduction of the named mechanism if apparatus words really are
#: non-discriminative and content words really are discriminative.
MIN_APPARATUS_DF_FRACTION = 0.12
MAX_CONTENT_DF_FRACTION = 0.05

PARAMETERS: dict[str, Any] = {
    "schema_version": ECHO_WORLD_SCHEMA_VERSION,
    "seed": FROZEN_SEED,
    "lexicons": {
        "incidental": list(INCIDENTAL_LEXICON),
        "domain": list(DOMAIN_LEXICON),
        "neutral": list(NEUTRAL_LEXICON),
    },
    "families": dict(sorted(FAMILY_SIZES.items())),
    "documents": {
        "content_terms_per_task": CONTENT_TERMS_PER_TASK,
        "incidental_terms_per_task": INCIDENTAL_TERMS_PER_TASK,
        "neighbours_per_task": NEIGHBOURS_PER_TASK,
        "echo_distractors_per_echo_task": ECHO_DISTRACTORS_PER_ECHO_TASK,
        "background_fillers": BACKGROUND_FILLERS,
        "neutrals_per_abstract": NEUTRALS_PER_ABSTRACT,
        "incidental_density": INCIDENTAL_DENSITY,
        "incidental_draws_per_document": INCIDENTAL_DRAWS_PER_DOCUMENT,
        "paraphrase_offset": PARAPHRASE_OFFSET,
    },
    "question_templates": {
        FAMILY_ECHO: ECHO_QUESTION_TEMPLATE,
        FAMILY_NO_ECHO: NO_ECHO_QUESTION_TEMPLATE,
        FAMILY_PARAPHRASE: ECHO_QUESTION_TEMPLATE,
    },
    "world_preconditions": {
        "min_apparatus_df_fraction": MIN_APPARATUS_DF_FRACTION,
        "max_content_df_fraction": MAX_CONTENT_DF_FRACTION,
    },
}


def parameters_digest() -> str:
    """sha256 of the frozen parameter block, in the programme's canonical form."""

    return sha256_digest(PARAMETERS)


# --------------------------------------------------------------------------
# Tasks
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EchoTask:
    """One needle question and the single document that answers it.

    `target_doc_id` is the whole ground truth. `content_terms` and
    `incidental_terms` are retained for reporting only — no arm is given them.
    """

    task_id: str
    family: str
    question: str
    target_doc_id: str
    content_terms: tuple[str, ...]
    incidental_terms: tuple[str, ...]
    topic_id: str

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "question": self.question,
            "target_doc_id": self.target_doc_id,
            "content_terms": list(self.content_terms),
            "incidental_terms": list(self.incidental_terms),
            "topic_id": self.topic_id,
        }


@dataclass(frozen=True)
class EchoWorld:
    """The corpus, its topics and its tasks."""

    schema_version: str
    seed: int
    world: DiscoveryWorld
    tasks: tuple[EchoTask, ...]

    @property
    def documents(self) -> tuple[Document, ...]:
        return self.world.documents

    def tasks_in(self, family: str) -> tuple[EchoTask, ...]:
        return tuple(task for task in self.tasks if task.family == family)

    @property
    def content_hash(self) -> str:
        return sha256_digest(
            {
                "schema_version": self.schema_version,
                "seed": self.seed,
                "world": self.world.as_json(),
                "tasks": [task.as_json() for task in self.tasks],
            }
        )


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------


def _paraphrase(term: str) -> str:
    """The fixed synonym map used by `paraphrase_gap`. Never a fixed point."""

    index = DOMAIN_LEXICON.index(term)
    return DOMAIN_LEXICON[(index + PARAPHRASE_OFFSET) % len(DOMAIN_LEXICON)]


def _sentence(words: list[str]) -> str:
    return " ".join(words)


def _make_document(
    doc_id: str,
    title_words: list[str],
    abstract_words: list[str],
    concept_tags: tuple[str, ...],
    rng: random.Random,
) -> Document:
    title = " ".join(word.capitalize() for word in title_words)
    abstract = _sentence(abstract_words)
    return Document(
        doc_id=doc_id,
        content_identity=f"work:{doc_id}",
        content_digest=sha256_digest({"title": title, "abstract": abstract}),
        version=1,
        title=title,
        abstract=abstract,
        venue=f"venue-{rng.randrange(1, 12):02d}",
        year=2018 + rng.randrange(0, 8),
        authors=(f"author-{rng.randrange(1, 400):03d}",),
        references=(),
        concept_tags=concept_tags,
        access_keys=(),
    )


def _incidental_spray(rng: random.Random) -> list[str]:
    """The corpus-wide apparatus vocabulary that makes those words non-discriminative.

    Applied to every non-needle document. Needles are excluded by construction:
    that asymmetry is property 2 of the module docstring, not a convenience.
    """

    if rng.random() >= INCIDENTAL_DENSITY:
        return []
    return list(rng.sample(INCIDENTAL_LEXICON, INCIDENTAL_DRAWS_PER_DOCUMENT))


def _neutrals(rng: random.Random, count: int = NEUTRALS_PER_ABSTRACT) -> list[str]:
    return list(rng.sample(NEUTRAL_LEXICON, count))


def _task_documents(
    task_index: int,
    family: str,
    content_terms: tuple[str, ...],
    incidental_terms: tuple[str, ...],
    rng: random.Random,
) -> tuple[list[Document], str, tuple[str, ...]]:
    """Mint one task's needle, neighbours and (for `echo`) echo distractors.

    Returns the documents, the needle's id, and the needle's concept tags — which
    are the paraphrased terms in the `paraphrase_gap` family, so the topic's
    relevance rule still resolves to the needle there.
    """

    prefix = f"T{task_index:04d}"
    documents: list[Document] = []

    written = (
        tuple(_paraphrase(term) for term in content_terms)
        if family == FAMILY_PARAPHRASE
        else content_terms
    )

    # --- needle: carries every content term, never an apparatus term.
    title_terms = list(rng.sample(written, 2))
    needle_id = f"{prefix}-needle"
    documents.append(
        _make_document(
            needle_id,
            title_terms + _neutrals(rng, 2),
            list(written) + _neutrals(rng),
            tuple(sorted(written)),
            rng,
        )
    )

    # --- topical neighbours: one per distinct pair, genuinely half on topic.
    pairs = [
        (written[a], written[b])
        for a in range(len(written))
        for b in range(a + 1, len(written))
    ]
    for index, (first, second) in enumerate(pairs[:NEIGHBOURS_PER_TASK]):
        unrelated = [
            term
            for term in rng.sample(DOMAIN_LEXICON, 6)
            if term not in written
        ][:2]
        abstract = [first, second, second] + unrelated + _neutrals(rng, 5)
        abstract += _incidental_spray(rng)
        documents.append(
            _make_document(
                f"{prefix}-near{index}",
                [first] + _neutrals(rng, 2),
                abstract,
                tuple(sorted({first, second, *unrelated})),
                rng,
            )
        )

    # --- echo distractors: the "Supplementary Orbit" shape.
    if family == FAMILY_ECHO:
        for index in range(ECHO_DISTRACTORS_PER_ECHO_TASK):
            apparatus = incidental_terms[index % len(incidental_terms)]
            content = written[index % len(written)]
            abstract = [apparatus, apparatus, apparatus, content] + _neutrals(rng, 5)
            abstract += _incidental_spray(rng)
            documents.append(
                _make_document(
                    f"{prefix}-echo{index}",
                    [apparatus, content],
                    abstract,
                    (content,),
                    rng,
                )
            )

    return documents, needle_id, tuple(sorted(written))


def _filler_documents(rng: random.Random) -> list[Document]:
    documents: list[Document] = []
    for index in range(BACKGROUND_FILLERS):
        domain = list(rng.sample(DOMAIN_LEXICON, 3))
        abstract = domain + _neutrals(rng) + _incidental_spray(rng)
        documents.append(
            _make_document(
                f"F{index:04d}-filler",
                domain[:2] + _neutrals(rng, 1),
                abstract,
                tuple(sorted(domain)),
                rng,
            )
        )
    return documents


def build_echo_world(seed: int = FROZEN_SEED) -> EchoWorld:
    """Generate the frozen world. Deterministic in `seed` and nothing else."""

    rng = random.Random(seed)
    documents: list[Document] = []
    tasks: list[EchoTask] = []
    topics: list[Topic] = []

    plan: list[str] = []
    for family in (FAMILY_ECHO, FAMILY_NO_ECHO, FAMILY_PARAPHRASE):
        plan.extend([family] * FAMILY_SIZES[family])

    for task_index, family in enumerate(plan):
        content_terms = tuple(rng.sample(DOMAIN_LEXICON, CONTENT_TERMS_PER_TASK))
        incidental_terms = tuple(
            rng.sample(INCIDENTAL_LEXICON, INCIDENTAL_TERMS_PER_TASK)
        )
        task_documents, needle_id, needle_tags = _task_documents(
            task_index, family, content_terms, incidental_terms, rng
        )
        documents.extend(task_documents)

        template = (
            NO_ECHO_QUESTION_TEMPLATE
            if family == FAMILY_NO_ECHO
            else ECHO_QUESTION_TEMPLATE
        )
        question = template.format(
            c1=content_terms[0],
            c2=content_terms[1],
            c3=content_terms[2],
            c4=content_terms[3],
            i1=incidental_terms[0],
            i2=incidental_terms[1],
        )
        topic_id = f"TOPIC-{task_index:04d}"
        topics.append(
            Topic(
                topic_id=topic_id,
                label=" ".join(needle_tags),
                required_concepts=needle_tags,
            )
        )
        tasks.append(
            EchoTask(
                task_id=f"TASK-{task_index:04d}",
                family=family,
                question=question,
                target_doc_id=needle_id,
                content_terms=content_terms,
                incidental_terms=incidental_terms,
                topic_id=topic_id,
            )
        )

    documents.extend(_filler_documents(rng))

    world = DiscoveryWorld(
        schema_version=ECHO_WORLD_SCHEMA_VERSION,
        seed=seed,
        documents=tuple(documents),
        topics=tuple(topics),
    )
    return EchoWorld(
        schema_version=ECHO_WORLD_SCHEMA_VERSION,
        seed=seed,
        world=world,
        tasks=tuple(tasks),
    )
