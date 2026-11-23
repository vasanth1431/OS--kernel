#!/usr/bin/env python3
"""
Multi-Core Scheduling Design & Debugging Challenge (CA-3)
Intentionally Defective Block Distributor vs. Round-Robin & Dynamic Queue Repairs.
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Institution: Jain University FET Campus | Course: 25PCCS201 - Operating Systems

Run on Linux:
 python3 ca3_multicore_scheduler_debug.py --self-test
 python3 ca3_multicore_scheduler_debug.py --mode none --dist block --workers 4 --repeat 5
 python3 ca3_multicore_scheduler_debug.py --mode none --dist rr --workers 4 --repeat 5
 python3 ca3_multicore_scheduler_debug.py --mode none --dist dynamic --workers 4 --repeat 5
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
    x = 0
    for i in range(units * 1000):
        x = (x * 31 + i) & 0xFFFFFFFF
    return x

def make_tasks(n):
    # Front-loaded unequal-cost task set: first 10% are 10x costlier
    heavy = n // 10
    return [(i, 200 if i < heavy else 20) for i in range(n)]

def split_tasks(tasks, workers, distribution):
    if distribution == "block":
        # Defective: Contiguous equal-count partition concentrates all heavy tasks in worker 0
        k = len(tasks) // workers
        parts = [tasks[i * k:(i + 1) * k] for i in range(workers - 1)]
        parts.append(tasks[(workers - 1) * k:])
        return parts
    elif distribution == "rr":
        # Repair Option 1: Round-robin interleaves task positions to balance heavy costs
        return [tasks[i::workers] for i in range(workers)]
    raise ValueError(f"Unknown static distribution: {distribution}")

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

def worker(worker_id, mode, cpus, distribution, assigned_tasks,
           task_queue, barrier, output_queue):
    apply_affinity(mode, worker_id, cpus)
    barrier.wait()
    start_time = time.monotonic()
    cpu_start = time.process_time()
    completed_ids = []
    checksum = 0

    if distribution == "dynamic":
        # Repair Option 2: Shared chunk queue dynamically assigns tasks as workers finish
        while True:
            chunk = task_queue.get()
            if chunk is None:
                break
            for task_id, cost in chunk:
                checksum ^= burn(cost)
                completed_ids.append(task_id)
    else:
        for task_id, cost in assigned_tasks:
            checksum ^= burn(cost)
            completed_ids.append(task_id)

    end_time = time.monotonic()
    cpu_end = time.process_time()

    output_queue.put({
        "worker_id": worker_id,
        "start": start_time,
        "end": end_time,
        "busy_time": end_time - start_time,
        "cpu_time": cpu_end - cpu_start,
        "completed_ids": completed_ids,
        "checksum": checksum
    })

def run_once(mode, distribution, workers, n_tasks, chunk_size):
    if hasattr(os, "sched_getaffinity"):
        try:
            cpus = sorted(os.sched_getaffinity(0))
        except Exception:
            cpus = list(range(os.cpu_count() or 4))
    else:
        cpus = list(range(os.cpu_count() or 4))

    tasks = make_tasks(n_tasks)
    barrier = mp.Barrier(workers)
    output_queue = mp.Queue()
    task_queue = mp.Queue()
    parts = [[] for _ in range(workers)]

    if distribution == "dynamic":
        for i in range(0, len(tasks), chunk_size):
            task_queue.put(tasks[i:i + chunk_size])
        for _ in range(workers):
            task_queue.put(None)
    else:
        parts = split_tasks(tasks, workers, distribution)

    processes = [
        mp.Process(
            target=worker,
            args=(w, mode, cpus, distribution, parts[w],
                  task_queue, barrier, output_queue)
        )
        for w in range(workers)
    ]

    for p in processes:
        p.start()

    results = [output_queue.get() for _ in processes]

    for p in processes:
        p.join()

    # Invariant Verification (Task conservation & uniqueness)
    all_completed = []
    for r in results:
        all_completed.extend(r["completed_ids"])
    assert len(all_completed) == n_tasks, f"Task conservation failed: {len(all_completed)} != {n_tasks}"
    assert len(set(all_completed)) == n_tasks, f"Task duplication detected: {len(set(all_completed))} != {n_tasks}"

    wall = max(r["end"] for r in results) - min(r["start"] for r in results)
    busy = [r["busy_time"] for r in results]
    avg_busy = sum(busy) / len(busy)
    imbalance = max(busy) / avg_busy if avg_busy else 1.0

    return {
        "execution_time_s": wall,
        "throughput_tasks_s": n_tasks / wall if wall else 0.0,
        "load_imbalance": imbalance,
        "completed_tasks": len(all_completed),
        "worker_cpu_time_s": sum(r["cpu_time"] for r in results),
        "allowed_cpus": len(cpus)
    }

def run_self_test():
    print("=== Running Multi-Core Scheduler Self-Test ===")
    tasks = make_tasks(2000)
    print(f"[1/3] Generated {len(tasks)} tasks.")
    print(f"      First task cost: {tasks[0][1]} (heavy), Last task cost: {tasks[-1][1]} (normal)")

    # Test Block (defective skew)
    parts_block = split_tasks(tasks, 4, "block")
    cost_block_0 = sum(t[1] for t in parts_block[0])
    cost_block_1 = sum(t[1] for t in parts_block[1])
    print(f"[2/3] Block distribution work costs: Worker 0={cost_block_0}, Worker 1={cost_block_1}")
    assert cost_block_0 > cost_block_1, "Expected block distributor to skew work heavily to worker 0"

    # Test Round-Robin (repaired balance)
    parts_rr = split_tasks(tasks, 4, "rr")
    cost_rr_0 = sum(t[1] for t in parts_rr[0])
    cost_rr_1 = sum(t[1] for t in parts_rr[1])
    print(f"[3/3] Round-Robin work costs: Worker 0={cost_rr_0}, Worker 1={cost_rr_1}")
    assert cost_rr_0 == cost_rr_1, "Expected round-robin distributor to achieve balanced estimated cost"

    print("✔ Self-test passed: Invariants and defect-repair mechanics verified!\n")

def main():
    parser = argparse.ArgumentParser(description="CA-3 Multi-Core Scheduler Debugging Challenge")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic partition verification")
    parser.add_argument("--mode", choices=["none", "spread", "single"], default="none")
    parser.add_argument("--dist", choices=["block", "rr", "dynamic"], default="block")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--tasks", type=int, default=2000)
    parser.add_argument("--chunk", type=int, default=10)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--csv", default="ca3_scheduler_results.csv")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    rows = []
    for r in range(1, args.repeat + 1):
        res = run_once(args.mode, args.dist, args.workers, args.tasks, args.chunk)
        row = {
            "run": r,
            "mode": args.mode,
            "distribution": args.dist,
            "workers": args.workers,
            "tasks": args.tasks,
            "chunk": args.chunk,
            **res
        }
        rows.append(row)
        print(f"run={r} mode={args.mode} dist={args.dist} workers={args.workers} "
              f"time={res['execution_time_s']:.6f}s throughput={res['throughput_tasks_s']:.2f} t/s "
              f"imbalance={res['load_imbalance']:.3f}")

    if rows:
        fieldnames = list(rows[0].keys())
        write_header = not os.path.exists(args.csv)
        with open(args.csv, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                w.writeheader()
            w.writerows(rows)
        print(f"Results successfully saved to {args.csv}")

if __name__ == "__main__":
    main()
