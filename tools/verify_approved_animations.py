#!/usr/bin/env python3
"""Detect changes to the user-approved animation snapshot."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(A/'characters/approved-animations-20261029-v2.json');excluded=set(read(A/'characters/removed.json')['ids']);visible={x['id'] for x in read(A/'extracted/catalog.json')['assets'] if x['id'] not in excluded}|{x['id'] for f in ['split-catalog.json','composite-catalog.json'] for x in read(A/'extracted'/f)['assets']}; entries=manifest['assets'];provisional={x['id'] for x in read(A/'characters/provisional-animations-five-20261029.json')['assets']};approved={x['id'] for x in entries};assert len(entries)==len(approved) and not approved & provisional and approved | provisional == visible
previous=ROOT/manifest['previous_snapshot'];assert sha(previous)==manifest['previous_snapshot_sha256'];current={entry['id']:entry for entry in entries};assert all(current.get(entry['id'])==entry for entry in read(previous)['assets'])
targets={x['id']:x for x in read(A/'characters/height-targets.json')['assets']};frames=pages=0
for entry in entries:
 assert entry['default_profile'] in [p['id'] for p in entry['profiles']]
 for p in entry['profiles']:
  candidate=ROOT/p['candidate'];assert sha(candidate)==p['candidate_sha256'],candidate; m=read(candidate);assert m['id']==p['id'] and len(m['frames'])==p['frame_count']==m['frame_count'];assert sha(ROOT/m['source'])==m['source_sha256']==targets[entry['id']]['source_sha256'];height=targets[entry['id']]['parts'][1]['target_height_px'] if p['id']=='crapit_secondary' else targets[entry['id']]['target_height_px'];assert height==p['target_height_px'];assert abs(m['reference_height_px']*m['display_scale']-height)<1e-7
  for file,digest in p['atlas_sha256'].items():assert sha(ROOT/file)==digest,file;pages+=1
  assert {f"{candidate.parent.relative_to(ROOT)}/atlas_{f['atlas']:03d}.png" for f in m['frames']} <= set(p['atlas_sha256']);frames+=len(m['frames'])
print(f'PASS: {len(entries)} assets, {sum(len(x["profiles"]) for x in entries)} profiles, {frames} frames, {pages} atlas pages')
