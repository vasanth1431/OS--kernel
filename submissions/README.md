# Academic Submissions Index (CA-2, CA-3, CA-5 & OS Lab Record)
## Course: 25PCCS201 – Operating Systems & Systems Programming
**Institution**: Faculty of Engineering & Technology (FET), Jain (Deemed-to-be University)  
**Student**: Tadigotla Vasanth Diwakar  
**USN**: `25BTRCL270` | **Branch**: CSE-AIML-E  
**Research Theme**: *Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution on Execution Performance*  

---

## 📂 Submissions Directory Structure

```text
submissions/
├── CA2_Performance_Investigation_25BTRCL270.pdf      # CA-2 Official Submission PDF (18 Pages)
├── CA3_Design_and_Debugging_Challenge_25BTRCL270.pdf # CA-3 Official Submission PDF (8 Pages)
├── CA5_Linux_Systems_Engineering_25BTRCL270.pdf      # CA-5 Official Submission PDF (11 Pages)
├── OS_Lab_Record_Vasanth_25BTRCL270.pdf              # OS Laboratory Record PDF (7 Pages)
├── OS_LAB_RECORD.md                                  # Complete Lab Experiments & Terminal Logs (Markdown)
├── ca2_sched_exp.py                                  # CA-2 Python Benchmark Script (Multiprocessing & Affinity)
├── ca3_multicore_scheduler_debug.py                  # CA-3 Defect Diagnosis & Repair Script (--self-test)
├── ca5_multicore_scheduling.py                       # CA-5 Linux Systems Engineering Script (/proc instrumentation)
└── README.md                                         # This Submission Summary Index
```

---

## 📑 Assessment Summaries & Deliverables

### 1. CA-2: Performance Investigation (18 Pages)
- **Document**: [`CA2_Performance_Investigation_25BTRCL270.pdf`](./CA2_Performance_Investigation_25BTRCL270.pdf)
- **Executable Script**: [`ca2_sched_exp.py`](./ca2_sched_exp.py)
- **Objective**: Empirical performance investigation of Linux processor affinity modes (`none`, `spread`, `single`) and workload distribution policies (`block`, `round-robin`, `dynamic`) under heterogeneous CPU-bound task costs.
- **Run Command**:
  ```bash
  python3 submissions/ca2_sched_exp.py --mode spread --dist dynamic --workers 4 --repeat 5
  ```

---

### 2. CA-3: OS Design & Debugging Challenge (8 Pages, 10 Marks)
- **Document**: [`CA3_Design_and_Debugging_Challenge_25BTRCL270.pdf`](./CA3_Design_and_Debugging_Challenge_25BTRCL270.pdf)
- **Executable Script**: [`ca3_multicore_scheduler_debug.py`](./ca3_multicore_scheduler_debug.py)
- **Challenge Alignment**: Category B, B4 (Scheduling Policy Selection) & B3 (Excessive Context Switching).
- **Core Diagnosis**: Diagnoses an intentionally defective user-space block distributor that assumes task-count equality equals work equality, concentrating expensive front-loaded tasks on Worker 0 and causing high load imbalance.
- **Engineered Repairs**:
  1. *Round-Robin Static Slicing* (`--dist rr`): Interleaves task indices, distributing expensive front-loaded work evenly with zero runtime queue overhead.
  2. *Dynamic Shared Chunk Queue* (`--dist dynamic`): Adapts to runtime worker speeds via shared task queue.
- **Invariants Verified**: Task conservation (all 2,000 tasks executed exactly once) and zero duplication.
- **Run Self-Test & Repair Verification**:
  ```bash
  # 1. Run deterministic partition and task conservation self-test
  python3 submissions/ca3_multicore_scheduler_debug.py --self-test

  # 2. Run defective block baseline (exposing load imbalance)
  python3 submissions/ca3_multicore_scheduler_debug.py --mode none --dist block --workers 4 --repeat 5

  # 3. Run round-robin repair (demonstrating balanced execution)
  python3 submissions/ca3_multicore_scheduler_debug.py --mode none --dist rr --workers 4 --repeat 5
  ```

---

### 3. CA-5: Linux Systems Engineering Challenge (11 Pages, 10 Marks)
- **Document**: [`CA5_Linux_Systems_Engineering_25BTRCL270.pdf`](./CA5_Linux_Systems_Engineering_25BTRCL270.pdf)
- **Executable Script**: [`ca5_multicore_scheduling.py`](./ca5_multicore_scheduling.py)
- **Challenge Alignment**: Challenge L6 (CPU Affinity Investigation), supported by L7 (Scheduling Observation) and L35 (CPU Saturation Investigation).
- **Linux Instrumentation**:
  - Direct reading of `/proc/self/status` for process voluntary and non-voluntary context switches.
  - Linux `os.sched_setaffinity` and `os.sched_getaffinity` CPU mask verification.
  - Multi-worker scalability analysis (1, 2, 4, 8 cores).
- **Run Command**:
  ```bash
  python3 submissions/ca5_multicore_scheduling.py --mode spread --dist dynamic --workers 4 --repeat 5 --csv ca5_sched_results.csv
  ```

---

### 4. Operating Systems Laboratory Record (7 Pages)
- **Document**: [`OS_Lab_Record_Vasanth_25BTRCL270.pdf`](./OS_Lab_Record_Vasanth_25BTRCL270.pdf)
- **Online Markdown Edition**: [`OS_LAB_RECORD.md`](./OS_LAB_RECORD.md)
- **Student Ownership**: Verified for user `vasanth` on host `VASANTH`.
- **Experiments Included**:
  1. *UNIX Basics & Shell*: Directory listing, file operations, permissions, `simulate_cp.c`, and Shell scripts (Even/Odd, Leap Year, Swap).
  2. *Processes & IPC*: PID Management using a Bitmap, Collatz sequence, Bidirectional IPC using pipes, custom UNIX shell project (`myshell`), and `/proc` process telemetry (`pid.py`).
  3. *Threads & Concurrency*: Multithreading and shared results, Sudoku validator with 27 threads, multithreaded sorting.
  4. *Synchronization*: Thread-safe resource manager using mutexes, Bounded Buffer (Producer-Consumer), Readers-Writers, and Dining Philosophers.
  5. *Deadlocks*: Banker's Algorithm safety check, Deadlock Detection simulation, and Resource Ordering Prevention.
  6. *Memory & Storage*: Fixed & Dynamic memory partition allocation, Page table translation, Virtual Memory replacement (FIFO, LRU, Optimal), and Disk Scheduling (FCFS, SSTF, SCAN).

---

## 🛠️ Verification & Academic Integrity
- **Authenticity**: All assessments preserve the original research question and experimental parameters developed by Tadigotla Vasanth Diwakar (USN: `25BTRCL270`).
- **Reproducibility**: All three Python scripts are self-contained and run on standard Linux/POSIX environments with standard CPython libraries (`multiprocessing`, `os`, `time`, `statistics`, `argparse`, `csv`).
- **GitHub Repository**: [https://github.com/vasanth1431/OS--kernel](https://github.com/vasanth1431/OS--kernel)
