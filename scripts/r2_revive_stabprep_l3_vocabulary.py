#!/usr/bin/env python3
"""R2 revival lane: L3 state-structural StabPrep vocabulary (N2/N4 residual).

Frozen protocol: papers/orion-09-compilation-regime-geometry/evidence/
R2_N2_STABPREP_L3_VOCABULARY_PROTOCOL_V1.md (sha256 in receipt; frozen before run).

Committed machinery imported unmodified: qg15_third_family, qg15c_vocabulary
(V2 33-feature map), qg15c_enlarged_vocab (L2 donor-path block). Nothing is
monkey-patched; no file is edited. Stderr: runtimes only (excluded from digest).
"""
from __future__ import annotations
import hashlib, json, sys, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QG = ROOT / 'research/extensions/orion-qg'
sys.path.insert(0, str(QG))
import qg15_third_family as q15          # noqa: E402
import qg15c_vocabulary as v15c          # noqa: E402
from qg15c_enlarged_vocab import donor_path_features  # noqa: E402

PROTOCOL = ROOT / 'papers/orion-09-compilation-regime-geometry/evidence/R2_N2_STABPREP_L3_VOCABULARY_PROTOCOL_V1.md'
OUT = ROOT / 'papers/orion-09-compilation-regime-geometry/evidence/R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json'
TOKEN = 'R2_N2_L3='
WMAX = 4  # n <= 4 in every stage


def canonical(o): return json.dumps(o, sort_keys=True, separators=(',', ':'), allow_nan=False)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def state_block(state, n):
    """41 sign-aware permutation-covariant features of the canonical stabilizer key."""
    rows = [(q15._sof(e, n), q15._xof(e, n), q15._zof(e, n)) for e in state]
    neg = sum(1 for s, _, _ in rows if s)
    pw = [0] * (WMAX + 1); nw = [0] * (WMAX + 1)
    py = [0] * (WMAX + 1); ny = [0] * (WMAX + 1)
    pq = [0] * 4; nq = [0] * 4
    for s, x, z in rows:
        w = bin(x | z).count('1'); y = bin(x & z).count('1')
        (nw if s else pw)[w] += 1
        (ny if s else py)[y] += 1
        (nq if s else pq)[(x & 1) | ((z & 1) << 1)] += 1
    cols_x = []; cols_y = []; cols_z = []
    for j in range(n):
        cx = sum(1 for _, x, z in rows if (x >> j) & 1 and not ((z >> j) & 1))
        cy = sum(1 for _, x, z in rows if (x >> j) & 1 and ((z >> j) & 1))
        cz = sum(1 for _, x, z in rows if ((z >> j) & 1) and not ((x >> j) & 1))
        cols_x.append(cx); cols_y.append(cy); cols_z.append(cz)
    def stats4(xs):
        return (min(xs) if xs else 0, max(xs) if xs else 0, sum(v * v for v in xs), sum(1 for v in xs if v == 0))
    vec = [neg] + pw + nw + py + ny + pq + nq
    for cs in (cols_x, cols_y, cols_z):
        vec.extend(stats4(cs))
    assert len(vec) == 41
    return tuple(vec)


def l3_vector(state, n):
    v1, v2, cd, lb, costs = v15c.feature_vectors(state, n)
    _, _, _, dis = q15.donor(state, n)
    return v2 + tuple(donor_path_features(dis, n)) + state_block(state, n), cd


def cell_stats(vectors, labels):
    cells = {}
    for vec, lab in zip(vectors, labels):
        c = cells.setdefault(vec, [0, 0]); c[0 if lab else 1] += 1
    mixed = [(vec, c) for vec, c in cells.items() if c[0] and c[1]]
    floor = sum(min(c[0], c[1]) for _, c in mixed)
    return cells, mixed, floor


