import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'common/supervisor.py'

class SupervisorTest(unittest.TestCase):
    def test_child_failure_terminates_sibling(self):
        with tempfile.TemporaryDirectory() as directory:
            pidfile = pathlib.Path(directory) / 'pid'
            commands = pathlib.Path(directory) / 'commands.json'
            import json
            commands.write_text(json.dumps([
                [sys.executable, '-c', 'import time; time.sleep(1); raise SystemExit(7)'],
                [sys.executable, '-c', f'import os,time; open({str(pidfile)!r},"w").write(str(os.getpid())); time.sleep(60)'],
            ]))
            result = subprocess.run([sys.executable, str(SCRIPT), str(commands)], timeout=8)
            self.assertEqual(result.returncode, 7)
            pid = int(pidfile.read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_signal_terminates_children(self):
        with tempfile.TemporaryDirectory() as directory:
            import json
            commands = pathlib.Path(directory) / 'commands.json'
            commands.write_text(json.dumps([[sys.executable, '-c', 'import time; time.sleep(60)']]))
            process = subprocess.Popen([sys.executable, str(SCRIPT), str(commands)])
            time.sleep(.3)
            process.terminate()
            self.assertEqual(process.wait(timeout=5), 0)

if __name__ == '__main__':
    unittest.main()
