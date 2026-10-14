"""Статьи-инструкции: /guides/<статья>/ (ru) и /uz/guides/<статья>/ + каталог /guides/.

Вызывается из tools/build.py. Тексты — здесь же, в GUIDES: HTML-разметка тела
(h2, p, ol, ul, a). Внутренние ссылки пишем от корня русской версии
("/prices/", "/guides/trade-link/") — для узбекской сборщик добавляет /uz.
Английской версии нет: статьи для покупателей из Узбекистана.
"""
import html
import re

LANGS = ['ru', 'uz']

T = {
    'ru': {
        'hub': 'Инструкции', 'home': 'Главная',
        'hub_title': 'Инструкции: как купить и продать скины CS2 в Узбекистане | DGhostMarket',
        'hub_h1': 'Инструкции по скинам CS2',
        'hub_desc': 'Как купить и продать скины CS2 за сумы, где взять trade-ссылку Steam, что такое float и как не попасть на мошенников — простые инструкции DGhostMarket.',
        'hub_lead': 'Простые ответы на частые вопросы: как купить и продать скины CS2 за сумы и не потерять ни предмет, ни деньги.',
        'cta': 'Открыть DGhostMarket', 'prices': 'Цены на скины в сумах',
        'more': 'Ещё инструкции', 'updated': 'Обновлено',
    },
    'uz': {
        'hub': 'Qo‘llanmalar', 'home': 'Bosh sahifa',
        'hub_title': 'Qo‘llanmalar: O‘zbekistonda CS2 skinlarini sotib olish va sotish | DGhostMarket',
        'hub_h1': 'CS2 skinlari bo‘yicha qo‘llanmalar',
        'hub_desc': 'CS2 skinlarini so‘mga qanday sotib olish va sotish, Steam trade havolasini qayerdan olish, float nima va firibgarlarga qanday aldanmaslik — DGhostMarket’ning oddiy qo‘llanmalari.',
        'hub_lead': 'Ko‘p beriladigan savollarga oddiy javoblar: CS2 skinlarini so‘mga qanday sotib olish va sotish, buyumni ham, pulni ham yo‘qotmaslik.',
        'cta': 'DGhostMarket’ni ochish', 'prices': 'Skinlar narxi so‘mda',
        'more': 'Boshqa qo‘llanmalar', 'updated': 'Yangilangan',
    },
}

CSS = """
.article{max-width:760px}
.article h2{font-size:22px;margin:34px 0 12px}
.article p,.article li{font-size:17px;line-height:1.65;color:var(--text)}
.article p{margin:0 0 14px}
.article ol,.article ul{padding-left:22px;margin:0 0 16px}
.article li{margin:6px 0}
.article .tip{background:var(--surface);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:14px 16px;margin:18px 0}
.article code{overflow-wrap:anywhere;word-break:break-all;background:rgba(255,255,255,0.06);padding:1px 5px;border-radius:6px;font-size:15px}
.article .actions{display:flex;flex-wrap:wrap;gap:10px;margin:28px 0}
.guide-list{display:grid;gap:12px;max-width:760px;margin:20px 0}
.guide-list a{display:block;background:var(--surface);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:16px 18px;text-decoration:none}
.guide-list b{display:block;font-size:17px;margin-bottom:4px}
.guide-list span{color:var(--muted);font-size:14px}
"""

UPDATED = '2026-10-14'

