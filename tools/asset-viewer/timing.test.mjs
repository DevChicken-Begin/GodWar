import test from 'node:test';
import assert from 'node:assert/strict';
import { frameDuration } from './timing.mjs';

test('70 ms preview keeps source data unchanged and can return to source timing', () => {
  const frame = { duration_ms: 30 };
  assert.equal(frameDuration(frame, '60'), 60);
  assert.equal(frameDuration(frame, '70'), 70);
  assert.equal(frameDuration(frame, '130'), 130);
  assert.equal(frame.duration_ms, 30);
  assert.equal(frameDuration(frame, 'source'), 30);
  assert.equal(frameDuration({ duration_ms: 0 }, 'source'), 0.01);
  assert.equal(frameDuration({ duration_ms: 0.7 }, 'source'), 0.7);
});
