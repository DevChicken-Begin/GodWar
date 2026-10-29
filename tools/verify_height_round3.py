#!/usr/bin/env python3
"""Verify the third-round targets and unchanged atlas and timeline evidence."""
import hashlib
import json
import math
from update_height_targets_round3 import A, TARGET, HISTORY, sha

EXPECTED={'Kahn':87,'choptian':90,'comic':85,'congpha':85,'corepion':65,'costmic':75,
          'dracian':95,'dragonight':100,'dragonot':100,'firemen':70,'hades':110,
          'iternal':90,'jaik':85,'kengkeng':90,'kumen':80,'kungchang':85,
          'midnight':80,'momo':85,'nox':87,'omra':80}

def main():
    history=json.loads(HISTORY.read_text());data=json.loads(TARGET.read_text())
    entries={e['id']:e for e in data['assets']}
    assert history['changes']==EXPECTED and len(history['unchanged_targets'])==123
    original_ids=set(EXPECTED) | set(history['unchanged_targets'])
    assert len(original_ids)==143 and original_ids <= entries.keys()
    frames_total=pages_total=0
    for name in original_ids:
        entry=entries[name]
        expected=EXPECTED[name] if name in EXPECTED else history['unchanged_targets'][name]
        assert entry['target_height_px']==expected
        if name in EXPECTED:assert entry['size_target_approval']=='user_updated_round3'
        folder=A/'measured_atlas_pilots'/('crapit_main' if name=='crapit' else name)
        meta=json.loads((folder/'candidate.json').read_text())
        assert meta['target_height_px']==expected
        assert math.isclose(meta['display_scale']*meta['reference_height_px'],expected,rel_tol=1e-10)
        assert meta['size_target_approval']==entry['size_target_approval']
        if name!='crapit':assert math.isclose(entry['scale'],meta['display_scale'],rel_tol=1e-10)
        if name not in EXPECTED:continue
        proof=history['proof'][name]
        assert proof['target_height_px']==expected and proof['reference_height_px']==meta['reference_height_px']
        assert proof['frame_count']==meta['frame_count']==len(meta['frames'])
        timeline=hashlib.sha256(json.dumps(meta['frames'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert timeline==proof['frames_sha256']
        for filename,digest in proof['atlas_sha256'].items():
            assert sha(folder/filename)==digest,(name,filename)
            pages_total+=1
        frames_total+=len(meta['frames'])
    for name,source in [('crapit_secondary','crapit'),('moxie_repaired','moxie')]:
        m=json.loads((A/'measured_atlas_pilots'/name/'candidate.json').read_text())
        height=40 if name=='crapit_secondary' else entries[source]['target_height_px']
        assert m['target_height_px']==height and math.isclose(m['display_scale']*m['reference_height_px'],height,rel_tol=1e-10)
        assert m['size_target_approval']==entries[source]['size_target_approval']
    print(f'PASS: 20 replacements, 123 unchanged, 143 original profiles, {frames_total} frames and {pages_total} atlas files unchanged')

if __name__=='__main__':main()
