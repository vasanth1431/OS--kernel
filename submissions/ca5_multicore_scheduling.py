#!/usr/bin/env python3
"""
Continuous Assessment 5 (CA-5): Linux Systems Engineering Challenge
Topic: Multi-Core Scheduling — Processor Affinity & Workload Distribution
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Institution: Jain University FET Campus | Course: 25PCCS201 - Operating Systems

Features:
- Linux /proc/self/status context switch instrumentation (voluntary & involuntary)
- Processor affinity control via os.sched_setaffinity (spread, single, none)
- Workload distributions: static block, static round-robin, dynamic shared queue
- Raw CSV trial logger for statistical evidence and Viva defense
"""

import argparse
import csv
import multiprocessing as mp
import os
import platform
import statistics
import sys
import time

def read_context_switches():
    """Read this process's context-switch counters from /proc/self/status."""
    values = {"voluntary": 0, "involuntary": 0}
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("voluntary_ctxt_switches:"):
                    values["voluntary"] = int(line.split()[1])
                elif line.startswith("nonvoluntary_ctxt_switches:"):
                    values["involuntary"] = int(line.split()[1])
    except OSError:
        pass
    return values

def burn(units):
    """Deterministic CPU-bound kernel; identical in every configuration."""
    x = 0
    for i in range(units * 1000):
        x = (x * 31 + i) & 0xFFFFFFFF
    return x

def make_tasks(task_count):
    """Fixed task list: first 10% cost 10x more, intentionally stressing block order."""
    heavy = task_count // 10
    return [200] * heavy + [20] * (task_count - heavy)

def split_tasks(costs, workers, distribution):
    if distribution == "block":
        q, r = divmod(len(costs), workers)
        parts, start = [], 0
        for worker_id in range(workers):
            size = q + (1 if worker_id < r else 0)
            parts.append(costs[start:start + size])
            start += size
        return parts
    elif distribution == "rr":
        return [costs[i::workers] for i in range(workers)]
    raise ValueError("Static distribution must be block or rr")

def apply_affinity(mode, worker_id, allowed_cpus):
    if not hasattr(os, "sched_setaffinity") or not allowed_cpus:
        return
    try:
        if mode == "spread":
            cpu = allowed_cpus[worker_id % len(allowed_cpus)]
            os.sched_setaffinity(0, {cpu})
        elif mode == "single":
            os.sched_setaffinity(0, {allowed_cpus[0]})
        elif mode != "none":
            raise ValueError("Unknown affinity mode: " + mode)
    except Exception:
        pass

def worker(worker_id, mode, allowed_cpus, distribution, assigned_costs,
           task_queue, barrier, output_queue):
    apply_affinity(mode, worker_id, allowed_cpus)
    effective_cpus = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
    barrier.wait()
    ctx_before = read_context_switches()
    cpu_before = time.process_time()
    start = time.monotonic()

    completed = 0
    checksum = 0
    if distribution == "dynamic":
        while True:
            chunk = task_queue.get()
            if chunk is None:
                break
            for cost in chunk:
                checksum ^= burn(cost)
                completed += 1
    else:
        for cost in assigned_costs:
            checksum ^= burn(cost)
            completed += 1

    end = time.monotonic()
    cpu_after = time.process_time()
    ctx_after = read_context_switches()

    output_queue.put({
        "worker_id": worker_id,
        "start": start,
        "end": end,
        "busy_time_s": end - start,
        "cpu_time_s": cpu_after - cpu_before,
        "completed_tasks": completed,
        "voluntary_context_switches": max(0, ctx_after["voluntary"] - ctx_before["voluntary"]),
        "involuntary_context_switches": max(0, ctx_after["involuntary"] - ctx_before["involuntary"]),
        "effective_cpus": ",".join(map(str, effective_cpus)),
        "checksum": checksum,
    })

