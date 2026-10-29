#!/usr/bin/env python3
"""Remove obsolete target values while retaining frame/atlas provenance."""
import json
from pathlib import Path

A=Path(__file__).resolve().parents[1]/'Asset/Character/characters'
latest=json.loads((A/'height-update-round3.json').read_text())['changes']
targets={e['id']:e for e in json.loads((A/'height-targets.json').read_text())['assets']}
assert len(latest)==20 and all(targets[n]['target_height_px']==v for n,v in latest.items())
path=A/'height-update-round2.json';history=json.loads(path.read_text())
for name in latest:
    history['changes'].pop(name,None)
    history['unchanged_targets'].pop(name,None)
    proof=history['proof'].get(name,{})
    proof.pop('new_height_px',None);proof.pop('new_scale',None)
history['superseded_by_round3']=sorted(latest)
history['note']='Earlier targets for IDs changed in round 3 were removed; original frame/atlas hash evidence remains.'
path.write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
for filename in ('height-update-20261029.json','height-component-refinement-20261029.json','height-manual-refinement-20261029.json'):
    path=A/filename
    if not path.exists():continue
    old=json.loads(path.read_text())
    for name in latest:
        old.get('requested_changes',{}).pop(name,None)
        prior=old.get('prior_values',{}).get(name)
        if prior:
            for key in ('target_height_px','display_scale','reference_height_px','reference_body_bounds'):
                prior.pop(key,None)
    old['superseded_values']='Earlier target and scale values for changed IDs removed at user request.'
    path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
print('Removed superseded target values for',len(latest),'characters; retained hash evidence')
