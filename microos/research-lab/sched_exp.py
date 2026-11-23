#!/usr/bin/env python3
"""
Multi-Core Scheduling Experiment: Processor Affinity & Workload Distribution
Academic Research Module for MicroOS v1.0
Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Institution: Jain University, FET Campus (25PCCS201 Operating Systems Research Activity)
"""

import os
import sys
import time
import argparse
import multiprocessing as mp

# Try importing the optional compiled CPU kernel, else use pure-Python burn kernel
try:
    import cpu_kernel  # Built with PyO3/maturin or C-extension
    burn = cpu_kernel.burn
    BACKEND = "rust"
except ImportError:
    def burn(units):
        x = 0
        for i in range(units * 1000):
            x = (x * 31 + i) & 0xFFFFFFFF
        return x
    BACKEND = "python"

def make_tasks(n):
    """
    Generate n tasks with unequal cost:
    The first 10% of tasks are 10x costlier (units=200 vs units=20).
    This intentionally creates workload heterogeneity to measure load imbalance.
    """
    heavy = n // 10
    return [200] * heavy + [20] * (n - heavy)

def split(costs, workers, dist):
    """
    Split task costs among worker processes using static block or round-robin distribution.
    """
    if dist == "block":
        k = len(costs) // workers
        parts = [costs[i * k:(i + 1) * k] for i in range(workers - 1)]
        parts.append(costs[(workers - 1) * k:])
        return parts
    elif dist == "rr":
        # Round-robin assignment in advance
        return [costs[i::workers] for i in range(workers)]
    return [[] for _ in range(workers)]

def pin(mode, wid, cpus):
    """
    Set CPU affinity of the current worker process using Linux os.sched_setaffinity.
    Handles cross-platform execution gracefully if sched_setaffinity is unavailable.
    """
    if not hasattr(os, "sched_setaffinity") or not cpus:
        return  # Non-Linux host (e.g. Windows development environment)

    try:
        if mode == "spread":
            os.sched_setaffinity(0, {cpus[wid % len(cpus)]})
        elif mode == "single":
            os.sched_setaffinity(0, {cpus[0]})
        elif mode == "none":
            # Default scheduler: allow execution across all available logical cores
            os.sched_setaffinity(0, set(cpus))
    except Exception:
        pass

def worker(wid, mode, cpus, dist, my_costs, task_q, barrier, out_q):
    """
    Worker process: pins CPU affinity, synchronizes at barrier, executes tasks,
    and returns wall-clock timing and throughput data.
    """
    pin(mode, wid, cpus)
    barrier.wait()
    t0 = time.monotonic()
    done = 0

    if dist == "dynamic":
        while True:
            chunk = task_q.get()
            if chunk is None:
                break
            for c in chunk:
                burn(c)
                done += 1
    else:
        for c in my_costs:
            burn(c)
            done += 1

    t_end = time.monotonic()
    out_q.put((wid, t0, t_end, done))

def run_once(mode, dist, workers, n_tasks, chunk):
    """
    Execute a single benchmark run with specified affinity mode, distribution, and worker count.
    """
    if hasattr(os, "sched_getaffinity"):
        try:
            cpus = sorted(os.sched_getaffinity(0))
        except Exception:
            cpus = list(range(os.cpu_count() or 4))
    else:
        cpus = list(range(os.cpu_count() or 4))

    costs = make_tasks(n_tasks)
    barrier = mp.Barrier(workers)
    out_q = mp.Queue()
    task_q = mp.Queue()

    if dist == "dynamic":
        for i in range(0, len(costs), chunk):
            task_q.put(costs[i:i + chunk])
        for _ in range(workers):
            task_q.put(None)
        parts = [[] for _ in range(workers)]
    else:
        parts = split(costs, workers, dist)

    procs = [
        mp.Process(target=worker, args=(w, mode, cpus, dist, parts[w], task_q, barrier, out_q))
        for w in range(workers)
    ]

    for p in procs:
        p.start()

    # Collect results from all workers before joining to prevent queue deadlocks
    results = [out_q.get() for _ in procs]

    for p in procs:
        p.join()

    wall = max(r[2] for r in results) - min(r[1] for r in results)
    busy = [r[2] - r[1] for r in results]
    done = sum(r[3] for r in results)
    avg_busy = sum(busy) / len(busy)
    imbalance = max(busy) / avg_busy if avg_busy > 0 else 1.0

    return wall, done / wall, imbalance

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Multi-Core Scheduling Benchmark")
    ap.add_argument("--mode", default="none", choices=["none", "spread", "single"], help="Processor affinity mode")
    ap.add_argument("--dist", default="dynamic", choices=["block", "rr", "dynamic"], help="Workload distribution")
    ap.add_argument("--workers", type=int, default=4, help="Number of worker processes")
    ap.add_argument("--tasks", type=int, default=2000, help="Total number of tasks")
    ap.add_argument("--chunk", type=int, default=10, help="Dynamic queue chunk size")
    ap.add_argument("--repeat", type=int, default=5, help="Number of repetitions")
    a = ap.parse_args()

    for r in range(1, a.repeat + 1):
        t, tp, imb = run_once(a.mode, a.dist, a.workers, a.tasks, a.chunk)
        print(f"[{BACKEND}] run={r} mode={a.mode} dist={a.dist} "
              f"workers={a.workers} time={t:.4f}s "
              f"throughput={tp:.2f} tasks/s imbalance={imb:.3f}")
