#!/usr/bin/env python3
"""Inventory displayed candidates and sample their exact integral pixel grids."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';REPORT=ROOT/'docs/fine-batch/audit.json'
# Same precedence as the viewer before creating the new fine candidates.
PRIORITY=('pixel_220_candidates','sharp_candidates','scorpit_repair18_candidates','logo_candidates','scene_protected_candidates','pixel_180_candidates','scorpit_repair_candidates','pixel_120_candidates','native_candidates','oct28_fix_candidates','pixel_candidates','spot_candidates','remaining_scene_candidates','scene_detail_v3_candidates','foot_candidates','detailed_candidates','special_candidates','shared_scene_candidates','temporal_candidates','batch_candidates','refined_candidates','candidates')
EXCLUDED={'agon','airpot','amore','aoda'}
def main():
 if REPORT.exists():raise FileExistsError(REPORT)
 catalog=json.loads((A/'extracted/catalog.json').read_text())['assets'];splits=json.loads((A/'extracted/split-catalog.json').read_text())['assets'];removed=set(json.loads((A/'characters/removed.json').read_text())['ids']);entries=[x for x in catalog+splits if x['id'] not in removed];result=[]
 for entry in entries:
  name=entry['id'];src=ROOT/entry['source'];row={'id':name,'source':entry['source'],'source_sha256':entry['source_sha256'],'frame_count':entry['frame_count'],'size':entry['size']}
  if name in EXCLUDED:row['status']='excluded_already_requested';result.append(row);continue
  if (A/'fine_candidates'/name).exists() or (A/'review'/name/'fine_frames').exists():row['status']='existing_output_preserved';result.append(row);continue
  if not src.is_file() or hashlib.sha256(src.read_bytes()).hexdigest()!=entry['source_sha256']:row['status']='source_missing_or_hash_mismatch';result.append(row);continue
  base=next((x for x in PRIORITY if (A/x/name/'candidate.json').exists()),None)
  # Current viewer has a special cleanup candidate preference for aminao.
  if name=='aminao' and (A/'cleanup_candidates'/name/'candidate.json').exists():base='cleanup_candidates'
  base=base or 'extracted';row['base_candidate']=base
  if base!='extracted':
   meta=json.loads((A/base/name/'candidate.json').read_text())
   if meta.get('source_sha256')!=entry['source_sha256']:row['status']='candidate_hash_mismatch';result.append(row);continue
  w,h=entry['size'];periods=[n for n in range(min(32,math.gcd(w,h)),1,-1) if w%n==0 and h%n==0];samples=sorted({0,len(entry['frames'])//2,len(entry['frames'])-1});valid=periods[:]
  try:
   for i in samples:
    f=entry['frames'][i];x,y,w,h=f['region']
    with Image.open(A/base/name/f'atlas_{f["atlas"]:03d}.png') as im:p=np.asarray(im.convert('RGBA').crop((x,y,x+w,y+h)))
    keep=[]
    for period in valid:
     cells=p.reshape(h//period,period,w//period,period,4);small=cells[:,0,:,0,:]
     if np.all(cells==small[:,None,:,None,:]):keep.append(period)
    valid=keep
    if not valid:break
   row.update({'status':'sampled_grid' if valid else 'no_exact_grid_in_samples','periods':valid,'sample_frames':samples})
  except (OSError,ValueError,KeyError) as exc:row.update({'status':'sample_failed','error':str(exc)})
  result.append(row);print(name,row['status'],row.get('periods',[])[:3],flush=True)
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps({'version':1,'method':'Match selected viewer baseline; exact uniform square cells on first, middle and last frames; complete frame check required before publication.','excluded':sorted(EXCLUDED),'results':result},ensure_ascii=False,indent=2)+'\n')
 from collections import Counter
 print('SUMMARY',dict(Counter(r['status'] for r in result)),flush=True)
if __name__=='__main__':main()
