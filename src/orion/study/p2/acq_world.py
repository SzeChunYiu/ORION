"""Constructed reproduction of the V2 Wide acquisition failure.

`P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json` is the terminal negative this
world exists to model. Its shape, not just its headline, is what has to be
reproduced:

* three provider calls per task, twenty results per call, a twenty-candidate cap;
* ``mean_candidates_returned = 20.0`` for **both** arms — the queries were *not*
  coming back empty;
* ``avg_recall`` 0.051422 (baseline) and 0.044213 (candidate);
* ``zero_hit_tasks`` 19 of 24 for both;
* per-task gold sets of 2 to 21 documents;
* and, in `P2_V2_WIDE_BOUNDED_STAGE_DIAGNOSTIC_2026-08-18.json`, tasks where a
  gold identifier *was* returned by the provider and still did not survive into
  the final twenty.

So the failure under repair is not an empty result set. It is twenty
topically-adjacent wrong records filling a hard cap, on nineteen tasks in
twenty-four. This module builds the smallest corpus in which that is literally
what happens, so a successor mechanic can be measured against the failure rather
than against a story about it.

Three properties are carried over from the already-validated lexical-echo world
(`echo_world`) rather than invented here, because inventing a fresh set of
favourable assumptions for a fresh mechanic is how a constructed study stops
being evidence:

1. *Apparatus vocabulary is frequent and non-discriminative.* Question framing
   words are sprayed across most non-gold documents, so their document frequency
   is genuinely high corpus-wide.
2. *Gold documents do not carry the question's apparatus words.* This is
   `echo_world`'s property 2 — a paper is relevant because of what it is about,
   not because it shares the asker's framing vocabulary — and it is the single
   load-bearing assumption of the `distinguishable` family. It is **assumed** of
   the live setting on the strength of `DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17`
   and is not established by anything here.
3. *The wrong records are topically adjacent, not random.* The neighbourhood of
   each task carries two of the topic's five content terms; gold carries three.
   The evidence separating them is therefore *coordination level* — how many
   distinct topic terms a record agrees with — which an additive term-frequency
   score does not read directly.

What is new here, and deliberately so, is the ``undistinguished`` family: a
control in which gold is built to be lexically **indistinguishable** from the
adjacent neighbourhood. It models the live possibility that the Wide gold
references simply are not separable by any surface-lexical mechanism. Every arm,
successor included, is pre-committed to be unable to lift recall there. Without
that family a positive result on the other families would silently imply the live
setting is repairable, which this study cannot show.

The world reuses `orion.study.p2.corpus` (`Document`, `Topic`, `DiscoveryWorld`,
`sha256_digest`) rather than standing up a parallel corpus type.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from .corpus import Document, DiscoveryWorld, Topic, sha256_digest

ACQ_WORLD_SCHEMA_VERSION = "orion.p2.open-world-acquisition-world.v1"

# --------------------------------------------------------------------------
# Frozen parameters. This exact object is hashed into the freeze twin and
# compared before any arm runs.
# --------------------------------------------------------------------------

FROZEN_SEED = 20260822

#: Question framing vocabulary. Small pool on purpose: apparatus vocabulary is a
#: few words used everywhere, which is what makes it non-discriminative. Every
#: entry survives `arb_runtime._STOPWORDS`, so these words really do enter a
#: shipped query rather than being filtered before it is formed.
SCAFFOLD_LEXICON: tuple[str, ...] = (
    "benchmark",
    "empirical",
    "evaluation",
    "reported",
    "baseline",
    "protocol",
)

#: Topic content vocabulary. Each term is shared by roughly a dozen topics, so no
#: single content term identifies a task and a one-term match is weak evidence.
DOMAIN_LEXICON: tuple[str, ...] = (
    "adsorption", "allosteric", "anisotropy", "astrocyte", "attractor",
    "bandgap", "baryon", "bilayer", "bioreactor", "birefringence",
    "calorimetry", "cavitation", "chelation", "chondrite", "clathrate",
    "cochlear", "colloid", "conductance", "coronagraph", "crystallite",
    "cyclotron", "decoherence", "dendrimer", "dielectrophoresis", "dislocation",
    "dosimetry", "ductility", "eccentricity", "electrolyte", "endosome",
    "epigenome", "escarpment", "eutectic", "exciton", "extremophile",
    "ferroelectric", "flavonoid", "fluvial", "fractionation", "gametophyte",
    "geomagnetic", "glycolysis", "granulocyte", "halophile", "hepatocyte",
    "holography", "hydrogel", "hyperfine", "immunoassay", "interferometry",
    "ionosphere", "isotherm", "karyotype", "keratinocyte", "kinetochore",
    "lamellar", "leptonic", "lithification", "lyophilization", "macrophage",
    "magnetosphere", "martensite", "mesophase", "microtubule", "morphogen",
    "myelination", "nanowire", "nephron", "nucleoside", "olivine",
    "organoid", "osmolarity", "paleosol", "pericyte", "perovskite",
    "phagocyte", "photocathode", "piezoelectric", "planetesimal", "polaron",
    "porphyrin", "proteasome", "pyrolysis", "quiescence", "radiolysis",
    "reflectance", "rheology", "ribozyme", "saccade", "scintillator",
    "sialic", "spallation", "stoichiometry", "subduction", "supercritical",
    "surfactant", "telomerase", "thermistor", "titration", "tokamakite",
    "transducer", "ultracentrifuge", "vacuolar", "vesicular", "viscoelastic",
    "voxel", "wavefront", "xenolith", "ytterbium", "zirconia",
)

#: Alternate surface forms used by the two vocabulary-gap families. Disjoint from
#: `DOMAIN_LEXICON`, so a variant shares no token with the term it renames.
VARIANT_LEXICON: tuple[str, ...] = (
    "aggregatory", "bimodality", "coactivation", "delamination", "eigenstress",
    "flocculation", "geothermics", "hemodynamic", "isomerization", "junctional",
    "kinematics", "luminance", "metastability", "nucleophile", "oscillatory",
    "photolysis", "quenching", "reactivation", "sedimentology", "thermolysis",
    "ultrastructure", "vitrification", "waveform", "xerogel", "yielding",
    "zonation", "adiabaticity", "bioaccumulation", "capacitance", "dispersivity",
    "emissivity", "fractality", "granularity", "hysteresis", "inductance",
    "jitteriness", "kurtosity", "lability", "modularity", "nonlinearity",
    "opacity", "porosity", "quantization", "refractivity", "solvation",
    "tortuosity", "uniaxiality", "viscosity", "wettability", "xerophily",
)

#: Connective scientific filler present in every stratum and in no question, so
#: document length and generic vocabulary discriminate nothing and never enter a
#: query.
NEUTRAL_LEXICON: tuple[str, ...] = (
    "section", "discussion", "context", "summary", "material", "note",
    "regime", "setting", "estimate", "outcome", "procedure", "comparison",
    "background", "uncertainty", "presentation", "consideration", "account",
    "observation", "condition", "arrangement",
)

FAMILY_DISTINGUISHABLE = "distinguishable"
FAMILY_UNDISTINGUISHED = "undistinguished"
FAMILY_WELL_POSED = "well_posed"
FAMILY_VARIANT_GAP = "variant_gap"
FAMILY_NO_BRIDGE = "no_bridge"

FAMILY_SIZES: dict[str, int] = {
    FAMILY_DISTINGUISHABLE: 120,
    FAMILY_UNDISTINGUISHED: 40,
    FAMILY_WELL_POSED: 40,
    FAMILY_VARIANT_GAP: 40,
    FAMILY_NO_BRIDGE: 40,
}

FAMILY_ORDER: tuple[str, ...] = (
    FAMILY_DISTINGUISHABLE,
    FAMILY_UNDISTINGUISHED,
    FAMILY_WELL_POSED,
    FAMILY_VARIANT_GAP,
    FAMILY_NO_BRIDGE,
)

CONTENT_TERMS_PER_TASK = 5
SCAFFOLD_TERMS_PER_TASK = 2
#: Distinct topic terms a gold record carries. Three of five: a relevant paper
#: addresses the topic without reciting every term of the asker's question, which
#: is why a wide conjunction over the question's vocabulary is unsatisfiable.
GOLD_TERMS_PER_DOCUMENT = 3
#: Distinct topic terms an adjacent non-gold record carries.
NEIGHBOUR_TERMS_PER_DOCUMENT = 2
#: Distinct topic terms a `well_posed` gold record carries.
WELL_POSED_GOLD_TERMS = 4
GOLD_MIN = 3
GOLD_MAX = 6
NEIGHBOURS_PER_TASK = 24
BRIDGES_PER_TASK = 3
BACKGROUND_FILLERS = 1500
NEUTRALS_PER_ABSTRACT = 5
SCAFFOLD_DENSITY = 0.8
SCAFFOLD_DRAWS_PER_DOCUMENT = 2
SCAFFOLD_REPEATS = 2
NEIGHBOUR_TERM_REPEATS = 2
#: Fraction of a `variant_gap`/`no_bridge` task's gold written in variant terms.
VARIANT_GOLD_FRACTION = 0.5

#: Two question templates. Every connective word in them is in
#: `arb_runtime._STOPWORDS`, so the tokens a shipped derivation sees are exactly
#: the placeholders — which keeps the comparison about term *selection* rather
#: than about incidental English the templates happen to contain.
WIDE_QUESTION_TEMPLATE = (
    "I am looking for {s1} {c1} {c2} that {s2} {c3}; in particular the {s1} {s2} "
    "of {c4} and {c5} for {c1}."
)
WELL_POSED_QUESTION_TEMPLATE = (
    "I am looking for {c1} {c2} that {c3}; in particular the {c4} of {c5} and {c1}."
)

#: Preconditions on the generated corpus, evaluated before any query is issued.
MIN_SCAFFOLD_DF_FRACTION = 0.20
MAX_CONTENT_DF_FRACTION = 0.06
MIN_NEIGHBOURHOOD_SIZE = 20

PARAMETERS: dict[str, Any] = {
    "schema_version": ACQ_WORLD_SCHEMA_VERSION,
    "seed": FROZEN_SEED,
    "lexicons": {
        "scaffold": list(SCAFFOLD_LEXICON),
        "domain": list(DOMAIN_LEXICON),
        "variant": list(VARIANT_LEXICON),
        "neutral": list(NEUTRAL_LEXICON),
    },
    "families": dict(sorted(FAMILY_SIZES.items())),
    "documents": {
        "content_terms_per_task": CONTENT_TERMS_PER_TASK,
        "scaffold_terms_per_task": SCAFFOLD_TERMS_PER_TASK,
        "gold_terms_per_document": GOLD_TERMS_PER_DOCUMENT,
        "neighbour_terms_per_document": NEIGHBOUR_TERMS_PER_DOCUMENT,
        "well_posed_gold_terms": WELL_POSED_GOLD_TERMS,
        "gold_min": GOLD_MIN,
        "gold_max": GOLD_MAX,
        "neighbours_per_task": NEIGHBOURS_PER_TASK,
        "bridges_per_task": BRIDGES_PER_TASK,
        "background_fillers": BACKGROUND_FILLERS,
        "neutrals_per_abstract": NEUTRALS_PER_ABSTRACT,
        "scaffold_density": SCAFFOLD_DENSITY,
        "scaffold_draws_per_document": SCAFFOLD_DRAWS_PER_DOCUMENT,
        "scaffold_repeats": SCAFFOLD_REPEATS,
        "neighbour_term_repeats": NEIGHBOUR_TERM_REPEATS,
        "variant_gold_fraction": VARIANT_GOLD_FRACTION,
    },
    "question_templates": {
        FAMILY_DISTINGUISHABLE: WIDE_QUESTION_TEMPLATE,
        FAMILY_UNDISTINGUISHED: WIDE_QUESTION_TEMPLATE,
        FAMILY_WELL_POSED: WELL_POSED_QUESTION_TEMPLATE,
        FAMILY_VARIANT_GAP: WIDE_QUESTION_TEMPLATE,
        FAMILY_NO_BRIDGE: WIDE_QUESTION_TEMPLATE,
    },
    "world_preconditions": {
        "min_scaffold_df_fraction": MIN_SCAFFOLD_DF_FRACTION,
        "max_content_df_fraction": MAX_CONTENT_DF_FRACTION,
        "min_neighbourhood_size": MIN_NEIGHBOURHOOD_SIZE,
    },
}


def parameters_digest() -> str:
    """sha256 of the frozen parameter block, in the programme's canonical form."""

    return sha256_digest(PARAMETERS)


