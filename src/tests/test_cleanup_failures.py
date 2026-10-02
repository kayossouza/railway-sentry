import importlib.util
import os
import pathlib
import subprocess
import sys
import types
import unittest
from unittest.mock import Mock, patch
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'common'))

class CleanupFailureTest(unittest.TestCase):
    def load(self, client):
        spec=importlib.util.spec_from_file_location('cleanup',ROOT/'sentry-config/cleanup.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'storage':types.SimpleNamespace(client=lambda:client)}):
            spec.loader.exec_module(module)
        return module

    def test_s3_delete_error_reports_failure(self):
        client=Mock()
        client.get_paginator.return_value.paginate.return_value=[{'Contents':[{'Key':'nodestore/test'}]}]
        client.head_object.return_value={'Metadata':{'expires-at':'0'}}
        client.delete_objects.return_value={'Errors':[{'Code':'InternalError'}]}
        cleanup=self.load(client)
        with patch.dict(os.environ,{'SENTRY_EVENT_RETENTION_DAYS':'7','NODE_BUCKET':'test'}), patch.object(cleanup.subprocess,'run'):
            with self.assertRaisesRegex(RuntimeError,'Nodestore expiry failed'):
                cleanup.main()

    def test_relational_failure_reports_failure_before_s3_mutation(self):
        client=Mock();cleanup=self.load(client)
        with patch.dict(os.environ,{'SENTRY_EVENT_RETENTION_DAYS':'7'}), patch.object(cleanup.subprocess,'run',side_effect=subprocess.CalledProcessError(1,'cleanup')):
            with self.assertRaises(subprocess.CalledProcessError):
                cleanup.main()
        client.delete_objects.assert_not_called()
