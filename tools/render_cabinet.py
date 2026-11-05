"""Самостоятельная регистрация и кабинет клиента DGhost 3D (ru, uz, en).

Регистрация — блок #start на странице /3d-api/ (и на render.dghostmarket.com):
почта + сайт → сервис dghost-3d-api сразу выдаёт пробный ключ на 14 дней и
ссылку в кабинет. Кабинет — /3d-api/cabinet/: ключ, показы, сайты, код,
оплата тарифа (окно Paddle, когда платёжка подключена; до этого — «напишите нам»).

Вход в кабинет — секретная ссылка …/cabinet/#t=<токен>; браузер её запоминает
(localStorage), токен из адреса сразу убирается.
"""

import html
import json

API = 'https://dghost-3d-api-production.up.railway.app'
CABINET_PATH = '3d-api/cabinet/'
MARKET_SITE = 'https://dghostmarket.uz'


def esc(s):
    return html.escape(str(s), quote=True)


# Кабинет — на сайте сервиса render.dghostmarket.com: окно оплаты Paddle
# открывается только на сайте, одобренном в Paddle (это он, не маркет).
RENDER_SITE = 'https://render.dghostmarket.com'


def cabinet_url(lang):
    return f'{RENDER_SITE}{"" if lang == "en" else "/" + lang}/cabinet/'


def redirect_page_main(lang):
    """Старый адрес кабинета на dghostmarket.uz: ведём на render.dghostmarket.com
    вместе с ссылкой входа (а если её нет в адресе — с запомненной этим браузером)."""
    target = json.dumps(cabinet_url(lang))
    return ('<main id="top" class="r3d cab"><div class="wrap"><div class="center"><p>…</p></div></div></main>'
            '<script>(function(){var t=' + target + ';var h=location.hash;'
            'if(!/t=/.test(h)){try{var s=localStorage.getItem("dg3d_cab");if(s)h="#t="+s;}catch(e){}}'
            'location.replace(t+location.search+h);})();</script>')


