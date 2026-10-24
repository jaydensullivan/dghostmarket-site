"""Сервис 3D-рендера (DGhost 3D): страница /3d-api/ на сайте маркета (ru, uz, en)
и отдельный сайт render.dghostmarket.com (render_site: en, ru, uz + условия,
конфиденциальность, возвраты). Сейчас продаётся только виджет; API картинок
и видео в разработке — в тарифах его нет.
Тарифы — в PLANS (цены в долларах; суммы в сумах — по RATE, округлены).
"""
import os
import html
from urllib.parse import quote

LANGS = ['ru', 'uz', 'en']
# Заявки — в личные сообщения канала @dghostmarket.
SUPPORT_TG = 'https://t.me/dghostmarket?direct'
EMBED_URL = 'https://app.dghostmarket.uz/embed.html'
# Скины для живого демо (ключ demo работает только на наших сайтах).
DEMO_SKINS = [
    ('AK-47 | Redline', 0.15, 661),
    ('★ Karambit | Fade', 0.012, 412),
    ('AWP | Asiimov', 0.24, 77),
    ('M4A1-S | Printstream', 0.08, 233),
    ('★ Butterfly Knife | Doppler', 0.02, 905),
]
SUPPORT_MAIL = 'support@dghostmarket.uz'
def _load_rate(default=11900):
    """Курс сум за $ из data/rate.json (его обновляет build.py) — только для подписи «≈ … сум»."""
    try:
        import json as _json
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'rate.json'), encoding='utf-8') as f:
            return float(_json.load(f)['usd_uzs']) or default
    except Exception:
        return default


