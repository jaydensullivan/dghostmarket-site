#!/usr/bin/env python3
"""Сборка сайта dghostmarket.uz из шаблона и живых лотов.

    python3 tools/build.py

Шаблон — src/index.html (русский текст прямо в разметке), переводы —
i18n.json. На выходе — готовые страницы, которые видят поисковики:

    index.html, uz/index.html, en/index.html — лендинг на трёх языках;
    skins/index.html (+ uz/, en/) — цены на скины из лотов маркета;
    prices/index.html, prices/<скин>/index.html (+ uz/, en/) — рыночные цены
        популярных скинов в сумах (tools/skins.py);
    guides/index.html, guides/<статья>/index.html (+ uz/) — инструкции (tools/guides.py);
    sitemap.xml, robots.txt.

Лоты берутся из открытого API бота (/api/skins). Если API недоступен,
используется прошлая выгрузка data/lots.json — страница цен не обнуляется.
Только стандартная библиотека Python: запускается в GitHub Actions
(.github/workflows/build.yml) раз в сутки и после правок шаблона.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request

import guides
import skins

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://dghostmarket.uz'
API = 'https://api.dghostmarket.uz/api/skins'
APP = 'https://app.dghostmarket.uz/'
LANGS = ['ru', 'uz', 'en']
PREVIEW = 6

WEAR = {
    'ru': {'FN': 'Прямо с завода', 'MW': 'Немного поношенное', 'FT': 'После полевых испытаний', 'WW': 'Поношенное', 'BS': 'Закалённое в боях'},
    'uz': {'FN': 'Zavoddan yangi', 'MW': 'Biroz ishlatilgan', 'FT': 'Dala sinovidan keyin', 'WW': 'Eskirgan', 'BS': 'Jangda toblangan'},
    'en': {'FN': 'Factory New', 'MW': 'Minimal Wear', 'FT': 'Field-Tested', 'WW': 'Well-Worn', 'BS': 'Battle-Scarred'},
}

# Тексты сгенерированных частей (превью лотов и страница цен).
L = {
    'ru': {
        'cur': 'сум', 'buy': 'Купить', 'below': 'на {p}% дешевле рынка', 'market': 'Рынок Steam: {v}',
        'preview_title': 'Сейчас в продаже', 'preview_sub': 'Лоты от проверенных продавцов — сделка через гаранта.',
        'all_prices': 'Все цены →',
        'cat_title': 'Цены на скины CS2 в сумах',
        'cat_doc_title': 'Цены на скины CS2 в сумах — DGhostMarket',
        'cat_desc': 'Актуальные цены на скины CS2 в сумах: {n} лотов на DGhostMarket, обновлено {d}. Ножи, перчатки, AK-47, AWP — с float и паттерном. Сделка через гаранта.',
        'cat_lead': 'Все лоты, которые сейчас продаются на DGhostMarket. Цены в сумах, обновляются каждый день. Оплата удерживается площадкой, пока предмет не придёт в ваш Steam.',
        'updated': 'Обновлено {d} · лотов: {n}',
        'empty': 'Сейчас лотов нет — загляните позже или откройте маркет в Telegram.',
        'float': 'Float', 'other': 'Другое',
        'home': 'Главная', 'market_prices': 'Рыночные цены всех скинов →', 'guides': 'Как купить и продать — инструкции →',
    },
    'uz': {
        'cur': "so'm", 'buy': 'Sotib olish', 'below': "bozordan {p}% arzon", 'market': 'Steam bozori: {v}',
        'preview_title': 'Hozir sotuvda', 'preview_sub': "Tekshirilgan sotuvchilarning lotlari — bitim kafil orqali.",
        'all_prices': 'Barcha narxlar →',
        'cat_title': "CS2 skinlari narxlari so'mda",
        'cat_doc_title': "CS2 skinlari narxlari so'mda — DGhostMarket",
        'cat_desc': "CS2 skinlarining so'mdagi dolzarb narxlari: DGhostMarket'da {n} ta lot, {d} yangilandi. Pichoqlar, qo'lqoplar, AK-47, AWP — float va naqsh bilan. Bitim kafil orqali.",
        'cat_lead': "DGhostMarket'da hozir sotilayotgan barcha lotlar. Narxlar so'mda, har kuni yangilanadi. Buyum Steam'ingizga kelmaguncha to'lov platformada ushlab turiladi.",
        'updated': '{d} yangilandi · lotlar: {n}',
        'empty': "Hozircha lotlar yo'q — keyinroq kiring yoki marketni Telegramda oching.",
        'float': 'Float', 'other': 'Boshqa',
        'home': 'Bosh sahifa', 'market_prices': 'Barcha skinlarning bozor narxlari →', 'guides': 'Qanday sotib olish va sotish — qo‘llanmalar →',
    },
    'en': {
        'cur': 'UZS', 'buy': 'Buy', 'below': '{p}% below market', 'market': 'Steam market: {v}',
        'preview_title': 'On sale now', 'preview_sub': 'Listings from verified sellers — every deal goes through escrow.',
        'all_prices': 'All prices →',
        'cat_title': 'CS2 skin prices in Uzbek sum',
        'cat_doc_title': 'CS2 skin prices in UZS — DGhostMarket',
        'cat_desc': 'Current CS2 skin prices in Uzbek sum: {n} listings on DGhostMarket, updated {d}. Knives, gloves, AK-47, AWP — with float and pattern. Escrow-protected deals.',
        'cat_lead': 'Every listing currently on sale at DGhostMarket. Prices in Uzbek sum, updated daily. The platform holds the payment until the item reaches your Steam.',
        'updated': 'Updated {d} · listings: {n}',
        'empty': 'No listings right now — check back later or open the market in Telegram.',
        'float': 'Float', 'other': 'Other',
        'home': 'Home', 'market_prices': 'Market prices of all skins →',
    },
}

EXTRA_CSS = """
.lots{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.lot{display:flex;flex-direction:column;background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:16px;text-decoration:none;color:inherit}
.lot img{width:100%;aspect-ratio:4/3;object-fit:contain;background:radial-gradient(ellipse at 50% 40%,#2a2238,#130e1c 70%);border-radius:12px;margin-bottom:12px}
.lot h3{margin:0 0 4px;font-size:16px;line-height:1.3}
.lot .sub{color:var(--muted);font-size:13px;margin-bottom:10px}
.lot .row{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:auto}
.lot .price{font-weight:700;font-size:18px}
.lot .tag{font-size:12px;color:#7CF2A5}
.lot .go{background:var(--grad);color:#fff;border-radius:999px;padding:6px 14px;font-weight:600;font-size:13px;white-space:nowrap}
.cat-group{margin:36px 0 14px;font-size:20px}
.crumbs{color:var(--muted);font-size:14px;margin:24px 0 8px}
.crumbs a{color:var(--muted)}
.more{margin-top:20px}
@media(max-width:900px){.lots{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.lots{grid-template-columns:1fr}}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def txt(s):
    """Текст между тегами — кавычки можно не экранировать."""
    return html.escape(str(s), quote=False)


def money(n):
    return f'{int(n):,}'.replace(',', ' ')


def page_url(lang, kind):
    """kind: 'home', 'skins', 'prices' или 'prices/<скин>'."""
    base = '' if lang == 'ru' else f'/{lang}'
    return f'{SITE}{base}/' if kind == 'home' else f'{SITE}{base}/{kind}/'


def load_lots():
    cache = os.path.join(ROOT, 'data', 'lots.json')
    try:
        req = urllib.request.Request(API, headers={'User-Agent': 'dghostmarket-site-build'})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode('utf-8'))
        lots = data if isinstance(data, list) else data.get('skins', [])
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        keep = ['id', 'title', 'wear', 'stattrak', 'price', 'photo_url', 'float_value', 'pattern',
                'weapon_type', 'market_price_uzs', 'view_count', 'created_at']
        lots = [{k: s.get(k) for k in keep} for s in lots if s.get('id') and s.get('price')]
        json.dump(lots, open(cache, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        return lots, True
    except Exception as e:  # API недоступен — прошлая выгрузка
        print(f'⚠️ API недоступен ({e!r}) — беру data/lots.json', file=sys.stderr)
        try:
            return json.load(open(cache, encoding='utf-8')), False
        except Exception:
            return [], False


def lot_card(s, lang):
    t = L[lang]
    name = ('StatTrak™ ' if s.get('stattrak') else '') + (s.get('title') or '')
    sub = [s.get('weapon_type') if s.get('weapon_type') and s.get('weapon_type') not in name else '',
           WEAR[lang].get(s.get('wear') or '', '')]
    if s.get('float_value') is not None:
        sub.append(f"{t['float']} {float(s['float_value']):.4f}")
    sub = ' · '.join(x for x in sub if x)
    price = int(s['price'])
    market = s.get('market_price_uzs')
    tag = ''
    if market and market > price:
        p = round((1 - price / market) * 100)
        if p >= 1:
            tag = f'<span class="tag">{esc(t["below"].format(p=p))}</span>'
    img = f'<img src="{esc(s["photo_url"])}" alt="{esc(name)}" loading="lazy" width="320" height="240">' if s.get('photo_url') else ''
    return (f'<a class="lot" href="{APP}?open=skin_{int(s["id"])}" rel="nofollow">{img}'
            f'<h3>{esc(name)}</h3><div class="sub">{esc(sub)}</div>'
            f'<div class="row"><div><div class="price">{money(price)} {esc(t["cur"])}</div>{tag}</div>'
            f'<span class="go">{esc(t["buy"])}</span></div></a>')


def offers_jsonld(lots, lang):
    items = []
    for i, s in enumerate(lots[:50]):
        name = ('StatTrak™ ' if s.get('stattrak') else '') + (s.get('title') or '')
        if s.get('wear'):
            name += f" ({WEAR['en'].get(s['wear'], s['wear'])})"
        prod = {'@type': 'Product', 'name': name, 'category': s.get('weapon_type') or 'CS2 skin',
                'offers': {'@type': 'Offer', 'price': int(s['price']), 'priceCurrency': 'UZS',
                           'availability': 'https://schema.org/InStock', 'url': f'{APP}?open=skin_{int(s["id"])}'}}
        if s.get('photo_url'):
            prod['image'] = s['photo_url']
        items.append({'@type': 'ListItem', 'position': i + 1, 'item': prod})
    return {'@context': 'https://schema.org', '@type': 'ItemList', 'name': L[lang]['cat_title'],
            'numberOfItems': len(lots), 'itemListElement': items}


def site_jsonld(lang):
    return [
        {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'DGhostMarket', 'url': SITE + '/',
         'logo': SITE + '/apple-touch-icon.png', 'email': 'support@dghostmarket.com',
         'sameAs': ['https://t.me/dghostmarketbot', 'https://t.me/dghostmarket']},
        {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'DGhostMarket', 'url': page_url(lang, 'home'),
         'inLanguage': lang},
    ]


def alternates(kind, langs=LANGS):
    out = [f'<link rel="alternate" hreflang="{l}" href="{page_url(l, kind)}">' for l in langs]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("ru", kind)}">')
    return '\n'.join(out)


def localize(tpl, lang, i18n, css=''):
    """Шаблон (русский) → страница на языке lang."""
    s = tpl
    if lang != 'ru':
        d = i18n[lang]

        def sub_text(m):
            key = m.group(3)
            return m.group(1) + (txt(d[key]) if key in d else m.group(4)) + m.group(5)

        def sub_html(m):
            key = m.group(3)
            return m.group(1) + (d[key] if key in d else m.group(4)) + m.group(5)

        s = re.sub(r'(<(\w+)\b[^>]*\sdata-i18n="([^"]+)"[^>]*>)(.*?)(</\2>)', sub_text, s, flags=re.S)
        s = re.sub(r'(<(\w+)\b[^>]*\sdata-i18n-html="([^"]+)"[^>]*>)(.*?)(</\2>)', sub_html, s, flags=re.S)
        s = s.replace('<html lang="ru">', f'<html lang="{lang}">')
        s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{txt(d["_title"])}</title>', s, count=1)
        s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(d['_description']), s, count=1)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(d['_title']), s, count=1)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(d['_og_description']), s, count=1)
        s = s.replace('aria-label="Язык"', 'aria-label="Language"')
    # Активная кнопка языка и ссылки внутри языка.
    s = re.sub(r'(<a href="[^"]*" data-lang="(\w+)")( class="on")?', lambda m: m.group(1) + (' class="on"' if m.group(2) == lang else ''), s)
    prefix = '' if lang == 'ru' else f'/{lang}'
    s = s.replace('href="/skins/"', f'href="{prefix}/skins/"').replace('href="/prices/"', f'href="{prefix}/prices/"')
    # Картинки и иконки — от корня сайта (страницы лежат и в подпапках).
    s = re.sub(r'(href|src)="(favicon\.png|apple-touch-icon\.png|logo\.webp|og\.jpg)"', r'\1="/\2"', s)
    s = s.replace('</style>', EXTRA_CSS + css + '</style>', 1)
    return s


def set_meta(s, lang, kind, title=None, desc=None, langs=LANGS):
    url = page_url(lang, kind)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, s, count=1)
    if title:
        s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{txt(title)}</title>', s, count=1)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title), s, count=1)
    if desc:
        s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), s, count=1)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), s, count=1)
    return s.replace('<!--ALTERNATES-->', alternates(kind, langs))


