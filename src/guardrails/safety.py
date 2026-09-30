"""Output safety checks. Any flag sends the reply to a human instead.

TODO (you, Week 3 Block 1): extend these checks, and add a test for each
one in tests/test_guardrails.py.
"""

from __future__ import annotations

import re

MEDICAL_ADVICE = re.compile(
    r"\b(you should (stop|start|take|increase|decrease)|dosage|diagnos(e|is)|mg\b)", re.I
)
LEAKED_ID = re.compile(r"\b(\d{3}-\d{2}-\d{4}|M\d{7})\b")


def check_output(answer: str, citations: list[str]) -> list[str]:
    flags = []
    if not answer.strip():
        flags.append("empty_answer")
    if MEDICAL_ADVICE.search(answer):
        flags.append("possible_medical_advice")
    if LEAKED_ID.search(answer):
        flags.append("identifier_in_output")
    if not citations:
        flags.append("no_citation")  # every factual answer must be grounded
    return flags
