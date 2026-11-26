// Все звуки ролика синтезируются здесь — без сэмплов. Run: node tools/gen-audio.mjs
// Writes assets/sfx/*.wav and assets/sfx/placements.json (clip id, file, start, volume).
import fs from "node:fs";
import path from "node:path";

const SR = 48000;
const OUT = path.join(path.dirname(new URL(import.meta.url).pathname), "..", "assets", "sfx");
fs.mkdirSync(OUT, { recursive: true });

// deterministic noise
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6d2b79f5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return (((t ^ (t >>> 14)) >>> 0) / 4294967296) * 2 - 1; }; }
const buf = (sec) => [new Float32Array(Math.ceil(sec * SR)), new Float32Array(Math.ceil(sec * SR))];
const env = (t, a, d) => (t < 0 ? 0 : t < a ? t / a : Math.exp(-(t - a) / d));

// state-variable bandpass / lowpass / highpass, per-sample cutoff
function svf() { let lp = 0, bp = 0; return (x, fc, q = 0.7) => { const f = 2 * Math.sin(Math.PI * Math.min(fc, SR / 6) / SR); const hp = x - lp - q * bp; bp += f * hp; lp += f * bp; return { lp, bp, hp }; }; }

function addMono(B, i, v, pan = 0) { if (i < 0 || i >= B[0].length) return; B[0][i] += v * (1 - Math.max(0, pan)); B[1][i] += v * (1 + Math.min(0, pan)); }

// small stereo room: feedback combs + allpass, mixed wet
function reverb(B, wet = 0.25, size = 1) {
  const out = [new Float32Array(B[0].length), new Float32Array(B[0].length)];
  [0, 1].forEach((ch) => {
    const x = B[ch], y = out[ch];
    const combs = [1116, 1188, 1277, 1356].map((d) => Math.round(d * size * (ch ? 1.03 : 1) * SR / 44100));
    const bufs = combs.map((d) => ({ d, b: new Float32Array(d), i: 0, f: 0 }));
    for (let n = 0; n < x.length; n++) {
      let s = 0;
      for (const c of bufs) { const o = c.b[c.i]; c.f = o * 0.7 + c.f * 0.3; c.b[c.i] = x[n] + c.f * 0.82; c.i = (c.i + 1) % c.d; s += o; }
      y[n] = x[n] + wet * s * 0.25;
    }
  });
  return out;
}

function writeWav(name, B, gain = 1) {
  let peak = 0;
  for (const ch of B) for (const v of ch) peak = Math.max(peak, Math.abs(v));
  const g = peak > 0 ? (0.89 / peak) * gain : 1; // ≈ -1 dBFS peak, then gain
  const n = B[0].length, data = Buffer.alloc(44 + n * 4);
  data.write("RIFF", 0); data.writeUInt32LE(36 + n * 4, 4); data.write("WAVE", 8); data.write("fmt ", 12);
  data.writeUInt32LE(16, 16); data.writeUInt16LE(1, 20); data.writeUInt16LE(2, 22); data.writeUInt32LE(SR, 24);
  data.writeUInt32LE(SR * 4, 28); data.writeUInt16LE(4, 32); data.writeUInt16LE(16, 34); data.write("data", 36); data.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) for (let c = 0; c < 2; c++) data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, B[c][i] * g)) * 32767), 44 + (i * 2 + c) * 2);
  fs.writeFileSync(path.join(OUT, name + ".wav"), data);
}

