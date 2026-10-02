import os
import sentry_sdk
sentry_sdk.init(dsn=os.environ["SENTRY_DSN"],
                traces_sample_rate=1.0, enable_logs=True)
with sentry_sdk.start_transaction(name="railway-example", op="task"):
    with sentry_sdk.start_span(op="work", description="child span"):
        sentry_sdk.logger.info("Railway structured log {name}", name="example")
        try:
            raise RuntimeError("Railway error example")
        except RuntimeError:
            sentry_sdk.capture_exception()
sentry_sdk.flush(timeout=30)
print("Uploaded Railway error example, structured log and railway-example trace", flush=True)
