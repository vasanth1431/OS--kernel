#!/usr/bin/env python3
"""
Multi-Core Scheduling CA-2 Performance Investigation
Compare Linux CPU affinity and workload distribution.
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Institution: Jain University FET Campus | Course: 25PCCS201 - Operating Systems

Run on Linux:
 python3 ca2_sched_exp.py --mode none --dist dynamic --workers 4 --repeat 5
 python3 ca2_sched_exp.py --mode spread --dist block --workers 4 --repeat 5
 python3 ca2_sched_exp.py --mode single --dist rr --workers 4 --repeat 5
"""

import argparse
import csv
import multiprocessing as mp
import os
import platform
import statistics
import sys
import time

def burn(units):
    """Deterministic CPU-bound work; identical for every configuration."""
    x = 0
    for i in range(units * 1000):
        x = (x * 31 + i) & 0xFFFFFFFF
    return x

def make_tasks(n):
    # First 10% of tasks are 10x more expensive, creating an imbalanced workload.
    heavy = n // 10
    return [200] * heavy + [20] * (n - heavy)

def split_tasks(costs, workers, distribution):
    if distribution == "block":
        k = len(costs) // workers
        parts = [costs[i * k:(i + 1) * k] for i in range(workers - 1)]
        parts.append(costs[(workers - 1) * k:])
        return parts
    if distribution == "rr":
        return [costs[i::workers] for i in range(workers)]
    raise ValueError("Static split supports only block and rr")

def apply_affinity(mode, worker_id, cpus):
    if not hasattr(os, "sched_setaffinity") or not cpus:
        return
    try:
        if mode == "spread":
            os.sched_setaffinity(0, {cpus[worker_id % len(cpus)]})
        elif mode == "single":
            os.sched_setaffinity(0, {cpus[0]})
        elif mode != "none":
            raise ValueError(f"Unknown affinity mode: {mode}")
    except Exception:
        pass

def worker(worker_id, mode, cpus, distribution, my_costs,
           task_queue, barrier, output_queue):
    apply_affinity(mode, worker_id, cpus)
    barrier.wait()
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
        for cost in my_costs:
            checksum ^= burn(cost)
            completed += 1
    end = time.monotonic()
    output_queue.put((worker_id, start, end, completed, checksum))

def run_once(mode, distribution, workers, n_tasks, chunk_size):
    if hasattr(os, "sched_getaffinity"):
        try:
            cpus = sorted(os.sched_getaffinity(0))
        except Exception:
            cpus = list(range(os.cpu_count() or 4))
    else:
        cpus = list(range(os.cpu_count() or 4))

    costs = make_tasks(n_tasks)
    barrier = mp.Barrier(workers)
    output_queue = mp.Queue()
    task_queue = mp.Queue()
    parts = [[] for _ in range(workers)]

    if distribution == "dynamic":
        for i in range(0, len(costs), chunk_size):
            task_queue.put(costs[i:i + chunk_size])
        for _ in range(workers):
            task_queue.put(None)
    else:
        parts = split_tasks(costs, workers, distribution)

    processes = [
        mp.Process(
            target=worker,
            args=(wid, mode, cpus, distribution, parts[wid],
                  task_queue, barrier, output_queue)
        )
        for wid in range(workers)
    ]

    for process in processes:
        process.start()

    results = [output_queue.get() for _ in processes]

    for process in processes:
        process.join()

    wall_time = max(row[2] for row in results) - min(row[1] for row in results)
    busy_times = [row[2] - row[1] for row in results]
    completed = sum(row[3] for row in results)
    average_busy = sum(busy_times) / len(busy_times)
    imbalance = max(busy_times) / average_busy if average_busy else 0.0
    throughput = completed / wall_time if wall_time else 0.0

    return {
        "execution_time_s": wall_time,
        "throughput_tasks_s": throughput,
        "load_imbalance": imbalance,
        "completed_tasks": completed,
        "allowed_cpus": len(cpus),
    }

def main():
    parser = argparse.ArgumentParser(description="CA-2 Multi-Core Scheduling Investigation")
    parser.add_argument("--mode", choices=["none", "spread", "single"], default="none")
    parser.add_argument("--dist", choices=["block", "rr", "dynamic"], default="dynamic")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--tasks", type=int, default=2000)
    parser.add_argument("--chunk", type=int, default=10)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--csv", default="ca2_sched_results.csv")
    args = parser.parse_args()

    if args.workers < 1 or args.tasks < 1 or args.chunk < 1 or args.repeat < 1:
        parser.error("workers, tasks, chunk, and repeat must be positive integers")

    rows = []
    for run_number in range(1, args.repeat + 1):
        result = run_once(args.mode, args.dist, args.workers, args.tasks, args.chunk)
        row = {
            "run": run_number,
            "mode": args.mode,
            "distribution": args.dist,
            "workers": args.workers,
            "tasks": args.tasks,
            "chunk": args.chunk,
            **result,
        }
        rows.append(row)
        print(
            f"run={run_number} mode={args.mode} dist={args.dist} "
            f"workers={args.workers} time={result['execution_time_s']:.6f}s "
            f"throughput={result['throughput_tasks_s']:.2f} tasks/s "
            f"imbalance={result['load_imbalance']:.3f}"
        )

    fieldnames = list(rows[0].keys())
    write_header = not os.path.exists(args.csv)
    with open(args.csv, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    times = [r["execution_time_s"] for r in rows]
    throughputs = [r["throughput_tasks_s"] for r in rows]
    imbalances = [r["load_imbalance"] for r in rows]
    print("\n--- SUMMARY ---")
    print(f"Average execution time: {statistics.mean(times):.6f} s")
    print(f"Average throughput: {statistics.mean(throughputs):.2f} tasks/s")
    print(f"Average load imbalance: {statistics.mean(imbalances):.3f}")
    print(f"Python: {sys.version.split()[0]} | Platform: {platform.platform()}")
    print(f"Raw runs appended to: {args.csv}")

if __name__ == "__main__":
    main()
