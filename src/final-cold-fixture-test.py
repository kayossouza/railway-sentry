"""Acceptance fixture and SDK for the isolated cold-deploy test project."""
import base64,json,pathlib,shlex,subprocess
root=pathlib.Path(__file__).resolve().parent
work=root.parent/'test4'
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=work))
assert s['id']=='f4ce2e9f-f8b2-4508-b440-d08d5b48baef' and s['name']=='bounty-test-sentry-4'
code=base64.b64encode((root/'sdk/create-project.py').read_bytes()).decode()
command='python3 -c '+shlex.quote('exec(__import__("base64").b64decode("'+code+'"))')
r=subprocess.run(['railway','ssh','--project',s['id'],'--environment','production','--service','web','--',command],cwd=work,capture_output=True,text=True)
line=next((line for line in r.stdout.splitlines() if line.startswith('ACCEPTANCE_JSON=')),None)
(root/'evidence/cold4-fixture.txt').write_text('\n'.join(line if not line.startswith('ACCEPTANCE_JSON=') else 'ACCEPTANCE_JSON=[redacted]' for line in (r.stdout+r.stderr).splitlines()))
assert line,'Fixture failed'
fixture=json.loads(line.split('=',1)[1]);(root.parent/'.cold4-acceptance.json').write_text(json.dumps(fixture));(root.parent/'.cold4-acceptance.json').chmod(0o600)
services={e['node']['name']:e['node']['id'] for e in s['services']['edges']}
if 'sdk' not in services:
 services['sdk']=json.loads(subprocess.check_output(['railway','add','--service','sdk','--json'],cwd=work))['id']
env=s['environments']['edges'][0]['node']['id']
query='mutation($s:String!,$e:String!,$i:ServiceInstanceUpdateInput!){serviceInstanceUpdate(serviceId:$s,environmentId:$e,input:$i)}'
subprocess.run(['railway','api',query,'--variables',json.dumps({'s':services['sdk'],'e':env,'i':{'dockerfilePath':'sdk/Dockerfile','restartPolicyType':'NEVER','rootDirectory':'/'}})],cwd=work,check=True)
dsn='http://'+fixture['public_key']+'@gateway.railway.internal:8080/'+str(fixture['project_id'])
subprocess.run(['railway','variable','set','--service','sdk','--skip-deploys','SENTRY_DSN='+dsn,'TEST_MARKER=bounty-cold4-e2e'],cwd=work,check=True,capture_output=True)
subprocess.run(['railway','up','--project',s['id'],'--environment','production','--service','sdk','--detach','--path-as-root',str(root)],cwd=work,check=True)
print('Cold fixture created:',fixture['org'],fixture['project_id'])