# --------------------------------------------------------------------------
# Tasks
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class AcquisitionTask:
    """One question and the complete gold set that answers it.

    `gold_doc_ids` is the whole ground truth and is applied host-side only.
    `content_terms`, `scaffold_terms` and `variant_terms` are retained for
    reporting and for the world preconditions; no arm is given them.
    """

    task_id: str
    family: str
    question: str
    gold_doc_ids: tuple[str, ...]
    neighbour_doc_ids: tuple[str, ...]
    content_terms: tuple[str, ...]
    scaffold_terms: tuple[str, ...]
    variant_terms: tuple[str, ...]
    topic_id: str

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "question": self.question,
            "gold_doc_ids": list(self.gold_doc_ids),
            "neighbour_doc_ids": list(self.neighbour_doc_ids),
            "content_terms": list(self.content_terms),
            "scaffold_terms": list(self.scaffold_terms),
            "variant_terms": list(self.variant_terms),
            "topic_id": self.topic_id,
        }


@dataclass(frozen=True)
class AcquisitionWorld:
    """The corpus, its topics and its tasks."""

    schema_version: str
    seed: int
    world: DiscoveryWorld
    tasks: tuple[AcquisitionTask, ...]

    @property
    def documents(self) -> tuple[Document, ...]:
        return self.world.documents

    def tasks_in(self, family: str) -> tuple[AcquisitionTask, ...]:
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


