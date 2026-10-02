"""Restore all stopped disposable stores from the coordinated backup point."""
import json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parent
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
assert s['id']=='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369' and s['name']=='bounty-test-sentry-1'
v=json.loads((root/'evidence/volume-instances.json').read_text())['data']['project']
for edge in v['volumes']['edges']:
 node=edge['node'];instance=node['volumeInstances']['edges'][0]['node']
 query='query($v:String!){volumeInstanceBackupList(volumeInstanceId:$v){id name createdAt usedMB referencedMB}}'
 r=subprocess.run(['railway','api',query,'--var','v='+instance['id']],cwd=root,text=True,capture_output=True,check=True)
 (root/'evidence'/('backups-'+node['name']+'.json')).write_text(r.stdout)
 backups=json.loads(r.stdout)['data']['volumeInstanceBackupList']
 candidates=[b for b in backups if b['name']=='bounty-recovery-test']
 if not candidates:raise RuntimeError('Backup still pending: '+node['name'])
 backup=sorted(candidates,key=lambda b:b['createdAt'])[-1]
 query='mutation($v:String!,$b:String!){volumeInstanceBackupRestore(volumeInstanceId:$v,volumeInstanceBackupId:$b){workflowId}}'
 r=subprocess.run(['railway','api',query,'--var','v='+instance['id'],'--var','b='+backup['id']],cwd=root,text=True,capture_output=True)
 (root/'evidence'/('restore-'+node['name']+'.json')).write_text(r.stdout+r.stderr)
 print(node['name'],r.returncode,flush=True)
 assert r.returncode==0
