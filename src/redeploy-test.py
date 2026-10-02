"""Apply selected candidate changes only to the authorized throwaway project."""
import json
import pathlib
import subprocess
import sys

root=pathlib.Path(__file__).resolve().parent
status=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
if status['name'] != 'bounty-test-sentry-1' or status['id'] != 'ec4ac01c-64d8-4713-aeb5-c9f6a22f8369':
    sys.exit('Refusing non-throwaway project')
ids=json.loads((root/'evidence/service-ids.json').read_text())
env=status['environments']['edges'][0]['node']['id']
for name in sys.argv[1:]:
    data=json.loads((root/name/'railway.json').read_text())
    query='mutation($s:String!,$e:String!,$i:ServiceInstanceUpdateInput!){serviceInstanceUpdate(serviceId:$s,environmentId:$e,input:$i)}'
    subprocess.run(['railway','api',query,'--variables',json.dumps({'s':ids[name],'e':env,'i':dict(data['deploy'],dockerfilePath=name+'/Dockerfile')})],cwd=root,check=True)
    if name=='kafka':
        subprocess.run(['railway','variable','set','--service',ids[name],'--skip-deploys','KAFKA_LOG_DIRS=/var/lib/kafka/data/logs'],cwd=root,check=True)
    subprocess.run(['railway','up','--project',status['id'],'--environment',env,'--service',ids[name],'--detach','--path-as-root',str(root)],cwd=root,check=True)
