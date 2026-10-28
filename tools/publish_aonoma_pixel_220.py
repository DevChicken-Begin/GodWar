#!/usr/bin/env python3
"""Build a non-destructive 198x158 Aonoma preview atlas."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';R=A/'review/aonoma';out=A/'pixel_220_candidates/aonoma';e=json.loads((R/'extraction-entry.json').read_text());src=ROOT/e['source'];qa=json.loads((R/'forge_quantized_220/quantize-qa.json').read_text())
if out.exists():raise FileExistsError(out)
assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256'] and qa['status']=='pass' and len(qa['frames'])==e['frame_count']
out.mkdir(parents=True);page=-1;atlas=None
for i,f in enumerate(e['frames']):
 if page!=f['atlas']:
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
  page=f['atlas'];old=Image.open(A/'extracted/aonoma'/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',old.size);old.close()
 with Image.open(R/'forge_quantized_220'/f'frame_{i:03d}.png') as im:
  p=im.convert('RGBA').resize(tuple(e['size']),Image.Resampling.NEAREST);x,y,w,h=f['region'];assert p.size==(w,h);atlas.paste(p,(x,y))
if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
m={'source':e['source'],'source_sha256':e['source_sha256'],'art_source':'existing','frame_count':e['frame_count'],'frames':e['frames'],'logical_canvas':[198,158],'previous_canvas':[162,129],'palette_colors':128,'palette':'Asset/Character/review/aonoma/forge_quantized_220/palette.json','qa':'Asset/Character/review/aonoma/forge_quantized_220/quantize-qa.json','status':'candidate_unreviewed','method':'Source matte estimate and BOX reduction to 198x158, Forge quantize-seq 128 colors and no orphan removal; nearest-neighbor viewer preview on 268x214 canvas.','limitations':'Lossy matte and palette can alter VFX, saturation or edges; source actions remain unclassified and mobile performance is unmeasured.'}
(out/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('published 198x158 candidate for',e['frame_count'],'frames')
