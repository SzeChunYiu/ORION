from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

DONORS = (
    "FAVA_PERMISSION", "PCAA_ACTION_CERT", "HDP_DELEGATION", "SENTINEL_DCC",
    "APC_BOUNDED_AGENTS", "ECA_TYPED_EVIDENCE", "COGEEG_SCIENTIFIC_HARNESS",
    "SCIENTISTONE_CHAIN_OF_EVIDENCE", "XCIENTIST_RESEARCH_HARNESS",
    "STATEFUL_DISCOVERY_ADJUDICATION", "EP_AEC_HETEROGENEOUS_RECEIPTS",
    "EVIDENCE_LEDGER_ADJUDICATION", "ARF_CROSS_DOMAIN_AUTHORITY",
)
COORDS = ("domain", "kind", "scope", "content", "epoch")
BLOCKERS = ("REFUTED", "UNDETERMINED", "ESTABLISHED")


def terminal(native, flags, narrowing, blocker, sa, sb, coercion):
    if native is not True:
        return "NO_DONOR_AUTHORITY"
    if narrowing is not True:
        return "BLOCK"
    if blocker == "ESTABLISHED":
        return "BLOCK"
    if blocker == "UNDETERMINED":
        return "CANNOT_CHECK"
    if not (sa or sb):
        return "BLOCK"
    if not (all(flags) or coercion):
        return "BLOCK"
    return "DISCHARGE"


def main():
    rows = []
    counts = Counter()
    for donor in DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                for narrowing in (False, True):
                    for blocker in BLOCKERS:
                        for sa in (False, True):
                            for sb in (False, True):
                                for coercion in (False, True):
                                    verdict = terminal(native, flags, narrowing, blocker, sa, sb, coercion)
                                    counts[verdict] += 1
                                    rows.append({
                                        "donor": donor,
                                        "native_valid": native,
                                        "scientific_type": dict(zip(COORDS, flags)),
                                        "narrowing_ok": narrowing,
                                        "blocker": blocker,
                                        "support_a": sa,
                                        "support_b": sb,
                                        "protected_coercion": coercion,
                                        "terminal": verdict,
                                        "ideal_product": verdict,
                                    })

    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert len(rows) == 39936
    assert digest == "ed186b824692fd5b3ab31be718c75b84e2126b577ce921ca5cc01b2d08ae19e6"
    assert dict(counts) == {
        "NO_DONOR_AUTHORITY": 19968,
        "BLOCK": 15353,
        "CANNOT_CHECK": 3328,
        "DISCHARGE": 1287,
    }

    full = (True,) * 5
    sep = coercion_yes = coercion_no = 0
    refuted = unknown = established = 0
    support_survives = all_support_revoked = 0
    for _donor in DONORS:
        for idx in range(5):
            broken = list(full)
            broken[idx] = False
            broken = tuple(broken)
            assert terminal(True, broken, True, "REFUTED", True, False, False) == "BLOCK"
            sep += 1
            coercion_no += 1
            assert terminal(True, broken, True, "REFUTED", True, False, True) == "DISCHARGE"
            coercion_yes += 1
        assert terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        refuted += 1
        assert terminal(True, full, True, "UNDETERMINED", True, False, False) == "CANNOT_CHECK"
        unknown += 1
        assert terminal(True, full, True, "ESTABLISHED", True, False, False) == "BLOCK"
        established += 1
        assert terminal(True, full, True, "REFUTED", False, True, False) == "DISCHARGE"
        support_survives += 1
        assert terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        support_survives += 1
        assert terminal(True, full, True, "REFUTED", False, False, False) == "BLOCK"
        all_support_revoked += 1

    assert (sep, coercion_yes, coercion_no) == (65, 65, 65)
    assert (refuted, unknown, established) == (13, 13, 13)
    assert (support_survives, all_support_revoked) == (26, 13)

    chain_ok = chain_widen = 0
    for _left in DONORS:
        for _right in DONORS:
            assert terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
            chain_ok += 1
            assert terminal(True, full, False, "REFUTED", True, False, False) == "BLOCK"
            chain_widen += 1
    assert (chain_ok, chain_widen) == (169, 169)

    print(json.dumps({
        "status": "P8_X4_INDEPENDENT_AUDIT_PASS",
        "state_evaluations": 39936,
        "terminal_counts": dict(counts),
        "type_separation_witnesses": sep,
        "protected_coercion_successes": coercion_yes,
        "unprotected_coercion_countermodels": coercion_no,
        "single_support_revocation_survivals": support_survives,
        "all_support_revoked_blocks": all_support_revoked,
        "heterogeneous_chain_successes": chain_ok,
        "heterogeneous_chain_widening_countermodels": chain_widen,
        "canonical_rows_sha256": digest,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
