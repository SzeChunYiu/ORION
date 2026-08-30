# ORION-04 global saturation obstruction v1

This packet combines the committed support-at-least-14 parent with complete dual exact replay of all support patterns 14 through 31.

```bash
python generate_cover.py
python independent_checker/check_static.py
python run_replay.py
python independent_checker/check_result.py
```

The positive terminal is `ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30`. External replay, novelty, venue, and submission authority remain false.
