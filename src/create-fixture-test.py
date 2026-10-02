import base64
import json
import pathlib
import shlex
import subprocess
import sys
root=pathlib.Path(__file__).resolve().parent
status=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
if status['id']!='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369' or status['name']!='bounty-test-sentry-1':sys.exit('Refusing non-throwaway project')
source=base64.b64encode((root/'sdk/create-project.py').read_bytes()).decode()
code=f'exec(__import__("base64").b64decode("{source}"))'
command='python3 -c '+shlex.quote(code)
result=subprocess.run(['railway','ssh','--project',status['id'],'--environment','production','--service','web','--',command],cwd=root,text=True,capture_output=True)
(root.parent/'.fixture-output.txt').write_text('\n'.join(line if not line.startswith('ACCEPTANCE_JSON=') else 'ACCEPTANCE_JSON=[redacted]' for line in (result.stdout+result.stderr).splitlines()))
lines=[line for line in result.stdout.splitlines() if line.startswith('ACCEPTANCE_JSON=')]
if not lines:
    print('Fixture failed:',result.returncode)
    sys.exit(1)
data=json.loads(lines[-1].split('=',1)[1])
(root.parent/'.acceptance.json').write_text(json.dumps(data))
(root.parent/'.acceptance.json').chmod(0o600)
print('Fixture created:',data['org'],data['project_id'])
