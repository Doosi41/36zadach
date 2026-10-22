<p align="center"><a href="README.md">English</a> &nbsp;|&nbsp; <b>Русский</b></p>

<a href="#how"><img src="assets/banner.svg" alt="3D PRO — калькулятор 3D-печати с ИИ. Загрузил STL. Получил цену. Отправил КП." width="100%"></a>

<p align="center">
  <a href="#screens">В деле&nbsp;›</a>&emsp;
  <a href="#features">Возможности&nbsp;›</a>&emsp;
  <a href="#how">Как считается&nbsp;›</a>&emsp;
  <a href="#ai">КП&nbsp;›</a>&emsp;
  <a href="#run">Запуск&nbsp;›</a>&emsp;
  <a href="#structure">Структура&nbsp;›</a>
</p>

<br>

<img src="assets/stats.svg" alt="Один STL-файл, чтобы получить цену. Три технологии: FDM, SLA, SLM. Django 6 и Python 3.12. ИИ пишет описание и коммерческое предложение." width="100%">

<br>
<br>

<p align="center">
  <i>«Any sufficiently advanced technology is indistinguishable from magic.»</i><br>
  <sub>— Arthur C. Clarke</sub>
</p>

<br>

<a name="screens"></a>
<img src="assets/titles/screens.svg" alt="В деле" width="100%">

<img src="assets/screen-home.png" alt="Главная страница 3D PRO" width="100%">

<img src="assets/calc.svg" alt="Пример расчёта: шестерня Z20, 59.8 × 59.8 × 10 мм, 640 полигонов, объём 23.47 см³, вес 5.87 г, себестоимость 14.67 ₽, итого 37 ₽" width="100%">

<br>
<br>

<a name="features"></a>
<img src="assets/titles/features.svg" alt="Возможности" width="100%">

<a href="main/views.py"><img src="assets/rows/stl.svg" alt="Разбор STL — numpy-stl считает объём, габариты и число полигонов модели" width="100%"></a>
<a href="main/views.py"><img src="assets/rows/price.svg" alt="Расчёт стоимости — вес по плотности и заполнению, себестоимость и цена с наценкой" width="100%"></a>
<a href="templates/main/calculate.html"><img src="assets/rows/tech.svg" alt="Технологии — FDM, SLA и SLM" width="100%"></a>
<a href="main/views.py"><img src="assets/rows/ai.svg" alt="КП от ИИ — Gemini пишет описание детали и коммерческое предложение" width="100%"></a>
<a href="templates/main/projects_list.html"><img src="assets/rows/projects.svg" alt="Мои проекты — все расчёты хранятся в аккаунте" width="100%"></a>
<a href="main/models.py"><img src="assets/rows/model.svg" alt="Модель проекта — параметры производства: наценка, брак, налог, энергия" width="100%"></a>

<br>
<br>

<a name="how"></a>
<img src="assets/titles/how.svg" alt="Как считается" width="100%">

<img src="assets/flow.svg" alt="Расчёт: загрузка STL, объём и габариты, вес по плотности и заполнению, цена с наценкой 2.5" width="100%">

<br>
<br>

<a name="ai"></a>
<img src="assets/titles/ai.svg" alt="Коммерческое предложение" width="100%">

<img src="assets/ai.svg" alt="В Gemini уходят название, габариты и технология, в ответ приходит JSON с описанием детали и коммерческим предложением" width="100%">

<br>
<br>

<a name="run"></a>
<img src="assets/titles/run.svg" alt="Запуск" width="100%">

<img src="assets/run.svg" alt="Запуск: виртуальное окружение, зависимости, .env из шаблона, migrate, runserver" width="100%">

<details>
<summary>Скопировать команды</summary>
<br>

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # впиши GEMINI_API_KEY
python manage.py migrate
python manage.py runserver  # http://127.0.0.1:8000
python manage.py test       # 19 тестов
```

</details>

<br>

<img src="assets/titles/env.svg" alt="Настройки" width="100%">

<a href=".env.example"><img src="assets/env.svg" alt="Переменные окружения: GEMINI_API_KEY, GEMINI_MODEL, DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS" width="100%"></a>

<br>
<br>

<a name="structure"></a>
<img src="assets/titles/structure.svg" alt="Структура" width="100%">

<img src="assets/structure.svg" alt="Структура репозитория" width="100%">

<br>
<br>

<img src="assets/titles/roadmap.svg" alt="Roadmap" width="100%">

<img src="assets/roadmap.svg" alt="Roadmap: готово 6 из 9" width="100%">

<br>
<br>

<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">

<p align="center">
  <sub>Сделано с ☕ и Django &nbsp;·&nbsp; <a href="https://github.com/a1tvv">@a1tvv</a></sub>
</p>
