import os
import requests
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template_string

#── CONFIG ──────────────────────────────────────────────────────────────────
# Put your GNews API key here (get free key at https://gnews.io)
# OR set environment variable:  export GNEWS_API_KEY=your_key_here
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "YOUR_API_KEY")

PORT = 5000
# ────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)

SECTIONS = [
    {"id": "defence",  "label": "Defence & Security", "kicker": "Strategic Affairs",     "topic": None,         "query": "defence military army security threat", "head": "DEFENCE & SECURITY",    "sub": "Strategic affairs, military operations & national security intelligence"},
    {"id": "business", "label": "Business",           "kicker": "Markets & Commerce",    "topic": "business",   "query": None,                                   "head": "BUSINESS & MARKETS",    "sub": "Commerce, trade, financial markets & corporate intelligence"},
    {"id": "tech",     "label": "Technology",         "kicker": "Science & Innovation",  "topic": "technology", "query": None,                                   "head": "TECHNOLOGY",            "sub": "Artificial intelligence, innovation, cybersecurity & digital frontiers"},
    {"id": "world",    "label": "World",              "kicker": "Foreign Correspondence","topic": "world",      "query": None,                                   "head": "WORLD AFFAIRS",         "sub": "Geopolitics, diplomacy & international relations"},
    {"id": "politics", "label": "Politics",           "kicker": "Governance & Policy",   "topic": "politics",   "query": None,                                   "head": "POLITICS & GOVERNANCE", "sub": "Elections, policy, parliament & the machinery of state"},
    {"id": "science",  "label": "Science",            "kicker": "Knowledge & Discovery", "topic": "science",    "query": None,                                   "head": "SCIENCE & ENVIRONMENT", "sub": "Research, discovery, climate & the natural world"},
    {"id": "sports",   "label": "Sports",             "kicker": "Athletics & Competition","topic": "sports",    "query": None,                                   "head": "SPORTS",                "sub": "Athletics, competition, records & the pursuit of excellence"},
    {"id": "health",   "label": "Health",             "kicker": "Medicine & Wellbeing",  "topic": "health",     "query": None,                                   "head": "HEALTH & MEDICINE",     "sub": "Medical research, public health & the science of human wellbeing"},
]


def fetch_section(section):
    """Fetch articles for a section from GNews API."""
    base = "https://gnews.io/api/v4"
    if section["topic"]:
        url = f"{base}/top-headlines?topic={section['topic']}&lang=en&max=9&apikey={GNEWS_API_KEY}"
    else:
        url = f"{base}/search?q={requests.utils.quote(section['query'])}&lang=en&max=9&sortby=publishedAt&apikey={GNEWS_API_KEY}"

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if resp.status_code == 401:
            return {"articles": [], "error": "Invalid API key (401). Check GNEWS_API_KEY in app.py"}
        if resp.status_code == 429:
            return {"articles": [], "error": "Rate limit exceeded (100/day). Wait until tomorrow."}
        if not resp.ok:
            msg = (data.get("errors") or [data.get("message", f"HTTP {resp.status_code}")])[0]
            return {"articles": [], "error": str(msg)}

        errors = data.get("errors", [])
        if errors:
            return {"articles": [], "error": errors[0]}

        articles = [
            a for a in data.get("articles", [])
            if a.get("title") and a.get("description") and a.get("url")
        ][:8]
        return {"articles": articles, "error": None}

    except requests.exceptions.ConnectionError:
        return {"articles": [], "error": "No internet connection or DNS failure."}
    except requests.exceptions.Timeout:
        return {"articles": [], "error": "Request timed out. Check your internet."}
    except Exception as e:
        return {"articles": [], "error": str(e)}


# ── ROUTES

@app.route("/")
def index():
    """Serve the main e-paper page."""
    key_missing = (GNEWS_API_KEY == "YOUR_GNEWS_API_KEY_HERE" or not GNEWS_API_KEY.strip())
    return render_template_string(HTML_TEMPLATE,
        sections=SECTIONS,
        today=datetime.now().strftime("%A, %d %B %Y"),
        key_missing=key_missing,
        api_key_hint=GNEWS_API_KEY[:6] + "…" if len(GNEWS_API_KEY) > 8 else "(not set)"
    )


