"""Страницы цен на скины CS2 в сумах: /prices/<скин>/ (+ uz, en) и каталог /prices/.

Вызывается из tools/build.py. Данные готовит workflow (.github/workflows/build.yml)
перед сборкой, в папку data/ (эти выгрузки в git не попадают):

    data/skins-meta.json  — справочник скинов (ByMykel/CSGO-API, skins.json):
                            название, оружие, редкость, коллекции, float, картинка;
    data/skinport.json    — цены всех предметов CS2 на Skinport (одним запросом);
    data/rate.json        — курс доллара ЦБ Узбекистана ({"usd_uzs": 12650.0}).

Нет справочника или цен — страницы скинов не трогаем (остаются прошлые).
Цены округляются до трёх значащих цифр, а файл перезаписывается, только если
страница изменилась: мелкие колебания курса не переписывают сотни страниц
каждый день. Дата изменения — в data/prices-lastmod.json (для sitemap).
"""
import html
import json
import os
import re

TOP_SKINS = 400          # сколько скинов: самые торгуемые по количеству на Skinport
RELATED = 6              # ссылок на соседние скины того же оружия

WEARS = ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred']
WEAR_T = {
    'ru': ['Прямо с завода', 'Немного поношенное', 'После полевых испытаний', 'Поношенное', 'Закалённое в боях'],
    'uz': ['Zavoddan yangi', 'Biroz ishlatilgan', 'Dala sinovidan keyin', 'Eskirgan', 'Jangda toblangan'],
    'en': WEARS,
}
RARITY_T = {
    'ru': {'Consumer Grade': 'Ширпотреб', 'Industrial Grade': 'Промышленное качество', 'Mil-Spec Grade': 'Армейское качество',
           'Restricted': 'Запрещённое', 'Classified': 'Засекреченное', 'Covert': 'Тайное', 'Contraband': 'Контрабанда',
           'Extraordinary': 'Экстраординарное'},
    'uz': {'Consumer Grade': 'Iste’mol darajasi', 'Industrial Grade': 'Sanoat darajasi', 'Mil-Spec Grade': 'Harbiy daraja',
           'Restricted': 'Cheklangan', 'Classified': 'Maxfiy', 'Covert': 'Yashirin', 'Contraband': 'Kontrabanda',
           'Extraordinary': 'Favqulodda'},
    'en': {},
}

