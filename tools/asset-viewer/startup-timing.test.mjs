import test from 'node:test';
import assert from 'node:assert/strict';
import { createAssetServer } from './server.mjs';

test('playback clock waits for the first image before advancing', async (t) => {
  const server = createAssetServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  const realFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = realFetch; });
  globalThis.fetch = (url, ...rest) => realFetch(new URL(url, origin), ...rest);
  let nextTick;
  globalThis.requestAnimationFrame = (callback) => { nextTick = callback; };
  const images = [];
  globalThis.Image = class {
    set src(value) { this.width = 2048; this.height = 2048; images.push(this); }
    async decode() {}
  };
  globalThis.Option = class { constructor(text, value) { this.textContent = text; this.value = value; } };
  class Element {
    constructor(id) { this.id = id; this.value = ''; this.children = []; this.events = {}; this.style = {}; }
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
  globalThis.window = { addEventListener() {} };
  for (const [id, value] of [['speed', '1'], ['zoom', '1'], ['timing', 'source']]) document.getElementById(id).value = value;
  await import('./app.js');
  for (let i = 0; i < 100 && !images.length; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.ok(images.length, 'first frame requested');
  nextTick(0); nextTick(2000);
  assert.match(document.getElementById('frame-label').textContent, /Frame 1 \/ /);
  images[0].onload();
  await new Promise((resolve) => setTimeout(resolve, 0));
  nextTick(2016); nextTick(2032);
  assert.match(document.getElementById('frame-label').textContent, /Frame 1 \/ /);
  nextTick(2100);
  assert.doesNotMatch(document.getElementById('frame-label').textContent, /Frame 1 \/ /);
});
