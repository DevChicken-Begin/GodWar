#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';TICK=1000/60
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=next(e for e in json.loads((A/'extracted/catalog.json').read_text())['assets'] if e['id']=='firer');base=A/'fine_candidates/firer';meta=json.loads((base/'candidate.json').read_text());assert sha(ROOT/e['source'])==e['source_sha256']==meta['source_sha256']
out=A/'tune_60fps_candidates/firer'
if out.exists():raise FileExistsError(out)
frames=[];target=0;previous=0
for f in e['frames']:
 target+=f['duration_ms']/2/TICK;end=round(target);ticks=end-previous;previous=end;assert ticks>0
 frames.append({**f,'duration_ticks':ticks,'duration_ms':ticks*TICK})
result={'id':'firer','source':e['source'],'source_sha256':e['source_sha256'],'art_source':'existing','base_candidate':'fine_candidates','base_metadata_sha256':sha(base/'candidate.json'),'base_atlas_sha256':{p.name:sha(p) for p in sorted(base.glob('atlas_*.png'))},'image_variant':'fine_candidates','display_size':e['size'],'frame_count':len(frames),'frames':frames,'fps':60,'target_speed_multiplier':2,'method':'Divide original duration by 2, round cumulative time to nearest 60Hz tick.','status':'candidate_unreviewed','limitations':'Actual browser and device frame rate is not guaranteed.'}
out.mkdir(parents=True);(out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('firer',len(frames),'frames',round(sum(x['duration_ms'] for x in frames),3),'ms')
