"""Derigava v5: writes SHA256SUMS.txt for everything the repository publishes.

Files listed in PRIVATE stay on the author's disk and out of git. Only their
hashes are published, in «00 Основа/references/PRIVATE-HASHES.txt»: the hash
fixes the date a text existed without revealing the text.
Check a clone with:  sha256sum -c SHA256SUMS.txt
"""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {'.git', '.remember', '__pycache__'}
PRIVATE = ['00 Основа/references/Примеры постов.txt']
OUT = ROOT / 'SHA256SUMS.txt'
PRIVATE_OUT = ROOT / '00 Основа' / 'references' / 'PRIVATE-HASHES.txt'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


lines = []
for rel in PRIVATE:
    path = ROOT / rel
    if path.exists():
        lines.append(f'{sha256(path)}  {Path(rel).name}')
if lines:
    # Without the private file on disk (a fresh clone) the published hashes are left as they are.
    PRIVATE_OUT.write_text(
        'SHA-256 файлов, которые автор хранит у себя и не публикует.\n'
        'Совпадение хэша с файлом показывает, что этот текст существовал на дату коммита.\n\n'
        + '\n'.join(lines) + '\n',
        encoding='utf-8', newline='\n',
    )

entries = []
for path in ROOT.rglob('*'):
    rel = path.relative_to(ROOT)
    if not path.is_file() or SKIP_DIRS & set(rel.parts) or path == OUT or rel.as_posix() in PRIVATE:
        continue
    entries.append((rel.as_posix(), sha256(path)))
entries.sort()
OUT.write_text(''.join(f'{digest}  ./{name}\n' for name, digest in entries), encoding='utf-8', newline='\n')
print(f'SHA256SUMS.txt: {len(entries)} files; private hashes: {len(lines)}')