def jsonld_tag(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def preview_section(lots, lang):
    t = L[lang]
    if not lots:
        return ''
    top = sorted(lots, key=lambda s: (-(s.get('view_count') or 0), -(s.get('id') or 0)))[:PREVIEW]
    prefix = '' if lang == 'ru' else f'/{lang}'
    return (f'<section id="lots"><div class="wrap"><div class="sec-head"><h2>{esc(t["preview_title"])}</h2>'
            f'<p>{esc(t["preview_sub"])}</p></div><div class="lots">'
            + ''.join(lot_card(s, lang) for s in top)
            + f'</div><p class="more"><a class="btn ghost" href="{prefix}/skins/">{esc(t["all_prices"])}</a> '
            f'<a class="btn ghost" href="{prefix}/prices/">{esc(t["market_prices"])}</a></p></div></section>')


def catalog_main(lots, lang, today):
    t = L[lang]
    prefix = '' if lang == 'ru' else f'/{lang}'
    # Одна сетка, от дорогих к дешёвым: при 1–3 лотах на оружие группы по
    # оружию давали пустые ряды с одной карточкой.
    ordered = sorted(lots, key=lambda s: -int(s['price']))
    body = ('<div class="lots">' + ''.join(lot_card(s, lang) for s in ordered) + '</div>') if ordered else f'<p>{esc(t["empty"])}</p>'
    return (f'<main id="top"><div class="wrap"><nav class="crumbs"><a href="{prefix}/">{esc(t["home"])}</a> / {esc(t["cat_title"])}</nav>'
            f'<h1>{esc(t["cat_title"])}</h1><p class="lead">{esc(t["cat_lead"])}</p>'
            f'<p class="crumbs">{esc(t["updated"].format(d=today, n=len(lots)))}</p>{body}'
            f'<p class="more"><a class="btn ghost" href="{prefix}/prices/">{esc(t["market_prices"])}</a>'
            + (f' <a class="btn ghost" href="{prefix}/guides/">{esc(t["guides"])}</a>' if t.get('guides') else '')
            + '</p></div></main>')


def tag_links(text, page):
    """Метка перехода для «Аналитика» бота: ссылки в мини-апп получают
    src=site_<page>, в бота — /start site_<page>."""
    src = f'site_{page}'

    def app(m):
        url = m.group(1)
        if 'src=' in url:
            return m.group(0)
        sep = '&amp;' if '?' in url else '?'
        return f'href="{url}{sep}src={src}"'

    text = re.sub(r'href="(https://app\.dghostmarket\.com/[^"]*)"', app, text)
    return text.replace('href="https://t.me/dghostmarketbot"', f'href="https://t.me/dghostmarketbot?start={src}"')


def write(rel, text):
    """Пишет файл, только если он изменился. True — файл новый или другой."""
    path = os.path.join(ROOT, rel)
    try:
        if open(path, encoding='utf-8').read() == text:
            return False
    except OSError:
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return True


def build_prices(tpl, i18n, lots, iso):
    """Страницы рыночных цен. Возвращает {путь страницы: дата изменения} для sitemap."""
    lm_path = os.path.join(ROOT, 'data', 'prices-lastmod.json')
    try:
        lastmod = json.load(open(lm_path, encoding='utf-8'))
    except Exception:
        lastmod = {}
    inputs, err = skins.load_inputs(ROOT)
    if not inputs:
        print(f'⚠️ Нет данных для цен ({err}) — страницы цен не трогаю', file=sys.stderr)
        return {k: v for k, v in lastmod.items() if os.path.exists(os.path.join(ROOT, k, 'index.html'))}
    meta, market, rate = inputs
    keep = {k.split('/')[-1] for k in lastmod if k.startswith('prices/')}
    items = skins.collect(meta, market, rate, keep)
    if not items:
        print('⚠️ Ни одного скина с ценой — страницы цен не трогаю', file=sys.stderr)
        return lastmod
    by_weapon = {}
    for s in items:
        by_weapon.setdefault(s['weapon'], []).append(s)
    new, changed = {}, []

    def put(rel, text):
        # Переключатель языка ведёт на ту же страницу, а не на главную.
        path = rel.split('/', 1)[1] if rel.split('/')[0] in LANGS else rel
        for l in LANGS:
            text = text.replace(f'href="{"/" if l == "ru" else f"/{l}/"}" data-lang="{l}"',
                                f'href="{"" if l == "ru" else f"/{l}"}/{path}/" data-lang="{l}"')
        if write(rel + '/index.html', text) or rel not in lastmod:
            new[rel] = iso
            changed.append(rel)
        else:
            new[rel] = lastmod[rel]

    for lang in LANGS:
        page = localize(tpl, lang, i18n, skins.CSS)
        t = skins.T[lang]
        base = '' if lang == 'ru' else f'{lang}/'
        hub = set_meta(page, lang, 'prices', t['hub_title'], t['hub_desc'].format(n=len(items)))
        hub = hub.replace('<!--JSONLD-->', '')
        hub = re.sub(r'<main id="top">.*?</main>', lambda m: skins.hub_main(items, lang), hub, count=1, flags=re.S)
        put(base + 'prices', tag_links(hub, 'prices'))
        for s in items:
            kind = f'prices/{s["slug"]}'
            title = t['title'].format(name=s['base'])
            desc = t['desc'].format(name=s['base'], low=skins.money(s['low']), st=t['st_desc'] if s['stattrak'] else '')
            out = set_meta(page, lang, kind, title, desc)
            out = out.replace('<!--JSONLD-->', jsonld_tag(skins.skin_jsonld(s, lang, page_url(lang, kind))))
            same = by_weapon.get(s['weapon'], [])
            i = same.index(s)
            related = (same[i + 1:] + same[:i])[:skins.RELATED]
            body = skins.skin_main(s, lang, lots, related, rate, lot_card)
            out = re.sub(r'<main id="top">.*?</main>', lambda m: body, out, count=1, flags=re.S)
            put(base + kind, tag_links(out, 'price'))
    # Страницы, которые больше не собираются (скина нет в справочнике), оставляем в sitemap.
    for k, v in lastmod.items():
        if k not in new and os.path.exists(os.path.join(ROOT, k, 'index.html')):
            new[k] = v
    write('data/prices-lastmod.json', json.dumps(dict(sorted(new.items())), ensure_ascii=False, indent=0) + '\n')
    print(f'Цены: {len(items)} скинов, страниц {len(new)}, изменено {len(changed)}, курс {rate}')
    return new


def build_guides(tpl, i18n, iso):
    """Инструкции (ru, uz). Возвращает {путь: дата изменения} для sitemap."""
    lm_path = os.path.join(ROOT, 'data', 'guides-lastmod.json')
    try:
        lastmod = json.load(open(lm_path, encoding='utf-8'))
    except Exception:
        lastmod = {}
    new = {}

    def put(rel, kind, text):
        # Переключатель языка: ru/uz — та же статья, en — английская главная.
        for l in LANGS:
            href = f'{guides.prefix(l)}/{kind}/' if l in guides.LANGS else '/en/'
            text = text.replace(f'href="{"/" if l == "ru" else f"/{l}/"}" data-lang="{l}"', f'href="{href}" data-lang="{l}"')
        text = tag_links(text, 'guide')
        changed = write(rel + '/index.html', text)
        new[rel] = iso if changed or rel not in lastmod else lastmod[rel]

    for lang in guides.LANGS:
        page = localize(tpl, lang, i18n, guides.CSS)
        t = guides.T[lang]
        base = '' if lang == 'ru' else f'{lang}/'
        hub = set_meta(page, lang, 'guides', t['hub_title'], t['hub_desc'], guides.LANGS)
        hub = hub.replace('<!--JSONLD-->', '')
        hub = re.sub(r'<main id="top">.*?</main>', lambda m: guides.hub_main(lang), hub, count=1, flags=re.S)
        put(base + 'guides', 'guides', hub)
        for g in guides.GUIDES:
            kind = f'guides/{g["slug"]}'
            d = g[lang]
            out = set_meta(page, lang, kind, d['title'] + ' | DGhostMarket', d['desc'], guides.LANGS)
            out = out.replace('<!--JSONLD-->', jsonld_tag(guides.article_jsonld(g, lang, page_url(lang, kind), SITE)))
            body = guides.guide_main(g, lang)
            out = re.sub(r'<main id="top">.*?</main>', lambda m: body, out, count=1, flags=re.S)
            put(base + kind, kind, out)
    write('data/guides-lastmod.json', json.dumps(dict(sorted(new.items())), ensure_ascii=False, indent=0) + '\n')
    return new


def main():
    tpl = open(os.path.join(ROOT, 'src', 'index.html'), encoding='utf-8').read()
    i18n = json.load(open(os.path.join(ROOT, 'i18n.json'), encoding='utf-8'))
    lots, fresh = load_lots()
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).strftime('%d.%m.%Y')
    pages = []
    for lang in LANGS:
        page = localize(tpl, lang, i18n)
        home = set_meta(page, lang, 'home')
        home = home.replace('<!--JSONLD-->', '\n'.join(jsonld_tag(o) for o in site_jsonld(lang)))
        home = home.replace('<!--LOTS-->', preview_section(lots, lang))
        base = '' if lang == 'ru' else f'{lang}/'
        write(base + 'index.html', tag_links(home, 'home'))
        pages.append(page_url(lang, 'home'))

        t = L[lang]
        cat = set_meta(page, lang, 'skins', t['cat_doc_title'], t['cat_desc'].format(n=len(lots), d=today))
        cat = cat.replace('<!--JSONLD-->', jsonld_tag(offers_jsonld(lots, lang)))
        cat = re.sub(r'<main id="top">.*?</main>', lambda m: catalog_main(lots, lang, today), cat, count=1, flags=re.S)
        write(base + 'skins/index.html', tag_links(cat, 'skins'))
        pages.append(page_url(lang, 'skins'))

    iso = dt.date.today().isoformat()
    tpl_prices = tpl.replace('href="/skins/" data-i18n="nav_prices"', 'href="/prices/" data-i18n="nav_prices"')
    prices = build_prices(tpl_prices, i18n, lots, iso)
    prices.update(build_guides(tpl_prices, i18n, iso))
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'<url><loc>{u}</loc><lastmod>{iso}</lastmod><changefreq>daily</changefreq></url>\n' for u in pages)
          + ''.join(f'<url><loc>{SITE}/{k}/</loc><lastmod>{v}</lastmod></url>\n' for k, v in sorted(prices.items()))
          + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'Готово: {len(pages) + len(prices)} страниц, лотов {len(lots)}{"" if fresh else " (из кэша)"}')


if __name__ == '__main__':
    main()
