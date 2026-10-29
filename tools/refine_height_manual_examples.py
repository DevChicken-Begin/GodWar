#!/usr/bin/env python3
"""Record visually estimated body bounds for frames dominated by large effects."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'Asset/Character'
TARGET=A/'characters/height-targets.json'
HISTORY=A/'characters/height-manual-refinement-20261029.json'
# Approximate bounds from frame 0 on a 100-source-pixel grid, excluding obvious VFX/weapons.
BOUNDS={'aminao':[230,255,380,409], 'changlie':[230,350,480,624], 'costmic':[160,220,365,405]}

def write(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)

def main():
    if HISTORY.exists():raise FileExistsError(HISTORY)
    data=json.loads(TARGET.read_text());items={x['id']:x for x in data['assets']};plan=[]
    for name,box in BOUNDS.items():
        path=A/'measured_atlas_pilots'/name/'candidate.json';meta=json.loads(path.read_text());x,y,r,b=box
        assert 0 <= x < r <= meta['frame_size'][0] and 0 <= y < b <= meta['frame_size'][1]
        before={k:meta.get(k) for k in ('reference_height_px','display_scale','measurement_kind','reference_body_bounds')}
        meta['reference_body_bounds']=box;meta['reference_height_px']=b-y
        meta['display_scale']=meta['target_height_px']/(b-y)
        meta['measurement_kind']='visually_estimated_body_bounds'
        meta['body_measurement_note']='Approximate visible body bounds on frame 0; excludes obvious effects and weapon. Source pixels and animation are unchanged.'
        items[name]['reference_body_bounds']=box;items[name]['scale']=meta['display_scale']
        plan.append((path,meta,before))
    write(HISTORY,{'target_sha256_before':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'bounds':BOUNDS,
                   'method':'Visual estimates using source pixel grid, frame 0. Not a segmentation mask.',
                   'prior_values':{meta['id']:before for _,meta,before in plan}})
    for path,meta,_ in plan:write(path,meta)
    write(TARGET,data)
    print('Refined',len(plan),'body references; atlas pixels unchanged')

if __name__=='__main__':main()
