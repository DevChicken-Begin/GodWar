#!/usr/bin/env python3
"""Remove stable blue background and stable logo remnants using 80 shared-scene samples."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, json,hashlib,shutil,subprocess,sys
A=Path('Asset/Character');names='Kungteng charmia combra cons cornra hecpoirt isis ison isorat kikontai maxoi omega ompan onaon oset osiris pandung samset thorn uopon'.split();samples=[];sources=[]
for n in names:
 p=A/'vfx'/f'{n}.gif';g=Image.open(p);idxs=[0,g.n_frames//3,2*g.n_frames//3,g.n_frames-1];sources.append({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frames':idxs})
 for i in idxs:g.seek(i);samples.append(np.asarray(g.convert('RGB')).copy())
stack=np.stack(samples).astype(np.int16);ref=np.median(stack,axis=0).astype(np.int16);matches=(np.max(np.abs(stack-ref),axis=3)<=8).sum(axis=0);stable=matches>=len(samples)*.7; blue=stable&(ref[:,:,0]<40)&(ref[:,:,1]<115)&(ref[:,:,2]<165)&(ref[:,:,2]>ref[:,:,1]);yy,xx=np.indices((520,520));logo=stable&(yy>=35)&(yy<150)&(xx>=90)&(xx<435);review=A/'review/twenty-import-20261030';Image.fromarray(ref.astype(np.uint8)).save(review/'static-reference.png');Image.fromarray((blue*255).astype(np.uint8)).save(review/'static-blue-mask.png');refs_hash=hashlib.sha256((review/'static-reference.png').read_bytes()).hexdigest();summary=[]
for n in names:
 cur=A/'measured_atlas_pilots'/n;backup=A/'archive/twenty_before_static_residue'/n
 if backup.exists():raise FileExistsError(backup)
 backup.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(cur,backup);m=json.load(open(cur/'candidate.json'));pages={};counts=[];group='six_remaining_20261030' if n in ['Kungteng','cons','isis','omega','oset','pandung'] else 'fourteen_20261030';forge=A/'forge_pilots'/group/n;frames=forge/'static_refined_frames';frames.mkdir(exist_ok=False);sheets={shade:Image.new('RGB',(1000,((len(m['frames'])+7)//8)*140),color) for shade,color in [('light','#eee'),('dark','#181818')]};draw={k:ImageDraw.Draw(v) for k,v in sheets.items()}
 for i,f in enumerate(m['frames']):
  idx=f['atlas'];x,y,w,h=f['region']
  if idx not in pages:pages[idx]=np.array(Image.open(backup/f'atlas_{idx:03d}.png').convert('RGBA'))
  a=pages[idx][y:y+h,x:x+w];rgb=a[:,:,:3].astype(np.int16);dist=np.max(np.abs(rgb-ref),axis=2);mask=((blue&(dist<=8))|(logo&(dist<=8)))&(a[:,:,3]>0);counts.append(int(mask.sum()));a[mask,3]=0;im=Image.fromarray(a.copy());im.save(frames/f'frame_{i:03d}.png',compress_level=3);thumb=im.resize((115,115),Image.Resampling.NEAREST)
  for shade,sheet in sheets.items():
   px=i%8*125;py=i//8*140;sheet.paste(thumb,(px+5,py+20),thumb);draw[shade].text((px+2,py+2),str(i),fill='black' if shade=='light' else 'white')
 for idx,arr in pages.items():Image.fromarray(arr).save(cur/f'atlas_{idx:03d}.png',compress_level=3)
 for shade,sheet in sheets.items():sheet.save(review/n/f'static-refined-{shade}.jpg',quality=95)
 m['static_residue_refinement']={'base':str(backup),'reference':str(review/'static-reference.png'),'reference_sha256':refs_hash,'sample_sources':sources,'method':'Median 80 GIF samples; stable pixel at >=70% within RGB max distance 8; remove visible blue background-matching pixel, or stable logo-region pixel, within RGB max distance 8.','removed_per_frame':counts,'limitations':'Character/VFX can match stable scene colors; logo or blue pixels outside the thresholds may remain. Needs visual review.'};m['forge_current_clip']='static-refined-clips/animation-clips.json';(cur/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 manifest=json.load(open(forge/'manifest.json'));manifest['frames']=[f'static_refined_frames/frame_{i:03d}.png' for i in range(len(counts))];(forge/'static-refined-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');r=subprocess.run([sys.executable,'/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py','--manifest',str(forge/'static-refined-manifest.json'),'--output-dir',str(forge/'static-refined-clips'),'--no-reviews'],capture_output=True,text=True);(forge/'static-refined-build.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(n+': '+r.stderr)
 summary.append({'id':n,'removed_pixels':sum(counts),'frames_changed':sum(c>0 for c in counts)});print(n,sum(counts),flush=True)
(review/'static-refinement-summary.json').write_text(json.dumps({'reference_sources':sources,'results':summary},ensure_ascii=False,indent=2)+'\n')