// ---------- instruments ----------
function kick(B, t0, amp = 1, pitch = 1) {
  let ph = 0; const r = rng(t0 * 1000);
  for (let i = 0; i < 0.5 * SR; i++) {
    const t = i / SR, f = (45 + 110 * Math.exp(-t / 0.035)) * pitch; ph += (2 * Math.PI * f) / SR;
    const v = Math.sin(ph) * env(t, 0.002, 0.16) * 0.9 + r() * env(t, 0.0005, 0.004) * 0.5;
    addMono(B, Math.round(t0 * SR) + i, Math.tanh(v * 1.6) * amp);
  }
}
function hat(B, t0, amp = 0.25, len = 0.035, pan = 0.2) {
  const r = rng(Math.round(t0 * 977)), f = svf();
  for (let i = 0; i < len * 6 * SR; i++) { const t = i / SR; addMono(B, Math.round(t0 * SR) + i, f(r(), 9000, 0.4).hp * env(t, 0.0005, len) * amp, pan); }
}
function clap(B, t0, amp = 0.5) {
  const r = rng(Math.round(t0 * 313)), f = svf();
  for (let i = 0; i < 0.25 * SR; i++) {
    const t = i / SR, bursts = env(t, 0.0005, 0.006) + env(t - 0.011, 0.0005, 0.006) + env(t - 0.022, 0.0005, 0.05);
    addMono(B, Math.round(t0 * SR) + i, f(r(), 1500, 0.5).bp * bursts * amp * 2);
  }
}
// noise whoosh: band sweeps f0→f1, swell peaks at `peak` (fraction of len)
function whoosh(len, f0, f1, peak = 0.6, seed = 1, pan0 = -0.4, pan1 = 0.4) {
  const B = buf(len + 0.05), r = rng(seed), fa = svf(), fb = svf();
  for (let i = 0; i < len * SR; i++) {
    const u = i / (len * SR), fc = f0 * Math.pow(f1 / f0, u);
    const a = u < peak ? Math.pow(u / peak, 2.2) : Math.pow(1 - (u - peak) / (1 - peak), 1.6);
    const x = r(); const v = fa(x, fc, 0.25).bp * 0.7 + fb(x, fc * 2.1, 0.5).bp * 0.3;
    addMono(B, i, v * a, pan0 + (pan1 - pan0) * u);
  }
  return B;
}
function pop(f0 = 900, f1 = 200, len = 0.09, seed = 3, thump = 0) {
  const B = buf(len + 0.25), r = rng(seed); let ph = 0, ph2 = 0;
  for (let i = 0; i < (len + 0.2) * SR; i++) {
    const t = i / SR, f = f1 + (f0 - f1) * Math.exp(-t / (len * 0.25)); ph += (2 * Math.PI * f) / SR; ph2 += (2 * Math.PI * (55 + 60 * Math.exp(-t / 0.03))) / SR;
    addMono(B, i, Math.sin(ph) * env(t, 0.001, len * 0.4) * 0.8 + r() * env(t, 0.0003, 0.003) * 0.4 + thump * Math.sin(ph2) * env(t, 0.002, 0.09));
  }
  return B;
}
function impact(len = 1.6, size = 1, seed = 9) {
  const B = buf(len), r = rng(seed), f = svf(), f2 = svf(); let ph = 0;
  for (let i = 0; i < len * SR; i++) {
    const t = i / SR; ph += (2 * Math.PI * (38 + 90 * Math.exp(-t / 0.05))) / SR;
    const boom = Math.sin(ph) * env(t, 0.003, 0.35 * size);
    const crack = f(r(), 2500, 0.6).bp * env(t, 0.0005, 0.03) * 1.6;
    const body = f2(r(), 400 + 600 * Math.exp(-t / 0.1), 0.4).bp * env(t, 0.002, 0.18 * size);
    addMono(B, i, Math.tanh((boom * 1.2 + crack + body) * 1.4), 0);
  }
  return reverb(B, 0.35 * size, 1.1);
}
function tick(fc = 3200, seed = 5, amp = 1, pan = 0) {
  const B = buf(0.12), r = rng(seed), f = svf();
  for (let i = 0; i < 0.12 * SR; i++) { const t = i / SR; addMono(B, i, f(r() * env(t, 0.0002, 0.0025), fc, 0.08).bp * amp * 6 * env(t, 0, 0.03), pan); }
  return B;
}
function thwip() { // rubber stretch: rising sweep with a little noise
  const B = buf(0.45), r = rng(11), f = svf(); let ph = 0;
  for (let i = 0; i < 0.4 * SR; i++) {
    const t = i / SR, u = t / 0.4, fr = 140 * Math.pow(9, Math.min(1, t / 0.12)); ph += (2 * Math.PI * fr) / SR;
    addMono(B, i, (Math.sin(ph) * 0.6 + f(r(), fr * 2, 0.5).bp * 0.5) * env(t, 0.004, 0.09) * (1 - u));
  }
  return B;
}
function shimmer(len = 0.6, seed = 21) { // granular sparkle as a shape breaks into dots
  const B = buf(len + 0.1), r = rng(seed);
  for (let g = 0; g < 90; g++) {
    const u = Math.pow((g + 0.5) / 90, 0.6), t0 = u * len, fc = 3000 + 4000 * Math.abs(r()), T = tick(fc, seed + g, 0.25 + 0.5 * u, r() * 0.8);
    const off = Math.round(t0 * SR); for (let i = 0; i < T[0].length; i++) { addMono(B, off + i, T[0][i], -1); B[1][off + i] !== undefined && (B[1][off + i] += T[1][i]); }
  }
  return B;
}
function riser(len = 1.25, seed = 31) {
  const B = buf(len), r = rng(seed), f = svf(), f2 = svf();
  for (let i = 0; i < len * SR; i++) {
    const u = i / (len * SR), fc = 300 * Math.pow(25, u);
    const v = (f(r(), fc, 0.2).bp + f2(r(), fc * 1.5, 0.3).bp * 0.5) * Math.pow(u, 2.4);
    addMono(B, i, v, Math.sin(u * 30) * 0.3 * u);
  }
  return B;
}
function suck(len = 0.75, seed = 41) { // reversed whoosh: swells to a hard stop
  const W = whoosh(len, 6000, 400, 0.15, seed, 0.5, -0.5);
  return [W[0].slice().reverse(), W[1].slice().reverse()];
}

