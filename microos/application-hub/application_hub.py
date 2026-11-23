#!/usr/bin/env python3
"""
Micro Hub - Original Asymmetric Application Launcher
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Categorized launcher for Development, Internet, Networking, System Utilities, Research, Accessories, Games.
"""

import sys
import os
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_BG = "#14171a"        # Deep Graphite
COLOR_SIDEBAR = "#1a1d21"   # Charcoal Sidebar
COLOR_CARD = "#1e2227"      # Card Background
COLOR_TEAL = "#00b4d8"      # Electric Teal Highlight
COLOR_AMBER = "#ffb703"     # Amber Accent
COLOR_GREEN = "#2ec4b6"     # Mint Green
COLOR_TEXT = "#e0e6ed"      # Crisp Off-White
COLOR_MUTED = "#8892b0"     # Muted Slate

APPLICATIONS = [
    # Research
    {"name": "Micro Research Lab", "cat": "Research", "desc": "Multi-Core Scheduling benchmark & analysis engine", "exec": ["micro-research-lab"], "badge": "Core Research"},
    # Networking
    {"name": "Micro Network Center", "cat": "Networking", "desc": "Live network telemetry, bandwidth & routing controls", "exec": ["micro-network-center"], "badge": "Telemetry"},
    {"name": "Micro Wi-Fi Scanner", "cat": "Networking", "desc": "Hardware wireless scanner & secure authenticator", "exec": ["micro-wifi-scanner"], "badge": "Wireless"},
    # System Utilities
    {"name": "Micro Monitor", "cat": "System Utilities", "desc": "Real-time CPU/RAM/Network utilization & process manager", "exec": ["micro-monitor"], "badge": "Monitor"},
    {"name": "Micro Control Center", "cat": "System Utilities", "desc": "Comprehensive 10-section engineering settings suite", "exec": ["micro-control-center"], "badge": "Config"},
    # Development
    {"name": "MicroShell Terminal", "cat": "Development", "desc": "Interactive Bash environment with custom engineering diagnostics", "exec": ["xfce4-terminal"], "badge": "CLI"},
    {"name": "Kernel Lab", "cat": "Development", "desc": "Educational bare-metal freestanding x86 kernel", "exec": ["micro-kernel-lab"], "badge": "Bare-Metal"},
    # Internet
    {"name": "Firefox Web Browser", "cat": "Internet", "desc": "Fast, secure web browser configured with MicroOS startpage", "exec": ["firefox"], "badge": "Web"},
    # Accessories
    {"name": "Thunar File Manager", "cat": "Accessories", "desc": "High-performance filesystem explorer", "exec": ["thunar"], "badge": "Files"},
    # Games
    {"name": "Process Panic", "cat": "Games", "desc": "Operating Systems scheduling & memory puzzle game", "exec": ["process-panic"], "badge": "Game"}
]

