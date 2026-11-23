#!/usr/bin/env python3
"""
Micro Research Lab - Graphical Academic Benchmark Suite
Topic: Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution
Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Institution: Jain University, FET Campus (25PCCS201 Operating Systems Research Activity)
"""

import sys
import os
import threading
import subprocess
import json
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_BG = "#14171a"        # Deep Graphite
COLOR_PANEL = "#1e2227"     # Charcoal Panel
COLOR_TEAL = "#00b4d8"      # Electric Teal Highlight
COLOR_AMBER = "#ffb703"     # Amber Accent
COLOR_GREEN = "#2ec4b6"     # Mint Green
COLOR_RED = "#e63946"       # Crimson Alert
COLOR_TEXT = "#e0e6ed"      # Crisp Off-White
COLOR_MUTED = "#8892b0"     # Muted Slate

class MicroResearchLabGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Micro Research Lab — Multi-Core Scheduling Suite")
        self.geometry("960x680")
        self.minsize(840, 560)
        self.configure(bg=COLOR_BG)

        self.is_running = False
        self._init_ui()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLOR_BG, padx=16, pady=12)
        header.pack(fill=tk.X)

        tk.Label(header, text="MICRO RESEARCH LAB", font=("Segoe UI", 16, "bold"), fg=COLOR_TEAL, bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Label(header, text="Multi-Core Scheduling & Workload Distribution Engine", font=("Segoe UI", 10, "italic"), fg=COLOR_MUTED, bg=COLOR_BG).pack(side=tk.LEFT, padx=12, pady=(4, 0))

        author_badge = tk.Label(header, text="T. Vasanth Diwakar | 25BTRCL270", font=("Segoe UI", 9, "bold"), fg=COLOR_AMBER, bg=COLOR_PANEL, padx=8, pady=4)
        author_badge.pack(side=tk.RIGHT)

        # Top Control / Configuration Card
        config_card = tk.LabelFrame(self, text=" Benchmark Configuration ", font=("Segoe UI", 10, "bold"),
                                    fg=COLOR_TEAL, bg=COLOR_PANEL, padx=16, pady=12)
        config_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Parameters Grid
        row1 = tk.Frame(config_card, bg=COLOR_PANEL)
        row1.pack(fill=tk.X, pady=2)

        # Affinity Mode
        tk.Label(row1, text="Affinity Mode:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.var_mode = tk.StringVar(value="spread")
        ttk.Combobox(row1, textvariable=self.var_mode, values=["none", "spread", "single"], state="readonly", width=10).grid(row=0, column=1, padx=(0, 16))

        # Distribution Method
        tk.Label(row1, text="Distribution:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.var_dist = tk.StringVar(value="dynamic")
        ttk.Combobox(row1, textvariable=self.var_dist, values=["dynamic", "block", "rr"], state="readonly", width=10).grid(row=0, column=3, padx=(0, 16))

        # Workers Count
        tk.Label(row1, text="Worker Processes:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.var_workers = tk.StringVar(value="4")
        ttk.Combobox(row1, textvariable=self.var_workers, values=["1", "2", "4", "8"], state="readonly", width=8).grid(row=0, column=5, padx=(0, 16))

        # Repeat Count
        tk.Label(row1, text="Repeats:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).grid(row=0, column=6, sticky="w", padx=(0, 6))
        self.var_repeats = tk.StringVar(value="5")
        ttk.Combobox(row1, textvariable=self.var_repeats, values=["3", "5", "10"], state="readonly", width=6).grid(row=0, column=7)

        # Action Buttons
        btn_bar = tk.Frame(config_card, bg=COLOR_PANEL)
        btn_bar.pack(fill=tk.X, pady=(12, 0))

        self.btn_run_single = tk.Button(btn_bar, text="▶ Run Single Configuration", font=("Segoe UI", 9, "bold"),
                                        bg=COLOR_TEAL, fg="#000", relief=tk.FLAT, padx=12, pady=5, command=self.run_single_config)
        self.btn_run_single.pack(side=tk.LEFT)

        self.btn_run_full = tk.Button(btn_bar, text="⚡ Run Full Paper Matrix (All Experiments)", font=("Segoe UI", 9, "bold"),
                                      bg=COLOR_GREEN, fg="#000", relief=tk.FLAT, padx=12, pady=5, command=self.run_full_matrix)
        self.btn_run_full.pack(side=tk.LEFT, padx=10)

        self.btn_gen_graphs = tk.Button(btn_bar, text="📊 Generate Graphs (Matplotlib)", font=("Segoe UI", 9),
                                        bg="#313640", fg=COLOR_TEXT, relief=tk.FLAT, padx=12, pady=5, command=self.generate_graphs)
        self.btn_gen_graphs.pack(side=tk.RIGHT)

        # Output Terminal Box
        term_frame = tk.LabelFrame(self, text=" Research Console Output ", font=("Segoe UI", 10, "bold"),
                                   fg=COLOR_TEAL, bg=COLOR_PANEL, padx=12, pady=10)
        term_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 14))

        self.term_text = tk.Text(term_frame, bg="#0d0e12", fg="#00f5d4", font=("Courier New", 9), relief=tk.FLAT, wrap=tk.NONE)
        scroll_y = ttk.Scrollbar(term_frame, orient=tk.VERTICAL, command=self.term_text.yview)
        scroll_x = ttk.Scrollbar(term_frame, orient=tk.HORIZONTAL, command=self.term_text.xview)
        self.term_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.term_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.log_terminal("Micro Research Lab initialized.")
        self.log_terminal("Research Topic: Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution.")
        self.log_terminal("Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270) | Branch: CSE-AIML-E\n")

    def log_terminal(self, msg):
        self.term_text.insert(tk.END, msg + "\n")
        self.term_text.see(tk.END)

    def run_single_config(self):
        if self.is_running:
            return
        mode = self.var_mode.get()
        dist = self.var_dist.get()
        workers = self.var_workers.get()
        repeats = self.var_repeats.get()

        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "sched_exp.py"),
               "--mode", mode, "--dist", dist, "--workers", workers, "--repeat", repeats]

        self.log_terminal(f"\n>>> Running: python3 sched_exp.py --mode {mode} --dist {dist} --workers {workers} --repeat {repeats}")
        self._spawn_worker_thread(cmd)

    def run_full_matrix(self):
        if self.is_running:
            return
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "run_benchmarks.py")]
        self.log_terminal("\n>>> Executing complete academic experimental matrix (Table 1, Table 2, Table 3)...")
        self._spawn_worker_thread(cmd)

    def generate_graphs(self):
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "generate_graphs.py")]
        self.log_terminal("\n>>> Generating academic research graphs (Figures 2, 3, 4)...")
        self._spawn_worker_thread(cmd)

    def _spawn_worker_thread(self, cmd):
        self.is_running = True
        self.btn_run_single.configure(state=tk.DISABLED)
        self.btn_run_full.configure(state=tk.DISABLED)

        def worker():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                for line in proc.stdout:
                    self.after(0, self.log_terminal, line.strip())
                proc.wait()
            except Exception as e:
                self.after(0, self.log_terminal, f"Error: {e}")
            finally:
                self.is_running = False
                self.after(0, lambda: self.btn_run_single.configure(state=tk.NORMAL))
                self.after(0, lambda: self.btn_run_full.configure(state=tk.NORMAL))

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app = MicroResearchLabGUI()
    app.mainloop()
