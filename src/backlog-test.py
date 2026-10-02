"""Controlled private SDK backlog experiment in disposable project 3 only."""
import json,pathlib,subprocess,datetime,shlex
root=pathlib.Path(__file__).resolve().parent;work=root.parent/'test2'
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=work))
assert s['id']=='91d7ec9f-de08-466d-aebf-d5c102a31ed1' and s['name']=='bounty-test-sentry-3'
def run(args,file):
 r=subprocess.run(['railway',*args],cwd=work,capture_output=True,text=True)
 (root/'evidence'/file).write_text(r.stdout+r.stderr)
 assert r.returncode==0,file
common=['--project',s['id'],'--environment','production']
for service in ['sentry-consumers','snuba-consumers']:
 run(['down',*common,'--service',service,'--yes'],'backlog-stop-'+service+'.txt')
run(['variable','set',*common,'--service','sdk','--skip-deploys','TEST_COUNT=20','TEST_MARKER=bounty-backlog-20261001'],'backlog-sdk-config.txt')
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
(root/'evidence/backlog-window.json').write_text(json.dumps({'since':start,'declared_errors':20,'declared_logs':20,'declared_root_spans':20,'declared_child_spans':20,'retention_days':7,'kafka_retention_hours':3},indent=2)+'\n')
run(['up',*common,'--service','sdk','--detach','--path-as-root',str(root)],'backlog-sdk-upload.txt')
print('Producer uploaded; consumers stopped',start)
