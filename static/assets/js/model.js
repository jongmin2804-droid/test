/* 미니카 3D 모델 보기 (three.js r170)
   - assets/model/minicar_assembly.glb 를 불러온다.
   - GLB 안 각 부품(메시/노드)의 이름을 아래 PARTS 의 키와 같게 만들어 두면 한국어 이름이 표시된다.
   - EXPLODE 에 적은 부품은 '분해 정도'를 올리면 그 방향(mm)으로 움직인다. */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const MODEL_Z_UP = true;   // GLB의 위쪽이 Z축이면 true

const PARTS = {
  tray: '전장 트레이', dashboard: '대시보드', rear_pod: '후면 포드', front_pod: '전면 포드',
  plate_E26_est: '섀시 판', wheel: '바퀴', tt_motor: 'TT 기어모터', caster: '볼 캐스터', standoff: '스탠드오프',
  battery_18650_2S: '18650 배터리 팩', power_block: '전원 블록(메인 스위치·퓨즈)',
  uno_r3: 'Arduino Uno', l298n: 'L298N 모터드라이버', breadboard_400: '브레드보드', relay_1ch: '릴레이 모듈',
  hc06: 'HC-06 블루투스', lcd_1602: '1602 LCD', hc_sr04: '초음파 센서 HC-SR04',
};
// 분해할 때 움직이는 방향과 거리(mm). 모델 좌표 [X 앞, Y 왼쪽, Z 위] 기준
const T = [0, 0, 60], D = [50, 0, 90], R = [-70, 0, 0], F = [60, 0, -10];
const EXPLODE = {
  tray: T, uno_r3: T, l298n: T, breadboard_400: T, relay_1ch: T, hc06: T,
  dashboard: D, lcd_1602: D, rear_pod: R, hc_sr04: R, front_pod: F, standoff: [0, 0, 25],
};
const keyOf = n => PARTS[n] ? n : (PARTS[n.replace(/_(L|R|\d+)$/, '')] ? n.replace(/_(L|R|\d+)$/, '') : null);

const canvas = document.getElementById('viewer');
const msg = document.getElementById('viewer-msg');
const nameEl = document.getElementById('part-name');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.005, 10);
camera.position.set(0.35, 0.25, 0.35);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a9bb0, 1.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.8); sun.position.set(0.4, 0.8, 0.5); scene.add(sun);
scene.add(new THREE.GridHelper(0.6, 24, 0x9fb3c8, 0xd5dfe9));

const movers = [];   // [object, 원래 위치, 분해 방향]
const pickable = [];

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

new GLTFLoader().load('/assets/model/minicar_assembly.glb', gltf => {
  const root = gltf.scene;
  // CAD·파이썬(trimesh)에서 만든 모델은 Z가 위쪽이므로 화면(Y가 위쪽)에 맞게 눕힌다.
  // Blender에서 '+Y Up'으로 내보낸 GLB라면 MODEL_Z_UP 을 false 로 바꾼다.
  const wrap = new THREE.Group();
  if (MODEL_Z_UP) wrap.rotation.x = -Math.PI / 2;
  wrap.add(root);
  wrap.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(wrap);
  const c = box.getCenter(new THREE.Vector3());
  wrap.position.set(-c.x, -box.min.y, -c.z);
  scene.add(wrap);
  root.traverse(o => {
    const k = keyOf(o.name);
    if (k && EXPLODE[k] && !movers.some(m => m[0] === o)) movers.push([o, o.position.clone(), new THREE.Vector3(...EXPLODE[k]).multiplyScalar(0.001)]);
    if (o.isMesh) pickable.push(o);
  });
  controls.target.set(0, box.getSize(new THREE.Vector3()).y / 2, 0);
  msg.hidden = true;
  resize();
}, undefined, () => { msg.textContent = '모델 파일을 불러오지 못했다 (assets/model/minicar_assembly.glb 확인).'; });

document.getElementById('explode').addEventListener('input', e => {
  const t = e.target.value / 100;
  movers.forEach(([o, p0, d]) => o.position.copy(p0).addScaledVector(d, t));
});

const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
canvas.addEventListener('click', e => {
  const r = canvas.getBoundingClientRect();
  ptr.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
  ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(pickable, false)[0];
  if (!hit) return;
  for (let o = hit.object; o; o = o.parent) { const k = keyOf(o.name); if (k) { nameEl.textContent = PARTS[k]; return; } }
  nameEl.textContent = hit.object.name || '이름 없는 부품';
});

renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