T = {
    'ru': {
        'h1': '{name} — цена в сумах',
        'title': '{name} — цена в сумах, купить в Узбекистане | DGhostMarket',
        'desc': 'Цена {name} в сумах: от {low} сум. Все износы{st}, float, коллекция. Купить и продать {name} в Telegram через гаранта — DGhostMarket.',
        'st_desc': ' и StatTrak™',
        'cur': 'сум', 'wear': 'Износ', 'normal': 'Обычный', 'st': 'StatTrak™',
        'price_note': 'Рыночная цена — минимальное предложение на Skinport в долларах, пересчитанное по курсу ЦБ Узбекистана. Обновляется каждый день.',
        'about': 'О скине', 'weapon': 'Оружие', 'rarity': 'Редкость', 'float': 'Float', 'collection': 'Коллекция', 'case': 'Где выпадает',
        'on_sale': 'В продаже на DGhostMarket', 'buy': 'Купить',
        'none': 'Сейчас этого скина нет в продаже. Добавьте его в «Хочу» — бот напишет, как только он появится, а продавцам подскажет, что его ищут.',
        'notify': 'Сообщить, когда появится',
        'sell': 'Есть такой скин? Выставите его за минуту — DGhostMarket подскажет цену по рынку, оплата через гаранта.',
        'sell_btn': 'Продать на DGhostMarket',
        'related': 'Другие скины {weapon}',
        'hub': 'Цены на скины CS2', 'home': 'Главная',
        'hub_title': 'Цены на скины CS2 в сумах — каталог | DGhostMarket',
        'hub_h1': 'Цены на скины CS2 в сумах',
        'hub_desc': 'Каталог цен на {n} популярных скинов CS2 в сумах: ножи, перчатки, AK-47, AWP, M4A4 и другие — по всем износам и StatTrak™. Обновляется каждый день.',
        'hub_lead': 'Рыночные цены популярных скинов CS2 в узбекских сумах — по всем износам. Выберите скин, чтобы увидеть цены, float, коллекцию и предложения на DGhostMarket.',
        'from': 'от {p}',
        'other': 'Другое',
    },
    'uz': {
        'h1': '{name} — narxi so‘mda',
        'title': '{name} narxi so‘mda — O‘zbekistonda sotib olish | DGhostMarket',
        'desc': '{name} narxi so‘mda: {low} so‘mdan. Barcha holatlar{st}, float, kolleksiya. {name}ni Telegramda kafil orqali sotib oling va soting — DGhostMarket.',
        'st_desc': ' va StatTrak™',
        'cur': 'so‘m', 'wear': 'Holati', 'normal': 'Oddiy', 'st': 'StatTrak™',
        'price_note': 'Bozor narxi — Skinport’dagi eng arzon taklif (dollarda), O‘zbekiston Markaziy banki kursi bo‘yicha hisoblangan. Har kuni yangilanadi.',
        'about': 'Skin haqida', 'weapon': 'Qurol', 'rarity': 'Noyoblik', 'float': 'Float', 'collection': 'Kolleksiya', 'case': 'Qayerdan tushadi',
        'on_sale': 'DGhostMarket’da sotuvda', 'buy': 'Sotib olish',
        'none': 'Hozir bu skin sotuvda yo‘q. Uni «Xohlayman» ro‘yxatiga qo‘shing — paydo bo‘lishi bilan bot xabar beradi, sotuvchilarga esa uni qidirishayotganini aytadi.',
        'notify': 'Paydo bo‘lganda xabar berish',
        'sell': 'Sizda shu skin bormi? Bir daqiqada sotuvga qo‘ying — DGhostMarket bozor narxini taklif qiladi, to‘lov kafil orqali.',
        'sell_btn': 'DGhostMarket’da sotish',
        'related': '{weapon} uchun boshqa skinlar',
        'hub': 'CS2 skinlari narxlari', 'home': 'Bosh sahifa',
        'hub_title': 'CS2 skinlari narxlari so‘mda — katalog | DGhostMarket',
        'hub_h1': 'CS2 skinlari narxlari so‘mda',
        'hub_desc': '{n} ta mashhur CS2 skinining so‘mdagi narxlari: pichoqlar, qo‘lqoplar, AK-47, AWP, M4A4 va boshqalar — barcha holatlar va StatTrak™. Har kuni yangilanadi.',
        'hub_lead': 'Mashhur CS2 skinlarining so‘mdagi bozor narxlari — barcha holatlar bo‘yicha. Narxlar, float, kolleksiya va DGhostMarket’dagi takliflarni ko‘rish uchun skinni tanlang.',
        'from': '{p}dan',
        'other': 'Boshqa',
    },
    'en': {
        'h1': '{name} — price in Uzbek sum',
        'title': '{name} price in UZS — buy in Uzbekistan | DGhostMarket',
        'desc': '{name} price in Uzbek sum: from {low} UZS. All wears{st}, float, collection. Buy and sell {name} in Telegram with escrow — DGhostMarket.',
        'st_desc': ' and StatTrak™',
        'cur': 'UZS', 'wear': 'Wear', 'normal': 'Normal', 'st': 'StatTrak™',
        'price_note': 'Market price is the lowest Skinport listing in USD, converted at the Central Bank of Uzbekistan rate. Updated daily.',
        'about': 'About the skin', 'weapon': 'Weapon', 'rarity': 'Rarity', 'float': 'Float', 'collection': 'Collection', 'case': 'Drops from',
        'on_sale': 'On sale at DGhostMarket', 'buy': 'Buy',
        'none': 'This skin isn’t on sale right now. Add it to your wishlist — the bot will message you as soon as it appears and let sellers know it’s wanted.',
        'notify': 'Notify me when available',
        'sell': 'Own this skin? List it in a minute — DGhostMarket suggests a market price, payment goes through escrow.',
        'sell_btn': 'Sell on DGhostMarket',
        'related': 'More {weapon} skins',
        'hub': 'CS2 skin prices', 'home': 'Home',
        'hub_title': 'CS2 skin prices in Uzbek sum — catalog | DGhostMarket',
        'hub_h1': 'CS2 skin prices in Uzbek sum',
        'hub_desc': 'Prices for {n} popular CS2 skins in Uzbek sum: knives, gloves, AK-47, AWP, M4A4 and more — every wear and StatTrak™. Updated daily.',
        'hub_lead': 'Market prices of popular CS2 skins in Uzbek sum, for every wear. Pick a skin to see prices, float, collection and offers on DGhostMarket.',
        'from': 'from {p}',
        'other': 'Other',
    },
}