@app.route("/api/news/<section_id>")
def get_news(section_id):
    """API endpoint — fetch news for one section."""
    section = next((s for s in SECTIONS if s["id"] == section_id), None)
    if not section:
        return jsonify({"error": "Unknown section", "articles": []}), 404
    if GNEWS_API_KEY == "YOUR_GNEWS_API_KEY_HERE" or not GNEWS_API_KEY.strip():
        return jsonify({"error": "API key not set. Open app.py and set GNEWS_API_KEY.", "articles": []}), 500
    result = fetch_section(section)
    return jsonify(result)


@app.route("/api/sections")
def get_sections():
    """Return section metadata for the frontend."""
    return jsonify(SECTIONS)


# ── HTML TEMPLATE ─

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>The Daily Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,400&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet"/>
<style>
:root{--ink:#1a1410;--ink-f:#4a4035;--ink-m:#7a6e60;--paper:#f5f0e8;--paper2:#ede8dc;--paper3:#d8d0c0;--thin:rgba(26,20,16,.25);--red:#8b1a1a;--blue:#2c4a6e}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#c8bfaa;font-family:'Source Serif 4',Georgia,serif;color:var(--ink);min-height:100vh;padding:20px;
  background-image:repeating-linear-gradient(0deg,transparent,transparent 59px,rgba(0,0,0,.04) 60px)}