TX = {
    'ru': {
        'start_h': 'Начать бесплатно', 'start_sub': '14 дней и 1 000 показов без оплаты и без карты. Ключ — сразу, на ваш сайт.',
        'f_email': 'Рабочая почта', 'f_site': 'Адрес сайта', 'f_name': 'Название проекта (необязательно)',
        'ph_site': 'shop.uz', 'start_btn': 'Получить ключ', 'start_wait': 'Создаём ключ…',
        'start_note': 'Нажимая кнопку, вы соглашаетесь с условиями сервиса. Почта нужна, чтобы связаться по ключу и оплате.',
        'plan_try': 'Начать бесплатно', 'plan_sub': 'Подписаться', 'plan_contact': 'Обсудить',
        'e_bad_email': 'Проверьте адрес почты.', 'e_bad_website': 'Укажите адрес сайта, например shop.uz.',
        'e_email_taken': 'На эту почту уже есть кабинет. Откройте его по своей ссылке или напишите нам — пришлём новую.',
        'e_domain_taken': 'Этот сайт уже подключён. Если это ваш сайт — напишите нам.',
        'e_too_many_signups': 'Слишком много попыток с этого адреса. Попробуйте завтра или напишите нам.',
        'e_network': 'Сервис не ответил. Проверьте интернет и попробуйте ещё раз.',
        'cab_title': 'Кабинет DGhost 3D', 'cab_loading': 'Загружаем кабинет…',
        'cab_noauth_h': 'Нужна ссылка на кабинет', 'cab_noauth': 'Кабинет открывается по личной ссылке, которую вы получили при регистрации. Нет ссылки — зарегистрируйтесь или напишите нам.',
        'cab_signup': 'Зарегистрироваться', 'cab_contact': 'Написать в Telegram',
        'cab_save_h': 'Сохраните ссылку на кабинет', 'cab_save': 'Это ваш вход — почты и пароля нет. Добавьте страницу в закладки или скопируйте ссылку в надёжное место.',
        'cab_copy_link': 'Скопировать ссылку', 'copied': 'Скопировано', 'cab_new_link': 'Выдать новую ссылку',
        'cab_new_confirm': 'Старая ссылка перестанет работать. Продолжить?',
        'cab_key': 'Ключ', 'cab_plan': 'Тариф', 'cab_until': 'до {d}', 'cab_expired': 'Срок закончился — виджет на сайте не показывается. Выберите тариф ниже.',
        'cab_sub_on': 'Подписка продлевается сама.', 'cab_sub_cancel': 'Подписка отменена — ключ работает до конца оплаченного срока.',
        'cab_views': 'Показы в этом месяце', 'cab_nolimit': 'без лимита',
        'cab_domains': 'Сайты, где работает виджет', 'cab_domains_max': 'до {n}', 'cab_save_btn': 'Сохранить', 'cab_saved': 'Сохранено',
        'cab_code': 'Код для страницы товара', 'cab_copy': 'Скопировать код',
        'cab_usage': 'Показы по месяцам', 'cab_month': 'Месяц', 'cab_shown': 'Показано', 'cab_denied': 'Отказано',
        'cab_plans': 'Тарифы', 'per_month': '/ мес', 'per_year': '/ год', 'm_month': 'Помесячно', 'm_year': 'За год −20%',
        'cab_current': 'Ваш тариф', 'cab_choose': 'Выбрать', 'cab_contact_plan': 'Написать нам',
        'cab_views_n': '{n} показов', 'cab_domains_n': 'сайтов: {n}', 'cab_ar': 'AR «на столе»', 'cab_nobadge': 'без значка',
        'cab_pay_soon_h': 'Оплата картой подключается', 'cab_pay_soon': 'Пока оплата — через нас: напишите в Telegram или на почту, укажите тариф и ключ, пришлём счёт. Ключ продлим сразу после оплаты.',
        'cab_paid': 'Оплата прошла — обновляем тариф…', 'e_bad_domains': 'Проверьте адреса сайтов.',
        'e_too_many_domains': 'Сайтов в вашем тарифе: не больше {n}.', 'e_unauthorized': 'Ссылка устарела. Откройте новую ссылку на кабинет.',
    },
    'uz': {
        'start_h': 'Bepul boshlash', 'start_sub': '14 kun va 1 000 ko‘rsatuv — to‘lovsiz va kartasiz. Kalit darhol, saytingiz uchun.',
        'f_email': 'Ish pochtasi', 'f_site': 'Sayt manzili', 'f_name': 'Loyiha nomi (ixtiyoriy)',
        'ph_site': 'shop.uz', 'start_btn': 'Kalitni olish', 'start_wait': 'Kalit yaratilmoqda…',
        'start_note': 'Tugmani bosib, xizmat shartlariga rozilik bildirasiz. Pochta kalit va to‘lov bo‘yicha bog‘lanish uchun kerak.',
        'plan_try': 'Bepul boshlash', 'plan_sub': 'Obuna bo‘lish', 'plan_contact': 'Muhokama qilish',
        'e_bad_email': 'Pochta manzilini tekshiring.', 'e_bad_website': 'Sayt manzilini kiriting, masalan shop.uz.',
        'e_email_taken': 'Bu pochtaga kabinet allaqachon bor. Uni o‘z havolangiz orqali oching yoki bizga yozing — yangisini yuboramiz.',
        'e_domain_taken': 'Bu sayt allaqachon ulangan. Agar sayt sizniki bo‘lsa — bizga yozing.',
        'e_too_many_signups': 'Bu manzildan juda ko‘p urinish. Ertaga urinib ko‘ring yoki bizga yozing.',
        'e_network': 'Xizmat javob bermadi. Internetni tekshirib, qayta urinib ko‘ring.',
        'cab_title': 'DGhost 3D kabineti', 'cab_loading': 'Kabinet yuklanmoqda…',
        'cab_noauth_h': 'Kabinet havolasi kerak', 'cab_noauth': 'Kabinet ro‘yxatdan o‘tishda olgan shaxsiy havolangiz orqali ochiladi. Havola yo‘qmi — ro‘yxatdan o‘ting yoki bizga yozing.',
        'cab_signup': 'Ro‘yxatdan o‘tish', 'cab_contact': 'Telegram’da yozish',
        'cab_save_h': 'Kabinet havolasini saqlang', 'cab_save': 'Bu sizning kirishingiz — pochta va parol yo‘q. Sahifani xatcho‘pga qo‘shing yoki havolani ishonchli joyga nusxalang.',
        'cab_copy_link': 'Havolani nusxalash', 'copied': 'Nusxalandi', 'cab_new_link': 'Yangi havola berish',
        'cab_new_confirm': 'Eski havola ishlamay qoladi. Davom etasizmi?',
        'cab_key': 'Kalit', 'cab_plan': 'Tarif', 'cab_until': '{d} gacha', 'cab_expired': 'Muddat tugadi — vidjet saytda ko‘rinmaydi. Quyida tarifni tanlang.',
        'cab_sub_on': 'Obuna o‘zi uzaytiriladi.', 'cab_sub_cancel': 'Obuna bekor qilingan — kalit to‘langan muddat oxirigacha ishlaydi.',
        'cab_views': 'Shu oydagi ko‘rsatuvlar', 'cab_nolimit': 'cheklovsiz',
        'cab_domains': 'Vidjet ishlaydigan saytlar', 'cab_domains_max': '{n} tagacha', 'cab_save_btn': 'Saqlash', 'cab_saved': 'Saqlandi',
        'cab_code': 'Tovar sahifasi uchun kod', 'cab_copy': 'Kodni nusxalash',
        'cab_usage': 'Oylar bo‘yicha ko‘rsatuvlar', 'cab_month': 'Oy', 'cab_shown': 'Ko‘rsatildi', 'cab_denied': 'Rad etildi',
        'cab_plans': 'Tariflar', 'per_month': '/ oy', 'per_year': '/ yil', 'm_month': 'Oylik', 'm_year': 'Yillik −20%',
        'cab_current': 'Sizning tarifingiz', 'cab_choose': 'Tanlash', 'cab_contact_plan': 'Bizga yozing',
        'cab_views_n': '{n} ko‘rsatuv', 'cab_domains_n': 'saytlar: {n}', 'cab_ar': 'AR «Stolda»', 'cab_nobadge': 'belgisiz',
        'cab_pay_soon_h': 'Karta orqali to‘lov ulanmoqda', 'cab_pay_soon': 'Hozircha to‘lov biz orqali: Telegram yoki pochtaga yozing, tarif va kalitni ko‘rsating — hisob yuboramiz. To‘lovdan so‘ng kalit darhol uzaytiriladi.',
        'cab_paid': 'To‘lov o‘tdi — tarif yangilanmoqda…', 'e_bad_domains': 'Sayt manzillarini tekshiring.',
        'e_too_many_domains': 'Tarifingizda — {n} tagacha sayt.', 'e_unauthorized': 'Havola eskirgan. Kabinetning yangi havolasini oching.',
    },
    'en': {
        'start_h': 'Start for free', 'start_sub': '14 days and 1,000 views — no payment, no card. Your key right away, bound to your website.',
        'f_email': 'Work email', 'f_site': 'Website', 'f_name': 'Project name (optional)',
        'ph_site': 'shop.com', 'start_btn': 'Get my key', 'start_wait': 'Creating your key…',
        'start_note': 'By clicking the button you accept the terms of service. We use your email only about your key and billing.',
        'plan_try': 'Start for free', 'plan_sub': 'Subscribe', 'plan_contact': 'Talk to us',
        'e_bad_email': 'Please check your email address.', 'e_bad_website': 'Enter your website, e.g. shop.com.',
        'e_email_taken': 'This email already has a dashboard. Open it with your link or message us — we will send a new one.',
        'e_domain_taken': 'This website is already connected. If it is yours, message us.',
        'e_too_many_signups': 'Too many attempts from this address. Try tomorrow or message us.',
        'e_network': 'The service did not respond. Check your connection and try again.',
        'cab_title': 'DGhost 3D dashboard', 'cab_loading': 'Loading your dashboard…',
        'cab_noauth_h': 'You need your dashboard link', 'cab_noauth': 'The dashboard opens with the personal link you got when you signed up. No link? Sign up or message us.',
        'cab_signup': 'Sign up', 'cab_contact': 'Message us on Telegram',
        'cab_save_h': 'Save your dashboard link', 'cab_save': 'This link is your login — there is no email or password. Bookmark this page or keep the link somewhere safe.',
        'cab_copy_link': 'Copy link', 'copied': 'Copied', 'cab_new_link': 'Issue a new link',
        'cab_new_confirm': 'Your old link will stop working. Continue?',
        'cab_key': 'Key', 'cab_plan': 'Plan', 'cab_until': 'until {d}', 'cab_expired': 'Your plan has ended — the widget is not shown on your site. Pick a plan below.',
        'cab_sub_on': 'Your subscription renews automatically.', 'cab_sub_cancel': 'Subscription cancelled — the key works until the end of the paid period.',
        'cab_views': 'Views this month', 'cab_nolimit': 'unlimited',
        'cab_domains': 'Websites where the widget works', 'cab_domains_max': 'up to {n}', 'cab_save_btn': 'Save', 'cab_saved': 'Saved',
        'cab_code': 'Code for your product page', 'cab_copy': 'Copy code',
        'cab_usage': 'Views by month', 'cab_month': 'Month', 'cab_shown': 'Shown', 'cab_denied': 'Denied',
        'cab_plans': 'Plans', 'per_month': '/ mo', 'per_year': '/ yr', 'm_month': 'Monthly', 'm_year': 'Yearly −20%',
        'cab_current': 'Your plan', 'cab_choose': 'Choose', 'cab_contact_plan': 'Contact us',
        'cab_views_n': '{n} views', 'cab_domains_n': 'websites: {n}', 'cab_ar': 'AR on the table', 'cab_nobadge': 'no badge',
        'cab_pay_soon_h': 'Card payments are being connected', 'cab_pay_soon': 'For now, pay through us: message us on Telegram or by email with your plan and key, and we will send an invoice. Your key is extended right after payment.',
        'cab_paid': 'Payment received — updating your plan…', 'e_bad_domains': 'Please check the website addresses.',
        'e_too_many_domains': 'Your plan allows {n} website(s) at most.', 'e_unauthorized': 'This link is no longer valid. Open your new dashboard link.',
    },
}

