import os
import subprocess
import psycopg2
from wait import wait

wait([os.environ['POSTGRES_HOST'] + ':5432', os.environ['REDIS_HOST'] + ':6379',
      os.environ['KAFKA_BROKERS'], os.environ['SNUBA'] + '/health'])
connection = psycopg2.connect(host=os.environ['POSTGRES_HOST'], user='postgres',
                            dbname='postgres', password=os.environ['POSTGRES_PASSWORD'])
connection.autocommit = True
with connection.cursor() as cursor:
    cursor.execute('SELECT pg_advisory_lock(269000)')
    subprocess.run(['/docker-entrypoint.sh', 'upgrade', '--noinput', '--create-kafka-topics'], check=True)
    # Uses the ORM after migrations; an existing admin password is never overwritten.
    subprocess.run(['python3', '/opt/railway/sentry-config/admin.py'], check=True)
    cursor.execute('SELECT pg_advisory_unlock(269000)')
connection.close()
os.execv('/docker-entrypoint.sh', ['/docker-entrypoint.sh', 'run', 'web'])
