"""Картинки превью для страниц цен (og:image): 1200×630, фото скина на фоне
DGhost с подсветкой цветом редкости, название, логотип и адрес сайта.

    python3 tools/og_cards.py            # дорисовать недостающие (новые скины)
    python3 tools/og_cards.py --force    # перерисовать все
    python3 tools/og_cards.py ak-47-asiimov awp-dragon-lore   # только эти

Нужен Pillow (pip install pillow) — поэтому отдельно от tools/build.py,
который работает на одной стандартной библиотеке. Скины и фото — те же, что
у страниц цен (data/skins-meta.json, data/skinport.json, data/rate.json).
Цены на картинке нет: она меняется каждый день, а картинка рисуется один раз.
Слов на языке тоже нет — одна картинка на RU / UZ / EN.

Готовые файлы — og/prices/<slug>.jpg; build.py ставит их в og:image, а если
файла нет — фото скина из Steam.
"""

import io
import os
import sys
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skins  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'og', 'prices')
FONTS = os.path.join(ROOT, 'tools', 'og-fonts')
W, H = 1200, 630
BG = (8, 7, 13)
BRAND = (123, 44, 255)


def font(name, size, weight):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def hex_rgb(h, default=BRAND):
    h = (h or '').lstrip('#')
    if len(h) != 6:
        return default
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def glow(color, cx, cy, rx, ry, alpha):
    """Мягкое пятно цвета (радиальная подсветка) на прозрачном слое W×H."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color + (alpha,))
    return layer.filter(ImageFilter.GaussianBlur(max(rx, ry) // 2))


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Перенос по словам; не влезает в max_lines — None (уменьшим шрифт)."""
    words, lines, cur = text.split(), [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
            if draw.textlength(cur, font=fnt) > max_w:
                return None
    if cur:
        lines.append(cur)
    return lines if len(lines) <= max_lines else None


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'dghostmarket-site-og/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception:
            time.sleep(1 + i)
    return None


def card(skin, photo, logo):
    color = hex_rgb(skin.get('rarity_color'))
    im = Image.new('RGBA', (W, H), BG + (255,))
    im.alpha_composite(glow(color, 820, 330, 360, 250, 120))
    im.alpha_composite(glow(BRAND, 150, 80, 300, 200, 70))
    # Фото скина справа, крупно, с тенью.
    if photo is not None:
        ph = photo.convert('RGBA')
        scale = min(620 / ph.width, 500 / ph.height)
        ph = ph.resize((int(ph.width * scale), int(ph.height * scale)), Image.LANCZOS)
        x, y = 1170 - ph.width, (H - ph.height) // 2 + 10
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 150), (x + 18, y + 28), ph.split()[3])
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
        im.alpha_composite(ph, (x, y))
    d = ImageDraw.Draw(im)
    # Логотип сверху слева.
    if logo is not None:
        lg = logo.convert('RGBA')
        lg = lg.resize((int(lg.width * 92 / lg.height), 92), Image.LANCZOS)
        im.alpha_composite(lg, (64, 52))
    # Оружие мелко, название скина крупно (переносим и уменьшаем, чтобы влезло).
    base = skin['base']
    weapon, _, finish = base.partition('|')
    weapon, finish = weapon.strip(), finish.strip() or base
    max_w = 470
    for size in (76, 66, 58, 50, 44, 38):
        f_big = font('Unbounded-latin.ttf', size, 800)
        lines = fit_lines(d, finish, f_big, max_w, 3)
        if lines:
            break
    lines = lines or [finish]
    f_small = font('Inter-latin.ttf', 34, 600)
    line_h = int(size * 1.12)
    block_h = 46 + len(lines) * line_h
    y0 = 330 - block_h // 2 + 20
    d.text((64, y0), weapon, font=f_small, fill=(196, 160, 255))
    for i, ln in enumerate(lines):
        d.text((64, y0 + 46 + i * line_h), ln, font=f_big, fill=(255, 255, 255))
    # Полоса цвета редкости и адрес сайта снизу.
    d.rounded_rectangle((64, 528, 64 + 120, 536), radius=4, fill=color)
    d.text((64, 552), 'dghostmarket.uz', font=font('Inter-latin.ttf', 30, 700), fill=(242, 238, 250))
    return im.convert('RGB')


def main(argv):
    force = '--force' in argv
    only = {a for a in argv if not a.startswith('--')}
    inputs, err = skins.load_inputs(ROOT)
    if not inputs:
        print('Нет данных для скинов:', err)
        return 1
    meta, market, rate = inputs
    keep = {n for n in os.listdir(os.path.join(ROOT, 'prices')) if os.path.isdir(os.path.join(ROOT, 'prices', n))}
    items = skins.collect(meta, market, rate, keep)
    os.makedirs(OUT, exist_ok=True)
    logo = Image.open(os.path.join(ROOT, 'logo-h240.webp'))
    made = skipped = failed = 0
    for s in items:
        if only and s['slug'] not in only:
            continue
        path = os.path.join(OUT, s['slug'] + '.jpg')
        if os.path.exists(path) and not force and not only:
            skipped += 1
            continue
        raw = fetch(s['image']) if s.get('image') else None
        photo = None
        if raw:
            try:
                photo = Image.open(io.BytesIO(raw))
            except Exception:
                photo = None
        if photo is None:
            failed += 1
            continue
        card(s, photo, logo).save(path, 'JPEG', quality=80, optimize=True, progressive=True)
        made += 1
    print(f'Картинки превью: нарисовано {made}, уже были {skipped}, без фото {failed}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
