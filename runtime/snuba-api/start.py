import os
import subprocess
from wait import wait
wait([os.environ['CLICKHOUSE_HOST'] + ':9000', os.environ['DEFAULT_BROKERS'], os.environ['REDIS_HOST'] + ':6379'])
subprocess.run(['python3', '/usr/src/snuba/docker_entrypoint.py', 'bootstrap', '--force'], check=True)
os.execvp('python3', ['python3', '/usr/src/snuba/docker_entrypoint.py', 'api'])
