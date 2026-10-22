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
import render
import skins

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://dghostmarket.uz'
API = 'https://api.dghostmarket.uz/api/skins'
PRO_API = 'https://api.dghostmarket.uz/api/pro/tiers'
# Если бот недоступен и выгрузки ещё нет — тарифы как в боте (PRO_TIERS).
PRO_FALLBACK = {'first_discount_percent': 50, 'tiers': [
    {'key': 'start', 'price': 50000, 'days': 30, 'own_channels': 1, 'own_posts': 5, 'own_auctions': 0, 'own_raffles': 0, 'market_posts': 1, 'approval': False, 'popular': False},
    {'key': 'pro', 'price': 150000, 'days': 30, 'own_channels': 5, 'own_posts': 20, 'own_auctions': 10, 'own_raffles': 4, 'market_posts': 3, 'approval': False, 'popular': True},
    {'key': 'business', 'price': 400000, 'days': 30, 'own_channels': 15, 'own_posts': 60, 'own_auctions': 30, 'own_raffles': 10, 'market_posts': 5, 'approval': False, 'popular': False},
    {'key': 'garant', 'price': 1199990, 'days': 30, 'own_channels': None, 'own_posts': None, 'own_auctions': None, 'own_raffles': None, 'market_posts': None, 'approval': True, 'popular': False},
]}
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

# Блок тарифов PRO на главной (цены и лимиты — из бота, /api/pro/tiers).
PRO_T = {
    'ru': {'names': {'start': 'Старт', 'pro': 'PRO', 'business': 'Бизнес', 'garant': 'Гарант'},
           'per': 'за {d} дней', 'popular': 'Популярный', 'unlimited': 'Без ограничений', 'by_request': 'по заявке',
           'channels': 'Своих каналов: {v}', 'posts': 'Постов в свои каналы в день: {v}',
           'market': 'Постов в канал @dghostmarket в день: {v}',
           'auctions': 'Аукционов в месяц: {v}', 'raffles': 'Розыгрышей в месяц: {v}', 'none': '—',
           'first': 'Скидка {p}% на первый месяц', 'cta': 'Подключить в приложении'},
    'uz': {'names': {'start': 'Start', 'pro': 'PRO', 'business': 'Biznes', 'garant': 'Garant'},
           'per': '{d} kun uchun', 'popular': 'Ommabop', 'unlimited': 'Cheklovsiz', 'by_request': 'ariza orqali',
           'channels': "O'z kanallari: {v}", 'posts': "O'z kanallariga kunlik postlar: {v}",
           'market': '@dghostmarket kanaliga kunlik postlar: {v}',
           'auctions': 'Oyiga auksionlar: {v}', 'raffles': "Oyiga o'yinlar: {v}", 'none': '—',
           'first': 'Birinchi oyga {p}% chegirma', 'cta': 'Ilovada ulash'},
    'en': {'names': {'start': 'Start', 'pro': 'PRO', 'business': 'Business', 'garant': 'Garant'},
           'per': 'per {d} days', 'popular': 'Popular', 'unlimited': 'Unlimited', 'by_request': 'on request',
           'channels': 'Own channels: {v}', 'posts': 'Posts to own channels per day: {v}',
           'market': 'Posts to @dghostmarket per day: {v}',
           'auctions': 'Auctions per month: {v}', 'raffles': 'Giveaways per month: {v}', 'none': '—',
           'first': '{p}% off the first month', 'cta': 'Subscribe in the app'},
}

PRO_CSS = """
.pro-tiers{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:20px}
.pro-tier{background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:20px;position:relative}
.pro-tier.pop{border-color:var(--violet)}
.pro-tier .tag{position:absolute;top:-11px;left:16px;background:var(--grad);color:#fff;font-size:12px;font-weight:700;padding:3px 10px;border-radius:999px}
.pro-tier h3{margin:0 0 6px;font-size:18px}
.pro-tier .p{font-size:24px;font-weight:800}
.pro-tier .per{color:var(--muted);font-size:13px;margin-bottom:12px}
.pro-tier ul{list-style:none;padding:0;margin:0;color:var(--muted);font-size:14px}
.pro-tier li{margin:5px 0}
.pro-first{margin-top:16px;font-weight:600}
@media(max-width:900px){.pro-tiers{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.pro-tiers{grid-template-columns:1fr}}
"""

