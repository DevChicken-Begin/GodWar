import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveHeightProfile } from './height-profile.mjs';

test('current target overrides stale atlas metadata and aliases use the right part', () => {
  const targets = new Map([
    ['aminao', { id: 'aminao', source_sha256: 'a', target_height_px: 70 }],
    ['crapit', { id: 'crapit', source_sha256: 'b', target_height_px: 100, parts: [{ target_height_px: 100 }, { target_height_px: 40 }] }],
    ['conden', { id: 'conden', source_sha256: 'c', target_height_px: 65 }],
  ]);
  const body = resolveHeightProfile({ id: 'aminao', source_sha256: 'a', target_height_px: 75, display_scale: 0.9, reference_height_px: 140 }, targets);
  assert.equal(body.target_height_px, 70);
  assert.equal(body.display_scale, 0.5);
  assert.equal(resolveHeightProfile({ id: 'crapit_secondary', source_sha256: 'b', reference_height_px: 80 }, targets).display_scale, 0.5);
  assert.equal(resolveHeightProfile({ id: 'conden', source_sha256: 'c', reference_height_px: 130 }, targets).display_scale, 0.5);
  assert.throws(() => resolveHeightProfile({ id: 'aminao', source_sha256: 'wrong', reference_height_px: 140 }, targets));
});
