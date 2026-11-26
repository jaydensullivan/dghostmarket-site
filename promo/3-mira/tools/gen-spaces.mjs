// Генерирует compositions/{hook,skins,gifts,topup}.html.
// Переходы повторяют мини-апп (app.css, app-spaces.js): нажатие — карточка 0.98;
// вход — раздел раскрывается из рамки карточки (clip-path), две другие
// карточки уезжают влево/вправо; назад — раздел сжимается в свою карточку,
// другие въезжают с боков. Тайминги мини-аппа × SLOW, чтобы читалось на видео.
// Тексты — дословно из словарей мини-аппа (app-i18n.js / app-i18n-uz.js).
import fs from "node:fs";
const SLOW = 1.4;
// Формат: 9:16 (по умолчанию) или 4:5 (FORMAT=45) — меняется только размещение.
const FMT = process.env.FORMAT === "45" ? "45" : "916";
const LAY = FMT === "45"
  ? { H: 1350, PL: 270, PT: 360, PW: 540, textTop: 96, titleSize: 68, titleLH: 76, subTop: 300, hookTop: 96, hookSize: 84, hookLH: 92, focusTy: 790, logoCY: 532, logoW: 380, dir: "compositions45" }
  : { H: 1920, PL: 160, PT: 600, PW: 760, textTop: 300, titleSize: 76, titleLH: 84, subTop: 526, hookTop: 300, hookSize: 96, hookLH: 104, focusTy: null, logoCY: 464, logoW: 420, dir: "compositions" };
const PW = LAY.PW, PH = Math.round(LAY.PW * 1992 / 1170); // пропорции снимка 1170×1992
const K = PW / 390;                  // экран 390×664 css px → телефон PW×PH
const SW = 390, SH = 664;
const CARD = { x: 13.6, w: 362.8, h: 188, tops: { ru: [163, 362, 559], uz: [196, 394, 592] } };
const KEYS = ["skins", "gifts", "topup"];
const common = fs.readFileSync("compositions/_common.css.txt", "utf8")
  .replace("left: 160px; top: 600px; width: 760px; height: 1294px; border-radius: 64px;", `left: ${LAY.PL}px; top: ${LAY.PT}px; width: ${PW}px; height: ${PH}px; border-radius: ${Math.round(PW * 64 / 760)}px;`)
  .replace(/(\.tag \{[^}]*?)top: 300px;/, `$1top: ${LAY.textTop}px;`)
  .replace(/(\.title \{[^}]*?)top: 346px;([^}]*?)font-size: 76px; line-height: 84px;/, `$1top: ${LAY.textTop + 46}px;$2font-size: ${LAY.titleSize}px; line-height: ${LAY.titleLH}px;`)
  .replace(/(\.sub \{[^}]*?)top: 526px;/, `$1top: ${LAY.subTop}px;`);
fs.mkdirSync(LAY.dir, { recursive: true });
const words = (s) => s.split("|").map((line) => line.trim().split(" ").map((w) => `<span class="w">${w}</span>`).join(" ")).join("<br>");
const px = (v) => (v * K).toFixed(1);
// clip-path рамки карточки i в телефоне (как --sp-ct/--sp-cr/... в app-spaces.js)
const cardClip = (lang, i) => {
  const t = CARD.tops[lang][i];
  const b = Math.max(0, SH - t - CARD.h), r = SW - CARD.x - CARD.w;
  return `inset(${px(Math.max(0, t))}px ${px(r)}px ${px(b)}px ${px(CARD.x)}px round ${px(24)}px)`;
};
const FULL = "inset(0px 0px 0px 0px round 0px)";

