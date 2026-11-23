#!/usr/bin/env python3
"""
Micro Control Center - MicroOS System Configuration
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
10 Functional Configuration Sections interfacing with actual Linux subsystem APIs:
Appearance, Display, Keyboard, Mouse, Network, Sound, Storage, Users, System Info, Applications.
"""

import sys
import os
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

COLOR_BG = "#14171a"        # Deep Graphite
COLOR_SIDEBAR = "#1a1d21"   # Dark Sidebar
COLOR_PANEL = "#1e2227"     # Charcoal Panel
COLOR_TEAL = "#00b4d8"      # Electric Teal Highlight
COLOR_AMBER = "#ffb703"     # Amber Accent
COLOR_GREEN = "#2ec4b6"     # Mint Green
COLOR_RED = "#e63946"       # Crimson Alert
COLOR_TEXT = "#e0e6ed"      # Crisp Off-White
COLOR_MUTED = "#8892b0"     # Muted Slate

class MicroControlCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Micro Control Center — MicroOS v1.0")
        self.geometry("920x640")
        self.minsize(800, 520)
        self.configure(bg=COLOR_BG)

        self.current_section = None
        self._init_layout()
        self.show_section("appearance")

    def _init_layout(self):
        # Header
        header = tk.Frame(self, bg=COLOR_BG, padx=16, pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="MICRO CONTROL CENTER", font=("Segoe UI", 15, "bold"), fg=COLOR_TEAL, bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Label(header, text="Unified Linux Engineering Preferences", font=("Segoe UI", 9, "italic"), fg=COLOR_MUTED, bg=COLOR_BG).pack(side=tk.LEFT, padx=12, pady=(3, 0))

        # Main Split Body
        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        # Left Sidebar (10 Sections)
        self.sidebar = tk.Frame(body, bg=COLOR_SIDEBAR, width=220, bd=1, relief=tk.SOLID)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        self.sidebar.pack_propagate(False)

        sections = [
            ("🎨 Appearance", "appearance"),
            ("🖥 Display & Graphics", "display"),
            ("⌨ Keyboard & Input", "keyboard"),
            ("🖱 Mouse & Touchpad", "mouse"),
            ("🌐 Network & Routing", "network"),
            ("🔊 Sound & Audio", "sound"),
            ("💾 Storage & Disks", "storage"),
            ("👤 Users & Security", "users"),
            ("ℹ System Information", "sysinfo"),
            ("🚀 Default Applications", "apps")
        ]

        self.nav_buttons = {}
        for title, key in sections:
            btn = tk.Button(self.sidebar, text=title, font=("Segoe UI", 10),
                            bg=COLOR_SIDEBAR, fg=COLOR_TEXT, activebackground="#282c34",
                            activeforeground=COLOR_TEAL, relief=tk.FLAT, anchor="w",
                            padx=14, pady=8, command=lambda k=key: self.show_section(k))
            btn.pack(fill=tk.X)
            self.nav_buttons[key] = btn

        # Right Content Area
        self.content_container = tk.Frame(body, bg=COLOR_PANEL, bd=1, relief=tk.SOLID, padx=20, pady=16)
        self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def show_section(self, key):
        self.current_section = key
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg="#282c34", fg=COLOR_TEAL, font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg=COLOR_SIDEBAR, fg=COLOR_TEXT, font=("Segoe UI", 10))

        # Clear existing view
        for child in self.content_container.winfo_children():
            child.destroy()

        handler = getattr(self, f"_view_{key}", None)
        if handler:
            handler()

    # 1. Appearance Section
    def _view_appearance(self):
        tk.Label(self.content_container, text="Desktop Appearance & Themes", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        # GTK Theme Selector
        tk.Label(self.content_container, text="Desktop Theme (XFCE / GTK):", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        theme_var = tk.StringVar(value="MicroOS-Dark")
        combo_theme = ttk.Combobox(self.content_container, textvariable=theme_var, values=["MicroOS-Dark", "Greybird-dark", "Adwaita-dark", "HighContrast"], state="readonly", width=30)
        combo_theme.pack(anchor="w", pady=(4, 12))

        def apply_theme():
            theme = theme_var.get()
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", theme], stderr=subprocess.DEVNULL)
            messagebox.showinfo("Theme Applied", f"Successfully activated GTK theme '{theme}'.")
        tk.Button(self.content_container, text="Apply Theme", bg=COLOR_TEAL, fg="#000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4, command=apply_theme).pack(anchor="w", pady=(0, 16))

        # Wallpaper Config
        tk.Label(self.content_container, text="Desktop Wallpaper:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        tk.Label(self.content_container, text="MicroOS Graphite Engineering Wallpaper (1920x1080 SVG/PNG)", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=COLOR_PANEL).pack(anchor="w", pady=(2, 6))

        def reset_wallpaper():
            wp_path = "/usr/share/backgrounds/microos/microos_wallpaper.png"
            subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/workspace0/last-image", "-s", wp_path], stderr=subprocess.DEVNULL)
            messagebox.showinfo("Wallpaper", "Restored MicroOS default graphite wallpaper.")
        tk.Button(self.content_container, text="Set Default MicroOS Wallpaper", bg=COLOR_SIDEBAR, fg=COLOR_TEXT, relief=tk.FLAT, padx=10, pady=4, command=reset_wallpaper).pack(anchor="w")

    # 2. Display Section
    def _view_display(self):
        tk.Label(self.content_container, text="Display & Resolution (xrandr)", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        # Query xrandr
        current_res = "1920x1080"
        try:
            out = subprocess.check_output(["xrandr"], stderr=subprocess.DEVNULL).decode("utf-8")
            for line in out.splitlines():
                if "*" in line:
                    current_res = line.split()[0]
                    break
        except Exception:
            pass

        tk.Label(self.content_container, text=f"Active Screen Resolution: {current_res}", font=("Segoe UI", 11), fg=COLOR_AMBER, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 10))

        tk.Label(self.content_container, text="Select Screen Resolution:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        res_var = tk.StringVar(value=current_res)
        combo_res = ttk.Combobox(self.content_container, textvariable=res_var, values=["1920x1080", "1600x900", "1366x768", "1280x720", "1024x768"], state="readonly", width=20)
        combo_res.pack(anchor="w", pady=(4, 12))

        def set_resolution():
            res = res_var.get()
            subprocess.run(["xrandr", "-s", res], stderr=subprocess.DEVNULL)
            messagebox.showinfo("Resolution Changed", f"Display resolution adjusted to {res}.")
        tk.Button(self.content_container, text="Apply Resolution", bg=COLOR_TEAL, fg="#000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4, command=set_resolution).pack(anchor="w")

    # 3. Keyboard Section
    def _view_keyboard(self):
        tk.Label(self.content_container, text="Keyboard Layout & Settings", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        tk.Label(self.content_container, text="Keyboard Layout (setxkbmap):", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        layout_var = tk.StringVar(value="us")
        combo_kb = ttk.Combobox(self.content_container, textvariable=layout_var, values=["us", "gb", "de", "fr", "in"], state="readonly", width=20)
        combo_kb.pack(anchor="w", pady=(4, 12))

        def apply_kb():
            subprocess.run(["setxkbmap", layout_var.get()], stderr=subprocess.DEVNULL)
            messagebox.showinfo("Keyboard", f"Set layout to '{layout_var.get()}'.")
        tk.Button(self.content_container, text="Set Layout", bg=COLOR_TEAL, fg="#000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4, command=apply_kb).pack(anchor="w")

    # 4. Mouse Section
    def _view_mouse(self):
        tk.Label(self.content_container, text="Mouse & Pointer Controls", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        tk.Label(self.content_container, text="Pointer Acceleration Rate:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        accel_scale = tk.Scale(self.content_container, from_=1, to=10, orient=tk.HORIZONTAL, bg=COLOR_PANEL, fg=COLOR_TEXT, highlightthickness=0, length=240)
        accel_scale.set(3)
        accel_scale.pack(anchor="w", pady=(4, 12))

        def apply_mouse():
            rate = accel_scale.get()
            subprocess.run(["xset", "m", str(rate), "1"], stderr=subprocess.DEVNULL)
            messagebox.showinfo("Mouse", f"Applied mouse acceleration rate {rate}.")
        tk.Button(self.content_container, text="Save Pointer Settings", bg=COLOR_TEAL, fg="#000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4, command=apply_mouse).pack(anchor="w")

    # 5. Network Section
    def _view_network(self):
        tk.Label(self.content_container, text="Networking Subsystem Controls", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        tk.Label(self.content_container, text="Network Service Operations:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        
        btn_frame = tk.Frame(self.content_container, bg=COLOR_PANEL)
        btn_frame.pack(anchor="w", pady=8)

        def restart_nm():
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], stderr=subprocess.DEVNULL)
            messagebox.showinfo("NetworkManager", "Restarted NetworkManager service daemon.")
        tk.Button(btn_frame, text="Restart NetworkManager", bg=COLOR_SIDEBAR, fg=COLOR_AMBER, relief=tk.FLAT, padx=10, pady=5, command=restart_nm).pack(side=tk.LEFT)

        def open_net_center():
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "..", "network-center", "network_center.py")])
        tk.Button(btn_frame, text="Launch Network Center GUI", bg=COLOR_TEAL, fg="#000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=5, command=open_net_center).pack(side=tk.LEFT, padx=10)

    # 6. Sound Section
    def _view_sound(self):
        tk.Label(self.content_container, text="Sound & Audio (PipeWire / ALSA)", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        tk.Label(self.content_container, text="Master Playback Volume:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(anchor="w")
        vol_scale = tk.Scale(self.content_container, from_=0, to=100, orient=tk.HORIZONTAL, bg=COLOR_PANEL, fg=COLOR_TEXT, highlightthickness=0, length=280)
        vol_scale.set(75)
        vol_scale.pack(anchor="w", pady=(4, 12))

        def apply_volume(val=None):
            v = vol_scale.get()
            subprocess.run(["amixer", "set", "Master", f"{v}%"], stderr=subprocess.DEVNULL)
        vol_scale.configure(command=apply_volume)

        def play_test_tone():
            subprocess.run(["speaker-test", "-t", "sine", "-f", "440", "-l", "1"], stderr=subprocess.DEVNULL)
        tk.Button(self.content_container, text="🔊 Play Sound Test Tone", bg=COLOR_TEAL, fg="#000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4, command=play_test_tone).pack(anchor="w")

    # 7. Storage Section
    def _view_storage(self):
        tk.Label(self.content_container, text="Storage & Disk Partitions", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        text_box = tk.Text(self.content_container, height=12, bg="#111417", fg=COLOR_TEXT, font=("Courier New", 9), relief=tk.FLAT)
        text_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        try:
            out = subprocess.check_output(["lsblk", "-o", "NAME,SIZE,FSTYPE,MOUNTPOINT"], stderr=subprocess.DEVNULL).decode("utf-8")
            text_box.insert(tk.END, out)
        except Exception:
            text_box.insert(tk.END, "lsblk output unavailable.")
        text_box.configure(state=tk.DISABLED)

    # 8. Users Section
    def _view_users(self):
        tk.Label(self.content_container, text="User Accounts & Security", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        user = os.environ.get("USER", "microos")
        tk.Label(self.content_container, text=f"Current Active User: {user}", font=("Segoe UI", 11, "bold"), fg=COLOR_GREEN, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 6))

        # Check sudo groups
        groups_str = "None"
        try:
            groups_str = subprocess.check_output(["groups"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except Exception:
            pass
        tk.Label(self.content_container, text=f"Group Memberships: {groups_str}", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

    # 9. System Info Section
    def _view_sysinfo(self):
        tk.Label(self.content_container, text="System Hardware & Kernel Specifications", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        info_text = tk.Text(self.content_container, height=14, bg="#111417", fg=COLOR_TEXT, font=("Courier New", 9), relief=tk.FLAT)
        info_text.pack(fill=tk.BOTH, expand=True)

        lines = [
            f"OS Distribution: MicroOS v1.0 (Beyond the Ordinary Desktop)",
            f"Base Operating System: Ubuntu 24.04 LTS (Noble Numbat)",
            f"Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)",
            f"Target Architecture: x86_64",
            f"Desktop Environment: XFCE 4.18 with Asymmetric Engineering Layout",
            f"Display Manager: LightDM"
        ]
        try:
            lines.append(f"Kernel Version: {os.uname().release}")
        except Exception:
            pass

        info_text.insert(tk.END, "\n".join(lines))
        info_text.configure(state=tk.DISABLED)

    # 10. Default Applications Section
    def _view_apps(self):
        tk.Label(self.content_container, text="Default Application Handlers", font=("Segoe UI", 14, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL).pack(anchor="w", pady=(0, 12))

        apps = [
            ("Web Browser", "Firefox (Standard HTTP/HTTPS)"),
            ("Terminal Emulator", "MicroShell / XFCE Terminal"),
            ("File Manager", "Thunar File Manager"),
            ("Text Editor", "Mousepad / Nano"),
            ("Research Lab", "Micro Multi-Core Scheduling Lab"),
            ("OS Puzzle Game", "Process Panic")
        ]

        for label, val in apps:
            row = tk.Frame(self.content_container, bg=COLOR_PANEL)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEAL, bg=COLOR_PANEL, width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=val, font=("Segoe UI", 9), fg=COLOR_TEXT, bg=COLOR_PANEL).pack(side=tk.LEFT)

if __name__ == "__main__":
    app = MicroControlCenter()
    app.mainloop()
