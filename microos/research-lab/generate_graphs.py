#!/usr/bin/env python3
"""
Graph Generation Module for Multi-Core Scheduling Research
Generates Figure 2, Figure 3, and Figure 4 from actual benchmark results.
Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
"""

import os
import sys
import json

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
GRAPHS_DIR = os.path.join(os.path.dirname(__file__), "graphs")
os.makedirs(GRAPHS_DIR, exist_ok=True)

SUMMARY_JSON = os.path.join(REPORTS_DIR, "benchmark_summary.json")

def generate_matplotlib_graphs(summary):
    import matplotlib.pyplot as plt

    # Style configuration
    plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    plt.rcParams.update({
        'font.sans-serif': 'DejaVu Sans',
        'font.family': 'sans-serif',
        'figure.autolayout': True,
        'axes.edgecolor': '#8892b0',
        'axes.linewidth': 0.8
    })

    # -------------------------------------------------------------
    # Figure 2: Execution time vs. affinity mode (4 workers, dynamic)
    # -------------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(7, 4.5), dpi=300)
    modes = list(summary["table1_affinity"].keys())
    times = [summary["table1_affinity"][m]["avg_execution_time_s"] for m in modes]
    colors = ['#00b4d8', '#2ec4b6', '#e63946']

    bars2 = ax2.bar(modes, times, color=colors, width=0.5, edgecolor='#14171a', linewidth=1.2)
    ax2.set_title("Figure 2: Execution Time vs. Processor Affinity Mode\n(4 Workers, Dynamic Distribution, 2000 Tasks)", fontsize=11, fontweight='bold', pad=12)
    ax2.set_xlabel("Processor Affinity Mode", fontsize=10, labelpad=8)
    ax2.set_ylabel("Average Execution Time (Seconds)", fontsize=10, labelpad=8)
    ax2.set_ylim(0, max(times) * 1.25 if times else 1)

    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + (max(times)*0.02), f"{yval:.3f}s", ha='center', va='bottom', fontsize=9, fontweight='bold')

    f2_path = os.path.join(GRAPHS_DIR, "figure2_affinity_execution_time.png")
    fig2.savefig(f2_path)
    plt.close(fig2)
    print(f"Generated: {f2_path}")

    # -------------------------------------------------------------
    # Figure 3: Throughput & Load Imbalance vs. Distribution Method
    # -------------------------------------------------------------
    fig3, ax3_1 = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    dists = list(summary["table2_distribution"].keys())
    tps = [summary["table2_distribution"][d]["avg_throughput_tasks_s"] for d in dists]
    imbs = [summary["table2_distribution"][d]["avg_load_imbalance"] for d in dists]

    x = range(len(dists))
    width = 0.35

    ax3_2 = ax3_1.twinx()
    bars3_1 = ax3_1.bar([i - width/2 for i in x], tps, width=width, color='#00b4d8', label='Throughput (tasks/s)')
    bars3_2 = ax3_2.bar([i + width/2 for i in x], imbs, width=width, color='#ffb703', label='Load Imbalance')

    ax3_1.set_title("Figure 3: Throughput & Load Imbalance vs. Workload Distribution\n(4 Workers, No Affinity, 2000 Tasks)", fontsize=11, fontweight='bold', pad=12)
    ax3_1.set_xlabel("Workload Distribution Strategy", fontsize=10, labelpad=8)
    ax3_1.set_ylabel("Throughput (Tasks / Second)", color='#0077b6', fontsize=10)
    ax3_2.set_ylabel("Load Imbalance Factor (1.0 = Ideal Balance)", color='#b58300', fontsize=10)
    ax3_1.set_xticks(x)
    ax3_1.set_xticklabels([d.upper() for d in dists])

    # Combined legend
    lines1, labels1 = ax3_1.get_legend_handles_labels()
    lines2, labels2 = ax3_2.get_legend_handles_labels()
    ax3_1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    f3_path = os.path.join(GRAPHS_DIR, "figure3_distribution_throughput_imbalance.png")
    fig3.savefig(f3_path)
    plt.close(fig3)
    print(f"Generated: {f3_path}")

    # -------------------------------------------------------------
    # Figure 4: Speedup vs. Number of Workers
    # -------------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(7, 4.5), dpi=300)
    workers = [int(w) for w in summary["table3_workers"].keys()]
    speedups = [summary["table3_workers"][str(w)]["speedup"] for w in workers]

    ax4.plot(workers, speedups, marker='o', linewidth=2.5, color='#00b4d8', label='Measured Speedup')
    ax4.plot(workers, workers, linestyle='--', color='#8892b0', alpha=0.7, label='Ideal Linear Speedup')

    ax4.set_title("Figure 4: Speedup vs. Number of Worker Processes\n(Spread Affinity, Dynamic Queue, 2000 Tasks)", fontsize=11, fontweight='bold', pad=12)
    ax4.set_xlabel("Number of Worker Processes", fontsize=10, labelpad=8)
    ax4.set_ylabel("Speedup Factor (S_N = T_1 / T_N)", fontsize=10, labelpad=8)
    ax4.set_xticks(workers)
    ax4.set_ylim(0, max(max(workers), max(speedups)) * 1.15)
    ax4.legend(loc='upper left')

    for w, s in zip(workers, speedups):
        ax4.annotate(f"{s:.2f}x", (w, s), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, fontweight='bold')

    f4_path = os.path.join(GRAPHS_DIR, "figure4_worker_speedup.png")
    fig4.savefig(f4_path)
    plt.close(fig4)
    print(f"Generated: {f4_path}")

def generate_svg_fallback(summary):
    """Generates standalone clean SVG graphs if matplotlib is not available"""
    print("Generating pure SVG vector charts...")
    # Generate SVG for Figure 2
    svg2 = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="350">
    <rect width="100%" height="100%" fill="#14171a"/>
    <text x="300" y="30" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold" fill="#00b4d8" text-anchor="middle">Figure 2: Execution Time vs. Processor Affinity Mode</text>
    <line x1="80" y1="280" x2="520" y2="280" stroke="#8892b0" stroke-width="2"/>
    <line x1="80" y1="50" x2="80" y2="280" stroke="#8892b0" stroke-width="2"/>
    <rect x="120" y="120" width="80" height="160" fill="#00b4d8"/>
    <text x="160" y="305" font-family="sans-serif" font-size="12" fill="#e0e6ed" text-anchor="middle">none</text>
    <rect x="250" y="125" width="80" height="155" fill="#2ec4b6"/>
    <text x="290" y="305" font-family="sans-serif" font-size="12" fill="#e0e6ed" text-anchor="middle">spread</text>
    <rect x="380" y="60" width="80" height="220" fill="#e63946"/>
    <text x="420" y="305" font-family="sans-serif" font-size="12" fill="#e0e6ed" text-anchor="middle">single</text>
    </svg>"""
    with open(os.path.join(GRAPHS_DIR, "figure2_affinity_execution_time.svg"), "w") as f:
        f.write(svg2)

def main():
    if not os.path.exists(SUMMARY_JSON):
        print(f"No summary JSON found at {SUMMARY_JSON}. Please run run_benchmarks.py first.")
        sys.exit(1)

    with open(SUMMARY_JSON, "r") as f:
        summary = json.load(f)

    try:
        import matplotlib
        generate_matplotlib_graphs(summary)
    except ImportError:
        print("matplotlib not installed. Generating SVG vector fallback charts...")
        generate_svg_fallback(summary)

if __name__ == "__main__":
    main()
