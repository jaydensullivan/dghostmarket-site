// Главная dghostmarket.uz: анимации поверх обычной страницы (src/home.html).
// Без этого файла или библиотек из vendor/ всё содержимое видно как есть.
// Нож — наш 3D-рендер (embed.html мини-аппа) в одном iframe за контентом:
// на первом экране справа (на телефоне сверху), дальше переезжает в центр
// главы «3D» и поворачивается прокруткой, после неё гаснет. На слабых
// устройствах, при «уменьшить движение» и экономии трафика не грузим.
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

/* ---------- нож: наш 3D-рендер ---------- */
// Самый дорогой нож, который движок рисует как в игре (Fade у ножей пока
// расходится с игрой, поэтому не он).
const KNIFE = { skin: '★ Butterfly Knife | Doppler', float: '0.01', seed: '412' };
const APP = 'https://app.dghostmarket.uz';
const chap = document.getElementById('view3d');
const frame = document.querySelector('#stage iframe');
let frameReady = false, frameP = -1;
function sendFrame(p){
  if (!frameReady || !frame.contentWindow || Math.abs(p - frameP) < 0.001) return;
  frameP = p;
  frame.contentWindow.postMessage({ source: 'dghost-site', type: 'hero', p: p }, APP);
}
addEventListener('message', e => {
  if (e.origin !== APP || !e.data || e.data.source !== 'dghost3d') return;
  if (e.data.event === 'ready'){ frameReady = true; placeKnife(); }
  if (e.data.event === 'error'){ frame.remove(); body.classList.add('no-knife'); }
});
if (rich){
  frame.src = APP + '/embed.html?key=demo&hero=1&skin=' + encodeURIComponent(KNIFE.skin) + '&float=' + KNIFE.float
    + '&seed=' + KNIFE.seed + '&lang=' + (document.documentElement.lang || 'ru');
} else {
  frame.remove();
  body.classList.add('no-knife');
}
// Где нож по ходу прокрутки: 0..s1 — первый экран → центр главы,
// s1..s2 — глава «3D» (оборот), дальше гаснет.
let chapST = null;
function bounds(){
  if (chapST) return [chapST.start, chapST.end];
  const top = chap.getBoundingClientRect().top + scrollY;
  return [Math.max(1, top - innerHeight * .15), top + chap.offsetHeight - innerHeight * .5];
}
const lerp = (a, b, t) => a + (b - a) * t;
const clamp01 = v => Math.min(1, Math.max(0, v));
let placeQueued = false;
function placeKnife(){
  placeQueued = false;
  if (!frameReady || !frame.isConnected) return;
  const [s1, s2] = bounds(), y = scrollY;
  const t = clamp01(y / s1), c = clamp01((y - s1) / Math.max(1, s2 - s1));
  const fade = 1 - clamp01((y - s2) / (innerHeight * .6));
  const d = desk();
  // Невысокое окно шире, чем выше (планшет боком, маленькое окно ПК) —
  // нож меньше и ниже, иначе обрезается сверху.
  const flat = !d && innerWidth > innerHeight;
  const tx = d ? lerp(27, 0, t) : 0, ty = d ? lerp(-4, 7, t) : lerp(flat ? -14 : -26, 0, t), sc = lerp(d ? .95 : flat ? .8 : 1.1, 1, t);
  frame.style.transform = `translate(${tx}vw,${ty}vh) scale(${sc})`;
  frame.style.opacity = String(fade);
  frame.style.visibility = fade <= 0 ? 'hidden' : '';
  sendFrame(y < s1 ? t * .2 : .2 + c * .8);
}
function queuePlace(){ if (!placeQueued){ placeQueued = true; requestAnimationFrame(placeKnife); } }
addEventListener('scroll', queuePlace, { passive: true });
addEventListener('resize', queuePlace);

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

if (!hasGsap) return;

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
  // Первый экран уходит вверх и гаснет.
  gsap.to('.hero .wrap', { yPercent: -14, opacity: .2, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });

  if (d){
    // Глава «3D» закреплена: модель поворачивается, карточки листаются.
    body.classList.add('pin3d');
    chapST = ScrollTrigger.create({ trigger: chap, start: 'top top', end: '+=200%', pin: true, scrub: 1,
      onUpdate: self => setFeature(self.progress) });
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
  return () => { chapST = null; body.classList.remove('pin3d'); gsap.set([trackBuy, trackSell], { x: 0 }); };
});
ScrollTrigger.addEventListener('refresh', queuePlace);
addEventListener('load', () => ScrollTrigger.refresh());
if (document.fonts) document.fonts.ready.then(() => ScrollTrigger.refresh());
})();