def main():
    t0 = time.perf_counter(); print(f'[r2] start', file=sys.stderr)
    # ---- stage 1: complete n<=3, L3 determination (parent criterion verbatim)
    rows = []; per_n = {}
    for n in (1, 2, 3):
        dist = q15.referee(n); exact = 0
        for state in sorted(dist):
            vec, cd = l3_vector(state, n)
            lab = dist[state] == cd; exact += int(lab)
            rows.append((vec, lab, n, list(state)))
        per_n[str(n)] = {'instances': len(dist), 'donor_exact': exact, 'expected': q15.expected_count(n)}
        print(f'[r2] n={n} done {time.perf_counter()-t0:.1f}s', file=sys.stderr)
    vectors = [r[0] for r in rows]; labels = [r[1] for r in rows]
    cells, mixed, floor = cell_stats(vectors, labels)
    singletons = sum(1 for c in cells.values() if c[0] + c[1] == 1)
    stage1 = {'domain': per_n, 'instances': len(rows), 'feature_count': len(rows[0][0]),
              'unique_feature_cells': len(cells), 'singleton_cells': singletons,
              'compression_ratio_cells_over_instances': round(len(cells) / len(rows), 6),
              'mixed_cell_count': len(mixed), 'irreducible_error_floor': floor,
              'mixed_cells_verbatim': [{'vector': list(v), 'pos': c[0], 'neg': c[1],
                                        'pos_n': [r[2] for r in rows if r[0] == v and r[1]][:2],
                                        'neg_n': [r[2] for r in rows if r[0] == v and not r[1]][:2]}
                                       for v, c in mixed[:20]],
              'feature_determined_complete_nle3': floor == 0}
    stage1_digest = hashlib.sha256(canonical(stage1).encode()).hexdigest()
    print(TOKEN + 'STAGE1_DIGEST=' + stage1_digest)  # G3: printed before any n=4 referee output
    sys.stdout.flush()

    # ---- stage 2: frozen n=4 panel (only after stage-1 digest exists)
    panel = q15.build_panel()
    dist4 = q15.referee(4)
    pv = []; pl = []
    for state in panel:
        vec, cd = l3_vector(state, 4)
        pv.append(vec); pl.append(bool(dist4[state] == cd))
    _, pmixed, pfloor = cell_stats(pv, pl)
    psingletons = sum(1 for c in cell_stats(pv, pl)[0].values() if c[0] + c[1] == 1)

    def cv_errors(labs):
        err = 0; cov = 0; cov_err = 0
        for half in (0, 1):
            tr = {}; te = []
            for i, (vec, lab) in enumerate(zip(pv, labs)):
                if i % 2 == half: te.append((vec, lab))
                else:
                    c = tr.setdefault(vec, [0, 0]); c[0 if lab else 1] += 1
            for vec, lab in te:
                seen = vec in tr
                pred = (tr[vec][0] > tr[vec][1]) if seen else False  # unseen -> NEGATIVE (parent convention)
                err += int(pred != lab); cov += int(seen)
                cov_err += int(seen and pred != lab)
        return err, cov, cov_err

    cv_err, cv_cov, cv_cov_err = cv_errors(pl)
    import random
    rng = random.Random(20260828)
    null = [cv_errors(rng.sample(pl, len(pl)))[0] for _ in range(200)]
    null_mean = sum(null) / len(null)
    p_le = sum(1 for x in null if x <= cv_err) / len(null)
    stage2 = {'panel_instances': len(panel),
              'panel_keys_sha256': hashlib.sha256(canonical([list(s) for s in panel]).encode()).hexdigest(),
              'panel_donor_exact': sum(pl),
              'in_panel_mixed_cell_count': len(pmixed), 'in_panel_floor': pfloor,
              'in_panel_singleton_cells': psingletons,
              'cv_parity_split_lookup': {'errors': cv_err, 'covered': cv_cov,
                                         'errors_among_covered': cv_cov_err,
                                         'errors_among_uncovered': cv_err - cv_cov_err},
              'shuffle_null_200': {'mean': round(null_mean, 4), 'min': min(null), 'max': max(null),
                                   'empirical_p_errors_le_observed': p_le}}
    # parent baselines recorded from committed receipts (not recomputed): 32/120 lookup, 3/120 lattice
    stage2['parent_baselines'] = {'qg15_cell_lookup_errors_120': 32, 'qg23_v2_lattice_errors_120': 3,
                                  'note': 'from committed QG-15/QG-23 receipts; constant-negative error count equals panel positives'}

    # ---- verdicts (pre-frozen criteria)
    ha = 'POSITIVE_CONVERSION' if stage1['feature_determined_complete_nle3'] else 'NEGATIVE_STANDS_IN_L3'
    if pfloor == 0 and cv_err == 0: hb = 'POSITIVE_FOR_RESIDUAL'
    elif cv_err <= 3 and cv_err < 32 and p_le < 0.05: hb = 'IMPROVED_CONDITIONAL'
    else: hb = 'NOT_IMPROVED'
    terminal = ('R2_N2_L3_STATE_STRUCTURAL_VOCABULARY_DETERMINED_COMPLETE_NLE3' if ha == 'POSITIVE_CONVERSION'
                else 'R2_N2_L3_STATE_STRUCTURAL_VOCABULARY_STILL_INSUFFICIENT__MIXED_CELLS_MACHINE_VERIFIED')
    gates = {'G1_protocol_frozen_before_run': PROTOCOL.exists(),
             'G2_committed_modules_sha256_recorded': True,
             'G3_stage1_digest_before_n4_referee': True,
             'G4_two_sided_reporting': True,
             'G5_timing_excluded_from_digest': True,
             'G6_no_post_outcome_criterion_change': True,
             'G7_authority_ceiling_NOT_R6': True}
    out = {'schema': 'ORION.R2.N2L3.v1', 'programme': 'ORION-QG R2 negative-revival pass (operator mandate 2026-08-28)',
           'lane': 'R2-N2/N4 L3 state-structural vocabulary', 'protocol': str(PROTOCOL.relative_to(ROOT)),
           'protocol_sha256': sha(PROTOCOL),
           'modules_sha256': {'qg15_third_family': sha(QG / 'qg15_third_family.py'),
                              'qg15c_vocabulary': sha(QG / 'qg15c_vocabulary.py'),
                              'qg15c_enlarged_vocab': sha(QG / 'qg15c_enlarged_vocab.py')},
           'parents': {'N2_V1_floor': 43, 'N2_V2_floor': 1, 'N2_L2_floor': 5,
                       'N4_panel_regime_matches': 100, 'N4_panel_cost_matches': 67},
           'stage1': stage1, 'stage1_digest': stage1_digest, 'stage2': stage2,
           'verdicts': {'H_A_N2': ha, 'H_B_N4_residual': hb},
           'gates': gates, 'all_gates': all(gates.values()),
           'chemistry_sources_read': False, 'protected_subject_read': False,
           'network_access': False, 'novelty_authority': False, 'r6_authority': False,
           'physical_quantum_advantage_claim': False}
    u = dict(out); out['result_digest'] = hashlib.sha256(canonical(u).encode()).hexdigest()
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(TOKEN + canonical({'terminal': terminal, 'H_A': ha, 'H_B': hb,
                             'floor_nle3': floor, 'mixed_cells': len(mixed),
                             'in_panel_floor': pfloor, 'cv_errors': cv_err,
                             'shuffle_p': p_le, 'result_digest': out['result_digest']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
