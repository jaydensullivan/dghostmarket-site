"""Страница внешнего сервиса 3D-рендера: /3d-api/ (ru), /uz/3d-api/, /en/3d-api/.

Вызывается из tools/build.py. Сервис пока в разработке — страница собирает
заявки на пилот (Telegram поддержки и почта), оплаты на ней нет.
Тарифы — в PLANS (цены в долларах; суммы в сумах — по RATE, округлены).
"""
import html
from urllib.parse import quote

LANGS = ['ru', 'uz', 'en']
SUPPORT_TG = 'https://t.me/DGhostMarket_Support'
SUPPORT_MAIL = 'support@dghostmarket.uz'
RATE = 11900  # сум за $ — только для подписи «≈ … сум» у тарифов

# Лимиты в месяц; None — «по договору», 0 — нет в тарифе.
PLANS = [
    {'key': 'trial', 'usd': 0, 'domains': 1, 'views': 1000, 'images': 50, 'videos': 0,
     'ar': False, 'badge': 'full', 'brand': False, 'support': 'none'},
    {'key': 'starter', 'usd': 19, 'domains': 1, 'views': 10000, 'images': 1000, 'videos': 0,
     'ar': False, 'badge': 'small', 'brand': False, 'support': 'mail'},
    {'key': 'pro', 'usd': 49, 'domains': 3, 'views': 50000, 'images': 5000, 'videos': 100,
     'ar': True, 'badge': 'off_opt', 'brand': False, 'support': 'mail24', 'best': True},
    {'key': 'business', 'usd': 129, 'domains': 10, 'views': 250000, 'images': 25000, 'videos': 500,
     'ar': True, 'badge': 'off', 'brand': True, 'support': 'tg'},
    {'key': 'enterprise', 'usd': None, 'domains': None, 'views': None, 'images': None, 'videos': None,
     'ar': True, 'badge': 'off', 'brand': True, 'support': 'personal'},
]

