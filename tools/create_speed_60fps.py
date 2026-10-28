#!/usr/bin/env python3
"""Create non-destructive 60 Hz timelines from existing artwork."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; TICK=1000/60
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cat={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for name in ('firer','conden'):
  if (A/'speed_60fps_candidates'/name).exists(): raise FileExistsError(name)
 for name in ('firer','conden'):
  e=cat[name]; base=A/'speed_oct28_candidates'/name; m=json.loads((base/'candidate.json').read_text()); assert sha(ROOT/e['source'])==m['source_sha256']; frames=[]; cumulative=0; prev=0
  if name=='firer':
   for f in e['frames']:
    cumulative+=f['duration_ms']/3/TICK; end=round(cumulative); ticks=end-prev; assert ticks>=1; prev=end
    frames.append({**f,'duration_ticks':ticks,'duration_ms':ticks*TICK})
   image={'image_variant':'fine_candidates'}
  else:
   for i,src in enumerate(e['frames']):
    cumulative+=src['duration_ms']/TICK; end=round(cumulative); ticks=end-prev;prev=end
    group=[f for f in m['frames'] if f['source_index']==i]; arrows=[f for f in group if f.get('speed_insert')]; poses=[f for f in group if not f.get('speed_insert')]; assert len(poses)==1 and ticks>len(arrows)
    for f in arrows: frames.append({**f,'duration_ticks':1,'duration_ms':TICK})
    frames.append({**poses[0],'duration_ticks':ticks-len(arrows),'duration_ms':(ticks-len(arrows))*TICK})
   image={'frame_files':True}
  result={'id':name,'source':e['source'],'source_sha256':e['source_sha256'],'art_source':'existing','base_candidate':'speed_oct28_candidates','base_metadata_sha256':sha(base/'candidate.json'),'fps':60,'frame_count':len(frames),'frames':frames,'display_size':m['display_size'],**image,'status':'candidate_unreviewed','method':'Use cumulative rounding to 60 Hz display ticks; firer aims for source duration / 3; conden allocates one tick to each of nine prior arrow positions and retains approximately the source pose timing.','limitations':'A 60 Hz timeline does not guarantee display refresh or avoid dropped frames. Firer is approximately 3x; conden arrow is now visible for about 150ms and is slower than the previous 6.3ms version.'}
  out=A/'speed_60fps_candidates'/name;out.mkdir(parents=True); (out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  print(name,'frames',len(frames),'ticks',sum(f['duration_ticks'] for f in frames),'ms',round(sum(f['duration_ms'] for f in frames),3))
if __name__=='__main__':main()