RATE = _load_rate()

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
        'title': '3D-просмотр скинов CS2 для вашего сайта — виджет | DGhost 3D',
        'desc': 'Встраиваемый 3D-просмотр скинов CS2 с float, паттерном и наклейками для маркетплейсов, трейд-ботов и магазинов. Тарифы от $19 в месяц, 14 дней бесплатно.',
        'badge': '14 дней бесплатно',
        'h1': '3D-рендер скинов CS2 <span>для вашего сайта</span>',
        'lead': 'Тот же 3D-движок, что в маркете DGhostMarket: реальная раскраска, float и паттерн конкретного предмета. Добавьте виджет на страницу товара одной строкой кода.',
        'cta': 'Получить пробный ключ', 'cta_mail': 'Написать на почту', 'cta_demo': 'Посмотреть 3D в маркете',
        'demo_h': 'Попробуйте прямо здесь', 'demo_sub': 'Это и есть виджет — так он будет выглядеть на вашем сайте. Крутите пальцем или мышкой, переключайте фоны и износ.',
        'code_h': 'Код для вашего сайта', 'code_sub': 'Ключ выдаём сразу по запросу. Скин, float и паттерн подставляете из своих товаров.',
        'what_h': 'Что вы получаете',
        'what': [('🧊 3D-виджет', 'Одна строка кода — и на странице товара 3D-просмотр: вращение, приближение, фоны карт CS2, износ по float, рисунок по паттерну и наклейки.'), ('📐 AR «на столе»', 'Покупатель ставит скин на свой стол через камеру телефона в натуральную величину.'), ('🔑 Ключ под ваш домен', 'Ключ работает только на ваших сайтах — чужой сайт его не использует. Домены добавляете сами.'), ('📊 Кабинет и статистика', 'Показы за месяц, лимит тарифа и код для вставки — в личном кабинете.')],
        'who_h': 'Кому подходит',
        'who': ['маркетплейсам и магазинам скинов', 'трейд-ботам и Telegram-магазинам', 'сайтам с кейсами и обзорами, блогерам и стримерам', 'сервисам оценки и аналитики инвентаря'],
        'plans_h': 'Тарифы', 'plans_sub': 'Цены в месяц. При оплате за год — скидка 20%. Отменить подписку можно в любой момент.',
        'per_month': '/ мес', 'free': 'Бесплатно', 'trial_note': '14 дней', 'custom': 'Договорная', 'approx': '≈ {v} сум',
        'best': 'Популярный',
        'f_domains': 'Сайтов (доменов)', 'f_views': 'Показы 3D-виджета', 'f_images': 'Картинки по API', 'f_videos': 'Видео и GIF по API',
        'f_ar': 'AR «на столе»', 'f_badge': 'Значок «3D by DGhost»', 'f_brand': 'Свой фон и брендинг', 'f_support': 'Поддержка',
        'v_custom': 'по договору', 'v_yes': '✓', 'v_no': '—',
        'badge_full': 'есть', 'badge_small': 'маленький', 'badge_off_opt': 'можно убрать', 'badge_off': 'нет',
        'sup_none': '—', 'sup_mail': 'почта', 'sup_mail24': 'почта, ответ за 24 ч', 'sup_tg': 'Telegram, в приоритете', 'sup_personal': 'персональный менеджер',
        'over_h': 'Если лимит закончился', 'over': 'Виджет не отключается — сверх лимита: $2 за каждые 1 000 показов. Перерасход виден в личном кабинете.',
        'plan_trial': 'Пробный', 'plan_starter': 'Starter', 'plan_pro': 'Pro', 'plan_business': 'Business', 'plan_enterprise': 'Enterprise',
        'how_h': 'Как подключиться',
        'how': ['Напишите нам в Telegram или на почту: адрес сайта и примерное число показов в месяц.', 'Выдадим пробный ключ на 14 дней и привяжем его к вашему домену.', 'Вставьте код виджета на страницу товара — обычно это занимает несколько минут.', 'Понравилось — выбираете тариф и оплачиваете подписку.'],
        'faq_h': 'Вопросы',
        'faq': [('Чем отличается от картинок Steam?', 'В Steam одна картинка на весь скин. У нас — конкретный предмет: его float (потёртости) и паттерн (положение рисунка), в 3D со всех сторон.'), ('Насколько похоже на игру?', 'Модели и раскраски собираются из файлов CS2, сходство мы постоянно сверяем с CSFloat и Steam. Для части редких раскрасок работа ещё идёт — в пробный период проверите на своих товарах.'), ('Вы отдаёте файлы моделей?', 'Нет. Модели показываются только внутри виджета на ваших доменах; файлы не скачиваются и не передаются.'), ('Есть ли API картинок и видео?', 'Готовые картинки и ролики по API — в разработке. Если вам это нужно, напишите: учтём ваш формат и сообщим о запуске.')],
        'legal': 'DGhost 3D не связан с Valve Corporation. CS2, Counter-Strike и Steam — товарные знаки Valve Corporation. Сервис показывает внешний вид предметов, но не продаёт игровые предметы и не распространяет игровые файлы.',
        'mail_subject': 'Заявка на 3D-рендер',
    },
    'uz': {
        'home': 'Bosh sahifa', 'crumb': 'Biznes uchun 3D-render',
        'title': 'Saytingiz uchun CS2 skinlarining 3D-ko‘rinishi — vidjet | DGhost 3D',
        'desc': 'Marketpleyslar, treyd-botlar va do‘konlar uchun CS2 skinlarini float, naqsh va stikerlar bilan 3D ko‘rsatuvchi vidjet. Tariflar oyiga $19 dan, 14 kun bepul.',
        'badge': '14 kun bepul',
        'h1': 'CS2 skinlarining 3D-renderi <span>saytingiz uchun</span>',
        'lead': 'DGhostMarket marketidagi o‘sha 3D-dvigatel: aynan shu buyumning haqiqiy bo‘yog‘i, float va naqshi. Vidjetni tovar sahifasiga bitta qator kod bilan qo‘shing.',
        'cta': 'Sinov kalitini olish', 'cta_mail': 'Pochtaga yozish', 'cta_demo': 'Marketda 3D’ni ko‘rish',
        'demo_h': 'Shu yerning o‘zida sinab ko‘ring', 'demo_sub': 'Bu vidjetning o‘zi — saytingizda ham xuddi shunday ko‘rinadi. Barmoq yoki sichqoncha bilan aylantiring, fon va eskirishni almashtiring.',
        'code_h': 'Saytingiz uchun kod', 'code_sub': 'Kalitni so‘rov bo‘yicha darhol beramiz. Skin, float va naqshni o‘z tovarlaringizdan qo‘yasiz.',
        'what_h': 'Siz nimani olasiz',
        'what': [('🧊 3D-vidjet', 'Bitta qator kod — va tovar sahifasida 3D-ko‘rinish: aylantirish, yaqinlashtirish, CS2 xaritalari fonlari, float bo‘yicha eskirish, naqsh va stikerlar.'), ('📐 AR «Stolda»', 'Xaridor telefon kamerasi orqali skinni stoliga haqiqiy o‘lchamda qo‘yadi.'), ('🔑 Domeningizga kalit', 'Kalit faqat sizning saytlaringizda ishlaydi — boshqa sayt undan foydalana olmaydi. Domenlarni o‘zingiz qo‘shasiz.'), ('📊 Kabinet va statistika', 'Oylik ko‘rsatuvlar, tarif limiti va joylash kodi — shaxsiy kabinetda.')],
        'who_h': 'Kimlar uchun',
        'who': ['skin marketpleyslari va do‘konlari', 'treyd-botlar va Telegram-do‘konlar', 'keys va obzor saytlari, blogerlar va strimerlar', 'inventarni baholash va tahlil qilish servislari'],
        'plans_h': 'Tariflar', 'plans_sub': 'Narxlar oyiga. Bir yilga to‘lasangiz — 20% chegirma. Obunani istalgan vaqtda bekor qilish mumkin.',
        'per_month': '/ oy', 'free': 'Bepul', 'trial_note': '14 kun', 'custom': 'Kelishilgan', 'approx': '≈ {v} so‘m',
        'best': 'Ommabop',
        'f_domains': 'Saytlar (domenlar)', 'f_views': '3D-vidjet ko‘rsatuvlari', 'f_images': 'API orqali rasmlar', 'f_videos': 'API orqali video va GIF',
        'f_ar': 'AR «Stolda»', 'f_badge': '«3D by DGhost» belgisi', 'f_brand': 'O‘z foni va brendingi', 'f_support': 'Yordam',
        'v_custom': 'kelishuv bo‘yicha', 'v_yes': '✓', 'v_no': '—',
        'badge_full': 'bor', 'badge_small': 'kichik', 'badge_off_opt': 'olib tashlash mumkin', 'badge_off': 'yo‘q',
        'sup_none': '—', 'sup_mail': 'pochta', 'sup_mail24': 'pochta, 24 soatda javob', 'sup_tg': 'Telegram, birinchi navbatda', 'sup_personal': 'shaxsiy menejer',
        'over_h': 'Limit tugasa', 'over': 'Vidjet o‘chmaydi — limitdan ortig‘i: har 1 000 ko‘rsatuv uchun $2. Ortiqcha sarf shaxsiy kabinetda ko‘rinadi.',
        'plan_trial': 'Sinov', 'plan_starter': 'Starter', 'plan_pro': 'Pro', 'plan_business': 'Business', 'plan_enterprise': 'Enterprise',
        'how_h': 'Qanday ulanish',
        'how': ['Telegram yoki pochta orqali yozing: sayt manzili va oyiga taxminiy ko‘rsatuvlar soni.', '14 kunlik sinov kalitini beramiz va uni domeningizga bog‘laymiz.', 'Vidjet kodini tovar sahifasiga qo‘ying — odatda bir necha daqiqa.', 'Yoqdimi — tarifni tanlaysiz va obunani to‘laysiz.'],
        'faq_h': 'Savollar',
        'faq': [('Steam rasmlaridan farqi nima?', 'Steam’da butun skin uchun bitta rasm. Bizda — aynan shu buyum: uning float’i (eskirishi) va naqshi (rasm joylashuvi), 3D’da har tomondan.'), ('O‘yinga qanchalik o‘xshash?', 'Modellar va bo‘yoqlar CS2 fayllaridan yig‘iladi, o‘xshashlikni doimiy ravishda CSFloat va Steam bilan solishtiramiz. Ba’zi noyob bo‘yoqlar ustida ish davom etmoqda — sinov davrida o‘z tovarlaringizda tekshirasiz.'), ('Model fayllarini berasizmi?', 'Yo‘q. Modellar faqat domenlaringizdagi vidjet ichida ko‘rsatiladi; fayllar yuklab olinmaydi va berilmaydi.'), ('Rasm va video API bormi?', 'API orqali tayyor rasm va roliklar — ishlab chiqilmoqda. Agar kerak bo‘lsa, yozing: formatingizni hisobga olamiz va ishga tushganda xabar beramiz.')],
        'legal': 'DGhost 3D Valve Corporation bilan bog‘liq emas. CS2, Counter-Strike va Steam — Valve Corporation tovar belgilari. Servis buyumlarning tashqi ko‘rinishini ko‘rsatadi, lekin o‘yin buyumlarini sotmaydi va o‘yin fayllarini tarqatmaydi.',
        'mail_subject': '3D-render uchun ariza',
    },
    'en': {
        'home': 'Home', 'crumb': '3D rendering for business',
        'title': '3D viewer for CS2 skins on your website — embeddable widget | DGhost 3D',
        'desc': 'Embeddable 3D viewer for CS2 skins with float, pattern and stickers for marketplaces, trade bots and stores. Plans from $19 per month, 14-day free trial.',
        'badge': '14-day free trial',
        'h1': 'CS2 skin 3D rendering <span>for your website</span>',
        'lead': 'The same 3D engine that powers the DGhostMarket marketplace: real finish, float and pattern of the exact item. Add the viewer to your product page with one line of code.',
        'cta': 'Get a trial key', 'cta_mail': 'Email us', 'cta_demo': 'See 3D in action',
        'demo_h': 'Try it right here', 'demo_sub': 'This is the widget itself — it will look the same on your website. Drag to rotate, switch backgrounds and wear.',
        'code_h': 'Code for your website', 'code_sub': 'We issue your key on request. Fill in the skin, float and pattern from your own listings.',
        'what_h': 'What you get',
        'what': [('🧊 3D widget', 'One line of code adds a 3D viewer to your product page: rotate, zoom, CS2 map backgrounds, wear by float, artwork by pattern and stickers.'), ('📐 AR on the table', 'Buyers place the skin on their desk at real size with their phone camera.'), ('🔑 Domain-locked key', 'Your key only works on your own websites — no one else can use it. You add your domains yourself.'), ('📊 Dashboard and usage', 'Monthly views, plan limit and the embed code — all in your dashboard.')],
        'who_h': 'Who it is for',
        'who': ['skin marketplaces and stores', 'trade bots and Telegram shops', 'case and review sites, bloggers and streamers', 'inventory valuation and analytics services'],
        'plans_h': 'Pricing', 'plans_sub': 'Prices per month. Pay yearly and save 20%. Cancel anytime.',
        'per_month': '/ mo', 'free': 'Free', 'trial_note': '14 days', 'custom': 'Custom', 'approx': '≈ {v} UZS',
        'best': 'Popular',
        'f_domains': 'Websites (domains)', 'f_views': '3D widget views', 'f_images': 'API images', 'f_videos': 'API videos and GIFs',
        'f_ar': 'AR on the table', 'f_badge': '“3D by DGhost” badge', 'f_brand': 'Custom background and branding', 'f_support': 'Support',
        'v_custom': 'custom', 'v_yes': '✓', 'v_no': '—',
        'badge_full': 'yes', 'badge_small': 'small', 'badge_off_opt': 'removable', 'badge_off': 'no',
        'sup_none': '—', 'sup_mail': 'email', 'sup_mail24': 'email, reply within 24 h', 'sup_tg': 'Telegram, priority', 'sup_personal': 'dedicated manager',
        'over_h': 'If you run out', 'over': 'Your widget keeps working — overage is $2 per 1,000 views. You can see it in your dashboard.',
        'plan_trial': 'Trial', 'plan_starter': 'Starter', 'plan_pro': 'Pro', 'plan_business': 'Business', 'plan_enterprise': 'Enterprise',
        'how_h': 'How to start',
        'how': ['Message us on Telegram or by email: your website and roughly how many views per month.', 'We issue a 14-day trial key bound to your domain.', 'Paste the widget code into your product page — usually a few minutes.', 'Happy with it? Pick a plan and subscribe.'],
        'faq_h': 'FAQ',
        'faq': [('How is this different from Steam images?', 'Steam has one image per skin. We render the exact item — its float (wear) and pattern (artwork placement) — in 3D from every side.'), ('How close is it to the game?', 'Models and finishes are built from CS2 game files, and we continuously compare them with CSFloat and Steam. Some rare finishes are still in progress — check them on your own items during the trial.'), ('Do you hand out model files?', 'No. Models are displayed only inside the widget on your domains; files are not downloadable or transferred.'), ('Do you offer an image or video API?', 'Ready-made images and videos via API are in development. If you need them, let us know your format and we will notify you at launch.')],
        'legal': 'DGhost 3D is not affiliated with Valve Corporation. CS2, Counter-Strike and Steam are trademarks of Valve Corporation. The service displays the appearance of items; it does not sell in-game items or distribute game files.',
        'mail_subject': '3D rendering request',
    },
}