T = {
    'ru': {
        'home': 'Главная', 'crumb': '3D-рендер для бизнеса',
        'title': '3D-рендер скинов CS2 для сайтов и магазинов — API и виджет | DGhostMarket',
        'desc': 'Встраиваемый 3D-просмотр скинов CS2 с float и паттерном, API картинок и видео для маркетплейсов, трейд-ботов и магазинов. Тарифы от $19 в месяц, пробный период 14 дней.',
        'badge': 'Скоро · набираем пилотных клиентов',
        'h1': '3D-рендер скинов CS2 <span>для вашего сайта</span>',
        'lead': 'Тот же 3D-движок, что в маркете DGhostMarket: реальная раскраска, float и паттерн конкретного предмета. Подключите на свой сайт виджетом или получайте готовые картинки и видео по API.',
        'cta': 'Оставить заявку на пилот', 'cta_mail': 'Написать на почту', 'cta_demo': 'Посмотреть 3D в маркете',
        'what_h': 'Что вы получаете',
        'what': [
            ('🧊 3D-виджет', 'Вставляете одну строку кода — на странице товара появляется 3D-просмотр: вращение, приближение, фоны карт CS2, износ по float и рисунок по паттерну.'),
            ('🖼 API картинок', 'Отправляете скин, float и паттерн — получаете PNG или WebP нужного ракурса. Готовые картинки кэшируются: повторный запрос мгновенный.'),
            ('🎬 Видео и GIF', 'Ролик вращения или осмотр «в руках» — для карточек товара, постов и рекламы.'),
            ('📐 AR «на столе»', 'Покупатель ставит скин на свой стол через камеру телефона в натуральную величину.'),
        ],
        'who_h': 'Кому подходит',
        'who': ['маркетплейсам и магазинам скинов', 'трейд-ботам и Telegram-магазинам', 'сайтам с кейсами и обзорами, блогерам и стримерам', 'сервисам оценки и аналитики инвентаря'],
        'plans_h': 'Тарифы', 'plans_sub': 'Цены в месяц. При оплате за год — скидка 20%. Клиентам из Узбекистана — оплата в сумах картой Humo или Uzcard.',
        'per_month': '/ мес', 'free': 'Бесплатно', 'trial_note': '14 дней', 'custom': 'Договорная', 'approx': '≈ {v} сум',
        'best': 'Популярный',
        'f_domains': 'Сайтов (доменов)', 'f_views': 'Показы 3D-виджета', 'f_images': 'Картинки по API', 'f_videos': 'Видео и GIF по API',
        'f_ar': 'AR «на столе»', 'f_badge': 'Значок «3D by DGhost»', 'f_brand': 'Свой фон и брендинг', 'f_support': 'Поддержка',
        'v_custom': 'по договору', 'v_yes': '✓', 'v_no': '—',
        'badge_full': 'есть', 'badge_small': 'маленький', 'badge_off_opt': 'можно убрать', 'badge_off': 'нет',
        'sup_none': '—', 'sup_mail': 'почта', 'sup_mail24': 'почта, ответ за 24 ч', 'sup_tg': 'Telegram, в приоритете', 'sup_personal': 'персональный менеджер',
        'over_h': 'Если лимит закончился', 'over': 'Сервис не отключается — сверх лимита: $2 за 1 000 показов, $5 за 1 000 картинок, $0,10 за видео. Перерасход виден в личном кабинете.',
        'plan_trial': 'Пробный', 'plan_starter': 'Starter', 'plan_pro': 'Pro', 'plan_business': 'Business', 'plan_enterprise': 'Enterprise',
        'how_h': 'Как подключиться',
        'how': ['Оставьте заявку в Telegram или на почту: сайт, сколько товаров и показов в месяц.', 'Мы выдадим ключ и привяжем его к вашему домену — чужой сайт ваш ключ использовать не сможет.', 'Вставьте виджет или подключите API по документации — обычно это занимает час.', '14 дней бесплатно, потом выбираете тариф.'],
        'faq_h': 'Вопросы',
        'faq': [
            ('Чем отличается от картинок Steam?', 'В Steam одна картинка на весь скин. У нас — конкретный предмет: его float (потёртости) и паттерн (положение рисунка), в 3D со всех сторон.'),
            ('Насколько похоже на игру?', 'Модели и раскраски собираются из файлов CS2, сходство мы постоянно сверяем с CSFloat и Steam. Для части редких раскрасок работа ещё идёт — во время пилота покажем результат на ваших товарах.'),
            ('Вы отдаёте файлы моделей?', 'Нет. Вы получаете показ и готовые картинки или видео; исходные файлы закрыты и привязаны к вашему домену.'),
            ('Когда запуск?', 'Сейчас набираем пилотных клиентов: первые получают бесплатный месяц и скидку на тариф.'),
        ],
        'legal': 'DGhostMarket не связан с Valve Corporation. CS2, Counter-Strike и Steam — товарные знаки Valve Corporation. Сервис показывает внешний вид предметов, но не продаёт и не распространяет игровые файлы.',
        'mail_subject': 'Заявка на 3D-рендер',
    },
    'uz': {
        'home': 'Bosh sahifa', 'crumb': 'Biznes uchun 3D-render',
        'title': 'Saytlar va do‘konlar uchun CS2 skinlarining 3D-renderi — API va vidjet | DGhostMarket',
        'desc': 'CS2 skinlarini float va naqsh bilan 3D ko‘rsatuvchi vidjet, marketpleyslar, treyd-botlar va do‘konlar uchun rasm va video API. Tariflar oyiga $19 dan, 14 kunlik sinov muddati.',
        'badge': 'Tez kunda · pilot mijozlarni yig‘moqdamiz',
        'h1': 'CS2 skinlarining 3D-renderi <span>saytingiz uchun</span>',
        'lead': 'DGhostMarket marketidagi o‘sha 3D-dvigatel: aynan shu buyumning haqiqiy bo‘yog‘i, float va naqshi. Saytingizga vidjet orqali ulang yoki API orqali tayyor rasm va videolarni oling.',
        'cta': 'Pilotga ariza qoldirish', 'cta_mail': 'Pochtaga yozish', 'cta_demo': 'Marketda 3D’ni ko‘rish',
        'what_h': 'Siz nimani olasiz',
        'what': [
            ('🧊 3D-vidjet', 'Bitta qator kod qo‘shasiz — tovar sahifasida 3D-ko‘rinish paydo bo‘ladi: aylantirish, yaqinlashtirish, CS2 xaritalari fonlari, float bo‘yicha eskirish va naqsh bo‘yicha rasm.'),
            ('🖼 Rasmlar API', 'Skin, float va naqshni yuborasiz — kerakli burchakdan PNG yoki WebP olasiz. Tayyor rasmlar keshlanadi: takroriy so‘rov bir zumda.'),
            ('🎬 Video va GIF', 'Aylanish roligi yoki «qo‘lda» ko‘rish — tovar kartochkalari, postlar va reklama uchun.'),
            ('📐 AR «Stolda»', 'Xaridor telefon kamerasi orqali skinni stoliga haqiqiy o‘lchamda qo‘yadi.'),
        ],
        'who_h': 'Kimlar uchun',
        'who': ['skin marketpleyslari va do‘konlari', 'treyd-botlar va Telegram-do‘konlar', 'keys va obzor saytlari, blogerlar va strimerlar', 'inventarni baholash va tahlil qilish servislari'],
        'plans_h': 'Tariflar', 'plans_sub': 'Narxlar oyiga. Bir yilga to‘lasangiz — 20% chegirma. O‘zbekistondagi mijozlar uchun — Humo yoki Uzcard kartasi bilan so‘mda to‘lov.',
        'per_month': '/ oy', 'free': 'Bepul', 'trial_note': '14 kun', 'custom': 'Kelishilgan', 'approx': '≈ {v} so‘m',
        'best': 'Ommabop',
        'f_domains': 'Saytlar (domenlar)', 'f_views': '3D-vidjet ko‘rsatuvlari', 'f_images': 'API orqali rasmlar', 'f_videos': 'API orqali video va GIF',
        'f_ar': 'AR «Stolda»', 'f_badge': '«3D by DGhost» belgisi', 'f_brand': 'O‘z foni va brendingi', 'f_support': 'Yordam',
        'v_custom': 'kelishuv bo‘yicha', 'v_yes': '✓', 'v_no': '—',
        'badge_full': 'bor', 'badge_small': 'kichik', 'badge_off_opt': 'olib tashlash mumkin', 'badge_off': 'yo‘q',
        'sup_none': '—', 'sup_mail': 'pochta', 'sup_mail24': 'pochta, 24 soatda javob', 'sup_tg': 'Telegram, birinchi navbatda', 'sup_personal': 'shaxsiy menejer',
        'over_h': 'Limit tugasa', 'over': 'Servis o‘chmaydi — limitdan ortig‘i: 1 000 ko‘rsatuv uchun $2, 1 000 rasm uchun $5, bitta video uchun $0,10. Ortiqcha sarf shaxsiy kabinetda ko‘rinadi.',
        'plan_trial': 'Sinov', 'plan_starter': 'Starter', 'plan_pro': 'Pro', 'plan_business': 'Business', 'plan_enterprise': 'Enterprise',
        'how_h': 'Qanday ulanish',
        'how': ['Telegram yoki pochta orqali ariza qoldiring: sayt, oyiga qancha tovar va ko‘rsatuv.', 'Biz kalit beramiz va uni domeningizga bog‘laymiz — boshqa sayt kalitingizdan foydalana olmaydi.', 'Vidjetni qo‘ying yoki hujjatlar bo‘yicha API’ni ulang — odatda bir soat vaqt oladi.', '14 kun bepul, keyin tarifni tanlaysiz.'],
        'faq_h': 'Savollar',
        'faq': [
            ('Steam rasmlaridan farqi nima?', 'Steam’da butun skin uchun bitta rasm. Bizda — aynan shu buyum: uning float’i (eskirishi) va naqshi (rasm joylashuvi), 3D’da har tomondan.'),
            ('O‘yinga qanchalik o‘xshash?', 'Modellar va bo‘yoqlar CS2 fayllaridan yig‘iladi, o‘xshashlikni doimiy ravishda CSFloat va Steam bilan solishtiramiz. Ba’zi noyob bo‘yoqlar ustida ish davom etmoqda — pilot davomida natijani o‘z tovarlaringizda ko‘rsatamiz.'),
            ('Model fayllarini berasizmi?', 'Yo‘q. Siz ko‘rsatuv va tayyor rasm yoki videolarni olasiz; asl fayllar yopiq va domeningizga bog‘langan.'),
            ('Qachon ishga tushadi?', 'Hozir pilot mijozlarni yig‘moqdamiz: birinchilar bir oy bepul va tarifga chegirma oladi.'),
        ],
        'legal': 'DGhostMarket Valve Corporation bilan bog‘liq emas. CS2, Counter-Strike va Steam — Valve Corporation tovar belgilari. Servis buyumlarning tashqi ko‘rinishini ko‘rsatadi, lekin o‘yin fayllarini sotmaydi va tarqatmaydi.',
        'mail_subject': '3D-render uchun ariza',
    },
    'en': {
        'home': 'Home', 'crumb': '3D rendering for business',
        'title': 'CS2 skin 3D rendering for websites and stores — API and widget | DGhostMarket',
        'desc': 'Embeddable 3D viewer for CS2 skins with float and pattern, image and video API for marketplaces, trade bots and stores. Plans from $19 per month, 14-day free trial.',
        'badge': 'Coming soon · looking for pilot clients',
        'h1': 'CS2 skin 3D rendering <span>for your website</span>',
        'lead': 'The same 3D engine that powers the DGhostMarket marketplace: real finish, float and pattern of the exact item. Embed it on your site with a widget or get ready-made images and videos via API.',
        'cta': 'Apply for the pilot', 'cta_mail': 'Email us', 'cta_demo': 'See 3D in the marketplace',
        'what_h': 'What you get',
        'what': [
            ('🧊 3D widget', 'Add one line of code and your product page gets a 3D viewer: rotate, zoom, CS2 map backgrounds, wear by float and artwork by pattern.'),
            ('🖼 Image API', 'Send the skin, float and pattern — get a PNG or WebP from the angle you need. Results are cached, so repeat requests are instant.'),
            ('🎬 Video and GIF', 'A rotation clip or an in-hand inspect — for product cards, posts and ads.'),
            ('📐 AR on the table', 'Buyers place the skin on their desk at real size with their phone camera.'),
        ],
        'who_h': 'Who it is for',
        'who': ['skin marketplaces and stores', 'trade bots and Telegram shops', 'case and review sites, bloggers and streamers', 'inventory valuation and analytics services'],
        'plans_h': 'Pricing', 'plans_sub': 'Prices per month. Pay yearly and save 20%. Clients in Uzbekistan can pay in UZS with Humo or Uzcard.',
        'per_month': '/ mo', 'free': 'Free', 'trial_note': '14 days', 'custom': 'Custom', 'approx': '≈ {v} UZS',
        'best': 'Popular',
        'f_domains': 'Websites (domains)', 'f_views': '3D widget views', 'f_images': 'API images', 'f_videos': 'API videos and GIFs',
        'f_ar': 'AR on the table', 'f_badge': '“3D by DGhost” badge', 'f_brand': 'Custom background and branding', 'f_support': 'Support',
        'v_custom': 'custom', 'v_yes': '✓', 'v_no': '—',
        'badge_full': 'yes', 'badge_small': 'small', 'badge_off_opt': 'removable', 'badge_off': 'no',
        'sup_none': '—', 'sup_mail': 'email', 'sup_mail24': 'email, reply within 24 h', 'sup_tg': 'Telegram, priority', 'sup_personal': 'dedicated manager',
        'over_h': 'If you run out', 'over': 'Your service keeps working — overage is $2 per 1,000 views, $5 per 1,000 images and $0.10 per video. You can see it in your dashboard.',
        'plan_trial': 'Trial', 'plan_starter': 'Starter', 'plan_pro': 'Pro', 'plan_business': 'Business', 'plan_enterprise': 'Enterprise',
        'how_h': 'How to start',
        'how': ['Apply via Telegram or email: your site, number of products and monthly views.', 'We issue a key bound to your domain — no other site can use it.', 'Add the widget or connect the API using the docs — usually about an hour.', '14 days free, then pick a plan.'],
        'faq_h': 'FAQ',
        'faq': [
            ('How is this different from Steam images?', 'Steam has one image per skin. We render the exact item — its float (wear) and pattern (artwork placement) — in 3D from every side.'),
            ('How close is it to the game?', 'Models and finishes are built from CS2 game files, and we continuously compare them with CSFloat and Steam. Some rare finishes are still in progress — during the pilot we will show results on your items.'),
            ('Do you hand out model files?', 'No. You get the viewer and ready-made images or videos; source files stay private and bound to your domain.'),
            ('When is the launch?', 'We are onboarding pilot clients now: early clients get a free month and a discount on their plan.'),
        ],
        'legal': 'DGhostMarket is not affiliated with Valve Corporation. CS2, Counter-Strike and Steam are trademarks of Valve Corporation. The service shows the appearance of items and does not sell or distribute game files.',
        'mail_subject': '3D rendering request',
    },
}

