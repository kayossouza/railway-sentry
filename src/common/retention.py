"""Expiry metadata survives object restore; legacy objects are retained conservatively."""
import datetime
import os


def expiry(ttl=None, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    default = datetime.timedelta(days=int(os.environ['SENTRY_EVENT_RETENTION_DAYS']))
    return str((now + (ttl if ttl is not None else default)).timestamp())


def expired(metadata, now):
    value = metadata.get('expires-at')
    return value is not None and float(value) <= now.timestamp()
