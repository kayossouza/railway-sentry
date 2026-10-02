"""Execute a diagnostic only inside the explicitly authorized disposable project."""
import pathlib, subprocess, sys, json, shlex
root=pathlib.Path(__file__).resolve().parent
project='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369'
status=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
if status['id']!=project or status['name']!='bounty-test-sentry-1':
    sys.exit('Refusing non-throwaway project')
service=sys.argv[1]
command=' '.join(shlex.quote(s) for s in sys.argv[2:])
r=subprocess.run(['railway','ssh','--project',project,'--environment','production','--service',service,'--',command],cwd=root)
sys.exit(r.returncode)
