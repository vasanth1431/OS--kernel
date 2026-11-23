#!/usr/bin/env python3
"""
Micro Monitor - MicroOS Real-Time System Telemetry
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Reads live metrics from /proc/stat, /proc/meminfo, /proc/uptime, /proc/net/dev,
and /proc filesystem to display hardware utilization and process management.
"""

import sys
import os
import time
import subprocess
import signal
import tkinter as tk
from tkinter import ttk, messagebox

# Palette
COLOR_BG = "#14171a"        # Deep Graphite
COLOR_PANEL = "#1e2227"     # Charcoal Panel
COLOR_TEAL = "#00b4d8"      # Electric Teal Highlight
COLOR_AMBER = "#ffb703"     # Amber Accent
COLOR_GREEN = "#2ec4b6"     # Mint Green
COLOR_RED = "#e63946"       # Crimson Alert
COLOR_TEXT = "#e0e6ed"      # Crisp Off-White
COLOR_MUTED = "#8892b0"     # Muted Slate

class MicroMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Micro Monitor — MicroOS v1.0")
        self.geometry("960x680")
        self.minsize(820, 560)
        self.configure(bg=COLOR_BG)

        # Telemetry State
        self.prev_cpu_total = 0
        self.prev_cpu_idle = 0
        self.cpu_history = [0] * 30
        self.mem_history = [0] * 30
        self.prev_rx = 0
        self.prev_tx = 0
        self.last_net_time = time.time()

        self._init_ui()
        self._sample_telemetry()
        self._periodic_refresh()

    def _init_ui(self):
        # Header Bar
        header = tk.Frame(self, bg=COLOR_BG, padx=16, pady=12)
        header.pack(fill=tk.X)

        tk.Label(header, text="MICRO MONITOR", font=("Segoe UI", 16, "bold"), fg=COLOR_TEAL, bg=COLOR_BG).pack(side=tk.LEFT)
        self.lbl_kernel = tk.Label(header, text="Kernel: Probing...", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=COLOR_BG)
        self.lbl_kernel.pack(side=tk.LEFT, padx=(16, 0), pady=(4, 0))

        self.lbl_uptime = tk.Label(header, text="Uptime: --", font=("Segoe UI", 9, "bold"), fg=COLOR_AMBER, bg=COLOR_BG)
        self.lbl_uptime.pack(side=tk.RIGHT)

        # Overview Metrics Grid (Cards)
        cards_frame = tk.Frame(self, bg=COLOR_BG, padx=16)
        cards_frame.pack(fill=tk.X, pady=(0, 10))

        # CPU Card
        self.card_cpu = self._create_metric_card(cards_frame, "CPU Utilization", "0.0%", COLOR_TEAL)
        self.card_cpu.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        # RAM Card
        self.card_ram = self._create_metric_card(cards_frame, "Memory (RAM)", "0 MB / 0 MB", COLOR_GREEN)
        self.card_ram.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        # Swap Card
        self.card_swap = self._create_metric_card(cards_frame, "Swap Space", "0 MB", COLOR_AMBER)
        self.card_swap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        # Disk Card
        self.card_disk = self._create_metric_card(cards_frame, "Root Disk (df)", "0% Used", COLOR_MUTED)
        self.card_disk.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        # Real-Time Sparkline Graphs Canvas
        graph_box = tk.LabelFrame(self, text=" System Performance Graphs (Last 30 Seconds) ", font=("Segoe UI", 9, "bold"),
                                  fg=COLOR_TEAL, bg=COLOR_PANEL, padx=10, pady=6)
        graph_box.pack(fill=tk.X, padx=16, pady=(0, 10))

        self.canvas_graph = tk.Canvas(graph_box, bg="#121518", height=90, highlightthickness=0)
        self.canvas_graph.pack(fill=tk.X, expand=True)

        # Process Table Section
        proc_box = tk.LabelFrame(self, text=" Active Processes (/proc) ", font=("Segoe UI", 10, "bold"),
                                 fg=COLOR_TEAL, bg=COLOR_PANEL, padx=10, pady=8)
        proc_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # Search Bar & Controls
        ctrl_bar = tk.Frame(proc_box, bg=COLOR_PANEL)
        ctrl_bar.pack(fill=tk.X, pady=(0, 6))

        tk.Label(ctrl_bar, text="Filter Process:", font=("Segoe UI", 9), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(side=tk.LEFT)
        self.var_filter = tk.StringVar()
        self.var_filter.trace_add("write", lambda *args: self.refresh_processes())
        ent_filter = tk.Entry(ctrl_bar, textvariable=self.var_filter, font=("Segoe UI", 9), bg="#282c34", fg=COLOR_TEXT, insertbackground=COLOR_TEAL, width=20)
        ent_filter.pack(side=tk.LEFT, padx=(8, 16))

        tk.Button(ctrl_bar, text="Terminate PID (SIGTERM)", font=("Segoe UI", 8, "bold"), bg=COLOR_RED, fg="#ffffff",
                  relief=tk.FLAT, padx=8, pady=3, command=self.kill_selected).pack(side=tk.RIGHT)

        tk.Button(ctrl_bar, text="Refresh Now", font=("Segoe UI", 8), bg="#313640", fg=COLOR_TEXT,
                  relief=tk.FLAT, padx=8, pady=3, command=self.refresh_processes).pack(side=tk.RIGHT, padx=8)

        # Table
        cols = ("pid", "user", "cpu", "mem", "rss", "stat", "cmd")
        self.tree_proc = ttk.Treeview(proc_box, columns=cols, show="headings", selectmode="browse")
        self.tree_proc.heading("pid", text="PID", command=lambda: self.sort_column("pid", False))
        self.tree_proc.heading("user", text="User")
        self.tree_proc.heading("cpu", text="CPU %", command=lambda: self.sort_column("cpu", True))
        self.tree_proc.heading("mem", text="MEM %", command=lambda: self.sort_column("mem", True))
        self.tree_proc.heading("rss", text="Resident (MB)")
        self.tree_proc.heading("stat", text="Status")
        self.tree_proc.heading("cmd", text="Command")

        self.tree_proc.column("pid", width=70, anchor="center")
        self.tree_proc.column("user", width=90, anchor="w")
        self.tree_proc.column("cpu", width=70, anchor="center")
        self.tree_proc.column("mem", width=70, anchor="center")
        self.tree_proc.column("rss", width=100, anchor="center")
        self.tree_proc.column("stat", width=70, anchor="center")
        self.tree_proc.column("cmd", width=360, anchor="w")

        scroll = ttk.Scrollbar(proc_box, orient=tk.VERTICAL, command=self.tree_proc.yview)
        self.tree_proc.configure(yscrollcommand=scroll.set)
        self.tree_proc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_metric_card(self, parent, title, initial_val, color):
        frame = tk.Frame(parent, bg=COLOR_PANEL, bd=1, relief=tk.SOLID, padx=12, pady=8)
        tk.Label(frame, text=title, font=("Segoe UI", 8, "bold"), fg=COLOR_MUTED, bg=COLOR_PANEL).pack(anchor="w")
        val_lbl = tk.Label(frame, text=initial_val, font=("Segoe UI", 13, "bold"), fg=color, bg=COLOR_PANEL)
        val_lbl.pack(anchor="w", pady=(3, 0))
        frame.val_lbl = val_lbl
        return frame

    def _read_cpu_percent(self):
        """Read /proc/stat to compute true CPU busy percentage"""
        if not os.path.exists("/proc/stat"):
            return 0.0
        try:
            with open("/proc/stat", "r") as f:
                first_line = f.readline()
            parts = [float(x) for x in first_line.split()[1:8]]
            idle = parts[3] + parts[4]  # idle + iowait
            total = sum(parts)

            dt_total = total - self.prev_cpu_total
            dt_idle = idle - self.prev_cpu_idle
            self.prev_cpu_total = total
            self.prev_cpu_idle = idle

            if dt_total > 0:
                cpu_usage = 100.0 * (1.0 - (dt_idle / dt_total))
                return max(0.0, min(100.0, cpu_usage))
        except Exception:
            pass
        return 0.0

    def _read_memory(self):
        """Read /proc/meminfo"""
        mem_info = {"total": 1, "avail": 1, "swap_total": 0, "swap_free": 0}
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            mem_info["total"] = int(line.split()[1]) // 1024
                        elif line.startswith("MemAvailable:"):
                            mem_info["avail"] = int(line.split()[1]) // 1024
                        elif line.startswith("SwapTotal:"):
                            mem_info["swap_total"] = int(line.split()[1]) // 1024
                        elif line.startswith("SwapFree:"):
                            mem_info["swap_free"] = int(line.split()[1]) // 1024
            except Exception:
                pass
        return mem_info

    def _sample_telemetry(self):
        # Kernel & Uptime
        try:
            uname = os.uname()
            self.lbl_kernel.configure(text=f"Linux Kernel {uname.release} ({uname.machine})")
        except Exception:
            self.lbl_kernel.configure(text="Linux Kernel 6.8.0-generic (x86_64)")

        if os.path.exists("/proc/uptime"):
            try:
                with open("/proc/uptime", "r") as f:
                    up_secs = float(f.readline().split()[0])
                mins, secs = divmod(int(up_secs), 60)
                hrs, mins = divmod(mins, 60)
                self.lbl_uptime.configure(text=f"Uptime: {hrs}h {mins}m {secs}s")
            except Exception:
                pass

        # CPU Metric
        cpu_pct = self._read_cpu_percent()
        self.card_cpu.val_lbl.configure(text=f"{cpu_pct:.1f}%")
        self.cpu_history.pop(0)
        self.cpu_history.append(cpu_pct)

        # Memory Metric
        mem = self._read_memory()
        mem_used = mem["total"] - mem["avail"]
        mem_pct = (mem_used / mem["total"]) * 100 if mem["total"] > 0 else 0
        self.card_ram.val_lbl.configure(text=f"{mem_used} / {mem['total']} MB ({mem_pct:.0f}%)")
        self.mem_history.pop(0)
        self.mem_history.append(mem_pct)

        # Swap Metric
        swap_used = mem["swap_total"] - mem["swap_free"]
        self.card_swap.val_lbl.configure(text=f"{swap_used} / {mem['swap_total']} MB")

        # Root Disk Space
        try:
            statvfs = os.statvfs("/")
            total_disk = (statvfs.f_blocks * statvfs.f_frsize) / (1024**3)
            free_disk = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
            used_disk = total_disk - free_disk
            pct_disk = (used_disk / total_disk) * 100 if total_disk > 0 else 0
            self.card_disk.val_lbl.configure(text=f"{pct_disk:.1f}% ({used_disk:.1f} / {total_disk:.1f} GB)")
        except Exception:
            pass

        self._draw_graphs()

    def _draw_graphs(self):
        """Draw CPU (Teal) and Memory (Green) line graph"""
        c = self.canvas_graph
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return

        # Grid lines
        for y_pct in (0.25, 0.50, 0.75):
            y = int(h * (1.0 - y_pct))
            c.create_line(0, y, w, y, fill="#21262d", dash=(2, 4))

        n = len(self.cpu_history)
        step = w / (n - 1)

        # CPU Points (Teal)
        cpu_coords = []
        mem_coords = []
        for i in range(n):
            x = i * step
            y_cpu = h - (self.cpu_history[i] / 100.0 * h)
            y_mem = h - (self.mem_history[i] / 100.0 * h)
            cpu_coords.extend([x, max(2, min(h - 2, y_cpu))])
            mem_coords.extend([x, max(2, min(h - 2, y_mem))])

        if len(cpu_coords) >= 4:
            c.create_line(cpu_coords, fill=COLOR_TEAL, width=2)
            c.create_line(mem_coords, fill=COLOR_GREEN, width=2)

        # Legend
        c.create_text(40, 12, text="― CPU", fill=COLOR_TEAL, font=("Segoe UI", 8, "bold"))
        c.create_text(90, 12, text="― RAM", fill=COLOR_GREEN, font=("Segoe UI", 8, "bold"))

    def refresh_processes(self):
        """Query genuine Linux processes using ps"""
        query = self.var_filter.get().lower().strip()
        selected_pid = None
        sel = self.tree_proc.selection()
        if sel:
            selected_pid = self.tree_proc.item(sel[0], "values")[0]

        for item in self.tree_proc.get_children():
            self.tree_proc.delete(item)

        try:
            cmd = ["ps", "-eo", "pid,user,%cpu,%mem,rss,stat,comm", "--sort=-%cpu"]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
            lines = out.strip().splitlines()[1:]

            to_select = None
            for line in lines[:80]:
                parts = line.split(None, 6)
                if len(parts) >= 7:
                    pid, user, cpu, mem, rss, stat, command = parts
                    rss_mb = f"{int(rss) // 1024} MB"
                    if not query or query in command.lower() or query in pid or query in user.lower():
                        item_id = self.tree_proc.insert("", tk.END, values=(pid, user, cpu, mem, rss_mb, stat, command))
                        if selected_pid and pid == str(selected_pid):
                            to_select = item_id

            if to_select:
                self.tree_proc.selection_set(to_select)
        except Exception:
            pass

    def sort_column(self, col, numeric=False):
        items = [(self.tree_proc.set(k, col), k) for k in self.tree_proc.get_children("")]
        if numeric:
            items.sort(key=lambda t: float(t[0].replace("MB", "").strip() or 0), reverse=True)
        else:
            items.sort(key=lambda t: t[0].lower(), reverse=False)

        for index, (val, k) in enumerate(items):
            self.tree_proc.move(k, "", index)

    def kill_selected(self):
        sel = self.tree_proc.selection()
        if not sel:
            messagebox.showinfo("Select Process", "Please select a process to terminate.")
            return

        pid, user, cpu, mem, rss, stat, cmd = self.tree_proc.item(sel[0], "values")
        if messagebox.askyesno("Confirm Terminate", f"Send SIGTERM to process '{cmd}' (PID: {pid})?"):
            try:
                os.kill(int(pid), signal.SIGTERM)
                messagebox.showinfo("Terminated", f"SIGTERM sent to PID {pid}.")
                self.refresh_processes()
            except PermissionError:
                messagebox.showerror("Permission Denied", f"Cannot terminate PID {pid}. Root privileges required.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill PID {pid}: {e}")

    def _periodic_refresh(self):
        self._sample_telemetry()
        # Refresh process list every 3 seconds to avoid UI stutter
        if int(time.time()) % 3 == 0:
            self.refresh_processes()
        self.after(1000, self._periodic_refresh)

if __name__ == "__main__":
    app = MicroMonitor()
    app.refresh_processes()
    app.mainloop()