const S = {
  skins: { tag: "01 / MARKETPLACE", ink: "#c4a0ff", a: "#7c3aed", b: "#9333ea",
    title: { ru: "Скины CS2 | за сумы", uz: "CS2 skinlar | so'mda" },
    // карточка Covert-лота: блик (dgSheen) → нажатие → фото перелетает в окно лота (dgOpenLot)
    lot: { card: { x: 200, y: 364, w: 174, h: 287 }, photo: { x: 209, y: 375, w: 156, h: 117 }, lotPhoto: { x: 75, y: 84, w: 240, h: 240 }, topH: 548 } },
  gifts: { tag: "02 / GIFTS", ink: "#ffe3f4", a: "#c026d3", b: "#ec4899",
    title: { ru: "Купил — подарок | в Telegram", uz: "Oldingiz — sovg'a | Telegram'da" },
    sub: { ru: "Оплата в сумах", uz: "So'mda to'lov" },
    focus: { x: 17, y: 204, w: 172, h: 270, s: 1.3, tx: 540, ty: 1000 } },
  topup: { tag: "03 / TOP-UP", ink: "#8cb4ff", a: "#4f46e5", b: "#3b82f6",
    title: { ru: "Пополнения | за 1–5 минут", uz: "To'ldirish | 1–5 daqiqada" },
    sub: { ru: "Steam, Stars, игры", uz: "Steam, Stars, o'yinlar" },
    focus: { x: 201, y: 270, w: 172, h: 202, s: 1.4, tx: 540, ty: 1000 } },
};

function homeLayer(p) {
  const cards = ["ru", "uz"].map((l) => KEYS.map((k, i) => {
    const t = CARD.tops[l][i];
    return `<div class="card ${l}" id="${p}-card-${k}-${l}" style="left:${px(CARD.x)}px;top:${px(t)}px;width:${px(CARD.w)}px;height:${px(CARD.h)}px"><img src="assets/screens/${l}-home.jpg" alt="" style="left:${px(-CARD.x)}px;top:${px(-t)}px"></div>`;
  }).join("")).join("\n        ");
  return `<div class="home" id="${p}-home"><img class="ru bg" src="assets/screens/ru-home-bg.jpg" alt=""><img class="uz bg" src="assets/screens/uz-home-bg.jpg" alt="">
        ${cards}</div>`;
}
const scrLayer = (p, key, id, hidden) => `<div class="scr" id="${p}-${id}"${hidden ? ' style="opacity:0"' : ""}><img class="ru" src="assets/screens/ru-${key}.jpg" alt=""><img class="uz" src="assets/screens/uz-${key}.jpg" alt=""></div>`;
const cardSel = (p, k) => `#${p}-card-${k}-ru, #${p}-card-${k}-uz`;

