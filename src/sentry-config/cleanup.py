"""One bounded cleanup run. Called by cleanup_runner; failures are isolated."""
import datetime
import os
import subprocess
from storage import client
from retention import expired


def main():
    days = int(os.environ['SENTRY_EVENT_RETENTION_DAYS'])
    if days <= 0:
        raise ValueError('Retention must be positive')
    subprocess.run(['/docker-entrypoint.sh', 'cleanup', '--days', str(days)],
                   check=True, timeout=1800)
    now = datetime.datetime.now(datetime.timezone.utc)
    s3 = client()
    bucket = os.environ['NODE_BUCKET']
    for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket, Prefix='nodestore/'):
        keys = []
        for item in page.get('Contents', []):
            metadata = s3.head_object(Bucket=bucket, Key=item['Key']).get('Metadata', {})
            if expired(metadata, now):
                keys.append({'Key': item['Key']})
        if keys:
            result = s3.delete_objects(Bucket=bucket, Delete={'Objects': keys})
            if result.get('Errors'):
                raise RuntimeError('Nodestore expiry failed')


if __name__ == '__main__':
    main()