CSS = """
.r3d .wrap > .hero-badge:first-child{margin-top:32px}
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
.r3d .demo{display:grid;grid-template-columns:1fr;gap:12px;max-width:900px}
.r3d .demo iframe{width:100%;height:440px;border:0;border-radius:18px;background:#0c0816}
.r3d .demo-skins{display:flex;flex-wrap:wrap;gap:8px}
.r3d .demo-skins button{font:inherit;font-size:14px;color:var(--text);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}
.r3d .demo-skins button.on{background:var(--grad);border-color:transparent;color:#fff}
.r3d pre.code{background:#0c0816;border:1px solid var(--line);border-radius:14px;padding:14px 16px;overflow-x:auto;font-size:13px;line-height:1.5;color:#d8c8ff;max-width:900px;white-space:pre-wrap;word-break:break-all}
@media(max-width:1000px){.r3d .plans{grid-template-columns:repeat(2,1fr)}.r3d .cards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.r3d .plans,.r3d .cards{grid-template-columns:1fr}.r3d .demo iframe{height:360px}}
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


def embed_src(key, skin, lang):
    name, flt, seed = skin
    return f'{EMBED_URL}?key={key}&skin={quote(name)}&float={flt}&seed={seed}&lang={lang}'


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
    first = DEMO_SKINS[0]
    src = embed_src('demo', first, lang)
    buttons = ''.join(
        '<button type="button"' + (' class="on"' if i == 0 else '') + f' data-src="{esc(embed_src("demo", d, lang))}">'
        f'{esc(d[0].replace("★ ", ""))}</button>' for i, d in enumerate(DEMO_SKINS))
    demo = (f'<div class="block" id="demo"><h2>{esc(t["demo_h"])}</h2><p class="sub">{esc(t["demo_sub"])}</p>'
            f'<div class="demo"><iframe id="demoFrame" src="{esc(src)}" title="3D" loading="lazy" '
            'allow="xr-spatial-tracking; fullscreen" allowfullscreen></iframe><div class="demo-skins">' + buttons + '</div></div>'
            '<script>document.querySelectorAll(".demo-skins button").forEach(function(b){b.addEventListener("click",function(){'
            'document.getElementById("demoFrame").src=b.dataset.src;'
            'document.querySelectorAll(".demo-skins button").forEach(function(x){x.classList.toggle("on",x===b);});});});</script></div>')
    code = esc('<iframe src="' + embed_src('YOUR_KEY', first, lang) + '"\n  width="100%" height="420" style="border:0;border-radius:12px"\n  allow="xr-spatial-tracking; fullscreen" allowfullscreen loading="lazy"></iframe>')
    return (f'<main id="top" class="r3d"><div class="wrap">'
            f'<nav class="crumbs"><a href="{p}/">{esc(t["home"])}</a> / {esc(t["crumb"])}</nav>'
            f'<div class="hero-badge">{esc(t["badge"])}</div>'
            f'<h1>{t["h1"]}</h1><p class="lead">{esc(t["lead"])}</p>{actions}'
            f'{demo}'
            f'<div class="block"><h2>{esc(t["what_h"])}</h2><div class="cards">{what}</div></div>'
            f'<div class="block"><h2>{esc(t["who_h"])}</h2><ul class="who">{who}</ul></div>'
            f'<div class="block" id="plans"><h2>{esc(t["plans_h"])}</h2><p class="sub">{esc(t["plans_sub"])}</p>'
            f'<div class="plans">{plans}</div>'
            f'<div class="note"><b>{esc(t["over_h"])}</b>{esc(t["over"])}</div></div>'
            f'<div class="block"><h2>{esc(t["how_h"])}</h2><ol class="how">{how}</ol></div>'
            f'<div class="block"><h2>{esc(t["code_h"])}</h2><p class="sub">{esc(t["code_sub"])}</p><pre class="code">{code}</pre></div>'
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


# ---------- Отдельный сайт render.dghostmarket.com ----------
# Собирается в папку render/ этого репозитория; на поддомене его отдаёт
# Worker «dghost-render-site» (репозиторий dghost-3d-pipeline, папка
# render-site): / → /render/, а шрифты, иконки и картинки — из корня сайта.
# Английский — основной язык (клиенты в основном за рубежом).

RENDER_SITE = 'https://render.dghostmarket.com'
SITE_LANGS = ['en', 'ru', 'uz']
# Оператор сервиса — для условий и политики. Юридическое имя ИП впишем, когда
# владелец пришлёт данные (пока — торговое имя и страна регистрации).
OPERATOR = 'DGhostMarket, an individual entrepreneur registered in the Republic of Uzbekistan'


def site_prefix(lang):
    return '' if lang == 'en' else f'/{lang}'


def site_url(lang, path=''):
    return f'{RENDER_SITE}{site_prefix(lang)}/{path}'


SITE_T = {
    'en': {'nav_demo': 'Demo', 'nav_plans': 'Pricing', 'nav_faq': 'FAQ', 'cta_short': 'Get a key',
           'terms': 'Terms of Service', 'privacy': 'Privacy Policy', 'refund': 'Refund Policy', 'contact': 'Contact'},
    'ru': {'nav_demo': 'Демо', 'nav_plans': 'Тарифы', 'nav_faq': 'Вопросы', 'cta_short': 'Получить ключ',
           'terms': 'Условия использования', 'privacy': 'Конфиденциальность', 'refund': 'Возвраты', 'contact': 'Контакты'},
    'uz': {'nav_demo': 'Demo', 'nav_plans': 'Tariflar', 'nav_faq': 'Savollar', 'cta_short': 'Kalit olish',
           'terms': 'Foydalanish shartlari', 'privacy': 'Maxfiylik', 'refund': 'Qaytarish', 'contact': 'Aloqa'},
}


def site_header(lang, path='', path_langs=None):
    """Шапка. path_langs — на каких языках есть эта страница: на остальные
    переключатель ведёт на главную (условия, например, только на английском)."""
    t = SITE_T[lang]
    p = site_prefix(lang)
    on = ' class="on"'
    langs = ''.join(
        f'<a href="{site_prefix(l)}/{path if path_langs is None or l in path_langs else ""}" hreflang="{l}"'
        f'{on if l == lang else ""}>{l.upper()}</a>'
        for l in SITE_LANGS)
    return (f'<header><div class="wrap bar"><a class="brand" href="{p}/"><img src="/favicon.png" alt=""><span>DGhost<b>3D</b></span></a>'
            f'<nav class="links"><a href="{p}/#demo">{esc(t["nav_demo"])}</a><a href="{p}/#plans">{esc(t["nav_plans"])}</a>'
            f'<a href="{p}/#faq">{esc(t["nav_faq"])}</a></nav>'
            f'<div class="langs" role="group" aria-label="Language">{langs}</div>'
            f'<a class="btn primary small" href="{SUPPORT_TG}">{esc(t["cta_short"])}</a></div></header>')


def site_footer(lang):
    t = SITE_T[lang]
    return (f'<footer><div class="wrap"><div>© 2026 DGhost 3D · <a href="/terms/">{esc(t["terms"])}</a> · '
            f'<a href="/privacy/">{esc(t["privacy"])}</a> · <a href="/refund/">{esc(t["refund"])}</a> · '
            f'<a href="mailto:{SUPPORT_MAIL}">{SUPPORT_MAIL}</a></div>'
            f'<div>{esc(T[lang]["legal"])}</div></div></footer>')


def site_alternates(path=''):
    out = [f'<link rel="alternate" hreflang="{l}" href="{site_url(l, path)}">' for l in SITE_LANGS]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{site_url("en", path)}">')
    return '\n'.join(out)


LEGAL = {
    'terms': ('Terms of Service', [
        ('Service', 'DGhost 3D ("we", "the Service") is a hosted 3D viewer for Counter-Strike 2 item listings, operated by '
                    f'{OPERATOR}. Customers embed the viewer on their own websites with an API key bound to their domains.'),
        ('Accounts and keys', 'You are responsible for the websites you add to your key and for keeping your key private. '
                              'Keys only work on the domains you register. We may suspend a key used on domains you do not control.'),
        ('Trial, plans and billing', 'New customers get a 14-day free trial with 1,000 widget views. Paid plans are billed monthly '
                                     '(or yearly with a 20% discount) in advance and renew until cancelled. Views above your plan '
                                     'limit are billed at $2 per 1,000 views at the end of the billing month. After a payment is '
                                     'missed, the widget keeps working for 3 days and is then disabled until the plan is renewed.'),
        ('Cancellation', 'You can cancel at any time; the plan stays active until the end of the paid period.'),
        ('Acceptable use', 'You may use the Service only to display items on your own websites. You may not attempt to download, '
                           'extract or redistribute the 3D models or textures, resell access to your key, or use the Service '
                           'for gambling or any activity that is illegal where you or your users are located.'),
        ('What we do not do', 'The Service displays the appearance of in-game items. We do not sell, trade or transfer in-game '
                              'items, game currency or game accounts, and we do not distribute game files. DGhost 3D is not '
                              'affiliated with Valve Corporation; CS2, Counter-Strike and Steam are trademarks of Valve Corporation.'),
        ('Availability and liability', 'We aim for continuous availability but do not guarantee it. To the extent permitted by law, '
                                       'our total liability is limited to the amount you paid for the Service in the previous three months.'),
        ('Changes', 'We may update these terms; material changes will be announced to customers by email or Telegram at least '
                    '14 days in advance.'),
        ('Contact', f'Questions: {SUPPORT_MAIL}'),
    ]),
    'privacy': ('Privacy Policy', [
        ('What we collect', 'Contact details you give us (email or Telegram account), the domains you register for your key, '
                            'and usage statistics of the widget: number of views per key and month. To avoid counting the same '
                            'visitor twice, the widget server briefly keeps the visitor IP address in memory (up to 30 minutes); '
                            'it is not stored in our database.'),
        ('What we do not collect', 'We do not use advertising trackers in the widget and do not sell or share personal data with third '
                                   'parties, except payment processors that handle your payments.'),
        ('Payments', 'Payments are processed by our payment provider; we do not receive or store your card details.'),
        ('Retention and deletion', 'We keep account data while your key is active and for up to 12 months after. You can ask us '
                                   f'to delete your data at any time: {SUPPORT_MAIL}.'),
        ('Operator', OPERATOR + '.'),
    ]),
    'refund': ('Refund Policy', [
        ('Free trial first', 'Every new customer gets a 14-day free trial, so you can check the Service on your own listings before paying.'),
        ('Refunds', 'If the Service does not work as described, you can request a full refund within 14 days of your first payment '
                    'for a plan. Renewals can be refunded within 7 days if the widget was not used in the new period.'),
        ('Overage', 'Overage charges for views already served are not refundable.'),
        ('How to request', f'Email {SUPPORT_MAIL} with your key or the email used for payment. We reply within 2 business days.'),
    ]),
}


def legal_main(kind):
    title, sections = LEGAL[kind]
    body = ''.join(f'<h2>{esc(h)}</h2><p>{esc(x)}</p>' for h, x in sections)
    return (f'<main id="top" class="r3d legal-page"><div class="wrap"><h1>{esc(title)}</h1>'
            f'<p class="sub">Last updated: 2026-10-20</p>{body}</div></main>')


LEGAL_CSS = """
.legal-page h1{font-size:34px;margin:40px 0 8px}
.legal-page h2{font-size:20px;margin:28px 0 8px}
.legal-page p{max-width:760px;line-height:1.65;color:var(--text)}
.legal-page{padding-bottom:56px}
"""
