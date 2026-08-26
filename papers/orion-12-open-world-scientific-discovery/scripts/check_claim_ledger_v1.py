#!/usr/bin/env python3
"""Machine-check the P2 claim ledger against the manuscript and the archive.

The ledger (``protocol/CLAIM_LEDGER_V1.json``) is the binding between what the
manuscript *asserts* and what the committed evidence *supports*.  This command
refuses four distinct defect classes:

1. ``LEDGER_SENTENCE_MISSING`` -- a ledger claim marked ``ASSERTED`` whose
   sentence is no longer present in its manuscript region.
2. ``UNLEDGERED_CLAIM`` -- a sentence in a hard-fail region (abstract,
   conclusion) that asserts an outcome and is neither a ledger claim nor an
   explicitly reasoned non-claim.
3. ``ARTIFACT_MISSING`` / ``ARTIFACT_KEY_MISSING`` / ``NUMERIC_MISMATCH`` -- a
   ledger entry citing a path that does not exist, a key absent from it, or a
   manuscript number that disagrees with the archived value.
4. ``OVERSTATED_STRENGTH`` -- a claim labelled ``CONFIRMATORY`` whose support is
   ``NONE_YET``, or a ``NONE_YET`` claim not held at ``CANNOT_CHECK``.
5. ``DIGEST_MISMATCH`` -- a ``support_artifacts`` SHA-256 that does not appear
   in the manuscript sentence, or a 64-hex digest in that sentence that is not
   one of the bound artifact values.  Hex digests are excluded from numeric
   slots on purpose; this class is the binding that exclusion would otherwise
   skip.

Two deliberate design decisions, both documented so they can be vetoed rather
than discovered:

*Numeric slots are matched positionally, not literally.*  A stored sentence is
compared to the manuscript with its numbers replaced by a placeholder, and each
number slot is then bound **in order of appearance** to an artifact key and
compared to the archived value.  This is strictly stronger than string equality:
it survives a legitimate re-run that moves a number (the ledger does not need a
manual edit for every regenerated digit) while catching the defect string
equality cannot see -- a manuscript number that no longer matches the evidence
it cites.  Slot count must equal the declared binding count, so a sentence that
gains or loses a number still fails.

*Unledgered-claim detection hard-fails only where the ledger declares it.*
Abstract and conclusion are hard-fail.  Results prose and Limitations report
uncovered outcome sentences as ``INFO`` instead, because those regions are under
active revision; their ledgered sentences are still numerically hard-checked.

Exit codes: ``0`` clean, ``1`` ledger violations, ``2`` harness/IO error.  A
harness error is never reported as a pass -- "could not check" is not "fine".

Examples::

    python3 papers/orion-12-open-world-scientific-discovery/scripts/check_claim_ledger.py --check
    python3 papers/orion-12-open-world-scientific-discovery/scripts/check_claim_ledger.py --emit-sentences abstract
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PAPER_DEFAULT = Path(__file__).resolve().parents[1]
LEDGER_RELATIVE = Path("protocol") / "CLAIM_LEDGER_V1.json"

SUPPORT_TYPES = {
    "OFFLINE_MECHANISM",
    "EXTERNAL_OFFICIAL",
    "EXTERNAL_DECLARED_DEVIATION",
    "NONE_YET",
}
STRENGTHS = {"CONFIRMATORY", "DESCRIPTIVE", "CANNOT_CHECK"}
MANUSCRIPT_STATUSES = {"ASSERTED", "NOT_ASSERTED_ARCHIVED_ONLY"}

NUMBER_SLOT = "\u2588NUM\u2588"

# A standalone number.  Three guards, each earning its place:
#   ``(?<![A-Za-z0-9_.])``  -- rejects the tail of an identifier and the
#                              fractional part of an already-matched decimal
#                              (``994444`` inside ``0.994444``).
#   ``(?<![A-Za-z0-9]-)``   -- rejects a hyphen that joins an identifier
#                              (``SHA-256``, ``P2-3``) while still admitting a
#                              leading minus sign (``-1.0``).
#   ``(?![A-Za-z0-9])``     -- rejects hex digests (``611808dc...``, ``2da5...``).
# The optional leading ``-`` is captured so that a negative archived value such
# as ``-1.0`` compares correctly rather than as its absolute value.  Thousands
# separators are part of the token: without this, ``1,677`` parses as two
# separate numbers and silently demands two bindings.
_NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_.])(?<![A-Za-z0-9]-)-?\d{1,3}(?:,\d{3})+(?![A-Za-z0-9])"
    r"|(?<![A-Za-z0-9_.])(?<![A-Za-z0-9]-)-?\d+(?:\.\d+)?(?![A-Za-z0-9])"
)

# SHA-256 hex strings.  Intentionally not numeric slots (see _NUMBER_RE);
# compared as exact identity against support_artifacts values.
_DIGEST_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")

# Outcome vocabulary.  A sentence in a hard-fail region matching any of these
# asserts a result and therefore needs a ledger entry.
_OUTCOME_VERBS = (
    r"reach(?:es|ed)?",
    r"attain(?:s|ed)?",
    r"achiev(?:es|ed)",
    r"improv(?:es|ed)",
    r"outperform(?:s|ed)",
    r"exceed(?:s|ed)",
    r"beat(?:s)?",
    r"support(?:s|ed)",
    r"demonstrat(?:es|ed)",
    r"show(?:s|ed|n)?",
    r"establish(?:es|ed)",
    r"yield(?:s|ed)",
    r"produc(?:es|ed)",
    r"confirm(?:s|ed)",
    r"makes no",
    r"expose(?:s|d)?",
    r"remains?",
    r"classifies",
    r"leaves",
)
_OUTCOME_RE = re.compile(r"\b(?:%s)\b" % "|".join(_OUTCOME_VERBS), re.IGNORECASE)

# Comparative-superiority vocabulary.  Never allowlistable.
_COMPARATIVE_RE = re.compile(
    r"\b(?:outperform\w*|superior\w*|better than|worse than|stronger than|"
    r"strongest|best|versus|compared with|improves? (?:on|over)|"
    r"state[- ]of[- ]the[- ]art)\b",
    re.IGNORECASE,
)

_ABBREVIATIONS = ("e.g.", "i.e.", "et al.", "cf.", "vs.", "Fig.", "Eq.", "Sec.")


class HarnessError(RuntimeError):
    """Raised for IO/parse problems -- reported as exit code 2, never as a pass."""


# --------------------------------------------------------------------------- #
# LaTeX normalization
# --------------------------------------------------------------------------- #

_STRIP_COMMANDS_WITH_ARG = (
    "cite",
    "ref",
    "label",
    "eqref",
    "citep",
    "citet",
    "subsubsection",
    "subsection",
    "section",
    "paragraph",
    "title",
    "author",
    "date",
)
_UNWRAP_COMMANDS = ("texttt", "textbf", "textit", "emph", "textsc", "text", "idt", "path")

# One level of brace nesting inside the value, for LaTeX thousands-grouping
# literals like ``{16{,}380}`` (render_suite_facts emits ``{,}`` so the comma
# survives math-mode spacing).  The raw value is then canonicalized to ``16,380``
# in load_macros so substituted prose forms a single number token.
_MACRO_DEF_RE = re.compile(
    r"\\(?:newcommand|renewcommand|providecommand)\s*\*?\s*\{?\\([A-Za-z]+)\}?\s*\{((?:[^{}]|\{[^{}]*\})*)\}"
)
# ``\Name{}`` -- an empty-brace invocation.  This is the idiom for splicing a
# generated value into prose (``\OfflineTaskCount{}-task``).  Formatting commands
# are not written this way, so an unresolved one is a real defect rather than
# noise: before macro resolution existed, the generic command strip deleted
# ``\OfflineTaskCount{}`` silently and the abstract read "a frozen -task index".
_VALUE_MACRO_USE_RE = re.compile(r"\\([A-Za-z]+)\{\}")


def _strip_comments(text: str) -> str:
    out = []
    for line in text.split("\n"):
        idx = 0
        while True:
            idx = line.find("%", idx)
            if idx == -1:
                out.append(line)
                break
            if idx > 0 and line[idx - 1] == "\\":
                idx += 1
                continue
            out.append(line[:idx])
            break
    return "\n".join(out)


def _drop_balanced(text: str, names: tuple[str, ...], keep_inner: bool) -> str:
    """Remove ``\\name{...}`` honouring nested braces.

    ``keep_inner`` keeps the argument body (unwrap) rather than deleting it.
    """
    pattern = re.compile(r"\\(?:%s)\s*\{" % "|".join(names))
    while True:
        match = pattern.search(text)
        if match is None:
            return text
        depth = 1
        i = match.end()
        while i < len(text) and depth:
            if text[i] == "\\":
                i += 2
                continue
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        if depth:
            raise HarnessError(f"unbalanced braces after {match.group(0)!r}")
        inner = text[match.end() : i - 1] if keep_inner else ""
        text = text[: match.start()] + inner + text[i:]


def _drop_environments(text: str, names: tuple[str, ...]) -> str:
    for name in names:
        pattern = re.compile(
            r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (re.escape(name), re.escape(name)),
            re.DOTALL,
        )
        text = pattern.sub(" ", text)
    return text


def load_macros(paper: Path, sources: Any) -> dict[str, str]:
    """Collect ``\\newcommand`` value definitions from generated macro files.

    The manuscript splices suite facts in as macros (``\\OfflineTaskCount{}``) so
    the prose cannot hardcode a task count.  The checker must resolve them to the
    same values, then bind those values to artifact keys -- which transitively
    verifies the generated macro file against the archive.
    """
    macros: dict[str, str] = {}
    for relative in sources or []:
        path = paper / "manuscript" / relative
        if not path.is_file():
            raise HarnessError(f"declared macro source missing: {path}")
        for match in _MACRO_DEF_RE.finditer(_read(path)):
            # Canonicalize ``{,}`` (LaTeX thousands separator) to a plain
            # comma so substituted prose carries ``16,380`` as one number
            # token; the numeric compare already strips grouping commas.
            macros[match.group(1)] = match.group(2).strip().replace("{,}", ",")
    return macros


def expand_macros(text: str, macros: dict[str, str]) -> tuple[str, set[str]]:
    """Substitute known value macros; report unresolved empty-brace invocations."""
    unresolved: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in macros:
            return macros[name]
        unresolved.add(name)
        return match.group(0)

    return _VALUE_MACRO_USE_RE.sub(replace, text), unresolved


def normalize_latex(text: str) -> str:
    """Reduce LaTeX source to comparable prose.

    Order matters: comments first, then argument-bearing commands, then unwraps,
    so that ``\\texttt{DESCRIPTIVE\\_ONLY}`` survives as ``DESCRIPTIVE_ONLY``.
    """
    text = _strip_comments(text)
    text = _drop_environments(text, ("tabular", "tabular*", "array"))
    text = _drop_balanced(text, _STRIP_COMMANDS_WITH_ARG, keep_inner=False)
    text = _drop_balanced(text, _UNWRAP_COMMANDS, keep_inner=True)
    text = re.sub(r"\\input\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\(?:begin|end)\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\(?:centering|small|hline|maketitle|noindent|par)\b", " ", text)
    text = text.replace("\\_", "_").replace("\\%", "%").replace("\\&", "&")
    text = text.replace("\\#", "#").replace("\\$", "$")
    text = re.sub(r"\$([^$]*)\$", r"\1", text)
    text = re.sub(r"``|''", '"', text)
    text = text.replace("--", "-").replace("~", " ")
    text = re.sub(r"\\[A-Za-z@]+\s*", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    """Split normalized prose into sentences.

    Never splits inside a decimal, because the split requires whitespace after
    the terminator.  Known abbreviations are protected before splitting.
    """
    guarded = text
    for i, abbrev in enumerate(_ABBREVIATIONS):
        guarded = guarded.replace(abbrev, f"\u0000{i}\u0000")
    parts = re.split(r"(?<=[.!?])\s+(?=[\"(]?[A-Z0-9])", guarded)
    out = []
    for part in parts:
        for i, abbrev in enumerate(_ABBREVIATIONS):
            part = part.replace(f"\u0000{i}\u0000", abbrev)
        part = part.strip()
        if part:
            out.append(part)
    return out


# --------------------------------------------------------------------------- #
# Region extraction
# --------------------------------------------------------------------------- #


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        raise HarnessError(f"cannot read {path}: {exc}") from exc


def extract_region(
    paper: Path,
    spec: dict[str, Any],
    name: str,
    macros: dict[str, str] | None = None,
    unresolved: set[str] | None = None,
) -> str:
    source = paper / "manuscript" / spec["file"]
    if not source.is_file():
        raise HarnessError(f"region {name!r} source missing: {source}")
    raw = _read(source)
    mode = spec["mode"]
    if mode == "ABSTRACT_ENV":
        match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, re.DOTALL)
        if match is None:
            raise HarnessError(f"region {name!r}: no abstract environment in {source}")
        body = match.group(1)
    elif mode == "SECTION":
        title = re.escape(spec["section"])
        match = re.search(
            r"\\section\{%s\}(.*?)(?=\\section\{|\\input\{|\\bibliographystyle|\\end\{document\})"
            % title,
            raw,
            re.DOTALL,
        )
        if match is None:
            raise HarnessError(
                f"region {name!r}: section {spec['section']!r} not found in {source}"
            )
        body = match.group(1)
    elif mode == "PROSE_FILE":
        body = _drop_environments(raw, ("figure", "figure*", "table", "table*"))
    else:
        raise HarnessError(f"region {name!r}: unknown mode {mode!r}")
    body, missing = expand_macros(body, macros or {})
    if unresolved is not None:
        unresolved.update(f"{name}:\\{n}" for n in missing)
    return normalize_latex(body)


# --------------------------------------------------------------------------- #
# Numeric slots and artifact resolution
# --------------------------------------------------------------------------- #


def numeric_slots(sentence: str) -> list[str]:
    return [m.group(0) for m in _NUMBER_RE.finditer(sentence)]


def blank_numbers(sentence: str) -> str:
    return _NUMBER_RE.sub(NUMBER_SLOT, sentence)


_MISSING = object()


_SELECTOR_RE = re.compile(r"^\[([^\]=]+)=([^\]]*)\]$")


def resolve_key(payload: Any, dotted: str) -> Any:
    """Resolve a dotted path into a JSON payload.

    Tolerates keys that themselves contain dots.  List elements may be addressed
    positionally (``tiers.3.required_n``) or, preferably, by a field match
    (``tiers.[tier=TIER_D_minimum_inferential].required_n``).  The field match is
    stable when a list gains or is reordered upstream, which a positional index is
    not -- an index silently starts pointing at a different record.
    """
    if not dotted:
        return payload
    if isinstance(payload, dict):
        parts = dotted.split(".")
        for take in range(len(parts), 0, -1):
            head = ".".join(parts[:take])
            if head in payload:
                rest = ".".join(parts[take:])
                found = resolve_key(payload[head], rest)
                if found is not _MISSING:
                    return found
        return _MISSING
    if isinstance(payload, list):
        head, _, rest = dotted.partition(".")
        selector = _SELECTOR_RE.match(head)
        if selector is not None:
            field, wanted = selector.group(1), selector.group(2)
            hits = [
                item
                for item in payload
                if isinstance(item, dict) and str(item.get(field)) == wanted
            ]
            if len(hits) != 1:
                return _MISSING
            return resolve_key(hits[0], rest)
        if head.isdigit() and int(head) < len(payload):
            return resolve_key(payload[int(head)], rest)
        return _MISSING
    return _MISSING


def numbers_equal(manuscript_token: str, archived: Any, scale: float = 1.0) -> bool:
    """Compare a manuscript number to an archived value.

    ``scale`` is the declared rendering factor: a rate archived as ``1.0`` and
    written as ``100%`` needs ``scale: 100``.  It must be declared per binding so
    it cannot be used to quietly reconcile a genuine mismatch.  Comparison is at
    the precision the manuscript itself writes, so ``0.70`` matches ``0.7``.
    """
    if isinstance(archived, bool) or not isinstance(archived, (int, float)):
        return False
    try:
        written = float(manuscript_token.replace(",", ""))
    except ValueError:
        return False
    manuscript_token = manuscript_token.replace(",", "")
    scaled = float(archived) * scale
    if "." in manuscript_token:
        places = len(manuscript_token.split(".")[1])
        return round(scaled, places) == written
    return scaled == written


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []
        self.info: list[str] = []

    def fail(self, code: str, detail: str) -> None:
        self.violations.append(f"{code}: {detail}")

    def note(self, code: str, detail: str) -> None:
        self.info.append(f"{code}: {detail}")


def _load_json(path: Path, label: str) -> Any:
    if not path.is_file():
        raise HarnessError(f"{label} missing: {path}")
    try:
        return json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise HarnessError(f"{label} is not valid JSON ({path}): {exc}") from exc


def _artifact_payloads(paper: Path, ledger: dict[str, Any], report: Report) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for alias, relative in ledger["artifacts"].items():
        path = paper / relative
        if not path.is_file():
            report.fail(
                "ARTIFACT_MISSING",
                f"artifact alias {alias!r} points at {relative} which does not exist; "
                f"fix the path in {LEDGER_RELATIVE} or archive the artifact",
            )
            continue
        try:
            payloads[alias] = json.loads(_read(path))
        except json.JSONDecodeError as exc:
            report.fail("ARTIFACT_UNPARSEABLE", f"{relative}: {exc}")
    return payloads


def _check_schema(ledger: dict[str, Any], report: Report) -> None:
    seen: set[str] = set()
    for claim in ledger["claims"]:
        cid = claim.get("claim_id", "<missing>")
        if cid in seen:
            report.fail("DUPLICATE_CLAIM_ID", f"{cid} appears more than once")
        seen.add(cid)
        if claim.get("support_type") not in SUPPORT_TYPES:
            report.fail(
                "BAD_SUPPORT_TYPE",
                f"{cid} support_type {claim.get('support_type')!r} not in {sorted(SUPPORT_TYPES)}",
            )
        if claim.get("strength") not in STRENGTHS:
            report.fail(
                "BAD_STRENGTH",
                f"{cid} strength {claim.get('strength')!r} not in {sorted(STRENGTHS)}",
            )
        if claim.get("manuscript_status") not in MANUSCRIPT_STATUSES:
            report.fail(
                "BAD_MANUSCRIPT_STATUS",
                f"{cid} manuscript_status {claim.get('manuscript_status')!r} invalid",
            )
        if claim.get("region") not in ledger["regions"]:
            report.fail("UNKNOWN_REGION", f"{cid} region {claim.get('region')!r} undeclared")
        if claim.get("manuscript_status") == "NOT_ASSERTED_ARCHIVED_ONLY" and not claim.get(
            "not_asserted_reason"
        ):
            report.fail(
                "MISSING_REASON",
                f"{cid} is NOT_ASSERTED_ARCHIVED_ONLY but gives no not_asserted_reason",
            )


def _check_strength(ledger: dict[str, Any], report: Report) -> None:
    for claim in ledger["claims"]:
        cid = claim["claim_id"]
        support = claim.get("support_type")
        strength = claim.get("strength")
        if strength == "CONFIRMATORY" and support == "NONE_YET":
            report.fail(
                "OVERSTATED_STRENGTH",
                f"{cid} is CONFIRMATORY with support_type NONE_YET; a claim without "
                "archived support cannot be confirmatory",
            )
        if support == "NONE_YET" and strength != "CANNOT_CHECK":
            report.fail(
                "OVERSTATED_STRENGTH",
                f"{cid} has support_type NONE_YET but strength {strength!r}; "
                "unsupported claims must be held at CANNOT_CHECK",
            )
        if strength == "CONFIRMATORY" and not claim.get("confirmatory_authority"):
            report.fail(
                "OVERSTATED_STRENGTH",
                f"{cid} is CONFIRMATORY but names no confirmatory_authority artifact",
            )


def _check_bindings(
    ledger: dict[str, Any],
    payloads: dict[str, Any],
    manuscript_sentences: dict[str, str],
    report: Report,
) -> None:
    """Check declared numbers against the archive.

    Numbers are read from the **manuscript occurrence** where one was matched,
    not from the ledger's stored copy.  Reading them from the stored copy would
    make the check vacuous: an edited manuscript number would still compare the
    ledger's own (stale) digits to the artifact and pass.  The stored copy is
    checked too, so a ledger that has rotted away from the archive also fails.
    """
    for claim in ledger["claims"]:
        cid = claim["claim_id"]
        stored_slots = numeric_slots(claim["sentence"])
        found = manuscript_sentences.get(cid)
        slots = numeric_slots(found) if found is not None else stored_slots
        source = "manuscript" if found is not None else "ledger (sentence not located)"
        bindings = claim.get("numeric_bindings", [])
        if len(slots) != len(bindings):
            report.fail(
                "SLOT_COUNT_MISMATCH",
                f"{cid} {source} sentence has {len(slots)} number slot(s) {slots} but "
                f"{len(bindings)} numeric_bindings; re-verify and update {LEDGER_RELATIVE}",
            )
            continue
        if found is not None and stored_slots != slots:
            report.fail(
                "LEDGER_STALE_NUMBER",
                f"{cid} ledger records {stored_slots} but the manuscript now writes {slots}; "
                f"re-verify the claim and update {LEDGER_RELATIVE}",
            )
        for index, (token, binding) in enumerate(zip(slots, bindings)):
            alias = binding["artifact"]
            key = binding["key"]
            if alias not in payloads:
                report.fail(
                    "ARTIFACT_MISSING",
                    f"{cid} slot {index} cites unresolvable artifact alias {alias!r}",
                )
                continue
            value = resolve_key(payloads[alias], key)
            if value is _MISSING:
                report.fail(
                    "ARTIFACT_KEY_MISSING",
                    f"{cid} slot {index} cites key {key!r} absent from {alias}; "
                    f"re-verify and update {LEDGER_RELATIVE}",
                )
                continue
            scale = float(binding.get("scale", 1))
            if not numbers_equal(token, value, scale):
                rendered = f"{value!r}" if scale == 1 else f"{value!r} x scale {scale:g}"
                report.fail(
                    "NUMERIC_MISMATCH",
                    f"{cid} slot {index} says {token} but {alias}:{key} archives "
                    f"{rendered}; the manuscript disagrees with its own evidence",
                )
        for support in claim.get("support_artifacts", []):
            alias = support["artifact"]
            key = support.get("key", "")
            if alias not in payloads:
                report.fail(
                    "ARTIFACT_MISSING",
                    f"{cid} support cites unresolvable artifact alias {alias!r}",
                )
                continue
            if key and resolve_key(payloads[alias], key) is _MISSING:
                report.fail(
                    "ARTIFACT_KEY_MISSING",
                    f"{cid} support cites key {key!r} absent from {alias}",
                )
        _check_digest_bindings(cid, claim, found, payloads, report)


def _check_digest_bindings(
    cid: str,
    claim: dict[str, Any],
    found: str | None,
    payloads: dict[str, Any],
    report: Report,
) -> None:
    """Bind 64-hex SHA-256 strings that numeric slots deliberately ignore."""

    expected: list[tuple[str, str, str]] = []
    for support in claim.get("support_artifacts", []):
        alias = support["artifact"]
        key = support.get("key", "")
        if alias not in payloads or not key:
            continue
        value = resolve_key(payloads[alias], key)
        if isinstance(value, str) and _DIGEST_RE.fullmatch(value.strip()):
            expected.append((alias, key, value.strip().lower()))
    if not expected:
        return
    expected_set = {digest for _, _, digest in expected}
    for source_name, text in (
        ("manuscript", found),
        ("ledger", claim["sentence"]),
    ):
        if text is None:
            continue
        observed = {match.group(0).lower() for match in _DIGEST_RE.finditer(text)}
        for alias, key, digest in expected:
            if digest not in observed:
                report.fail(
                    "DIGEST_MISMATCH",
                    f"{cid} {source_name} sentence is missing SHA-256 {digest} "
                    f"bound as {alias}:{key}",
                )
        extras = observed - expected_set
        if extras:
            report.fail(
                "DIGEST_MISMATCH",
                f"{cid} {source_name} sentence carries unbound SHA-256 "
                f"{sorted(extras)}; bind them as support_artifacts or remove them",
            )


def _check_presence(
    ledger: dict[str, Any], regions: dict[str, str], report: Report
) -> tuple[dict[str, set[str]], dict[str, str]]:
    """Verify ledger sentences appear in their region.

    Returns the blanked sentences matched per region (so the unledgered-claim
    scan knows what is already covered) and, per claim id, the actual manuscript
    sentence that matched -- which is what the numeric checks must read.
    """
    matched: dict[str, set[str]] = {name: set() for name in regions}
    located: dict[str, str] = {}
    region_index: dict[str, dict[str, str]] = {}
    for name, text in regions.items():
        index: dict[str, str] = {}
        for sentence in split_sentences(text):
            index.setdefault(blank_numbers(sentence), sentence)
        region_index[name] = index
    blanked_regions = {name: blank_numbers(text) for name, text in regions.items()}

    for claim in ledger["claims"]:
        cid = claim["claim_id"]
        region = claim.get("region")
        if region not in blanked_regions:
            continue
        blank = blank_numbers(claim["sentence"])
        present = blank in blanked_regions[region]
        if claim["manuscript_status"] == "NOT_ASSERTED_ARCHIVED_ONLY":
            if present:
                report.fail(
                    "STALE_NOT_ASSERTED",
                    f"{cid} is marked NOT_ASSERTED_ARCHIVED_ONLY but its sentence is now "
                    f"present in {region}; promote it to ASSERTED in {LEDGER_RELATIVE}",
                )
            continue
        if present:
            matched[region].add(blank)
            if blank in region_index[region]:
                located[cid] = region_index[region][blank]
            else:
                # Substring hit without a discrete sentence match: the numeric
                # check would otherwise fall back to comparing the ledger's own
                # digits to the archive, which is vacuous.  Refuse instead.
                report.fail(
                    "SENTENCE_NOT_ISOLABLE",
                    f"{cid} matches region {region!r} only as a substring, not as a whole "
                    "sentence, so its numbers cannot be read from the manuscript; store "
                    f"the sentence exactly as it is extracted (see --emit-sentences {region})",
                )
        else:
            hint = _nearest_sentence(claim["sentence"], region_index[region].values())
            detail = (
                f"{cid} sentence is no longer present in region {region!r}; the claim "
                f"changed or moved -- re-verify and update {LEDGER_RELATIVE}"
            )
            if hint:
                detail += f"\n    ledger:     {claim['sentence']}\n    manuscript: {hint}"
            report.fail("LEDGER_SENTENCE_MISSING", detail)
    return matched, located


def _nearest_sentence(target: str, candidates: Any) -> str | None:
    """Best-overlap manuscript sentence, to make a drift failure reviewable.

    A bare "sentence is missing" forces a manual sweep of the whole region.
    Printing what the manuscript now reads turns that into a guided review.  This
    only reports; nothing is auto-applied, so the ledger cannot self-heal.
    """
    wanted = {w for w in re.findall(r"[A-Za-z_]{4,}", target.lower())}
    if not wanted:
        return None
    best: tuple[float, str] | None = None
    for candidate in candidates:
        words = {w for w in re.findall(r"[A-Za-z_]{4,}", candidate.lower())}
        if not words:
            continue
        score = len(wanted & words) / len(wanted | words)
        if best is None or score > best[0]:
            best = (score, candidate)
    if best is None or best[0] < 0.4:
        return None
    return best[1]


def _asserts_outcome(sentence: str) -> bool:
    return bool(numeric_slots(sentence)) or bool(_OUTCOME_RE.search(sentence))


def _check_unledgered(
    ledger: dict[str, Any],
    regions: dict[str, str],
    matched: dict[str, set[str]],
    report: Report,
) -> None:
    allow: dict[str, dict[str, str]] = {name: {} for name in regions}
    for entry in ledger.get("non_claim_sentences", []):
        region = entry.get("region")
        if region not in allow:
            report.fail(
                "UNKNOWN_REGION",
                f"non_claim_sentences entry cites undeclared region {region!r}",
            )
            continue
        if not entry.get("reason"):
            report.fail(
                "MISSING_REASON",
                f"non-claim allowlist entry in {region!r} gives no reason",
            )
            continue
        sentence = entry["sentence"]
        if numeric_slots(sentence):
            report.fail(
                "ILLEGAL_ALLOWLIST",
                f"non-claim allowlist entry in {region!r} contains a number and therefore "
                "needs a ledger entry, not an allowlist entry",
            )
            continue
        if _COMPARATIVE_RE.search(sentence):
            report.fail(
                "ILLEGAL_ALLOWLIST",
                f"non-claim allowlist entry in {region!r} makes a comparative claim and "
                "therefore needs a ledger entry, not an allowlist entry",
            )
            continue
        allow[region][blank_numbers(sentence)] = entry["reason"]

    # A sentence recorded as a known defect is already accounted for -- by an
    # entry that must name a contradicting artifact, an owner and a required fix.
    # Reporting it a second time as unledgered would only add noise.
    for defect in ledger.get("known_defects", []):
        region = defect.get("region")
        if region in allow and defect.get("sentence"):
            allow[region][blank_numbers(defect["sentence"])] = "recorded as a known defect"

    for name, text in regions.items():
        hard = bool(ledger["regions"][name].get("hard_fail_unledgered"))
        for sentence in split_sentences(text):
            blank = blank_numbers(sentence)
            if blank in matched[name] or blank in allow[name]:
                continue
            if not _asserts_outcome(sentence):
                continue
            detail = (
                f"region {name!r} asserts an outcome with no ledger entry: {sentence!r}; "
                f"add a claim to {LEDGER_RELATIVE} or an explicitly reasoned "
                "non_claim_sentences entry"
            )
            if hard:
                report.fail("UNLEDGERED_CLAIM", detail)
            else:
                report.note("UNLEDGERED_CLAIM_ADVISORY", detail)


def _check_known_defects(
    ledger: dict[str, Any],
    regions: dict[str, str],
    payloads: dict[str, Any],
    report: Report,
    strict: bool,
) -> None:
    """Record manuscript sentences the archive contradicts.

    These are statements the evidence shows to be wrong or stale, in files this
    ledger does not own.  They are reported on every run so they cannot rot
    quietly, and ``--strict`` promotes them to violations once the owning lane
    has had the chance to fix them.  A defect entry must name a contradicting
    artifact that actually exists, and its sentence must still be present --
    otherwise the entry itself is stale and that is a violation.
    """
    for defect in ledger.get("known_defects", []):
        did = defect.get("defect_id", "<missing>")
        for required in ("region", "sentence", "contradicted_by", "owner", "required_fix"):
            if not defect.get(required):
                report.fail("DEFECT_INCOMPLETE", f"{did} is missing {required!r}")
                return
        region = defect["region"]
        if region not in regions:
            report.fail("UNKNOWN_REGION", f"{did} cites undeclared region {region!r}")
            continue
        blank = blank_numbers(defect["sentence"])
        if blank not in blank_numbers(regions[region]):
            report.fail(
                "STALE_DEFECT_ENTRY",
                f"{did} records a defective sentence that is no longer in {region!r}; "
                f"the manuscript was fixed -- remove the entry from {LEDGER_RELATIVE}",
            )
            continue
        alias = defect["contradicted_by"]["artifact"]
        key = defect["contradicted_by"].get("key", "")
        if alias not in payloads:
            report.fail("ARTIFACT_MISSING", f"{did} cites unresolvable artifact {alias!r}")
            continue
        if key and resolve_key(payloads[alias], key) is _MISSING:
            report.fail(
                "ARTIFACT_KEY_MISSING",
                f"{did} cites key {key!r} absent from {alias}; the contradiction is "
                "unproven as written",
            )
            continue
        if _COMPARATIVE_RE.search(defect["sentence"]):
            # A defect entry records a statement the archive contradicts, and it
            # suppresses the unledgered scan for that sentence.  That is
            # acceptable for an under-claim.  For a comparative-superiority
            # sentence it would park an over-claim as a "known issue" instead of
            # failing it, which is the one outcome this ledger exists to prevent.
            report.fail(
                "ILLEGAL_DEFECT",
                f"{did} records a comparative-superiority sentence as a known defect: "
                f"{defect['sentence']!r}. An over-claim must be removed from the "
                "manuscript, not recorded and tolerated.",
            )
            continue
        detail = (
            f"{did}: {region} states {defect['sentence']!r}, which {alias}:{key} "
            f"contradicts. Owner: {defect['owner']}. Required fix: {defect['required_fix']}"
        )
        if strict:
            report.fail("KNOWN_DEFECT", detail)
        else:
            report.note("KNOWN_DEFECT_OPEN", detail)


def _check_task_count_agreement(
    paper: Path, ledger: dict[str, Any], payloads: dict[str, Any], report: Report
) -> None:
    agreement = ledger.get("task_count_agreement")
    if not agreement:
        return
    values: dict[str, Any] = {}
    for entry in agreement:
        alias = entry["artifact"]
        key = entry["key"]
        if alias not in payloads:
            report.fail("ARTIFACT_MISSING", f"task-count agreement alias {alias!r} unresolvable")
            return
        value = resolve_key(payloads[alias], key)
        if value is _MISSING:
            report.fail(
                "ARTIFACT_KEY_MISSING",
                f"task-count agreement key {key!r} absent from {alias}",
            )
            return
        values[f"{alias}:{key}"] = value
    distinct = set(values.values())
    if len(distinct) > 1:
        report.fail(
            "TASK_COUNT_DISAGREEMENT",
            f"declared task counts disagree across artifacts: {values}; the world and the "
            "results summary describe different suites",
        )


def run_check(paper: Path, strict: bool = False) -> tuple[int, Report]:
    ledger = _load_json(paper / LEDGER_RELATIVE, "claim ledger")
    for required in ("schema_version", "regions", "artifacts", "claims"):
        if required not in ledger:
            raise HarnessError(f"claim ledger missing required field {required!r}")
    report = Report()
    _check_schema(ledger, report)
    macros = load_macros(paper, ledger.get("macro_sources"))
    unresolved: set[str] = set()
    regions = {
        name: extract_region(paper, spec, name, macros, unresolved)
        for name, spec in ledger["regions"].items()
    }
    for item in sorted(unresolved):
        report.fail(
            "UNRESOLVED_MACRO",
            f"{item} is invoked as a value macro but is not defined in any declared "
            "macro_sources file; it would otherwise be deleted silently and the claim "
            f"would lose a number. Add its source file to macro_sources in {LEDGER_RELATIVE}",
        )
    payloads = _artifact_payloads(paper, ledger, report)
    _check_strength(ledger, report)
    matched, located = _check_presence(ledger, regions, report)
    _check_bindings(ledger, payloads, located, report)
    _check_unledgered(ledger, regions, matched, report)
    _check_known_defects(ledger, regions, payloads, report, strict)
    _check_task_count_agreement(paper, ledger, payloads, report)
    return (1 if report.violations else 0), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the ledger (default)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="promote recorded known_defects from advisory notes to violations",
    )
    parser.add_argument(
        "--paper-root",
        type=Path,
        default=PAPER_DEFAULT,
        help="paper directory to check (tests point this at a fixture copy)",
    )
    parser.add_argument(
        "--emit-sentences",
        metavar="REGION",
        help="print normalized sentences for a region instead of checking",
    )
    args = parser.parse_args(argv)
    paper = args.paper_root.resolve()

    try:
        if args.emit_sentences:
            ledger = _load_json(paper / LEDGER_RELATIVE, "claim ledger")
            spec = ledger["regions"].get(args.emit_sentences)
            if spec is None:
                raise HarnessError(f"unknown region {args.emit_sentences!r}")
            macros = load_macros(paper, ledger.get("macro_sources"))
            region = extract_region(paper, spec, args.emit_sentences, macros)
            for sentence in split_sentences(region):
                print(sentence)
            return 0
        code, report = run_check(paper, strict=args.strict)
    except HarnessError as exc:
        print(f"CLAIM LEDGER HARNESS ERROR: {exc}", file=sys.stderr)
        print("could not check the ledger; this is not a pass", file=sys.stderr)
        return 2

    for note in report.info:
        print(f"info    {note}")
    for violation in report.violations:
        print(f"VIOLATION {violation}", file=sys.stderr)
    if code:
        print(
            f"\n{len(report.violations)} claim-ledger violation(s).",
            file=sys.stderr,
        )
    else:
        print(f"claim ledger clean ({len(report.info)} advisory note(s)).")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
