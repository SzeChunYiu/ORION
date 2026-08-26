"""A log parser is only as good as its fixtures, so this one is tested on logs.

Both directions: it must catch an overfull box in a file nobody excused, stay
quiet on an excused one, fail when an excuse is no longer needed, and never
silently drop a warning it could not attribute.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    ROOT
    / "papers"
    / "orion-12-open-world-scientific-discovery"
    / "scripts"
    / "check_manuscript_typography.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("check_manuscript_typography", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CLEAN_LOG = """
This is pdfTeX
(./main.tex
(./sections/methods.tex) (./sections/availability.tex)
Output written on main.pdf (7 pages).
"""

OVERFULL_IN_METHODS = """
(./main.tex
(./sections/methods.tex
Overfull \\hbox (38.04115pt too wide) in paragraph at lines 86--93
)
)
"""

OVERFULL_IN_RESULTS = """
(./main.tex
(./sections/results.tex
Overfull \\hbox (122.67274pt too wide) in paragraph at lines 24--38
)
)
"""

UNATTRIBUTED = """
Overfull \\hbox (9.9pt too wide) in paragraph at lines 1--2
"""


def test_a_clean_log_passes():
    module = _module()
    boxes = module.parse(CLEAN_LOG)
    assert boxes == []
    offences, _ = module.evaluate(boxes, max_points=0.0, allowed={})
    assert offences == 0


def test_an_overfull_box_is_attributed_and_fails():
    module = _module()
    boxes = module.parse(OVERFULL_IN_METHODS)
    assert len(boxes) == 1
    assert boxes[0].source == "methods.tex"
    assert boxes[0].points > 38
    offences, messages = module.evaluate(boxes, max_points=0.0, allowed={})
    assert offences == 1
    assert any("methods.tex" in item and "idt" in item for item in messages), messages


def test_an_allowed_file_is_reported_but_does_not_fail():
    module = _module()
    boxes = module.parse(OVERFULL_IN_RESULTS)
    offences, messages = module.evaluate(
        boxes, max_points=0.0, allowed={"results.tex": "owned elsewhere"}
    )
    assert offences == 0
    assert any(item.startswith("ALLOWED") for item in messages)


def test_an_allowance_that_is_no_longer_needed_fails():
    """A stale excuse is a lie about the current state, so it must break the run."""

    module = _module()
    boxes = module.parse(CLEAN_LOG)
    offences, messages = module.evaluate(
        boxes, max_points=0.0, allowed={"results.tex": "owned elsewhere"}
    )
    assert offences == 1
    assert any(item.startswith("STALE") for item in messages)


def test_an_unattributable_warning_is_counted_not_dropped():
    """Failing closed: a parser that loses a warning turns the gate into decoration."""

    module = _module()
    boxes = module.parse(UNATTRIBUTED)
    assert len(boxes) == 1
    assert boxes[0].source == "<unattributed>"
    offences, _ = module.evaluate(boxes, max_points=0.0, allowed={})
    assert offences == 1


def test_the_tolerance_is_honoured_but_defaults_to_zero():
    module = _module()
    boxes = module.parse(OVERFULL_IN_METHODS)
    assert module.evaluate(boxes, max_points=50.0, allowed={})[0] == 0
    assert module.evaluate(boxes, max_points=0.0, allowed={})[0] == 1


def test_cli_returns_nonzero_for_an_unexcused_box(tmp_path):
    module = _module()
    log = tmp_path / "main.log"
    log.write_text(OVERFULL_IN_METHODS, encoding="utf-8")
    assert module.main(["--log", str(log)]) == 1

    missing = tmp_path / "absent.log"
    assert module.main(["--log", str(missing)]) == 1, "a missing log is not a pass"


def test_every_committed_allowance_names_its_owner():
    """Any allowance that exists must name its owner and removal trigger."""

    module = _module()
    assert isinstance(module.ALLOWED_OVERFULL, dict)
    for name, reason in module.ALLOWED_OVERFULL.items():
        assert len(reason) > 40, f"{name}: the allowance must say who owns clearing it and when"


#: A verbatim excerpt of a real tectonic/LaTeX log, kept because both parser bugs
#: were invisible to hand-written fixtures: the elided ".tex" extension and the
#: unbalanced parenthesis counting that drained the stack. Fixtures agreed with my
#: mental model of the format; the real log did not.
REAL_LOG_EXCERPT = r"""
Underfull \hbox (badness 10000) in paragraph at lines 86--93
[][][][][][] [] [][][][][]$\TU/lmr/m/n/10.95 , and $[][][][][][][][] [] [][][][
][][] [] [][][][][][][][][][] [] [][][][][][]$. A seventh comparator,
 []

[6]) (sections/results [7]
Overfull \hbox (99.7106pt too wide) in paragraph at lines 24--38
\TU/lmr/m/n/10.95 It binds the full 840-record set by SHA-256 \TU/lmtt/m/n/10.9
5 611808dc80846d5057c84c12af7ff8ec3fa88ef15a6ede91807e590f4edb6f1f
 []


Overfull \hbox (122.67274pt too wide) in paragraph at lines 24--38
\TU/lmr/m/n/10.95 and the corresponding rich-artifact hash list by \TU/lmtt/m/n
/10.95 2da59dc21e6473e4a81eb93910501a67bed008dbc3e29c26116041b68dfbb325\TU/lmr/
m/n/10.95 .
 []
"""


def test_the_real_log_format_attributes_correctly():
    """Regression for two bugs that only the real log exposed."""

    module = _module()
    boxes = module.parse(REAL_LOG_EXCERPT)
    assert len(boxes) == 2, boxes
    assert {box.source for box in boxes} == {"results.tex"}, (
        "a real log writes '(sections/results [7]' with the extension elided, and is "
        "full of unrelated parentheses; both broke attribution before"
    )
    offences, _ = module.evaluate(boxes, max_points=0.0, allowed={})
    assert offences == 2
