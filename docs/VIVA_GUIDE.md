# MicroOS & Multi-Core Scheduling — Viva Examination Preparation Guide

**Candidate**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Branch**: CSE-AIML (Section E)  
**Subject**: 25PCCS201 Operating Systems Research Activity  
**Institution**: Faculty of Engineering and Technology, Jain (Deemed-to-be University)

---

## 1. High-Level Project Pitch (30-Second Opening)

> *"Good morning respected examiners. My project is **MicroOS Version 1.0**, an independent modular Linux engineering and research operating system built upon Ubuntu 24.04 LTS with an asymmetric XFCE engineering desktop. Alongside custom system monitoring, genuine NetworkManager wireless hardware scanning, and an educational bare-metal kernel lab, the core academic component is an experimental research module investigating: **'Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution on Execution Performance'**. We empirically evaluated how CPU pinning and dynamic work queue dispatching mitigate cache thrashing and load imbalance across multi-core processors."*

---

## 2. Core Concepts & Definitions You Must Know

### Q1: What is Processor Affinity (CPU Pinning)?
**Answer**: Processor affinity is an operating system mechanism that binds a thread or process to a specific set of CPU cores. In Linux, it is managed by the system call `sched_setaffinity(2)` or CLI `taskset`.
- **Soft Affinity**: The default kernel scheduler preference to keep a thread on the same CPU core to preserve CPU cache warmness, while reserving the freedom to migrate it if cores become unbalanced.
- **Hard Affinity**: A strict constraint where the thread is forbidden from executing on any other core, even if other cores sit completely idle.

### Q2: What is the difference between Static and Dynamic Workload Distribution?
**Answer**:
- **Static Distribution (Block / Round-Robin)**: All tasks are pre-divided among worker processes at launch time before execution begins. It requires zero lock synchronization during runtime, but if task execution costs are unequal, it causes severe **load imbalance** (some workers finish early while others struggle with heavy tasks).
- **Dynamic Distribution (Shared Queue)**: Workers pull small chunks of work on-demand from a shared thread-safe queue. Faster workers naturally pull more work, achieving near-perfect load balance at the cost of slight queue synchronization overhead.

### Q3: Why did you use Python multiprocessing instead of multithreading?
**Answer**: In standard CPython, the **Global Interpreter Lock (GIL)** restricts Python bytecode execution to a single OS thread at a time, preventing true CPU-bound multi-core parallelism. By using `multiprocessing`, each worker is an independent OS process with its own memory space and PID, allowing true concurrent execution across physical CPU cores and direct invocation of `os.sched_setaffinity`.

### Q4: How is Load Imbalance Factor calculated?
**Answer**:
$$\lambda_{\text{imb}} = \frac{\text{Maximum Worker Busy Time}}{\text{Average Worker Busy Time}}$$
If all 4 workers take exactly 5.0 seconds, $\lambda_{\text{imb}} = 5.0 / 5.0 = 1.0$ (perfect balance). If one worker takes 10.0 seconds and the others take 2.0 seconds, $\lambda_{\text{imb}} = 10.0 / 4.0 = 2.5$ (severe imbalance).

### Q5: What is the difference between MicroOS and the Linux Kernel?
**Answer**:
- **MicroOS** is a complete **Linux Distribution** containing the desktop environment (XFCE), display manager (LightDM), package manager (APT), shell utilities (MicroShell), and engineering applications.
- The **Linux Kernel** is the underlying monolithic core (v6.8 LTS) managing virtual memory paging, process scheduling, and hardware drivers.
- The **Kernel Lab** is our separate, freestanding educational x86 bare-metal kernel written in Assembly and C to demonstrate low-level GDT, IDT, PIC, and VGA drivers from scratch.

---

## 3. Top Viva Questions & Answers

### Q6: Why did 'Single' affinity mode run almost 4 times slower than 'Spread' on 4 workers?
**Answer**: When all 4 CPU-bound worker processes were pinned to Core 0 (`single`), they were forced to time-share a single physical processing core. This converted parallel execution into serialized execution and introduced involuntary context-switching overhead, increasing execution time from ~4.76s to ~18.24s.

### Q7: Why did Round-Robin distribution perform so much better than Block distribution?
**Answer**: Our synthetic workload placed all heavy tasks (cost=200) in the first 10% of the list. Under Block distribution, Worker 0 received all 200 heavy tasks, causing severe load imbalance ($\lambda_{\text{imb}} = 2.418$). Under Round-Robin, the heavy tasks were interleaved evenly across all 4 workers (Worker 0 took task 0, Worker 1 took task 1, etc.), balancing the load effectively without dynamic queue locking.

### Q8: Why does speedup not scale linearly to 8x on 8 workers?
**Answer**: Speedup exhibits diminishing returns due to **Amdahl's Law** and hardware architecture:
1. Synchronization barriers and queue serialization represent a non-parallelizable fraction.
2. If the physical CPU has 4 physical cores and 8 logical threads (via Intel Hyper-Threading or AMD SMT), logical threads share physical ALUs and caches, typically providing only a 20–30% boost rather than a 100% doubling.

### Q9: How does Micro Wi-Fi Scanner work inside VirtualBox?
**Answer**: Oracle VirtualBox normally emulates a virtual wired Ethernet adapter (`enp0s3`) via NAT. Through virtual Ethernet, the guest cannot scan physical Wi-Fi channels. To perform real Wi-Fi scanning, we pass a physical USB Wi-Fi dongle directly to the VM using VirtualBox USB passthrough (`Devices -> USB`), which allows the Linux kernel driver (`ath9k_htc` or `rtl8xxxu`) to scan surrounding access points via `nmcli`.

### Q10: What are the key papers you cited in your research?
**Answer**:
1. *Vesilo (Queueing Systems, 2024)* on multi-core allocation and flow time.
2. *Computer-Aided Civil & Infrastructure Engineering (2022)* on processor affinity in parallel optimization.
3. *Scalpel (IEEE Transactions on Computers, 2025)* on shared cache hierarchy contention.
4. *Lozi et al. (EuroSys 2016)* on Linux scheduler wasted cores.
5. *Blumofe & Leiserson (1999)* on work-stealing algorithms.
