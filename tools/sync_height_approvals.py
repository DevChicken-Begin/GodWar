#!/usr/bin/env python3
"""Record approved height targets on every preview without changing atlas pixels."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/'Asset/Character'
targets = {e['id']:e for e in json.loads((A/'characters/height-targets.json').read_text())['assets']}
planned = []
for path in sorted((A/'measured_atlas_pilots').glob('*/candidate.json')):
    meta = json.loads(path.read_text())
    name = path.parent.name
    source_id = {'crapit_main':'crapit','crapit_secondary':'crapit',
                 'moxie_repaired':'moxie','conden_tuned':'conden'}.get(name,name)
    entry = targets[source_id]
    height = 40 if name == 'crapit_secondary' else entry['target_height_px']
    assert meta['target_height_px'] == height, (name,meta['target_height_px'],height)
    assert abs(meta['display_scale'] * meta['reference_height_px'] - height) < 1e-7
    meta['size_target_approval'] = entry['size_target_approval']
    planned.append((path,meta))
for path,meta in planned:
    tmp=path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)
print('Recorded user size approval for',len(planned),'atlas sets')
