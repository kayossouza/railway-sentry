"""Isolate transient cleanup failures, with bounded work and observable completion."""
import json
import os
import pathlib
import signal
import subprocess
import time


active = None


def stop(_signum, _frame):
    if active is not None and active.poll() is None:
        os.killpg(active.pid, signal.SIGTERM)
        try:
            active.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(active.pid, signal.SIGKILL)
            active.wait()
    raise SystemExit(0)


def run_cleanup(command, timeout):
    global active
    active = subprocess.Popen(command, start_new_session=True)
    try:
        return active.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(active.pid, signal.SIGKILL)
        active.wait()
        return -1
    finally:
        active = None


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    if int(os.environ['SENTRY_EVENT_RETENTION_DAYS']) <= 0:
        raise ValueError('Retention must be positive')
    status = {'last_completed': None, 'last_error': None, 'failures': 0}
    path = pathlib.Path('/tmp/cleanup-status.json')
    while True:
        code = run_cleanup(['python3', '/opt/railway/sentry-config/cleanup.py'], 3600)
        if code == 0:
            status.update(last_completed=time.time(), last_error=None, failures=0)
        else:
            status.update(last_error={'time': time.time(), 'exit': code},
                          failures=status['failures'] + 1)
            print('cleanup failed; background workers remain running', json.dumps(status), flush=True)
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(status))
        temp.replace(path)
        time.sleep(86400 if code == 0 else min(3600, 60 * 2 ** min(status['failures'], 6)))


if __name__ == '__main__':
    main()
