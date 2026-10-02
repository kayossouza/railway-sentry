"""Collect exact CLI time-series data for every throwaway service, no cost guesses."""
import concurrent.futures
import datetime
import json
import pathlib
import subprocess
import sys

root=pathlib.Path(__file__).resolve().parent
work=root if len(sys.argv)<4 else root.parent/sys.argv[3]
status=json.loads(subprocess.check_output(['railway','status','--json'],cwd=work))
authorized={'bounty-test-sentry-1':'ec4ac01c-64d8-4713-aeb5-c9f6a22f8369',
            'bounty-test-sentry-3':'91d7ec9f-de08-466d-aebf-d5c102a31ed1',
            'bounty-test-sentry-4':'f4ce2e9f-f8b2-4508-b440-d08d5b48baef'}
if authorized.get(status['name'])!=status['id']:
    sys.exit('Refusing non-throwaway project')
label=sys.argv[1]
since=sys.argv[2]
end=sys.argv[4] if len(sys.argv)>4 else datetime.datetime.now(datetime.timezone.utc).isoformat()
ids={e['node']['name']:e['node']['id'] for e in status['services']['edges']}
(root/'evidence'/f'{label}-service-ids.json').write_text(json.dumps(ids,indent=2)+'\n')

def measure(item):
    name,id=item
    args=['railway','metrics','--project',status['id'],'--environment','production','--service',id,'--since',since,'--until',end,'--raw','--json']
    result=subprocess.run(args,cwd=root,capture_output=True,text=True)
    path=root/'evidence'/f'{label}-{name}.json'
    path.write_text(result.stdout)
    (root/'evidence'/f'{label}-{name}-command.json').write_text(json.dumps({'command':args,'exit':result.returncode,'stderr':result.stderr},indent=2)+'\n')
    return name,result.returncode

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    print(list(pool.map(measure,ids.items())))
result=subprocess.run(['railway','usage','projects','--project',status['id'],'--workspace',status['workspaceId'],'--json'],cwd=root,capture_output=True,text=True)
(root/'evidence'/f'{label}-usage.json').write_text(result.stdout)
print('Usage exit:',result.returncode)