def _make_document(
    doc_id: str,
    title_words: list[str],
    abstract_words: list[str],
    concept_tags: tuple[str, ...],
    references: tuple[str, ...],
    rng: random.Random,
) -> Document:
    title = " ".join(word.capitalize() for word in title_words)
    abstract = " ".join(abstract_words)
    return Document(
        doc_id=doc_id,
        content_identity=f"work:{doc_id}",
        content_digest=sha256_digest({"title": title, "abstract": abstract}),
        version=1,
        title=title,
        abstract=abstract,
        venue=f"venue-{rng.randrange(1, 24):02d}",
        year=2016 + rng.randrange(0, 11),
        authors=(f"author-{rng.randrange(1, 900):03d}",),
        references=references,
        concept_tags=concept_tags,
        access_keys=(),
    )


def _neutrals(rng: random.Random, count: int = NEUTRALS_PER_ABSTRACT) -> list[str]:
    return list(rng.sample(NEUTRAL_LEXICON, count))


def _scaffold_spray(rng: random.Random) -> list[str]:
    """Corpus-wide apparatus vocabulary. Never applied to `distinguishable` gold.

    That asymmetry is `echo_world` property 2 carried over, not a convenience:
    it is what makes a question's framing vocabulary actively point away from the
    records that answer it.
    """

    if rng.random() >= SCAFFOLD_DENSITY:
        return []
    drawn = rng.sample(SCAFFOLD_LEXICON, SCAFFOLD_DRAWS_PER_DOCUMENT)
    return [term for term in drawn for _ in range(SCAFFOLD_REPEATS)]


