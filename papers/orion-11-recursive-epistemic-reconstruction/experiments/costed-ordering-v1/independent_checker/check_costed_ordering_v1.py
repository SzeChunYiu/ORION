#!/usr/bin/env python3
"""Independent checker for ORION11.COSTED_EPISTEMIC_ORDERING.v1.

Recomputes, from `raw_traces.jsonl` and the three frozen documents alone:
every score row, every gate G1-G7 under the non-compensatory composition in
which G6 dominates G3, the stratified percentile bootstrap, the Holm
adjustment across the registered gate family, and the terminal -- selected
only from the frozen set in EXPECTED_TERMINALS.json.

INDEPENDENCE
    Imports nothing from the candidate policies, the production scorer, the
    statistics module or any runner module. `--self-check` asserts this at
    runtime against the loaded interpreter.

EXIT CODES -- these are not a pass/fail axis
    0  CHECKED. The recomputed terminal is emitted. This includes every
       UNFAVOURABLE terminal: H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION
       is the outcome Theorem C predicts, and a checker that computed it
       successfully exits 0. Falsified is not an error.
    2  CHECKED, and the checker DISAGREES with a supplied RESULT_V1.json.
       Terminal CANNOT_CHECK__CHECKER_DISAGREEMENT.
    3  COULD NOT CHECK. Missing, contaminated, non-decomposing or structurally
       incoherent traces; an unmeasured gate; a seed-sensitive verdict.

    "Could not check" is never reported as "checked and fine".

USAGE
    python3 check_costed_ordering_v1.py [TRACES] [--compare RESULT_V1.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

if __package__ in (None, ""):  # direct-script invocation
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

from independent_checker import _constants as K  # noqa: E402
from independent_checker import _compare as C  # noqa: E402
from independent_checker import _coverage as COV  # noqa: E402
from independent_checker import _faults as F  # noqa: E402
from independent_checker import _gates as G  # noqa: E402
from independent_checker import _load as L  # noqa: E402
from independent_checker import _terminal as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PACKET = os.path.dirname(HERE)


def independence_self_check() -> dict[str, object]:
    """Assert no forbidden module reached the interpreter."""
    offenders = sorted(
        name
        for name in sys.modules
        if any(fragment in name.lower() for fragment in K.FORBIDDEN_IMPORT_FRAGMENTS)
    )
    return {
        "must_not_import": list(K.FORBIDDEN_IMPORT_FRAGMENTS),
        "offending_modules": offenders,
        "independent": not offenders,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_costed_ordering_v1",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "traces",
        nargs="?",
        default=os.path.join(PACKET, "raw_traces.jsonl"),
        help="raw_traces.jsonl (default: the packet's own trace file)",
    )
    parser.add_argument(
        "--compare",
        metavar="RESULT_V1.json",
        default=None,
        help="compare the independent recomputation against a supplied result",
    )
    parser.add_argument(
        "--terminals",
        default=os.path.join(PACKET, "EXPECTED_TERMINALS.json"),
        help="frozen terminal set (terminals are selected only from this file)",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=K.BOOTSTRAP_SEED_DEFAULT,
        help=(
            "bootstrap seed. PROTOCOL.json declares a frozen seed but freezes no "
            f"value, so the checker defaults to {K.BOOTSTRAP_SEED_DEFAULT} and records "
            "the source in the output."
        ),
    )
    parser.add_argument("--resamples", type=int, default=K.BOOTSTRAP_RESAMPLES)
    parser.add_argument(
        "--seed-probes",
        type=int,
        default=K.SEED_PROBE_COUNT,
        help="extra seeds used to test whether the terminal is seed-stable (0 disables)",
    )
    parser.add_argument("--out", default=None, help="write the report JSON here instead of stdout")
    parser.add_argument("--quiet", action="store_true", help="suppress the stderr summary")
    return parser


def seed_probe(index, rows, base_seed, resamples, probes, terminal, frozen_ids):
    """Is the terminal stable under a seed the protocol never froze?"""
    if probes <= 0:
        return {"probed": False, "reason": "disabled", "seed_sensitive": False}
    observed = {}
    for offset in range(1, probes + 1):
        probe_seed = base_seed + offset * 7919
        scratch = F.Ledger()
        analysis = G.evaluate(index, rows, probe_seed, resamples, scratch)
        decision = T.select(analysis, scratch, frozen_ids)
        observed[probe_seed] = decision["terminal"]
    distinct = sorted({terminal, *observed.values()}, key=lambda x: (x is None, x))
    return {
        "probed": True,
        "base_seed": base_seed,
        "probe_terminals": observed,
        "distinct_terminals": distinct,
        "seed_sensitive": len(distinct) > 1,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ledger = F.Ledger()
    ledger.defect(
        "PROTOCOL.json statistics.interval_method declares a frozen bootstrap seed but "
        "no seed value appears in any frozen document. The checker used "
        f"{args.bootstrap_seed} and probed terminal stability across other seeds."
    )

    independence = independence_self_check()
    if not independence["independent"]:
        ledger.fault(
            F.FAULT_MALFORMED_TRACE,
            "checker independence violated: a forbidden module is loaded",
            independence["offending_modules"],
        )

    try:
        frozen_ids, frozen_classes = T.load_frozen_terminals(args.terminals)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        report = {
            "schema": "ORION.ORION11.CostedEpistemicOrdering.IndependentCheck.v1",
            "status": "CANNOT_CHECK",
            "terminal": None,
            "terminal_status": F.NO_FROZEN_TERMINAL,
            "error": f"frozen terminal set unreadable at {args.terminals}: {exc}",
            "exit_code": K.EXIT_CANNOT_CHECK,
        }
        _emit(report, args)
        return K.EXIT_CANNOT_CHECK

    rows = L.load_traces(args.traces, ledger)

    # A row failing a per-row invariant is excluded from the index, which
    # would then present as a coverage hole and a pairing break as well. That
    # cascade buries the primary fault and, because the frozen CANNOT_CHECK
    # terminals map per fault class, would leave a well-defined fault with no
    # terminal. Stages are therefore gated: coverage runs only on a trace
    # whose rows all hold. The later stages are marked NOT_EVALUATED rather
    # than silently omitted, so "could not check" is never read as "checked".
    row_stage_clean = not ledger.refused
    if row_stage_clean:
        index = COV.index_rows(rows, ledger) if rows else None
        coverage = COV.check_coverage(index, ledger) if index else {}
    else:
        index = None
        coverage = {
            "status": "NOT_EVALUATED",
            "reason": "per-row invariants failed; coverage and pairing were not "
            "assessed, and their silence here is not a pass",
            "blocking_fault_classes": ledger.fault_classes(),
        }

    analysis: dict = {}
    decision: dict = {}
    probe: dict = {"probed": False, "reason": "not reached", "seed_sensitive": False}

    if index and not ledger.refused:
        analysis = G.evaluate(index, rows, args.bootstrap_seed, args.resamples, ledger)
        decision = T.select(analysis, ledger, frozen_ids)
        if not ledger.refused:
            probe = seed_probe(
                index,
                rows,
                args.bootstrap_seed,
                args.resamples,
                args.seed_probes,
                decision["terminal"],
                frozen_ids,
            )
            if probe["seed_sensitive"]:
                ledger.fault(
                    F.FAULT_SEED_SENSITIVE_VERDICT,
                    "the terminal changes with the bootstrap seed, and PROTOCOL freezes "
                    "no seed; a seed-dependent verdict is not a measured verdict",
                    probe["distinct_terminals"],
                )
                decision = T.select(analysis, ledger, frozen_ids)
    else:
        decision = T.select({"gates": {}}, ledger, frozen_ids)

    exit_code = K.EXIT_CANNOT_CHECK if ledger.refused else K.EXIT_CHECKED
    status = "CANNOT_CHECK" if ledger.refused else "CHECKED"

    comparison = None
    if args.compare:
        try:
            with open(args.compare, "r", encoding="utf-8") as handle:
                supplied = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            ledger.fault(
                F.FAULT_MALFORMED_TRACE,
                f"--compare target unreadable: {args.compare} ({exc})",
                args.compare,
            )
            exit_code, status = K.EXIT_CANNOT_CHECK, "CANNOT_CHECK"
        else:
            if analysis and decision:
                comparison = C.compare(analysis, decision, supplied)
                if comparison["n_fields_comparable"] == 0:
                    ledger.fault(
                        F.FAULT_MALFORMED_TRACE,
                        "the supplied result shares no comparable field with the "
                        "independent recomputation; the comparison is vacuous",
                        args.compare,
                    )
                    exit_code, status = K.EXIT_CANNOT_CHECK, "CANNOT_CHECK"
                elif comparison["n_disagreements"] > 0 and exit_code == K.EXIT_CHECKED:
                    exit_code, status = K.EXIT_DISAGREEMENT, "CHECKED__DISAGREEMENT"
                    decision = dict(decision)
                    decision["terminal"] = T.T_DISAGREEMENT
                    decision["terminal_status"] = "SELECTED"
                    decision["selection_reasoning"] = list(
                        decision.get("selection_reasoning", [])
                    ) + [
                        "The independent recomputation disagrees with the supplied "
                        "result on "
                        + ", ".join(comparison["disagreeing_fields"])
                        + ". No claim may be read from a disputed computation."
                    ]
            else:
                ledger.fault(
                    F.FAULT_MALFORMED_TRACE,
                    "cannot compare: the independent recomputation did not complete",
                    args.compare,
                )
                exit_code, status = K.EXIT_CANNOT_CHECK, "CANNOT_CHECK"

    report = {
        "schema": "ORION.ORION11.CostedEpistemicOrdering.IndependentCheck.v1",
        "successor_id": "ORION11.COSTED_EPISTEMIC_ORDERING.v1",
        "scientific_authority_delta": "NONE",
        "status": status,
        "exit_code": exit_code,
        "exit_code_semantics": {
            "0": "CHECKED -- includes every unfavourable terminal; falsified is not an error",
            "2": "CHECKED and DISAGREES with the supplied result",
            "3": "COULD NOT CHECK -- never reported as checked and fine",
        },
        "traces": os.path.abspath(args.traces),
        "independence": independence,
        "terminal": decision.get("terminal"),
        "terminal_status": decision.get("terminal_status"),
        "terminal_class": frozen_classes.get(decision.get("terminal")),
        "decision": decision,
        "bootstrap": {
            "resamples": args.resamples,
            "seed": args.bootstrap_seed,
            "seed_source": K.BOOTSTRAP_SEED_SOURCE_DEFAULT
            if args.bootstrap_seed == K.BOOTSTRAP_SEED_DEFAULT
            else "OPERATOR_SUPPLIED",
            "method": "stratified percentile bootstrap, paired by world identity",
            "seed_stability_probe": probe,
        },
        "coverage": coverage,
        "analysis": analysis,
        "comparison": comparison,
        "protocol_defects": ledger.protocol_defects,
        "faults": ledger.faults,
        "warnings": ledger.warnings,
        "refusal_classes": ledger.fault_classes(),
    }
    _emit(report, args)
    return exit_code


def _emit(report: dict, args) -> None:
    text = json.dumps(report, indent=2, sort_keys=False, default=str)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    if args.quiet:
        return
    print(
        f"[independent-checker] status={report['status']} "
        f"exit={report['exit_code']} terminal={report.get('terminal')} "
        f"faults={len(report.get('faults', []))} warnings={len(report.get('warnings', []))}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    raise SystemExit(main())
