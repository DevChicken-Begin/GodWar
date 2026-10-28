#!/usr/bin/env python3
"""Build auditable Scale2x candidates only where every source grid is exact."""
import hashlib,json,os,shutil
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';AUDIT=ROOT/'docs/fine-batch/audit.json';REPORT=ROOT/'docs/fine-batch/build.json'
def save(report):
 temp=REPORT.with_suffix('.tmp');temp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');os.replace(temp,REPORT)
def frames_from(folder,entry):
 page=-1;img=None
 try:
  for f in entry['frames']:
   if f['atlas']!=page:
    if img is not None:img.close()
    page=f['atlas'];img=Image.open(folder/f'atlas_{page:03d}.png').convert('RGBA')
   x,y,w,h=f['region'];yield np.array(img.crop((x,y,x+w,y+h)))
 finally:
  if img is not None:img.close()
def same_grid(p,k):
 h,w=p.shape[:2];cells=p.reshape(h//k,k,w//k,k,4);small=cells[:,0,:,0,:];return np.all(cells==small[:,None,:,None,:])
def scale2(p,k):
 h,w=p.shape[:2];small=p.reshape(h//k,k,w//k,k,4)[:,0,:,0,:];pad=np.pad(small,((1,1),(1,1),(0,0)),mode='edge');b=pad[:-2,1:-1];d=pad[1:-1,:-2];r=pad[1:-1,2:];dn=pad[2:,1:-1];eq=lambda p,q:np.all(p==q,axis=2);active=(~eq(b,dn))&(~eq(d,r));q=np.repeat(np.repeat(small,2,axis=0),2,axis=1)
 for dx,dy,condition,replace in ((0,0,eq(d,b),d),(1,0,eq(b,r),r),(0,1,eq(d,dn),d),(1,1,eq(dn,r),r)):
  tile=q[dy::2,dx::2];selected=active&condition;tile[selected]=replace[selected]
 return small,q

def process(row,entry):
 name=row['id'];base=A/row['base_candidate']/name;src=ROOT/entry['source'];out=A/'fine_candidates'/name;review=A/'review'/name/'fine_frames';stage=A/'fine_candidates'/('.batch-stage-'+name);stage_frames=A/'review'/name/'.batch-fine-frames'
 if any(p.exists() for p in (out,review,stage,stage_frames)):return {'status':'output_already_exists'}
 if hashlib.sha256(src.read_bytes()).hexdigest()!=entry['source_sha256']:return {'status':'source_hash_mismatch'}
 options=row['periods'][:];durations=[];source_start=entry.get('sourceStart',0)
 with Image.open(src) as gif:
  for i,(pixels,f) in enumerate(zip(frames_from(base,entry),entry['frames'])):
   gif.seek(i+source_start);actual=gif.info.get('duration',0);durations.append(actual)
   if actual!=f['duration_ms']:return {'status':'duration_mismatch','frame':i}
   options=[n for n in options if same_grid(pixels,n)]
   if not options:return {'status':'no_exact_grid_all_frames','first_nonuniform_frame':i}
 if len(durations)!=len(entry['frames']):return {'status':'frame_count_mismatch'}
 period=options[0];stage.mkdir(parents=True);stage_frames.mkdir(parents=True);counts=[];page=-1;atlas=None;previous_page=None
 try:
  for i,(pixels,f) in enumerate(zip(frames_from(base,entry),entry['frames'])):
   if f['atlas']!=page:
    if atlas is not None:atlas.save(stage/f'atlas_{page:03d}.png',compress_level=1)
    page=f['atlas']
    with Image.open(base/f'atlas_{page:03d}.png') as im:atlas=Image.new('RGBA',im.size)
   small,q=scale2(pixels,period);plain=np.repeat(np.repeat(small,2,axis=0),2,axis=1);counts.append(int(np.any(q!=plain,axis=2).sum()));Image.fromarray(q).save(stage_frames/f'frame_{i:03d}.png')
   x,y,w,h=f['region'];atlas.paste(Image.fromarray(q).resize((w,h),Image.Resampling.NEAREST),(x,y))
  if atlas is not None:atlas.save(stage/f'atlas_{page:03d}.png',compress_level=1)
  base_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(base.glob('atlas_*.png'))};w,h=entry['size'];meta={'source':entry['source'],'source_sha256':entry['source_sha256'],'source_start':source_start,'base_candidate':row['base_candidate'],'base_atlas_sha256':base_hashes,'art_source':'existing','frame_count':entry['frame_count'],'frames':entry['frames'],'grid_period':period,'logical_canvas':[w//period,h//period],'refined_canvas':[2*w//period,2*h//period],'viewer_canvas':[w,h],'changed_subpixels_per_frame':counts,'status':'candidate_unreviewed','method':'Every frame has exact aligned source cells; Scale2x edge rules preserve source RGBA palette; nearest resize to existing viewer canvas.','limitations':'Cannot recover absent detail. Edge/VFX silhouettes can change or flicker; non-integer display scale can yield uneven widths. Source and prior unreviewed background candidate preserved.'}
  (stage/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');os.rename(stage_frames,review);os.rename(stage,out)
 except BaseException:
  if stage.exists():shutil.rmtree(stage)
  if stage_frames.exists():shutil.rmtree(stage_frames)
  raise
 return {'status':'created_unreviewed','period':period,'frames':entry['frame_count'],'logical_canvas':meta['logical_canvas'],'refined_canvas':meta['refined_canvas'],'changed_subpixels':sum(counts)}
def main():
 audit=json.loads(AUDIT.read_text());entries={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']+json.loads((A/'extracted/split-catalog.json').read_text())['assets']};report={'version':1,'method':'Exact aligned per-frame source-grid validation; no source modification; only complete candidate directories published.','results':[]};save(report)
 for row in audit['results']:
  if row['status']!='sampled_grid':report['results'].append({'id':row['id'],'status':row['status']});continue
  try:r=process(row,entries[row['id']])
  except (OSError,ValueError,AssertionError,KeyError) as exc:r={'status':'failed','error':str(exc)}
  report['results'].append({'id':row['id'],**r});save(report);print(row['id'],r['status'],r.get('period',''),r.get('error',''),flush=True)
 from collections import Counter
 print('SUMMARY',dict(Counter(x['status'] for x in report['results'])),flush=True)
if __name__=='__main__':main()