def _rotating_subset(terms: tuple[str, ...], size: int, offset: int) -> tuple[str, ...]:
    """A deterministic `size`-subset of `terms`, rotating with `offset`.

    Rotation rather than sampling so every topic term appears in a comparable
    number of that task's records; a sampled subset would leave some terms
    carried by no gold document at all, and the task's recall would then depend on
    which term a query happened to pick.
    """

    return tuple(terms[(offset + step) % len(terms)] for step in range(size))


def _task_documents(
    task_index: int,
    family: str,
    content_terms: tuple[str, ...],
    scaffold_terms: tuple[str, ...],
    variant_terms: tuple[str, ...],
    rng: random.Random,
) -> tuple[list[Document], tuple[str, ...], tuple[str, ...]]:
    """Mint one task's gold set, adjacent neighbourhood and (where used) bridges."""

    prefix = f"T{task_index:04d}"
    documents: list[Document] = []
    gold_count = rng.randint(GOLD_MIN, GOLD_MAX)
    gold_ids: list[str] = []
    variant_of = dict(zip(content_terms, variant_terms)) if variant_terms else {}

    gold_terms_per_document = (
        WELL_POSED_GOLD_TERMS if family == FAMILY_WELL_POSED else GOLD_TERMS_PER_DOCUMENT
    )
    if family == FAMILY_UNDISTINGUISHED:
        gold_terms_per_document = NEIGHBOUR_TERMS_PER_DOCUMENT

    variant_gold = 0
    if family in (FAMILY_VARIANT_GAP, FAMILY_NO_BRIDGE):
        variant_gold = int(round(gold_count * VARIANT_GOLD_FRACTION))

    for index in range(gold_count):
        carried = _rotating_subset(content_terms, gold_terms_per_document, index)
        if index < variant_gold:
            carried = tuple(variant_of.get(term, term) for term in carried)
        # `undistinguished` gold is written exactly like an adjacent record: same
        # term count, same apparatus spray. Nothing lexical separates it.
        spray = _scaffold_spray(rng) if family == FAMILY_UNDISTINGUISHED else []
        abstract = list(carried) + spray + _neutrals(rng)
        rng.shuffle(abstract)
        documents.append(
            _make_document(
                f"{prefix}-gold{index}",
                list(carried[:2]) + _neutrals(rng, 1),
                abstract,
                tuple(sorted(set(carried))),
                (),
                rng,
            )
        )
        gold_ids.append(f"{prefix}-gold{index}")

    # Reference edges inside the gold set, so `D3_CITATION_NEIGHBORHOOD` is a real
    # route rather than a route that can never return anything.
    linked: list[Document] = []
    for position, document in enumerate(documents):
        successor = gold_ids[(position + 1) % len(gold_ids)]
        linked.append(
            Document(
                doc_id=document.doc_id,
                content_identity=document.content_identity,
                content_digest=document.content_digest,
                version=document.version,
                title=document.title,
                abstract=document.abstract,
                venue=document.venue,
                year=document.year,
                authors=document.authors,
                references=(successor,) if successor != document.doc_id else (),
                concept_tags=document.concept_tags,
                access_keys=document.access_keys,
            )
        )
    documents = linked

    neighbour_ids: list[str] = []
    for index in range(NEIGHBOURS_PER_TASK):
        carried = _rotating_subset(content_terms, NEIGHBOUR_TERMS_PER_DOCUMENT, index)
        apparatus = [
            term
            for term in scaffold_terms
            for _ in range(SCAFFOLD_REPEATS + 1)
        ]
        abstract = (
            [term for term in carried for _ in range(NEIGHBOUR_TERM_REPEATS)]
            + apparatus
            + _neutrals(rng)
        )
        rng.shuffle(abstract)
        doc_id = f"{prefix}-near{index}"
        documents.append(
            _make_document(
                doc_id,
                [carried[0], scaffold_terms[index % len(scaffold_terms)]],
                abstract,
                tuple(sorted(set(carried))),
                (),
                rng,
            )
        )
        neighbour_ids.append(doc_id)

    if family == FAMILY_VARIANT_GAP:
        for index in range(BRIDGES_PER_TASK):
            pair = content_terms[index % len(content_terms)]
            other = content_terms[(index + 1) % len(content_terms)]
            abstract = [
                pair,
                variant_of[pair],
                variant_of[pair],
                other,
                variant_of[other],
            ] + _neutrals(rng)
            rng.shuffle(abstract)
            documents.append(
                _make_document(
                    f"{prefix}-bridge{index}",
                    [pair, variant_of[pair]],
                    abstract,
                    tuple(sorted({pair, variant_of[pair], other, variant_of[other]})),
                    (),
                    rng,
                )
            )

    return documents, tuple(gold_ids), tuple(neighbour_ids)


