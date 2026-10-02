"""Read-only checks of the deployable contract, distinct from live acceptance."""
import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
inventory = json.loads((root / 'services.json').read_text())
pins = json.loads((root / 'images.lock.json').read_text())
known = set(inventory) | {'Nodestore', 'Filestore'}
for name, metadata in inventory.items():
    config = json.loads((root / name / 'railway.json').read_text())
    assert config['build']['dockerfilePath'] == name + '/Dockerfile'
    assert config['deploy']['numReplicas'] == 1
    assert config['deploy']['overlapSeconds'] == 0
    variables = json.loads((root / name / 'variables.json').read_text())
    for value in variables.values():
        for reference in re.findall(r'\$\{\{([^}]+)\}\}', value):
            assert reference.startswith('secret(') or reference.split('.')[0] in known, reference
    for line in (root / name / 'Dockerfile').read_text().splitlines():
        if line.startswith('FROM '):
            image = line.split()[1]
            tag, digest = image.split('@')
            assert pins[tag] == digest, image
    print(name, 'contract and immutable image pins OK')

for path in (root / 'upstream').glob('*'):
    original = root.parent / 'repos/upstream' / {
        'sentry.conf.py': 'sentry/sentry.conf.example.py',
        'config.yml': 'sentry/config.example.yml',
        'nginx.conf': 'nginx.conf',
        'clickhouse.xml': 'clickhouse/config.xml',
        'symbolicator.yml': 'symbolicator/config.example.yml',
        'taskbroker.yml': 'taskbroker/config.yml',
    }.get(path.name, path.name)
    if original.is_file() and path.name != 'nodestore-LICENSE.md':
        assert path.read_bytes() == original.read_bytes(), path
        print('Unmodified upstream:', path.name, hashlib.sha256(path.read_bytes()).hexdigest())

sentry = json.loads((root / 'sentry-consumers/commands.json').read_text())
snuba = json.loads((root / 'snuba-consumers/commands.json').read_text())
assert any('ingest-events' in command for command in sentry)
assert any('ingest-transactions' in command for command in sentry)
assert any('process-spans' in command for command in sentry)
assert any('eap_items' in command and 'rust-consumer' in command for command in snuba)
print('Errors, transactions, spans and EAP storage pipelines present')