class MicroHub(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Micro Hub — MicroOS v1.0")
        self.geometry("900x620")
        self.minsize(780, 520)
        self.configure(bg=COLOR_BG)

        self.selected_cat = "All"
        self._init_ui()
        self.filter_apps()

    def _init_ui(self):
        # Header & Search
        header = tk.Frame(self, bg=COLOR_BG, padx=20, pady=16)
        header.pack(fill=tk.X)

        tk.Label(header, text="MICRO HUB", font=("Segoe UI", 16, "bold"), fg=COLOR_TEAL, bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Label(header, text="Engineering Workspace Launcher", font=("Segoe UI", 9, "italic"), fg=COLOR_MUTED, bg=COLOR_BG).pack(side=tk.LEFT, padx=12, pady=(4, 0))

        # Search Bar
        search_frame = tk.Frame(header, bg=COLOR_BG)
        search_frame.pack(side=tk.RIGHT)
        tk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 9), fg=COLOR_TEXT, bg=COLOR_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *args: self.filter_apps())
        ent_search = tk.Entry(search_frame, textvariable=self.var_search, font=("Segoe UI", 10), bg="#22272e", fg=COLOR_TEXT, insertbackground=COLOR_TEAL, width=22)
        ent_search.pack(side=tk.LEFT)

        # Main Layout
        body = tk.Frame(self, bg=COLOR_BG, padx=20)
        body.pack(fill=tk.BOTH, expand=True, pady=(0, 16))

        # Category Sidebar
        self.sidebar = tk.Frame(body, bg=COLOR_SIDEBAR, width=200, bd=1, relief=tk.SOLID)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        self.sidebar.pack_propagate(False)

        categories = ["All", "Development", "Internet", "Networking", "System Utilities", "Research", "Accessories", "Games"]
        self.cat_buttons = {}
        for cat in categories:
            btn = tk.Button(self.sidebar, text=cat, font=("Segoe UI", 9), bg=COLOR_SIDEBAR, fg=COLOR_TEXT,
                            activebackground="#282c34", activeforeground=COLOR_TEAL, relief=tk.FLAT, anchor="w",
                            padx=14, pady=8, command=lambda c=cat: self.set_category(c))
            btn.pack(fill=tk.X)
            self.cat_buttons[cat] = btn

        # Applications Scrollable Grid
        canvas_container = tk.Frame(body, bg=COLOR_BG)
        canvas_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg=COLOR_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def set_category(self, cat):
        self.selected_cat = cat
        for c, btn in self.cat_buttons.items():
            if c == cat:
                btn.configure(bg="#282c34", fg=COLOR_TEAL, font=("Segoe UI", 9, "bold"))
            else:
                btn.configure(bg=COLOR_SIDEBAR, fg=COLOR_TEXT, font=("Segoe UI", 9))
        self.filter_apps()

    def filter_apps(self):
        # Clear existing cards
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        query = self.var_search.get().lower().strip()
        matched = []

        for app in APPLICATIONS:
            if self.selected_cat != "All" and app["cat"] != self.selected_cat:
                continue
            if query and (query not in app["name"].lower() and query not in app["desc"].lower() and query not in app["cat"].lower()):
                continue
            matched.append(app)

        # Render Cards (2 columns)
        for i, app in enumerate(matched):
            row = i // 2
            col = i % 2
            self._render_app_card(self.grid_frame, app, row, col)

    def _render_app_card(self, parent, app, row, col):
        card = tk.Frame(parent, bg=COLOR_CARD, bd=1, relief=tk.SOLID, padx=14, pady=12, width=320, height=120)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        card.pack_propagate(False)

        top_row = tk.Frame(card, bg=COLOR_CARD)
        top_row.pack(fill=tk.X)

        tk.Label(top_row, text=app["name"], font=("Segoe UI", 11, "bold"), fg=COLOR_TEAL, bg=COLOR_CARD).pack(side=tk.LEFT)
        tk.Label(top_row, text=app["badge"], font=("Segoe UI", 8, "bold"), fg=COLOR_AMBER, bg="#282c34", padx=6, pady=2).pack(side=tk.RIGHT)

        tk.Label(card, text=app["desc"], font=("Segoe UI", 8), fg=COLOR_MUTED, bg=COLOR_CARD, wraplength=290, justify=tk.LEFT).pack(anchor="w", pady=(4, 8))

        btn_launch = tk.Button(card, text="🚀 Launch Application", font=("Segoe UI", 8, "bold"), bg=COLOR_TEAL, fg="#000",
                               activebackground="#0096c7", activeforeground="#ffffff", relief=tk.FLAT, padx=10, pady=4,
                               command=lambda a=app: self.launch_app(a))
        btn_launch.pack(anchor="e")

    def launch_app(self, app):
        cmd = app["exec"]
        try:
            # Check if binary is in PATH or relative
            if shutil.which(cmd[0]):
                subprocess.Popen(cmd)
            else:
                # Check known project paths
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                target_map = {
                    "micro-network-center": os.path.join(base_dir, "network-center", "network_center.py"),
                    "micro-wifi-scanner": os.path.join(base_dir, "wifi-scanner", "wifi_scanner.py"),
                    "micro-monitor": os.path.join(base_dir, "system-monitor", "system_monitor.py"),
                    "micro-control-center": os.path.join(base_dir, "control-center", "control_center.py"),
                    "micro-research-lab": os.path.join(base_dir, "research-lab", "gui.py"),
                    "process-panic": os.path.join(base_dir, "process-panic", "main.py")
                }
                if cmd[0] in target_map and os.path.exists(target_map[cmd[0]]):
                    subprocess.Popen([sys.executable, target_map[cmd[0]]])
                else:
                    subprocess.Popen(cmd)
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to execute {app['name']}:\n{e}")

if __name__ == "__main__":
    app = MicroHub()
    app.mainloop()