HOW = {
    'ru': ['Заполните короткую форму: почта и адрес сайта.', 'Сразу получите пробный ключ на 14 дней и ссылку в кабинет.', 'Вставьте код виджета на страницу товара — обычно это занимает несколько минут.', 'Понравилось — выберите тариф в кабинете.'],
    'uz': ['Qisqa shaklni to‘ldiring: pochta va sayt manzili.', 'Darhol 14 kunlik sinov kaliti va kabinet havolasini olasiz.', 'Vidjet kodini tovar sahifasiga qo‘ying — odatda bir necha daqiqa.', 'Yoqdimi — kabinetda tarifni tanlang.'],
    'en': ['Fill in a short form: your email and website.', 'Get a 14-day trial key and your dashboard link right away.', 'Paste the widget code into your product page — usually a few minutes.', 'Happy with it? Pick a plan in your dashboard.'],
}

CSS = """
.r3d .plan .pbtn{margin-top:auto;padding-top:16px}
.r3d .plan .pbtn .btn{width:100%;justify-content:center;box-sizing:border-box}
.r3d #start{scroll-margin-top:90px}
.r3d .start{display:grid;grid-template-columns:1.1fr 1fr;gap:28px;align-items:start;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:28px;max-width:980px}
.r3d .start h2{margin:0 0 8px}
.r3d .start .sub{margin:0 0 4px}
.r3d .start form{display:grid;gap:12px}
.r3d .start label{display:grid;gap:6px;font-size:14px;color:var(--muted)}
.r3d .start input{font:inherit;font-size:16px;color:var(--text);background:#0c0816;border:1px solid var(--line);border-radius:12px;padding:12px 14px;outline:0}
.r3d .start input:focus{border-color:var(--violet)}
.r3d .start button{border:0;cursor:pointer;font:inherit;font-weight:700}
.r3d .start button[disabled]{opacity:.6;cursor:default}
.r3d .start .fine{font-size:12px;color:var(--muted);line-height:1.5}
.r3d .msg{min-height:20px;font-size:14px;color:#ff8aa6}
.r3d .msg a{color:inherit}
.cab .wrap{max-width:1080px}
.cab h1{font-size:34px;margin:36px 0 4px}
.cab .who{color:var(--muted);margin:0 0 22px}
.cab .grid{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;align-items:start}
.cab .box{background:var(--surface);border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:20px}
.cab .box h3{margin:0 0 12px;font-size:16px}
.cab .save{border-color:var(--violet);background:linear-gradient(140deg,rgba(123,44,255,.22),rgba(196,22,159,.1));margin-bottom:16px}
.cab .save p{margin:0 0 12px;color:#dccff3;line-height:1.5}
.cab .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.cab .kv{display:grid;grid-template-columns:auto 1fr;gap:8px 16px;margin:0}
.cab .kv dt{color:var(--muted)}
.cab .kv dd{margin:0;font-weight:600;word-break:break-all}
.cab .mono{font-family:'JetBrains Mono',ui-monospace,monospace;font-variant-numeric:tabular-nums}
.cab .bar{height:8px;border-radius:8px;background:rgba(255,255,255,.08);overflow:hidden;margin:10px 0 4px}
.cab .bar i{display:block;height:100%;background:var(--grad);border-radius:8px}
.cab input.dom{width:100%;box-sizing:border-box;font:inherit;color:var(--text);background:#0c0816;border:1px solid var(--line);border-radius:12px;padding:11px 13px;margin:0 0 10px}
.cab pre{background:#0c0816;border:1px solid var(--line);border-radius:12px;padding:12px 14px;white-space:pre-wrap;word-break:break-all;font-size:12px;line-height:1.5;color:#d8c8ff;margin:0 0 10px}
.cab table{width:100%;border-collapse:collapse;font-size:14px}
.cab th,.cab td{text-align:left;padding:8px 6px;border-bottom:1px solid rgba(255,255,255,.06)}
.cab th{color:var(--muted);font-weight:500}
.cab .warn{color:#ffc46b;margin:10px 0 0;line-height:1.5}
.cab .ok{color:#3ddc97}
.cab .seg{display:inline-flex;border:1px solid var(--line);border-radius:999px;overflow:hidden;margin:0 0 14px}
.cab .seg button{font:inherit;font-size:14px;color:var(--muted);background:none;border:0;padding:8px 16px;cursor:pointer}
.cab .seg button.on{background:var(--grad);color:#fff}
.cab .plans{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.cab .pl{display:flex;flex-direction:column;gap:6px;background:var(--surface);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px}
.cab .pl.cur{border-color:var(--violet)}
.cab .pl b{font-size:17px}
.cab .pl .pr{font-size:24px;font-weight:800}
.cab .pl .pr small{font-size:13px;font-weight:500;color:var(--muted)}
.cab .pl ul{list-style:none;padding:0;margin:4px 0 10px;color:var(--muted);font-size:14px;display:grid;gap:4px}
.cab .pl .btn{margin-top:auto;justify-content:center}
.cab .note{margin:14px 0 0;background:var(--surface);border:1px solid rgba(255,196,107,.35);border-radius:14px;padding:14px 16px}
.cab .note b{display:block;margin-bottom:6px}
.cab .note p{margin:0 0 10px;color:var(--muted);line-height:1.5}
.cab .center{min-height:40vh;display:grid;place-content:center;text-align:center;gap:12px}
.cab .center p{color:var(--muted);max-width:520px}
.cab .btn{border:0;cursor:pointer;font:inherit;font-weight:700}
.cab .btn.ghost{border:1px solid var(--line)}
@media(max-width:900px){.r3d .start,.cab .grid{grid-template-columns:1fr}.cab .plans{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.cab .plans{grid-template-columns:1fr}.cab h1{font-size:28px}}
"""


