#!/usr/bin/env python3
"""GLM-5.3 attribution harvest: blinded packet preparation.

Rebuilds the frozen v2-protocol judge packets from the CURRENT main tree's
PROTECTED_SUITE_V1.json judge-visible fields, using the VERBATIM frozen prompts
(V1 ATTRIBUTION_PROMPT = control arm; v2 EXTRACTION_PROMPT = treatment arm),
imported from the frozen scripts (no retyping).

Emits packets/*.txt (one file = the exact full judge prompt) and
PREPARATION_RECEIPT.json (packet ids, sha256s, source map, sanitization rules,
protocol deviations). The source map is judge-invisible by construction: it is
written only into this receipt, which the blind judge never receives.
"""
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

REPO = Path('/projects/hep/fs9/scratch/scyiu-orion-ci/wtG53')
SUITE = REPO / 'papers/orion-15-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json'
PROTOCOL = REPO / 'papers/orion-15-self-orion/protocol/P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json'
V1 = REPO / 'scripts/run_p5_glm_attribution.py'
V2 = REPO / 'scripts/run_p5_glm_attribution_v2.py'
OUT = REPO / 'papers/orion-15-self-orion/evidence/glm-5.3-attribution-v2'
PKT = OUT / 'packets'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def sha_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


v1 = load(V1, 'v1run_harvest')
v2 = load(V2, 'v2run_harvest')
suite = json.loads(SUITE.read_text())
cases = suite['cases']
assert len(cases) == 24, len(cases)
FAMILIES = sorted(set(v2.LOCUS_TO_FAMILY.values()))

packets = []
guard_hits = []
exact_token_hits = []
for i, case in enumerate(cases, 1):
    symptom = case['visible_symptom']
    context = json.dumps(case['candidate_visible_context'], indent=2)
    for arm, tmpl, prefix in (
        ('control', v1.ATTRIBUTION_PROMPT, 'C'),
        ('treatment', v2.EXTRACTION_PROMPT, 'T'),
    ):
        pid = f'PKT-{prefix}-{i:02d}'
        text = (tmpl
                .replace('{CASE_ID}', pid)
                .replace('{VISIBLE_SYMPTOM}', symptom)
                .replace('{CONTEXT}', context))
        # sanitization guards on the FINAL judge-visible packet
        for forbidden, tag in (
            (case['root_cause_nonce'], 'root_cause_nonce'),
            ('P5-HC', 'source_case_id_prefix'),
            ('protected_root_cause', 'protected_field_root_cause'),
            ('root_cause_nonce', 'protected_field_nonce'),
            ('competing_cause_set', 'protected_field_competing_set'),
            ('allowed_change_surface', 'protected_field_change_surface'),
            ('protected_surface', 'protected_field_protected_surface'),
            ('success_rubric', 'protected_field_success_rubric'),
            ('harm_rubric', 'protected_field_harm_rubric'),
            ('negative_variant', 'protected_field_negative_variant'),
            ('motivating_tasks', 'protected_field_motivating_tasks'),
            ('replay_tasks', 'protected_field_replay_tasks'),
            ('fresh_tasks', 'protected_field_fresh_tasks'),
        ):
            if forbidden in text:
                guard_hits.append({'packet_id': pid, 'leak': tag})
        packets.append({
            'packet_id': pid,
            'arm': arm,
            'source_case_id': case['case_id'],
            'gold_root_cause': case['protected_root_cause'],
            'sha256': sha_text(text),
            'chars': len(text),
        })
        PKT.mkdir(parents=True, exist_ok=True)
        (PKT / f'{pid}.txt').write_text(text)
    # suite-level exact-token leakage check (independent verifier convention)
    vis = symptom + ' ' + json.dumps(case['candidate_visible_context'])
    for f in FAMILIES:
        if f in vis:
            exact_token_hits.append({'case_id': case['case_id'], 'family_token': f})

