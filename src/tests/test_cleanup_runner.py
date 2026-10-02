import importlib.util
import pathlib
import subprocess
import sys
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runner',ROOT/'sentry-config/cleanup_runner.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)

class CleanupRunnerTest(unittest.TestCase):
    def test_transient_failure_is_reported_without_raising(self):
        self.assertEqual(runner.run_cleanup([sys.executable,'-c','raise SystemExit(7)'],2),7)

    def test_alive_but_stuck_cleanup_is_bounded(self):
        self.assertEqual(runner.run_cleanup([sys.executable,'-c','import time;time.sleep(60)'],.05),-1)
