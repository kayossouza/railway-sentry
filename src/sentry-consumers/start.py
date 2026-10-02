import os
from wait import wait, web_url
wait([web_url() + '/_health/', os.environ['SNUBA'] + '/health'])
os.execvp('python3', ['python3', '/opt/railway/supervisor.py', '/opt/railway/service/commands.json'])
