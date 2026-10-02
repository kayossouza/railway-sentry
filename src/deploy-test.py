"""Private throwaway deployment helper. Refuses every other project name/ID."""
import json
import pathlib
import secrets
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
PROJECT = 'ec4ac01c-64d8-4713-aeb5-c9f6a22f8369'
ENVIRONMENT = '19cf537f-a2d9-4813-8bda-0cd1b1db5a9c'


def run(*args, secret=False):
    result = subprocess.run(['railway', *args], text=True, capture_output=True, cwd=ROOT)
    if result.returncode:
        # Variable commands may contain secrets; do not echo arguments.
        raise RuntimeError(result.stderr if not secret else result.stderr.splitlines()[0])
    return result.stdout


status = json.loads(run('status', '--json'))
if status['id'] != PROJECT or status['name'] != 'bounty-test-sentry-1':
    sys.exit('Refusing non-throwaway project')
services = json.loads((ROOT / 'services.json').read_text())
ids = {item['node']['name']:item['node']['id'] for item in status['services']['edges']}
for name in services:
    if name not in ids:
        print('create', name, flush=True)
        ids[name] = json.loads(run('add', '--service', name, '--json'))['id']
(ROOT / 'evidence/service-ids.json').write_text(json.dumps(ids, indent=2) + '\n')
domain = json.loads(run('domain', '--service', ids['gateway'], '--port', '8080', '--json'))
(ROOT / 'evidence/domain.json').write_text(json.dumps(domain, indent=2) + '\n')
# Resolve only generated secrets locally; Railway resolves cross-service references.
authority = {}
for name in services:
    data=json.loads((ROOT/name/'variables.json').read_text())
    for key,value in data.items():
        if value.startswith('${{secret('):
            authority[(name,key)] = secrets.token_hex(int(value.split('(')[1].split(')')[0])//2)
node=json.loads((ROOT.parent/'.node-credentials.json').read_text())
file=json.loads((ROOT.parent/'.file-credentials.json').read_text())
buckets={'Nodestore':node,'Filestore':file}
bkeys={'ENDPOINT':'endpoint','REGION':'region','BUCKET':'bucketName','ACCESS_KEY_ID':'accessKeyId','SECRET_ACCESS_KEY':'secretAccessKey'}
for name in ['postgres','valkey','clickhouse','gateway','web','kafka','memcached','symbolicator','taskbroker','relay','snuba-api','snuba-consumers','sentry-consumers','sentry-tasks']:
    meta = services[name]
    print('configure', name, flush=True)
    data=json.loads((ROOT/name/'variables.json').read_text())
    for key,value in list(data.items()):
        if (name,key) in authority:
            data[key]=authority[(name,key)]
        elif value.startswith('${{Nodestore.') or value.startswith('${{Filestore.'):
            service,variable=value[3:-2].split('.')
            data[key]=buckets[service][bkeys[variable]]
    if data:
        run('variable','set','--project',PROJECT,'--environment',ENVIRONMENT,'--service',ids[name],'--skip-deploys',*[k+'='+v for k,v in data.items()], secret=True)
    query='mutation($s:String!,$e:String!,$i:ServiceInstanceUpdateInput!){serviceInstanceUpdate(serviceId:$s,environmentId:$e,input:$i)}'
    run('api',query,'--variables',json.dumps({'s':ids[name],'e':ENVIRONMENT,'i':dict(json.loads((ROOT/name/'railway.json').read_text())['deploy'], dockerfilePath=name+'/Dockerfile', rootDirectory='/')}))
    if meta['volume']:
        run('volume','--project',PROJECT,'--environment',ENVIRONMENT,'--service',ids[name],'add','--mount-path',meta['volume'],'--json')
for name in services:
    print('upload', name, flush=True)
    result=run('up','--project',PROJECT,'--environment',ENVIRONMENT,'--service',ids[name],'--detach','--path-as-root',str(ROOT))
    (ROOT/'evidence'/f'upload-{name}.txt').write_text(result)
print('uploaded all services',flush=True)