// ---------- ритм: 120 BPM, доля = 0.5 с ----------
const bed = buf(15.6);
for (let b = 0; b < 30; b++) {
  const t = b * 0.5;
  if (t >= 11.5) continue;                 // перед логотипом ритм уходит, остаётся подъём
  kick(bed, t, t < 2.5 ? 0.7 : 0.9);
  if (t >= 2.5 && b % 2 === 1) clap(bed, t, 0.4);
  for (const h of (t < 2.5 ? [0.25] : [0.125, 0.25, 0.375])) hat(bed, t + h, h === 0.25 ? 0.2 : 0.09, 0.03, h === 0.25 ? 0.25 : -0.25);
}
writeWav("bed", reverb(bed, 0.12, 0.8), 0.9);

// ---------- эффекты: пик звука на кадр позже картинки ----------
const P = [];
const F = 1 / 30;
function place(id, name, B, pictureTime, peakOffset, vol) { writeWav(name, B); P.push({ id, src: `assets/sfx/${name}.wav`, start: +(pictureTime + F - peakOffset).toFixed(3), volume: vol, dur: +(B[0].length / SR).toFixed(3) }); }

// нажатия на карточки (тихий щелчок), раскрытие раздела, возврат к выбору
[[1.15, 2600], [3.6, 3400], [6.15, 3200], [9.75, 2900]].forEach(([t, fc], i) => place(`sfx-tap-${i + 1}`, `tap-${i + 1}`, reverb(tick(fc, 50 + i, 1, 0), 0.4, 0.5), t, 0, 0.7));
place("sfx-open-1", "open-1", whoosh(0.5, 400, 3200, 0.55, 6, -0.3, 0.3), 1.45, 0.275, 0.6);
place("sfx-sheen", "sheen", shimmer(0.6, 23), 2.6, 0, 0.3);
place("sfx-lot", "lot", whoosh(0.5, 500, 2600, 0.55, 24, 0.2, -0.2), 3.95, 0.275, 0.55);
place("sfx-back-1", "back-1", suck(0.42, 21), 6.0, 0.42, 0.45);
place("sfx-open-2", "open-2", whoosh(0.5, 450, 3400, 0.55, 7, 0.3, -0.3), 6.45, 0.275, 0.6);
place("sfx-back-2", "back-2", suck(0.42, 22), 9.6, 0.42, 0.45);
place("sfx-open-3", "open-3", whoosh(0.5, 420, 3000, 0.55, 8, -0.3, 0.3), 10.05, 0.275, 0.6);
// карточка выезжает из экрана
place("sfx-focus-2", "focus-2", pop(1000, 270, 0.08, 11), 7.55, 0, 0.55);
place("sfx-focus-3", "focus-3", pop(950, 260, 0.08, 12), 11.05, 0, 0.55);
place("sfx-riser", "riser", riser(1.0, 31), 12.5, 1.0, 0.55);
place("sfx-suck", "suck", suck(0.55, 41), 12.45, 0.55, 0.55);
place("sfx-impact", "impact", impact(2.2, 1.1, 15), 12.5, 0, 0.95);
place("sfx-cta", "cta", pop(1300, 420, 0.06, 99), 12.9, 0, 0.6);

fs.writeFileSync(path.join(OUT, "placements.json"), JSON.stringify(P, null, 2));
console.log(`wrote ${P.length + 1} files`);
