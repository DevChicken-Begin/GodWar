#!/usr/bin/env python3
"""Make viewer metadata for the exported SpriteFrames, verifying each atlas cell."""
import json
import re
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
PILOT = A / 'forge_pilots/dragonot_reference_v1/godot_export'
GODOT = PILOT / 'godot'


def main():
    output = GODOT / 'preview.json'
    if output.exists():
        raise FileExistsError(output)
    text = (GODOT / 'godot_export.tres').read_text()
    regions = {key: list(map(int, values.split(', '))) for key, values in re.findall(
        r'\[sub_resource type="AtlasTexture" id="([^"]+)"\]\natlas = .*?\nregion = Rect2\(([^)]+)\)', text)}
    ids = re.findall(r'"texture": SubResource\("([^"]+)"\)', text)
    clip = json.loads((PILOT / 'engine-export.json').read_text())['clips']['reference_unclassified']
    assert len(ids) == len(clip['duration_ms']) == 49
    frames = []
    with Image.open(GODOT / 'godot_export-atlas-00.png') as atlas:
        for index, key in enumerate(ids):
            x, y, w, h = regions[key]
            with Image.open(A / 'revision_candidates/dragonot' / f'frame_{index:03d}.png') as source:
                diff = ImageChops.difference(atlas.crop((x, y, x+w, y+h)).convert('RGBA'), source.convert('RGBA'))
                assert diff.getbbox(alpha_only=False) is None, index
            frames.append({'atlas': 0, 'region': [x, y, w, h], 'duration_ms': clip['duration_ms'][index]})
    data = {'id': 'dragonot', 'frames': frames, 'display_size': [384, 384],
            'source': 'Godot SpriteFrames atlas', 'note': 'reference_unclassified'}
    output.write_text(json.dumps(data, indent=2) + '\n')
    print('PASS 49 atlas cells and source frames match')


if __name__ == '__main__':
    main()
