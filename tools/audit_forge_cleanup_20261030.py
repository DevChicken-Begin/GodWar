#!/usr/bin/env python3
"""Audit current Forge dependencies and plan removal of obsolete intermediate versions."""
import hashlib,json,sys
from pathlib import Path
A=Path('Asset/Character');names='Kungteng charmia combra cons cornra hecpoirt isis ison isorat kikontai maxoi omega ompan onaon oset osiris pandung samset thorn uopon'.split();candidates=['clips','repaired-clips','static-refined-clips','reported-spots-clips','repaired_frames','static_refined_frames','reported_spots_frames'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();plan=[];protected_count=0
for n in names:
 m=json.loads((A/'measured_atlas_pilots'/n/'candidate.json').read_text());src=Path(m['source']);assert src.is_file() and sha(src)==m['source_sha256'];base=Path(m['forge_folder']);clip=base/m['forge_current_clip'];data=json.loads(clip.read_text());assert len(data['frames'])==m['frame_count']==len(m['frames']);protected={clip.resolve()}
 for f in data['qa']['inputs']+data['qa']['outputs']:
  q=(clip.parent/f['path']).resolve();assert q.is_file() and sha(q)==f['sha256'], f'{n}: {q}';protected.add(q);protected_count+=1
 for sub in candidates:
  target=base/sub
  if not target.is_dir():continue
  files=[x for x in target.rglob('*') if x.is_file()]
  if any(x.resolve() in protected for x in files):continue
  for p in files:
   assert p.is_relative_to(base) and not p.is_symlink();plan.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'id':n,'current_clip':str(clip),'reason':'obsolete Forge iteration; current verified QA inputs/outputs and GIF/initial frames retained'})
out=Path(sys.argv[1]) if len(sys.argv)>1 else Path('docs/cleanup-20261030-forge-plan.json');out.write_text(json.dumps({'status':'planned','protected_files_checked':protected_count,'files':plan},ensure_ascii=False,indent=2)+'\n');print('verified current QA files',protected_count,'obsolete files',len(plan),'bytes',sum(e['bytes'] for e in plan))
