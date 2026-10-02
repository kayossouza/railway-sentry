"""Restart every candidate service, exclusively in the disposable test project."""
import json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parent
project='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369'
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
assert s['id']==project and s['name']=='bounty-test-sentry-1'
for name in json.loads((root/'services.json').read_text()):
 r=subprocess.run(['railway','restart','--project',project,'--environment','production','--service',name,'--yes','--json'],cwd=root,capture_output=True,text=True)
 print(name,r.returncode,r.stdout,r.stderr,flush=True)
 if r.returncode: raise RuntimeError(name)
