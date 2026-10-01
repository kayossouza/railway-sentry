"""Run in a same-environment Railway service, never via local railway run."""
import json
import os
import time
import uuid
import sentry_sdk

marker = os.getenv('TEST_MARKER', 'bounty-' + uuid.uuid4().hex)
sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'], traces_sample_rate=1.0,
    enable_logs=True, send_default_pii=False,
    environment='bounty-validation', release='sentry-railway-26.9.0',
)
count = int(os.getenv('TEST_COUNT', '1'))
for index in range(count):
    sample = marker if count == 1 else marker + '-' + str(index)
    with sentry_sdk.start_transaction(name=sample, op='bounty.test') as transaction:
        trace_id = transaction.trace_id
        with sentry_sdk.start_span(op='bounty.child', description=sample + '-child'):
            sentry_sdk.logger.info('Sentry Railway marker {marker}', marker=sample, pipeline='structured-log')
            try:
                raise RuntimeError(sample)
            except RuntimeError:
                event_id = sentry_sdk.capture_exception()
            time.sleep(.05)
    sentry_sdk.flush(timeout=30)
    print(json.dumps({'marker':sample,'error_event_id':event_id,'trace_id':trace_id}), flush=True)
