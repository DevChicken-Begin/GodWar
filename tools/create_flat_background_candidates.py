#!/usr/bin/env python3
"""Create review-only candidates for sources with measured uniform borders."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / 'Asset/Character/review/background-audit.json').read_text(encoding='utf-8'))
entries = [item for item in audit['sources'] if item['category'] == 'solid_border_candidate']


def run(item):
    target = ROOT / 'Asset/Character/candidates' / item['id']
    if target.exists():
        metadata = target / 'candidate.json'
        if not metadata.is_file():
            return item['id'], 'incomplete candidate directory; preserved for inspection', False
        existing = json.loads(metadata.read_text(encoding='utf-8'))
        if existing.get('source_sha256') != item['source_sha256']:
            return item['id'], 'candidate hash mismatch; preserved for inspection', False
        return item['id'], 'exists; preserved', True
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    result = subprocess.run([sys.executable, str(ROOT / 'tools/remove_flat_background_candidate.py'), item['id']], text=True, capture_output=True, env=env)
    return item['id'], (result.stdout.strip() or result.stderr.strip()), result.returncode == 0


def main():
    failed = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(run, entry) for entry in entries]
        for future in as_completed(futures):
            name, message, ok = future.result()
            print(f'{name}: {message}', flush=True)
            if not ok: failed.append(name)
    print(f'Finished {len(entries)} candidates; failed: {failed}', flush=True)
    if failed: sys.exit(1)

if __name__ == '__main__':
    main()
