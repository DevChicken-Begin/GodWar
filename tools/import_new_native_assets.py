#!/usr/bin/env python3
"""Import five supplied GIFs and create native-resolution chroma candidates."""
import hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES=('reptalian','dracian','vargost','xinchan','raptilian')
sys.path.insert(0,str(ROOT/'tools'));from extract_gif_assets import extract

def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 catalog=load(A/'extracted/catalog.json');roster=load(A/'characters/roster.json');inventory=load(A/'review/inventory.json');review=load(A/'review/background-review-status.json')
 for n in NAMES:
  if not (ROOT/f'{n}.gif').is_file():raise FileNotFoundError(n)
  if (A/f'vfx/{n}.gif').exists() or (A/'extracted'/n).exists() or (A/'native_candidates'/n).exists() or any(e['id']==n for e in catalog['assets']):raise FileExistsError(n)
 for n in NAMES:
  source=ROOT/f'{n}.gif';dest=A/'vfx'/source.name
  with source.open('rb') as r,dest.open('xb') as w:shutil.copyfileobj(r,w)
  entry=extract(dest,A/'extracted');assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['source_sha256']
  out=A/'native_candidates'/n;out.mkdir(parents=True);reviews=A/'review'/n;reviews.mkdir();counts=[];pages=-1;atlas=None
  with Image.open(dest) as gif:
   gif.seek(0); bg=np.array(gif.convert('RGBA').getpixel((0,0))[:3],dtype=np.int16); sheet=None
   for i,f in enumerate(entry['frames']):
    gif.seek(i);im=gif.convert('RGBA');px=np.array(im); assert np.all(px[0,0,:3]==bg) and np.all(px[-1,-1,:3]==bg)
    distance=np.max(np.abs(px[:,:,:3].astype(np.int16)-bg),axis=2);mask=(px[:,:,3]>0)&(distance<=5);counts.append(int(mask.sum()));px[mask]=0
    if pages!=f['atlas']:
     if atlas is not None:atlas.save(out/f'atlas_{pages:03d}.png',compress_level=1)
     pages=f['atlas']
     with Image.open(A/'extracted'/n/f'atlas_{pages:03d}.png') as old:atlas=Image.new('RGBA',old.size)
    x,y,w,h=f['region'];atlas.paste(Image.fromarray(px),(x,y))
    if i%40==0:sheet=Image.new('RGB',(8*112,5*130),'#444');draw=ImageDraw.Draw(sheet)
    t=im.copy();t.thumbnail((104,104),Image.Resampling.LANCZOS);slot=i%40;sx=slot%8*112;sy=slot//8*130;sheet.paste(t,(sx+(112-t.width)//2,sy+20),t);draw.text((sx+2,sy+2),f'#{i} {f["duration_ms"]}ms',fill='white')
    if i%40==39 or i==entry['frame_count']-1:sheet.save(reviews/f'frames_{i//40*40:04d}_{i:04d}.jpg',quality=90)
   if atlas is not None:atlas.save(out/f'atlas_{pages:03d}.png',compress_level=1)
  meta={'source':entry['source'],'source_sha256':entry['source_sha256'],'art_source':'existing','method':'Original-resolution RGBA; clear pixels within RGB max 5 of the measured flat corner color, no resizing or palette reduction','background_rgb':bg.tolist(),'frame_count':entry['frame_count'],'frames':entry['frames'],'removed_per_frame':counts,'status':'candidate_unreviewed','limitations':'Colors close to background may occur on character or effects and be removed; disconnected background, lettering or edge artifacts can remain. Compare every frame with original.'}
  save(out/'candidate.json',meta);catalog['assets'].append(entry)
  roster['entries'].append({'source_id':n,'provisional_character_name':n,'source':entry['source'],'source_sha256':entry['source_sha256'],'identity_status':'name_from_filename_visual_review_needed','animations':{},'skill':{'status':'unreviewed','name':None,'provenance':None},'attack_range':'unreviewed','notes':'GIF người dùng cung cấp; chưa phân đoạn hành động hay skill.'})
  sheets=sorted(p.name for p in reviews.glob('frames_*.jpg'));inventory['sources'].append({'source':entry['source'],'sha256':entry['source_sha256'],'frames':entry['frame_count'],'review_sheets':sheets,'status':'unreviewed','observations':[],'characters':[]})
  review['sources'].append({'id':n,'status':'visual_review_pending','issue':'Bản tách nền nguyên độ phân giải chưa duyệt; có thể mất chi tiết cùng màu nền hoặc còn nền/VFX.','variants':['native_candidates']})
  print(n,entry['frame_count'],'frames',entry['size'],'sha256',entry['source_sha256'],flush=True)
 catalog['assets'].sort(key=lambda e:e['id'].lower());save(A/'extracted/catalog.json',catalog);save(A/'characters/roster.json',roster);save(A/'review/inventory.json',inventory);save(A/'review/background-review-status.json',review)
 index=A/'extracted/index.html';text=index.read_text();cards=[]
 for e in catalog['assets']:
  if e['id'] in NAMES:cards.append(f'<article><h2>{e["id"]}</h2><img loading="lazy" src="../vfx/{e["id"]}.gif" alt="{e["id"]}"><p>{e["frame_count"]} frames · {e["size"][0]} × {e["size"][1]} · chưa kiểm duyệt</p></article>')
 index.write_text(text.replace('</main></html>','\n'.join(cards)+'</main></html>'))
if __name__=='__main__':main()
