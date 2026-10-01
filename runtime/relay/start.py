import json
import os
import pathlib
import urllib.parse
from storage import client
from relay_identity import identity as derive_identity
from wait import web_url, wait

root = pathlib.Path('/work/.relay')
root.mkdir(parents=True, exist_ok=True)
# JSON is valid YAML and safely quotes secret-bearing connection strings.
config = {
    'relay': {'upstream': web_url() + '/', 'host': '::', 'port': 3000},
    'processing': {'enabled': True, 'kafka_config': [
        {'name': 'bootstrap.servers', 'value': os.environ['KAFKA_BROKERS']},
        {'name': 'message.max.bytes', 'value': 50000000}],
        'redis': os.environ['REDIS_URL']},
    'logging': {'level': 'WARN'}, 'http': {'dns_cache': False},
}
(root / 'config.yml').write_text(json.dumps(config))
credentials = root / 'credentials.json'
credentials.write_text(json.dumps(derive_identity(os.environ['RELAY_KEY_SEED'])))
identity = json.loads(credentials.read_text())
os.chmod(credentials, 0o600)
client().put_object(Bucket=os.environ['NODE_BUCKET'], Key='relay/public.json',
                    Body=json.dumps({'public_key': identity['public_key'], 'id': identity['id']}).encode())
redis = urllib.parse.urlsplit(os.environ['REDIS_URL'])
wait([os.environ['KAFKA_BROKERS'], redis.hostname + ':' + str(redis.port or 6379)])
os.execv('/bin/relay', ['/bin/relay', '--config', str(root), 'run'])