const box = (r) => `left:${px(r.x)}px;top:${px(r.y)}px;width:${px(r.w)}px;height:${px(r.h)}px`;
function lotLayers(p, L) {
  const two = (name) => `<img class="ru" src="assets/screens/ru-${name}.jpg" alt=""><img class="uz" src="assets/screens/uz-${name}.jpg" alt="">`;
  return `<div class="lcard" id="${p}-card" style="${box(L.card)}">${["ru", "uz"].map((l) => `<img class="${l}" src="assets/screens/${l}-skins.jpg" alt="" style="left:${px(-L.card.x)}px;top:${px(-L.card.y)}px">`).join("")}</div>
      <div class="sheen" id="${p}-sheenbox" style="${box(L.photo)}"><div class="bar" id="${p}-sheen"></div></div>
      <div class="lotdim" id="${p}-lotdim"></div>
      <div class="lottop" id="${p}-lot" style="height:${px(L.topH)}px">${two("lot-top")}</div>
      <div class="fly" id="${p}-fly" style="${box(L.photo)}"><div class="a">${two("card-photo")}</div><div class="b" id="${p}-flyb">${two("lot-photo")}</div></div>`;
}
function lotJs(p, L, t0) {
  const d = (0.36 * SLOW).toFixed(2), f = (0.3 * SLOW).toFixed(2);
  return `
      // блик по фото редкой карточки (dgSheen: -70% → 70%, ease-in-out)
      tl.fromTo("#${p}-sheen", { xPercent: -70 }, { xPercent: 70, duration: 1.1, ease: "power1.inOut" }, ${(t0).toFixed(2)});
      // нажатие
      tl.to("#${p}-card", { scale: 0.98, duration: 0.1, ease: "power2.out" }, ${(t0 + 1.15).toFixed(2)});
      tl.to("#${p}-card", { scale: 1, duration: 0.14, ease: "power2.out" }, ${(t0 + 1.25).toFixed(2)});
      // dgOpenLot: фото перелетает в шапку окна лота, всё остальное сменяется затуханием
      tl.fromTo("#${p}-fly", { opacity: 0 }, { opacity: 1, duration: 0.01, immediateRender: false }, ${(t0 + 1.3).toFixed(2)});
      tl.fromTo("#${p}-fly", { x: 0, y: 0, width: ${px(L.photo.w)}, height: ${px(L.photo.h)} },
        { x: ${px(L.lotPhoto.x - L.photo.x)}, y: ${px(L.lotPhoto.y - L.photo.y)}, width: ${px(L.lotPhoto.w)}, height: ${px(L.lotPhoto.h)}, duration: ${d}, ease: "power3.out", immediateRender: false }, ${(t0 + 1.31).toFixed(2)});
      tl.fromTo("#${p}-flyb", { opacity: 0 }, { opacity: 1, duration: ${d}, ease: "power1.inOut", immediateRender: false }, ${(t0 + 1.31).toFixed(2)});
      tl.fromTo("#${p}-lot", { opacity: 0 }, { opacity: 1, duration: ${f}, ease: "power1.out", immediateRender: false }, ${(t0 + 1.31).toFixed(2)});
      tl.fromTo("#${p}-lotdim", { opacity: 0 }, { opacity: 0.7, duration: ${f}, ease: "power1.out", immediateRender: false }, ${(t0 + 1.31).toFixed(2)});
      tl.to("#${p}-fly", { opacity: 0, duration: 0.01 }, ${(t0 + 1.31 + 0.36 * SLOW + 0.05).toFixed(2)});`;
}

// вход в раздел key в момент t: нажатие, раскрытие, остальные карточки разъезжаются
function enterJs(p, key, t, scrId) {
  const others = KEYS.filter((k) => k !== key);
  return `
      tl.to("${cardSel(p, key)}", { scale: 0.98, duration: 0.1, ease: "power2.out" }, ${t.toFixed(2)});
      tl.to("${cardSel(p, key)}", { scale: 1, duration: 0.14, ease: "power2.out" }, ${(t + 0.1).toFixed(2)});
      tl.fromTo("#${p}-${scrId}", { opacity: 1, clipPath: CLIP_${key} }, { opacity: 1, clipPath: "${FULL}", immediateRender: false, duration: ${(0.34 * SLOW).toFixed(2)}, ease: "power3.out" }, ${(t + 0.16).toFixed(2)});
      tl.to("#${p}-home", { opacity: 0, duration: ${(0.34 * SLOW).toFixed(2)}, ease: "power1.inOut" }, ${(t + 0.16).toFixed(2)});
      tl.to("${cardSel(p, others[0])}", { xPercent: -115, opacity: 0, duration: ${(0.28 * SLOW).toFixed(2)}, ease: "power2.inOut" }, ${(t + 0.16).toFixed(2)});
      tl.to("${cardSel(p, others[1])}", { xPercent: 115, opacity: 0, duration: ${(0.28 * SLOW).toFixed(2)}, ease: "power2.inOut" }, ${(t + 0.16).toFixed(2)});`;
}
// назад из раздела prev: он сжимается в свою карточку, другие въезжают с боков
function backJs(p, prev) {
  const others = KEYS.filter((k) => k !== prev);
  const d = 0.3 * SLOW;
  return `
      tl.fromTo("#${p}-prev", { clipPath: "${FULL}", opacity: 1 }, { clipPath: CLIP_${prev}, duration: ${d.toFixed(2)}, ease: "power2.inOut" }, 0);
      tl.to("#${p}-prev", { opacity: 0, duration: ${(d * 0.25).toFixed(2)}, ease: "none" }, ${(d * 0.75).toFixed(2)});
      tl.fromTo("${cardSel(p, others[0])}", { xPercent: -115, opacity: 0 }, { xPercent: 0, opacity: 1, duration: ${d.toFixed(2)}, ease: "power3.out" }, 0);
      tl.fromTo("${cardSel(p, others[1])}", { xPercent: 115, opacity: 0 }, { xPercent: 0, opacity: 1, duration: ${d.toFixed(2)}, ease: "power3.out" }, 0);`;
}