def _filler_documents(rng: random.Random) -> list[Document]:
    documents: list[Document] = []
    for index in range(BACKGROUND_FILLERS):
        domain = list(rng.sample(DOMAIN_LEXICON, 3))
        abstract = domain + _neutrals(rng) + _scaffold_spray(rng)
        rng.shuffle(abstract)
        documents.append(
            _make_document(
                f"F{index:04d}-filler",
                domain[:2] + _neutrals(rng, 1),
                abstract,
                tuple(sorted(domain)),
                (),
                rng,
            )
        )
    return documents


def build_acquisition_world(seed: int = FROZEN_SEED) -> AcquisitionWorld:
    """Generate the world. Deterministic in `seed` and nothing else."""

    rng = random.Random(seed)
    documents: list[Document] = []
    tasks: list[AcquisitionTask] = []
    topics: list[Topic] = []

    plan: list[str] = []
    for family in FAMILY_ORDER:
        plan.extend([family] * FAMILY_SIZES[family])

    for task_index, family in enumerate(plan):
        content_terms = tuple(rng.sample(DOMAIN_LEXICON, CONTENT_TERMS_PER_TASK))
        scaffold_terms = tuple(rng.sample(SCAFFOLD_LEXICON, SCAFFOLD_TERMS_PER_TASK))
        variant_terms: tuple[str, ...] = ()
        if family in (FAMILY_VARIANT_GAP, FAMILY_NO_BRIDGE):
            variant_terms = tuple(rng.sample(VARIANT_LEXICON, CONTENT_TERMS_PER_TASK))

        task_documents, gold_ids, neighbour_ids = _task_documents(
            task_index, family, content_terms, scaffold_terms, variant_terms, rng
        )
        documents.extend(task_documents)

        template = (
            WELL_POSED_QUESTION_TEMPLATE
            if family == FAMILY_WELL_POSED
            else WIDE_QUESTION_TEMPLATE
        )
        fields = {f"c{i + 1}": term for i, term in enumerate(content_terms)}
        fields.update({f"s{i + 1}": term for i, term in enumerate(scaffold_terms)})
        question = template.format(**fields)

        topic_id = f"topic-{task_index:04d}"
        topics.append(Topic(topic_id, f"Topic {task_index:04d}", content_terms[:1]))
        tasks.append(
            AcquisitionTask(
                task_id=f"ACQ-{task_index:04d}",
                family=family,
                question=question,
                gold_doc_ids=gold_ids,
                neighbour_doc_ids=neighbour_ids,
                content_terms=content_terms,
                scaffold_terms=scaffold_terms,
                variant_terms=variant_terms,
                topic_id=topic_id,
            )
        )

    documents.extend(_filler_documents(rng))
    world = DiscoveryWorld(
        schema_version=ACQ_WORLD_SCHEMA_VERSION,
        seed=seed,
        documents=tuple(sorted(documents, key=lambda item: item.doc_id)),
        topics=tuple(topics),
    )
    return AcquisitionWorld(
        schema_version=ACQ_WORLD_SCHEMA_VERSION,
        seed=seed,
        world=world,
        tasks=tuple(tasks),
    )
