<p align="center"><b>English</b> &nbsp;|&nbsp; <a href="README.ru.md">Русский</a></p>

<a href="#how"><img src="assets/en/banner.svg" alt="3D PRO — a 3D printing calculator with AI. Upload an STL. Get a price. Send an offer." width="100%"></a>

<p align="center">
  <a href="#screens">In action&nbsp;›</a>&emsp;
  <a href="#features">Features&nbsp;›</a>&emsp;
  <a href="#how">How it counts&nbsp;›</a>&emsp;
  <a href="#ai">Offer&nbsp;›</a>&emsp;
  <a href="#run">Run&nbsp;›</a>&emsp;
  <a href="#structure">Structure&nbsp;›</a>
</p>

<br>

<img src="assets/en/stats.svg" alt="One STL file to get a price. Three technologies: FDM, SLA, SLM. Django 6 and Python 3.12. AI writes the description and the sales offer." width="100%">

<br>
<br>

<p align="center">
  <i>«Any sufficiently advanced technology is indistinguishable from magic.»</i><br>
  <sub>— Arthur C. Clarke</sub>
</p>

<br>

<a name="screens"></a>
<img src="assets/en/titles/screens.svg" alt="In action" width="100%">

<img src="assets/screen-home.png" alt="3D PRO home page" width="100%">

<img src="assets/en/calc.svg" alt="Example: gear Z20, 59.8 × 59.8 × 10 mm, 640 polygons, volume 23.47 cm³, weight 5.87 g, cost 14.67 ₽, total 37 ₽" width="100%">

<br>
<br>

<a name="features"></a>
<img src="assets/en/titles/features.svg" alt="Features" width="100%">

<a href="main/views.py"><img src="assets/en/rows/stl.svg" alt="Reading STL — numpy-stl counts the volume, size and number of polygons" width="100%"></a>
<a href="main/views.py"><img src="assets/en/rows/price.svg" alt="Price calculation — weight from density and infill, cost and price with markup" width="100%"></a>
<a href="templates/main/calculate.html"><img src="assets/en/rows/tech.svg" alt="Technologies — FDM, SLA and SLM" width="100%"></a>
<a href="main/views.py"><img src="assets/en/rows/ai.svg" alt="AI offer — Gemini writes a part description and a sales offer" width="100%"></a>
<a href="templates/main/projects_list.html"><img src="assets/en/rows/projects.svg" alt="My projects — all calculations are saved in your account" width="100%"></a>
<a href="main/models.py"><img src="assets/en/rows/model.svg" alt="Project model — production settings: markup, defects, tax, energy" width="100%"></a>

<br>
<br>

<a name="how"></a>
<img src="assets/en/titles/how.svg" alt="How it counts" width="100%">

<img src="assets/en/flow.svg" alt="Calculation: upload an STL, get volume and size, weight from density and infill, price with markup 2.5" width="100%">

<br>
<br>

<a name="ai"></a>
<img src="assets/en/titles/ai.svg" alt="Sales offer" width="100%">

<img src="assets/en/ai.svg" alt="The name, size and technology go to Gemini. It sends back JSON with a part description and a sales offer" width="100%">

<br>
<br>

<a name="run"></a>
<img src="assets/en/titles/run.svg" alt="Run" width="100%">

<img src="assets/en/run.svg" alt="Run: virtual environment, packages, .env from the template, migrate, runserver" width="100%">

<details>
<summary>Copy the commands</summary>
<br>

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your GEMINI_API_KEY
python manage.py migrate
python manage.py runserver  # http://127.0.0.1:8000
python manage.py test       # 19 tests
```

</details>

<br>

<img src="assets/en/titles/env.svg" alt="Settings" width="100%">

<a href=".env.example"><img src="assets/en/env.svg" alt="Environment variables: GEMINI_API_KEY, GEMINI_MODEL, DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS" width="100%"></a>

<br>
<br>

<a name="structure"></a>
<img src="assets/en/titles/structure.svg" alt="Structure" width="100%">

<img src="assets/en/structure.svg" alt="Repository structure" width="100%">

<br>
<br>

<img src="assets/en/titles/roadmap.svg" alt="Roadmap" width="100%">

<img src="assets/en/roadmap.svg" alt="Roadmap: 6 of 9 done" width="100%">

<br>
<br>

<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">

<p align="center">
  <sub>Made with ☕ and Django &nbsp;·&nbsp; <a href="https://github.com/a1tvv">@a1tvv</a></sub>
</p>
