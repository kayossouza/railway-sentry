"""Bounded runtime dependency waits; secrets never appear in diagnostics."""
import os
import socket
import sys
import time
import urllib.request
import urllib.parse


def web_url():
    value = os.getenv('WEB_URL', '')
    return value if urllib.parse.urlsplit(value).hostname else 'http://web.railway.internal:9000'


def wait(targets):
    deadline = time.monotonic() + int(os.getenv('STARTUP_TIMEOUT', '900'))
    for target in targets:
        while True:
            try:
                if target.startswith(('http://', 'https://')):
                    with urllib.request.urlopen(target, timeout=5) as response:
                        if response.status != 200:
                            raise OSError('not ready')
                else:
                    host, port = target.rsplit(':', 1)
                    with socket.create_connection((host, int(port)), timeout=5):
                        pass
                break
            except (OSError, ValueError):
                if time.monotonic() >= deadline:
                    raise SystemExit('dependency readiness deadline exceeded')
                time.sleep(3)


if __name__ == '__main__':
    wait(sys.argv[1:])
