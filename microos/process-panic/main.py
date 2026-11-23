#!/usr/bin/env python3
"""
Process Panic - Original Operating Systems Puzzle & Scheduling Game
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
MicroOS v1.0 Engineering Suite
"""

import sys
import os
import json
import random
import time
import tkinter as tk
from tkinter import messagebox

COLOR_BG = "#101216"
COLOR_PANEL = "#1a1d24"
COLOR_CORE = "#222733"
COLOR_TEAL = "#00b4d8"
COLOR_AMBER = "#ffb703"
COLOR_GREEN = "#2ec4b6"
COLOR_RED = "#e63946"
COLOR_PURPLE = "#9d4edd"
COLOR_TEXT = "#e0e6ed"
COLOR_MUTED = "#8892b0"

SCORES_FILE = os.path.expanduser("~/.process_panic_scores.json")

class Process:
    def __init__(self, pid, name, burst, memory, priority):
        self.pid = pid
        self.name = name
        self.total_burst = burst
        self.remaining_burst = burst
        self.memory = memory
        self.priority = priority # "RT", "HIGH", "NORM", "LOW"
        self.wait_time = 0
        self.color = {
            "RT": COLOR_RED,
            "HIGH": COLOR_AMBER,
            "NORM": COLOR_TEAL,
            "LOW": COLOR_GREEN
        }.get(priority, COLOR_TEAL)

