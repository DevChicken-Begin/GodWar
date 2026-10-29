#!/usr/bin/env python3
"""Keep Moxie's previously expanded projectile canvas in a height preview."""
import json
from pathlib import Path
from PIL import Image
from build_measured_atlas_pilots import A, ROOT, OUT, pack, sha

def main():
    folder = A/'repaired_candidates/moxie'
    base = json.loads((folder/'candidate.json').read_text())
    targets = json.loads((A/'characters/height-targets.json').read_text())
    target = next(x for x in targets['assets'] if x['id'] == 'moxie')
    assert sha(ROOT/base['source']) == base['source_sha256'] == target['source_sha256']
    images, inputs = [], {}
    for frame in base['frames']:
        path = folder/f'atlas_{frame["atlas"]:03d}.png'
        key = str(path.relative_to(ROOT))
        if key not in inputs: inputs[key] = sha(path)
        x,y,w,h = frame['region']
        with Image.open(path) as atlas: images.append(atlas.crop((x,y,x+w,y+h)).convert('RGBA'))
    bbox = images[0].getbbox()
    assert bbox is not None
    left,top,right,bottom = bbox
    pack('moxie_repaired', images, [f['duration_ms'] for f in base['frames']], target['target_height_px'], bottom-top,
         [(left+right)/2,bottom], {'source':base['source'], 'source_sha256':base['source_sha256'],
         'input_candidate':'repaired_candidates/moxie', 'input_atlas_sha256':inputs,
         'measurement_kind':'automatic_alpha_bbox_unreviewed', 'reference_alpha_bounds':list(bbox)})
    path=OUT/'moxie_repaired'/'candidate.json'
    meta=json.loads(path.read_text());meta['limitations'] += ' Projectile pixels are reconstructed in the input candidate; alpha bounds and anchor remain unreviewed.'
    path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__': main()