EXTRA_CSS = PRO_CSS + """
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


def load_pro_tiers():
    """Тарифы PRO из бота; при сбое — прошлая выгрузка, затем PRO_FALLBACK."""
    cache = os.path.join(ROOT, 'data', 'pro-tiers.json')
    try:
        req = urllib.request.Request(PRO_API, headers={'User-Agent': 'dghostmarket-site-build'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode('utf-8'))
        if not data.get('tiers'):
            raise ValueError('no tiers')
        json.dump(data, open(cache, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        return data
    except Exception as e:
        print(f'⚠️ Тарифы PRO недоступны ({e!r}) — беру data/pro-tiers.json', file=sys.stderr)
        try:
            return json.load(open(cache, encoding='utf-8'))
        except Exception:
            return PRO_FALLBACK


def pro_tiers_html(data, lang):
    t = PRO_T[lang]
    cur = L[lang]['cur']

    def lim(v):
        if v is None:
            return t['unlimited']
        return t['none'] if not v else str(v)

    cards = []
    for x in data.get('tiers', []):
        name = t['names'].get(x['key'], x.get('name', x['key']))
        rows = [t['channels'].format(v=lim(x.get('own_channels'))), t['posts'].format(v=lim(x.get('own_posts'))),
                t['market'].format(v=lim(x.get('market_posts'))), t['auctions'].format(v=lim(x.get('own_auctions'))),
                t['raffles'].format(v=lim(x.get('own_raffles')))]
        if x.get('approval'):
            rows = [t['unlimited'] + ' · ' + t['by_request']]
        tag = f'<span class="tag">{esc(t["popular"])}</span>' if x.get('popular') else ''
        cards.append(f'<div class="pro-tier{" pop" if x.get("popular") else ""}">{tag}<h3>{esc(name)}</h3>'
                     f'<div class="p">{money(x["price"])} {esc(cur)}</div>'
                     f'<div class="per">{esc(t["per"].format(d=x.get("days", 30)))}</div>'
                     '<ul>' + ''.join(f'<li>{esc(r)}</li>' for r in rows) + '</ul></div>')
    first = data.get('first_discount_percent') or 0
    first_html = f'<p class="pro-first">🎁 {esc(t["first"].format(p=first))}</p>' if first else ''
    return f'<div class="pro-tiers">{"".join(cards)}</div>{first_html}'


def faq_jsonld(page):
    """FAQPage из блока «Частые вопросы» уже переведённой страницы."""
    qa = re.findall(r'<details><summary[^>]*>(.*?)</summary><p[^>]*>(.*?)</p></details>', page, flags=re.S)
    if not qa:
        return None
    strip = lambda h: html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qa]}


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
    img = (f'<img {skins.steam_img_attrs(s["photo_url"], "(max-width:560px) 100vw, (max-width:900px) 50vw, 320px")} '
           f'alt="{esc(name)}" loading="lazy" width="320" height="240">') if s.get('photo_url') else ''
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
         'logo': SITE + '/apple-touch-icon.png', 'email': 'support@dghostmarket.uz',
         'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support', 'email': 'support@dghostmarket.uz',
                          'url': 'https://t.me/DGhostMarket_Support', 'availableLanguage': ['uz', 'ru', 'en']},
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
    s = s.replace('href="/3d-api/"', f'href="{prefix}/3d-api/"')
    # Статьи есть на ru и uz; документы бот отдаёт на ru и uz (?lang=uz).
    if lang == 'uz':
        s = s.replace('href="/guides/', 'href="/uz/guides/')
        s = s.replace('/legal?doc=', '/legal?lang=uz&amp;doc=')
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


HERO_LOTS = 4
SHOWCASE_FILLER_PRICE = 3000   # как в мини-аппе (app-catalog.js)
OVERPRICED_SINK_RATIO = 1.5


def showcase_order(lots):
    """Порядок витрины мини-аппа (вкладка «Популярное», категория «Все»):
    дешевле рынка — первыми, дальше по просмотрам, при равенстве новые;
    сильно дороже рынка, наклейки и мелочь — в конец (showcaseRank)."""
    def rank(s):
        price = int(s.get('price') or 0)
        market = float(s.get('market_price_uzs') or 0)
        if 'sticker' in str(s.get('weapon_type') or '').lower() or str(s.get('title') or '').lower().startswith('sticker') \
                or price < SHOWCASE_FILLER_PRICE:
            return 3
        if market > 0 and price > market * OVERPRICED_SINK_RATIO:
            return 2
        return 0 if market > 0 and price < market else 1
    return sorted(lots, key=lambda s: (rank(s), -(s.get('view_count') or 0), -(s.get('id') or 0)))


def hero_lots(lots, lang):
    """4 реальных лота на первом экране главной — сразу под кнопками."""
    t = L[lang]
    top = [s for s in showcase_order(lots) if s.get('photo_url')][:HERO_LOTS]
    if not top:
        return ''
    cards = []
    for s in top:
        name = ('StatTrak™ ' if s.get('stattrak') else '') + (s.get('title') or '')
        img = skins.steam_img_attrs(s['photo_url'], '(max-width:520px) 45vw, 150px')
        cards.append(f'<a class="hlot" href="{APP}?open=skin_{int(s["id"])}" rel="nofollow">'
                     f'<img {img} alt="{esc(name)}" width="160" height="120">'
                     f'<b>{esc(name)}</b><span>{money(int(s["price"]))} {esc(t["cur"])}</span></a>')
    return '<div class="hlots">' + ''.join(cards) + '</div>'


def preview_section(lots, lang):
    t = L[lang]
    if not lots:
        return ''
    # Те же лоты, что на первом экране, не повторяем — дальше по витрине.
    shown = {s['id'] for s in [x for x in showcase_order(lots) if x.get('photo_url')][:HERO_LOTS]}
    top = [s for s in showcase_order(lots) if s['id'] not in shown][:PREVIEW]
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

    text = re.sub(r'href="(https://app\.dghostmarket\.(?:uz|com)/[^"]*)"', app, text)
    return text.replace('href="https://t.me/dghostmarketbot"', f'href="https://t.me/dghostmarketbot?start={src}"')


HOME_ANCHORS = ('how', 'view3d', 'fees', 'sellers', 'safety', 'faq', 'docs', 'contacts')


def fix_anchors(rel, text):
    """Меню шапки ведёт на разделы главной: на внутренних страницах
    «#how» никуда не ведёт — превращаем в «/#how» (или «/uz/#how»)."""
    if not rel.endswith('.html') or rel in ('index.html', 'uz/index.html', 'en/index.html') or rel.startswith('render/'):
        return text
    base = '/uz/' if rel.startswith('uz/') else '/en/' if rel.startswith('en/') else '/'
    return re.sub(r'href="#(' + '|'.join(HOME_ANCHORS) + ')"', lambda m: f'href="{base}#{m.group(1)}"', text)


