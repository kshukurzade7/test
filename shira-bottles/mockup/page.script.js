import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const stage = document.getElementById('stage');
const statusEl = document.getElementById('status');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const SANS = "'Montserrat', 'Helvetica Neue', Arial, sans-serif";

const FLAVOURS = [
  { key: 'apricot', label: 'apricot-wrap.png', accent: '#D96A12', juice: '#E2780F', density: 0.55, cloudy: 0.5, x: -7.8, z: 0.8, yaw: 0.12 },
  { key: 'pomegranate', label: 'pomegranate-wrap.png', accent: '#A8172C', juice: '#B00E2C', density: 2.4, cloudy: 0, x: 0, z: -0.8, yaw: 0 },
  { key: 'grape', label: 'grape-wrap.png', accent: '#5B2453', juice: '#7A2A72', density: 3.6, cloudy: 0, x: 7.8, z: 0.8, yaw: -0.12 },
];

// SHIRÁ citrus mark: a disc with eight cream spokes and a cream centre
function citrusMark(g, x, y, r, fill, cut) {
  // citrus slice: solid disc, eight segments split by thin lines through the centre, light centre
  g.save(); g.translate(x, y);
  g.fillStyle = fill; g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.fill();
  g.strokeStyle = cut; g.lineWidth = r * 0.075;
  for (let k = 0; k < 4; k++) {
    const a = k * Math.PI / 4;
    g.beginPath(); g.moveTo(-Math.cos(a) * r * 1.05, -Math.sin(a) * r * 1.05); g.lineTo(Math.cos(a) * r * 1.05, Math.sin(a) * r * 1.05); g.stroke();
  }
  g.fillStyle = cut; g.beginPath(); g.arc(0, 0, r * 0.3, 0, Math.PI * 2); g.fill();
  g.restore();
}

function collarCanvas(accent) {
  const W = 2048, H = 192, c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  g.fillStyle = '#F6EFE3'; g.fillRect(0, 0, W, H);
  g.fillStyle = '#B8934A'; g.fillRect(0, 20, W, 4); g.fillRect(0, H - 24, W, 4);
  citrusMark(g, W * 0.25, H / 2, 46, accent, '#F6EFE3');
  g.fillStyle = '#6E5D51'; g.font = `500 30px ${SANS}`; g.textAlign = 'center';
  g.fillText('S H I R Á', W * 0.75, H / 2 + 11);
  return c;
}

/*HELPERS*/

// ---------------------------------------------------------------- scene
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
} catch (e) {
  statusEl.textContent = 'This mockup needs WebGL, which is turned off or unavailable in this browser.';
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.02;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.VSMShadowMap;
stage.prepend(renderer.domElement);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;
scene.environmentIntensity = 0.65;

const camera = new THREE.PerspectiveCamera(22, 1, 0.5, 500);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 13, 0);
controls.enablePan = false; controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.minDistance = 40; controls.maxDistance = 160;
controls.minPolarAngle = 1.2; controls.maxPolarAngle = 1.66;
camera.position.set(0, 15.5, 100);

const aniso = renderer.capabilities.getMaxAnisotropy();
const tex = (src, srgb = true) => { const t = src instanceof HTMLCanvasElement ? new THREE.CanvasTexture(src) : new THREE.TextureLoader().load(src); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = aniso; return t; };

const wall = new THREE.Mesh(new THREE.PlaneGeometry(240, 120), new THREE.MeshBasicMaterial({ map: tex(wallCanvas()), toneMapped: false }));
wall.position.set(0, 34, -60); scene.add(wall);
const woodMap = tex(woodCanvas()); woodMap.wrapS = woodMap.wrapT = THREE.RepeatWrapping; woodMap.repeat.set(1.6, 0.8);
const shelf = new THREE.Mesh(new THREE.BoxGeometry(170, 2.4, 44), new THREE.MeshPhysicalMaterial({ map: woodMap, roughness: 0.5, clearcoat: 0.45, clearcoatRoughness: 0.3 }));
shelf.position.set(0, -1.2, -10); shelf.receiveShadow = true; scene.add(shelf);

