#!/usr/bin/env python3
"""Build review-only Momo resize/edge pass and Shellhost exact speck removal."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';BASE='scene_spot_candidates';SHELL_BOX=(168,418,177,426)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frame(base,f):
 x,y,w,h=f['region']
 with Image.open(base/f'atlas_{f["atlas"]:03}.png') as im:return im.convert('RGBA').crop((x,y,x+w,y+h))
def main():
 cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for n in ('momo','shellhost'):
  if (A/'revision_candidates'/n).exists():raise FileExistsError(n)
 for n in ('momo','shellhost'):
  base=A/BASE/n;old=json.loads((base/'candidate.json').read_text());e=cat[n];assert sha(ROOT/e['source'])==old['source_sha256']==e['source_sha256'];out=A/'revision_candidates'/n;out.mkdir(parents=True)
  if n=='momo':
   display=[round(v*1.15) for v in old['display_size']]; old_high=Image.open(base/'frame_000.png');prev_detail=list(old_high.size);old_high.close(); detail=[round(x*1.15*1.2) for x in prev_detail];aw,ah=detail;assert display==[506,506] and detail==[729,729]
  else:display=old['display_size'];aw,ah=display;template=np.array(frame(base,old['frames'][35]).crop(SHELL_BOX)); assert int((template[:,:,3]>0).sum())==20
  cols=2048//aw;rows=2048//ah;cap=cols*rows;page=-1;atlas=None;frames=[];counts=[];matched=[]
  for i,oldf in enumerate(old['frames']):
   if n=='momo':
    with Image.open(base/f'frame_{i:03d}.png') as im:
     pre=im.convert('RGBa').resize((aw,ah),Image.Resampling.LANCZOS); img=Image.blend(pre,pre.filter(ImageFilter.GaussianBlur(0.7)),0.10).convert('RGBA')
    counts.append(0)
   else:
    raw=np.array(frame(base,oldf));x0,y0,x1,y1=SHELL_BOX;match=np.array_equal(raw[y0:y1,x0:x1],template);mask=np.zeros((ah,aw),bool)
    if match:mask[y0:y1,x0:x1]=raw[y0:y1,x0:x1,3]>0
    counts.append(int(mask.sum()));matched.append(match);raw[mask]=0;img=Image.fromarray(raw)
   p,slot=divmod(i,cap)
   if p!=page:
    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
    page=p;count=min(cap,len(old['frames'])-page*cap);atlas=Image.new('RGBA',(min(cols,count)*aw,((count+cols-1)//cols)*ah))
   x,y=(slot%cols)*aw,(slot//cols)*ah;atlas.paste(img,(x,y));frames.append({'atlas':p,'region':[x,y,aw,ah],'duration_ms':oldf['duration_ms'],'source_index':oldf.get('source_index',i)})
   high=img if n=='momo' else img.convert('RGBa').resize((round(aw*1.2),round(ah*1.2)),Image.Resampling.LANCZOS).convert('RGBA');high.save(out/f'frame_{i:03d}.png',compress_level=3)
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
  meta={'id':n,'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':BASE,'base_metadata_sha256':sha(base/'candidate.json'),'base_atlas_sha256':{p.name:sha(p) for p in sorted(base.glob('atlas_*.png'))},'base_detail_sha256':{p.name:sha(p) for p in sorted(base.glob('frame_*.png'))} if n=='momo' else {},'art_source':'existing','frame_count':len(frames),'frames':frames,'loop':old['loop'],'display_size':display,'frame_size':[aw,ah],'anchor_display':[display[0]/2,display[1]],'anchor_frame':[aw/2,ah],'display_scale':[display[0]/aw,display[1]/ah],'removed_per_frame':counts,'status':'candidate_unreviewed'}
  if n=='momo':meta.update({'previous_display_size':old['display_size'],'previous_frame_detail_size':prev_detail,'display_growth':1.15,'pixel_density_growth':1.2,'edge_blend':0.1,'edge_blur_radius':0.7,'method':'Upsample previous 528px preview to 729px with premultiplied Lanczos, then 10% blend with Gaussian blur 0.7px; display 506px, keeping normalized bottom-center anchor.','limitations':'10% is a filter blend, not a measured increase in visual smoothness; interpolation cannot reconstruct missing details. Scaling applies to effects too; 729px atlases consume more texture memory and need performance testing.'})
  else:meta.update({'speck_box':list(SHELL_BOX),'template_source_frame_zero_based':35,'template_matches':matched,'method':'Remove opaque pixels in the 9x8 patch only in frames whose entire RGBA patch exactly equals source frame index 35; all other pixels unchanged.','limitations':'A repeated identical foreground pixel would also be removed, though the patch appears isolated in the review; compare in motion.'})
  (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(n,'frames',len(frames),'display',display,'atlas frame',(aw,ah),'removed',sum(counts), 'matched',[i+1 for i,x in enumerate(matched) if x],flush=True)
if __name__=='__main__':main()