def run_once(mode, distribution, workers, task_count, chunk_size):
    if hasattr(os, "sched_getaffinity"):
        try:
            allowed_cpus = sorted(os.sched_getaffinity(0))
        except Exception:
            allowed_cpus = list(range(os.cpu_count() or 4))
    else:
        allowed_cpus = list(range(os.cpu_count() or 4))

    costs = make_tasks(task_count)
    barrier = mp.Barrier(workers)
    output_queue = mp.Queue()
    task_queue = mp.Queue()
    assigned = [[] for _ in range(workers)]

    if distribution == "dynamic":
        for i in range(0, len(costs), chunk_size):
            task_queue.put(costs[i:i + chunk_size])
        for _ in range(workers):
            task_queue.put(None)
    else:
        assigned = split_tasks(costs, workers, distribution)

    processes = []
    for worker_id in range(workers):
        p = mp.Process(
            target=worker,
            args=(worker_id, mode, allowed_cpus, distribution,
                  assigned[worker_id], task_queue, barrier, output_queue)
        )
        processes.append(p)
        p.start()

    results = [output_queue.get() for _ in processes]
    for p in processes:
        p.join()

    wall_start = min(row["start"] for row in results)
    wall_end = max(row["end"] for row in results)
    elapsed = wall_end - wall_start
    busy = [row["busy_time_s"] for row in results]
    avg_busy = statistics.mean(busy) if busy else 0.0
    imbalance = max(busy) / avg_busy if avg_busy else 0.0
    completed = sum(row["completed_tasks"] for row in results)

    return {
        "execution_time_s": elapsed,
        "throughput_tasks_s": completed / elapsed if elapsed else 0.0,
        "load_imbalance": imbalance,
        "completed_tasks": completed,
        "allowed_cpu_count": len(allowed_cpus),
        "worker_cpu_time_s": sum(row["cpu_time_s"] for row in results),
        "voluntary_context_switches": sum(row["voluntary_context_switches"] for row in results),
        "involuntary_context_switches": sum(row["involuntary_context_switches"] for row in results),
        "worker_cpu_masks": ";".join(row["effective_cpus"] for row in sorted(results, key=lambda x: x["worker_id"])),
        "worker_busy_times_s": ";".join("{:.6f}".format(row["busy_time_s"]) for row in sorted(results, key=lambda x: x["worker_id"])),
    }

def main():
    parser = argparse.ArgumentParser(description="CA-5 Linux multi-core scheduling experiment")
    parser.add_argument("--mode", choices=("none", "spread", "single"), default="none",
                        help="none=Linux default; spread=one allowed CPU per worker; single=all workers on one CPU")
    parser.add_argument("--dist", choices=("block", "rr", "dynamic"), default="dynamic",
                        help="task distribution: contiguous blocks, round-robin, or shared queue")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--tasks", type=int, default=2000)
    parser.add_argument("--chunk", type=int, default=10, help="dynamic queue chunk size")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--csv", default="ca5_sched_results.csv")
    args = parser.parse_args()

    rows = []
    for trial in range(1, args.repeat + 1):
        metrics = run_once(args.mode, args.dist, args.workers, args.tasks, args.chunk)
        row = {
            "trial": trial,
            "affinity_mode": args.mode,
            "distribution": args.dist,
            "workers": args.workers,
            "tasks": args.tasks,
            "chunk_size": args.chunk,
            **metrics,
        }
        rows.append(row)
        print(
            "trial={:d} time={:.6f}s throughput={:.2f} tasks/s imbalance={:.3f} "
            "voluntary_cs={} involuntary_cs={}".format(
                trial, metrics["execution_time_s"], metrics["throughput_tasks_s"],
                metrics["load_imbalance"], metrics["voluntary_context_switches"],
                metrics["involuntary_context_switches"]
            )
        )

    fields = list(rows[0].keys())
    file_exists = os.path.exists(args.csv) and os.path.getsize(args.csv) > 0
    with open(args.csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    print(f"\nRaw trial data successfully appended to: {args.csv}")

if __name__ == "__main__":
    main()
