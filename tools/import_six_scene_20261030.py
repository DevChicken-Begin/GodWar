#!/usr/bin/env python3
"""Import six GIFs using a provisional shared-scene matte. Preserve all sources."""
import json, hashlib, math, shutil, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from extract_gif_assets import extract
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'
SPECS={'Also':(80,[200,325,320,455]),'Aquamen':(85,[190,285,335,455]),'Diorai':(90,[195,275,330,450]),'Evenl':(85,[195,295,330,455]),'Moregorn':(80,[190,295,330,455]),'Moresword':(85,[190,300,335,460])}
FORGE=Path('/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py')
def write(path, value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def input_gif(name):
 root = ROOT / f'{name}.gif'
 return root if root.is_file() else A / 'vfx' / f'{name}.gif'
def main():
 stage=A/'six_import_stage_20261030'; stage.mkdir(exist_ok=False)
 cat=json.loads((A/'extracted/catalog.json').read_text())
 for n in SPECS:
  if any(x['id']==n for x in cat['assets']) or any(p.exists() for p in [A/'vfx'/f'{n}.gif',A/'extracted'/n,A/'measured_atlas_pilots'/n]): raise RuntimeError(f'Existing output: {n}')
 samples=[]; refs=[]
 for n in list(SPECS)+['animent','overight','tigerknight']:
  p=input_gif(n) if n in SPECS else A/'vfx'/f'{n}.gif'; refs.append({'source':str(p.relative_to(ROOT)),'sha256':sha(p)})
  with Image.open(p) as gif:
   for i in np.linspace(0,gif.n_frames-1,8,dtype=int): gif.seek(i);samples.append(np.asarray(gif.convert('RGB')).copy())
 bg=np.median(np.stack(samples),axis=0).astype(np.int16); results=[]
 for n,(height,bounds) in SPECS.items():
  src=input_gif(n); out=stage/n;out.mkdir(); entry=extract(src,out/'extracted'); entry['source']=f'Asset/Character/vfx/{n}.gif'
  gif=Image.open(src); arr=[]
  for i in range(gif.n_frames): gif.seek(i);arr.append(np.asarray(gif.convert('RGB')).copy())
  first=arr[0].astype(np.int16);stable=np.zeros(first.shape[:2],np.uint16)
  for rgb in arr: stable+=np.max(np.abs(rgb.astype(np.int16)-first),axis=2)<=8
  yy,xx=np.indices(first.shape[:2]);logo=(yy<150)&(stable>=len(arr)*.8)
  measured=out/'measured';measured.mkdir(); forge=out/'forge';forge.mkdir(); (forge/'input_frames').mkdir();pages={};frames=[];counts=[]
  sheets={shade:Image.new('RGB',(1000,math.ceil(len(arr)/8)*140),color) for shade,color in [('light','#eee'),('dark','#181818')]};draw={k:ImageDraw.Draw(v) for k,v in sheets.items()}
  for i,rgb in enumerate(arr):
   diff=np.max(np.abs(rgb.astype(np.int16)-bg),axis=2); close=np.max(np.abs(rgb.astype(np.int16)-first),axis=2)<=10
   alpha=(diff>16)&~(logo&close); rgba=np.dstack((rgb,alpha.astype(np.uint8)*255));clean=Image.fromarray(rgba);counts.append(int(alpha.sum()))
   f=entry['frames'][i];page=f['atlas'];x,y,w,h=f['region']
   if page not in pages:
    with Image.open(out/'extracted'/n/f'atlas_{page:03d}.png') as old: pages[page]=Image.new('RGBA',old.size)
   pages[page].paste(clean,(x,y));frames.append(f); clean.save(forge/'input_frames'/f'frame_{i:03d}.png',compress_level=3)
   thumb=clean.resize((115,115),Image.Resampling.NEAREST)
   for shade,sheet in sheets.items():
    xx0=i%8*125;yy0=i//8*140;sheet.paste(thumb,(xx0+5,yy0+20),thumb);draw[shade].text((xx0+2,yy0+2),str(i),fill='black' if shade=='light' else 'white')
  for page,img in pages.items(): img.save(measured/f'atlas_{page:03d}.png',compress_level=3)
  for shade,sheet in sheets.items():sheet.save(out/f'contact-{shade}.jpg',quality=92)
  ref=bounds[3]-bounds[1];anchor=[(bounds[0]+bounds[2])/2,bounds[3]]
  meta={'id':n,'source':entry['source'],'source_sha256':entry['source_sha256'],'art_source':'existing','frame_count':len(frames),'frames':frames,'frame_size':[520,520],'target_height_px':height,'reference_frame':0,'reference_height_px':ref,'reference_body_bounds':bounds,'anchor_px':anchor,'display_scale':height/ref,'measurement_kind':'visually_estimated_body_bounds','status':'candidate_unreviewed','size_target_approval':'user_requested_20261030','method':'Shared median of six GIFs and three older shared-scene sources; RGB maximum difference >16; stable upper logo mask, first-frame difference <=10.','model_sources':refs,'opaque_pixels_per_frame':counts,'limitations':'Foreground or FX can be removed or background/logo can remain. Body bounds are approximate and unapproved; review all frames and motion.'};write(measured/'candidate.json',meta)
  manifest={'schema':'generate2dsprite.animation_clips.v2','frames':[f'input_frames/frame_{i:03d}.png' for i in range(len(frames))],'anchor_px':anchor,'art_source':'existing','sampling':'nearest','pixel_art':True,'clips':{'reference_unclassified':{'frames':list(range(len(frames))),'duration_ms':[f['duration_ms'] for f in frames],'loop':True}}};write(forge/'manifest.json',manifest)
  res=subprocess.run([sys.executable,str(FORGE),'--manifest',str(forge/'manifest.json'),'--output-dir',str(forge/'clips'),'--no-reviews'],capture_output=True,text=True);(forge/'build.log').write_text(res.stdout+res.stderr)
  if res.returncode: raise RuntimeError(f'{n}: {res.stderr} {res.stdout}')
  results.append((n,entry,meta));print(n, len(frames),flush=True)
 paths={'targets':A/'characters/height-targets.json','roster':A/'characters/roster.json','inventory':A/'review/inventory.json','status':A/'review/background-review-status.json','provisional':A/'characters/provisional-animations-five-20261029.json'};data={k:json.loads(p.read_text()) for k,p in paths.items()}
 for n,entry,m in results:
  out=stage/n;shutil.copy2(input_gif(n),A/'vfx'/f'{n}.gif');shutil.move(str(out/'extracted'/n),str(A/'extracted'/n));shutil.move(str(out/'measured'),str(A/'measured_atlas_pilots'/n)); dest=A/'forge_pilots/six_20261030';dest.mkdir(exist_ok=True);shutil.move(str(out/'forge'),str(dest/n));review=A/'review/six-import-20261030'/n;review.mkdir()
  for shade in ['light','dark']:shutil.move(str(out/f'contact-{shade}.jpg'),str(review/f'contact-{shade}.jpg'))
  cat['assets'].append(entry); data['targets']['assets'].append({'id':n,'target_height_px':m['target_height_px'],'source':entry['source'],'source_sha256':entry['source_sha256'],'reference_frame':0,'reference_body_bounds':m['reference_body_bounds'],'scale':m['display_scale'],'status':'visual_body_estimate_unreviewed','measured_atlas_candidate':f'Asset/Character/measured_atlas_pilots/{n}/candidate.json','size_target_approval':m['size_target_approval']});data['roster']['entries'].append({'source_id':n,'provisional_character_name':n,'source':entry['source'],'source_sha256':entry['source_sha256'],'identity_status':'name_from_filename_visual_review_needed','animations':{},'skill':{'status':'unreviewed','name':None,'provenance':None},'attack_range':'unreviewed','notes':'Chưa duyệt nền, hiệu ứng, thân và neo.'});data['inventory']['sources'].append({'source':entry['source'],'sha256':entry['source_sha256'],'frames':len(m['frames']),'review_sheets':[str((review/f'contact-{s}.jpg').relative_to(ROOT)) for s in ['light','dark']],'status':'unreviewed','observations':[],'characters':[]});data['status']['sources'].append({'id':n,'status':'visual_review_pending','issue':'Nền và logo phức tạp; còn khả năng sót nền, xóa nhầm VFX. Thân và neo ước lượng, chưa duyệt.','variants':['measured_atlas_pilots']});data['provisional']['assets'].append({'id':n,'profile':n,'source_sha256':entry['source_sha256']})
 cat['assets'].sort(key=lambda e:e['id'].lower());data['targets']['assets'].sort(key=lambda e:e['id'].lower());write(A/'extracted/catalog.json',cat)
 for k,p in paths.items():write(p,data[k])
 shutil.rmtree(stage);print('Imported six provisional candidates',flush=True)
if __name__=='__main__':main()
