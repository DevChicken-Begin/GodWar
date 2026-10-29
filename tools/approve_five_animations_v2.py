#!/usr/bin/env python3
"""Record the user's approval of five additions without altering the original snapshot."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=A/'characters/approved-animations-20261029.json';out=A/'characters/approved-animations-20261029-v2.json';pending=A/'characters/provisional-animations-five-20261029.json';targetpath=A/'characters/height-targets.json'
if out.exists():raise FileExistsError(out)
base=read(old);pending_data=read(pending);targets=read(targetpath);entries={e['id']:e for e in targets['assets']};heights={'Mythos':80,'Tracker':85,'Epicti':80,'Nemotront':80,'Kanhosst':90};assert {e['id'] for e in pending_data['assets']}==set(heights)
for n,h in heights.items():
 p=A/'measured_atlas_pilots'/n/'candidate.json';m=read(p);assert m['target_height_px']==entries[n]['target_height_px']==h and m['source_sha256']==entries[n]['source_sha256']==sha(ROOT/m['source']);assert abs(m['display_scale']*m['reference_height_px']-h)<1e-8
for n in heights:
 p=A/'measured_atlas_pilots'/n/'candidate.json';m=read(p);m['size_target_approval']='user_approved_20261029_v2';entries[n]['size_target_approval']=m['size_target_approval'];write(p,m)
write(targetpath,targets);approved=[]
for n in heights:
 folder=A/'measured_atlas_pilots'/n;p=folder/'candidate.json';m=read(p);approved.append({'id':n,'default_profile':n,'profiles':[{'id':n,'candidate':str(p.relative_to(ROOT)),'candidate_sha256':sha(p),'atlas_sha256':{str(f.relative_to(ROOT)):sha(f) for f in sorted(folder.glob('atlas_*.png'))},'frame_count':len(m['frames']),'target_height_px':heights[n]}]})
assert not set(heights)&{x['id'] for x in base['assets']};assets=sorted(base['assets']+approved,key=lambda x:x['id'].lower());write(out,{'version':2,'approval':'user_approved_current_animations','approval_date':'2026-10-29','previous_snapshot':str(old.relative_to(ROOT)),'previous_snapshot_sha256':sha(old),'scope':'Previous approved animations plus five approved new characters; technical visual QA limitations remain.','assets':assets});write(pending,{'status':'promoted_to_approved_v2','assets':[],'promoted_ids':list(heights)});print('Approved v2:',len(assets),'assets;',len(approved),'new characters')