class ProcessPanic(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Process Panic — OS Scheduling Challenge (MicroOS)")
        self.geometry("980x700")
        self.minsize(860, 600)
        self.configure(bg=COLOR_BG)

        # Game State
        self.level = 1
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False

        self.num_cores = 1
        self.total_ram = 1024 # MB
        self.used_ram = 0

        self.ready_queue = []
        self.swap_space = []
        self.cores = [None] # List of running processes per core
        self.next_pid = 1001

        self.quantum = 3 # Time slice for preemption
        self.core_timers = [0]

        self.spawn_counter = 0
        self.spawn_rate = 6 # ticks per spawn

        self._init_ui()
        self._set_level_params(1)
        self.after(200, self.game_loop)

    def load_high_score(self):
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r") as f:
                    return json.load(f).get("high_score", 0)
            except Exception:
                pass
        return 0

    def save_high_score(self):
        try:
            with open(SCORES_FILE, "w") as f:
                json.dump({"high_score": max(self.score, self.high_score)}, f)
        except Exception:
            pass

    def _set_level_params(self, lvl):
        self.level = lvl
        if lvl == 1:
            self.num_cores = 1
            self.total_ram = 1024
            self.spawn_rate = 7
        elif lvl == 2:
            self.num_cores = 2
            self.total_ram = 1024
            self.spawn_rate = 6
        elif lvl == 3:
            self.num_cores = 2
            self.total_ram = 512  # Thrashing memory challenge!
            self.spawn_rate = 5
        elif lvl == 4:
            self.num_cores = 4
            self.total_ram = 1536
            self.spawn_rate = 4
        elif lvl == 5:
            self.num_cores = 4
            self.total_ram = 1024
            self.spawn_rate = 3

        self.cores = [None] * self.num_cores
        self.core_timers = [0] * self.num_cores
        self.lbl_level.configure(text=f"LEVEL {self.level} — Cores: {self.num_cores} | RAM: {self.total_ram}MB")

    def _init_ui(self):
        # Header Bar
        header = tk.Frame(self, bg=COLOR_BG, padx=16, pady=10)
        header.pack(fill=tk.X)

        tk.Label(header, text="PROCESS PANIC", font=("Segoe UI", 16, "bold"), fg=COLOR_AMBER, bg=COLOR_BG).pack(side=tk.LEFT)
        self.lbl_level = tk.Label(header, text="LEVEL 1", font=("Segoe UI", 10, "bold"), fg=COLOR_TEAL, bg=COLOR_BG)
        self.lbl_level.pack(side=tk.LEFT, padx=16)

        self.lbl_score = tk.Label(header, text=f"Score: 0 | Best: {self.high_score}", font=("Segoe UI", 11, "bold"), fg=COLOR_GREEN, bg=COLOR_BG)
        self.lbl_score.pack(side=tk.RIGHT)

        # Control Bar
        ctrl_bar = tk.Frame(self, bg=COLOR_PANEL, padx=16, pady=6)
        ctrl_bar.pack(fill=tk.X)

        tk.Button(ctrl_bar, text="⏸ Pause / Resume (Space)", font=("Segoe UI", 9), bg="#282c34", fg=COLOR_TEXT, relief=tk.FLAT, padx=8, pady=3, command=self.toggle_pause).pack(side=tk.LEFT)
        tk.Button(ctrl_bar, text="🔄 Restart (R)", font=("Segoe UI", 9), bg="#282c34", fg=COLOR_TEXT, relief=tk.FLAT, padx=8, pady=3, command=self.restart_game).pack(side=tk.LEFT, padx=8)

        self.lbl_ram_bar = tk.Label(ctrl_bar, text="RAM Usage: 0 / 1024 MB (0%)", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL)
        self.lbl_ram_bar.pack(side=tk.RIGHT)

        # Main Game Canvas
        self.canvas = tk.Canvas(self, bg="#0d0e12", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Keyboard Bindings
        self.bind("<space>", lambda e: self.toggle_pause())
        self.bind("<r>", lambda e: self.restart_game())
        self.bind("<R>", lambda e: self.restart_game())
        for i in range(1, 5):
            self.bind(str(i), lambda e, c=i: self.assign_top_to_core(c - 1))

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused

    def restart_game(self):
        self.game_over = False
        self.paused = False
        self.score = 0
        self.ready_queue.clear()
        self.swap_space.clear()
        self.next_pid = 1001
        self._set_level_params(1)
        self.lbl_score.configure(text=f"Score: 0 | Best: {self.high_score}")

    def spawn_process(self):
        names = ["comp_kernel", "net_daemon", "db_worker", "ai_infer", "render_job", "audio_srv", "disk_flush", "crypto_task"]
        name = random.choice(names)
        burst = random.randint(4, 18)
        memory = random.choice([64, 128, 256, 384])
        prios = ["RT", "HIGH", "NORM", "NORM", "LOW"]
        prio = random.choice(prios)

        # Check if RAM is completely full
        if self.used_ram + memory > self.total_ram:
            # Memory pressure: send to swap if swap not full, else OOM Panic!
            if len(self.swap_space) >= 4:
                self.trigger_kernel_panic("OUT OF MEMORY (OOM PANIC) — RAM & Swap Exhausted!")
                return
            proc = Process(self.next_pid, name, burst, memory, prio)
            self.swap_space.append(proc)
        else:
            proc = Process(self.next_pid, name, burst, memory, prio)
            self.ready_queue.append(proc)
            self.used_ram += memory

        self.next_pid += 1

    def assign_top_to_core(self, core_idx):
        if core_idx >= self.num_cores or not self.ready_queue:
            return
        if self.cores[core_idx] is None:
            self.cores[core_idx] = self.ready_queue.pop(0)
            self.core_timers[core_idx] = 0

    def on_canvas_click(self, event):
        if self.game_over:
            self.restart_game()
            return
        x, y = event.x, event.y

        # Check click on Ready Queue process
        queue_start_y = 90
        for i, proc in enumerate(self.ready_queue[:8]):
            ry = queue_start_y + (i * 44)
            if 30 <= x <= 320 and ry <= y <= ry + 36:
                # Find first idle core or swap
                for c in range(self.num_cores):
                    if self.cores[c] is None:
                        self.cores[c] = self.ready_queue.pop(i)
                        self.core_timers[c] = 0
                        return
                # If no idle core, page out to swap if space available
                if len(self.swap_space) < 4:
                    p = self.ready_queue.pop(i)
                    self.used_ram -= p.memory
                    self.swap_space.append(p)
                return

        # Check click on Swap Space process to Page In
        swap_start_y = 480
        for i, proc in enumerate(self.swap_space):
            sx = 30 + (i * 140)
            if sx <= x <= sx + 130 and swap_start_y <= y <= swap_start_y + 40:
                if self.used_ram + proc.memory <= self.total_ram:
                    self.used_ram += proc.memory
                    self.ready_queue.append(self.swap_space.pop(i))
                return

        # Check click on Core to Preempt
        for c in range(self.num_cores):
            cx = 440 + ((c % 2) * 230)
            cy = 110 + ((c // 2) * 160)
            if cx <= x <= cx + 210 and cy <= y <= cy + 130:
                if self.cores[c] is not None:
                    # Preempt process back to ready queue
                    self.ready_queue.append(self.cores[c])
                    self.cores[c] = None
                    self.core_timers[c] = 0
                return

    def trigger_kernel_panic(self, reason):
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.lbl_score.configure(text=f"Score: {self.score} | Best: {self.high_score}")

    def game_loop(self):
        if not self.paused and not self.game_over:
            # Spawn logic
            self.spawn_counter += 1
            if self.spawn_counter >= self.spawn_rate:
                self.spawn_counter = 0
                if len(self.ready_queue) < 9:
                    self.spawn_process()

            # Execute Core Cycles
            for c in range(self.num_cores):
                proc = self.cores[c]
                if proc is not None:
                    proc.remaining_burst -= 1
                    self.core_timers[c] += 1

                    # Check if process completed
                    if proc.remaining_burst <= 0:
                        self.used_ram = max(0, self.used_ram - proc.memory)
                        bonus = {"RT": 40, "HIGH": 25, "NORM": 15, "LOW": 10}.get(proc.priority, 10)
                        self.score += bonus
                        self.lbl_score.configure(text=f"Score: {self.score} | Best: {self.high_score}")
                        self.cores[c] = None
                        self.core_timers[c] = 0

                        # Check level progression
                        if self.score >= self.level * 180 and self.level < 5:
                            self._set_level_params(self.level + 1)
                    # Round-robin preemption quantum
                    elif self.core_timers[c] >= self.quantum and len(self.ready_queue) > 0:
                        # Auto preemption if quantum expired and tasks waiting
                        self.ready_queue.append(proc)
                        self.cores[c] = None
                        self.core_timers[c] = 0

            # Update starvation timers in ready queue
            for proc in self.ready_queue:
                proc.wait_time += 1
                if proc.wait_time > 180 and proc.priority == "RT":
                    self.trigger_kernel_panic(f"REAL-TIME STARVATION — PID {proc.pid} missed scheduling deadline!")
                    break

            # Update RAM Indicator
            pct = int((self.used_ram / self.total_ram) * 100) if self.total_ram > 0 else 0
            color = COLOR_GREEN if pct < 70 else (COLOR_AMBER if pct < 90 else COLOR_RED)
            self.lbl_ram_bar.configure(text=f"RAM Usage: {self.used_ram} / {self.total_ram} MB ({pct}%)", fg=color)

        self.render()
        self.after(200, self.game_loop)

    def render(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10 or h < 10:
            return

        if self.game_over:
            c.create_rectangle(w//2 - 240, h//2 - 120, w//2 + 240, h//2 + 120, fill="#210a0c", outline=COLOR_RED, width=3)
            c.create_text(w//2, h//2 - 60, text="KERNEL PANIC!", fill=COLOR_RED, font=("Segoe UI", 24, "bold"))
            c.create_text(w//2, h//2 - 10, text="Operating System Scheduling / Memory Failure", fill=COLOR_TEXT, font=("Segoe UI", 11))
            c.create_text(w//2, h//2 + 25, text=f"Final Score: {self.score} (Level {self.level})", fill=COLOR_AMBER, font=("Segoe UI", 13, "bold"))
            c.create_text(w//2, h//2 + 70, text="Click Anywhere or Press 'R' to Reboot OS", fill=COLOR_MUTED, font=("Segoe UI", 10))
            return

        # Section 1: Ready Queue (Left Column)
        c.create_text(30, 40, text="READY QUEUE (Click task to schedule)", fill=COLOR_TEAL, font=("Segoe UI", 11, "bold"), anchor="w")
        c.create_rectangle(20, 60, 330, 440, fill=COLOR_PANEL, outline="#2a2e38")

        for i, proc in enumerate(self.ready_queue[:8]):
            py = 70 + (i * 44)
            c.create_rectangle(30, py, 320, py + 38, fill="#1c2027", outline=proc.color, width=2)
            c.create_text(40, py + 12, text=f"[{proc.priority}] {proc.name} (PID: {proc.pid})", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"), anchor="w")
            c.create_text(40, py + 26, text=f"Burst: {proc.remaining_burst}s | Mem: {proc.memory}MB | Wait: {proc.wait_time}t", fill=COLOR_MUTED, font=("Segoe UI", 8), anchor="w")

        # Section 2: Swap Space (Bottom Left)
        c.create_text(30, 460, text="SWAP SPACE / PAGING FILE (Click to swap in)", fill=COLOR_AMBER, font=("Segoe UI", 10, "bold"), anchor="w")
        c.create_rectangle(20, 480, 580, 560, fill=COLOR_PANEL, outline="#2a2e38")

        for i, proc in enumerate(self.swap_space):
            sx = 30 + (i * 135)
            c.create_rectangle(sx, 490, sx + 125, 545, fill="#181a20", outline=COLOR_MUTED)
            c.create_text(sx + 8, 505, text=f"{proc.name[:10]}", fill=COLOR_TEXT, font=("Segoe UI", 8, "bold"), anchor="w")
            c.create_text(sx + 8, 525, text=f"{proc.memory}MB (Swapped)", fill=COLOR_AMBER, font=("Segoe UI", 8), anchor="w")

        # Section 3: CPU Execution Cores (Right Section)
        c.create_text(440, 40, text=f"CPU MULTI-CORE PIPELINE ({self.num_cores} Logical Cores)", fill=COLOR_TEAL, font=("Segoe UI", 11, "bold"), anchor="w")

        for i in range(self.num_cores):
            cx = 440 + ((i % 2) * 230)
            cy = 70 + ((i // 2) * 160)
            c.create_rectangle(cx, cy, cx + 210, cy + 140, fill=COLOR_CORE, outline="#333a48", width=2)
            c.create_text(cx + 12, cy + 20, text=f"CORE #{i + 1} [Key: {i + 1}]", fill=COLOR_TEAL, font=("Segoe UI", 10, "bold"), anchor="w")

            proc = self.cores[i]
            if proc is not None:
                c.create_rectangle(cx + 10, cy + 38, cx + 200, cy + 130, fill="#1c2027", outline=proc.color, width=2)
                c.create_text(cx + 20, cy + 54, text=f"PID: {proc.pid} [{proc.priority}]", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"), anchor="w")
                c.create_text(cx + 20, cy + 72, text=f"{proc.name}", fill=COLOR_AMBER, font=("Segoe UI", 9), anchor="w")

                # Burst Progress Bar
                progress = 1.0 - (proc.remaining_burst / proc.total_burst)
                c.create_rectangle(cx + 20, cy + 90, cx + 190, cy + 102, fill="#101216", outline="#333a48")
                c.create_rectangle(cx + 20, cy + 90, cx + 20 + int(170 * progress), cy + 102, fill=COLOR_GREEN, outline="")
                c.create_text(cx + 20, cy + 116, text=f"Burst Left: {proc.remaining_burst} | Slice: {self.core_timers[i]}/{self.quantum}", fill=COLOR_MUTED, font=("Segoe UI", 8), anchor="w")
            else:
                c.create_text(cx + 105, cy + 85, text="[IDLE - Click Queue to Assign]", fill=COLOR_MUTED, font=("Segoe UI", 8, "italic"))

        if self.paused:
            c.create_rectangle(w//2 - 120, h//2 - 40, w//2 + 120, h//2 + 40, fill="#1a1d24", outline=COLOR_AMBER, width=2)
            c.create_text(w//2, h//2, text="GAME PAUSED", fill=COLOR_AMBER, font=("Segoe UI", 16, "bold"))

if __name__ == "__main__":
    game = ProcessPanic()
    game.mainloop()
