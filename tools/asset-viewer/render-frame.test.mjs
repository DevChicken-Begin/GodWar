import test from 'node:test';
import assert from 'node:assert/strict';
import { renderFrame } from './render-frame.mjs';

test('reuses the backing canvas, clears transparency, and flips when requested', () => {
  let width = 0, height = 0, resizes = 0;
  const canvas = {
    get width() { return width; }, set width(v) { width = v; resizes++; },
    get height() { return height; }, set height(v) { height = v; resizes++; },
  };
  const calls = [];
  const context = Object.fromEntries(['clearRect', 'save', 'translate', 'scale', 'drawImage', 'restore']
    .map(name => [name, (...args) => calls.push([name, ...args])]));
  const image = {};
  renderFrame(canvas, context, image, [10, 20, 720, 600], false);
  assert.equal(resizes, 2);
  assert.deepEqual(calls[0], ['clearRect', 0, 0, 720, 600]);
  assert.ok(calls.some(call => call[0] === 'drawImage' && call[1] === image && call[2] === 10));
  calls.length = 0;
  renderFrame(canvas, context, image, [0, 0, 720, 600], true);
  assert.equal(resizes, 2);
  assert.deepEqual(calls[0], ['clearRect', 0, 0, 720, 600]);
  assert.ok(calls.some(call => call[0] === 'translate' && call[1] === 720));
  assert.ok(calls.some(call => call[0] === 'scale' && call[1] === -1));
  renderFrame(canvas, context, image, [0, 0, 300, 300], false);
  assert.equal(resizes, 4);
});