/* KEY WARNING */
.key-warn{background:var(--red);color:#fff;padding:12px 24px;text-align:center;font-family:'IM Fell English',serif;font-size:13px;line-height:1.7}
.key-warn strong{display:block;font-size:15px;margin-bottom:3px}
.key-warn code{background:rgba(0,0,0,.3);padding:2px 6px;font-size:12px;letter-spacing:.04em}

/* PAPER */
#paper{max-width:1100px;margin:0 auto;background:var(--paper);box-shadow:0 0 40px rgba(0,0,0,.22)}

/* MASTHEAD */
.masthead{border-bottom:4px double var(--ink);padding:14px 28px 10px;text-align:center}
.masthead-meta{display:flex;justify-content:space-between;font-family:'IM Fell English',serif;font-size:11px;color:var(--ink-m);border-bottom:1px solid var(--thin);padding-bottom:5px;margin-bottom:7px}
.masthead-title{font-family:'UnifrakturMaguntia',serif;font-size:clamp(36px,6vw,70px);line-height:1}
.masthead-tag{font-family:'IM Fell English',serif;font-style:italic;font-size:12.5px;color:var(--ink-f);letter-spacing:.1em;border-top:1px solid var(--thin);border-bottom:1px solid var(--thin);padding:3px 0;margin:4px 0 6px}

/* NAV */
.sec-nav{background:var(--ink);display:flex;overflow-x:auto;scrollbar-width:none}
.sec-nav::-webkit-scrollbar{display:none}
.nav-tab{font-family:'IM Fell English',serif;font-size:11.5px;color:var(--paper);padding:9px 16px;cursor:pointer;letter-spacing:.08em;text-transform:uppercase;border-right:1px solid rgba(255,255,255,.12);transition:background .18s;white-space:nowrap;flex-shrink:0}
.nav-tab:hover{background:rgba(255,255,255,.1)}
.nav-tab.active{background:var(--red)}

/* TICKER */
.ticker-wrap{background:var(--paper2);border-top:1px solid var(--thin);border-bottom:1px solid var(--thin);overflow:hidden;padding:5px 0;min-height:27px}
.ticker-track{display:flex;gap:48px;animation:tick 55s linear infinite;width:max-content}
.ticker-item{font-family:'IM Fell English',serif;font-size:12px;color:var(--ink-f);white-space:nowrap}
.ticker-item::before{content:'◆  ';color:var(--red);font-size:8px}
@keyframes tick{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* LOADING overlay per section */
.page{display:none;padding-bottom:40px;min-height:400px}
.page.active{display:block}
.page-loading{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:340px;gap:16px}
.spinner{width:28px;height:28px;border:2px solid var(--paper3);border-top-color:var(--ink);border-radius:50%;animation:spin .85s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-txt{font-family:'IM Fell English',serif;font-size:13px;color:var(--ink-m);font-style:italic}

/* SECTION HEADER */
.sec-header{padding:12px 28px 0;border-bottom:3px solid var(--ink)}
.sec-label{font-family:'IM Fell English',serif;font-size:11px;letter-spacing:.2em;color:var(--red);text-transform:uppercase;margin-bottom:3px}
.sec-header h1{font-family:'Playfair Display',serif;font-size:clamp(26px,4vw,46px);font-weight:900;line-height:1;margin-bottom:5px}
.sec-sub{font-family:'IM Fell English',serif;font-size:12px;color:var(--ink-m);font-style:italic;padding-bottom:7px}

/* BREAKING */
.breaking{background:var(--red);color:var(--paper);padding:5px 28px;font-family:'IM Fell English',serif;font-size:12px;letter-spacing:.08em;display:flex;align-items:center;gap:10px}
.flash{background:var(--paper);color:var(--red);font-size:10px;font-weight:700;padding:1px 5px;letter-spacing:.1em;animation:pulse 1.3s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}

/* GRID */
.grid{display:grid;gap:0;padding:0 20px}
.g3{grid-template-columns:2fr 1fr 1fr}
.g4{grid-template-columns:repeat(4,1fr)}
.grid>*:not(:last-child){border-right:1px solid var(--thin)}
.grid .art{padding:16px 18px}
.h-rule{border-top:1px solid var(--thin);margin:0 20px}
.h-rule.thick{border-color:var(--ink);border-width:2px}

/* ARTICLE */
.art .kicker{font-family:'IM Fell English',serif;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--red);margin-bottom:5px}
.art h2{font-family:'Playfair Display',serif;font-weight:900;line-height:1.22;margin-bottom:7px;color:var(--ink)}
.art h2.xl{font-size:clamp(18px,2.8vw,30px)}
.art h2.lg{font-size:clamp(15px,2vw,20px)}
.art h2.md{font-size:15px}
.byline{font-family:'IM Fell English',serif;font-size:11px;color:var(--ink-m);font-style:italic;margin-bottom:7px;padding-bottom:5px;border-bottom:1px solid var(--thin)}
.art p{font-size:13.5px;line-height:1.78;color:var(--ink-f);margin-bottom:7px;text-align:justify;hyphens:auto}
.art p.dc::first-letter{font-family:'Playfair Display',serif;font-size:54px;font-weight:900;float:left;line-height:.84;margin:4px 5px 0 0;color:var(--ink)}
.src-tag{display:inline-block;font-family:'IM Fell English',serif;font-size:10px;letter-spacing:.09em;color:var(--paper);background:var(--ink-m);padding:2px 6px;margin-bottom:5px;text-transform:uppercase}
.read-more{display:inline-block;font-family:'IM Fell English',serif;font-size:12px;color:var(--blue);text-decoration:none;font-style:italic;margin-top:3px}
.read-more:hover{text-decoration:underline}
.img-wrap{width:100%;aspect-ratio:16/9;background:var(--paper3);overflow:hidden;margin-bottom:9px}
.img-wrap img{width:100%;height:100%;object-fit:cover;display:block}
.img-miss{display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-family:'IM Fell English',serif;font-size:11px;color:var(--ink-m);font-style:italic}
.err-box{margin:20px 28px;padding:14px 16px;border:1.5px solid var(--red);background:#fdf0f0;font-family:'IM Fell English',serif;font-size:13px;color:var(--red);line-height:1.7}
.err-box strong{display:block;font-size:14px;margin-bottom:4px}
.empty{padding:40px 28px;text-align:center;font-family:'IM Fell English',serif;font-style:italic;color:var(--ink-m);font-size:13px}

/* REFRESH */
.refresh-bar{display:flex;align-items:center;justify-content:space-between;padding:9px 28px;border-top:1px solid var(--thin);background:var(--paper2);font-family:'IM Fell English',serif;font-size:12px;color:var(--ink-m)}
.ref-btn{background:none;border:1px solid var(--ink-m);color:var(--ink);font-family:'IM Fell English',serif;font-size:12px;padding:4px 14px;cursor:pointer}
.ref-btn:hover{background:var(--paper3)}

@media(max-width:760px){
  body{padding:10px}
  .g3,.g4{grid-template-columns:1fr}
  .grid>*:not(:last-child){border-right:none;border-bottom:1px solid var(--thin)}
}
</style>
</head>
<body>

{% if key_missing %}
<div class="key-warn">
  <strong>⚠ API Key Not Set</strong>
  Open <code>app.py</code> and set your GNews API key: <code>GNEWS_API_KEY = "your_key_here"</code>
  &nbsp;·&nbsp; Get a free key at <a href="https://gnews.io" target="_blank" style="color:#ffcccc">gnews.io</a>
</div>
{% endif %}

<div id="paper">
  <div class="masthead">
    <div class="masthead-meta">
      <span>{{ today }}</span>
      <span>VOL. I &nbsp;·&nbsp; No. 1</span>
      <span>Powered by GNews API</span>
    </div>
    <div class="masthead-title">The Daily Intelligence</div>
    <div class="masthead-tag">All the news that is fit to print — curated, verified, classified</div>
  </div>

  <div class="sec-nav" id="sec-nav">
    {% for s in sections %}
    <div class="nav-tab {% if loop.first %}active{% endif %}" data-id="{{ s.id }}" onclick="switchPage('{{ s.id }}')">
      {{ s.label }}
    </div>
    {% endfor %}
  </div>

  <div class="ticker-wrap">
    <div class="ticker-track" id="ticker">
      <span class="ticker-item">Loading latest headlines from wire services…</span>
    </div>
  </div>

  <div id="pages">
    {% for s in sections %}
    <div class="page {% if loop.first %}active{% endif %}" id="page-{{ s.id }}" data-loaded="false">
      <div class="page-loading">
        <div class="spinner"></div>
        <div class="loading-txt">Gathering {{ s.label }} dispatches…</div>
      </div>
    </div>
    {% endfor %}
  </div>

  <div class="refresh-bar">
    <span id="last-fetch">Last fetched: —</span>
    <button class="ref-btn" onclick="refreshAll()">↺ Refresh Edition</button>
  </div>
</div>

<script>
const SECTIONS = {{ sections | tojson }};
const store = {};

// ── INIT: load first section immediately, rest lazily ──
document.addEventListener('DOMContentLoaded', () => {
  loadSection(SECTIONS[0]);
  // Load remaining sections with a small stagger
  SECTIONS.slice(1).forEach((s, i) => setTimeout(() => loadSection(s), (i+1) * 600));
});

async function loadSection(s) {
  const page = document.getElementById('page-' + s.id);
  if (page.dataset.loaded === 'true') return;

  try {
    const res = await fetch('/api/news/' + s.id);
    const data = await res.json();
    store[s.id] = data;
    page.innerHTML = renderPage(s, data);
    page.dataset.loaded = 'true';
    updateTicker();
  } catch(e) {
    page.innerHTML = renderError(s, 'Network error: ' + e.message);
  }
}

function refreshAll() {
  document.querySelectorAll('.page').forEach(p => {
    p.dataset.loaded = 'false';
    const s = SECTIONS.find(x => x.id === p.id.replace('page-',''));
    if (s) p.innerHTML = `<div class="page-loading"><div class="spinner"></div><div class="loading-txt">Refreshing ${s.label}…</div></div>`;
  });
  document.getElementById('ticker').innerHTML = '<span class="ticker-item">Refreshing headlines…</span>';
  SECTIONS.forEach((s,i) => setTimeout(() => loadSection(s), i * 500));
  document.getElementById('last-fetch').textContent = 'Refreshed: ' + new Date().toLocaleTimeString();
}

function switchPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-'+id).classList.add('active');
  document.querySelector(`.nav-tab[data-id="${id}"]`).classList.add('active');
  // Lazy-load if not yet loaded
  const s = SECTIONS.find(x => x.id === id);
  if (s) loadSection(s);
}

function updateTicker() {
  const all = Object.values(store).flatMap(r => (r.articles || []));
  if (!all.length) return;
  const items = all.slice(0, 24).map(a => `<span class="ticker-item">${esc(a.title)}</span>`).join('');
  document.getElementById('ticker').innerHTML = items + items;
  document.getElementById('last-fetch').textContent = 'Last fetched: ' + new Date().toLocaleTimeString();
}

// ── RENDER ──
function renderPage(s, result) {
  const header = `
    <div class="sec-header">
      <div class="sec-label">${s.kicker}</div>
      <h1>${s.head}</h1>
      <div class="sec-sub">${s.sub}</div>
    </div>`;

  if (result.error && !result.articles.length) return header + renderError(s, result.error);

  const arts = result.articles || [];
  if (!arts.length) return header + `<div class="empty">No articles found for this section.</div>`;

  const lead = arts[0];
  const mid  = arts.slice(1,3);
  const rest = arts.slice(3,7);
  const sn = a => (a.source && a.source.name) ? a.source.name : 'Wire Service';
  const img = a => a.image || null;

  const leadHtml = `
    <div class="art" style="padding-top:16px">
      <div class="kicker">${esc(sn(lead))}</div>
      <h2 class="xl">${esc(lead.title)}</h2>
      <div class="byline">By Wire Correspondent &nbsp;·&nbsp; ${ago(lead.publishedAt)}</div>
      ${img(lead) ? `<div class="img-wrap"><img src="${esc(img(lead))}" alt="" onerror="this.parentElement.innerHTML='<div class=img-miss>Image unavailable</div>'" loading="lazy"></div>` : ''}
      <p class="dc">${esc(clip(lead.description, 280))}</p>
      <a class="read-more" href="${esc(lead.url)}" target="_blank" rel="noopener">Continue reading at ${esc(sn(lead))} →</a>
    </div>`;

  const midHtml = mid.map(a => `
    <div class="art" style="padding-top:16px">
      <div class="kicker">${esc(sn(a))}</div>
      <h2 class="lg">${esc(a.title)}</h2>
      <div class="byline">${ago(a.publishedAt)}</div>
      ${img(a) ? `<div class="img-wrap"><img src="${esc(img(a))}" alt="" onerror="this.parentElement.style.display='none'" loading="lazy"></div>` : ''}
      <p>${esc(clip(a.description, 180))}</p>
      <a class="read-more" href="${esc(a.url)}" target="_blank" rel="noopener">Read more →</a>
    </div>`).join('');

  const restHtml = rest.length ? `
    <div class="h-rule thick"></div>
    <div class="grid g4">
      ${rest.map(a => `
      <div class="art" style="padding-top:13px">
        <span class="src-tag">${esc(sn(a))}</span>
        <h2 class="md">${esc(a.title)}</h2>
        <div class="byline">${ago(a.publishedAt)}</div>
        <p>${esc(clip(a.description, 130))}</p>
        <a class="read-more" href="${esc(a.url)}" target="_blank" rel="noopener">Full story →</a>
      </div>`).join('')}
    </div>` : '';

  return `
    <div class="breaking"><span class="flash">LATEST</span>${esc(sn(lead))} · ${ago(lead.publishedAt)}</div>
    ${header}
    <div class="grid g3">${leadHtml}${midHtml}</div>
    ${restHtml}`;
}

function renderError(s, msg) {
  return `
    <div class="err-box">
      <strong>Dispatch Failure — ${esc(s.label)}</strong>
      ${esc(String(msg))}<br><br>
      Check your <code>GNEWS_API_KEY</code> in <code>app.py</code> and your internet connection.
    </div>`;
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function clip(s, n) {
  if (!s) return '';
  s = String(s);
  return s.length > n ? s.slice(0,n).replace(/\\s\\S*$/,'') + '…' : s;
}
function ago(iso) {
  if (!iso) return '';
  const m = (Date.now() - new Date(iso)) / 60000;
  if (m < 60) return Math.round(m) + 'm ago';
  if (m < 1440) return Math.round(m/60) + 'h ago';
  return Math.round(m/1440) + 'd ago';
}
</script>
</body>
</html>"""


# ── ENTRY POINT ─

if __name__ == "__main__":
    print("\n" + "="*54)
    print("  📰  The Daily Intelligence — AI E-Paper")
    print("="*54)

    if GNEWS_API_KEY == "YOUR_GNEWS_API_KEY_HERE" or not GNEWS_API_KEY.strip():
        print("\n  ⚠  WARNING: API key not set!")
        print("  Open app.py and set GNEWS_API_KEY = 'your_key'")
        print("  Or run:  export GNEWS_API_KEY=your_key && python app.py")
        print("  Get a free key at: https://gnews.io\n")
    else:
        print(f"\n  ✓  GNews API key loaded ({GNEWS_API_KEY[:6]}…)")

    print(f"\n  ➜  Open your browser: http://localhost:{PORT}")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=False, port=PORT, host="0.0.0.0")