def plan_button(key, lang):
    t = TX[lang]
    if key == 'trial':
        return f'<div class="pbtn"><a class="btn ghost" href="#start">{esc(t["plan_try"])}</a></div>'
    if key == 'enterprise':
        return f'<div class="pbtn"><a class="btn ghost" href="https://t.me/dghostmarket?direct">{esc(t["plan_contact"])}</a></div>'
    return (f'<div class="pbtn"><a class="btn primary" href="#start" data-plan="{esc(key)}">'
            f'{esc(t["plan_sub"])}</a></div>')


def start_block(lang):
    t = TX[lang]
    return (f'<div class="block" id="start"><div class="start"><div><h2>{esc(t["start_h"])}</h2>'
            f'<p class="sub">{esc(t["start_sub"])}</p></div>'
            f'<form id="r3dStart" novalidate>'
            f'<label>{esc(t["f_email"])}<input name="email" type="email" autocomplete="email" required></label>'
            f'<label>{esc(t["f_site"])}<input name="website" type="text" inputmode="url" autocapitalize="off" placeholder="{esc(t["ph_site"])}" required></label>'
            f'<label>{esc(t["f_name"])}<input name="name" type="text" autocomplete="organization"></label>'
            f'<input type="hidden" name="plan" value="">'
            f'<button class="btn primary" type="submit">{esc(t["start_btn"])}</button>'
            f'<div class="msg" id="r3dStartMsg" role="alert"></div>'
            f'<div class="fine">{esc(t["start_note"])}</div></form></div></div>')


