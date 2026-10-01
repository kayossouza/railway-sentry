"""Supervise process groups and independently consume upstream heartbeat files."""
import http.server
import json
import os
import pathlib
import signal
import subprocess
import sys
import threading
import time

stopping = False
ready = False


def stop(_signum, _frame):
    global stopping
    stopping = True


class Health(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if ready and self.path == '/ready' else 503)
        self.end_headers()
        self.wfile.write(b'ready' if ready else b'waiting for consumer heartbeats')

    def log_message(self, *_args):
        pass


def heartbeat_paths(commands):
    paths = []
    for command in commands:
        for index, arg in enumerate(command):
            if arg.startswith(('--health-check-file', '--healthcheck-file-path')):
                paths.append(pathlib.Path(arg.split('=', 1)[1] if '=' in arg else command[index + 1]))
    if len(paths) != len(set(paths)):
        raise ValueError('Each consumer must have its own heartbeat path')
    return paths


def heartbeats_ready(seen, now):
    return all(stamp is not None and now - stamp <= 180 for stamp in seen.values())


def main():
    global ready
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    commands = json.load(open(sys.argv[1]))
    paths = heartbeat_paths(commands)
    seen = {path: None for path in paths}
    children = []
    status = 0
    started = time.monotonic()
    checked = None
    if 'PORT' in os.environ:
        server = http.server.HTTPServer(('0.0.0.0', int(os.environ['PORT'])), Health)
        threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        for command in commands:
            print('starting:', command, flush=True)
            children.append(subprocess.Popen(command, start_new_session=True))
        while not stopping:
            for child in children:
                code = child.poll()
                if code is not None:
                    status = code or 1
                    print('child exited:', child.pid, code, flush=True)
                    return status
            now = time.monotonic()
            if checked is None or now - checked >= 60:
                checked = now
                for path in paths:
                    try:
                        path.unlink()
                        seen[path] = now
                    except FileNotFoundError:
                        pass
                ready = heartbeats_ready(seen, now)
                if now - started > int(os.getenv('HEARTBEAT_START_PERIOD', '600')):
                    if any(timestamp is None or now - timestamp > 180 for timestamp in seen.values()):
                        print('consumer heartbeat missing or stale', flush=True)
                        return 1
            ready = heartbeats_ready(seen, now)
            time.sleep(.25)
    finally:
        ready = False
        for child in children:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
        deadline = time.monotonic() + 3
        for child in children:
            try:
                child.wait(timeout=max(.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    return status


if __name__ == '__main__':
    sys.exit(main())
