"""P14 external packet specifications - domain 3/3: RESEARCH_SYSTEMS_INFRASTRUCTURE.

Deterministic data only. Anonymized per the external governance protocol.
Numbers are carried over from preserved internal records with identifiers
renamed to generic codes (venues, systems, streams).
"""

DOMAIN = "RESEARCH_SYSTEMS_INFRASTRUCTURE"

SPECS = [
    # ---------------- STRONG_PROMOTABLE (3) ----------------
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A tamper-evident receipt format is claimed to make evaluation records independently checkable: any "
          "post-hoc edit to a result breaks a published digest chain. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Format frozen (per-record content hashes, chained digests, run-id binding) before any "
                         "attack attempt; the attack battery was preregistered."),
            ("RESULT", "Attack battery, 11 preregistered mutation classes (field edit, record swap, timestamp "
                       "shift, digest reuse, truncated tail, replayed record, cross-run splice, hash collision "
                       "attempt via truncation, header rewrite, signature strip, wholesale file replace): "
                       "11/11 detected; detection is by chain break in 9 and by run-id mismatch in 2."),
            ("CONTROL", "Negative control: 10,000 unmutated chains verified clean (0 false detections)."),
            ("DONOR", "Donor I-1 (transparency-log lineage): owns the chained-digest mechanism; the delta is the "
                      "evaluation-record binding and the preregistered mutation battery."),
        ],
        dp=["mutation battery fully executed", "false-detection control clean", "donor delta stated"],
        scope="the frozen receipt format",
        forbid=["claiming prevention of coercion", "claims beyond the 11 mutation classes"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A deterministic-regeneration gate is claimed to make artifact generation bit-reproducible across "
          "machines (no clock, no network, fixed seeds). Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Gate frozen: regenerate into a scratch directory and byte-compare against the committed "
                         "artifacts; any byte difference fails."),
            ("RESULT", "Executed on 3 machine profiles (two OS families, two filesystems): 3/3 byte-identical; "
                       "the artifacts total 4.1 MB across 3 files; a deliberate 1-byte flip in the committed copy "
                       "is caught (gate exit 1)."),
            ("CONTROL", "Positive-detection control: 20 seeded single-byte flips, 20/20 caught."),
            ("DONOR", "Donor I-2 (reproducible-build practice): owns determinism discipline; the delta is the "
                      "evaluation-artifact application and the flip-control battery."),
        ],
        dp=["cross-machine regeneration executed", "flip controls run", "donor delta stated"],
        scope="the frozen generator and its three artifacts",
        forbid=["claiming determinism for components not regenerated"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A fail-closed contract checker is claimed to prevent evaluation-config drift: schemas must keep "
          "additionalProperties=false and forbidden field names must stay absent, or the check fails. Determine "
          "the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Checker frozen with its forbidden-field list and marker strings; mutation testing "
                         "preregistered as the acceptance route."),
            ("RESULT", "Mutation battery: 24 single-concept mutations (allow additionalProperties, add a "
                       "forbidden field, drop an enum value, widen a type, remove a marker string, weaken a "
                       "minimum): 24/24 caught (exit 1)."),
            ("CONTROL", "Unmutated contract passes (exit 0); a minimal packet fixture passes while carrying only "
                        "a digest of hidden gold."),
            ("BACKGROUND", "The checker prints a distinct success string; absence of output is treated as failure "
                           "by the surrounding gate."),
        ],
        dp=["mutation battery executed", "clean fixture passes", "fail-closed semantics verified"],
        scope="the frozen checker and contract files",
        forbid=["claims about downstream consumers not tested"],
    ),

    # ---------------- APPARENT_POSITIVE_SUBSUMED (3) ----------------
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'novel' artifact-identity scheme is proposed: name artifacts by the SHA-256 of their canonical "
          "byte form. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Scheme frozen; novelty of the mechanism declared the estimand."),
            ("RESULT", "Scheme implemented; 1,200 artifacts named; collision-free as expected."),
            ("DONOR", "Donor I-3: content-addressed storage (git, and decades of Merkle-lineage systems) owns the "
                      "mechanism exactly; the canonicalisation choice is documented there too."),
            ("CONTROL", "A line-by-line mapping from the donor's scheme to the proposed one is included."),
        ],
        dp=["mechanism identity against donor established", "residual delta isolated", "decision recorded"],
        scope="flat artifact stores",
        forbid=["claiming the naming scheme as new"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'novel' staged-evaluation funnel is proposed: candidates pass through frozen gates with ratcheting "
          "thresholds that never loosen. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Funnel frozen with its gate list."),
            ("RESULT", "Funnel operated for 6 weeks; 41 candidates processed; no threshold loosened."),
            ("DONOR", "Donor I-4: ratcheting acceptance pipelines in release engineering own the mechanism "
                      "(never-loosen thresholds, gated promotion); the mapping is direct."),
        ],
        dp=["mechanism identity against donor established", "residual delta isolated", "decision recorded"],
        scope="the frozen gate list",
        forbid=["claiming the ratchet as new"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'novel' blind-scoring worksheet design is proposed: evaluators receive anonymised systems with "
          "identity stripped and agreement computed post-hoc. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Worksheet design frozen."),
            ("RESULT", "Pilot with 4 evaluators; identity-recovery rate 0/4 below chance."),
            ("DONOR", "Donor I-5: blinded adjudication in clinical-trials and measurement practice owns the "
                      "mechanism; the identity-stripping checklist maps item-for-item."),
        ],
        dp=["mechanism identity against donor established", "residual delta isolated", "decision recorded"],
        scope="paired judgment studies",
        forbid=["claiming blinding as new"],
    ),

    # ---------------- INTERACTION_ONLY (2) ----------------
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="A pipeline-latency gain is claimed for the combination of content-addressed caching and a "
          "stage-fusion rewrite. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Four-arm build-latency design frozen (median over 30 cold builds per arm)."),
            ("RESULT", "Median minutes: none 41.2, cache-only 40.8 (-1.0%, CI [-4,+2]%), fusion-only 40.9 (-0.7%, "
                       "CI [-3,+2]%), combination 28.4 (-31.1%, CI [-34,-28]%)."),
            ("CONTROL", "When cache keys are coarsened (defeating exact-address reuse), the combination's gain "
                        "shrinks to -3% - the fusion benefit requires exact cache identity."),
        ],
        dp=["factorial completed", "coarsening control locates the co-dependence", "decision recorded"],
        scope="the frozen pipeline and workload",
        forbid=["recommending either component alone"],
    ),
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="A correctness gain is claimed for combining a lock-free queue with a checkpoint interval change in a "
          "verification worker pool. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Two-by-two design frozen; stuck-run rate declared the estimand."),
            ("RESULT", "Stuck runs per 1,000: none 8.1, queue-only 7.9 (p=0.86), checkpoint-only 8.0 (p=0.91), "
                       "combined 1.2 (p<1e-4)."),
            ("CONTROL", "With checkpoints disabled entirely the combined gain disappears (7.8 per 1,000): the "
                        "lock-free queue only helps when recovery is cheap."),
        ],
        dp=["factorial completed", "recovery-cost control run", "decision recorded"],
        scope="the frozen pool configuration",
        forbid=["crediting either component alone"],
    ),

    # ---------------- NULL_LIVE_PARENT (3) ----------------
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A validated parent result (artifact-store dedup reclaiming 58 GB, reproduced) is claimed to extend to "
          "a second store with the same reclaim fraction. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Parent reclaim (0.41 of store bytes) and the extension declared separately; minimum "
                         "detectable fraction 0.20."),
            ("RESULT", "Parent store re-audited: 0.40 reclaimed, matches. Second store: 0.03 reclaimed "
                       "(CI [0.01,0.05]); the 0.20 minimum detectable effect is excluded."),
            ("CONTROL", "A synthetic duplicate-injection control recovers injected duplicates at 0.97 efficiency "
                        "on the second store, so the null is about content, not tooling."),
        ],
        dp=["parent scored separately", "injection control run", "null recorded for the second store only"],
        scope="the second store",
        forbid=["recording a null against the parent audit"],
    ),
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A live parent result (CI display-artifact false-failure fix, reproduced) is claimed to reduce "
          "operator misclassification of cancelled runs on a second dashboard. Determine the strongest "
          "defensible action.",
        ev=[
            ("PROTOCOL", "Misclassification rate threshold (halving) frozen for the second dashboard."),
            ("RESULT", "Parent dashboard: rate 7.1% -> 0.9% (reproduced). Second dashboard: 6.8% -> 6.5% "
                       "(CI [-1.7,+2.3] points, includes 0)."),
            ("CONTROL", "The second dashboard renders raw status text with no display summarisation layer; the "
                        "parent fix has no surface to act on there - the null is structural."),
        ],
        dp=["parent scored separately", "structural explanation verified", "null recorded for the second dashboard only"],
        scope="the second dashboard",
        forbid=["recording a null against the parent fix"],
    ),
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A live parent result (schema-hash drift detection catching 100% of injected contract drift, "
          "reproduced) is claimed to transfer to configuration files. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Transfer gate frozen: >= 80% detection on injected config drift."),
            ("RESULT", "Parent (contract schemas): 20/20 injected drifts caught (reproduced). Configs: 9/20 "
                       "(45%); the gate is excluded."),
            ("CONTROL", "Missed cases share one cause (comment-only reformatting is legitimate drift-free "
                        "change), giving a mechanism-level boundary: hash-detection transfers to content "
                        "formats, not comment-bearing ones."),
        ],
        dp=["parent scored separately", "missed-case mechanism identified", "null recorded for configs only"],
        scope="comment-bearing configuration files",
        forbid=["recording a null against the parent detection result"],
    ),

    # ---------------- NEGATIVE_RETAINED (3) ----------------
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="A live-deployment widening is claimed: extending a window parameter is asserted to raise daily "
          "profit, supported by a backtest showing +85.8 per day. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Paper-trading forensic preregistered as the only admissible evidence for the widening; "
                         "backtest-overfit gate (probability of backtest overfitting) frozen."),
            ("RESULT", "Backtest claims +85.8/day. Probability of backtest overfitting = 1.0 across the "
                       "configuration grid (every neighbouring configuration beats it - the selected point is "
                       "the grid's luckiest). Paper-trading forensic: the fillable additions realise -5.63 per "
                       "share (n=54 fills, CI [-7.41,-3.85]); the claimed sign is inverted in live paper fills."),
            ("CONTROL", "Failure attribution: 11/18 losses occur in the widened segment specifically; early-window "
                        "reversal is the mechanism."),
            ("BACKGROUND", "The un-widened rule remains positive in the same forensic (+2.06 per share); the "
                           "negative attaches to the widening only, and is retained."),
        ],
        dp=["paper forensic completed with n>=50", "overfit probability computed", "negative retained with mechanism and parent separation"],
        scope="the window widening only",
        forbid=["deploying the widening", "citing the +85.8/day backtest as live evidence"],
    ),
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="A shadow monitor is claimed to halve time-to-detection of performance decay. Determine the strongest "
          "defensible action.",
        ev=[
            ("PROTOCOL", "Time-to-detection gate (<= 50% of the incumbent monitor at matched false-alarm rate) "
                         "frozen; a decomposed false-alarm audit preregistered."),
            ("RESULT", "Measured ratio 1.9 (nearly twice as slow); the decomposed audit shows the monitor's "
                       "stand-down channel fires on 3 transient patterns, masking real decay until it is "
                       "asymptotic - the failure is structural to the transient filter, not tuning."),
            ("CONTROL", "Disabling the transient filter restores ratio 0.61 (gate met) but raises false alarms "
                        "above the matched budget; both operating points are reported."),
        ],
        dp=["decomposed audit completed", "structural attribution recorded", "both operating points reported"],
        scope="the frozen monitor class",
        forbid=["deploying the stand-down channel as-is", "reporting only the filter-off point"],
    ),
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="An auto-configuration agent is claimed to hold evaluation cost within 1.2x of manual configuration "
          "while improving throughput. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Cost gate (<= 1.2x manual spend) and throughput gate (>= +10%) frozen."),
            ("RESULT", "Measured spend ratio 3.4x (gate excluded); throughput +2.1% (CI [-1.2,+5.4], includes 0). "
                       "The agent's retry loop re-enumerates unchanged state after each rejection, accounting "
                       "for 71% of spend (trace accounting attached)."),
            ("CONTROL", "A memoisation patch for the re-enumeration drops spend to 1.8x with throughput +1.9% - "
                        "documented as the revival lever, not deployed as a pass."),
        ],
        dp=["both gates evaluated", "spend attribution traced", "revival lever documented without re-grading"],
        scope="the frozen agent and task suite",
        forbid=["grading the patched variant within this claim", "deploying the agent"],
    ),

    # ---------------- LEAKY_OR_CORRUPT_BENCHMARK (2) ----------------
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="An aggregate 'system health' score is offered as evidence of improvement (72 -> 81), where the score "
          "averages 12 submetrics of which 9 were redefined mid-period. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Metric definitions frozen with version stamps; unstamped redefinition declared a "
                         "corruption."),
            ("RESULT", "Version audit: 9/12 submetrics changed definition between the two measurement dates; "
                       "under fixed definitions the change is +1 (CI [-3,+5], includes 0)."),
            ("CONTROL", "Recompute with the old definitions on new data and new definitions on old data "
                        "(2x2 definitional control): only the new-on-new cell shows the gain, confirming "
                        "definitional drift as the mechanism."),
        ],
        dp=["version audit executed", "definitional 2x2 control run", "aggregate claim withdrawn"],
        scope="the frozen metric suite",
        forbid=["citing the 72 -> 81 change as evidence"],
    ),
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="A log-based incident study is offered where 2>/dev/null redirections and `|| true` guards are found "
          "on 14 of the analyzed pipelines, and the study's absence claims rest on empty output. Determine the "
          "strongest defensible action.",
        ev=[
            ("PROTOCOL", "Silent-failure scan preregistered: any absence claim must carry a counted search with "
                         "stated scope."),
            ("RESULT", "The offered study makes 6 absence claims from empty outputs; recounting with exit codes "
                       "and numeric tallies: 4 of 6 are false absences (the outputs were swallowed by display "
                       "filters; counted lines are non-zero)."),
            ("CONTROL", "A known-present target planted in the corpus is recovered by the counted method "
                        "(1/1) and missed by the naive method (0/1), certifying the diagnosis."),
        ],
        dp=["counted-search method applied", "planted-target control run", "affected absence claims retracted"],
        scope="the analyzed pipeline set",
        forbid=["publishing absence claims from empty output"],
    ),

    # ---------------- NON_IDENTIFIABLE (2) ----------------
    dict(
        family="NON_IDENTIFIABLE", gold="NON_IDENTIFIABLE",
        q="A claim states that an execution gate was 'hard-enforced, not logged' - that the gate blocked "
          "actions rather than merely recording them. The evidence base is post-hoc logs. Determine the "
          "strongest defensible action.",
        ev=[
            ("PROTOCOL", "Enforcement vs logging declared distinguishable only by a preregistered probe "
                         "(attempt a violating action under observation), not by reading logs."),
            ("PRIMARY", "Construction: for the logged-only configuration, the probe action appears in the log "
                        "AND is executed; for the enforced configuration it appears AND is refused. Both traces "
                        "supplied. The offered evidence contains logs from a configuration that cannot be "
                        "determined from the logs themselves."),
            ("RESULT", "The supplied log lines are byte-compatible with both configurations (50 such pairs "
                       "exhibited); post-hoc logs cannot identify which ran."),
            ("CONTROL", "The probe distinguishes the configurations in 20/20 trials when it is permitted."),
        ],
        dp=["probe-vs-log identifiability established", "both-directions construction certified", "decision recorded"],
        scope="post-hoc logs only",
        forbid=["claiming hard enforcement from logs alone"],
    ),
    dict(
        family="NON_IDENTIFIABLE", gold="CANNOT_CHECK",
        q="A dependency-isolation claim asserts that two co-deployed systems never shared state, based on a "
          "lock-file and manifest that were regenerated on every deploy. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Freeze requires the contemporaneous manifest for any sharing claim; regenerated "
                         "manifests declared non-evidentiary."),
            ("PRIMARY", "The manifest in the record post-dates the deployment under question (regeneration "
                        "timestamp); the contemporaneous file was not preserved."),
            ("RESULT", "Reconstruction from deploy logs yields 2 candidate manifest states with different "
                       "shared-state answers; the visible evidence cannot discriminate."),
            ("CONTROL", "A preserved-manifest positive control from a comparable deployment resolves its "
                        "question exactly, showing what the missing artifact would have settled."),
        ],
        dp=["regeneration timestamp established", "candidate reconstruction attempted", "external archive channel identified"],
        scope="the deployment window in question",
        forbid=["deciding the sharing question on the regenerated manifest"],
    ),

    # ---------------- REGIME_CHANGE_REOPEN (2, longitudinal pair) ----------------
    dict(
        family="REGIME_CHANGE_REOPEN", gold="REOPEN", round_no=1,
        q="Round 1 of a stream-coverage claim: a data stream is declared unarchivable (no reader can be "
          "attached without dropping the live consumer). Determine the strongest defensible action at this round.",
        ev=[
            ("PROTOCOL", "Longitudinal design frozen: a recovery round is scheduled in which a read-only "
                         "archive tap is attempted under a changed attach protocol; round-1 'unarchivable' is "
                         "scoped to the round-1 protocol."),
            ("RESULT", "Round 1 (attach protocol v1): 3/3 attach attempts drop the live consumer within 60s; "
                       "the failure trace is captured."),
            ("CONTROL", "Instrumentation: the drop is caused by backpressure on a shared buffer (trace shows "
                        "buffer overflow at attach), a protocol-level mechanism, not data-level."),
            ("BACKGROUND", "The round-2 protocol change (read-only tap with its own buffer) is frozen in the "
                           "same document."),
        ],
        dp=["round-1 scope respected", "failure mechanism traced", "scheduled recovery round acknowledged"],
        scope="attach protocol v1",
        forbid=["closing the stream as permanently unarchivable on round 1"],
    ),
    dict(
        family="REGIME_CHANGE_REOPEN", gold="REOPEN", round_no=2,
        q="Round 2 of the stream-coverage claim: the preregistered read-only tap protocol recovers the stream. "
          "Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Round-2 tap protocol (independent buffer, no backpressure coupling) frozen with "
                         "round 1 before either ran."),
            ("RESULT", "Round 2: tap attached for 6 consecutive hours, 0 drops, 2.3 GB recovered, checksum "
                       "match against the consumer's own offsets for the overlap window (0 mismatches over "
                       "41,112 records)."),
            ("CONTROL", "The round-1 mechanism is confirmed removed: shared-buffer pressure stays at 0 under "
                        "the tap (60-minute trace)."),
            ("BACKGROUND", "The round-1 'unarchivable' record is amended with the round-2 recovery; the "
                           "coverage claim reopens under the new protocol and the earlier scope is retained "
                           "as a correct statement about protocol v1."),
        ],
        dp=["round-2 recovery certified", "mechanism removal verified", "round-1 record amended, not deleted"],
        scope="tap protocol v2",
        forbid=["deleting the round-1 record", "treating round 2 as a new claim"],
    ),
]

assert len(SPECS) == 20, len(SPECS)
