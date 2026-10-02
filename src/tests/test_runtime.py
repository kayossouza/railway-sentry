import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('wait',ROOT/'common/wait.py')
wait=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wait)

class RuntimeTest(unittest.TestCase):
    def test_empty_web_domain_does_not_deadlock_relay_identity(self):
        with patch.dict(os.environ,{'WEB_URL':'http://:9000'}):
            self.assertEqual(wait.web_url(),'http://web.railway.internal:9000')
        with patch.dict(os.environ,{'WEB_URL':'http://custom.railway.internal:9000'}):
            self.assertEqual(wait.web_url(),'http://custom.railway.internal:9000')

    def test_missing_consumer_heartbeat_fails_group(self):
        with tempfile.TemporaryDirectory() as directory:
            commands=pathlib.Path(directory)/'commands.json'
            commands.write_text(json.dumps([[sys.executable,'-c','import time;time.sleep(60)',
                                            '--health-check-file',str(pathlib.Path(directory)/'missing')]]))
            env={**os.environ,'HEARTBEAT_START_PERIOD':'0'}
            env.pop('PORT',None)
            result=subprocess.run([sys.executable,str(ROOT/'common/supervisor.py'),str(commands)],env=env,timeout=5)
            self.assertEqual(result.returncode,1)

if __name__=='__main__': unittest.main()
