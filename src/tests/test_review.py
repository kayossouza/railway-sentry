import importlib.util
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('supervisor', ROOT / 'common/supervisor.py')
supervisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)

class ReviewTests(unittest.TestCase):
    def test_stale_heartbeat_not_ready(self):
        self.assertFalse(supervisor.heartbeats_ready({'worker': 0}, 181))
        self.assertTrue(supervisor.heartbeats_ready({'worker': 0}, 180))
        self.assertFalse(supervisor.heartbeats_ready({'worker': None}, 0))

    def test_feedback_disabled(self):
        self.assertIn("SENTRY_FEATURES['organizations:user-feedback-ui'] = False", (ROOT / 'sentry-config/sentry.conf.py').read_text())

    def test_gateway_waits_for_workers(self):
        start = (ROOT / 'gateway/start.sh').read_text()
        for name in ['SENTRY_CONSUMERS_HOST', 'SNUBA_CONSUMERS_HOST', 'TASKS_HOST']:
            self.assertIn(name, start)

    def test_fixture_absent_from_production(self):
        self.assertNotIn('COPY sdk/', (ROOT / 'web/Dockerfile').read_text())

    def test_feedback_route_and_navigation_excluded(self):
        config = (ROOT / 'gateway/nginx.conf.template').read_text()
        self.assertIn('Feedback is unsupported', config)
        self.assertIn('sub_filter', config)
