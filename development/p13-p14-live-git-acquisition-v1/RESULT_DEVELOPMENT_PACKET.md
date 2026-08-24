# P13+P14 live-Git acquisition V1 result packet

## Atomic question

Did the frozen live-Git acquisition protocol meet its minimum of 30 verified
repositories across at least five organizations without changing any frozen
identity or authority boundary?

## Execution

The runner was invoked from clean `main` at
`3d8c01662e64434c736e0179c58fb30469bf42f4` with the committed V1 protocol,
runner, 45-repository corpus and objective-gold contract. It retained all rows
and refused to overwrite an existing output. Four worker lanes changed latency,
not row order or terminal logic.

## Outcome

The minimum was not met: 0 verified repositories, 0 verified organizations, 31
observed digest mismatches and 14 license exclusions. The terminal is
`P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_NOT_MET__CAMPAIGN_BLOCKED`.

## Verification commands

```text
python development/p13-p14-live-git-acquisition-v1/check_live_git_acquisition_result_v1.py
pytest -q tests/unit/study/p14/test_p13_p14_live_git_acquisition_result_v1.py
python papers/paper-13-responsibility-carrying-state/check_p13_p14_pinned_corpus_v1.py
```

## Authority boundary

This package records an adverse acquisition result only. It does not create a
campaign result, comparator result, population inference, independent
adjudication or protected custody. No issue box is checked. Scientific-
authority delta: **NONE**.
