# DGhost «Три мира» — промо 15 с (RU + UZ, 9:16 и 4:5)

Ролик на HyperFrames (HTML → видео). Экраны — настоящие снимки мини-аппа
app.dghostmarket.uz (26.11.2026), тексты — из словарей мини-аппа, весь звук синтезирован кодом.

## Перерендерить

```bash
npx hyperframes skills update          # один раз: навыки и CLI HyperFrames
bash tools/render-all.sh               # 4 файла в renders/: 916-ru, 916-uz, 45-ru, 45-uz
bash tools/render-all.sh 916 uz        # только одна версия
```

## Что где

| Файл | Что внутри |
|---|---|
| index.html | корень 9:16: сцены, звук, переменная `lang` (ru / uz) |
| formats/45.html | корень 4:5 (1080×1350); render-all.sh на время рендера ставит его вместо index.html |
| tools/gen-spaces.mjs | генерирует сцены hook/skins/gifts/topup (`FORMAT=45` — для 4:5): переходы мини-аппа, блик, окно лота |
| compositions/, compositions45/ | сцены (сгенерированы; end.html — вручную) |
| tools/gen-audio.mjs | весь звук: ритм 120 BPM и эффекты → assets/sfx + placements.json |
| assets/screens | снимки мини-аппа (RU/UZ), фон экрана выбора без карточек, вырезки окна лота |

## Обновить экраны

Цены и лоты на снимках — на день съёмки. Переснять: Playwright, iPhone 13, ×3,
`reducedMotion: 'reduce'`, `?open=space_skins|space_gifts|space_topup`, язык — `setLanguage('uz')`.
Окно лота снимается без входа в Telegram, поэтому в ролике только его верх (фото, название,
«Деньги у гаранта…») — кнопка оплаты гостю недоступна и в кадр не попадает.
Если сменится лот во втором ряду каталога — поправить координаты `lot` в gen-spaces.mjs.
