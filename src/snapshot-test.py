"""Consistent snapshots of stopped stores in the first disposable project."""
import json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parent
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
assert s['id']=='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369' and s['name']=='bounty-test-sentry-1'
v=json.loads((root/'evidence/volume-instances.json').read_text())['data']['project']
assert v['name']==s['name']
for edge in v['volumes']['edges']:
 node=edge['node'];instance=node['volumeInstances']['edges'][0]['node']
 args=['railway','api','mutation($v:String!){volumeInstanceBackupCreate(volumeInstanceId:$v,name:"bounty-recovery-test"){workflowId}}', '--var','v='+instance['id']]
 r=subprocess.run(args,cwd=root,text=True,capture_output=True)
 (root/'evidence'/('backup-'+node['name']+'.json')).write_text(r.stdout+r.stderr)
 print(node['name'],r.returncode,flush=True)
 assert r.returncode==0