CSS = """
.r3d .hero-badge{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:13px;color:var(--violet);margin:8px 0 18px}
.r3d .actions{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 8px}
.r3d h2{font-size:26px;margin:0 0 18px}
.r3d .block{padding:44px 0 0}
.r3d .cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.r3d .card{background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:18px}
.r3d .card b{display:block;font-size:17px;margin-bottom:8px}
.r3d .card p{color:var(--muted);font-size:15px;line-height:1.55;margin:0}
.r3d ul.who{display:flex;flex-wrap:wrap;gap:10px;list-style:none;padding:0;margin:0}
.r3d ul.who li{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:8px 14px;font-size:15px}
.r3d .sub{color:var(--muted);margin:-8px 0 20px;max-width:720px}
.r3d .plans{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.r3d .plan{position:relative;display:flex;flex-direction:column;background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:18px 16px}
.r3d .plan.best{border-color:var(--violet);box-shadow:0 8px 30px rgba(123,44,255,0.25)}
.r3d .plan .tag{position:absolute;top:-11px;left:16px;background:var(--grad);color:#fff;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:600}
.r3d .plan h3{margin:0 0 8px;font-size:18px}
.r3d .plan .price{font-size:28px;font-weight:800}
.r3d .plan .price small{font-size:14px;font-weight:500;color:var(--muted)}
.r3d .plan .approx{color:var(--muted);font-size:13px;min-height:18px;margin:2px 0 12px}
.r3d .plan dl{margin:0;display:grid;gap:8px}
.r3d .plan dt{color:var(--muted);font-size:12px}
.r3d .plan dd{margin:0;font-size:15px;font-weight:600}
.r3d .note{background:var(--surface);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:14px 16px;margin:18px 0 0;max-width:760px}
.r3d .note b{display:block;margin-bottom:4px}
.r3d ol.how{padding-left:22px;max-width:760px;margin:0}
.r3d ol.how li{margin:8px 0;font-size:17px;line-height:1.55}
.r3d details{background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:14px 16px;margin:0 0 10px;max-width:760px}
.r3d summary{cursor:pointer;font-weight:600}
.r3d details p{color:var(--muted);margin:10px 0 0;line-height:1.55}
.r3d .legal{color:var(--muted);font-size:13px;max-width:760px;margin:36px 0 56px}
@media(max-width:1000px){.r3d .plans{grid-template-columns:repeat(2,1fr)}.r3d .cards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.r3d .plans,.r3d .cards{grid-template-columns:1fr}}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def prefix(lang):
    return '' if lang == 'ru' else f'/{lang}'


def num(n, lang):
    s = f'{int(n):,}'
    return s if lang == 'en' else s.replace(',', ' ')


def _limit(v, t, lang):
    if v is None:
        return t['v_custom']
    return num(v, lang) if v else t['v_no']


def plan_card(p, lang):
    t = T[lang]
    if p['usd'] is None:
        price, approx = esc(t['custom']), ''
    elif p['usd'] == 0:
        price, approx = esc(t['free']), esc(t['trial_note'])
    else:
        price = f'${p["usd"]} <small>{esc(t["per_month"])}</small>'
        approx = esc(t['approx'].format(v=num(round(p['usd'] * RATE, -4), lang)))
    rows = [
        (t['f_domains'], _limit(p['domains'], t, lang)),
        (t['f_views'], _limit(p['views'], t, lang)),
        (t['f_images'], _limit(p['images'], t, lang)),
        (t['f_videos'], _limit(p['videos'], t, lang)),
        (t['f_ar'], t['v_yes'] if p['ar'] else t['v_no']),
        (t['f_badge'], t['badge_' + p['badge']]),
        (t['f_brand'], t['v_yes'] if p['brand'] else t['v_no']),
        (t['f_support'], t['sup_' + p['support']]),
    ]
    tag = f'<span class="tag">{esc(t["best"])}</span>' if p.get('best') else ''
    return (f'<div class="plan{" best" if p.get("best") else ""}">{tag}<h3>{esc(t["plan_" + p["key"]])}</h3>'
            f'<div class="price">{price}</div><div class="approx">{approx}</div><dl>'
            + ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in rows)
            + '</dl></div>')


def render_main(lang, app_url):
    t = T[lang]
    p = prefix(lang)
    mail = f'mailto:{SUPPORT_MAIL}?subject={quote(t["mail_subject"])}'
    actions = (f'<div class="actions"><a class="btn primary" href="{SUPPORT_TG}">{esc(t["cta"])}</a>'
               f'<a class="btn ghost" href="{esc(mail)}">{esc(t["cta_mail"])}</a>'
               f'<a class="btn ghost" href="{esc(app_url)}">{esc(t["cta_demo"])}</a></div>')
    what = ''.join(f'<div class="card"><b>{esc(h)}</b><p>{esc(x)}</p></div>' for h, x in t['what'])
    who = ''.join(f'<li>{esc(x)}</li>' for x in t['who'])
    plans = ''.join(plan_card(pl, lang) for pl in PLANS)
    how = ''.join(f'<li>{esc(x)}</li>' for x in t['how'])
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in t['faq'])
    return (f'<main id="top" class="r3d"><div class="wrap">'
            f'<nav class="crumbs"><a href="{p}/">{esc(t["home"])}</a> / {esc(t["crumb"])}</nav>'
            f'<div class="hero-badge">{esc(t["badge"])}</div>'
            f'<h1>{t["h1"]}</h1><p class="lead">{esc(t["lead"])}</p>{actions}'
            f'<div class="block"><h2>{esc(t["what_h"])}</h2><div class="cards">{what}</div></div>'
            f'<div class="block"><h2>{esc(t["who_h"])}</h2><ul class="who">{who}</ul></div>'
            f'<div class="block" id="plans"><h2>{esc(t["plans_h"])}</h2><p class="sub">{esc(t["plans_sub"])}</p>'
            f'<div class="plans">{plans}</div>'
            f'<div class="note"><b>{esc(t["over_h"])}</b>{esc(t["over"])}</div></div>'
            f'<div class="block"><h2>{esc(t["how_h"])}</h2><ol class="how">{how}</ol></div>'
            f'<div class="block"><h2>{esc(t["faq_h"])}</h2>{faq}{actions}</div>'
            f'<p class="legal">{esc(t["legal"])}</p>'
            f'</div></main>')


def offer_jsonld(lang, url, site):
    t = T[lang]
    offers = [{'@type': 'Offer', 'name': t['plan_' + p['key']], 'price': str(p['usd']), 'priceCurrency': 'USD'}
              for p in PLANS if p['usd'] is not None]
    return {
        '@context': 'https://schema.org', '@type': 'Service', 'name': t['crumb'], 'description': t['desc'],
        'url': url, 'inLanguage': lang, 'serviceType': '3D rendering API',
        'provider': {'@type': 'Organization', 'name': 'DGhostMarket', 'url': site + '/'},
        'offers': offers,
    }
