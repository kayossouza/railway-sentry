import os
from wait import wait
wait([os.environ['SNUBA_API_URL'] + '/health'])
os.execvp('python3', ['python3', '/opt/railway/supervisor.py', '/opt/railway/service/commands.json'])
