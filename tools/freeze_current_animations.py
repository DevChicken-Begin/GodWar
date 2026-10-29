#!/usr/bin/env python3
"""Record user-approved current viewer selections with file hashes; never overwrite a snapshot."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character';out=A/'characters/approved-animations-20261029.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if out.exists():raise FileExistsError(out)
cat=read(A/'extracted/catalog.json');removed=set(read(A/'characters/removed.json')['ids']);assets=[x for x in cat['assets'] if x['id'] not in removed]+read(A/'extracted/split-catalog.json')['assets']+read(A/'extracted/composite-catalog.json')['assets'];assert len({x['id'] for x in assets})==len(assets)
targets={x['id']:x for x in read(A/'characters/height-targets.json')['assets']};entries=[]
for asset in assets:
 name=asset['id']; ids=['crapit_main','crapit_secondary'] if name=='crapit' else ['moxie_repaired'] if name=='moxie' else [name];profiles=[]
 for id in ids:
  folder=A/'measured_atlas_pilots'/id;p=folder/'candidate.json';meta=read(p);assert meta['source_sha256']==targets[name]['source_sha256']==sha(ROOT/meta['source']);assert len(meta['frames'])==meta['frame_count'];assert all((folder/('atlas_%03d.png'%f['atlas'])).is_file() for f in meta['frames']);profiles.append({'id':id,'candidate':str(p.relative_to(ROOT)),'candidate_sha256':sha(p),'atlas_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(folder.glob('atlas_*.png'))},'frame_count':len(meta['frames']),'target_height_px':targets[name]['parts'][1]['target_height_px'] if id=='crapit_secondary' else targets[name]['target_height_px']})
 entries.append({'id':name,'default_profile':ids[0],'profiles':profiles})
out.write_text(json.dumps({'version':1,'approval':'user_approved_current_animations','approval_date':'2026-10-29','scope':'Current viewer default measured animation per visible asset; crapit secondary is also retained as an approved part. Historical variants and GIF sources are retained for reference.','assets':entries},ensure_ascii=False,indent=2)+'\n');print(len(entries),'assets;',sum(len(x['profiles']) for x in entries),'profiles recorded')