GUIDES = [
    {
        'slug': 'buy-cs2-skins-uzbekistan',
        'ru': {
            'title': 'Как купить скин CS2 в Узбекистане за сумы — пошагово',
            'h1': 'Как купить скин CS2 в Узбекистане за сумы',
            'desc': 'Пошаговая инструкция: как купить скин CS2 за сумы через Telegram, без карты Steam и с защитой сделки. Сроки, комиссии и что делать, если предмет не пришёл.',
            'body': '''
<p>Купить скин в Steam напрямую из Узбекистана неудобно: нужен баланс Steam, а цены там в долларах. На DGhostMarket скины продают сами игроки, цены — в сумах, а деньги до получения предмета держит площадка.</p>
<h2>Что понадобится</h2>
<ul>
<li>Аккаунт Telegram — через него вы входите, регистрация не нужна.</li>
<li>Аккаунт Steam с CS2 и <a href="/guides/trade-link/">trade-ссылка</a> — по ней продавец отправит предмет.</li>
<li>Мобильный аутентификатор Steam Guard — без него Steam задерживает обмены (подробнее в <a href="/guides/trade-link/">инструкции про trade-ссылку</a>).</li>
</ul>
<h2>Покупка за 5 шагов</h2>
<ol>
<li><b>Откройте маркет.</b> В Telegram — бот @dghostmarketbot, в браузере — app.dghostmarket.com (вход через Telegram).</li>
<li><b>Привяжите trade-ссылку</b> в профиле. Покупателю проверка документов не нужна.</li>
<li><b>Выберите скин.</b> Фильтры по оружию, износу, float и цене. На карточке видно, насколько цена ниже или выше рынка. Ориентир — <a href="/prices/">цены на скины в сумах</a>.</li>
<li><b>Оплатите.</b> Пополните баланс способом из приложения и нажмите «Купить». Деньги удерживает площадка — продавец их пока не получает.</li>
<li><b>Примите обмен в Steam.</b> Продавец отправляет его в течение 24 часов. Проверьте, что в обмене именно тот предмет, примите его и нажмите «Получил» в приложении.</li>
</ol>
<div class="tip">Не отправил продавец за 24 часа — заказ отменяется сам, деньги возвращаются на баланс. Пришло не то — откройте спор, выплата продавцу замораживается до решения администрации.</div>
<h2>Сколько это стоит</h2>
<p>Покупатель платит ровно цену с карточки лота — комиссии площадки для покупателя нет. Если выбранный способ пополнения берёт свой сбор, итог показывается до оплаты.</p>
<h2>Почему это безопасно</h2>
<ul>
<li>Продавцы проходят проверку: документ, селфи и номер телефона через Telegram.</li>
<li>Деньги уходят продавцу только через 8 дней — дольше, чем Steam позволяет отменить обмен.</li>
<li>Вся сделка идёт внутри приложения, каждый шаг сохраняется в истории.</li>
</ul>
<p>Никогда не платите продавцу напрямую «в обход» площадки — тогда защиты нет. Больше советов — в статье <a href="/guides/avoid-scams/">как не попасть на мошенников</a>.</p>
''',
        },
        'uz': {
            'title': 'O‘zbekistonda CS2 skinini so‘mga qanday sotib olish — bosqichma-bosqich',
            'h1': 'O‘zbekistonda CS2 skinini so‘mga qanday sotib olish',
            'desc': 'Bosqichma-bosqich qo‘llanma: CS2 skinini Telegram orqali so‘mga, Steam kartasisiz va bitim himoyasi bilan qanday sotib olish. Muddatlar, komissiyalar va buyum kelmasa nima qilish kerak.',
            'body': '''
<p>O‘zbekistondan Steam’da to‘g‘ridan-to‘g‘ri skin sotib olish noqulay: Steam balansi kerak, narxlar esa dollarda. DGhostMarket’da skinlarni o‘yinchilarning o‘zlari sotadi, narxlar so‘mda, buyum kelmaguncha pulni esa platforma ushlab turadi.</p>
<h2>Nima kerak bo‘ladi</h2>
<ul>
<li>Telegram akkaunti — u orqali kirasiz, ro‘yxatdan o‘tish shart emas.</li>
<li>CS2 bor Steam akkaunti va <a href="/guides/trade-link/">trade havola</a> — sotuvchi buyumni shu havola orqali yuboradi.</li>
<li>Steam Guard mobil autentifikatori — usiz Steam almashuvlarni kechiktiradi (batafsil <a href="/guides/trade-link/">trade havola haqidagi qo‘llanmada</a>).</li>
</ul>
<h2>5 qadamda xarid</h2>
<ol>
<li><b>Marketni oching.</b> Telegram’da — @dghostmarketbot boti, brauzerda — app.dghostmarket.com (Telegram orqali kirish).</li>
<li><b>Profilda trade havolani ulang.</b> Xaridor hujjat tekshiruvidan o‘tmaydi.</li>
<li><b>Skinni tanlang.</b> Qurol, holat, float va narx bo‘yicha filtrlar bor. Kartochkada narx bozordan qancha arzon yoki qimmatligi ko‘rinadi. Mo‘ljal uchun — <a href="/prices/">skinlarning so‘mdagi narxlari</a>.</li>
<li><b>To‘lang.</b> Balansni ilovadagi usul bilan to‘ldiring va «Sotib olish»ni bosing. Pulni platforma ushlab turadi — sotuvchi uni hali olmaydi.</li>
<li><b>Steam’da almashuvni qabul qiling.</b> Sotuvchi uni 24 soat ichida yuboradi. Almashuvda aynan o‘sha buyum ekanini tekshiring, qabul qiling va ilovada «Oldim»ni bosing.</li>
</ol>
<div class="tip">Sotuvchi 24 soat ichida yubormasa — buyurtma o‘zi bekor bo‘ladi, pul balansga qaytadi. Boshqa buyum kelsa — nizo oching, ma’muriyat qaror qilguncha sotuvchiga to‘lov muzlatiladi.</div>
<h2>Bu qancha turadi</h2>
<p>Xaridor lot kartochkasidagi narxni to‘laydi — xaridor uchun platforma komissiyasi yo‘q. Tanlangan to‘ldirish usuli o‘z yig‘imini olsa, yakuniy summa to‘lovdan oldin ko‘rsatiladi.</p>
<h2>Nega bu xavfsiz</h2>
<ul>
<li>Sotuvchilar tekshiruvdan o‘tadi: hujjat, selfi va Telegram orqali telefon raqami.</li>
<li>Pul sotuvchiga faqat 8 kundan keyin o‘tadi — bu Steam almashuvni bekor qilishga ruxsat beradigan muddatdan uzoqroq.</li>
<li>Butun bitim ilova ichida o‘tadi, har bir qadam tarixda saqlanadi.</li>
</ul>
<p>Hech qachon sotuvchiga platformani «chetlab» to‘g‘ridan-to‘g‘ri pul to‘lamang — unda himoya bo‘lmaydi. Ko‘proq maslahatlar — <a href="/guides/avoid-scams/">firibgarlarga qanday aldanmaslik</a> maqolasida.</p>
''',
        },
    },
    {
        'slug': 'sell-cs2-skins',
        'ru': {
            'title': 'Как продать скины CS2 за сумы — инструкция для продавца',
            'h1': 'Как продать скины CS2 за сумы',
            'desc': 'Как продать скин CS2 за сумы в Узбекистане: проверка продавца, выставление лота из инвентаря Steam, сроки передачи, комиссия 5% и вывод денег на карту.',
            'body': '''
<p>На DGhostMarket вы продаёте скин другому игроку и получаете сумы на баланс, а потом выводите их на карту. Площадка держит оплату покупателя, пока сделка не завершится, поэтому рисковать предметом не нужно.</p>
<h2>1. Пройдите проверку продавца</h2>
<p>Один раз перед первым лотом: номер телефона через Telegram, фото документа и селфи. Решение принимает администратор. Это защищает покупателей — и поэтому они охотнее покупают у проверенных продавцов.</p>
<h2>2. Выставьте предмет</h2>
<p>Откройте «Продать» и выберите скин прямо из инвентаря Steam — фото, float и наклейки подтянутся сами. Инвентарь в Steam должен быть открыт.</p>
<h2>3. Поставьте цену</h2>
<p>Приложение подскажет рыночную цену. Лоты дешевле рынка продаются заметно быстрее, а сильно завышенные висят неделями — бот предложит снизить цену, если лот долго не продаётся. Сверьтесь с <a href="/prices/">ценами на скины в сумах</a>.</p>
<h2>4. Передайте предмет за 24 часа</h2>
<p>Когда скин купят, придёт уведомление. Отправьте обмен в Steam на trade-ссылку покупателя и нажмите «Отправил». Не успели за 24 часа — заказ отменяется, а деньги возвращаются покупателю.</p>
<h2>5. Получите деньги</h2>
<p>Через 8 дней после оплаты сумма за вычетом 5% приходит на баланс. Steam позволяет отменить обмен в течение 7 дней, поэтому выплата идёт чуть позже — так защищены обе стороны. Вывод на банковскую карту — без комиссии площадки, минимум 50 000 сум.</p>
<div class="tip">Пример: скин продан за 1 000 000 сум. Комиссия 5% — 50 000 сум, на баланс придёт 950 000 сум.</div>
<h2>Советы, чтобы продать быстрее</h2>
<ul>
<li>Ставьте цену на уровне рынка или чуть ниже.</li>
<li>Выставляйте все скины сразу — у покупателя больше выбора, у вас больше шансов.</li>
<li>Посмотрите раздел «Хочу»: там видно, какие скины сейчас ищут покупатели.</li>
</ul>
''',
        },
        'uz': {
            'title': 'CS2 skinlarini so‘mga qanday sotish — sotuvchi uchun qo‘llanma',
            'h1': 'CS2 skinlarini so‘mga qanday sotish',
            'desc': 'O‘zbekistonda CS2 skinini so‘mga qanday sotish: sotuvchi tekshiruvi, Steam inventaridan lot qo‘yish, topshirish muddati, 5% komissiya va pulni kartaga yechish.',
            'body': '''
<p>DGhostMarket’da skinni boshqa o‘yinchiga sotasiz va balansga so‘m olasiz, keyin uni kartaga yechasiz. Bitim tugaguncha xaridorning to‘lovini platforma ushlab turadi, shuning uchun buyumni xavf ostiga qo‘yishingiz shart emas.</p>
<h2>1. Sotuvchi tekshiruvidan o‘ting</h2>
<p>Birinchi lotdan oldin bir marta: Telegram orqali telefon raqami, hujjat surati va selfi. Qarorni administrator qabul qiladi. Bu xaridorlarni himoya qiladi — shuning uchun ular tekshirilgan sotuvchilardan bajonidil sotib olishadi.</p>
<h2>2. Buyumni sotuvga qo‘ying</h2>
<p>«Sotish»ni oching va skinni to‘g‘ridan-to‘g‘ri Steam inventaridan tanlang — surat, float va stikerlar o‘zi chiqadi. Steam’dagi inventar ochiq bo‘lishi kerak.</p>
<h2>3. Narx qo‘ying</h2>
<p>Ilova bozor narxini taklif qiladi. Bozordan arzon lotlar ancha tez sotiladi, juda qimmat qo‘yilganlari esa haftalab turib qoladi — lot uzoq sotilmasa, bot narxni tushirishni taklif qiladi. <a href="/prices/">Skinlarning so‘mdagi narxlari</a> bilan solishtiring.</p>
<h2>4. Buyumni 24 soat ichida topshiring</h2>
<p>Skin sotib olinganda xabar keladi. Xaridorning trade havolasiga Steam’da almashuv yuboring va «Yubordim»ni bosing. 24 soatda ulgurmasangiz — buyurtma bekor bo‘ladi, pul xaridorga qaytadi.</p>
<h2>5. Pulni oling</h2>
<p>To‘lovdan 8 kun o‘tgach, summa 5% chegirilgan holda balansga tushadi. Steam almashuvni 7 kun ichida bekor qilishga ruxsat beradi, shuning uchun to‘lov biroz keyinroq bo‘ladi — shunda ikkala tomon ham himoyalangan. Bank kartasiga yechish — platforma komissiyasisiz, kamida 50 000 so‘m.</p>
<div class="tip">Misol: skin 1 000 000 so‘mga sotildi. 5% komissiya — 50 000 so‘m, balansga 950 000 so‘m tushadi.</div>
<h2>Tezroq sotish uchun maslahatlar</h2>
<ul>
<li>Narxni bozor darajasida yoki biroz pastroq qo‘ying.</li>
<li>Barcha skinlarni birdaniga qo‘ying — xaridorda tanlov ko‘p, sizda imkoniyat ko‘p.</li>
<li>«Xohlayman» bo‘limiga qarang: hozir xaridorlar qaysi skinlarni qidirayotgani ko‘rinadi.</li>
</ul>
''',
        },
    },
    {
        'slug': 'trade-link',
        'ru': {
            'title': 'Где найти trade-ссылку Steam и как торговать без задержек',
            'h1': 'Где найти trade-ссылку Steam',
            'desc': 'Где взять ссылку на обмен (trade URL) в Steam с телефона и компьютера, зачем нужен Steam Guard и как избежать задержки обменов на 15 дней.',
            'body': '''
<p>Trade-ссылка (ссылка на обмен) позволяет отправить вам предложение обмена, даже если вы не в друзьях. Она нужна, чтобы продавец мог передать купленный скин.</p>
<h2>С компьютера</h2>
<ol>
<li>Откройте Steam и войдите в аккаунт.</li>
<li>Наведите на свой ник → «Инвентарь».</li>
<li>Нажмите «Предложения обмена» → «Кто может отправлять мне предложения обмена?».</li>
<li>В блоке «Сайты сторонних разработчиков» скопируйте ссылку. Она выглядит так: <code>https://steamcommunity.com/tradeoffer/new/?partner=…&amp;token=…</code></li>
</ol>
<p>Быстрый путь — открыть в браузере <code>steamcommunity.com/my/tradeoffers/privacy</code> после входа в Steam.</p>
<h2>С телефона</h2>
<ol>
<li>В приложении Steam откройте меню → «Инвентарь».</li>
<li>Нажмите «Предложения обмена» (значок с двумя стрелками) → «Кто может отправлять мне предложения обмена?».</li>
<li>Скопируйте ссылку из раздела для сторонних сайтов.</li>
</ol>
<h2>Как сделать, чтобы обмены не задерживались</h2>
<ul>
<li><b>Подключите мобильный аутентификатор Steam Guard</b> в приложении Steam. Без него обмены задерживаются до 15 дней.</li>
<li>После подключения аутентификатора Steam на 7 дней ограничивает обмены — сделайте это заранее.</li>
<li><b>Откройте инвентарь</b>: настройки профиля → «Приватность» → «Инвентарь: открытый». Продавцам это нужно, чтобы выставить лот.</li>
</ul>
<div class="tip">Если нажмёте «Создать новую ссылку», старая перестанет работать — не забудьте обновить её в профиле DGhostMarket.</div>
<h2>Безопасно ли давать trade-ссылку</h2>
<p>Да: по ней можно только отправить вам предложение обмена, а принимать его или нет — решаете вы. Опасно другое — отдавать <b>API-ключ Steam</b>, коды Steam Guard или входить в Steam на странных сайтах. Подробнее — <a href="/guides/avoid-scams/">как не попасть на мошенников</a>.</p>
''',
        },
        'uz': {
            'title': 'Steam trade havolasini qayerdan topish va almashuvlarni kechiktirmaslik',
            'h1': 'Steam trade havolasini qayerdan topish mumkin',
            'desc': 'Steam’da almashuv havolasini (trade URL) telefon va kompyuterdan qanday olish, Steam Guard nima uchun kerak va almashuvlarning 15 kunga kechikishidan qanday qochish.',
            'body': '''
<p>Trade havola (almashuv havolasi) do‘st bo‘lmasangiz ham sizga almashuv taklifini yuborish imkonini beradi. U sotuvchi sotib olingan skinni sizga topshirishi uchun kerak.</p>
<h2>Kompyuterdan</h2>
<ol>
<li>Steam’ni oching va akkauntga kiring.</li>
<li>Nikingiz ustiga olib boring → <b>Inventory</b> (Inventar).</li>
<li><b>Trade Offers</b> → <b>Who can send me Trade Offers?</b> tugmasini bosing.</li>
<li><b>Third-Party Sites</b> blokidan havolani nusxalang. U shunday ko‘rinadi: <code>https://steamcommunity.com/tradeoffer/new/?partner=…&amp;token=…</code></li>
</ol>
<p>Tez yo‘l — Steam’ga kirgach, brauzerda <code>steamcommunity.com/my/tradeoffers/privacy</code> sahifasini ochish.</p>
<h2>Telefondan</h2>
<ol>
<li>Steam ilovasida menyu → <b>Inventory</b>ni oching.</li>
<li><b>Trade Offers</b> (ikki strelkali belgi) → <b>Who can send me Trade Offers?</b> tugmasini bosing.</li>
<li><b>Third-Party Sites</b> bo‘limidagi havolani nusxalang.</li>
</ol>
<h2>Almashuvlar kechikmasligi uchun</h2>
<ul>
<li><b>Steam Guard mobil autentifikatorini ulang</b> (Steam ilovasida). Usiz almashuvlar 15 kungacha kechiktiriladi.</li>
<li>Autentifikator ulangach, Steam 7 kun almashuvlarni cheklaydi — buni oldindan qiling.</li>
<li><b>Inventarni oching</b>: profil sozlamalari → <b>Privacy Settings</b> → <b>Inventory: Public</b>. Sotuvchilarga bu lot qo‘yish uchun kerak.</li>
</ul>
<div class="tip"><b>Create New URL</b> tugmasini bossangiz, eskisi ishlamay qoladi — DGhostMarket profilida uni yangilashni unutmang.</div>
<h2>Trade havolani berish xavfsizmi</h2>
<p>Ha: u orqali faqat sizga almashuv taklifi yuborish mumkin, uni qabul qilish-qilmaslikni siz hal qilasiz. Xavfli narsa boshqa — <b>Steam API kalitini</b>, Steam Guard kodlarini berish yoki shubhali saytlarda Steam’ga kirish. Batafsil — <a href="/guides/avoid-scams/">firibgarlarga qanday aldanmaslik</a>.</p>
''',
        },
    },
    {
        'slug': 'avoid-scams',
        'ru': {
            'title': 'Как не попасть на мошенников при покупке скинов CS2',
            'h1': 'Как не попасть на мошенников при покупке и продаже скинов',
            'desc': 'Частые схемы обмана со скинами CS2: фейковые сайты входа в Steam, кража API-ключа, «случайная жалоба», оплата в обход гаранта. Как распознать и защитить аккаунт.',
            'body': '''
<p>Большинство потерь со скинами происходит не из-за взлома, а из-за доверия: человек сам отдаёт доступ или платит напрямую. Вот схемы, которые встречаются чаще всего.</p>
<h2>1. Оплата «в обход» гаранта</h2>
<p>«Давай напрямую, без комиссии» — самый частый способ остаться без денег. Пока сделка идёт через площадку, деньги удерживаются до получения предмета. Перевели напрямую — вернуть их уже некому.</p>
<h2>2. Фейковая страница входа в Steam</h2>
<p>Ссылка на «розыгрыш», «голосование за команду» или «проверку инвентаря» открывает страницу, похожую на вход в Steam. Введёте логин и код — аккаунт уведут. Входите в Steam только на <b>steamcommunity.com</b> и <b>store.steampowered.com</b> или через приложение Steam.</p>
<h2>3. Кража API-ключа</h2>
<p>Мошенник получает ваш Steam Web API-ключ и подменяет обмены: вы отправляете скин «боту-копии» с таким же ником и аватаркой. Проверьте страницу <code>steamcommunity.com/dev/apikey</code>: если там есть ключ, который вы не создавали, — удалите его и смените пароль.</p>
<h2>4. «Я случайно на тебя пожаловался»</h2>
<p>Пишет «знакомый»: случайно отправил жалобу, теперь вас забанят — свяжитесь с «администратором». Дальше «администратор» просит предметы «на проверку». Поддержка Steam никогда не пишет в Telegram и не просит скины.</p>
<h2>5. Подмена предмета в обмене</h2>
<p>Похожий скин другого износа, без StatTrak™ или без наклеек. Перед тем как принять обмен, проверьте название, износ и float — всё должно совпадать с купленным лотом. Не совпадает — не принимайте и откройте спор.</p>
<h2>6. Фейковые «админы» и поддержка</h2>
<p>Администраторы DGhostMarket не просят коды Steam Guard, пароли, API-ключи и не просят перевести деньги на личную карту. Все вопросы по сделке решаются в приложении, а связаться с поддержкой можно через support@dghostmarket.com.</p>
<div class="tip">Простое правило: никому не давайте пароль, коды Steam Guard и API-ключ, а платите только внутри площадки с удержанием оплаты.</div>
<h2>Как защищает DGhostMarket</h2>
<ul>
<li>Продавцы проходят проверку личности.</li>
<li>Оплата удерживается до получения предмета и ещё 8 дней — дольше, чем Steam позволяет отменить обмен.</li>
<li>Если что-то не так — спор, и выплата продавцу замораживается.</li>
<li>Антифрод ищет связанные аккаунты и подозрительные сделки.</li>
</ul>
<p>Как купить безопасно — в <a href="/guides/buy-cs2-skins-uzbekistan/">пошаговой инструкции</a>.</p>
''',
        },
        'uz': {
            'title': 'CS2 skinlarini sotib olishda firibgarlarga qanday aldanmaslik',
            'h1': 'Skin sotib olish va sotishda firibgarlarga qanday aldanmaslik',
            'desc': 'CS2 skinlari bilan tez-tez uchraydigan aldov sxemalari: Steam’ga kirishning soxta sahifalari, API kalitni o‘g‘irlash, «tasodifiy shikoyat», kafilni chetlab to‘lash. Ularni qanday aniqlash va akkauntni himoya qilish.',
            'body': '''
<p>Skinlar bilan yo‘qotishlarning ko‘pchiligi buzib kirish tufayli emas, ishonch tufayli bo‘ladi: odam o‘zi kirish huquqini beradi yoki to‘g‘ridan-to‘g‘ri pul to‘laydi. Mana eng ko‘p uchraydigan sxemalar.</p>
<h2>1. Kafilni «chetlab» to‘lash</h2>
<p>«Keling, to‘g‘ridan-to‘g‘ri, komissiyasiz» — pulsiz qolishning eng keng tarqalgan yo‘li. Bitim platforma orqali o‘tsa, buyum kelmaguncha pul ushlab turiladi. To‘g‘ridan-to‘g‘ri o‘tkazsangiz — uni qaytaradigan hech kim yo‘q.</p>
<h2>2. Steam’ga kirishning soxta sahifasi</h2>
<p>«O‘yin», «jamoa uchun ovoz berish» yoki «inventarni tekshirish» havolasi Steam’ga kirish sahifasiga o‘xshash sahifani ochadi. Login va kodni kiritsangiz — akkauntni olib qo‘yishadi. Steam’ga faqat <b>steamcommunity.com</b> va <b>store.steampowered.com</b> saytlarida yoki Steam ilovasi orqali kiring.</p>
<h2>3. API kalitni o‘g‘irlash</h2>
<p>Firibgar Steam Web API kalitingizni qo‘lga kiritib, almashuvlarni almashtiradi: siz skinni xuddi shunday nik va avatarli «nusxa-botga» yuborasiz. <code>steamcommunity.com/dev/apikey</code> sahifasini tekshiring: u yerda siz yaratmagan kalit bo‘lsa — o‘chiring va parolni almashtiring.</p>
<h2>4. «Men tasodifan sizga shikoyat qildim»</h2>
<p>«Tanish» yozadi: tasodifan shikoyat yuborgan, endi sizni bloklashadi — «administrator» bilan bog‘laning. Keyin «administrator» buyumlarni «tekshiruvga» so‘raydi. Steam yordam xizmati hech qachon Telegram’da yozmaydi va skin so‘ramaydi.</p>
<h2>5. Almashuvda buyumni almashtirish</h2>
<p>Boshqa holatdagi, StatTrak™siz yoki stikerlarsiz o‘xshash skin. Almashuvni qabul qilishdan oldin nomi, holati va float’ni tekshiring — hammasi sotib olingan lot bilan mos bo‘lishi kerak. Mos kelmasa — qabul qilmang va nizo oching.</p>
<h2>6. Soxta «adminlar» va yordam xizmati</h2>
<p>DGhostMarket administratorlari Steam Guard kodlari, parollar, API kalitlarni so‘ramaydi va shaxsiy kartaga pul o‘tkazishni so‘ramaydi. Bitim bo‘yicha barcha savollar ilovada hal qilinadi, yordam xizmati bilan esa support@dghostmarket.com orqali bog‘lanish mumkin.</p>
<div class="tip">Oddiy qoida: parol, Steam Guard kodlari va API kalitni hech kimga bermang, faqat to‘lov ushlab turiladigan platforma ichida to‘lang.</div>
<h2>DGhostMarket qanday himoya qiladi</h2>
<ul>
<li>Sotuvchilar shaxsini tasdiqlashdan o‘tadi.</li>
<li>To‘lov buyum kelguncha va yana 8 kun ushlab turiladi — bu Steam almashuvni bekor qilishga ruxsat beradigan muddatdan uzoqroq.</li>
<li>Biror narsa noto‘g‘ri bo‘lsa — nizo ochiladi va sotuvchiga to‘lov muzlatiladi.</li>
<li>Antifrod bog‘langan akkauntlar va shubhali bitimlarni qidiradi.</li>
</ul>
<p>Xavfsiz sotib olish — <a href="/guides/buy-cs2-skins-uzbekistan/">bosqichma-bosqich qo‘llanmada</a>.</p>
''',
        },
    },
    {
        'slug': 'float-and-wear',
        'ru': {
            'title': 'Что такое float и износ скина в CS2 — простое объяснение',
            'h1': 'Что такое float и износ скина в CS2',
            'desc': 'Float и износ скинов CS2 простыми словами: диапазоны Factory New — Battle-Scarred, почему цены одного скина отличаются в разы, что такое паттерн и StatTrak™.',
            'body': '''
<p>У одного и того же скина цена может отличаться в несколько раз. Главные причины — износ (float), паттерн, StatTrak™ и наклейки.</p>
<h2>Float — точный износ</h2>
<p>Float — число от 0 до 1: чем меньше, тем «новее» выглядит скин. По float определяется категория износа:</p>
<ul>
<li><b>Прямо с завода (Factory New)</b> — 0,00–0,07</li>
<li><b>Немного поношенное (Minimal Wear)</b> — 0,07–0,15</li>
<li><b>После полевых испытаний (Field-Tested)</b> — 0,15–0,38</li>
<li><b>Поношенное (Well-Worn)</b> — 0,38–0,45</li>
<li><b>Закалённое в боях (Battle-Scarred)</b> — 0,45–1,00</li>
</ul>
<p>Внутри одной категории низкий float тоже ценится: Field-Tested с float 0,15 выглядит почти как Minimal Wear и стоит дороже, чем с 0,37. Не у всех скинов есть все категории — у некоторых float ограничен (например, 0,00–0,08).</p>
<h2>Паттерн</h2>
<p>Паттерн (paint seed) — номер от 0 до 1000, который определяет, как рисунок ложится на оружие. Для большинства скинов он почти не важен, но у Case Hardened, Fade, Doppler, Crimson Web и некоторых других редкий паттерн может стоить в разы дороже обычного.</p>
<h2>StatTrak™</h2>
<p>Версия со счётчиком убийств. Обычно стоит дороже — иногда в два раза и больше. На <a href="/prices/">страницах цен</a> обычная и StatTrak™ версии показаны отдельно.</p>
<h2>Наклейки</h2>
<p>Редкие наклейки (особенно старых турниров) могут поднять цену. Обычные наклейки почти не влияют на стоимость.</p>
<h2>Как выбрать</h2>
<ul>
<li>Хотите выгодно — Field-Tested или Minimal Wear с низким float.</li>
<li>Важна картинка — посмотрите 3D-просмотр лота: в приложении DGhostMarket износ виден на модели.</li>
<li>Сравните цену с рынком: на карточке лота видно, насколько она ниже или выше.</li>
</ul>
<p>Посмотреть цены по износам — в <a href="/prices/">каталоге цен на скины CS2 в сумах</a>.</p>
''',
        },
        'uz': {
            'title': 'CS2’da skin float’i va holati nima — oddiy tushuntirish',
            'h1': 'CS2’da skin float’i va holati nima',
            'desc': 'CS2 skinlarining float’i va holati oddiy so‘zlar bilan: Factory New — Battle-Scarred oraliqlari, nega bitta skin narxi bir necha baravar farq qiladi, naqsh va StatTrak™ nima.',
            'body': '''
<p>Bitta skinning narxi bir necha baravar farq qilishi mumkin. Asosiy sabablar — holat (float), naqsh, StatTrak™ va stikerlar.</p>
<h2>Float — aniq eskirish darajasi</h2>
<p>Float — 0 dan 1 gacha bo‘lgan son: qancha kichik bo‘lsa, skin shuncha «yangi» ko‘rinadi. Float bo‘yicha holat toifasi aniqlanadi:</p>
<ul>
<li><b>Zavoddan yangi (Factory New)</b> — 0,00–0,07</li>
<li><b>Biroz ishlatilgan (Minimal Wear)</b> — 0,07–0,15</li>
<li><b>Dala sinovidan keyin (Field-Tested)</b> — 0,15–0,38</li>
<li><b>Eskirgan (Well-Worn)</b> — 0,38–0,45</li>
<li><b>Jangda toblangan (Battle-Scarred)</b> — 0,45–1,00</li>
</ul>
<p>Bitta toifa ichida ham past float qadrlanadi: float’i 0,15 bo‘lgan Field-Tested deyarli Minimal Wear’dek ko‘rinadi va 0,37 dagisidan qimmatroq turadi. Hamma skinlarda barcha toifalar bo‘lavermaydi — ba’zilarida float cheklangan (masalan, 0,00–0,08).</p>
<h2>Naqsh</h2>
<p>Naqsh (paint seed) — 0 dan 1000 gacha raqam, u rasm qurolga qanday tushishini belgilaydi. Ko‘pchilik skinlar uchun u deyarli ahamiyatsiz, lekin Case Hardened, Fade, Doppler, Crimson Web va boshqa ba’zi skinlarda noyob naqsh oddiysidan bir necha baravar qimmat turishi mumkin.</p>
<h2>StatTrak™</h2>
<p>O‘ldirishlar hisoblagichi bor versiya. Odatda qimmatroq — ba’zan ikki baravar va undan ham ko‘p. <a href="/prices/">Narxlar sahifalarida</a> oddiy va StatTrak™ versiyalari alohida ko‘rsatilgan.</p>
<h2>Stikerlar</h2>
<p>Noyob stikerlar (ayniqsa eski turnirlarniki) narxni oshirishi mumkin. Oddiy stikerlar qiymatga deyarli ta’sir qilmaydi.</p>
<h2>Qanday tanlash kerak</h2>
<ul>
<li>Foydali xarid istasangiz — past float’li Field-Tested yoki Minimal Wear.</li>
<li>Ko‘rinish muhim bo‘lsa — lotning 3D ko‘rinishiga qarang: DGhostMarket ilovasida holat modelda ko‘rinadi.</li>
<li>Narxni bozor bilan solishtiring: lot kartochkasida narx qancha past yoki baland ekani ko‘rinadi.</li>
</ul>
<p>Holatlar bo‘yicha narxlarni ko‘rish — <a href="/prices/">CS2 skinlari narxlari so‘mda katalogida</a>.</p>
''',
        },
    },
]


