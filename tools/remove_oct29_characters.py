#!/usr/bin/env python3
"""Remove five explicitly retired character assets and live catalog entries."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
NAMES = {'knigblack', 'monsterdead', 'newwomen', 'firer', 'kapicon'}


def update(path, key, identify):
    data = json.loads(path.read_text(encoding='utf-8'))
    before = len(data[key])
    data[key] = [item for item in data[key] if identify(item) not in NAMES]
    assert 0 <= before - len(data[key]) <= len(NAMES), (path, before - len(data[key]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    for name in sorted(NAMES):
        source = A / 'vfx' / f'{name}.gif'
        if not source.is_file():
            raise FileNotFoundError(source)
    update(A / 'extracted/catalog.json', 'assets', lambda x: x['id'])
    update(A / 'characters/roster.json', 'entries', lambda x: x['source_id'])
    update(A / 'review/inventory.json', 'sources', lambda x: Path(x['source']).stem)
    update(A / 'review/background-review-status.json', 'sources', lambda x: x['id'])
    update(A / 'review/background-audit.json', 'sources', lambda x: x['id'])
    removed_path = A / 'characters/removed.json'
    removed = json.loads(removed_path.read_text(encoding='utf-8'))
    removed['ids'] = list(dict.fromkeys([*removed['ids'], *sorted(NAMES)]))
    removed_path.write_text(json.dumps(removed, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    index = A / 'extracted/index.html'
    html = index.read_text(encoding='utf-8')
    for name in NAMES:
        html, count = re.subn(rf'^<article><h2>{name}</h2>.*?</article>\n?', '', html, flags=re.MULTILINE)
        assert count == 1, (name, count)
    index.write_text(html, encoding='utf-8')
    for name in sorted(NAMES):
        source = A / 'vfx' / f'{name}.gif'
        source.unlink()
        print('removed', source.relative_to(ROOT))
        for directory in A.iterdir():
            target = directory / name
            if target.is_dir():
                shutil.rmtree(target)
                print('removed', target.relative_to(ROOT))


if __name__ == '__main__':
    main()
