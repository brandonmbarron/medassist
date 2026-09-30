"""PHI/PII redaction. Runs before any text reaches a model or a log.

Starter version: regex for the most obvious identifiers.
TODO (you, Week 3 Block 1): add Microsoft Presidio for names and addresses,
then compare what each approach misses on your adversarial prompts.
"""

from __future__ import annotations

import re

PATTERNS = [
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("PHONE", re.compile(r"\b(?:\(\d{3}\)\s?|\d{3}[-.\s])\d{3}[-.\s]\d{4}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
    ("DOB", re.compile(r"\b(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])/(?:19|20)\d{2}\b")),
    ("MEMBER_ID", re.compile(r"\bM\d{7}\b")),
]


def redact(text: str) -> str:
    for label, pattern in PATTERNS:
        text = pattern.sub(f"[{label}]", text)
    return text
