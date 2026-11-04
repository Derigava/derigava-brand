"""Derigava: release files in dist/ (SHA256SUMS.txt and derigava-logos.zip).

Files listed in PRIVATE stay on disk and out of git. Only their hashes are
published, in «00 Основа/references/PRIVATE-HASHES.txt».
Check a clone with:  sha256sum -c SHA256SUMS.txt
"""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist'
SKIP_DIRS = {'.git', '.claude', '.remember', '.venv', '__pycache__', 'dist'}
PRIVATE = ['00 Основа/references/Примеры постов.txt']
PRIVATE_OUT = ROOT / '00 Основа' / 'references' / 'PRIVATE-HASHES.txt'
LOGOS = ROOT / '00 Основа' / 'logos'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


DIST.mkdir(exist_ok=True)

lines = []
for rel in PRIVATE:
    path = ROOT / rel
    if path.exists():
        lines.append(f'{sha256(path)}  {Path(rel).name}')
if lines:
    # Without the private file on disk (a fresh clone) the published hashes are left as they are.
    PRIVATE_OUT.write_text('SHA-256 текстов, которые хранятся только у меня.\n\n' + '\n'.join(lines) + '\n', encoding='utf-8', newline='\n')

entries = []
for path in ROOT.rglob('*'):
    rel = path.relative_to(ROOT)
    if not path.is_file() or SKIP_DIRS & set(rel.parts) or rel.as_posix() in PRIVATE:
        continue
    entries.append((rel.as_posix(), sha256(path)))
entries.sort()
(DIST / 'SHA256SUMS.txt').write_text(''.join(f'{digest}  ./{name}\n' for name, digest in entries), encoding='utf-8', newline='\n')

with zipfile.ZipFile(DIST / 'derigava-logos.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(LOGOS.iterdir()):
        archive.write(path, f'derigava-logos/{path.name}')

print(f'dist/SHA256SUMS.txt: {len(entries)} files; private hashes: {len(lines)}; logos in zip: {len(list(LOGOS.iterdir()))}')
