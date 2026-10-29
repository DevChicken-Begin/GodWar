#!/usr/bin/env python3
"""Build reviewable measured previews from preserved inputs; never modify GIF sources."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageFilter
from build_measured_atlas_pilots import pack, A, ROOT

def read(p): return json.loads(p.read_text())
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def frames(folder,meta):
 pages={}; out=[]
 for f in meta['frames']:
  a=f['atlas']
  if a not in pages: pages[a]=Image.open(folder/f'atlas_{a:03d}.png').convert('RGBA')
  x,y,w,h=f['region'];out.append(pages[a].crop((x,y,x+w,y+h)))
 return out
archive=A/'archive/revision_oct29'
if archive.exists(): raise FileExistsError(archive)
archive.mkdir(parents=True)
for name in ['Actem','fireknight']:
 current=A/'measured_atlas_pilots'/name
 shutil.copytree(current,archive/name)
 old=read(archive/name/'candidate.json')
 if sha(ROOT/old['source'])!=old['source_sha256']: raise ValueError('source hash mismatch')
 if name=='Actem':
  imgs=frames(archive/name,old); size=tuple(round(x*1.2) for x in old['frame_size']); processed=[]
  for im in imgs:
   im=im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA'); alpha=im.getchannel('A');im=im.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1,percent=18,threshold=3));im.putalpha(alpha);processed.append(im)
  reference=old['reference_height_px']*1.2; anchor=[v*1.2 for v in old['anchor_px']]; target=85; source_dir=archive/name
 else:
  source_dir=A/'fire_deep_candidates'/name; deep=read(source_dir/'candidate.json'); assert deep['source_sha256']==old['source_sha256'];processed=frames(source_dir,deep);reference=old['reference_height_px'];anchor=old['anchor_px'];target=old['target_height_px']
 shutil.rmtree(current)
 pack(name,processed,[f['duration_ms'] for f in old['frames']],target,reference,anchor,{'source':old['source'],'source_sha256':old['source_sha256'],'input_candidate':str(source_dir.relative_to(ROOT)),'input_atlas_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(source_dir.glob('atlas_*.png'))}})
 p=current/'candidate.json';meta=read(p);meta['method']=('Premultiplied Lanczos 120% and mild unsharp mask, matching Hatomin; display target 85 px.' if name=='Actem' else 'Repacked previously reviewed fire_deep candidate into measured preview; retains its particle-removal limitations.');meta['limitations']='Mốc alpha frame 0 chưa xác nhận là chiều cao thân; nội suy không tạo thêm chi tiết nguồn.' if name=='Actem' else 'Lọc màu có thể xóa hạt VFX hoặc còn sót đốm; cần duyệt toàn bộ frame và nền.';meta['status']='candidate_unreviewed';write(p,meta)
p=A/'characters/height-targets.json';data=read(p);item=next(x for x in data['assets'] if x['id']=='Actem');item['target_height_px']=85;item['scale']=85/(read(A/'measured_atlas_pilots/Actem/candidate.json')['reference_height_px']);write(p,data)
