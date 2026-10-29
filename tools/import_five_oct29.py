#!/usr/bin/env python3
"""Import five supplied GIFs as provisional measured atlases and Forge clips."""
import json,math,shutil,subprocess,sys
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from extract_gif_assets import extract
from import_charnew import ROOT,A,digest,write
from import_oct29_gifs import background,key
from import_five_oct29_specs import SPECS
FORGE=Path('/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py')
stage=A/'five_oct29_staging'
if stage.exists():raise FileExistsError(stage)
for n in SPECS:
 assert (ROOT/(n+'.gif')).is_file()
 for p in [A/'vfx'/(n+'.gif'),A/'extracted'/n,A/'measured_atlas_pilots'/n,A/'forge_pilots/five_oct29'/n]:
  if p.exists():raise FileExistsError(p)
cat= json.loads((A/'extracted/catalog.json').read_text()); assert not set(SPECS)&{e['id'] for e in cat['assets']}
stage.mkdir();results=[]
for n,(height,bounds) in SPECS.items():
 root=stage/n;root.mkdir();source=ROOT/(n+'.gif');entry=extract(source,root/'extracted');entry['source']=f'Asset/Character/vfx/{n}.gif'; meta_dir=root/'measured';meta_dir.mkdir();forge=root/'forge';forge.mkdir();(forge/'input_frames').mkdir();frames=[];pages={};bgcounts=Counter();removed=[];contact={shade:Image.new('RGB',(1000,((entry['frame_count']+7)//8)*140),color) for shade,color in [('light','#d9d9d9'),('dark','#242424')]};draws={k:ImageDraw.Draw(v) for k,v in contact.items()}
 with Image.open(source) as gif:
  w,h=gif.size;cols=2048//w;rows=2048//h;capacity=cols*rows
  for i in range(gif.n_frames):
   gif.seek(i);raw=gif.convert('RGBA');bg=background(raw);bgcounts[','.join(map(str,bg.tolist()))]+=1;clean,count=key(raw,bg);removed.append(count);page,slot=divmod(i,capacity)
   if page not in pages:
    countpage=min(capacity,gif.n_frames-page*capacity);pages[page]=Image.new('RGBA',(min(cols,countpage)*w,math.ceil(countpage/cols)*h))
   x,y=slot%cols*w,slot//cols*h;pages[page].paste(clean,(x,y));frames.append({'atlas':page,'region':[x,y,w,h],'duration_ms':entry['frames'][i]['duration_ms']});clean.save(forge/'input_frames'/f'frame_{i:03d}.png',compress_level=3)
   thumb=clean.copy();thumb.thumbnail((120,115),Image.Resampling.NEAREST)
   for shade,sheet in contact.items():
    xx=i%8*125; yy=i//8*140;sheet.paste(thumb,(xx+(125-thumb.width)//2,yy+18),thumb);draws[shade].text((xx+2,yy+2),str(i+1),fill='black' if shade=='light' else 'white')
 for p,img in pages.items():img.save(meta_dir/f'atlas_{p:03d}.png',compress_level=3)
 ref=bounds[3]-bounds[1];anchor=[(bounds[0]+bounds[2])/2,bounds[3]]
 m={'id':n,'source':entry['source'],'source_sha256':entry['source_sha256'],'art_source':'existing','frame_count':len(frames),'frames':frames,'frame_size':[w,h],'target_height_px':height,'reference_frame':0,'reference_height_px':ref,'reference_body_bounds':bounds,'anchor_px':anchor,'display_scale':height/ref,'measurement_kind':'visually_estimated_body_bounds','status':'candidate_unreviewed','size_target_approval':'user_requested_20261029_five','background_rgb_frame_counts':dict(bgcounts),'removed_per_frame':removed,'method':'Per-frame most common border RGB; remove opaque pixels within maximum channel difference 5. Fixed body reference and anchor estimated visually from frame 0; no resizing or frame cropping.','limitations':'Matte can retain background or remove similarly coloured details; body bounds and anchor are visual estimates affected by effects and pose; review all frames and playback.'};write(meta_dir/'candidate.json',m)
 for shade,sheet in contact.items():sheet.save(root/f'contact-{shade}.jpg',quality=90)
 manifest={'schema':'generate2dsprite.animation_clips.v2','frames':[f'input_frames/frame_{i:03d}.png' for i in range(len(frames))],'anchor_px':anchor,'art_source':'existing','sampling':'nearest','pixel_art':True,'clips':{'reference_unclassified':{'frames':list(range(len(frames))),'duration_ms':[f['duration_ms'] for f in frames],'loop':True}}};write(forge/'manifest.json',manifest)
 result=subprocess.run([sys.executable,str(FORGE),'--manifest',str(forge/'manifest.json'),'--output-dir',str(forge/'clips'),'--no-reviews'],capture_output=True,text=True);(forge/'build.log').write_text(result.stdout+result.stderr);print(n,'frames',len(frames),'reference',ref,'background',dict(bgcounts),'forge exit',result.returncode,flush=True)
 if result.returncode: raise RuntimeError(result.stderr+result.stdout)
 results.append((n,entry,m))
# Only install once all five have been successfully staged.
paths={'targets':A/'characters/height-targets.json','roster':A/'characters/roster.json','inventory':A/'review/inventory.json','status':A/'review/background-review-status.json'};data={k:json.loads(p.read_text()) for k,p in paths.items()};provisional=[]
for n,entry,m in results:
 root=stage/n;shutil.copyfile(ROOT/(n+'.gif'),A/'vfx'/(n+'.gif'));shutil.move(str(root/'extracted'/n),str(A/'extracted'/n));shutil.move(str(root/'measured'),str(A/'measured_atlas_pilots'/n));(A/'forge_pilots/five_oct29').mkdir(parents=True,exist_ok=True);shutil.move(str(root/'forge'),str(A/'forge_pilots/five_oct29'/n));review=A/'review'/f'five_oct29_{n}';review.mkdir();
 for s in ['light','dark']:shutil.move(str(root/f'contact-{s}.jpg'),str(review/f'contact-{s}.jpg'))
 cat['assets'].append(entry);data['targets']['assets'].append({'id':n,'target_height_px':m['target_height_px'],'source':entry['source'],'source_sha256':entry['source_sha256'],'reference_frame':0,'reference_body_bounds':m['reference_body_bounds'],'scale':m['display_scale'],'status':'visual_body_estimate_unreviewed','measured_atlas_candidate':f'Asset/Character/measured_atlas_pilots/{n}/candidate.json','size_target_approval':m['size_target_approval']});data['roster']['entries'].append({'source_id':n,'provisional_character_name':n,'source':entry['source'],'source_sha256':entry['source_sha256'],'identity_status':'name_from_filename_visual_review_needed','animations':{},'skill':{'status':'unreviewed','name':None,'provenance':None},'attack_range':'unreviewed','notes':'Nguồn mới, hoạt ảnh chưa phân loại; nền và mốc thân cần duyệt.'});data['inventory']['sources'].append({'source':entry['source'],'sha256':entry['source_sha256'],'frames':len(m['frames']),'review_sheets':[f'Asset/Character/review/five_oct29_{n}/contact-{s}.jpg' for s in ['light','dark']],'status':'unreviewed','observations':[],'characters':[]});data['status']['sources'].append({'id':n,'status':'visual_review_pending','issue':'Tách màu nền và mốc thân ước lượng; cần duyệt viền, VFX, chuyển động và neo.','variants':['measured_atlas_pilots']});provisional.append({'id':n,'profile':n,'source_sha256':entry['source_sha256']})
cat['assets'].sort(key=lambda e:e['id'].lower());data['targets']['assets'].sort(key=lambda e:e['id'].lower());write(A/'extracted/catalog.json',cat)
for k,p in paths.items():write(p,data[k])
write(A/'characters/provisional-animations-five-20261029.json',{'status':'pending_visual_review','assets':provisional});shutil.rmtree(stage);print('Installed five provisional animations; existing approved snapshot untouched.')
