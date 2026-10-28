#!/usr/bin/env python3
"""Publish the prepared Aonoma source and Forge frames as review-only viewer data."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'; REVIEW=A/'review/aonoma'; OUT=A/'pixel_candidates/aonoma'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 entry=read(REVIEW/'extraction-entry.json');catalog=read(A/'extracted/catalog.json');roster=read(A/'characters/roster.json');inventory=read(A/'review/inventory.json');status=read(A/'review/background-review-status.json');source=ROOT/entry['source']
 if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['source_sha256']:raise ValueError('source hash mismatch')
 if any(x['id']=='aonoma' for x in catalog['assets']) or OUT.exists() or any(x.get('source_id')=='aonoma' for x in roster['entries']):raise FileExistsError('candidate or catalog entry exists')
 if any(x.get('source')==entry['source'] for x in inventory['sources']) or any(x['id']=='aonoma' for x in status['sources']):raise ValueError('review entry exists')
 qa=read(REVIEW/'forge_quantized/quantize-qa.json');assert qa['status']=='pass' and len(qa['frames'])==entry['frame_count']
 OUT.mkdir(parents=True);number=-1; atlas=None
 for i,f in enumerate(entry['frames']):
  if number!=f['atlas']:
   if atlas is not None:atlas.save(OUT/f'atlas_{number:03d}.png',compress_level=1)
   number=f['atlas']
   with Image.open(A/'extracted/aonoma'/f'atlas_{number:03d}.png') as p:atlas=Image.new('RGBA',p.size)
  with Image.open(REVIEW/'forge_quantized'/f'frame_{i:03d}.png') as frame:
   frame=frame.convert('RGBA').resize((270,216),Image.Resampling.NEAREST).crop((0,0,268,214));x,y,w,h=f['region'];assert frame.size==(w,h);atlas.paste(frame,(x,y))
 if atlas is not None:atlas.save(OUT/f'atlas_{number:03d}.png',compress_level=1)
 meta={'source':entry['source'],'source_sha256':entry['source_sha256'],'art_source':'existing','frame_count':entry['frame_count'],'frames':entry['frames'],'grid_scale':3,'logical_canvas':[90,72], 'preview_canvas':[268,214], 'palette_colors':32,'palette':'Asset/Character/review/aonoma/forge_quantized/palette.json','qa':'Asset/Character/review/aonoma/forge_quantized/quantize-qa.json','status':'candidate_unreviewed', 'method':'estimated matte from near-gray 242 background; padded fixed canvas; alpha-aware BOX downscale to 90x72; Forge palette_tool quantize-seq; nearest 3x display, cropped to original frame canvas', 'limitations':'Matte and color quantization are lossy; pale detail, purple/red glows and VFX can be lost or saturated; source includes multiple poses/effects that are not classified. Needs visual review.'}
 write(OUT/'candidate.json',meta)
 # One numbered contact sheet, independent of existing review sheets.
 canvas=Image.new('RGB',(4*180,4*165),'#555');draw=ImageDraw.Draw(canvas);gif=Image.open(source)
 for i in range(gif.n_frames):
  gif.seek(i);im=gif.convert('RGBA');im.thumbnail((176,140),Image.Resampling.LANCZOS);x=(i%4)*180;y=(i//4)*165;canvas.paste(im,(x+(180-im.width)//2,y+20),im);draw.text((x+3,y+2),f'#{i}  {gif.info.get("duration",0)} ms',fill='white')
 canvas.save(REVIEW/'frames_0000_0013.jpg',quality=90);gif.close()
 catalog['assets'].append(entry);catalog['assets'].sort(key=lambda x:x['id'].lower());write(A/'extracted/catalog.json',catalog)
 roster['entries'].append({'source_id':'aonoma','provisional_character_name':'aonoma','source':entry['source'],'source_sha256':entry['source_sha256'],'identity_status':'name_from_filename_visual_review_needed','animations':{},'skill':{'status':'unreviewed','name':None,'provenance':None},'attack_range':'unreviewed','notes':'Nguồn do người dùng cung cấp; chưa phân đoạn động tác hoặc skill.'});write(A/'characters/roster.json',roster)
 inventory['sources'].append({'source':entry['source'],'sha256':entry['source_sha256'],'frames':entry['frame_count'],'review_sheets':['frames_0000_0013.jpg'],'status':'partially_reviewed','observations':[{'frames':[0,13],'observation':'Nhân vật màu tối đỏ tím, có những tư thế và hiệu ứng thay đổi; chưa xác nhận tên động tác hoặc skill.','evidence':'aonoma/frames_0000_0013.jpg'}],'characters':[]});write(A/'review/inventory.json',inventory)
 status['sources'].append({'id':'aonoma','status':'visual_review_pending','issue':'Bản pixel và tách nền là bản thử mất mát; kiểm tra viền, hiệu ứng, độ nhấp nháy và so với GIF nguồn.','variants':['pixel_candidates']});write(A/'review/background-review-status.json',status)
 index=A/'extracted/index.html';html=index.read_text(encoding='utf8');card='<article><h2>aonoma</h2><img loading="lazy" src="../vfx/aonoma.gif" alt="aonoma"><p>14 frames · 268 × 214 · chưa kiểm duyệt</p></article>\n';assert '</main></html>' in html;index.write_text(html.replace('</main></html>',card+'</main></html>'),encoding='utf8')
 print('Published aonoma source and pixel candidate; visual review pending')
if __name__=='__main__':main()
