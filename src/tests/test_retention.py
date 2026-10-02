import datetime
import os
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'common'))
from retention import expiry, expired

class RetentionTest(unittest.TestCase):
    def test_restore_preserves_expiry_boundary(self):
        os.environ['SENTRY_EVENT_RETENTION_DAYS'] = '7'
        now = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        metadata = {'expires-at': expiry(datetime.timedelta(seconds=10), now)}
        self.assertFalse(expired(metadata, now + datetime.timedelta(seconds=9)))
        self.assertTrue(expired(dict(metadata), now + datetime.timedelta(seconds=10)))
        self.assertFalse(expired({}, now + datetime.timedelta(days=100)))
