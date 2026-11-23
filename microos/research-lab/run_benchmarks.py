#!/usr/bin/env python3
"""
Automated Multi-Core Scheduling Benchmark Suite
Executes the experimental matrix specified in Tadigotla Vasanth Diwakar's Research Paper:
- Table 1: Effect of Processor Affinity (none, spread, single)
- Table 2: Effect of Workload Distribution (block, rr, dynamic)
- Table 3: Effect of Worker Count (1, 2, 4, 8)
- Generates CSV and JSON reports in reports/
"""

import os
import sys
import json
import csv
import time
from sched_exp import run_once, BACKEND

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

CSV_FILE = os.path.join(REPORTS_DIR, "benchmark_results.csv")
JSON_FILE = os.path.join(REPORTS_DIR, "benchmark_summary.json")

def run_experiment_matrix(tasks=2000, chunk=10, repeats=5):
    print("=" * 72)
    print(" MICROOS MULTI-CORE SCHEDULING RESEARCH BENCHMARK")
    print(f" Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270) | Backend: {BACKEND}")
    print(f" Workload: {tasks} tasks (10% heavy=200 units, 90% light=20 units)")
    print(f" Trials: {repeats} per configuration")
    print("=" * 72)

    raw_records = []

    # -------------------------------------------------------------
    # Experiment 1 (Table 1): Effect of Processor Affinity
    # Workers=4, dist=dynamic, mode in [none, spread, single]
    # -------------------------------------------------------------
    print("\n--- EXPERIMENT 1: EFFECT OF PROCESSOR AFFINITY (Workers=4, Dist=dynamic) ---")
    affinity_modes = ["none", "spread", "single"]
    for mode in affinity_modes:
        print(f"\n[Affinity Mode: {mode.upper()}] Running {repeats} trials...")
        for r in range(1, repeats + 1):
            wall, tp, imb = run_once(mode=mode, dist="dynamic", workers=4, n_tasks=tasks, chunk=chunk)
            print(f"  Trial {r}/{repeats}: Time={wall:.4f}s | Throughput={tp:.2f} tasks/s | Imbalance={imb:.3f}")
            raw_records.append({
                "experiment": "affinity_mode",
                "mode": mode,
                "dist": "dynamic",
                "workers": 4,
                "trial": r,
                "time_s": round(wall, 4),
                "throughput_tasks_s": round(tp, 2),
                "load_imbalance": round(imb, 3)
            })

    # -------------------------------------------------------------
    # Experiment 2 (Table 2): Effect of Workload Distribution
    # Workers=4, mode=none, dist in [block, rr, dynamic]
    # -------------------------------------------------------------
    print("\n--- EXPERIMENT 2: EFFECT OF WORKLOAD DISTRIBUTION (Workers=4, Mode=none) ---")
    dist_methods = ["block", "rr", "dynamic"]
    for dist in dist_methods:
        print(f"\n[Distribution: {dist.upper()}] Running {repeats} trials...")
        for r in range(1, repeats + 1):
            wall, tp, imb = run_once(mode="none", dist=dist, workers=4, n_tasks=tasks, chunk=chunk)
            print(f"  Trial {r}/{repeats}: Time={wall:.4f}s | Throughput={tp:.2f} tasks/s | Imbalance={imb:.3f}")
            raw_records.append({
                "experiment": "workload_distribution",
                "mode": "none",
                "dist": dist,
                "workers": 4,
                "trial": r,
                "time_s": round(wall, 4),
                "throughput_tasks_s": round(tp, 2),
                "load_imbalance": round(imb, 3)
            })

    # -------------------------------------------------------------
    # Experiment 3 (Table 3): Effect of Worker Count
    # Dist=dynamic, mode=spread, workers in [1, 2, 4, 8]
    # -------------------------------------------------------------
    print("\n--- EXPERIMENT 3: EFFECT OF WORKER COUNT (Dist=dynamic, Mode=spread) ---")
    worker_counts = [1, 2, 4, 8]
    for w in worker_counts:
        print(f"\n[Workers: {w}] Running {repeats} trials...")
        for r in range(1, repeats + 1):
            wall, tp, imb = run_once(mode="spread", dist="dynamic", workers=w, n_tasks=tasks, chunk=chunk)
            print(f"  Trial {r}/{repeats}: Time={wall:.4f}s | Throughput={tp:.2f} tasks/s | Imbalance={imb:.3f}")
            raw_records.append({
                "experiment": "worker_count",
                "mode": "spread",
                "dist": "dynamic",
                "workers": w,
                "trial": r,
                "time_s": round(wall, 4),
                "throughput_tasks_s": round(tp, 2),
                "load_imbalance": round(imb, 3)
            })

    # Write Raw Records to CSV
    print(f"\nWriting raw measurements to {CSV_FILE}...")
    fieldnames = ["experiment", "mode", "dist", "workers", "trial", "time_s", "throughput_tasks_s", "load_imbalance"]
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(raw_records)

    # Calculate Aggregated Summary
    summary = compute_summary(raw_records)
    with open(JSON_FILE, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Summary JSON saved to {JSON_FILE}")
    print_tables(summary)

def compute_summary(records):
    grouped = {}
    for r in records:
        key = (r["experiment"], r["mode"], r["dist"], r["workers"])
        grouped.setdefault(key, []).append(r)

    summary = {
        "metadata": {
            "author": "Tadigotla Vasanth Diwakar",
            "usn": "25BTRCL270",
            "backend": BACKEND,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "table1_affinity": {},
        "table2_distribution": {},
        "table3_workers": {}
    }

    # Baseline for speedup (1 worker)
    baseline_time = 1.0
    for key, items in grouped.items():
        exp, mode, dist, workers = key
        avg_time = sum(x["time_s"] for x in items) / len(items)
        avg_tp = sum(x["throughput_tasks_s"] for x in items) / len(items)
        avg_imb = sum(x["load_imbalance"] for x in items) / len(items)

        if exp == "worker_count" and workers == 1:
            baseline_time = avg_time

    for key, items in grouped.items():
        exp, mode, dist, workers = key
        avg_time = sum(x["time_s"] for x in items) / len(items)
        avg_tp = sum(x["throughput_tasks_s"] for x in items) / len(items)
        avg_imb = sum(x["load_imbalance"] for x in items) / len(items)
        speedup = baseline_time / avg_time if avg_time > 0 else 1.0

        entry = {
            "avg_execution_time_s": round(avg_time, 4),
            "avg_throughput_tasks_s": round(avg_tp, 2),
            "avg_load_imbalance": round(avg_imb, 3),
            "speedup": round(speedup, 2)
        }

        if exp == "affinity_mode":
            summary["table1_affinity"][mode] = entry
        elif exp == "workload_distribution":
            summary["table2_distribution"][dist] = entry
        elif exp == "worker_count":
            summary["table3_workers"][str(workers)] = entry

    return summary

def print_tables(summary):
    print("\n" + "=" * 76)
    print("                     ACADEMIC PAPER RESULTS SUMMARY                     ")
    print("=" * 76)

    # Table 1: Effect of Affinity Mode
    print("\nTABLE 1: EFFECT OF AFFINITY MODE ON PERFORMANCE (Workers=4, Dist=dynamic)")
    print(f"{'Affinity Mode':<26} | {'Avg Time (s)':<14} | {'Avg Throughput (t/s)':<20} | {'Avg Load Imbalance':<18}")
    print("-" * 86)
    for mode, data in summary["table1_affinity"].items():
        print(f"{mode:<26} | {data['avg_execution_time_s']:<14.4f} | {data['avg_throughput_tasks_s']:<20.2f} | {data['avg_load_imbalance']:<18.3f}")

    # Table 2: Effect of Workload Distribution
    print("\nTABLE 2: EFFECT OF WORKLOAD DISTRIBUTION ON PERFORMANCE (Workers=4, Mode=none)")
    print(f"{'Distribution':<26} | {'Avg Time (s)':<14} | {'Avg Throughput (t/s)':<20} | {'Avg Load Imbalance':<18}")
    print("-" * 86)
    for dist, data in summary["table2_distribution"].items():
        print(f"{dist:<26} | {data['avg_execution_time_s']:<14.4f} | {data['avg_throughput_tasks_s']:<20.2f} | {data['avg_load_imbalance']:<18.3f}")

    # Table 3: Effect of Number of Workers
    print("\nTABLE 3: EFFECT OF WORKER COUNT ON PERFORMANCE (Mode=spread, Dist=dynamic)")
    print(f"{'Workers':<10} | {'Avg Time (s)':<14} | {'Avg Throughput (t/s)':<20} | {'Speedup':<12}")
    print("-" * 62)
    for workers, data in summary["table3_workers"].items():
        print(f"{workers:<10} | {data['avg_execution_time_s']:<14.4f} | {data['avg_throughput_tasks_s']:<20.2f} | {data['speedup']:<12.2f}")

    print("\n" + "=" * 76)

if __name__ == "__main__":
    run_experiment_matrix()
