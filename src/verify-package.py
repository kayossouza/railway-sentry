"""Verify the delivered file inventory, evidence parts, line limit and cleanup."""
import hashlib
import json
import pathlib
import sys
from evidence_files import read

ROOT = pathlib.Path(__file__).resolve().parent
EXCLUDED = {'PACKAGE.sha256', 'evidence/package-verification.txt'}


def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not {'node_modules', '__pycache__', 'integrity'} & set(p.relative_to(ROOT).parts)
                  and str(p.relative_to(ROOT)) not in EXCLUDED)


def inventory():
    return ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  '
                   + str(p.relative_to(ROOT)) + '\n' for p in files())


if '--write' in sys.argv:
    target = ROOT / 'integrity'
    target.mkdir(exist_ok=True)
    for old in target.glob('*.sha256'):
        old.unlink()
    lines = inventory().splitlines(keepends=True)
    for index, offset in enumerate(range(0, len(lines), 200)):
        (target / f'{index:04d}.sha256').write_text(''.join(lines[offset:offset + 200]))
    (ROOT / 'PACKAGE.sha256').write_text(hashlib.sha256(''.join(lines).encode()).hexdigest()
                                       + '  sorted-file-inventory\n')

expected = ''.join(p.read_text() for p in sorted((ROOT / 'integrity').glob('*.sha256')))
assert inventory() == expected, 'File inventory/hash mismatch'
assert hashlib.sha256(expected.encode()).hexdigest() == (ROOT / 'PACKAGE.sha256').read_text().split()[0]
count = 0
for p in files():
    if p.is_relative_to(ROOT / 'evidence') or p.name == 'package-lock.json':
        read(p)
    try:
        lines = len(p.read_text().splitlines())
    except UnicodeError:
        continue
    if lines > 400:
        assert p == ROOT / 'upstream/sentry.conf.py', p
        assert p.read_bytes() == (ROOT.parent / 'repos/upstream/sentry/sentry.conf.example.py').read_bytes()
    count += 1
projects = json.loads(read(ROOT / 'evidence/cleanup-railway-list.json'))
assert not any(p['name'].startswith('bounty-test-sentry-') for p in projects)
assert not (ROOT / '.railway/secrets.json').exists()
print('PASS: file hashes, split evidence, authored-file line limit, no packaged secrets, cleanup proof')
print('Verified text/data files:', count)
print('Package SHA256:', hashlib.sha256(expected.encode()).hexdigest())
