#!/usr/bin/env python3
"""
Baut docs/index.html mit den aktuellen Top KI/Tech-Meldungen von der
oeffentlichen, keyless Hacker-News-API (news.ycombinator.com).
Wird taeglich per GitHub Actions ausgefuehrt (siehe .github/workflows/daily-briefing.yml).
"""
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
MAX_CANDIDATES = 120
MAX_RESULTS = 8

KEYWORDS = re.compile(
    r"\b(ai|a\.i\.|gpt|llm|openai|anthropic|claude|gemini|deepmind|nvidia|chip|"
    r"semiconductor|robot|chatbot|machine learning|neural|model|quantum|startup|"
    r"apple|google|meta|microsoft|amazon|spacex|tesla|app store|iphone|android|"
    r"software|cyber|data center|datacenter)\b",
    re.IGNORECASE,
)


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ki-tech-briefing-bot"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def collect_items():
    ids = fetch_json(HN_TOP)[:MAX_CANDIDATES]
    items = []
    for item_id in ids:
        try:
            item = fetch_json(HN_ITEM.format(item_id))
        except Exception:
            continue
        if not item or not item.get("title") or not item.get("url"):
            continue
        if KEYWORDS.search(item["title"]):
            items.append(item)
    items.sort(key=lambda x: x.get("score", 0), reverse=True)
    return items[:MAX_RESULTS]


def render_card(item):
    title = html.escape(item["title"])
    url = html.escape(item["url"])
    score = item.get("score", 0)
    domain = urllib.parse.urlparse(item["url"]).hostname or ""
    domain = re.sub(r"^www\.", "", domain)
    return f"""
        <div class="card">
          <span class="badge">{score} Punkte</span>
          <h2>{title}</h2>
          <a class="source" href="{url}" target="_blank" rel="noopener">{html.escape(domain)} &rarr;</a>
        </div>"""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0f1115">
<title>KI/Tech-Briefing</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%236c5ce7'/%3E%3Ctext x='50' y='66' font-size='55' text-anchor='middle' fill='white' font-family='Arial'%3E%E2%9A%A1%3C/text%3E%3C/svg%3E">
<style>
  :root {{
    --bg: #0f1115; --card: #1a1d24; --card-border: #262a33;
    --text: #eaecef; --muted: #9aa0ab; --accent: #7c6cf2; --accent2: #4fd1c5;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: linear-gradient(180deg, #0f1115 0%, #12141a 100%);
    color: var(--text); min-height: 100vh; padding-bottom: 40px;
  }}
  header {{
    padding: 28px 20px 18px; position: sticky; top: 0;
    background: rgba(15,17,21,0.92); backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--card-border); z-index: 10;
  }}
  header h1 {{ margin: 0; font-size: 22px; letter-spacing: -0.02em; }}
  header h1 span {{ color: var(--accent2); }}
  #date {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
  main {{ padding: 16px; max-width: 640px; margin: 0 auto; }}
  .card {{
    background: var(--card); border: 1px solid var(--card-border);
    border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
  }}
  .card h2 {{ font-size: 16px; margin: 0 0 6px; line-height: 1.35; }}
  .card a.source {{ font-size: 12.5px; color: var(--accent2); text-decoration: none; font-weight: 600; }}
  .badge {{
    display: inline-block; font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--muted); background: #232733; border-radius: 6px; padding: 2px 7px; margin-bottom: 8px;
  }}
  .section-label {{
    font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--muted); margin: 22px 0 10px 4px;
  }}
  button#refresh {{
    background: var(--accent); color: white; border: none; border-radius: 12px;
    padding: 12px 18px; font-size: 14px; font-weight: 600; width: 100%; cursor: pointer; margin-top: 24px;
  }}
  button#refresh[disabled] {{ opacity: 0.5; }}
  #live-status {{ font-size: 12.5px; color: var(--muted); text-align: center; margin-top: 8px; min-height: 16px; }}
  footer {{ text-align: center; color: var(--muted); font-size: 11.5px; margin-top: 30px; padding: 0 20px; line-height: 1.6; }}
</style>
</head>
<body>

<header>
  <h1>KI<span>/</span>Tech-Briefing</h1>
  <div id="date">Automatisch aktualisiert: {stamp} Uhr (UTC)</div>
</header>

<main>
  <div class="section-label">Top-Meldungen von heute</div>
  <div id="static-briefing">{cards}</div>

  <button id="refresh">Jetzt manuell nachladen</button>
  <div id="live-status"></div>
  <div id="live-briefing"></div>

  <footer>
    Automatisch generiert von GitHub Actions, taeglich gegen 6 Uhr MESZ.<br>
    Quelle: oeffentliche Hacker-News-API (news.ycombinator.com), gefiltert nach KI/Tech-Stichwoertern.
  </footer>
</main>

<script>
const KEYWORDS = /\\b(ai|a\\.i\\.|gpt|llm|openai|anthropic|claude|gemini|deepmind|nvidia|chip|semiconductor|robot|chatbot|machine learning|neural|model|quantum|startup|apple|google|meta|microsoft|amazon|spacex|tesla|app store|iphone|android|software|cyber|data center|datacenter)\\b/i;

async function loadLive() {{
  const btn = document.getElementById('refresh');
  const status = document.getElementById('live-status');
  const liveEl = document.getElementById('live-briefing');
  btn.disabled = true;
  status.textContent = 'Lade aktuelle Top-Meldungen...';
  try {{
    const idsRes = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
    const ids = (await idsRes.json()).slice(0, 90);
    const items = await Promise.all(ids.map(id =>
      fetch(`https://hacker-news.firebaseio.com/v0/item/${{id}}.json`).then(r => r.json()).catch(() => null)
    ));
    const filtered = items
      .filter(it => it && it.title && it.url && KEYWORDS.test(it.title))
      .sort((a, b) => (b.score || 0) - (a.score || 0))
      .slice(0, 6);
    if (filtered.length === 0) {{
      status.textContent = 'Keine neuen Live-Treffer gerade eben.';
    }} else {{
      liveEl.innerHTML = '<div class="section-label">Live nachgeladen</div>' +
        filtered.map(it => `
          <div class="card">
            <span class="badge">${{it.score}} Punkte</span>
            <h2>${{it.title}}</h2>
            <a class="source" href="${{it.url}}" target="_blank" rel="noopener">${{new URL(it.url).hostname.replace('www.','')}} &rarr;</a>
          </div>
        `).join('');
      status.textContent = 'Aktualisiert: ' + new Date().toLocaleTimeString('de-DE');
    }}
  }} catch (e) {{
    status.textContent = 'Live-Laden fehlgeschlagen (keine Internetverbindung?).';
  }} finally {{
    btn.disabled = false;
  }}
}}
document.getElementById('refresh').addEventListener('click', loadLive);
</script>

</body>
</html>
"""


def main():
    items = collect_items()
    cards = "".join(render_card(it) for it in items) or "<p>Keine passenden Meldungen gefunden.</p>"
    stamp = datetime.now(timezone.utc).strftime("%d.%m.%Y, %H:%M")
    html_out = PAGE_TEMPLATE.format(cards=cards, stamp=stamp)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Wrote docs/index.html with {len(items)} items.")


if __name__ == "__main__":
    main()
