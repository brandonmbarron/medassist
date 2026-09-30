"""Generate synthetic Medicare Advantage data for MedAssist.

Everything here is fake. No real member data is ever used in this project.

Outputs (in data/raw/):
    members.csv   one row per member
    claims.csv    one row per claim
    messages.csv  labeled member messages for the intent classifier

Usage:
    python scripts/generate_data.py --members 10000 --seed 42
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

PLANS = ["HMO-GOLD", "HMO-SILVER", "PPO-GOLD", "PPO-PLATINUM", "DSNP-CARE"]
STATES = ["KY", "IN", "OH", "TN", "FL", "TX", "GA", "IL"]
CLAIM_STATUS = ["PAID", "PAID", "PAID", "PAID", "DENIED", "PENDING", "IN_REVIEW"]
DENIAL_REASONS = [
    "PRIOR_AUTH_MISSING",
    "OUT_OF_NETWORK",
    "NOT_MEDICALLY_NECESSARY",
    "DUPLICATE_CLAIM",
    "COVERAGE_TERMINATED",
]
# (CPT code, description, typical billed amount)
PROCEDURES = [
    ("99213", "Office visit, established patient", 140),
    ("99214", "Office visit, moderate complexity", 210),
    ("80053", "Comprehensive metabolic panel", 60),
    ("71046", "Chest X-ray, 2 views", 120),
    ("93000", "Electrocardiogram", 85),
    ("97110", "Physical therapy exercise", 95),
    ("72148", "MRI lumbar spine", 1200),
    ("45378", "Colonoscopy", 1800),
    ("99285", "Emergency department visit, high severity", 2400),
]
ICD10 = ["E11.9", "I10", "M54.5", "J44.9", "E78.5", "N18.3", "F32.9", "Z00.00"]

FIRST = ["James", "Mary", "Robert", "Linda", "John", "Patricia", "William", "Barbara",
         "David", "Susan", "Richard", "Karen", "Charles", "Nancy", "Thomas", "Betty"]
LAST = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Clark", "Lewis"]

# Intent labels the classifier learns in Week 2
INTENT_TEMPLATES = {
    "benefits": [
        "Does my plan cover {service}?",
        "How much is my copay for {service}?",
        "Is {service} included in my {plan} plan?",
        "What is my out-of-pocket max this year?",
        "Do I need a referral to see a specialist for {service}?",
        "Are dental cleanings covered?",
        "What's my deductible for {service}?",
    ],
    "claim_status": [
        "What is the status of my claim from {date}?",
        "Why was my claim for {service} denied?",
        "My claim {claim_id} is still pending, any update?",
        "Has my {service} claim been paid yet?",
        "I got a bill for {service}, did insurance process it?",
        "Can you check claim {claim_id} for me?",
    ],
    "prior_auth": [
        "Do I need prior authorization for {service}?",
        "My doctor ordered {service}, is approval needed first?",
        "How long does prior auth take for {service}?",
        "Was the prior authorization for my {service} approved?",
        "What paperwork is needed to get {service} authorized?",
    ],
    "complaint": [
        "I've called three times about {service} and nobody helps.",
        "I want to file a grievance about my {service} denial.",
        "Your customer service was rude to me yesterday.",
        "This is ridiculous, my {service} claim has been stuck for weeks.",
        "How do I file an appeal? I'm very unhappy.",
    ],
    "urgent_clinical": [
        "I'm having chest pain right now, what should I do?",
        "I think I took too much of my medication.",
        "My mother fell and can't get up.",
        "I'm having trouble breathing.",
        "Should I stop taking my blood pressure pills? I feel dizzy.",
        "I have a really high fever and I'm confused.",
    ],
}
SERVICES = ["an MRI", "physical therapy", "a colonoscopy", "an office visit", "lab work",
            "an ER visit", "a chest X-ray", "hearing aids", "an eye exam"]


def rand_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def make_members(rng: random.Random, n: int) -> list[dict]:
    members = []
    for i in range(n):
        dob = rand_date(rng, date(1935, 1, 1), date(1960, 12, 31))  # 65+ population
        members.append({
            "member_id": f"M{i:07d}",
            "first_name": rng.choice(FIRST),
            "last_name": rng.choice(LAST),
            "dob": dob.isoformat(),
            "state": rng.choice(STATES),
            "plan_id": rng.choice(PLANS),
            "enroll_date": rand_date(rng, date(2020, 1, 1), date(2025, 6, 30)).isoformat(),
        })
    return members


def make_claims(rng: random.Random, members: list[dict], avg_per_member: int) -> list[dict]:
    claims = []
    cid = 0
    for m in members:
        for _ in range(rng.randint(0, avg_per_member * 2)):
            cpt, desc, base = rng.choice(PROCEDURES)
            billed = round(base * rng.uniform(0.8, 1.4), 2)
            status = rng.choice(CLAIM_STATUS)
            service_date = rand_date(rng, date(2025, 1, 1), date(2026, 8, 31))
            paid = round(billed * rng.uniform(0.5, 0.85), 2) if status == "PAID" else 0.0
            claims.append({
                "claim_id": f"C{cid:09d}",
                "member_id": m["member_id"],
                "service_date": service_date.isoformat(),
                "received_date": (service_date + timedelta(days=rng.randint(1, 30))).isoformat(),
                "cpt_code": cpt,
                "procedure_desc": desc,
                "icd10_code": rng.choice(ICD10),
                "billed_amount": billed,
                "paid_amount": paid,
                "status": status,
                "denial_reason": rng.choice(DENIAL_REASONS) if status == "DENIED" else "",
                "days_to_process": rng.randint(3, 45) if status in ("PAID", "DENIED") else "",
            })
            cid += 1
    # Inject some dirty rows on purpose so the Week 1 data quality checks have work to do
    for c in rng.sample(claims, k=max(1, len(claims) // 200)):
        c["billed_amount"] = -abs(c["billed_amount"])
    for c in rng.sample(claims, k=max(1, len(claims) // 300)):
        c["member_id"] = ""
    return claims


def make_messages(rng: random.Random, per_intent: int) -> list[dict]:
    rows = []
    for intent, templates in INTENT_TEMPLATES.items():
        for _ in range(per_intent):
            text = rng.choice(templates).format(
                service=rng.choice(SERVICES),
                plan=rng.choice(PLANS),
                date=rand_date(rng, date(2026, 1, 1), date(2026, 8, 31)).strftime("%B %d"),
                claim_id=f"C{rng.randint(0, 999999):09d}",
            )
            # Light noise so the classifier can't just memorize templates
            if rng.random() < 0.3:
                text = text.lower()
            if rng.random() < 0.2:
                text = rng.choice(["Hi, ", "Hello. ", "Quick question: ", "Please help. "]) + text
            rows.append({"text": text, "intent": intent})
    rng.shuffle(rows)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows):>8,} rows -> {path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--members", type=int, default=10_000)
    p.add_argument("--claims-per-member", type=int, default=20)
    p.add_argument("--messages-per-intent", type=int, default=400)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("data/raw"))
    args = p.parse_args()

    rng = random.Random(args.seed)
    members = make_members(rng, args.members)
    write_csv(args.out / "members.csv", members)
    write_csv(args.out / "claims.csv", make_claims(rng, members, args.claims_per_member))
    write_csv(args.out / "messages.csv", make_messages(rng, args.messages_per_intent))


if __name__ == "__main__":
    main()