// ---------------------------------------------------------------- bottle
const PROFILE = [[0, 0], [2.85, 0], [3.18, 0.18], [3.3, 0.6], [3.3, 11.6], [3.24, 12.9], [3.02, 14.8], [2.62, 16.9],
  [2.12, 18.8], [1.7, 20.4], [1.44, 21.8], [1.36, 23.2], [1.34, 24.6], [1.48, 24.75], [1.5, 25.15], [1.38, 25.3]];
const pts = (list, n = 240) => new THREE.SplineCurve(list.map(([r, y]) => new THREE.Vector2(r, y))).getPoints(n);
const FILL = 21.9;
const juicePts = PROFILE.filter(([, y]) => y <= FILL).map(([r, y]) => [r ? r - 0.28 : 0, r ? y : 0.55]);
juicePts.push([juicePts[juicePts.length - 1][0], FILL], [0, FILL]);
const geo = {
  juice: new THREE.LatheGeometry(pts(juicePts), 160),
  shell: new THREE.LatheGeometry(pts(PROFILE), 160),
  neck: new THREE.LatheGeometry(pts(PROFILE.filter(([r, y]) => y >= FILL - 0.3 && r > 0), 80), 160),
  base: new THREE.CylinderGeometry(3.08, 2.86, 0.55, 128),
  label: new THREE.CylinderGeometry(3.32, 3.32, 9.5, 224, 1, true, -(19 / 3.3) * 0.25, 19 / 3.3),
  collar: new THREE.CylinderGeometry(1.395, 1.4, 1.35, 160, 1, true),
  cap: new THREE.CylinderGeometry(1.6, 1.63, 1.75, 160, 1, true),
  capTop: new THREE.CylinderGeometry(1.52, 1.6, 0.14, 160),
  ring: new THREE.TorusGeometry(1.62, 0.07, 16, 160),
  seal: new THREE.TorusGeometry(1.5, 0.05, 12, 160),
};
const shellMat = new THREE.MeshPhysicalMaterial({ color: '#000000', roughness: 0.02, clearcoat: 1, clearcoatRoughness: 0.01, envMapIntensity: 1.5, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
const clearGlass = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: 0.02, transmission: 1, thickness: 0.3, ior: 1.52, attenuationColor: new THREE.Color('#E2EFE6'), attenuationDistance: 1.6, envMapIntensity: 1.5, clearcoat: 1 });
const knurl = document.createElement('canvas'); knurl.width = 1024; knurl.height = 8;
{ const g = knurl.getContext('2d'); for (let x = 0; x < 1024; x += 6) { const gr = g.createLinearGradient(x, 0, x + 6, 0); gr.addColorStop(0, '#444'); gr.addColorStop(0.5, '#fff'); gr.addColorStop(1, '#444'); g.fillStyle = gr; g.fillRect(x, 0, 6, 8); } }
const goldMat = new THREE.MeshPhysicalMaterial({ color: '#C9A257', metalness: 1, roughness: 0.26, bumpMap: tex(knurl, false), bumpScale: 0.5, clearcoat: 0.7, clearcoatRoughness: 0.15 });
const goldTop = new THREE.MeshPhysicalMaterial({ color: '#C9A257', metalness: 1, roughness: 0.2, clearcoat: 0.7 });

const bottles = [];
for (const f of FLAVOURS) {
  const b = new THREE.Group();
  const juiceMat = new THREE.MeshPhysicalMaterial({
    color: f.cloudy ? f.juice : '#ffffff', roughness: f.cloudy ? 0.3 : 0.03, transmission: 1 - f.cloudy, thickness: 6.4, ior: 1.34,
    attenuationColor: new THREE.Color(f.juice), attenuationDistance: f.density, envMapIntensity: 0.7,
  });
  const liquid = new THREE.Mesh(geo.juice, juiceMat); liquid.castShadow = true; b.add(liquid);
  b.add(new THREE.Mesh(geo.shell, shellMat), new THREE.Mesh(geo.neck, clearGlass));
  const base = new THREE.Mesh(geo.base, clearGlass); base.position.y = 0.28; b.add(base);
  const map = tex(f.label);
  map.repeat.set(190 / 196, 95 / 101); map.offset.set(3 / 196, 3 / 101); // trim off the 3 mm print bleed
  const label = new THREE.Mesh(geo.label, new THREE.MeshPhysicalMaterial({ map, roughness: 0.72, envMapIntensity: 0.55 }));
  label.position.y = 1.7 + 4.75; label.castShadow = true; b.add(label);
  const collar = new THREE.Mesh(geo.collar, new THREE.MeshPhysicalMaterial({ map: tex(collarCanvas(f.accent)), roughness: 0.68 }));
  collar.position.y = 23.65; collar.rotation.y = -Math.PI / 2; collar.userData.accent = f.accent; b.add(collar);
  const cap = new THREE.Mesh(geo.cap, goldMat); cap.position.y = 25.4; cap.castShadow = true; b.add(cap);
  const top = new THREE.Mesh(geo.capTop, goldTop); top.position.y = 26.32; b.add(top);
  const ring = new THREE.Mesh(geo.ring, goldTop); ring.rotation.x = Math.PI / 2; ring.position.y = 24.56; b.add(ring);
  const seal = new THREE.Mesh(geo.seal, goldTop); seal.rotation.x = Math.PI / 2; seal.position.y = 24.36; b.add(seal);
  b.position.set(f.x, 0, f.z); b.userData.baseYaw = f.yaw; b.rotation.y = f.yaw;
  scene.add(b); bottles.push({ group: b, collar });
}

