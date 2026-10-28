#!/usr/bin/env python3
"""Create review-only 130% detail experiments at the same viewer canvas size."""
import hashlib,json,os,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from build_fine_batch import scale2
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES='artemis nox overight powerdame wuchen ziggist scorpit skyles snowpie tigerknight azza dracian dragonmout mortafi'.split();REPORT=ROOT/'docs/fine-batch/detail130.json'
def main():
 catalog={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']};audit={e['id']:e for e in json.loads((ROOT/'docs/fine-batch/audit.json').read_text())['results']};result=[]
 if REPORT.exists():raise FileExistsError(REPORT)
 for name in NAMES:
  if (A/'detail_130_candidates'/name).exists() or (A/'review'/name/'detail_130_frames').exists():raise FileExistsError(name)
 for name in NAMES:
  e=catalog[name];src=ROOT/e['source'];base_name='fine_candidates' if (A/'fine_candidates'/name/'candidate.json').exists() else audit[name]['base_candidate'];base=A/base_name/name;meta=json.loads((base/'candidate.json').read_text());assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256']==meta['source_sha256'];out=A/'detail_130_candidates'/name;frames=A/'review'/name/'detail_130_frames';out.mkdir(parents=True);frames.mkdir(parents=True);page=-1;prior=atlas=None;details=[];counts=[]
  try:
   for i,f in enumerate(e['frames']):
    if page!=f['atlas']:
     if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
     page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
    x,y,w,h=f['region'];view=np.array(prior.crop((x,y,x+w,y+h)).convert('RGBA'))
    if base_name=='fine_candidates':
     with Image.open(A/'review'/name/'fine_frames'/f'frame_{i:03d}.png') as im:p=np.array(im.convert('RGBA'))
    else:p=view
    _,q=scale2(p,1);oldh,oldw=p.shape[:2];target=(round(oldw*1.3),round(oldh*1.3));assert target[0]>oldw and target[1]>oldh
    high=Image.fromarray(q).resize(target,Image.Resampling.NEAREST);high.save(frames/f'frame_{i:03d}.png');preview=high.resize((w,h),Image.Resampling.NEAREST);arr=np.array(preview);counts.append(int(np.any(arr!=view,axis=2).sum()));atlas.paste(preview,(x,y));details.append({'old':[oldw,oldh],'new':list(target)})
   if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  except BaseException:
   if prior is not None:prior.close()
   shutil.rmtree(out,ignore_errors=True);shutil.rmtree(frames,ignore_errors=True);raise
  hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(base.glob('atlas_*.png'))};m={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':base_name,'base_atlas_sha256':hashes,'art_source':'existing','frame_count':e['frame_count'],'frames':e['frames'],'detail_sizes':details,'viewer_canvas':e['size'],'changed_pixels_per_frame':counts,'status':'candidate_unreviewed','method':'Scale2x on current detail grid then nearest-resample to 130% per axis; nearest preview at original canvas. When a prior fine candidate exists its logical frames are used, otherwise current canvas pixels are the starting grid.','limitations':'An interpolated variant does not create missing source detail; can alter edges or VFX, introduce flicker or uneven widths and cannot guarantee improvement. Earlier background defects are inherited. Compare each frame.'}
  (out/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');result.append({'id':name,'status':'candidate_unreviewed','base_candidate':base_name,'frames':e['frame_count'],'detail':details[0],'changed_preview_pixels':sum(counts)});REPORT.write_text(json.dumps({'version':1,'results':result},ensure_ascii=False,indent=2)+'\n');print(name,base_name,e['frame_count'],details[0],flush=True)
if __name__=='__main__':main()
