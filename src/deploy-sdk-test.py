import json
import pathlib
import subprocess
import sys
root=pathlib.Path(__file__).resolve().parent
status=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
if status['id']!='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369' or status['name']!='bounty-test-sentry-1':sys.exit('Refusing non-throwaway project')
fixture=json.loads((root.parent/'.acceptance.json').read_text())
ids={s['node']['name']:s['node']['id'] for s in status['services']['edges']}
if 'sdk' not in ids:
    ids['sdk']=json.loads(subprocess.check_output(['railway','add','--service','sdk','--json'],cwd=root))['id']
key=fixture['public_key']
dsn='http://'+key+'@${{gateway.RAILWAY_SERVICE_NAME}}.railway.internal:8080/'+str(fixture['project_id'])
subprocess.run(['railway','variable','set','--service',ids['sdk'],'--skip-deploys','SENTRY_DSN='+dsn,'TEST_MARKER=bounty-sentry-e2e-20261001'],cwd=root,check=True,capture_output=True)
query='mutation($s:String!,$e:String!,$i:ServiceInstanceUpdateInput!){serviceInstanceUpdate(serviceId:$s,environmentId:$e,input:$i)}'
subprocess.run(['railway','api',query,'--variables',json.dumps({'s':ids['sdk'],'e':status['environments']['edges'][0]['node']['id'],'i':{'dockerfilePath':'sdk/Dockerfile','restartPolicyType':'NEVER'}})],cwd=root,check=True)
subprocess.run(['railway','up','--project',status['id'],'--environment','production','--service',ids['sdk'],'--detach','--path-as-root',str(root)],cwd=root,check=True)
print('SDK service deployed:',ids['sdk'])