receipt = {
    'schema_version': 'orion.p5.glm-5.3-attribution-harvest.preparation.v1',
    'campaign_id': 'p5-glm-5.3-attribution-v2-harvest',
    'prepared_at_unix': time.time(),
    'prepared_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'judge_model': 'GLM-5.3 (claude-cn harness, glm-5.3)',
    'judge_mechanics': 'One fresh blind subagent per packet (general-purpose agent, no inherited context), spawned from the Mac-side claude-cn harness; judge receives ONLY the packet text.',
    'protocol_path': 'papers/orion-15-self-orion/protocol/P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json',
    'protocol_sha256': sha_file(PROTOCOL),
    'suite_path': 'papers/orion-15-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json',
    'suite_sha256': sha_file(SUITE),
    'v1_prompt_sha256': sha_text(v1.ATTRIBUTION_PROMPT),
    'extraction_prompt_sha256': sha_text(v2.EXTRACTION_PROMPT),
    'source_tree': 'origin/main @ ff0df7f2 (worktree wtG53, branch claude/glm53-attribution-harvest-20260828)',
    'packet_construction_rules': [
        'Population: all 24 cases of the frozen PROTECTED_SUITE_V1.json (unchanged on current main).',
        'Judge-visible fields per case: visible_symptom (verbatim) + candidate_visible_context (json.dumps indent=2), exactly as the frozen drivers format them.',
        'Control packet = verbatim V1 ATTRIBUTION_PROMPT (scripts/run_p5_glm_attribution.py) with placeholders substituted.',
        'Treatment packet = verbatim v2 EXTRACTION_PROMPT (scripts/run_p5_glm_attribution_v2.py) with placeholders substituted; Stage B mapping is deterministic code executed by the scorer, never by the judge.',
        'Packet order = suite order; packet ids PKT-C-01..24 (control) and PKT-T-01..24 (treatment).',
    ],
    'sanitization_rules_applied': [
        'Case ids P5-HC-NNN replaced by neutral PKT-{-C|-T}-NN ids so no paper/case identity is judge-visible.',
        'No file paths, no commit metadata, no authorship strings, no timestamps, no provenance headers in any packet (guarded: P5-HC, protected, competing, nonce all asserted absent).',
        'Protected suite fields (protected_root_cause, root_cause_nonce, competing_cause_set, motivating/replay/fresh tasks, change surfaces, rubrics) never enter packet construction; only visible_symptom and candidate_visible_context are read.',
        'Source map (packet_id -> case_id -> gold) exists ONLY in this receipt, written after packet construction and never shown to any judge.',
    ],
    'protocol_deviations': [
        'Judge substitution (the point of this harvest): frozen protocol requested_model glm-5.2 via z.ai endpoint; this harvest judges with GLM-5.3 (claude-cn harness, glm-5.3) via blind subagents. Note the frozen v2 run itself already recorded served_model glm-5.3 under the glm-5.2 alias, so the judge MODEL is unchanged; what changes is the judge HARNESS (subagent vs API call) and the enforced blindness.',
        'Case-id neutralization: frozen prompts embed {CASE_ID} = P5-HC-NNN; this harvest substitutes PKT-NNN to remove paper identity from judge-visible text (blinding hardening requested for this harvest).',
        'Serving parameters: temperature 0.0 and max_tokens are harness-managed in the subagent path and not settable per call; the frozen protocol values (0.0 / 4096 / 2048) cannot be enforced byte-exactly. Recorded, not hidden.',
        'Blindness enforcement is by prompt confinement: the subagent is instructed to answer only from the packet text and not to use tools; subagent tool access is not technically sandboxed. This is stronger than the frozen run (judge then could not be isolated from the colocated gold at all) but not a cryptographic guarantee.',
    ],
    'sanitization_guard_hits': guard_hits,
    'exact_family_token_in_judge_visible_fields': exact_token_hits,
    'packet_count': len(packets),
    'packets': packets,
    'source_map_withheld_from_judge': True,
}
(OUT / 'PREPARATION_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({
    'packets': len(packets),
    'guard_hits': guard_hits,
    'exact_token_hits': exact_token_hits,
    'v1_prompt_sha256': receipt['v1_prompt_sha256'],
    'extraction_prompt_sha256': receipt['extraction_prompt_sha256'],
    'protocol_sha256': receipt['protocol_sha256'],
    'suite_sha256': receipt['suite_sha256'],
}, indent=1))
