"""Independent checker for ORION-11 costed-ordering-v1.

This package recomputes every score row, every gate, the bootstrap intervals,
the Holm adjustment and the terminal from raw_traces.jsonl alone. It imports
no candidate policy, no production scorer, no statistics module and no runner
module, as PROTOCOL.json independent_checker_requirements demands.
"""
