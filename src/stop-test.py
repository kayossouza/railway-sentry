import concurrent.futures,json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parent
project='ec4ac01c-64d8-4713-aeb5-c9f6a22f8369'
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=root))
assert s['id']==project and s['name']=='bounty-test-sentry-1'
names=list(json.loads((root/'services.json').read_text()))
def stop(name):
 r=subprocess.run(['railway','down','--project',project,'--environment','production','--service',name,'--yes'],cwd=root,capture_output=True,text=True)
 print(name,r.returncode,r.stdout,r.stderr,flush=True)
 assert r.returncode==0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(stop,names))
