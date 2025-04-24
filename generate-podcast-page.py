#!/usr/bin/env python3
import feedparser, requests
from bs4 import BeautifulSoup
from datetime import datetime

RSS_URL = "https://radiofrance-podcast.net/podcast09/rss_11370.xml"
OUTFILE = "rf_podcast_cleaned.html"

# 1) Parse RSS feed
feed = feedparser.parse(RSS_URL)
entries = feed.entries
if not entries:
    raise SystemExit("Flux RSS vide")

# 2) Find most recent publication date (day-level)
dates = [datetime(*e.published_parsed[:6]) for e in entries]
max_date = max(dates).date()

# 3) Filter entries matching that date
recent = [e for e, dt in zip(entries, dates) if dt.date() == max_date]

# 4) Build HTML output
def build_html(episodes):
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

    for e in episodes:
        title = e.title
        link = e.link
        display = datetime(*e.published_parsed[:6]).strftime("%d %B %Y")

        resp = requests.get(link, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")

        block = soup.select_one("div.podcast-texte, article.podcast-content, main")
        if block:
            for sel in ["nav", "header", "footer", "aside", ".related", ".menu", ".breadcrumb", ".share", ".advert"]:
                for tag in block.select(sel):
                    tag.decompose()
            for tag in block.find_all():
                if not (tag.get_text(strip=True) or tag.find("img") or tag.find("audio")):
                    tag.decompose()
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
    return "\n".join(html)

with open(OUTFILE, "w", encoding="utf-8") as f:
    f.write(build_html(recent))
