# Original pinned upstream settings followed by Railway-specific overrides.
import os
import json
import runpy
import time
import urllib.parse
from storage import client

globals().update(runpy.run_path('/etc/sentry/upstream.py'))
DATABASES['default'].update(HOST=os.environ['POSTGRES_HOST'], PASSWORD=os.environ['POSTGRES_PASSWORD'], PORT='5432')
SENTRY_OPTIONS['redis.clusters']['default']['hosts'][0].update(host=os.environ['REDIS_HOST'], password=os.environ['REDIS_PASSWORD'])
CACHES['default']['LOCATION'] = [os.environ['MEMCACHED_HOST'] + ':11211']
DEFAULT_KAFKA_OPTIONS['bootstrap.servers'] = os.environ['KAFKA_BROKERS']
SENTRY_OPTIONS['system.url-prefix'] = os.environ['PUBLIC_URL']
SENTRY_OPTIONS['system.secret-key'] = os.environ['SENTRY_SYSTEM_SECRET_KEY']
SENTRY_OPTIONS['symbolicator.options'] = {'url': 'http://' + os.environ['SYMBOLICATOR_HOST'] + ':3021'}
SENTRY_OPTIONS['filestore.backend'] = 's3'
SENTRY_OPTIONS['filestore.options'] = {
    'access_key': os.environ['FILE_ACCESS_KEY'], 'secret_key': os.environ['FILE_SECRET_KEY'],
    'bucket_name': os.environ['FILE_BUCKET'], 'endpoint_url': os.environ['FILE_ENDPOINT'],
    'region_name': os.environ['FILE_REGION'],
}
SENTRY_NODESTORE_OPTIONS.update(
    endpoint_url=os.environ['NODE_ENDPOINT'], bucket_name=os.environ['NODE_BUCKET'],
    bucket_path='nodestore', region_name=os.environ['NODE_REGION'],
    aws_access_key_id=os.environ['NODE_ACCESS_KEY'], aws_secret_access_key=os.environ['NODE_SECRET_KEY'],
)
# Trust only this installation's cryptographic identity, not network address ranges.
deadline = time.monotonic() + int(os.getenv('STARTUP_TIMEOUT', '900'))
while True:
    try:
        identity = json.loads(client().get_object(Bucket=os.environ['NODE_BUCKET'], Key='relay/public.json')['Body'].read())
        break
    except Exception:
        if time.monotonic() > deadline:
            raise RuntimeError('Relay identity unavailable; bootstrap aborted')
        time.sleep(3)
SENTRY_RELAY_WHITELIST_PK = [identity['public_key']]
INTERNAL_SYSTEM_IPS = ()
SENTRY_RELAY_OPEN_REGISTRATION = False
SENTRY_RELAY_STATIC_AUTH = {identity['id']: {'public_key': identity['public_key'], 'internal': True}}
TASKWORKER_RPC_HOST = os.environ['TASKBROKER_HOST'] + ':50051'
SENTRY_WEB_OPTIONS['workers'] = int(os.getenv('WEB_WORKERS', '1'))
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [os.environ['PUBLIC_URL']]
ALLOWED_HOSTS = ['*']
# Explicit exclusions audited against the pinned upstream feature profile.
for feature in ('organizations:continuous-profiling', 'organizations:continuous-profiling-stats', 'organizations:monitors', 'organizations:ourlogs-replay-ui', 'organizations:profiling', 'organizations:profiling-view', 'organizations:session-replay', 'organizations:tracemetrics-alerts', 'organizations:tracemetrics-enabled', 'organizations:tracemetrics-equations-in-alerts', 'organizations:tracemetrics-equations-in-explore', 'organizations:tracemetrics-ingestion', 'organizations:tracemetrics-multi-metric-selection-in-dashboards', 'organizations:tracemetrics-pii-scrubbing-ui', 'organizations:tracemetrics-stats-bytes-ui', 'organizations:tracemetrics-units-ui', 'organizations:uptime', 'organizations:uptime-create-issues'):
    SENTRY_FEATURES[feature] = False
SENTRY_FEATURES['organizations:user-feedback-ui'] = False

# The pinned image always dispatches segment tasks; the older rollout option is removed.
SENTRY_OPTIONS.pop('spans.buffer.process-segments-task-rollout-rate', None)
GEOIP_PATH_MMDB = None

SENTRY_NODESTORE = "nodestore.ExpiringNodeStorage"

# Optional external SMTP; no resident mail service.
SENTRY_OPTIONS['mail.backend'] = 'dummy'
if os.getenv('SMTP_HOST'):
    SENTRY_OPTIONS.update({
        'mail.backend': 'smtp', 'mail.host': os.environ['SMTP_HOST'],
        'mail.port': int(os.getenv('SMTP_PORT', '587')),
        'mail.username': os.getenv('SMTP_USER', ''),
        'mail.password': os.getenv('SMTP_PASSWORD', ''),
        'mail.use-tls': os.getenv('SMTP_TLS', 'true').lower() == 'true',
        'mail.from': os.getenv('SMTP_FROM', os.environ.get('ADMIN_EMAIL', '')),
    })

# Legacy metric extraction/metric alert subscriptions have no workers in this profile.
for feature in ('organizations:transaction-metrics-extraction',
                'organizations:on-demand-metrics-extraction',
                'projects:span-metrics-extraction', 'projects:span-metrics-extraction-addons',
                'organizations:metric-alerts', 'organizations:incidents'):
    SENTRY_FEATURES[feature] = False

# Required for a new administrator to create their first organization in the UI.
SENTRY_FEATURES['organizations:create'] = True
