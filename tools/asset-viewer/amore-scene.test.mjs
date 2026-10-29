import test from 'node:test';
import assert from 'node:assert/strict';
import { createAssetServer } from './server.mjs';

test('scene starts animation and constrains movement to the platform', async (t) => {
  const server = createAssetServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  const realFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = realFetch; });
  globalThis.fetch = (url, ...args) => realFetch(new URL(url, origin), ...args);
  let tick;
  globalThis.requestAnimationFrame = (fn) => { tick = fn; };
  globalThis.Image = class { set src(value) { this.url = value; queueMicrotask(() => this.onload()); } };
  globalThis.Option = class { constructor(text, value) { this.textContent = text; this.value = value; } };
  const draws = [];
  const ctx = { fillRect() {}, drawImage(...args) { draws.push(args); } };
  class Element {
    constructor(id) { this.id = id; this.events = {}; this.dataset = {}; this.value = id === 'speed' ? '1' : id === 'world-zoom' ? '0.7' : id === 'fit-mode' ? 'expand' : ''; this.checked = id === 'six'; }
    getContext() { return ctx; }
    addEventListener(name, fn) { this.events[name] = fn; }
    setPointerCapture() {}
    replaceChildren(...children) { this.children = children; }
  }
  const elements = new Map();
  globalThis.document = { getElementById(id) { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); } };
  globalThis.window = { addEventListener() {} };
  await import('./amore-scene.js');
  for (let i = 0; i < 100 && !tick; i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(tick, 'scene loaded');
  const choices = elements.get('character').children.map((option) => option.value);
  assert.ok(choices.includes('moxie_repaired'));
  assert.ok(!choices.includes('moxie'));
  assert.ok(choices.includes('crapit_main') && choices.includes('crapit_secondary'));
  let entered = false, exited = false;
  elements.get('scene-container').requestFullscreen = async () => { entered = true; document.fullscreenElement = elements.get('scene-container'); };
  document.exitFullscreen = async () => { exited = true; document.fullscreenElement = null; };
  await elements.get('fullscreen').events.click();
  assert.ok(entered);
  assert.match(elements.get('fullscreen-status').textContent, /Đang xem toàn màn hình/);
  assert.equal(elements.get('phone-view').dataset.fit, 'expand');
  assert.equal(elements.get('scene').width, 2401);
  elements.get('fullscreen-fit').events.click();
  assert.equal(elements.get('phone-view').dataset.fit, 'contain');
  assert.equal(elements.get('scene').width, 1920);
  elements.get('fullscreen-fit').events.click();
  assert.equal(elements.get('phone-view').dataset.fit, 'cover');
  assert.match(elements.get('fit-status').textContent, /108 px/);
  elements.get('fullscreen-fit').events.click();
  assert.equal(elements.get('phone-view').dataset.fit, 'expand');
  assert.equal(elements.get('scene').width, 2401);
  await elements.get('exit-fullscreen').events.click();
  assert.ok(exited);
  tick(0);
  assert.equal(draws.length, 7, 'map and six sample characters are drawn');
  const first = draws.at(-1);
  assert.equal(first[3], 240);
  assert.ok(Math.abs(first[8] * 94 / 240 - 80) < 0.01, 'default visible height is 80 pixels');
  const right = elements.get('right');
  right.events.pointerdown({ preventDefault() {}, pointerId: 1 });
  tick(100);
  const moved = draws.at(-1);
  assert.ok(moved[5] > first[5]);
  assert.notEqual(moved[1], first[1], 'animation frame advances');
  for (let i = 2; i < 100; i++) tick(i * 100);
  const last = draws.at(-1);
  const footX = last[5] + 126 * 80 / 94;
  const mapScale = 1920 / 512 * 0.7;
  const mapX = (2401 - 512 * mapScale) / 2;
  const mapY = (1080 - 352 * mapScale) / 2;
  assert.ok(footX <= mapX + 245 * mapScale + 0.01);
  assert.ok(Math.abs(last[6] + 208 * 80 / 94 - (mapY + 194 * mapScale)) < 0.01);
  right.events.pointerup();
  elements.get('world-zoom').value = '1';
  elements.get('six').checked = false;
  const count = draws.length;
  tick(10000);
  assert.equal(draws.length - count, 2, 'map and one character when comparison is off');
  assert.ok(Math.abs(draws.at(-1)[8] - 240 * 80 / 94 / 0.7) < 0.01, 'zoom scales character with map');
  elements.get('world-zoom').value = '0.7';
  await elements.get('character').events.change({ target: { value: 'agon' } });
  tick(10016);
  assert.match(elements.get('status').textContent, /90 px/);
  assert.ok(Math.abs(draws.at(-1)[8] * 220 / 400 - 90) < 0.01, 'Agon uses the measured body scale');
  await elements.get('character').events.change({ target: { value: 'airpot' } });
  tick(10032);
  assert.match(elements.get('status').textContent, /80 px/);
  assert.ok(Math.abs(draws.at(-1)[8] * 144 / 300 - 80) < 0.01, 'scene and viewer share the Airpot display scale');
  await elements.get('character').events.change({ target: { value: 'aminao' } });
  tick(10048);
  assert.match(elements.get('status').textContent, /70 px/);
  assert.ok(Math.abs(draws.at(-1)[8] * 154 / 560 - 70) < 0.01, 'round-two height is applied at scene zoom 70%');
  const wrappedFetch = globalThis.fetch;
  const targets = await (await wrappedFetch('/Asset/Character/characters/height-targets.json')).json();
  targets.assets.find((item) => item.id === 'aminao').target_height_px = 71;
  globalThis.fetch = (url, ...args) => String(url).endsWith('/height-targets.json')
    ? Promise.resolve(new Response(JSON.stringify(targets), { status: 200 }))
    : wrappedFetch(url, ...args);
  await elements.get('refresh-size').events.click();
  globalThis.fetch = wrappedFetch;
  tick(10080);
  assert.match(elements.get('status').textContent, /kích thước hiện hành: 71 px/);
  assert.match(elements.get('size-feedback').textContent, /Đã cập nhật aminao: 71 px/);
  assert.ok(Math.abs(draws.at(-1)[8] * 154 / 560 - 71) < 0.01, 'refresh uses new metadata without reloading the scene');
  await elements.get('character').events.change({ target: { value: 'Kahn' } });
  tick(10096);
  assert.match(elements.get('status').textContent, /87 px/);
  assert.ok(Math.abs(draws.at(-1)[8] * 211 / 360 - 87) < 0.01, 'Kahn uses the round-three scale on the scene');
  await elements.get('character').events.change({ target: { value: 'momo' } });
  tick(10112);
  assert.match(elements.get('status').textContent, /85 px/);
  assert.ok(Math.abs(draws.at(-1)[8] * 408 / 948 - 85) < 0.01, 'momo uses the round-three scale on the scene');
  for (const [name, height] of [['scorpit', 80], ['Hatomin', 80], ['Trainxoan', 85]]) {
    await elements.get('character').events.change({ target: { value: name } });
    tick(10128);
    assert.match(elements.get('status').textContent, new RegExp(`kích thước hiện hành: ${height} px`));
    const meta = await (await globalThis.fetch(`/Asset/Character/measured_atlas_pilots/${name}/candidate.json`)).json();
    assert.ok(Math.abs(draws.at(-1)[8] * meta.reference_height_px / meta.frame_size[1] - height) < 0.01, `${name} scene scale`);
  }
});
