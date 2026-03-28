#!/usr/bin/env python3
"""Convert business SLAs into load profile (VU ramp schedule).

Usage:
  python load-profile-calculator.py --target-p95-ms 200 --target-rps 100 --profile ramp-up --output profile.json

Output: JSON with VU schedule, think time, expected metrics.
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field, asdict


@dataclass
class VUStage:
    duration_seconds: int
    target_vus: int
    description: str


@dataclass
class LoadProfile:
    profile_type: str
    total_duration_seconds: int
    stages: list
    think_time_seconds: float
    target_p95_latency_ms: float
    target_error_rate_pct: float
    target_throughput_rps: float


def calculate_ramp_up_profile(
    target_vus: int,
    target_p95_ms: float,
    target_rps: float,
    total_duration_seconds: int = 600,
) -> LoadProfile:
    """Generate ramp-up profile: gradually increase VUs over time."""
    ramp_duration = 300
    stage_count = 5

    stages = []
    for i in range(1, stage_count + 1):
        vus = int(target_vus * (i / stage_count))
        stages.append(asdict(VUStage(
            duration_seconds=ramp_duration // stage_count,
            target_vus=vus,
            description=f"Ramp-up stage {i}: {vus} VUs"
        )))

    stages.append(asdict(VUStage(
        duration_seconds=total_duration_seconds - ramp_duration,
        target_vus=target_vus,
        description="Steady state"
    )))

    think_time = max(1.0, (target_vus / target_rps) - 0.5)

    return LoadProfile(
        profile_type="ramp-up",
        total_duration_seconds=total_duration_seconds,
        stages=stages,
        think_time_seconds=think_time,
        target_p95_latency_ms=target_p95_ms,
        target_error_rate_pct=1.0,
        target_throughput_rps=target_rps,
    )


def calculate_spike_profile(
    target_vus: int,
    target_p95_ms: float,
    target_rps: float,
) -> LoadProfile:
    """Generate spike profile: sudden jump in load."""
    stages = [
        asdict(VUStage(duration_seconds=60, target_vus=5, description="Baseline load (5 VUs)")),
        asdict(VUStage(duration_seconds=180, target_vus=target_vus, description=f"Spike: jump to {target_vus} VUs")),
        asdict(VUStage(duration_seconds=120, target_vus=5, description="Recovery to baseline")),
    ]

    think_time = max(1.0, (target_vus / target_rps) - 0.5)

    return LoadProfile(
        profile_type="spike",
        total_duration_seconds=360,
        stages=stages,
        think_time_seconds=think_time,
        target_p95_latency_ms=target_p95_ms,
        target_error_rate_pct=1.0,
        target_throughput_rps=target_rps,
    )


def calculate_soak_profile(
    target_vus: int,
    target_p95_ms: float,
    target_rps: float,
) -> LoadProfile:
    """Generate soak profile: sustained load over long time."""
    stages = [
        asdict(VUStage(duration_seconds=300, target_vus=target_vus, description=f"Ramp to {target_vus} VUs")),
        asdict(VUStage(duration_seconds=3600, target_vus=target_vus, description="Sustained load (1 hour)")),
    ]

    think_time = max(1.0, (target_vus / target_rps) - 0.5)

    return LoadProfile(
        profile_type="soak",
        total_duration_seconds=3900,
        stages=stages,
        think_time_seconds=think_time,
        target_p95_latency_ms=target_p95_ms,
        target_error_rate_pct=1.0,
        target_throughput_rps=target_rps,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate load profile from SLA targets")
    parser.add_argument("--target-p95-ms", type=float, required=True, help="Target p95 latency (ms)")
    parser.add_argument("--target-rps", type=float, required=True, help="Target throughput (requests/sec)")
    parser.add_argument("--target-vus", type=int, default=None, help="Target VUs (auto-calc if omitted)")
    parser.add_argument("--profile", default="ramp-up", help="ramp-up | spike | soak")
    parser.add_argument("--output", default="profile.json", help="Output JSON file")
    args = parser.parse_args()

    target_vus = args.target_vus or int(args.target_rps * 2)

    if args.profile == "spike":
        profile = calculate_spike_profile(target_vus, args.target_p95_ms, args.target_rps)
    elif args.profile == "soak":
        profile = calculate_soak_profile(target_vus, args.target_p95_ms, args.target_rps)
    else:
        profile = calculate_ramp_up_profile(target_vus, args.target_p95_ms, args.target_rps)

    with open(args.output, 'w') as f:
        json.dump(asdict(profile), f, indent=2)

    print(f"Load profile generated: {args.output}")
    print(f"Profile: {profile.profile_type}")
    print(f"Total duration: {profile.total_duration_seconds}s")
    print(f"Max VUs: {profile.stages[-1]['target_vus']}")
    print(f"Think time: {profile.think_time_seconds:.1f}s")


if __name__ == "__main__":
    main()
