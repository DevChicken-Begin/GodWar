#!/usr/bin/env python3
"""Relocate references to hash-identical source GIFs; preserve old candidate metadata."""
from pathlib import Path
import hashlib,json,shutil
A=Path('Asset/Character');old=A/'archive/root_gif_provenance_metadata_20261030';old.mkdir(parents=True,exist_ok=False); roots={p.name:p for p in Path('.').glob('*.gif')};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); mapping={name:str(A/'vfx'/name) for name,p in roots.items() if (A/'vfx'/name).is_file() and sha(p)==sha(A/'vfx'/name)}
def fix(v):
 if isinstance(v,dict):return {k:fix(x) for k,x in v.items()}
 if isinstance(v,list):return [fix(x) for x in v]
 if isinstance(v,str):return mapping.get(v,v)
 return v
changed=[]
for p in (A/'measured_atlas_pilots').glob('*/candidate.json'):
 d=json.load(open(p));new=fix(d)
 if new!=d:
  dest=old/p.parent.name;dest.mkdir();shutil.copy2(p,dest/'candidate.json');p.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n');changed.append({'id':p.parent.name,'old_candidate':str(dest/'candidate.json'),'old_sha256':sha(dest/'candidate.json'),'new_sha256':sha(p)})
for p in [A/'review/twenty-import-20261030/inventory.json',A/'review/six-import-20261030/report.json']:
 d=json.load(open(p));p.write_text(json.dumps(fix(d),ensure_ascii=False,indent=2)+'\n')
manifest=A/'characters/approved-animations-20261030-v5.json';d=json.load(open(manifest));by={x['id']:x for x in changed}
for asset in d['assets']:
 for profile in asset['profiles']:
  if profile['id'] in by:profile['candidate_sha256']=by[profile['id']]['new_sha256']
manifest.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');(old/'mapping.json').write_text(json.dumps({'root_to_source':mapping,'candidate_metadata':changed,'note':'Earlier snapshots retain original candidate hashes; their former candidate metadata is archived here. Current v5 has normalized paths and hashes.'},ensure_ascii=False,indent=2)+'\n');print('normalized metadata',len(changed),'duplicate sources',len(mapping))
