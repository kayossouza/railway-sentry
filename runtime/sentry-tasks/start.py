import json
import os
from wait import wait, web_url
wait([web_url() + '/_health/', os.environ['TASKBROKER_HOST'] + ':50051'])
commands = [
    ['/docker-entrypoint.sh', 'run', 'taskworker', '--concurrency=' + os.getenv('TASKWORKER_CONCURRENCY', '1'),
     '--rpc-host=' + os.environ['TASKBROKER_HOST'] + ':50051', '--health-check-file-path=/tmp/taskworker.health', '--max-child-task-count=10000'],
    ['/docker-entrypoint.sh', 'run', 'taskworker-scheduler'],
    ['python3', '/opt/railway/sentry-config/cleanup_runner.py'],
]
with open('/tmp/tasks.json', 'w') as file:
    json.dump(commands, file)
os.execvp('python3', ['python3', '/opt/railway/supervisor.py', '/tmp/tasks.json'])
