#!/usr/bin/env python3
"""Create reversible Scale2x candidates from verified source pixel grids."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';SPECS={'airpot':('logo_candidates',3),'amore':('batch_candidates',2),'aoda':('batch_candidates',6)}
def main():
 cat={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for name in SPECS:
  if (A/'fine_candidates'/name).exists() or (A/'review'/name/'fine_frames').exists():raise FileExistsError(name)
 for name,(base_name,period) in SPECS.items():
  e=cat[name];src=ROOT/e['source'];base=A/base_name/name;out=A/'fine_candidates'/name;logical=A/'review'/name/'fine_frames';meta=json.loads((base/'candidate.json').read_text());assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256']==meta['source_sha256'];out.mkdir(parents=True);logical.mkdir(parents=True);page=-1;prior=atlas=None;counts=[]
  for i,f in enumerate(e['frames']):
   if f['atlas']!=page:
    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
    page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
   x,y,w,h=f['region'];p=np.array(prior.crop((x,y,x+w,y+h)).convert('RGBA'));assert w%period==0 and h%period==0
   cells=p.reshape(h//period,period,w//period,period,4);small=cells[:,0,:,0,:];assert np.all(cells==small[:,None,:,None,:]),f'{name} frame {i} not on {period}px grid'
   pad=np.pad(small,((1,1),(1,1),(0,0)),mode='edge');b=pad[:-2,1:-1];d=pad[1:-1,:-2];right=pad[1:-1,2:];down=pad[2:,1:-1];eq=lambda p,q:np.all(p==q,axis=2)
   active=(~eq(b,down))&(~eq(d,right));q=np.repeat(np.repeat(small,2,axis=0),2,axis=1)
   for dx,dy,cond,repl in [(0,0,eq(d,b),d),(1,0,eq(b,right),right),(0,1,eq(d,down),d),(1,1,eq(down,right),right)]:
    tile=q[dy::2,dx::2];mask=active&cond;tile[mask]=repl[mask]
   counts.append(int(np.any(q!=np.repeat(np.repeat(small,2,axis=0),2,axis=1),axis=2).sum()));Image.fromarray(q).save(logical/f'frame_{i:03d}.png');atlas.paste(Image.fromarray(q).resize((w,h),Image.Resampling.NEAREST),(x,y))
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  w,h=e['size'];result={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':base_name,'art_source':'existing','frame_count':e['frame_count'],'frames':e['frames'],'grid_period':period,'logical_canvas':[w//period,h//period],'refined_canvas':[2*w//period,2*h//period],'viewer_canvas':[w,h],'changed_subpixels_per_frame':counts,'status':'candidate_unreviewed','method':'Exact uniform source cells; Scale2x edge rules using source RGBA colors; nearest resize to fixed original canvas for viewer.','limitations':'Interpolation cannot recover details absent from GIF. Fine silhouettes, effects, or flicker may change. Non-integer display scaling can create uneven pixel widths; compare every frame.'}
  (out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(name,len(counts),'frames',result['logical_canvas'],'->',result['refined_canvas'],'changed subpixels',sum(counts),flush=True)
if __name__=='__main__':main()
