// Главная dghostmarket.uz: анимации поверх обычной страницы (src/home.html).
// Без этого файла или библиотек из vendor/ всё содержимое видно как есть.
// Нож на первом экране — лёгкая модель из простых фигур (Three.js),
// в главе «3D» — настоящий Karambit | Lore из 3D-движка мини-аппа (iframe).
// На слабых устройствах, при «уменьшить движение» и экономии трафика ни
// того, ни другого не грузим.
(function(){
'use strict';
const body = document.body;
body.classList.remove('no-js');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const nav = navigator, conn = nav.connection || {};
const weak = !!(conn.saveData || (nav.deviceMemory && nav.deviceMemory < 3) || (nav.hardwareConcurrency && nav.hardwareConcurrency < 4));
const hasWebgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; } })();
const rich = !reduce && !weak && hasWebgl;
const desk = () => innerWidth >= 900;
const hasGsap = !!(window.gsap && window.ScrollTrigger);
if (hasGsap) gsap.registerPlugin(ScrollTrigger);
if (reduce || !hasGsap) body.classList.add('no-anim');

/* ---------- шапка: фон после первого экрана ---------- */
const navEl = document.getElementById('nav');
const onScroll = () => navEl.classList.toggle('solid', scrollY > 40);
addEventListener('scroll', onScroll, { passive: true });
onScroll();

/* ---------- вкладки «Покупателю / Продавцу» ---------- */
const tabBuy = document.getElementById('tabBuy'), tabSell = document.getElementById('tabSell');
const trackBuy = document.getElementById('trackBuy'), trackSell = document.getElementById('trackSell');
function setTab(sell){
  tabBuy.setAttribute('aria-selected', String(!sell));
  tabSell.setAttribute('aria-selected', String(sell));
  const show = sell ? trackSell : trackBuy, hide = sell ? trackBuy : trackSell;
  if (!show.hidden) return;
  hide.hidden = true; show.hidden = false;
  if (hasGsap && !reduce) gsap.from(show.querySelectorAll('.step'), { y: 24, opacity: 0, duration: .45, stagger: .05, ease: 'power3.out' });
  if (hasGsap) ScrollTrigger.refresh();
}
tabBuy.addEventListener('click', () => setTab(false));
tabSell.addEventListener('click', () => setTab(true));

/* ---------- счётчик «8 дней» ---------- */
const dayWord = (document.getElementById('txtDay') || {}).textContent || '';
const payWord = (document.querySelector('[data-i18n="hold_m2_t"]') || {}).textContent || '';
const holdCount = document.getElementById('holdCount');
function setHold(n){
  holdCount.textContent = n >= 8 ? payWord : (dayWord + ' ' + n);
  holdCount.style.color = n >= 8 ? 'var(--mint)' : '';
}
setHold(reduce || !hasGsap ? 8 : 0);

/* ---------- настоящая 3D-модель в главе «3D» ---------- */
const APP = 'https://app.dghostmarket.uz';
const chap = document.getElementById('view3d');
const frame = chap.querySelector('.frame');
let frameReady = false, frameStarted = false, frameP = -1;
function startFrame(){
  if (frameStarted || !rich) return;
  frameStarted = true;
  frame.src = APP + '/embed.html?key=demo&hero=1&skin=' + encodeURIComponent('★ Karambit | Lore') + '&float=0.03&seed=73&lang=' + (document.documentElement.lang || 'ru');
}
function sendFrame(p){
  if (!frameReady || !frame.contentWindow || Math.abs(p - frameP) < 0.001) return;
  frameP = p;
  frame.contentWindow.postMessage({ source: 'dghost-site', type: 'hero', p: p }, APP);
}
addEventListener('message', e => {
  if (e.origin !== APP || !e.data || e.data.source !== 'dghost3d') return;
  if (e.data.event === 'ready'){ frameReady = true; frame.classList.add('on'); sendFrame(0); }
  if (e.data.event === 'error') frame.remove();
});
if (rich){
  if ('IntersectionObserver' in window){
    new IntersectionObserver((es, o) => { if (es[0].isIntersecting){ startFrame(); o.disconnect(); } }, { rootMargin: '600px 0px' }).observe(chap);
  } else startFrame();
}
// Без закрепления (телефон) — поворот по положению главы на экране.
function chapProgress(){
  const r = chap.getBoundingClientRect();
  return Math.min(1, Math.max(0, (innerHeight - r.top) / (innerHeight + r.height)));
}
addEventListener('scroll', () => { if (!body.classList.contains('pin3d')) sendFrame(chapProgress()); }, { passive: true });

