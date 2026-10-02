"""Taskbroker requires Kafka topics created by the Web bootstrap."""
import os
from wait import wait

wait([os.environ['WEB_URL'] + '/_health/'])
os.execv('/opt/taskbroker', ['/opt/taskbroker', '-c', '/etc/taskbroker/config.yml'])