def write(rel, text):
    """Пишет файл, только если он изменился. True — файл новый или другой."""
    text = fix_anchors(rel, text)
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
    models3d = skins.load_models(ROOT)
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
            body = skins.skin_main(s, lang, lots, related, rate, lot_card, has3d=s['base'].lower() in models3d)
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


def site_page(page, lang, path, title, desc, main_html, jsonld=None):
    """Страница отдельного сайта render.dghostmarket.com из готовой страницы сайта маркета."""
    s = re.sub(r'<header>.*?</header>', lambda m: render.site_header(lang, path), page, count=1, flags=re.S)
    s = re.sub(r'<footer>.*?</footer>', lambda m: render.site_footer(lang), s, count=1, flags=re.S)
    s = re.sub(r'<main id="top">.*?</main>', lambda m: main_html, s, count=1, flags=re.S)
    url = render.site_url(lang, path)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, s, count=1)
    s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{txt(title)}</title>', s, count=1)
    for prop in ('og:title',):
        s = re.sub(r'(<meta property="' + prop + r'" content=")[^"]*', lambda m: m.group(1) + esc(title), s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(desc), s, count=1)
    s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', '', s)
    s = s.replace('</title>', '</title>\n' + render.site_alternates(path), 1)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', '', s, flags=re.S)
    if jsonld:
        s = s.replace('</head>', jsonld_tag(jsonld) + '</head>', 1)
    # Переадресация по языку браузера — для сайта маркета; здесь своя схема адресов.
    s = re.sub(r'<script>(?:(?!</script>).)*dgm_lang.*?</script>', '', s, flags=re.S)
    # Ссылки «в маркет» на отдельном сайте не нужны.
    s = s.replace('href="/skins/"', 'href="/"').replace('href="/prices/"', 'href="/"')
    return s


