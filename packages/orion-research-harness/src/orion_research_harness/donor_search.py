"""Novelty claims must be preceded by a donor search, and fail closed without one.

Why this module exists
----------------------

The ORION-QG hostile-novelty lane QG-19 attacked six novelty claims this
programme had frozen, and **none survived**: two outright ``SUBSUMED``, three
``INSTANCE_OF_KNOWN_GENERAL``, one ``NEAREST_MISS``. The headline structural
criterion turned out to be Wolf's 1978 syndrome trellis for maximum-likelihood
decoding of linear block codes -- forty-eight years older than the claim.

Every one of those six freezes was authored **without literature access**, and
every one was wrong in the same direction. That is not six mistakes; it is one
mechanism with six instances, and a mechanism can be closed in code.

What the harness already did, and why it was not enough
-------------------------------------------------------

``governance_runtime`` sets ``grants_novelty_authority: False`` -- the harness
refuses to *hand out* novelty authority. But nothing stopped a protocol from
*asserting* a novelty claim having never searched for a parent. The exit was
guarded and the entrance was open.

So a novelty claim now carries a typed donor-search record, and this module
refuses the ones that cannot show their work. It deliberately mirrors
``corroboration`` : a claim about what evidence establishes must state what kind
of evidence it has, and weak evidence may not be presented as strong.

What this module does NOT do
----------------------------

It cannot establish that anything is novel, and neither can any search. A
completed search with nothing found is a statement about the queries that were
run, never a grant -- which is why ``NO_PRIOR_ART_FOUND`` is admissible only
with its full query log attached, and why ``verdict_grants_novelty`` does not
exist anywhere in this file.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

#: A prior source states the claim, or a strictly more general one, over our
#: stated domain. The claim loses all novelty.
SUBSUMED = "SUBSUMED"

#: A prior source covers a proper sub-domain. Novelty survives only outside it,
#: and the surviving sub-domain must be named.
SUBSUMED_IN_SPECIAL_CASE = "SUBSUMED_IN_SPECIAL_CASE"

#: The claim is a specialization of an established general result. Novelty is at
#: most the specialization, and the general result must be cited.
INSTANCE_OF_KNOWN_GENERAL = "INSTANCE_OF_KNOWN_GENERAL"

#: A prior source is close and must be cited and distinguished. Novelty survives,
#: narrowed.
NEAREST_MISS = "NEAREST_MISS"

#: The declared query families returned nothing that bears. NOT a novelty grant:
#: a statement about the searches run, usable only with the query log.
NO_PRIOR_ART_FOUND = "NO_PRIOR_ART_FOUND"

#: The source could not be retrieved or read. Recorded, never inferred -- and
#: never a verdict on a claim that asserts novelty, since nothing was checked.
CANNOT_ASSESS = "CANNOT_ASSESS"

VERDICTS = frozenset(
    {
        SUBSUMED,
        SUBSUMED_IN_SPECIAL_CASE,
        INSTANCE_OF_KNOWN_GENERAL,
        NEAREST_MISS,
        NO_PRIOR_ART_FOUND,
        CANNOT_ASSESS,
    }
)

#: Verdicts that remove or narrow novelty. Each must bind a verbatim passage:
#: a verdict against a source we cannot quote is an opinion, not a finding.
VERDICTS_REQUIRING_A_PASSAGE = frozenset(
    {SUBSUMED, SUBSUMED_IN_SPECIAL_CASE, INSTANCE_OF_KNOWN_GENERAL, NEAREST_MISS}
)

#: The three query families QG-19 froze. All three are mandatory, because the
#: killing source for C-A came from a donor field the lane's own attack vector
#: never named -- the direct query's phrasing hid it.
QUERY_FAMILIES = ("OWN_VOCABULARY", "DONOR_FIELD_TRANSLATION", "INVERTED_OR_SURVEY")


def validate_donor_search(record: Mapping[str, Any]) -> None:
    """Fail closed on a novelty claim that cannot show a donor search.

    `record` describes one claim. If it does not assert novelty, nothing is
    required. If it does, it must carry a verdict, the three query families, and
    -- for any verdict that narrows or removes novelty -- a verbatim passage.
    """
    if not isinstance(record, Mapping):
        raise TypeError("donor-search record must be an object")

    if not bool(record.get("asserts_novelty", False)):
        return

    verdict = record.get("verdict")
    if verdict not in VERDICTS:
        raise ValueError(
            f"verdict must be one of {sorted(VERDICTS)}; got {verdict!r}. A "
            "claim asserting novelty must state the outcome of a donor search: "
            "QG-19 attacked six such claims and none survived, so an unsearched "
            "novelty claim is not a default, it is a known failure mode."
        )

    families = record.get("query_families")
    if not isinstance(families, Sequence) or isinstance(families, (str, bytes)):
        raise ValueError(
            "query_families must be a sequence naming the families actually run"
        )
    missing = [name for name in QUERY_FAMILIES if name not in families]
    if missing:
        raise ValueError(
            f"donor search is missing query families {missing}; all of "
            f"{list(QUERY_FAMILIES)} are mandatory. QG-19's killing source came "
            "from a donor field its own attack vector never named, so the "
            "translated and inverted queries are what make an empty result "
            "credible rather than a phrasing artifact."
        )

    if verdict == CANNOT_ASSESS:
        raise ValueError(
            "CANNOT_ASSESS cannot stand as the verdict on a claim that asserts "
            "novelty. It records that the source could not be retrieved, so "
            "nothing was checked -- and 'we could not check, therefore it is "
            "new' is the exact inference this module exists to refuse. Either "
            "complete the search, or drop asserts_novelty and report the claim "
            "as unassessed."
        )

    if not record.get("query_log_ref"):
        raise ValueError(
            "a claim asserting novelty must bind query_log_ref. Naming the "
            "query families is a declaration that searches were run; the log is "
            "the evidence that they were, with the verbatim queries and their "
            "result counts. Without it the gate checks three strings."
        )

    if verdict in VERDICTS_REQUIRING_A_PASSAGE and not str(
        record.get("verbatim_passage", "")
    ).strip():
        raise ValueError(
            f"verdict {verdict} must bind a verbatim_passage. A verdict against "
            "a source we cannot quote is an opinion, not a finding; paraphrase "
            "is how a near-miss gets talked into a non-match."
        )


def describe(verdict: str) -> str:
    """One line stating what a verdict does and does not establish."""
    if verdict == SUBSUMED:
        return "prior art states the claim or a more general one: novelty removed"
    if verdict == SUBSUMED_IN_SPECIAL_CASE:
        return (
            "prior art covers a proper sub-domain: novelty survives only outside "
            "it, and that sub-domain must be named"
        )
    if verdict == INSTANCE_OF_KNOWN_GENERAL:
        return (
            "claim is a specialization of an established result: novelty is at "
            "most the specialization, and the general result must be cited"
        )
    if verdict == NEAREST_MISS:
        return "prior art is close: novelty survives, narrowed, and must distinguish"
    if verdict == NO_PRIOR_ART_FOUND:
        return (
            "declared searches returned nothing bearing; novelty NOT established "
            "-- this reports the queries run, not the state of the literature"
        )
    if verdict == CANNOT_ASSESS:
        return (
            "source unretrievable: recorded as unassessed, never inferred either "
            "way, and never a basis for asserting novelty"
        )
    raise ValueError(f"unknown donor-search verdict: {verdict}")
