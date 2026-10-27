#!/usr/bin/env python3
"""Génère les pages « verset du jour » du site depuis les versets de l'app.

    python3 tools/build-verses.py [chemin/vers/Verses.json]

Écrit verset-du-jour/index.html (le verset d'aujourd'hui + tous les jours),
verset-du-jour/<jour>-<mois>/index.html (365 pages) et sitemap.xml.
Les versets sont repris tels quels : ne jamais les modifier ici.
"""
import datetime, html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Projects/Bible/VersetDuJour/App/Verses.json")
SITE = "https://aubeapp.fr"
STORE = "https://apps.apple.com/fr/app/aube-verset-du-jour/id6824431832?ct=site-verset"
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]
SLUG = {"février": "fevrier", "août": "aout", "décembre": "decembre"}

verses = json.load(open(SRC, encoding="utf-8"))
assert len(verses) == 365, len(verses)

# Jour n de l'année (année non bissextile) → verset n, comme dans l'app.
days = []
d = datetime.date(2027, 1, 1)
while d.year == 2027:
    m = MONTHS[d.month - 1]
    label = ("1er" if d.day == 1 else str(d.day)) + " " + m
    slug = f"{d.day}-{SLUG.get(m, m)}"
    days.append({"date": d, "label": label, "slug": slug, "verse": verses[d.timetuple().tm_yday - 1]})
    d += datetime.timedelta(days=1)

E = html.escape
APPLE = '<svg viewBox="0 0 384 512" aria-hidden="true"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>'
MARK = '<svg viewBox="0 0 64 52" class="mark" aria-hidden="true"><path d="M14 42a18 18 0 0 1 36 0"/><path d="M8 42h48"/><path d="M32 12v6"/><path d="M14 20l4 4"/><path d="M50 20l-4 4"/></svg>'


def head(title, desc, path, extra=""):
    url = SITE + path
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="apple-itunes-app" content="app-id=6824431832">
<meta name="theme-color" content="#FBF6EE">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Aube">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-aube.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/icon-180.png">
<link rel="apple-touch-icon" href="/assets/icon-180.png">
<link rel="stylesheet" href="/assets/verset.css">
{extra}</head>
<body>
<nav class="top"><a class="brand" href="/">{MARK}Aube</a><a href="/verset-du-jour/">Verset du jour</a></nav>
"""


def cta():
    return f"""<section class="cta">
  <p class="cta-kicker">Chaque matin à 6 h</p>
  <h2>Recevez le verset du jour sur votre iPhone.</h2>
  <p>Aube vous envoie un verset de la Bible chaque matin. Gratuite, sans compte, sans publicité.</p>
  <a class="store" href="{STORE}">{APPLE}Télécharger dans l’App Store</a>
</section>
"""


def footer():
    return """<footer><a href="/">Aube</a><a href="/verset-du-jour/">Tous les versets du jour</a><a href="/privacy/">Confidentialité</a><a href="mailto:contact@aubeapp.fr">contact@aubeapp.fr</a></footer>
"""


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


def write(path, text):
    full = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)


# Pages par jour
for i, day in enumerate(days):
    v = day["verse"]
    prev, nxt = days[i - 1], days[(i + 1) % 365]
    path = f"/verset-du-jour/{day['slug']}/"
    title = f"Verset du jour du {day['label']} : {v['reference']} | Aube"
    desc = f"Verset biblique du {day['label']} ({v['reference']}, Louis Segond) : « {v['text'][:110]}{'…' if len(v['text']) > 110 else ''} »"
    ld = jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "Quotation", "text": v["text"], "citation": f"{v['reference']} (Louis Segond 1910)",
         "inLanguage": "fr", "url": SITE + path},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Aube", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Verset du jour", "item": SITE + "/verset-du-jour/"},
            {"@type": "ListItem", "position": 3, "name": day["label"], "item": SITE + path}]}]})
    write(path, head(title, desc, path, ld) + f"""<main>
<header class="day-head">
  <p class="kicker">Verset du jour</p>
  <h1>{E(day['label'])}</h1>
</header>
<figure class="verse">
  <blockquote>{E(v['text'])}</blockquote>
  <figcaption>{E(v['reference'])}</figcaption>
</figure>
<p class="note">Traduction Louis Segond 1910. C’est le verset qu’Aube propose le {E(day['label'])}.</p>
<nav class="pager" aria-label="Autres jours">
  <a href="/verset-du-jour/{prev['slug']}/" rel="prev">← {E(prev['label'])}</a>
  <a href="/verset-du-jour/{nxt['slug']}/" rel="next">{E(nxt['label'])} →</a>
</nav>
{cta()}</main>
{footer()}</body>
</html>
""")

# Page d'accueil des versets : verset d'aujourd'hui (calculé dans le navigateur, comme l'app) + tous les jours
month_blocks = []
for mi, m in enumerate(MONTHS):
    items = "".join(
        f'<li><a href="/verset-du-jour/{d["slug"]}/"><span>{E(d["label"])}</span>{E(d["verse"]["reference"])}</a></li>'
        for d in days if d["date"].month == mi + 1)
    month_blocks.append(f'<section class="month"><h3>{m.capitalize()}</h3><ul>{items}</ul></section>')

data = json.dumps([[v["text"], v["reference"]] for v in verses], ensure_ascii=False)
labels = json.dumps([d["slug"] for d in days])
today_path = "/verset-du-jour/"
first = days[0]
write(today_path, head(
    "Verset du jour : le verset biblique d’aujourd’hui | Aube",
    "Le verset biblique du jour, chaque jour de l’année, dans la traduction Louis Segond. Recevez-le chaque matin à 6 h avec Aube, l’app gratuite.",
    today_path, jsonld({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Verset du jour",
                        "url": SITE + today_path, "inLanguage": "fr"})) + f"""<main>
<header class="day-head">
  <p class="kicker">Verset du jour</p>
  <h1 id="today-label">Aujourd’hui</h1>
</header>
<figure class="verse" id="today">
  <blockquote>{E(first['verse']['text'])}</blockquote>
  <figcaption>{E(first['verse']['reference'])}</figcaption>
</figure>
<p class="note">Le même verset que dans l’app Aube aujourd’hui. Traduction Louis Segond 1910.</p>
{cta()}
<section class="all">
  <h2>Un verset pour chaque jour de l’année</h2>
  {''.join(month_blocks)}
</section>
</main>
{footer()}<script>
(function () {{
  var V = {data};
  var now = new Date();
  var start = new Date(now.getFullYear(), 0, 1);
  var day = Math.round((new Date(now.getFullYear(), now.getMonth(), now.getDate()) - start) / 864e5) + 1;
  var v = V[(day - 1) % V.length];
  var fig = document.getElementById('today');
  fig.querySelector('blockquote').textContent = v[0];
  fig.querySelector('figcaption').textContent = v[1];
  document.getElementById('today-label').textContent = now.toLocaleDateString('fr-FR', {{ weekday: 'long', day: 'numeric', month: 'long' }});
}})();
</script>
</body>
</html>
""")

# Plan du site
today = datetime.date.today().isoformat()
urls = ["/", "/verset-du-jour/", "/privacy/"] + [f"/verset-du-jour/{d['slug']}/" for d in days]
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    + "</urlset>\n")
print(f"{len(days)} pages de jour, 1 page d'accueil des versets, sitemap de {len(urls)} adresses")
