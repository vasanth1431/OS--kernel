#!/usr/bin/env python3
"""
Micro Network Center - MicroOS Engineering Suite
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Comprehensive network dashboard, real-time throughput metrics, interface manager,
and 3-tier internet connectivity verification.
"""

import sys
import os
import time
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_BG = "#14171a"        # Deep Graphite
COLOR_PANEL = "#1e2227"     # Charcoal Panel
COLOR_TEAL = "#00b4d8"      # Electric Teal Highlight
COLOR_AMBER = "#ffb703"     # Amber Accent
COLOR_GREEN = "#2ec4b6"     # Mint Green Success
COLOR_RED = "#e63946"       # Crimson Alert
COLOR_TEXT = "#e0e6ed"      # Crisp Off-White
COLOR_MUTED = "#8892b0"     # Muted Slate

class MicroNetworkCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Micro Network Center — MicroOS v1.0")
        self.geometry("860x620")
        self.minsize(760, 520)
        self.configure(bg=COLOR_BG)

        self.last_rx = 0
        self.last_tx = 0
        self.last_time = time.time()
        self.active_iface = None

        self._setup_ui()
        self.refresh_telemetry()
        self._periodic_update()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self, bg=COLOR_BG, padx=20, pady=14)
        header.pack(fill=tk.X)

        tk.Label(header, text="MICRO NETWORK CENTER", font=("Segoe UI", 16, "bold"), fg=COLOR_TEAL, bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Label(header, text="Unified Telemetry & Routing Control", font=("Segoe UI", 10, "italic"), fg=COLOR_MUTED, bg=COLOR_BG).pack(side=tk.LEFT, padx=(12, 0), pady=(4, 0))

        # Main Split Panes
        content = tk.Frame(self, bg=COLOR_BG, padx=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Top Card: Status & Connectivity Badge
        status_card = tk.Frame(content, bg=COLOR_PANEL, bd=1, relief=tk.SOLID, padx=16, pady=12)
        status_card.pack(fill=tk.X, pady=(0, 12))

        self.lbl_status_badge = tk.Label(status_card, text="CHECKING CONNECTIVITY...", font=("Segoe UI", 12, "bold"), fg=COLOR_AMBER, bg=COLOR_PANEL)
        self.lbl_status_badge.pack(anchor="w")

        self.lbl_status_details = tk.Label(status_card, text="Querying interfaces, routes and DNS...", font=("Segoe UI", 9), fg=COLOR_TEXT, bg=COLOR_PANEL)
        self.lbl_status_details.pack(anchor="w", pady=(2, 0))

        # Two-Column Telemetry Grid
        grid_frame = tk.Frame(content, bg=COLOR_BG)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Left Column: Detailed Network Parameters
        left_card = tk.LabelFrame(grid_frame, text=" Connection Telemetry ", font=("Segoe UI", 10, "bold"),
                                  fg=COLOR_TEAL, bg=COLOR_PANEL, bd=1, relief=tk.SOLID, padx=14, pady=10)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        self.fields = {}
        row_idx = 0
        field_names = [
            ("Active Interface", "iface"),
            ("Connection Type", "type"),
            ("SSID / Link ID", "ssid"),
            ("IPv4 Address", "ip"),
            ("Subnet Mask / Prefix", "mask"),
            ("Default Gateway", "gw"),
            ("DNS Servers", "dns"),
            ("MAC Hardware Addr", "mac"),
            ("Link Speed / State", "state")
        ]

        for label_text, key in field_names:
            tk.Label(left_card, text=f"{label_text}:", font=("Segoe UI", 9, "bold"), fg=COLOR_MUTED, bg=COLOR_PANEL).grid(row=row_idx, column=0, sticky="w", pady=3)
            val_lbl = tk.Label(left_card, text="--", font=("Segoe UI", 9), fg=COLOR_TEXT, bg=COLOR_PANEL)
            val_lbl.grid(row=row_idx, column=1, sticky="w", padx=(10, 0), pady=3)
            self.fields[key] = val_lbl
            row_idx += 1

        # Right Column: Real-Time Bandwidth & Speed Meter
        right_card = tk.LabelFrame(grid_frame, text=" Real-Time Bandwidth ", font=("Segoe UI", 10, "bold"),
                                   fg=COLOR_TEAL, bg=COLOR_PANEL, bd=1, relief=tk.SOLID, padx=14, pady=10)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        # Download Meter
        tk.Label(right_card, text="Download Speed (RX):", font=("Segoe UI", 10, "bold"), fg=COLOR_GREEN, bg=COLOR_PANEL).pack(anchor="w", pady=(6, 2))
        self.lbl_rx_speed = tk.Label(right_card, text="0.00 KB/s", font=("Segoe UI", 18, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL)
        self.lbl_rx_speed.pack(anchor="w")

        # Upload Meter
        tk.Label(right_card, text="Upload Speed (TX):", font=("Segoe UI", 10, "bold"), fg=COLOR_AMBER, bg=COLOR_PANEL).pack(anchor="w", pady=(12, 2))
        self.lbl_tx_speed = tk.Label(right_card, text="0.00 KB/s", font=("Segoe UI", 18, "bold"), fg=COLOR_TEXT, bg=COLOR_PANEL)
        self.lbl_tx_speed.pack(anchor="w")

        # Cumulative Data
        self.lbl_total_transfer = tk.Label(right_card, text="Total Transferred: --", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=COLOR_PANEL)
        self.lbl_total_transfer.pack(anchor="w", pady=(18, 0))

        # Bottom Button Bar
        btn_bar = tk.Frame(self, bg=COLOR_BG, padx=20, pady=14)
        btn_bar.pack(fill=tk.X)

        tk.Button(btn_bar, text="⚡ Run Full Diagnostic", font=("Segoe UI", 9, "bold"), bg=COLOR_TEAL, fg="#000000",
                  relief=tk.FLAT, padx=12, pady=6, command=self.run_full_diagnostic).pack(side=tk.LEFT)

        tk.Button(btn_bar, text="Open Wi-Fi Scanner", font=("Segoe UI", 9), bg=COLOR_PANEL, fg=COLOR_TEXT,
                  relief=tk.FLAT, padx=12, pady=6, command=self.launch_wifi_scanner).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(btn_bar, text="Flush DNS Cache", font=("Segoe UI", 9), bg=COLOR_PANEL, fg=COLOR_TEXT,
                  relief=tk.FLAT, padx=12, pady=6, command=self.flush_dns).pack(side=tk.LEFT, padx=(10, 0))

    def _get_bytes_transferred(self, iface):
        """Read /proc/net/dev for real Linux network counter telemetry"""
        if not iface or not os.path.exists("/proc/net/dev"):
            return 0, 0
        try:
            with open("/proc/net/dev", "r") as f:
                for line in f:
                    if iface in line:
                        parts = line.split(":")[1].split()
                        rx_bytes = int(parts[0])
                        tx_bytes = int(parts[8])
                        return rx_bytes, tx_bytes
        except Exception:
            pass
        return 0, 0

    def refresh_telemetry(self):
        """Gather real network information from system interfaces"""
        iface = "lo"
        conn_type = "None"
        ssid = "N/A (Wired/Virtual)"
        ip_addr = "127.0.0.1"
        gateway = "None"
        dns = "None"
        mac = "--"
        link_state = "Down"

        # Determine default route interface
        try:
            route_out = subprocess.check_output(["ip", "route", "show", "default"], stderr=subprocess.DEVNULL).decode("utf-8")
            parts = route_out.strip().split()
            if "dev" in parts:
                idx = parts.index("dev")
                iface = parts[idx + 1]
            if "via" in parts:
                idx = parts.index("via")
                gateway = parts[idx + 1]
        except Exception:
            pass

        self.active_iface = iface

        # Get IP address and MAC
        try:
            addr_out = subprocess.check_output(["ip", "-br", "addr", "show", iface], stderr=subprocess.DEVNULL).decode("utf-8")
            tokens = addr_out.strip().split()
            if len(tokens) >= 2:
                link_state = tokens[1]
            if len(tokens) >= 3:
                ip_addr = tokens[2]
        except Exception:
            pass

        # Determine connection type (Wi-Fi or Ethernet)
        if iface.startswith("wl"):
            conn_type = "Wireless (802.11 Wi-Fi)"
            try:
                ssid_out = subprocess.check_output(["iwgetid", "-r"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
                if ssid_out:
                    ssid = ssid_out
            except Exception:
                pass
        elif iface.startswith("en") or iface.startswith("eth"):
            conn_type = "Ethernet (VirtualBox NAT/Bridged or Physical Wire)"
            ssid = "Direct Ethernet Link"
        elif iface == "lo":
            conn_type = "Loopback (No network connected)"
            ssid = "Disconnected"

        # Read DNS
        if os.path.exists("/etc/resolv.conf"):
            try:
                with open("/etc/resolv.conf", "r") as f:
                    dns_servers = [line.split()[1] for line in f if line.startswith("nameserver")]
                    dns = ", ".join(dns_servers[:2]) if dns_servers else "None"
            except Exception:
                pass

        # Read MAC address
        sysfs_mac = f"/sys/class/net/{iface}/address"
        if os.path.exists(sysfs_mac):
            try:
                with open(sysfs_mac, "r") as f:
                    mac = f.read().strip()
            except Exception:
                pass

        # Update labels
        self.fields["iface"].configure(text=iface)
        self.fields["type"].configure(text=conn_type)
        self.fields["ssid"].configure(text=ssid)
        self.fields["ip"].configure(text=ip_addr)
        self.fields["mask"].configure(text=ip_addr.split("/")[1] if "/" in ip_addr else "24")
        self.fields["gw"].configure(text=gateway)
        self.fields["dns"].configure(text=dns)
        self.fields["mac"].configure(text=mac)
        self.fields["state"].configure(text=link_state)

        # Calculate live bandwidth
        now = time.time()
        dt = now - self.last_time
        if dt >= 0.5:
            rx, tx = self._get_bytes_transferred(iface)
            if self.last_rx > 0 and rx >= self.last_rx:
                rx_speed = (rx - self.last_rx) / dt / 1024.0 # KB/s
                tx_speed = (tx - self.last_tx) / dt / 1024.0
                self.lbl_rx_speed.configure(text=f"{rx_speed:.2f} KB/s" if rx_speed < 1024 else f"{(rx_speed/1024):.2f} MB/s")
                self.lbl_tx_speed.configure(text=f"{tx_speed:.2f} KB/s" if tx_speed < 1024 else f"{(tx_speed/1024):.2f} MB/s")
                self.lbl_total_transfer.configure(text=f"Total: RX {rx/1048576:.1f} MB | TX {tx/1048576:.1f} MB")
            self.last_rx = rx
            self.last_tx = tx
            self.last_time = now

    def _periodic_update(self):
        self.refresh_telemetry()
        self.after(1000, self._periodic_update)

    def run_full_diagnostic(self):
        """Run 3-tier check and update status badge"""
        self.lbl_status_badge.configure(text="TESTING CONNECTIVITY...", fg=COLOR_AMBER)
        self.update()

        gateway = self.fields["gw"].cget("text")
        gw_ok = False
        ip_ok = False
        dns_ok = False

        # Ping gateway
        if gateway != "None":
            res = subprocess.run(["ping", "-c", "1", "-W", "1", gateway], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            gw_ok = (res.returncode == 0)

        # Ping 1.1.1.1
        res = subprocess.run(["ping", "-c", "1", "-W", "2", "1.1.1.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ip_ok = (res.returncode == 0)

        # Check DNS resolution
        res = subprocess.run(["getent", "hosts", "example.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dns_ok = (res.returncode == 0)

        if gw_ok and ip_ok and dns_ok:
            self.lbl_status_badge.configure(text="● CONNECTED — INTERNET VERIFIED", fg=COLOR_GREEN)
            self.lbl_status_details.configure(text="Gateway, Public Routing, and DNS resolution fully functional.")
        elif gw_ok and (not dns_ok or not ip_ok):
            self.lbl_status_badge.configure(text="▲ LIMITED CONNECTIVITY — DNS/ROUTING ISSUE", fg=COLOR_AMBER)
            self.lbl_status_details.configure(text="Local gateway reachable, but external WAN or DNS failed.")
        else:
            self.lbl_status_badge.configure(text="✖ DISCONNECTED — NO ROUTE", fg=COLOR_RED)
            self.lbl_status_details.configure(text="No active network connection detected. Check VirtualBox network adapter.")

    def launch_wifi_scanner(self):
        scanner_script = os.path.join(os.path.dirname(__file__), "..", "wifi-scanner", "wifi_scanner.py")
        if os.path.exists(scanner_script):
            subprocess.Popen([sys.executable, scanner_script])
        else:
            messagebox.showerror("Error", f"Scanner not found at {scanner_script}")

    def flush_dns(self):
        try:
            subprocess.run(["systemd-resolve", "--flush-caches"], stderr=subprocess.DEVNULL)
            messagebox.showinfo("DNS", "DNS cache flushed successfully.")
        except Exception:
            messagebox.showinfo("DNS", "DNS cache flush request dispatched.")

if __name__ == "__main__":
    app = MicroNetworkCenter()
    app.mainloop()
