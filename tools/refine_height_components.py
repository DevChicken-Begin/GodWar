#!/usr/bin/env python3
"""Remove detached alpha noise from reviewed reference measurements, not pixels."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/'Asset/Character'
TARGETS = A/'characters/height-targets.json'
HISTORY = A/'characters/height-component-refinement-20261029.json'
# Largest components visually inspected on frame 0; [x, y, width, height].
BOXES = {
    'aumen':[90,100,82,98], 'aurora':[156,216,246,276], 'authen':[196,186,149,246],
    'choptian':[55,103,142,147], 'comic':[199,193,238,332], 'congpha':[187,257,359,399],
    'corepion':[118,219,163,84], 'dracian':[111,183,210,185], 'dragonight':[103,159,254,261],
    'hades':[46,28,120,140], 'javis':[117,126,72,120], 'jaying':[80,155,130,108],
    'kengkeng':[296,382,367,508], 'kukang':[198,306,468,366], 'magicleo':[165,198,117,174],
    'oxiu':[132,156,208,260], 'pygon':[216,384,210,180], 'skypit':[101,117,226,234],
    'swithin':[80,98,108,123], 'tailer':[270,258,186,366], 'warrioram':[140,332,396,266],
}

def write(path, value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)

def main():
    if HISTORY.exists(): raise FileExistsError(HISTORY)
    targets=json.loads(TARGETS.read_text()); by_id={x['id']:x for x in targets['assets']}
    plan=[]
    for name, box in BOXES.items():
        path=A/'measured_atlas_pilots'/name/'candidate.json';data=json.loads(path.read_text())
        f=data['frames'][0];x,y,w,h=f['region']
        with Image.open(path.parent/f'atlas_{f["atlas"]:03d}.png') as atlas:
            alpha=np.asarray(atlas.crop((x,y,x+w,y+h)).convert('RGBA'))[:,:,3]
        count,_,stats,_=cv2.connectedComponentsWithStats((alpha>=32).astype('uint8'),8)
        assert count>1
        best=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))
        assert list(map(int,stats[best,:4]))==box, name
        left,top,width,height=box
        before={k:data.get(k) for k in ('reference_height_px','display_scale','measurement_kind','reference_body_bounds')}
        data['reference_height_px']=height
        data['reference_body_bounds']=[left,top,left+width,top+height]
        data['display_scale']=data['target_height_px']/height
        data['measurement_kind']='visually_inspected_component_unreviewed'
        data['body_measurement_note']='Frame 0 largest connected foreground component checked visually; attached VFX may remain, and detached details may be excluded.'
        entry=by_id[name]
        assert entry['target_height_px']==data['target_height_px']
        entry['reference_body_bounds']=data['reference_body_bounds']
        entry['scale']=data['display_scale']
        plan.append((path,data,before))
    history={'target_file_sha256_before':hashlib.sha256(TARGETS.read_bytes()).hexdigest(),
             'method':'Largest alpha>=32 connected component, frame 0; visually inspected sample sheet; measurements are approximate, no pixels changed.',
             'prior_values':{data['id']:before for _,data,before in plan},'boxes':BOXES}
    write(HISTORY,history)
    for path,data,_ in plan:write(path,data)
    write(TARGETS,targets)
    print('Refined',len(plan),'reference bounds; target heights and atlas pixels unchanged')

if __name__=='__main__':main()
