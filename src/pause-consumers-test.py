"""Pause every active ingestion deployment, not merely the newest candidate."""
import json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parent;work=root.parent/'test2'
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=work))
assert s['id']=='91d7ec9f-de08-466d-aebf-d5c102a31ed1' and s['name']=='bounty-test-sentry-3'
(root/'evidence/backlog2-before-status.json').write_text(json.dumps(s,indent=2)+'\n')
for edge in s['environments']['edges'][0]['node']['serviceInstances']['edges']:
 n=edge['node']
 if n['serviceName'] not in ['sentry-consumers','snuba-consumers']:continue
 ids={d['id'] for d in n['activeDeployments']}
 if n['latestDeployment']:ids.add(n['latestDeployment']['id'])
 for id in ids:
  r=subprocess.run(['railway','api','mutation($d:String!){deploymentRemove(id:$d)}','--var','d='+id],cwd=work,capture_output=True,text=True)
  (root/'evidence'/f'backlog2-remove-{id}.json').write_text(r.stdout+r.stderr)
  assert r.returncode==0
  print('Removed',n['serviceName'],id,flush=True)
