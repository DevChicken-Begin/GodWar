import test from 'node:test';
import assert from 'node:assert/strict';
import { createAssetServer } from './server.mjs';

test('candidate timelines switch frame counts and restore the original timeline', async (t) => {
  const server = createAssetServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  const nativeFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = nativeFetch; });
  globalThis.fetch = (url, ...rest) => nativeFetch(new URL(url, origin), ...rest);
  globalThis.requestAnimationFrame = () => 0;
  globalThis.Option = class { constructor(text, value) { this.textContent = text; this.value = value; } };
  globalThis.Image = class {
    set src(value) { this.width = 2048; this.height = 2048; queueMicrotask(() => this.onload()); }
    async decode() {}
  };
  class Element {
    constructor(id) { this.id = id; this.value = ''; this.children = []; this.events = {}; this.style = {}; this.className = ''; }
    addEventListener(name, callback) { this.events[name] = callback; }
    setAttribute() {}
    replaceChildren(...children) { this.children = children; if (this.id === 'variant' && children.length) this.value = children[0].value; }
    append(child) { this.children.push(child); }
    add(child) { this.children.push(child); }
    getContext() { return { clearRect() {}, save() {}, restore() {}, translate() {}, scale() {}, drawImage() {} }; }
  }
  const elements = new Map();
  globalThis.document = {
    getElementById(id) { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); },
    createElement() { return new Element(''); },
  };
  for (const [id, value] of [['speed', '1'], ['zoom', '1'], ['timing', 'source']]) document.getElementById(id).value = value;
  await import('./app.js');
  const el = (id) => document.getElementById(id);
  for (let i = 0; i < 100 && !el('asset-list').children.length; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.ok(el('asset-list').children.length, 'catalog loaded');
  function select(name) {
    el('search').value = name;
    el('search').events.input();
    const button = el('asset-list').children.find((x) => x.textContent === name);
    assert.ok(button, name);
    button.events.click();
  }
  for (const [name, last] of [['Trex', '48'], ['ethan', '71'], ['jaying', '20']]) {
    select(name);
    assert.equal(el('variant').value, 'batch12_detail_candidates');
    assert.equal(el('frame').max, last);
    assert.ok(el('variant').children.some((option) => option.value === 'batch12_native_candidates'));
  }
  for (const [name, last] of [['momo', '57'], ['shellhost', '40']]) {
    select(name);
    assert.equal(el('variant').value, 'revision_candidates');
    await el('variant').events.change();
    assert.match(el('asset-info').textContent, name === 'momo' ? /506 × 506/ : /520 × 520/);
    for (let i = 0; i < 100 && el('canvas').style.width !== (name === 'momo' ? '506px' : '520px'); i++) await new Promise((resolve) => setTimeout(resolve, 20));
    assert.equal(el('canvas').style.width, name === 'momo' ? '506px' : '520px');
    el('variant').value = 'scene_spot_candidates';
    await el('variant').events.change();
    assert.match(el('asset-info').textContent, name === 'momo' ? /440 × 440/ : /520 × 520/);
    assert.ok(el('variant').children.some((option) => option.value === 'scene_mask_candidates'));
    assert.equal(el('frame').max, last);
    assert.ok(el('variant').children.some((option) => option.value === 'batch12_detail_candidates'));
  }
  select('conden');
  for (let i = 0; i < 100 && el('frame').max !== '60'; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(el('variant').value, 'tune_60fps_candidates');
  assert.equal(el('frame').max, '60');
  el('variant').value = 'speed_60fps_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '56');
  el('variant').value = 'detail_oct28_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '52');
  assert.match(el('asset-info').textContent, /960 × 720/);
  el('variant').value = 'repaired_v5_candidates';
  await el('variant').events.change();
  assert.equal(el('variant').value, 'repaired_v5_candidates');
  assert.equal(el('frame').max, '55');
  select('firer');
  for (let i = 0; i < 100 && el('variant').value !== 'tune_60fps_candidates'; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  await el('variant').events.change();
  assert.equal(el('duration-label').textContent, '66.67 ms');
  el('variant').value = 'speed_60fps_candidates';
  await el('variant').events.change();
  assert.equal(el('duration-label').textContent, '50 ms');
  el('variant').value = 'speed_oct28_candidates';
  await el('variant').events.change();
  assert.equal(el('duration-label').textContent, '26 ms');
  select('moxie');
  el('variant').value = 'repaired_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '96');
  assert.match(el('asset-info').textContent, /340 × 250/);
  el('variant').value = 'batch_candidates';
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /300 × 250/);
  select('blacktiger');
  el('variant').value = 'motion_v2_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '51');
  el('variant').value = 'special_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '25');
});
