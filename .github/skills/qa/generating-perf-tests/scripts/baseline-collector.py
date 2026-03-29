#!/usr/bin/env python3
"""Collect single-user baseline metrics (latency, CPU, memory).

Usage:
  python baseline-collector.py --url http://localhost:3000 --requests 100 --output baseline.json

Output: JSON with p50/p95/p99 latencies, CPU/memory utilization, throughput.
"""

import argparse
import json
import sys
import subprocess
import time
from dataclasses import dataclass, asdict


@dataclass
class BaselineMetric:
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    mean_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    throughput_rps: float
    error_count: int
    error_rate_pct: float


def collect_metrics(base_url: str, request_count: int = 100) -> BaselineMetric:
    """Run single-user load test and collect metrics."""
    latencies: list = []
    error_count = 0

    print(f"Collecting baseline metrics ({request_count} requests)...")

    for _i in range(request_count):
        start = time.time()
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', base_url],
                capture_output=True,
                timeout=10,
            )
            elapsed = (time.time() - start) * 1000
            latencies.append(elapsed)

            if result.returncode != 0 or int(result.stdout.decode()) >= 400:
                error_count += 1
        except subprocess.TimeoutExpired:
            error_count += 1
            latencies.append(10000)

    latencies.sort()
    n = len(latencies)

    metric = BaselineMetric(
        p50_latency_ms=latencies[n // 2],
        p95_latency_ms=latencies[int(n * 0.95)],
        p99_latency_ms=latencies[int(n * 0.99)],
        mean_latency_ms=sum(latencies) / n,
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        throughput_rps=request_count / (sum(latencies) / 1000) if latencies else 0,
        error_count=error_count,
        error_rate_pct=(error_count / request_count * 100) if request_count > 0 else 0,
    )

    return metric


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect baseline performance metrics")
    parser.add_argument("--url", required=True, help="API URL to test")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests")
    parser.add_argument("--output", default="baseline.json", help="Output JSON file")
    args = parser.parse_args()

    metric = collect_metrics(args.url, args.requests)

    with open(args.output, 'w') as f:
        json.dump(asdict(metric), f, indent=2)

    print(f"Baseline metrics saved: {args.output}")
    print(f"p95 latency: {metric.p95_latency_ms:.0f}ms")
    print(f"Throughput: {metric.throughput_rps:.1f} rps")
    print(f"Error rate: {metric.error_rate_pct:.2f}%")


if __name__ == "__main__":
    main()
