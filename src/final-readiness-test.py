"""Show Gateway readiness failing closed on loss of either backend."""
import datetime,json,pathlib,subprocess,time,urllib.request,urllib.error
root=pathlib.Path(__file__).resolve().parent;work=root.parent/'test4'
project='f4ce2e9f-f8b2-4508-b440-d08d5b48baef'
base=json.loads((root/'evidence/cold4-domain.json').read_text())['domain']
records=[]
def state():
 s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=work))
 assert s['id']==project and s['name']=='bounty-test-sentry-4'
 return s
def probe(label,want_ready):
 deadline=time.monotonic()+300
 while True:
  try:
   r=urllib.request.urlopen(base+'/ready',timeout=10);code=r.status;body=r.read().decode()
  except urllib.error.HTTPError as e:code=e.code;body=e.read().decode()
  except OSError:code=0;body='transport unavailable'
  if (code==200)==want_ready:
   row={'label':label,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':code,'body':body}
   records.append(row);(root/'evidence/readiness4-drill.json').write_text(json.dumps(records,indent=2)+'\n');print(label,code,flush=True);return
  if time.monotonic()>deadline:raise RuntimeError(label+' readiness deadline')
  time.sleep(3)
probe('baseline',True)
for name in ['web','relay']:
 s=state();n=next(e['node'] for e in s['environments']['edges'][0]['node']['serviceInstances']['edges'] if e['node']['serviceName']==name)
 for d in n['activeDeployments']:
  subprocess.run(['railway','api','mutation($d:String!){deploymentRemove(id:$d)}','--var','d='+d['id']],cwd=work,check=True,capture_output=True)
 probe(name+' unavailable',False)
 r=subprocess.run(['railway','up','--project',project,'--environment','production','--service',name,'--detach','--path-as-root',str(root)],cwd=work,capture_output=True,text=True,check=True)
 (root/'evidence'/('readiness4-resume-'+name+'.txt')).write_text(r.stdout+r.stderr)
 probe(name+' restored',True)