// ---------------------------------------------------------------- lights
const key = new THREE.DirectionalLight('#fff1de', 2.6);
key.position.set(-26, 38, 30); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 10; key.shadow.blurSamples = 20; key.shadow.bias = -0.0004;
Object.assign(key.shadow.camera, { left: -26, right: 26, top: 34, bottom: -6, near: 1, far: 120 });
scene.add(key);
const rim = new THREE.DirectionalLight('#ffd6a6', 2.4); rim.position.set(14, 26, -36); scene.add(rim);
const fillL = new THREE.DirectionalLight('#ffe9d2', 0.45); fillL.position.set(30, 14, 26); scene.add(fillL);
scene.add(new THREE.HemisphereLight('#fff2e2', '#6b4a2e', 0.3));

// ---------------------------------------------------------------- views
const VIEWS = { front: 0, side: Math.PI / 2.2, back: Math.PI };
const buttons = { front: 'v-front', side: 'v-side', back: 'v-back' };
let yaw = 0, targetYaw = 0, spin = false;
function pick(name) {
  spin = false; document.getElementById('v-spin').setAttribute('aria-pressed', 'false');
  targetYaw = VIEWS[name];
  for (const [k, id] of Object.entries(buttons)) document.getElementById(id).setAttribute('aria-pressed', String(k === name));
  const d = camera.position.distanceTo(controls.target);
  camera.position.set(controls.target.x, 15.5, controls.target.z + d);
}
for (const [k, id] of Object.entries(buttons)) document.getElementById(id).addEventListener('click', () => pick(k));
document.getElementById('v-spin').addEventListener('click', (e) => {
  spin = !spin; e.currentTarget.setAttribute('aria-pressed', String(spin));
  for (const id of Object.values(buttons)) document.getElementById(id).setAttribute('aria-pressed', 'false');
});

// keep the whole lineup in frame at any aspect ratio
function resize() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  const vfov = THREE.MathUtils.degToRad(camera.fov);
  const needH = 33, needW = 30;
  const dist = Math.max(needH / 2 / Math.tan(vfov / 2), needW / 2 / (Math.tan(vfov / 2) * camera.aspect));
  const dir = camera.position.clone().sub(controls.target).normalize();
  camera.position.copy(controls.target).addScaledVector(dir, dist);
}
new ResizeObserver(resize).observe(stage);

let last = performance.now();
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (spin && !reduceMotion) targetYaw += dt * 0.5;
  yaw += (targetYaw - yaw) * Math.min(1, dt * 6);
  for (const { group } of bottles) group.rotation.y = group.userData.baseYaw + yaw;
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

try { await document.fonts.load(`500 30px ${SANS}`); } catch (e) { /* system sans fallback */ }
for (const { collar } of bottles) { collar.material.map.image = collarCanvas(collar.userData.accent); collar.material.map.needsUpdate = true; }
THREE.DefaultLoadingManager.onLoad = () => { window.READY = true; };
setTimeout(() => { window.READY = true; }, 6000);
resize();
statusEl.remove();
document.getElementById('hint').hidden = false;
requestAnimationFrame(frame);
