#!/usr/bin/env python3
"""Import the thirteen supplied GIFs and make reviewable native-size alpha candidates.

Run with the Sprite Forge venv Python. Source GIFs are copied, never modified.
"""
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from extract_gif_assets import extract

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
NAMES = ('aonime', 'buffoin', 'congpha', 'dragonot', 'hanko', 'kengkeng',
         'kungtailee', 'machinen', 'magma', 'swithin', 'trongit', 'vision', 'warrioram')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def background(frame):
    """Most common opaque border RGB, including GIFs with edge effects."""
    pixels = np.asarray(frame.convert('RGBA'))
    border = np.concatenate((pixels[0, :, :3], pixels[-1, :, :3],
                             pixels[1:-1, 0, :3], pixels[1:-1, -1, :3]))
    colors, counts = np.unique(border, axis=0, return_counts=True)
    return colors[counts.argmax()]


def key(frame, bg, multi_band=False):
    pixels = np.array(frame.convert('RGBA'))
    distance = np.max(np.abs(pixels[:, :, :3].astype(np.int16) - bg.astype(np.int16)), axis=2)
    # Exact and near-exact blue is background. Preserve all other colors,
    # especially dark character detail and cyan effects, for visual review.
    removed = (pixels[:, :, 3] > 0) & (distance <= 5)
    if multi_band:
        # dragonot uses several flat dark bands in one frame. Only consider
        # colors present on the border and covering >=0.5% of the canvas.
        rgb = pixels[:, :, :3]
        border = np.concatenate((rgb[0], rgb[-1], rgb[1:-1, 0], rgb[1:-1, -1]))
        colors, counts = np.unique(border, axis=0, return_counts=True)
        for color, border_count in zip(colors, counts):
            if border_count < 3 or not (color[0] <= 40 and color[1] <= 80 and color[2] <= 100):
                continue
            exact = np.all(rgb == color, axis=2)
            if exact.sum() >= rgb.shape[0] * rgb.shape[1] * 0.005:
                removed |= exact
    pixels[removed] = 0
    return Image.fromarray(pixels, 'RGBA'), int(removed.sum())


def main():
    paths = [ROOT / f'{name}.gif' for name in NAMES]
    catalog_path = ASSETS / 'extracted/catalog.json'
    roster_path = ASSETS / 'characters/roster.json'
    inventory_path = ASSETS / 'review/inventory.json'
    status_path = ASSETS / 'review/background-review-status.json'
    catalog, roster, inventory, status = map(read, (catalog_path, roster_path, inventory_path, status_path))
    existing = {item['id'] for item in catalog['assets']}
    for name, source in zip(NAMES, paths):
        if not source.is_file():
            raise FileNotFoundError(source)
        if name in existing or any((ASSETS / folder / name).exists() for folder in ('extracted', 'native_candidates', 'review')) or (ASSETS / 'vfx' / source.name).exists():
            raise FileExistsError(f'Already imported: {name}')

    for name, source in zip(NAMES, paths):
        dest = ASSETS / 'vfx' / source.name
        with source.open('rb') as src, dest.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        entry = extract(dest, ASSETS / 'extracted')
        assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
        output = ASSETS / 'native_candidates' / name
        output.mkdir()
        review_dir = ASSETS / 'review' / name
        review_dir.mkdir()
        page = None
        atlas = None
        bg_counts = {}
        removed_counts = []
        samples = sorted({round((entry['frame_count'] - 1) * k / 11) for k in range(12)})
        sheet = Image.new('RGB', (4 * 200, 3 * 205), '#333333')
        draw = ImageDraw.Draw(sheet)
        with Image.open(dest) as gif:
            for index, region in enumerate(entry['frames']):
                gif.seek(index)
                frame = gif.convert('RGBA')
                bg = background(frame)
                bg_key = ','.join(map(str, bg.tolist()))
                bg_counts[bg_key] = bg_counts.get(bg_key, 0) + 1
                keyed, count = key(frame, bg, multi_band=name == 'dragonot')
                removed_counts.append(count)
                if region['atlas'] != page:
                    if atlas is not None:
                        atlas.save(output / f'atlas_{page:03d}.png', compress_level=1)
                    page = region['atlas']
                    old = ASSETS / 'extracted' / name / f'atlas_{page:03d}.png'
                    with Image.open(old) as original:
                        atlas = Image.new('RGBA', original.size)
                x, y, _, _ = region['region']
                atlas.paste(keyed, (x, y))
                if index in samples:
                    slot = samples.index(index)
                    thumb = keyed.copy()
                    thumb.thumbnail((188, 174), Image.Resampling.LANCZOS)
                    sx, sy = slot % 4 * 200, slot // 4 * 205
                    sheet.paste(thumb, (sx + (200 - thumb.width) // 2, sy + 22), thumb)
                    draw.text((sx + 5, sy + 4), f'#{index}  {region["duration_ms"]} ms', fill='white')
        atlas.save(output / f'atlas_{page:03d}.png', compress_level=1)
        sheet.save(review_dir / 'sample-keyed.jpg', quality=92)
        write(output / 'candidate.json', {
            'source': entry['source'], 'source_sha256': entry['source_sha256'],
            'art_source': 'existing', 'method': 'Decode GIF at source resolution; per-frame modal border RGB; clear pixels with max RGB distance <= 5; dragonot additionally clears dominant flat dark border colors covering >=0.5% of frame; preserve source timing.',
            'background_rgb_frame_counts': bg_counts, 'frame_count': entry['frame_count'],
            'frames': entry['frames'], 'removed_per_frame': removed_counts,
            'status': 'candidate_unreviewed',
            'limitations': 'Dark detail near the blue background can disappear; near-blue fringe, lettering or scene elements can remain. Inspect all frames over light and dark backdrops.'
        })
        catalog['assets'].append(entry)
        roster['entries'].append({
            'source_id': name, 'provisional_character_name': name, 'source': entry['source'],
            'source_sha256': entry['source_sha256'], 'identity_status': 'name_from_filename_visual_review_needed',
            'animations': {}, 'skill': {'status': 'unreviewed', 'name': None, 'provenance': None},
            'attack_range': 'unreviewed', 'notes': 'GIF nguồn đã tách frame và thử tách nền; chưa xác nhận danh tính, phân đoạn động tác hay skill.'
        })
        inventory['sources'].append({
            'source': entry['source'], 'sha256': entry['source_sha256'], 'frames': entry['frame_count'],
            'review_sheets': ['sample-keyed.jpg'], 'status': 'unreviewed', 'observations': [], 'characters': []
        })
        status['sources'].append({
            'id': name, 'status': 'visual_review_pending',
            'issue': 'Bản tách nền nguyên kích thước chưa duyệt; có thể mất chi tiết tối gần màu nền hoặc còn viền xanh.',
            'variants': ['native_candidates']
        })
        print(f'{name}: {entry["frame_count"]} frames, {entry["size"]}, {bg_counts}', flush=True)
    catalog['assets'].sort(key=lambda item: item['id'].lower())
    for path, value in ((catalog_path, catalog), (roster_path, roster), (inventory_path, inventory), (status_path, status)):
        write(path, value)


if __name__ == '__main__':
    main()