def _strings(lang, keys):
    return {k: TX[lang][k] for k in keys}


START_KEYS = ['start_btn', 'start_wait', 'e_bad_email', 'e_bad_website', 'e_email_taken', 'e_domain_taken',
              'e_too_many_signups', 'e_network']


def start_script(lang):
    cfg = {'api': API, 'lang': lang, 'cabinet': cabinet_url(lang), 't': _strings(lang, START_KEYS)}
    return ('<script>(function(){var C=' + json.dumps(cfg, ensure_ascii=False).replace('</', '<\\/') + ';'
            r"""
var f=document.getElementById('r3dStart');if(!f)return;var msg=document.getElementById('r3dStartMsg');var btn=f.querySelector('button');
var saved=null;try{saved=localStorage.getItem('dg3d_cab');}catch(e){}
document.querySelectorAll('[data-plan]').forEach(function(a){a.addEventListener('click',function(e){
if(saved){e.preventDefault();location.href=C.cabinet+'?plan='+a.dataset.plan+'#t='+saved;return;}
f.elements.plan.value=a.dataset.plan;});});
f.addEventListener('submit',function(e){e.preventDefault();msg.textContent='';btn.disabled=true;btn.textContent=C.t.start_wait;
fetch(C.api+'/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.elements.email.value,website:f.elements.website.value,name:f.elements.name.value,lang:C.lang})})
.then(function(r){return r.json().catch(function(){return{error:'network'};});})
.then(function(d){if(!d.token){throw d;}try{localStorage.setItem('dg3d_cab',d.token);localStorage.setItem('dg3d_new','1');}catch(x){}
location.href=C.cabinet+(f.elements.plan.value?'?plan='+f.elements.plan.value:'')+'#t='+d.token;})
.catch(function(d){btn.disabled=false;btn.textContent=C.t.start_btn;msg.textContent=C.t['e_'+((d&&d.error)||'network')]||C.t.e_network;});});
})();</script>""")


