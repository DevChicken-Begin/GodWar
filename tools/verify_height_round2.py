#!/usr/bin/env python3
"""Check round-two targets, unchanged profiles, timing and atlas pixel files."""
import hashlib
import json
import math
from pathlib import Path
from update_height_targets_round3 import A, TARGET as TARGETS, sha
HISTORY = A/'characters/height-update-round2.json'

def main():
    history=json.loads(HISTORY.read_text());data=json.loads(TARGETS.read_text())
    entries={e['id']:e for e in data['assets']}
    assert len(history['proof'])==24
    frame_total=0; atlas_total=0
    for name,entry in entries.items():
        expected=entry['target_height_px']
        if name in history['changes']: assert expected==history['changes'][name]
        if name in history['unchanged_targets']: assert expected==history['unchanged_targets'][name]
        folder=A/'measured_atlas_pilots'/('crapit_main' if name=='crapit' else name)
        meta=json.loads((folder/'candidate.json').read_text())
        assert meta['target_height_px']==expected
        assert math.isclose(meta['display_scale']*meta['reference_height_px'],expected,rel_tol=1e-10)
        if name!='crapit': assert math.isclose(entry['scale'],meta['display_scale'],rel_tol=1e-10)
        if name not in history['proof']: continue
        proof=history['proof'][name]
        assert meta['frame_count']==proof['frame_count']==len(meta['frames'])
        timeline=hashlib.sha256(json.dumps(meta['frames'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert timeline==proof['frames_sha256']
        assert meta['reference_height_px']==proof['reference_height_px']
        for filename,digest in proof['atlas_sha256'].items():
            assert sha(folder/filename)==digest, (name,filename)
            atlas_total+=1
        frame_total+=meta['frame_count']
    for name,source in [('crapit_secondary','crapit'),('moxie_repaired','moxie')]:
        meta=json.loads((A/'measured_atlas_pilots'/name/'candidate.json').read_text())
        expected=40 if name=='crapit_secondary' else entries[source]['target_height_px']
        assert meta['target_height_px']==expected
        assert math.isclose(meta['display_scale']*meta['reference_height_px'],expected,rel_tol=1e-10)
        assert meta['size_target_approval']==entries[source]['size_target_approval']
    print(f'PASS: 24 historical frame proofs, {len(entries)} current targets, {frame_total} frames and {atlas_total} atlas files unchanged')

if __name__=='__main__':main()
