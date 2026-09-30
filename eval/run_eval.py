"""Week 3, Block 2: evaluation harness. Runs in CI and fails the build
if quality drops below thresholds.

Metrics:
    routing_accuracy   share of cases routed to expected_route
    escalation_recall  share of must-escalate cases that escalated (target 1.0)
    mention_rate       share of answers containing every must_mention phrase

Run:
    python -m eval.run_eval            # full run (needs LLM key for answer path)
    python -m eval.run_eval --routing  # routing only, no LLM calls (what CI runs)

TODO (you): grow golden_set.jsonl to 50 hand-labeled cases, including
tricky ones (sarcasm, two intents in one message, typos, fake SSNs).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.agent.graph import classify_node, redact_node, route

GOLDEN = Path("eval/golden_set.jsonl")
THRESHOLDS = {"routing_accuracy": 0.80, "escalation_recall": 1.0}


def load() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]


def routing_eval(cases: list[dict]) -> dict:
    correct, esc_total, esc_hit = 0, 0, 0
    for c in cases:
        state = {"raw_message": c["message"]}
        state |= redact_node(state)
        state |= classify_node(state)
        got = route(state)
        correct += got == c["expected_route"]
        if c["expected_route"] == "escalate":
            esc_total += 1
            esc_hit += got == "escalate"
    return {
        "routing_accuracy": correct / len(cases),
        "escalation_recall": esc_hit / esc_total if esc_total else 1.0,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--routing", action="store_true", help="routing metrics only, no LLM calls")
    args = p.parse_args()

    cases = load()
    scores = routing_eval(cases)
    if not args.routing:
        print("Full answer-path eval not built yet (Week 3, Block 2). Showing routing only.")
        # TODO (you): invoke the full graph and compute mention_rate

    print(f"\nMedAssist eval scorecard ({len(cases)} cases)")
    failed = False
    for name, value in scores.items():
        bar = THRESHOLDS.get(name)
        ok = bar is None or value >= bar
        failed |= not ok
        print(f"  {name:<20} {value:6.2%}  (min {bar:.0%})  {'PASS' if ok else 'FAIL'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