/* ---------- карточки 3D-главы ---------- */
const fcards = [...document.querySelectorAll('.fcard')], fdots = [...document.querySelectorAll('#fdots i')];
let fIdx = 0;
function setFeature(p){
  const i = Math.min(2, Math.floor(p * 3));
  if (i === fIdx) return;
  fIdx = i;
  fcards.forEach((c, j) => c.classList.toggle('on', j === i));
  fdots.forEach((d, j) => d.classList.toggle('on', j === i));
}

/* ---------- плавная прокрутка и якоря ---------- */
let lenis = null;
if (!reduce && window.Lenis){
  lenis = new Lenis({ lerp: .1, smoothWheel: true });
  if (hasGsap){ lenis.on('scroll', ScrollTrigger.update); gsap.ticker.add(t => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0); }
  else { const raf = t => { lenis.raf(t); requestAnimationFrame(raf); }; requestAnimationFrame(raf); }
}
document.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
  const id = a.getAttribute('href');
  const el = id === '#top' ? document.body : document.querySelector(id);
  if (!el) return;
  e.preventDefault();
  if (lenis) lenis.scrollTo(id === '#top' ? 0 : el, { offset: -70, duration: 1.2 });
  else el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  history.replaceState(null, '', id);
}));

/* ---------- прицел и магнитные кнопки (только мышь) ---------- */
if (matchMedia('(hover:hover) and (pointer:fine)').matches && !reduce){
  body.classList.add('js-cursor');
  const cross = document.getElementById('cross');
  let cx = innerWidth / 2, cy = innerHeight / 2, px = cx, py = cy;
  addEventListener('pointermove', e => { px = e.clientX; py = e.clientY; });
  (function c(){ cx += (px - cx) * .25; cy += (py - cy) * .25; cross.style.transform = `translate(${cx}px,${cy}px)`; requestAnimationFrame(c); })();
  document.querySelectorAll('a,button,summary,input').forEach(el => {
    el.addEventListener('pointerenter', () => cross.classList.add('hot'));
    el.addEventListener('pointerleave', () => cross.classList.remove('hot'));
  });
  document.querySelectorAll('.mag').forEach(el => {
    el.addEventListener('pointermove', e => { const r = el.getBoundingClientRect(); el.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .25}px,${(e.clientY - r.top - r.height / 2) * .35}px)`; });
    el.addEventListener('pointerleave', () => { el.style.transition = 'transform .5s cubic-bezier(.2,1.6,.4,1)'; el.style.transform = ''; setTimeout(() => el.style.transition = '', 500); });
  });
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('pointermove', e => {
      const r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      card.style.transform = `rotateY(${(x - .5) * 14}deg) rotateX(${(.5 - y) * 12}deg) translateZ(0)`;
      card.style.setProperty('--mx', x * 100 + '%'); card.style.setProperty('--my', y * 100 + '%'); card.style.setProperty('--hx', x * 100 + '%');
    });
    card.addEventListener('pointerleave', () => { card.style.transform = ''; });
  });
}

/* ---------- нож на первом экране ---------- */
const K = { x: 3.7, y: .1, s: .8, spin: 0, tilt: .35, op: 1, in: 1, is: 0 };
function placeKnife(){ Object.assign(K, desk() ? { x: 3.7, y: .1, s: .8 } : { x: .2, y: 2.15, s: .6 }); }
placeKnife();
const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
addEventListener('pointermove', e => { mouse.tx = e.clientX / innerWidth - .5; mouse.ty = e.clientY / innerHeight - .5; });
let renderKnife = null;
if (rich){
  const s = document.createElement('script');
  s.src = '/vendor/three-r128.min.js';
  s.onload = () => { try { renderKnife = initKnife(); requestAnimationFrame(loop); } catch (e) { body.classList.add('no-knife'); } };
  s.onerror = () => body.classList.add('no-knife');
  document.head.appendChild(s);
} else body.classList.add('no-knife');

function loop(now){
  if (renderKnife && renderKnife(now) !== false) requestAnimationFrame(loop);
  else if (renderKnife) setTimeout(() => requestAnimationFrame(loop), 300);
}

function dopplerTexture(){
  const c = document.createElement('canvas'); c.width = c.height = 512;
  const g = c.getContext('2d');
  const lg = g.createLinearGradient(0, 0, 512, 512);
  lg.addColorStop(0, '#ff2bd6'); lg.addColorStop(.45, '#7b2cff'); lg.addColorStop(.8, '#2bc8ff'); lg.addColorStop(1, '#ff2bd6');
  g.fillStyle = lg; g.fillRect(0, 0, 512, 512);
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 70; i++){
    const x = rnd() * 512, y = rnd() * 512, r = 20 + rnd() * 90;
    const rg = g.createRadialGradient(x, y, 0, x, y, r);
    rg.addColorStop(0, rnd() < .5 ? 'rgba(10,0,30,.55)' : 'rgba(255,255,255,.35)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = rg; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
  }
  g.globalAlpha = .25; g.strokeStyle = '#fff';
  for (let i = 0; i < 40; i++){ g.lineWidth = 1 + rnd() * 2; g.beginPath(); const x = rnd() * 512, y = rnd() * 512; g.moveTo(x, y); g.bezierCurveTo(x + rnd() * 120 - 60, y + rnd() * 120 - 60, x + rnd() * 200 - 100, y + rnd() * 200 - 100, x + rnd() * 260 - 130, y + rnd() * 260 - 130); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(.32, .32); t.encoding = THREE.sRGBEncoding;
  return t;
}
function envTexture(renderer){
  const c = document.createElement('canvas'); c.width = 1024; c.height = 512; const g = c.getContext('2d');
  const lg = g.createLinearGradient(0, 0, 0, 512); lg.addColorStop(0, '#2a1050'); lg.addColorStop(.5, '#06040a'); lg.addColorStop(1, '#1a0630');
  g.fillStyle = lg; g.fillRect(0, 0, 1024, 512);
  [['#ff2bd6', 150, 160, 120], ['#7b2cff', 520, 120, 180], ['#ffffff', 820, 200, 70], ['#57d6ff', 360, 380, 110]].forEach(([col, x, y, r]) => { const rg = g.createRadialGradient(x, y, 0, x, y, r); rg.addColorStop(0, col); rg.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = rg; g.fillRect(0, 0, 1024, 512); });
  g.fillStyle = 'rgba(255,255,255,.9)'; g.fillRect(0, 250, 1024, 6);
  const tex = new THREE.CanvasTexture(c); tex.mapping = THREE.EquirectangularReflectionMapping; tex.encoding = THREE.sRGBEncoding;
  const pm = new THREE.PMREMGenerator(renderer); const rt = pm.fromEquirectangular(tex); pm.dispose(); return rt.texture;
}
function initKnife(){
  const host = document.getElementById('stage');
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, desk() ? 2 : 1.5));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;
  host.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.environment = envTexture(renderer);
  const cam = new THREE.PerspectiveCamera(32, 1, .1, 100); cam.position.set(0, 0, 13);
  const knife = new THREE.Group(), pivot = new THREE.Group(); pivot.add(knife); scene.add(pivot);
  // Лезвие керамбита
  const b = new THREE.Shape();
  b.moveTo(0, .34); b.bezierCurveTo(1.25, .62, 2.55, .18, 3.0, -1.55); b.bezierCurveTo(2.35, -.72, 1.45, -.36, 0, -.3); b.lineTo(0, .34);
  const bg = new THREE.ExtrudeGeometry(b, { depth: .05, bevelEnabled: true, bevelThickness: .07, bevelSize: .06, bevelSegments: 4, curveSegments: 48 });
  bg.translate(0, 0, -.025);
  const tex = dopplerTexture();
  knife.add(new THREE.Mesh(bg, new THREE.MeshStandardMaterial({ map: tex, metalness: .9, roughness: .16, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: .22, envMapIntensity: 1.4 })));
  // Рукоять
  const h = new THREE.Shape();
  h.moveTo(0, .44); h.quadraticCurveTo(-1.3, .66, -2.45, .42); h.lineTo(-2.5, -.32); h.quadraticCurveTo(-1.3, -.22, 0, -.44); h.lineTo(0, .44);
  const hg = new THREE.ExtrudeGeometry(h, { depth: .26, bevelEnabled: true, bevelThickness: .07, bevelSize: .07, bevelSegments: 4, curveSegments: 24 });
  hg.translate(0, 0, -.13);
  knife.add(new THREE.Mesh(hg, new THREE.MeshStandardMaterial({ color: 0x1a1226, metalness: .35, roughness: .55, envMapIntensity: .8 })));
  const gripMat = new THREE.MeshStandardMaterial({ color: 0xff2bd6, emissive: 0xff2bd6, emissiveIntensity: .6, metalness: .2, roughness: .4 });
  for (let i = 0; i < 5; i++){ const m = new THREE.Mesh(new THREE.BoxGeometry(.05, .78, .44), gripMat); m.position.set(-.55 - i * .38, .06 + Math.sin(i * .6) * .06, 0); knife.add(m); }
  // Гарда и кольцо
  const metal = new THREE.MeshStandardMaterial({ color: 0xcfc4e6, metalness: 1, roughness: .18 });
  const guard = new THREE.Mesh(new THREE.BoxGeometry(.18, 1.05, .42), metal); guard.position.set(.02, .02, 0); knife.add(guard);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(.52, .14, 24, 64), metal); ring.position.set(-3.05, .06, 0); knife.add(ring);
  knife.position.x = .1;
  const l1 = new THREE.PointLight(0xff2bd6, 40, 30); l1.position.set(-4, 3, 5); scene.add(l1);
  const l2 = new THREE.PointLight(0x7b2cff, 50, 30); l2.position.set(5, -2, 4); scene.add(l2);
  scene.add(new THREE.AmbientLight(0xffffff, .25));
  function size(){ renderer.setSize(innerWidth, innerHeight, false); cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); }
  size(); addEventListener('resize', size);
  const t0 = performance.now();
  return function(now){
    const t = (now - t0) / 1000;
    mouse.x += (mouse.tx - mouse.x) * .06; mouse.y += (mouse.ty - mouse.y) * .06;
    renderer.domElement.style.opacity = K.op;
    // Нож ушёл с экрана — не рисуем (экономим батарею), проверяем реже.
    if (K.op <= .01 || document.hidden) return false;
    pivot.position.set(K.x + mouse.x * .4, K.y - mouse.y * .3 + Math.sin(t * 1.1) * .08, 0);
    pivot.scale.setScalar(K.s * K.in);
    pivot.rotation.set(K.tilt + mouse.y * .5, Math.sin(t * .6) * .55 + K.spin + K.is + mouse.x * .9, -.35 + mouse.x * .15);
    tex.offset.x = t * .01;
    renderer.render(scene, cam);
  };
}

if (!hasGsap){ sendFrame(chapProgress()); return; }

/* ---------- бегущие строки (скорость — от прокрутки) ---------- */
const tick = document.getElementById('tick');
const mq = document.getElementById('bigmq');
if (!reduce){
  let tickTw = null;
  if (tick){
    const clone = tick.innerHTML;
    tick.insertAdjacentHTML('beforeend', clone.replace(/<a /g, '<a tabindex="-1" aria-hidden="true" '));
    tickTw = gsap.to(tick, { xPercent: -50, duration: Math.max(20, tick.children.length * 1.4), ease: 'none', repeat: -1 });
  }
  const mqTw = mq ? gsap.to(mq, { xPercent: -50, duration: 22, ease: 'none', repeat: -1 }) : null;
  let vel = 0;
  ScrollTrigger.create({ onUpdate: self => { vel = self.getVelocity(); } });
  gsap.ticker.add(() => {
    const v = gsap.utils.clamp(-6, 6, vel / 400), ts = (1 + Math.abs(v) * 1.5) * (v < 0 ? -1 : 1);
    if (tickTw) tickTw.timeScale(ts);
    if (mqTw){ mqTw.timeScale(ts); gsap.set(mq, { skewX: -v * 2 }); }
    vel *= .92;
  });
}

/* полоса прогресса */
gsap.to('#prog', { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: true } });

if (reduce) return;

/* ---------- появление ---------- */
gsap.from('.h1 .ln>span', { yPercent: 110, rotate: 3, duration: 1.2, ease: 'expo.out', stagger: .12, delay: .1 });
gsap.from('.hero-row>*,.hero .kicker,.hud', { y: 30, opacity: 0, duration: 1, ease: 'power3.out', stagger: .08, delay: .45 });
gsap.fromTo(K, { in: .3, is: -3.5 }, { in: 1, is: 0, duration: 2.2, ease: 'expo.out' });
document.querySelectorAll('[data-count]').forEach(el => {
  const end = +el.dataset.count, o = { v: 0 };
  el.textContent = '0';
  gsap.to(o, { v: end, duration: 1.6, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 85%', once: true }, onUpdate: () => el.textContent = Math.round(o.v) });
});
gsap.utils.toArray('.rv').forEach(el => gsap.from(el, { y: 50, opacity: 0, duration: .9, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 92%', once: true } }));
gsap.utils.toArray('section h2').forEach(h => {
  if (h.closest('.chap') || h.closest('.hold')) return;
  gsap.from(h, { yPercent: 30, opacity: 0, duration: 1, ease: 'expo.out', scrollTrigger: { trigger: h, start: 'top 90%', once: true } });
});
gsap.from('.fee .big', { scale: .6, opacity: 0, duration: 1.2, ease: 'back.out(2)', stagger: .12, scrollTrigger: { trigger: '.feegrid', start: 'top 80%', once: true } });

/* ---------- сценарий прокрутки: ПК и телефон отдельно ---------- */
const mm = gsap.matchMedia();
mm.add({ d: '(min-width:900px)', m: '(max-width:899px)' }, ctx => {
  const d = ctx.conditions.d;
  placeKnife(); K.op = 1;
  // Первый экран уходит, нож гаснет до главы с настоящей моделью.
  gsap.to('.hero .wrap', { yPercent: -14, opacity: .2, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  gsap.to(K, { op: 0, x: d ? 1.2 : 0, y: d ? -.4 : 3, spin: Math.PI, ease: 'none', scrollTrigger: { trigger: '.stats', start: 'top 85%', end: 'bottom 30%', scrub: true } });

  if (d){
    // Глава «3D» закреплена: модель поворачивается, карточки листаются.
    body.classList.add('pin3d');
    ScrollTrigger.create({ trigger: chap, start: 'top top', end: '+=200%', pin: true, scrub: 1,
      onUpdate: self => { setFeature(self.progress); sendFrame(self.progress); } });
    // Сделка — лентой вбок.
    const how = document.getElementById('how');
    const visible = () => trackBuy.hidden ? trackSell : trackBuy;
    const dist = () => Math.max(0, visible().scrollWidth - innerWidth);
    const st = { trigger: how, start: 'top top', end: () => '+=' + dist(), pin: true, scrub: 1, invalidateOnRefresh: true };
    gsap.to([trackBuy, trackSell], { x: () => -dist(), ease: 'none', scrollTrigger: st });
    gsap.to('.rail b', { scaleX: 1, ease: 'none', scrollTrigger: Object.assign({}, st, { pin: false }) });
    // 8 дней заполняются по очереди.
    const fills = gsap.utils.toArray('.day b');
    const htl = gsap.timeline({ scrollTrigger: { trigger: '#hold', start: 'top top', end: '+=140%', pin: true, scrub: 1,
      onUpdate: self => setHold(Math.min(8, Math.floor(self.progress * 8.6))) } });
    fills.forEach(f => htl.to(f, { scaleX: 1, ease: 'none', duration: 1 }));
  } else {
    gsap.utils.toArray('.step').forEach(s => gsap.from(s, { y: 40, opacity: 0, duration: .8, ease: 'power3.out', scrollTrigger: { trigger: s, start: 'top 92%', once: true } }));
    // На телефоне без закреплений — дни заполняются, когда блок на экране.
    const htl = gsap.timeline({ scrollTrigger: { trigger: '#days', start: 'top 80%', once: true } });
    gsap.utils.toArray('.day b').forEach((f, i) => htl.to(f, { scaleX: 1, ease: 'power2.out', duration: .22, onComplete: () => setHold(i + 1) }));
  }
  return () => { body.classList.remove('pin3d'); gsap.set([trackBuy, trackSell], { x: 0 }); };
});
addEventListener('load', () => ScrollTrigger.refresh());
if (document.fonts) document.fonts.ready.then(() => ScrollTrigger.refresh());
})();