function scene({ p, key, prev, dur, base, exit, hookTitle }) {
  const s = S[key];
  const lot = !hookTitle && s.lot;
  const clipConsts = KEYS.map((k, i) => `const CLIP_${k} = () => (document.documentElement.dataset.lang === "uz" ? "${cardClip("uz", i)}" : "${cardClip("ru", i)}");`).join("\n      ");
  const text = hookTitle
    ? `<div class="title" id="${p}-title" style="top:${LAY.hookTop}px;font-size:${LAY.hookSize}px;line-height:${LAY.hookLH}px"><span class="ru">${words("Три мира — | <g>один бот</g>")}</span><span class="uz">${words("Uch dunyo — | <g>bitta bot</g>")}</span></div>`
    : `<div class="tag" id="${p}-tag">${s.tag}</div>
      <div class="title" id="${p}-title"><span class="ru">${words(s.title.ru)}</span><span class="uz">${words(s.title.uz)}</span></div>
      ${s.sub ? `<div class="sub" id="${p}-sub"><span class="ru">${s.sub.ru}</span><span class="uz">${s.sub.uz}</span></div>` : ""}`;
  const f = s.focus || { x: 0, y: 0, w: 1, h: 1, s: 1, tx: 0, ty: 0 };
  const focusHtml = hookTitle || lot ? "" : `<div class="dim" id="${p}-dim"></div>
    <div class="focus" id="${p}-focus"><img class="ru" src="assets/screens/ru-${key}.jpg" alt=""><img class="uz" src="assets/screens/uz-${key}.jpg" alt=""></div>
    ${s.chip ? `<div class="chip" id="${p}-chip"><span class="ru">${s.chip.ru}</span><span class="uz">${s.chip.uz}</span></div>` : ""}`;
  const fieldA = hookTitle ? "#7B2CFF" : s.a, fieldB = hookTitle ? "#FF2BD6" : s.b;
  const T = dur;
  let js = "";
  if (hookTitle) {
    js += enterJs(p, key, 1.15, "scr");
    js += `
      tl.to("#${p}-title .w", { opacity: 0, filter: "blur(10px)", duration: 0.18, ease: "power3.in", stagger: 0.03 }, 1.2);
      tl.fromTo("#${p}-field2", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, 1.3);`;
  } else {
    if (prev) {
      js += backJs(p, prev);
      js += enterJs(p, key, 0.55, "scr");
      js += `
      tl.to("#${p}-field0", { opacity: 0, duration: 0.5, ease: "power2.inOut" }, 0);
      tl.fromTo("#${p}-field", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, 0.7);`;
    }
    js += `
      tl.fromTo("#${p}-tag", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.3, ease: "expo.out" }, ${(base + 0.1).toFixed(2)});
      tl.fromTo("#${p}-title .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out", stagger: 0.067 }, ${(base + 0.18).toFixed(2)});
      ${s.sub ? `tl.fromTo("#${p}-sub", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, ${(base + 0.6).toFixed(2)});` : ""}
      ${lot ? lotJs(p, s.lot, base + 0.45) : `// главное на экране выезжает из телефона целиком, телефон за ним темнеет
      tl.fromTo("#${p}-focus", { opacity: 0, x: 0, y: 0, scale: 1 }, { opacity: 1, duration: 0.01 }, ${(base + 0.9).toFixed(2)});
      tl.to("#${p}-focus", { x: ${(f.tx - (LAY.PL + (f.x + f.w / 2) * K)).toFixed(1)}, y: ${((LAY.focusTy ?? f.ty) - (LAY.PT + (f.y + f.h / 2) * K)).toFixed(1)}, scale: ${f.s}, duration: 0.6, ease: "expo.out" }, ${(base + 0.91).toFixed(2)});
      tl.fromTo("#${p}-dim", { opacity: 0 }, { opacity: 0.55, duration: 0.4, ease: "power2.out" }, ${(base + 0.9).toFixed(2)});`}
      ${s.chip ? `tl.fromTo("#${p}-chip", { scale: 0.4, opacity: 0, y: 30, transformOrigin: "0% 50%" }, { scale: 1, opacity: 1, y: 0, duration: 0.5, ease: "elastic.out(1,0.7)" }, ${(base + 1.35).toFixed(2)});
      tl.to("#${p}-chip", { opacity: 0, y: 20, duration: 0.18, ease: "power3.in" }, ${(T - 0.5).toFixed(2)});` : ""}`;
    if (exit === "back") js += `
      tl.to("${lot ? `#${p}-lot, #${p}-lotdim` : `#${p}-focus, #${p}-dim`}", { opacity: 0, duration: 0.25, ease: "power2.in" }, ${(T - 0.45).toFixed(2)});
      tl.to("#${p}-text", { opacity: 0, filter: "blur(8px)", duration: 0.22, ease: "power3.in" }, ${(T - 0.3).toFixed(2)});`;
    if (exit === "carry") js += `
      tl.to("#${p}-focus, #${p}-dim", { opacity: 0, duration: 0.2, ease: "power2.in" }, ${(T - 0.75).toFixed(2)});
      tl.to("#${p}-text", { opacity: 0, filter: "blur(8px)", duration: 0.22, ease: "power3.in" }, ${(T - 0.55).toFixed(2)});
      tl.to("#${p}-phone", { scale: ${(LAY.logoW * 0.31 / PW).toFixed(3)}, y: ${(LAY.logoCY - (LAY.PT + PH / 2)).toFixed(1)}, borderRadius: 140, duration: 0.55, ease: "power3.inOut" }, ${(T - 0.55).toFixed(2)});
      tl.to("#${p}-phone", { opacity: 0, duration: 0.12, ease: "power1.in" }, ${(T - 0.14).toFixed(2)});
      tl.to("#${p}-field", { opacity: 0, duration: 0.5, ease: "power2.inOut" }, ${(T - 0.5).toFixed(2)});`;
  }
  const prevA = prev ? S[prev].a : "#7B2CFF", prevB = prev ? S[prev].b : "#FF2BD6";
  return `<template>
  <style>
${common}
    #root .fld { position: absolute; inset: 0; }
    #root #${p}-field0 { background: radial-gradient(85% 50% at 25% 20%, ${prevA}cc, ${prevB}33 55%, rgba(8,7,13,0) 80%); }
    #root #${p}-field { background: radial-gradient(85% 50% at 25% 20%, ${fieldA}${hookTitle ? "66" : "cc"}, ${fieldB}${hookTitle ? "1f" : "33"} 55%, rgba(8,7,13,0) 80%); }
    #root #${p}-field2 { background: radial-gradient(85% 50% at 25% 20%, ${S.skins.a}cc, ${S.skins.b}33 55%, rgba(8,7,13,0) 80%); }
    #root .tag { color: ${s.ink}; }
    .g { background: linear-gradient(90deg, #A855F7, #FF2BD6); -webkit-background-clip: text; background-clip: text; color: transparent; }
    .home, .home .bg { position: absolute; left: 0; top: 0; width: ${PW}px; height: ${PH}px; }
    .home .card { position: absolute; overflow: hidden; border-radius: ${px(24)}px; }
    .home .card img { position: absolute; width: ${PW}px; height: ${PH}px; }
    .lcard { position: absolute; overflow: hidden; border-radius: ${px(16)}px; }
    .lcard img { position: absolute; width: ${PW}px; height: ${PH}px; }
    .sheen { position: absolute; overflow: hidden; border-radius: ${px(10)}px; }
    .sheen .bar { position: absolute; left: -60%; top: -40%; width: 220%; height: 180%; background: linear-gradient(105deg, transparent 42%, rgba(255,255,255,.16) 50%, transparent 58%); }
    .lotdim { position: absolute; inset: 0; background: #08070D; opacity: 0; }
    .lottop { position: absolute; left: 0; top: 0; width: ${PW}px; overflow: hidden; opacity: 0; border-radius: 0 0 34px 34px; box-shadow: 0 30px 70px rgba(0,0,0,0.6); }
    .lottop img { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
    .fly { position: absolute; overflow: hidden; opacity: 0; border-radius: ${px(12)}px; }
    .fly .a, .fly .b { position: absolute; inset: 0; }
    .fly img { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
    .dim { position: absolute; left: ${LAY.PL}px; top: ${LAY.PT}px; width: ${PW}px; height: ${PH}px; border-radius: ${Math.round(PW * 64 / 760)}px; background: #08070D; opacity: 0; }
    .focus { position: absolute; left: ${(LAY.PL + f.x * K).toFixed(1)}px; top: ${(LAY.PT + f.y * K).toFixed(1)}px; width: ${(f.w * K).toFixed(1)}px; height: ${(f.h * K).toFixed(1)}px;
             border-radius: 26px; overflow: hidden; opacity: 0; box-shadow: 0 30px 80px rgba(0,0,0,0.6); z-index: 4; }
    .focus img { position: absolute; left: ${(-f.x * K).toFixed(1)}px; top: ${(-f.y * K).toFixed(1)}px; width: ${PW}px; height: ${PH}px; }
    .chip { position: absolute; left: 120px; top: 612px; padding: 22px 34px; border-radius: 24px; background: #fff; color: #120a22; font-weight: 800; font-size: 40px; white-space: nowrap; box-shadow: 0 20px 50px rgba(0,0,0,0.45); z-index: 5; }
  </style>
  <div id="root" data-composition-id="${p}" data-width="1080" data-height="${LAY.H}" data-layout-allow-overflow data-layout-allow-overlap>
    ${prev ? `<div class="fld" id="${p}-field0"></div>` : ""}
    <div class="fld" id="${p}-field"></div>
    ${hookTitle ? `<div class="fld" id="${p}-field2" style="opacity:0"></div>` : ""}
    <div id="${p}-text">
      ${text}
    </div>
    <div class="phone" id="${p}-phone">
      ${prev || hookTitle ? homeLayer(p) : ""}
      ${scrLayer(p, key, "scr", !!(prev || hookTitle))}
      ${lot ? lotLayers(p, s.lot) : ""}
      ${prev ? scrLayer(p, prev, "prev") : ""}
    </div>
    ${focusHtml}
  </div>
  <script>
    (function () {
      // позиция карточки зависит от языка (lang ставит index.html) — читаем при первом кадре анимации
      ${clipConsts}
      const tl = gsap.timeline({ paused: true });
      ${js}
      window.__timelines["${p}"] = tl;
    })();
  </script>
</template>
`.replace(/<g>(.*?)<\/g>/g, (m, inner) => inner).replace(/<span class="w">([^<]*)<\/span>/g, (m, w) => m);
}

// заголовок хука: «один бот» градиентом бренда
let hook = scene({ p: "hook", key: "skins", dur: 2.0, hookTitle: true });
hook = hook.replace('<span class="w">один</span> <span class="w">бот</span>', '<span class="w g">один</span> <span class="w g">бот</span>')
           .replace('<span class="w">bitta</span> <span class="w">bot</span>', '<span class="w g">bitta</span> <span class="w g">bot</span>');
fs.writeFileSync(`${LAY.dir}/hook.html`, hook);
fs.writeFileSync(`${LAY.dir}/skins.html`, scene({ p: "skins", key: "skins", dur: 3.6, base: 0, exit: "back" }));
fs.writeFileSync(`${LAY.dir}/gifts.html`, scene({ p: "gifts", key: "gifts", prev: "skins", dur: 3.6, base: 1.05, exit: "back" }));
fs.writeFileSync(`${LAY.dir}/topup.html`, scene({ p: "topup", key: "topup", prev: "gifts", dur: 3.3, base: 0.95, exit: "carry" }));
console.log("ok");