CAB_KEYS = [k for k in TX['ru'] if k.startswith(('cab_', 'e_', 'per_', 'm_')) or k in ('copied',)]


def cabinet_main(lang, start_url):
    t = TX[lang]
    cfg = {'api': API, 'lang': lang, 'start': start_url, 'tg': 'https://t.me/dghostmarket?direct',
           'mail': 'support@dghostmarket.uz', 't': _strings(lang, CAB_KEYS)}
    return (f'<main id="top" class="r3d cab"><div class="wrap"><div id="cab" class="center"><p>{esc(t["cab_loading"])}</p></div></div></main>'
            '<script>(function(){var C=' + json.dumps(cfg, ensure_ascii=False).replace('</', '<\\/') + ';' + CAB_JS + '})();</script>')


CAB_JS = r"""
var T=C.t,root=document.getElementById('cab');
function e(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function n(v){return Number(v||0).toLocaleString(C.lang==='en'?'en-US':'ru-RU');}
var token=null,m=location.hash.match(/t=([A-Za-z0-9_-]{20,})/);
if(m){token=m[1];try{localStorage.setItem('dg3d_cab',token);}catch(x){}history.replaceState(null,'',location.pathname+location.search);}
if(!token){try{token=localStorage.getItem('dg3d_cab');}catch(x){}}
var wantPlan=(location.search.match(/plan=(\w+)/)||[])[1]||'';
var period='month',data=null,status={};
function api(path,body){return fetch(C.api+path,{method:body?'POST':'GET',headers:Object.assign({'Authorization':'Bearer '+token},body?{'Content-Type':'application/json'}:{}),body:body?JSON.stringify(body):undefined})
.then(function(r){return r.json().catch(function(){return{error:'network'};}).then(function(d){d._s=r.status;return d;});});}
function noauth(){root.className='center';root.innerHTML='<h1>'+e(T.cab_noauth_h)+'</h1><p>'+e(T.cab_noauth)+'</p><div class="row" style="justify-content:center"><a class="btn primary" href="'+e(C.start)+'">'+e(T.cab_signup)+'</a><a class="btn ghost" href="'+e(C.tg)+'">'+e(T.cab_contact)+'</a></div>';}
function link(){return location.origin+location.pathname+'#t='+token;}
function copy(text,btn){var done=function(){var o=btn.textContent;btn.textContent=T.copied;setTimeout(function(){btn.textContent=o;},1500);};
if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(text).then(done,done);else done();}
function render(){var k=data.key,c=data.client;root.className='';
var isNew=false;try{isNew=localStorage.getItem('dg3d_new')==='1';}catch(x){}
var h='<h1>'+e(T.cab_title)+'</h1><p class="who">'+e(c.name)+' · '+e(c.email)+'</p>';
h+='<div class="box save"'+(isNew?'':' style="border-color:rgba(255,255,255,.07);background:var(--surface)"')+'><h3>'+e(T.cab_save_h)+'</h3><p>'+e(T.cab_save)+'</p><div class="row"><button class="btn primary small" data-a="copylink">'+e(T.cab_copy_link)+'</button><button class="btn ghost small" data-a="newlink">'+e(T.cab_new_link)+'</button></div></div>';
if(k){var lim=k.limit,pct=lim?Math.min(100,Math.round(k.views/lim*100)):0;
var until=k.expires_at?T.cab_until.replace('{d}',new Date(k.expires_at).toLocaleDateString(C.lang==='en'?'en-GB':'ru-RU')):'';
h+='<div class="grid"><div class="box"><dl class="kv"><dt>'+e(T.cab_plan)+'</dt><dd>'+e(k.plan_name)+(until?' · '+e(until):'')+'</dd><dt>'+e(T.cab_key)+'</dt><dd class="mono">'+e(k.key)+'</dd></dl>';
if(k.expired)h+='<p class="warn">'+e(T.cab_expired)+'</p>';else if(k.cancel_at_end)h+='<p class="warn">'+e(T.cab_sub_cancel)+'</p>';else if(k.subscription)h+='<p class="ok" style="margin:10px 0 0">'+e(T.cab_sub_on)+'</p>';
h+='<h3 style="margin-top:18px">'+e(T.cab_views)+'</h3><div class="mono">'+n(k.views)+' / '+(lim?n(lim):e(T.cab_nolimit))+'</div>'+(lim?'<div class="bar"><i style="width:'+pct+'%"></i></div>':'');
h+='<h3 style="margin-top:18px">'+e(T.cab_domains)+(k.max_domains?' · '+e(T.cab_domains_max.replace('{n}',k.max_domains)):'')+'</h3><input class="dom" id="cabDom" value="'+e((k.domains||[]).join(', '))+'" autocapitalize="off" inputmode="url"><div class="row"><button class="btn ghost small" data-a="domains">'+e(T.cab_save_btn)+'</button><span class="msg" id="cabDomMsg"></span></div></div>';
h+='<div class="box"><h3>'+e(T.cab_code)+'</h3><pre id="cabCode">'+e(k.code)+'</pre><button class="btn ghost small" data-a="copycode">'+e(T.cab_copy)+'</button>';
if((k.usage||[]).length){h+='<h3 style="margin-top:18px">'+e(T.cab_usage)+'</h3><table><tr><th>'+e(T.cab_month)+'</th><th>'+e(T.cab_shown)+'</th><th>'+e(T.cab_denied)+'</th></tr>'+k.usage.map(function(u){return'<tr><td class="mono">'+e(u.month)+'</td><td class="mono">'+n(u.views)+'</td><td class="mono">'+n(u.denied)+'</td></tr>';}).join('')+'</table>';}
h+='</div></div>';}
h+='<div class="block"><h2>'+e(T.cab_plans)+'</h2><div class="seg"><button data-p="month" class="'+(period==='month'?'on':'')+'">'+e(T.m_month)+'</button><button data-p="year" class="'+(period==='year'?'on':'')+'">'+e(T.m_year)+'</button></div><div class="plans">';
data.plans.forEach(function(p){var cur=k&&k.plan===p.key&&!k.expired;var price=p.usd_month==null?'':(period==='year'?'$'+p.usd_year+' <small>'+e(T.per_year)+'</small>':'$'+p.usd_month+' <small>'+e(T.per_month)+'</small>');
h+='<div class="pl'+(cur?' cur':'')+'"><b>'+e(p.name)+'</b><div class="pr">'+price+'</div><ul><li>'+e(T.cab_views_n.replace('{n}',p.views?n(p.views):T.cab_nolimit))+'</li><li>'+e(T.cab_domains_n.replace('{n}',p.domains||T.cab_nolimit))+'</li>'+(p.ar?'<li>'+e(T.cab_ar)+'</li>':'')+(!p.badge?'<li>'+e(T.cab_nobadge)+'</li>':'')+'</ul>'
+(p.usd_month==null?'<a class="btn ghost" href="'+e(C.tg)+'">'+e(T.cab_contact_plan)+'</a>':cur?'<span class="btn ghost" aria-disabled="true">'+e(T.cab_current)+'</span>':'<button class="btn primary" data-buy="'+e(p.key)+'">'+e(T.cab_choose)+'</button>')+'</div>';});
h+='</div><div id="cabPay"></div></div>';
root.innerHTML=h;}
function paySoon(){document.getElementById('cabPay').innerHTML='<div class="note"><b>'+e(T.cab_pay_soon_h)+'</b><p>'+e(T.cab_pay_soon)+'</p><div class="row"><a class="btn primary small" href="'+e(C.tg)+'">'+e(T.cab_contact)+'</a><a class="btn ghost small" href="mailto:'+e(C.mail)+'">'+e(C.mail)+'</a></div></div>';
document.getElementById('cabPay').scrollIntoView({behavior:'smooth',block:'center'});}
function paddle(cfg){var go=function(){try{if(cfg.environment==='sandbox')Paddle.Environment.set('sandbox');Paddle.Initialize({token:cfg.client_token,eventCallback:function(ev){if(ev&&ev.name==='checkout.completed'){document.getElementById('cabPay').innerHTML='<div class="note"><b>'+e(T.cab_paid)+'</b></div>';setTimeout(load,4000);setTimeout(load,12000);}}});
Paddle.Checkout.open({items:[{priceId:cfg.price_id,quantity:1}],customData:cfg.custom_data,customer:cfg.email?{email:cfg.email}:undefined});}catch(x){paySoon();}};
if(window.Paddle)return go();var s=document.createElement('script');s.src='https://cdn.paddle.com/paddle/v2/paddle.js';s.onload=go;s.onerror=paySoon;document.head.appendChild(s);}
function buy(plan){api('/api/cabinet/checkout',{plan:plan,period:period}).then(function(d){if(d.provider==='paddle')paddle(d);else if(d._s===401)noauth();else paySoon();},paySoon);}
root.addEventListener('click',function(ev){var b=ev.target.closest('[data-a],[data-p],[data-buy]');if(!b)return;
if(b.dataset.p){period=b.dataset.p;render();return;}
if(b.dataset.buy){buy(b.dataset.buy);return;}
var a=b.dataset.a;
if(a==='copylink'){copy(link(),b);try{localStorage.removeItem('dg3d_new');}catch(x){}}
else if(a==='copycode'){copy(data.key.code,b);}
else if(a==='newlink'){if(!confirm(T.cab_new_confirm))return;api('/api/cabinet/token',{}).then(function(d){if(d.token){token=d.token;try{localStorage.setItem('dg3d_cab',token);localStorage.setItem('dg3d_new','1');}catch(x){}render();}});}
else if(a==='domains'){var mm=document.getElementById('cabDomMsg');mm.textContent='';api('/api/cabinet/domains',{domains:document.getElementById('cabDom').value}).then(function(d){
if(d.key){data=d;render();var m2=document.getElementById('cabDomMsg');if(m2){m2.className='msg ok';m2.textContent=T.cab_saved;}}
else{mm.textContent=(T['e_'+d.error]||T.e_network).replace('{n}',d.max||'');}});}});
function load(){api('/api/cabinet').then(function(d){if(d._s===401){try{localStorage.removeItem('dg3d_cab');}catch(x){}noauth();return;}
if(!d.client){root.className='center';root.innerHTML='<p>'+e(T.e_network)+'</p>';return;}
data=d;render();if(wantPlan){var w=wantPlan;wantPlan='';var el=document.querySelector('[data-buy="'+w+'"]');if(el){el.scrollIntoView({block:'center'});buy(w);}}},
function(){root.className='center';root.innerHTML='<p>'+e(T.e_network)+'</p>';});}
if(!token)noauth();else load();
"""
