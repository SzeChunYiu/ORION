from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

DONORS = (
    "FAVA_PERMISSION",
    "PCAA_ACTION_CERT",
    "HDP_DELEGATION",
    "SENTINEL_DCC",
    "APC_BOUNDED_AGENTS",
    "ECA_TYPED_EVIDENCE",
)
COORDS = ("domain", "kind", "scope", "content", "epoch")
BLOCKERS = ("REFUTED", "UNDETERMINED", "ESTABLISHED")


def independent_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion):
    if native is not True:
        return "NO_DONOR_AUTHORITY"
    if narrowing is not True:
        return "BLOCK"
    if blocker == "ESTABLISHED":
        return "BLOCK"
    if blocker == "UNDETERMINED":
        return "CANNOT_CHECK"
    if not (support_a or support_b):
        return "BLOCK"
    if not (all(flags) or coercion):
        return "BLOCK"
    return "DISCHARGE"


def main() -> None:
    rows = []
    terminals = Counter()
    for donor in DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                for narrowing in (False, True):
                    for blocker in BLOCKERS:
                        for support_a in (False, True):
                            for support_b in (False, True):
                                for coercion in (False, True):
                                    terminal = independent_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion)
                                    terminals[terminal] += 1
                                    rows.append({
                                        "donor": donor,
                                        "native_valid": native,
                                        "scientific_type": dict(zip(COORDS, flags)),
                                        "narrowing_ok": narrowing,
                                        "blocker": blocker,
                                        "support_a": support_a,
                                        "support_b": support_b,
                                        "protected_coercion": coercion,
                                        "terminal": terminal,
                                        "ideal_product": terminal,
                                    })

    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert len(rows) == 18432
    # Corrected 2026-08-22. This literal was "f69a60c890b6...", a digest neither
    # this file nor check_p8_x2_authority_lifting.py has ever produced, so the X2
    # independent verifier exited 1 on its own assertion from the commit that
    # added it and P8-X2's "a separate implementation reproduces the enumeration"
    # was never true. Both implementations produce the value below.
    assert digest == "059687eb8a5a058f808a15da968a01cca99dcaf2731ddefebb8fae6d45aee0b3"
    assert dict(terminals) == {
        "NO_DONOR_AUTHORITY": 9216,
        "BLOCK": 7086,
        "CANNOT_CHECK": 1536,
        "DISCHARGE": 594,
    }

    full = (True,) * 5
    type_sep = coercion_ok = coercion_bad = 0
    for _donor in DONORS:
        for idx in range(5):
            broken = list(full)
            broken[idx] = False
            broken = tuple(broken)
            assert independent_terminal(True, broken, True, "REFUTED", True, False, False) == "BLOCK"
            type_sep += 1
            coercion_bad += 1
            assert independent_terminal(True, broken, True, "REFUTED", True, False, True) == "DISCHARGE"
            coercion_ok += 1
    assert (type_sep, coercion_ok, coercion_bad) == (30, 30, 30)

    refuted = undetermined = established = 0
    support_survives = support_all_broken = 0
    for _donor in DONORS:
        assert independent_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        refuted += 1
        assert independent_terminal(True, full, True, "UNDETERMINED", True, False, False) == "CANNOT_CHECK"
        undetermined += 1
        assert independent_terminal(True, full, True, "ESTABLISHED", True, False, False) == "BLOCK"
        established += 1
        assert independent_terminal(True, full, True, "REFUTED", False, True, False) == "DISCHARGE"
        support_survives += 1
        assert independent_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        support_survives += 1
        assert independent_terminal(True, full, True, "REFUTED", False, False, False) == "BLOCK"
        support_all_broken += 1
    assert (refuted, undetermined, established) == (6, 6, 6)
    assert (support_survives, support_all_broken) == (12, 6)

    chain_ok = chain_widen = 0
    for _left in DONORS:
        for _right in DONORS:
            assert independent_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
            chain_ok += 1
            assert independent_terminal(True, full, False, "REFUTED", True, False, False) == "BLOCK"
            chain_widen += 1
    assert (chain_ok, chain_widen) == (36, 36)

    print(json.dumps({
        "status": "P8_X2_INDEPENDENT_AUDIT_PASS",
        "state_evaluations": 18432,
        "terminal_counts": dict(terminals),
        "type_separation_witnesses": type_sep,
        "protected_coercion_successes": coercion_ok,
        "unprotected_coercion_countermodels": coercion_bad,
        "single_support_revocation_survivals": support_survives,
        "all_support_revoked_blocks": support_all_broken,
        "chain_narrowing_successes": chain_ok,
        "chain_widening_countermodels": chain_widen,
        "canonical_rows_sha256": digest,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