def esc(s):
    return html.escape(str(s), quote=True)


def prefix(lang):
    return '' if lang == 'ru' else f'/{lang}'


def localize_links(body, lang):
    """Внутренние ссылки статьи → версия на языке lang."""
    p = prefix(lang)
    return re.sub(r'href="/(?!/)', f'href="{p}/', body) if p else body


def guide_main(g, lang):
    t = T[lang]
    p = prefix(lang)
    d = g[lang]
    others = [x for x in GUIDES if x is not g]
    more = ''.join(f'<a href="{p}/guides/{x["slug"]}/"><b>{esc(x[lang]["h1"])}</b></a>' for x in others)
    return (f'<main id="top"><div class="wrap"><nav class="crumbs"><a href="{p}/">{esc(t["home"])}</a> / '
            f'<a href="{p}/guides/">{esc(t["hub"])}</a></nav><article class="article"><h1>{esc(d["h1"])}</h1>'
            f'<p class="crumbs">{esc(t["updated"])}: {UPDATED[8:10]}.{UPDATED[5:7]}.{UPDATED[:4]}</p>'
            f'{localize_links(d["body"], lang)}'
            f'<div class="actions"><a class="btn primary" href="https://app.dghostmarket.com/">{esc(t["cta"])}</a>'
            f'<a class="btn ghost" href="{p}/prices/">{esc(t["prices"])}</a></div>'
            f'<h2>{esc(t["more"])}</h2><div class="guide-list">{more}</div></article></div></main>')


def hub_main(lang):
    t = T[lang]
    p = prefix(lang)
    items = ''.join(f'<a href="{p}/guides/{g["slug"]}/"><b>{esc(g[lang]["h1"])}</b><span>{esc(g[lang]["desc"])}</span></a>'
                    for g in GUIDES)
    return (f'<main id="top"><div class="wrap"><nav class="crumbs"><a href="{p}/">{esc(t["home"])}</a> / {esc(t["hub"])}</nav>'
            f'<h1>{esc(t["hub_h1"])}</h1><p class="lead">{esc(t["hub_lead"])}</p>'
            f'<div class="guide-list">{items}</div></div></main>')


def article_jsonld(g, lang, url, site):
    d = g[lang]
    return {
        '@context': 'https://schema.org', '@type': 'Article', 'headline': d['h1'], 'description': d['desc'],
        'inLanguage': lang, 'datePublished': UPDATED, 'dateModified': UPDATED, 'mainEntityOfPage': url,
        'author': {'@type': 'Organization', 'name': 'DGhostMarket', 'url': site + '/'},
        'publisher': {'@type': 'Organization', 'name': 'DGhostMarket',
                      'logo': {'@type': 'ImageObject', 'url': site + '/apple-touch-icon.png'}},
    }
