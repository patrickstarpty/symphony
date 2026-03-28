#!/usr/bin/env python3
"""Generate domain-realistic test fixtures for insurance domain.

Usage:
  python data-generator.py --domain insurance --entity policy --count 5 --format json

Output: JSON with randomly generated fixtures matching entity schema.
"""

import argparse
import json
import random
import sys
from datetime import date, timedelta


LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
COVERAGE_TYPES = ["auto", "home", "life"]
POLICY_STATUSES = ["active", "expired", "cancelled"]
CLAIM_STATUSES = ["open", "approved", "rejected", "pending_review"]
DEDUCTIBLES = [250.0, 500.0, 1000.0, 2500.0]


def random_date(start_days_ago: int = 730, end_days_ago: int = 0) -> date:
    """Generate a random date within a range."""
    today = date.today()
    start = today - timedelta(days=start_days_ago)
    end = today - timedelta(days=end_days_ago)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def generate_policy() -> dict:
    """Generate a realistic insurance policy fixture."""
    start_date = random_date(730, 0)
    end_date = start_date + timedelta(days=365)
    return {
        "id": f"POL-{random.randint(1000000000, 9999999999)}",
        "customer_name": f"Test{random.choice(LAST_NAMES)}",
        "customer_email": f"test_{random.randint(1000, 9999)}@test.example",
        "policy_number": f"POL-TEST-{random.randint(100000, 999999)}",
        "coverage_type": random.choice(COVERAGE_TYPES),
        "premium_amount": round(random.uniform(50, 500), 2),
        "effective_date": start_date.isoformat(),
        "expiration_date": end_date.isoformat(),
        "status": random.choice(POLICY_STATUSES),
        "deductible": random.choice(DEDUCTIBLES),
    }


def generate_claim() -> dict:
    """Generate a realistic insurance claim fixture."""
    incident_date = random_date(365, 0)
    claim_date = incident_date + timedelta(days=random.randint(0, 30))
    return {
        "id": f"CLM-{random.randint(1000000000, 9999999999)}",
        "policy_id": f"POL-{random.randint(1000000000, 9999999999)}",
        "claim_number": f"CLM-TEST-{random.randint(100000, 999999)}",
        "incident_date": incident_date.isoformat(),
        "claim_date": claim_date.isoformat(),
        "claim_type": random.choice(COVERAGE_TYPES),
        "amount_claimed": round(random.uniform(100, 50000), 2),
        "status": random.choice(CLAIM_STATUSES),
        "description": "Test claim description for automated testing purposes.",
    }


def generate_customer() -> dict:
    """Generate a realistic customer fixture."""
    dob = random_date(29200, 6570)
    return {
        "id": f"CUST-{random.randint(10000000, 99999999)}",
        "first_name": f"Test{random.randint(10, 99)}",
        "last_name": random.choice(LAST_NAMES),
        "email": f"test_{random.randint(1000, 9999)}@test.example",
        "phone": "555-0100",
        "date_of_birth": dob.isoformat(),
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "99999",
    }


def generate_quote() -> dict:
    """Generate a realistic insurance quote fixture."""
    quote_date = random_date(30, 0)
    exp_date = quote_date + timedelta(days=30)
    return {
        "id": f"QT-{random.randint(10000000, 99999999)}",
        "customer_email": f"test_{random.randint(1000, 9999)}@test.example",
        "coverage_type": random.choice(COVERAGE_TYPES),
        "estimated_premium": round(random.uniform(75, 300), 2),
        "quote_date": quote_date.isoformat(),
        "expiration_date": exp_date.isoformat(),
        "status": random.choice(["pending", "accepted", "expired"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate domain-realistic test fixtures")
    parser.add_argument("--domain", default="insurance", help="insurance | financial | healthcare")
    parser.add_argument("--entity", default="policy", help="policy | claim | customer | quote")
    parser.add_argument("--count", type=int, default=5, help="Number of fixtures to generate")
    parser.add_argument("--format", default="json", help="json | csv")
    args = parser.parse_args()

    generators = {
        "policy": generate_policy,
        "claim": generate_claim,
        "customer": generate_customer,
        "quote": generate_quote,
    }

    generator = generators.get(args.entity)
    if not generator:
        print(f"Unknown entity: {args.entity}", file=sys.stderr)
        sys.exit(1)

    fixtures = [generator() for _ in range(args.count)]

    if args.format == "json":
        json.dump(fixtures, sys.stdout, indent=2, default=str)
    else:
        print(f"Unsupported format: {args.format}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
