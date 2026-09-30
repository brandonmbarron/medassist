import csv
import subprocess
import sys


def test_generator_runs_and_is_reproducible(tmp_path):
    for run in ("a", "b"):
        subprocess.run(
            [sys.executable, "scripts/generate_data.py", "--members", "50",
             "--messages-per-intent", "5", "--out", str(tmp_path / run)],
            check=True,
        )
    a = (tmp_path / "a" / "claims.csv").read_text()
    b = (tmp_path / "b" / "claims.csv").read_text()
    assert a == b, "same seed should give identical data"

    with open(tmp_path / "a" / "messages.csv") as f:
        intents = {row["intent"] for row in csv.DictReader(f)}
    assert intents == {"benefits", "claim_status", "prior_auth", "complaint", "urgent_clinical"}
