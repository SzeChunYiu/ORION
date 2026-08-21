from __future__ import annotations

import extract_p10_cross_revision_trace_v1 as extractor
from p10_lean_json_transport_v1 import parse_messages, run_lean


def main() -> None:
    extractor.run_lean = run_lean
    extractor.parse_messages = parse_messages
    extractor.main()


if __name__ == "__main__":
    main()
