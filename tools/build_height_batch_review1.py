#!/usr/bin/env python3
"""Pack first-frame measurements visually sampled for a small review batch."""
import json
from pathlib import Path
from PIL import Image
from build_measured_atlas_pilots import A, ROOT, OUT, pack, sha

# Source atlas, frame-0 alpha bbox, approximate shared contact anchor.
REVIEW = {
    'airpot': ('fine_candidates', [84,108,204,252], [144,252]),
    'black': ('native_candidates', [74,105,214,221], [170,221]),
    'bearen': ('batch_candidates', [84,135,216,252], [150,252]),
    'blackdog': ('batch_candidates', [53,124,146,189], [100,189]),
}

def main():
    catalog = {e['id']: e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
    target_path = A/'characters/height-targets.json'
    targets = json.loads(target_path.read_text())
    profiles = {e['id']: e for e in targets['assets']}
    for name in REVIEW:
        if (OUT/name).exists():
            raise FileExistsError(OUT/name)
    for name, (base, bounds, anchor) in REVIEW.items():
        entry = catalog[name]
        assert sha(ROOT/entry['source']) == entry['source_sha256']
        images, inputs = [], {}
        for frame in entry['frames']:
            path = A/base/name/f'atlas_{frame["atlas"]:03d}.png'
            relative = str(path.relative_to(ROOT))
            if relative not in inputs:
                inputs[relative] = sha(path)
            x, y, w, h = frame['region']
            with Image.open(path) as atlas:
                images.append(atlas.crop((x,y,x+w,y+h)).convert('RGBA'))
        assert list(images[0].getbbox()) == bounds
        height = bounds[3] - bounds[1]
        pack(name, images, [f['duration_ms'] for f in entry['frames']], profiles[name]['target_height_px'], height, anchor,
             {'source': entry['source'], 'source_sha256': entry['source_sha256'], 'input_atlas_sha256': inputs,
              'reference_alpha_bounds': bounds, 'review_note': 'Frame 0 visually sampled; alpha extent and approximate ground anchor require user review.'})
        profiles[name].update(reference_frame=0, reference_body_bounds=bounds,
                              scale=profiles[name]['target_height_px']/height,
                              status='measured_atlas_candidate_unreviewed',
                              measured_atlas_candidate=f'Asset/Character/measured_atlas_pilots/{name}/candidate.json')
        target_path.write_text(json.dumps(targets, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
