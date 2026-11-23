#!/usr/bin/env python3
"""
MicroOS Automated Verification and Validation Test Suite
Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Validates scripts, commands, algorithms, and application syntax.
"""

import os
import sys
import subprocess
import time
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class MicroOSTestCase(unittest.TestCase):
    def test_01_repo_structure(self):
        """Verify presence of core directories and launcher files"""
        required_paths = [
            "Start-MicroOS.bat",
            "start-microos.sh",
            "README.md",
            ".gitignore",
            "microos/build.sh",
            "microos/microshell/microshellrc",
            "microos/network-center/network_center.py",
            "microos/wifi-scanner/wifi_scanner.py",
            "microos/system-monitor/system_monitor.py",
            "microos/control-center/control_center.py",
            "microos/application-hub/application_hub.py",
            "microos/process-panic/main.py",
            "microos/research-lab/sched_exp.py",
            "microos/research-lab/run_benchmarks.py",
            "microos/research-lab/generate_graphs.py",
            "kernel-lab/src/boot.s",
            "kernel-lab/src/kernel.c",
            "kernel-lab/Makefile",
            "kernel-lab/README.md"
        ]
        for p in required_paths:
            full_p = os.path.join(PROJECT_ROOT, p)
            self.assertTrue(os.path.exists(full_p), f"Missing required file: {p}")

    def test_02_microshell_commands_exist(self):
        """Verify all 12 MicroShell binary commands exist and have shebangs"""
        bin_dir = os.path.join(PROJECT_ROOT, "microos", "microshell", "bin")
        commands = [
            "micro-info", "micro-status", "micro-health", "micro-network",
            "micro-wifi", "micro-ip", "micro-internet", "micro-process",
            "micro-storage", "micro-apps", "micro-update", "micro-help"
        ]
        for cmd in commands:
            cmd_path = os.path.join(bin_dir, cmd)
            self.assertTrue(os.path.exists(cmd_path), f"Missing binary command: {cmd}")
            with open(cmd_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
                self.assertTrue(first_line.startswith("#!"), f"Missing shebang in {cmd}")

    def test_03_research_algorithm_logic(self):
        """Test Multi-Core Scheduling task generator and split algorithms"""
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "microos", "research-lab"))
        import sched_exp

        # Test task generator
        tasks = sched_exp.make_tasks(100)
        self.assertEqual(len(tasks), 100)
        self.assertEqual(tasks[:10], [200] * 10, "First 10% must be 10x costlier (200)")
        self.assertEqual(tasks[10:], [20] * 90, "Remaining 90% must be light (20)")

        # Test block split
        parts_block = sched_exp.split(tasks, 4, "block")
        self.assertEqual(len(parts_block), 4)
        self.assertEqual(sum(len(p) for p in parts_block), 100)

        # Test round-robin split
        parts_rr = sched_exp.split(tasks, 4, "rr")
        self.assertEqual(len(parts_rr), 4)
        self.assertEqual(sum(len(p) for p in parts_rr), 100)

        # Test single run
        wall, tp, imb = sched_exp.run_once("none", "dynamic", 2, 50, 5)
        self.assertGreater(wall, 0.0)
        self.assertGreater(tp, 0.0)
        self.assertGreaterEqual(imb, 1.0)

    def test_04_desktop_entries_validity(self):
        """Ensure all .desktop files have required FreeDesktop keys"""
        app_dir = os.path.join(PROJECT_ROOT, "microos", "desktop", "applications")
        desktop_files = [f for f in os.listdir(app_dir) if f.endswith(".desktop")]
        self.assertGreater(len(desktop_files), 5)
        for df in desktop_files:
            with open(os.path.join(app_dir, df), "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("[Desktop Entry]", content)
                self.assertIn("Type=Application", content)
                self.assertIn("Name=", content)
                self.assertIn("Exec=", content)

def run_tests():
    print("=" * 72)
    print(" MICROOS v1.0 AUTOMATED VALIDATION TEST SUITE")
    print(" Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)")
    print("=" * 72)
    suite = unittest.TestLoader().loadTestsFromTestCase(MicroOSTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
