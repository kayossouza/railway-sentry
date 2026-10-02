"""Split long evidence/data without changing its bytes; verify on reconstruction."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def read(path):
    path = pathlib.Path(path)
    raw = path.read_bytes()
    try:
        pointer = json.loads(raw)
    except (ValueError, UnicodeError):
        return raw
    if not isinstance(pointer, dict) or 'evidence_parts' not in pointer:
        return raw
    manifest = json.loads((ROOT / pointer['evidence_parts']).read_text())
    assert manifest['sha256'] == pointer['sha256'], path
    blocks = []
    for part in manifest['parts']:
        block = (ROOT / part['path']).read_bytes()
        assert hashlib.sha256(block).hexdigest() == part['sha256'], part['path']
        blocks.append(block)
    raw = b''.join(blocks)
    assert hashlib.sha256(raw).hexdigest() == manifest['sha256'], path
    return raw


def pack(path):
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    if len(lines) <= 400:
        return False
    digest = hashlib.sha256(raw).hexdigest()
    folder = ROOT / 'evidence-parts' / digest
    folder.mkdir(parents=True, exist_ok=True)
    parts = []
    for index, offset in enumerate(range(0, len(lines), 300)):
        block = b''.join(lines[offset:offset + 300])
        target = folder / f'{index:04d}.part'
        target.write_bytes(block)
        parts.append({'path': str(target.relative_to(ROOT)),
                      'sha256': hashlib.sha256(block).hexdigest()})
    manifest = folder / 'manifest.json'
    manifest.write_text(json.dumps({'original': str(path.relative_to(ROOT)),
                                   'sha256': digest, 'parts': parts}, indent=2) + '\n')
    assert len(manifest.read_text().splitlines()) <= 400
    path.write_text(json.dumps({'evidence_parts': str(manifest.relative_to(ROOT)),
                               'sha256': digest,
                               'read': 'python3 evidence_files.py read ' + str(path.relative_to(ROOT))}, indent=2) + '\n')
    assert read(path) == raw
    return True


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'read':
        sys.stdout.buffer.write(read(ROOT / sys.argv[2]))
    elif command == 'pack':
        candidates = list((ROOT / 'evidence').rglob('*')) + [ROOT / 'package-lock.json']
        print('Split files:', sum(pack(p) for p in candidates if p.is_file()
                                  and p.suffix not in ('.png', '.pyc')))
    elif command == 'verify':
        pointers = []
        for p in list((ROOT / 'evidence').rglob('*')) + [ROOT / 'package-lock.json']:
            if p.is_file() and p.suffix not in ('.png', '.pyc'):
                read(p)
                pointers.append(p)
        print('Verified evidence/data files:', len(pointers))
    else:
        raise SystemExit('Use pack, verify, or read <path>')
