#!/usr/bin/env python3
import feedparser, requests
from bs4 import BeautifulSoup
from datetime import datetime

RSS_URL = "https://radiofrance-podcast.net/podcast09/rss_11370.xml"
OUTFILE = "rf_podcast_cleaned.html"

# 1) Récupérer et parser le flux RSS
feed = feedparser.parse(RSS_URL)
items = feed.entries
if not items:
    raise SystemExit("Flux vide")

# 2) Date la plus récente (JJ-MM-AAAA)
dates = [datetime(*e.published_parsed[:6]) for e in items]
max_date = max(dates).date()

# 3) Filtrer les épisodes de ce jour
recent = [e for e, d in zip(items, dates) if d.date() == max_date]

# 4) Entête HTML
html = [
    "<!DOCTYPE html>",
    "<html lang='fr'><head><meta charset='UTF-8'><title>On va déguster – Épisodes du même jour</title>",
    "<style>",
    "body{font-family:Arial,sans-serif;max-width:800px;margin:2rem auto;padding:1rem;background:#fafafa;color:#333}",
    "h1{color:#b30000}",
    ".episode{margin-bottom:2rem;padding:1rem;background:#fff;border:1px solid #ddd;border-radius:6px}",
    ".episode h2{margin:0 0 .5rem;font-size:1.2rem}",
    ".date{color:#555;font-size:.9rem;margin-bottom:.5rem}",
    ".content{margin-top:.5rem}",
    "</style></head><body><h1>On va déguster – Épisodes du même jour</h1>"
]

# 5) Pour chaque épisode
for e in recent:
    title = e.title
    link = e.link
    display = datetime(*e.published_parsed[:6]).strftime("%d %B")
    resp = requests.get(link, timeout=10)
    bs = BeautifulSoup(resp.content, "html.parser")
    block = bs.select_one("div.podcast-texte, article, main")
    if block:
        for sel in block.select("nav, header, footer, aside, .related, .advert, .share"):
            sel.decompose()
        content = str(block)
    else:
        content = f"<p><em>Résumé :</em> {e.summary}</p>"

    html += [
        "<div class='episode'>",
        f"<h2><a href='{link}' target='_blank'>{title}</a></h2>",
        f"<div class='date'>{display}</div>",
        "<div class='content'>", content, "</div>",
        "</div>"
    ]

html.append("</body></html>")

with open(OUTFILE, "w", encoding="utf-8") as f:
    f.write("\n".join(html))