def build_render_site(tpl, i18n):
    """Отдельный сайт 3D-рендера: render/ (en), render/ru/, render/uz/, условия, конфиденциальность, возвраты."""
    for lang in render.SITE_LANGS:
        t = render.T[lang]
        page = localize(tpl, lang, i18n, render.CSS)
        # «Посмотреть 3D» на отдельном сайте ведёт к демо на этой же странице, а не в маркет.
        main_html = render.render_main(lang, '#demo')
        main_html = re.sub(r'<nav class="crumbs">.*?</nav>', '', main_html, count=1, flags=re.S)
        main_html = main_html.replace('<div class="block"><h2>' + esc(t['faq_h']), '<div class="block" id="faq"><h2>' + esc(t['faq_h']), 1)
        ld = render.offer_jsonld(lang, render.site_url(lang), render.RENDER_SITE)
        ld['provider'] = {'@type': 'Organization', 'name': 'DGhost 3D', 'url': render.RENDER_SITE + '/'}
        out = site_page(page, lang, '', t['title'], t['desc'], main_html, ld)
        write('render/' + ('' if lang == 'en' else f'{lang}/') + 'index.html', out)
    page = localize(tpl, 'en', i18n, render.CSS + render.LEGAL_CSS)
    for kind in render.LEGAL:
        title = render.LEGAL[kind][0]
        out = site_page(page, 'en', f'{kind}/', f'{title} | DGhost 3D', f'{title} of DGhost 3D, an embeddable 3D viewer for CS2 item listings.',
                        render.legal_main(kind))
        out = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', '', out)
        write(f'render/{kind}/index.html', out)
    urls = [render.site_url(l) for l in render.SITE_LANGS] + [render.site_url('en', f'{k}/') for k in render.LEGAL]
    write('render/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'<url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('render/robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {render.RENDER_SITE}/sitemap.xml\n')


def build_render(tpl, i18n, iso):
    """Страница сервиса 3D-рендера (ru, uz, en). Возвращает {путь: дата изменения} для sitemap."""
    lm_path = os.path.join(ROOT, 'data', 'render-lastmod.json')
    try:
        lastmod = json.load(open(lm_path, encoding='utf-8'))
    except Exception:
        lastmod = {}
    new = {}
    for lang in render.LANGS:
        t = render.T[lang]
        page = localize(tpl, lang, i18n, render.CSS)
        out = set_meta(page, lang, '3d-api', t['title'], t['desc'], render.LANGS)
        out = out.replace('<!--JSONLD-->', jsonld_tag(render.offer_jsonld(lang, page_url(lang, '3d-api'), SITE)))
        out = re.sub(r'<main id="top">.*?</main>', lambda m: render.render_main(lang, APP), out, count=1, flags=re.S)
        # Переключатель языка ведёт на эту же страницу.
        for l in render.LANGS:
            out = out.replace(f'href="{"/" if l == "ru" else f"/{l}/"}" data-lang="{l}"',
                              f'href="{render.prefix(l)}/3d-api/" data-lang="{l}"')
        rel = ('' if lang == 'ru' else f'{lang}/') + '3d-api'
        changed = write(rel + '/index.html', tag_links(out, 'render3d'))
        new[rel] = iso if changed or rel not in lastmod else lastmod[rel]
    write('data/render-lastmod.json', json.dumps(dict(sorted(new.items())), ensure_ascii=False, indent=0) + '\n')
    return new


def main():
    tpl = open(os.path.join(ROOT, 'src', 'index.html'), encoding='utf-8').read()
    i18n = json.load(open(os.path.join(ROOT, 'i18n.json'), encoding='utf-8'))
    lots, fresh = load_lots()
    pro = load_pro_tiers()
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).strftime('%d.%m.%Y')
    pages = []
    for lang in LANGS:
        page = localize(tpl, lang, i18n)
        home = set_meta(page, lang, 'home')
        home = home.replace('<!--PRO_TIERS-->', pro_tiers_html(pro, lang))
        faq = faq_jsonld(home)
        home = home.replace('<!--JSONLD-->', '\n'.join(jsonld_tag(o) for o in site_jsonld(lang) + ([faq] if faq else [])))
        home = home.replace('<!--LOTS-->', preview_section(lots, lang)).replace('<!--HERO_LOTS-->', hero_lots(lots, lang))
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
    prices.update(build_render(tpl_prices, i18n, iso))
    build_render_site(tpl_prices, i18n)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'<url><loc>{u}</loc><lastmod>{iso}</lastmod><changefreq>daily</changefreq></url>\n' for u in pages)
          + ''.join(f'<url><loc>{SITE}/{k}/</loc><lastmod>{v}</lastmod></url>\n' for k, v in sorted(prices.items()))
          + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /render/\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'Готово: {len(pages) + len(prices)} страниц, лотов {len(lots)}{"" if fresh else " (из кэша)"}')


if __name__ == '__main__':
    main()