CSS = """
.price-head{display:grid;grid-template-columns:280px minmax(0,1fr);gap:28px;align-items:start;margin:8px 0 28px}
.price-head img{width:100%;max-width:100%;height:auto;aspect-ratio:4/3;object-fit:contain;background:radial-gradient(ellipse at 50% 40%,#2a2238,#130e1c 70%);border-radius:18px;border:1px solid rgba(255,255,255,0.06)}
.ptable{width:100%;border-collapse:collapse;background:var(--surface);border-radius:14px;overflow:hidden;font-size:15px}
.ptable th,.ptable td{padding:11px 14px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.06)}
.ptable th{color:var(--muted);font-weight:600;font-size:13px}
.ptable td.num{font-weight:700;white-space:nowrap}
.pnote{color:var(--muted);font-size:13px;margin:10px 0 0}
.facts-list{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;margin:0;font-size:15px}
.facts-list dt{color:var(--muted)}
.facts-list dd{margin:0}
.box{background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:20px;margin:22px 0}
.box p{margin:0 0 14px;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips a{border:1px solid var(--line);border-radius:999px;padding:6px 12px;text-decoration:none;font-size:14px}
.hub-group{margin:30px 0 10px;font-size:19px}
.hub-list{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 18px;font-size:15px}
.hub-list a{text-decoration:none;display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05)}
.hub-list span{color:var(--muted);white-space:nowrap}
@media(max-width:760px){.price-head{grid-template-columns:minmax(0,1fr)}.ptable{font-size:14px}.ptable th,.ptable td{padding:9px 8px}.facts-list{grid-template-columns:minmax(0,max-content) minmax(0,1fr)}.hub-list{grid-template-columns:1fr}}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(name):
    s = name.replace('★', '').replace('™', '').lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def round3(n):
    """Три значащие цифры: 1 234 567 → 1 230 000 (меньше «дрожания» страниц)."""
    n = int(round(n))
    if n < 1000:
        return n
    k = 10 ** (len(str(n)) - 3)
    return int(round(n / k) * k)


def money(n):
    return f'{int(n):,}'.replace(',', ' ')


def load_inputs(root):
    data = os.path.join(root, 'data')
    try:
        meta = json.load(open(os.path.join(data, 'skins-meta.json'), encoding='utf-8'))
        market = json.load(open(os.path.join(data, 'skinport.json'), encoding='utf-8'))
        rate = float(json.load(open(os.path.join(data, 'rate.json'), encoding='utf-8'))['usd_uzs'])
    except Exception as e:  # данных нет — страницы скинов не трогаем
        return None, repr(e)
    if not isinstance(meta, list) or not isinstance(market, list) or not rate:
        return None, 'пустые данные'
    return (meta, market, rate), None


def collect(meta, market, rate, keep=()):
    """[{name, slug, weapon, rarity, ..., prices: {(wear, st): сум}, low, qty}] — TOP_SKINS самых торгуемых."""
    by_name = {}
    for it in market:
        name = it.get('market_hash_name') or ''
        price = it.get('min_price') or it.get('suggested_price')
        if not name or not price:
            continue
        by_name[name] = (float(price), int(it.get('quantity') or 0))
    skins = []
    for s in meta:
        name = (s.get('name') or '').strip()
        if not name or '|' not in name:
            continue
        base = name.replace('★ ', '').replace('★', '').strip()
        prices, qty = {}, 0
        wears = [w.get('name') for w in (s.get('wears') or []) if w.get('name') in WEARS] or [None]
        for w in wears:
            for st in (False, True):
                if st and not s.get('stattrak'):
                    continue
                prefix = ('★ ' if name.startswith('★') else '') + ('StatTrak™ ' if st else '')
                key = prefix + base + (f' ({w})' if w else '')
                if key in by_name:
                    usd, q = by_name[key]
                    prices[(w, st)] = round3(usd * rate)
                    qty += q
        if not prices:
            continue
        skins.append({
            'name': name, 'base': base, 'slug': slugify(base),
            'weapon': (s.get('weapon') or {}).get('name') or '',
            'category': (s.get('category') or {}).get('name') or '',
            'rarity': (s.get('rarity') or {}).get('name') or '',
            'rarity_color': (s.get('rarity') or {}).get('color') or '',
            'min_float': s.get('min_float'), 'max_float': s.get('max_float'),
            'stattrak': bool(s.get('stattrak')),
            'collections': [c.get('name') for c in (s.get('collections') or []) if c.get('name')][:2],
            'crates': [c.get('name') for c in (s.get('crates') or []) if c.get('name')][:2],
            'image': s.get('image') or '',
            'wears': wears, 'prices': prices, 'low': min(prices.values()), 'qty': qty,
        })
    # Одно имя — одна страница (у Doppler фазы делят название): берём самую торгуемую.
    best = {}
    for s in skins:
        if s['slug'] not in best or s['qty'] > best[s['slug']]['qty']:
            best[s['slug']] = s
    # Уже опубликованные страницы продолжаем обновлять, даже если скин выпал из топа:
    # иначе на них застынут старые цены.
    ranked = sorted(best.values(), key=lambda s: -s['qty'])
    top = ranked[:TOP_SKINS] + [s for s in ranked[TOP_SKINS:] if s['slug'] in keep]
    return sorted(top, key=lambda s: s['base'])


def prefix(lang):
    return '' if lang == 'ru' else f'/{lang}'


def matching_lots(skin, lots):
    want = skin['base'].lower()
    out = []
    for s in lots:
        title = (s.get('title') or '').replace('★', '').strip().lower()
        if title == want:
            out.append(s)
    return sorted(out, key=lambda s: int(s['price']))


def skin_main(skin, lang, lots, related, rate, lot_card):
    t = T[lang]
    p = prefix(lang)
    name = skin['base']
    rows = []
    for i, w in enumerate(WEARS):
        if w not in skin['wears']:
            continue
        normal = skin['prices'].get((w, False))
        st = skin['prices'].get((w, True))
        cells = f'<td class="num">{money(normal) + " " + t["cur"] if normal else "—"}</td>'
        if skin['stattrak']:
            cells += f'<td class="num">{money(st) + " " + t["cur"] if st else "—"}</td>'
        rows.append(f'<tr><td>{esc(WEAR_T[lang][i])}</td>{cells}</tr>')
    if skin['wears'] == [None]:
        normal = skin['prices'].get((None, False))
        st = skin['prices'].get((None, True))
        cells = f'<td class="num">{money(normal) + " " + t["cur"] if normal else "—"}</td>'
        if skin['stattrak']:
            cells += f'<td class="num">{money(st) + " " + t["cur"] if st else "—"}</td>'
        rows.append(f'<tr><td>—</td>{cells}</tr>')
    head = f'<tr><th>{esc(t["wear"])}</th><th>{esc(t["normal"])}</th>' + (f'<th>{esc(t["st"])}</th>' if skin['stattrak'] else '') + '</tr>'
    table = f'<table class="ptable">{head}{"".join(rows)}</table><p class="pnote">{esc(t["price_note"])}</p>'

    facts = [(t['weapon'], skin['weapon'])]
    if skin['rarity']:
        facts.append((t['rarity'], RARITY_T[lang].get(skin['rarity'], skin['rarity'])))
    if skin['min_float'] is not None and skin['max_float'] is not None:
        facts.append((t['float'], f"{float(skin['min_float']):.2f} – {float(skin['max_float']):.2f}"))
    if skin['collections']:
        facts.append((t['collection'], ', '.join(skin['collections'])))
    if skin['crates']:
        facts.append((t['case'], ', '.join(skin['crates'])))
    facts_html = '<dl class="facts-list">' + ''.join(f'<dt>{esc(a)}</dt><dd>{esc(b)}</dd>' for a, b in facts) + '</dl>'

    img = f'<img src="{esc(skin["image"])}" alt="{esc(name)}" width="560" height="420">' if skin['image'] else ''
    found = matching_lots(skin, lots)
    if found:
        sale = (f'<section class="box"><h2>{esc(t["on_sale"])}</h2><div class="lots">'
                + ''.join(lot_card(s, lang) for s in found[:6]) + '</div></section>')
    else:
        q = urlquote(name)
        sale = (f'<section class="box"><h2>{esc(t["on_sale"])}</h2><p>{esc(t["none"])}</p>'
                f'<a class="btn primary" href="https://app.dghostmarket.com/?open=wants&amp;q={q}" rel="nofollow">{esc(t["notify"])}</a></section>')
    sell = (f'<section class="box"><p>{esc(t["sell"])}</p>'
            f'<a class="btn ghost" href="https://app.dghostmarket.com/?open=sell" rel="nofollow">{esc(t["sell_btn"])}</a></section>')
    rel = ''
    if related:
        rel = (f'<section><h2 class="hub-group">{esc(t["related"].format(weapon=skin["weapon"]))}</h2><div class="chips">'
               + ''.join(f'<a href="{p}/prices/{r["slug"]}/">{esc(r["base"])}</a>' for r in related) + '</div></section>')
    crumbs = (f'<nav class="crumbs"><a href="{p}/">{esc(t["home"])}</a> / <a href="{p}/prices/">{esc(t["hub"])}</a> / {esc(name)}</nav>')
    return (f'<main id="top"><div class="wrap">{crumbs}<div class="price-head">{img}<div>'
            f'<h1>{esc(t["h1"].format(name=name))}</h1>{table}</div></div>'
            f'<section class="box"><h2>{esc(t["about"])}</h2>{facts_html}</section>{sale}{sell}{rel}</div></main>')


def urlquote(s):
    from urllib.parse import quote
    return quote(s, safe='')


def skin_jsonld(skin, lang, url):
    t = T[lang]
    prices = list(skin['prices'].values())
    return {
        '@context': 'https://schema.org', '@type': 'Product', 'name': skin['base'],
        'image': skin['image'] or None, 'category': skin['category'] or 'CS2 skin',
        'description': t['desc'].format(name=skin['base'], low=money(skin['low']), st=t['st_desc'] if skin['stattrak'] else ''),
        'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'UZS', 'lowPrice': min(prices), 'highPrice': max(prices),
                   'offerCount': len(prices), 'url': url},
    }


def hub_main(skins, lang):
    t = T[lang]
    p = prefix(lang)
    groups = {}
    for s in skins:
        key = s['weapon'] or t['other']
        groups.setdefault(key, []).append(s)
    order = sorted(groups, key=lambda g: (-sum(x['qty'] for x in groups[g]), g))
    body = ''.join(
        f'<h2 class="hub-group">{esc(g)}</h2><div class="hub-list">'
        + ''.join(f'<a href="{p}/prices/{s["slug"]}/">{esc(s["base"].split("|", 1)[-1].strip())}'
                  f'<span>{esc(t["from"].format(p=money(s["low"]) + " " + t["cur"]))}</span></a>' for s in groups[g])
        + '</div>' for g in order)
    return (f'<main id="top"><div class="wrap"><nav class="crumbs"><a href="{p}/">{esc(t["home"])}</a> / {esc(t["hub"])}</nav>'
            f'<h1>{esc(t["hub_h1"])}</h1><p class="lead">{esc(t["hub_lead"])}</p>{body}</div></main>')
