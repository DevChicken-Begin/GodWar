#!/usr/bin/env python3
"""Create a non-destructive playback-speed candidate for conden."""
import hashlib, json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 catalog={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for name in ('conden',):
  if (A/'speed_oct28_candidates'/name).exists(): raise FileExistsError(name)
 # Conden: preserve the previous nine arrow positions, shorten their interval 100x.
 name='conden'; e=catalog[name]; base=A/'detail_oct28_candidates'/name; old=json.loads((base/'candidate.json').read_text()); assert sha(ROOT/e['source'])==old['source_sha256']==e['source_sha256']
 out=A/'speed_oct28_candidates'/name;out.mkdir(parents=True); frames=[]; original=e['frames']; arrow_frames=[(i,f) for i,f in enumerate(old['frames']) if f.get('projectile_x') is not None]
 assert len(arrow_frames)==9
 for source_index,source in enumerate(original):
  relevant=[(i,f) for i,f in arrow_frames if f['source_index']==source_index]
  for i,f in relevant:
   frames.append({**f,'image_index':i,'image_variant':'detail_oct28_candidates','duration_ms':f['duration_ms']/100,'speed_insert':True})
  # Rebuild the background-only pose from the same base as the previous variant.
  if relevant:
   path=A/'batch_candidates'/name/f'atlas_{source["atlas"]:03d}.png'; x,y,w,h=source['region']
   with Image.open(path) as im: pose=im.convert('RGBA').crop((x,y,x+w,y+h))
   canvas=Image.new('RGBA',(960,720));canvas.paste(pose,(0,0));canvas=canvas.convert('RGBa').resize((1152,864),Image.Resampling.LANCZOS).convert('RGBA'); canvas.save(out/f'frame_{source_index:03d}.png',compress_level=3)
   frame={**source,'region':[0,0,960,720],'source_index':source_index,'image_index':source_index,'image_variant':'speed_oct28_candidates','duration_ms':source['duration_ms']-sum(f['duration_ms']/100 for _,f in relevant),'speed_insert':False}
  else:
   i,f=next((i,f) for i,f in enumerate(old['frames']) if f.get('source_index')==source_index)
   frame={**f,'image_index':i,'image_variant':'detail_oct28_candidates','speed_insert':False}
  frames.append(frame)
 assert abs(sum(f['duration_ms'] for f in frames)-sum(f['duration_ms'] for f in original))<1e-7
 meta={'id':name,'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'detail_oct28_candidates','base_metadata_sha256':sha(base/'candidate.json'),'base_frames_sha256':{p.name:sha(p) for p in sorted(base.glob('frame_*.png'))},'reconstructed_pose_atlas_sha256':{p.name:sha(p) for p in sorted((A/'batch_candidates'/name).glob('atlas_*.png'))},'art_source':'existing','frame_files':True,'frame_count':len(frames),'frames':frames,'display_size':[960,720],'speed_multiplier':100,'status':'candidate_unreviewed','method':'Reuse previous arrow positions; show each for 0.7 ms (100x faster). Restore the background-only pose for remaining duration so the source body timing is unchanged.','limitations':'The complete flight is shorter than a display refresh and may be invisible or appear to teleport; arrow and shaft are reconstructed.'}
 (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print('conden',len(frames),'frames; projectile durations', [f['duration_ms'] for f in frames if f.get('speed_insert')])
if __name__=='__main__':main()
