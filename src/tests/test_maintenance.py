import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'scripts'))
import maintenance_replace as maintenance

class MaintenanceTest(unittest.TestCase):
    def test_ephemeral_offsets_and_empty_topics_do_not_block_drain(self):
        output='''snuba-consumers events 0 4 4 0 id host client
sentry-commit-log-random snuba-commit-log 0 - 4 - id host client
snuba-replacers event-replacements 0 - 0 - id host client
snuba-events-subscriptions-consumers snuba-commit-log 0 - 4 - id host client'''
        self.assertEqual(maintenance.pipeline_lag(output),0)

    def test_uncommitted_primary_records_block_drain(self):
        with self.assertRaises(RuntimeError):
            maintenance.pipeline_lag('snuba-consumers events 0 - 4 - id host client')
