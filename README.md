# 📰 The Daily Intelligence — AI E-Paper

A Python-powered AI newspaper that fetches **live, verified news** from trusted global sources and displays it as a beautiful broadsheet e-paper in your browser.

---

## ✨ Features

- 🐍 **Pure Python** — single `app.py` file, no frontend build tools
- 📡 **Live News** — fetches from Reuters, BBC, AP, Bloomberg, The Hindu, NDTV & more via GNews
- 🗞️ **Broadsheet Layout** — classic newspaper design with columns, drop caps & masthead
- 📑 **8 Section Pages** — Defence · Business · Technology · World · Politics · Science · Sports · Health
- ⚡ **Fast** — sections load in parallel, first page appears instantly
- 🔄 **One-click Refresh** — pull latest headlines without restarting

---

## 🚀 Setup & Run (3 steps)

### Step 1 — Get a free GNews API key
1. Go to **https://gnews.io** → click *Get API Key*
2. Sign up with email and confirm it
3. Copy your API key from the dashboard

Free tier: **100 requests/day** (enough for several full runs daily)

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Add your API key & run

**Option A — Edit app.py directly (easiest)**
Open `app.py` and replace line 14:
```python
GNEWS_API_KEY = "YOUR_GNEWS_API_KEY_HERE"
```
with:
```python
GNEWS_API_KEY = "your_actual_key_here"
```
Then run:
```bash
python app.py
```

**Option B — Environment variable (safer for GitHub)**
```bash
# Windows
set GNEWS_API_KEY=your_key_here
python app.py

# Mac / Linux
export GNEWS_API_KEY=your_key_here
python app.py
```

**Then open:** http://localhost:5000

---

## 🗂️ Project Structure

```
daily-intelligence/
├── app.py            ← Everything: Flask server + HTML template + news fetcher
├── requirements.txt  ← flask, requests
└── README.md         ← This file
```

No templates folder. No static folder. Just one Python file.

---

## 📑 News Sections

| Page | Coverage |
|---|---|
| Defence & Security | Military operations, strategic affairs, national security |
| Business & Markets | Stock markets, trade, corporate news, economy |
| Technology | AI, startups, cybersecurity, software |
| World Affairs | Geopolitics, diplomacy, international relations |
| Politics & Governance | Elections, policy, parliament |
| Science & Environment | Research, climate, space, discoveries |
| Sports | Cricket, football, Olympics, championships |
| Health & Medicine | Medical research, public health, disease |

---

## ⚠️ Important for GitHub

**Do NOT commit your API key.** Use the environment variable method (Option B above).

Add this to `.gitignore` if you create a config file:
```
.env
config_local.py
```

---

## 🔧 Add More Sections

Edit the `SECTIONS` list in `app.py`:

```python
{"id": "entertainment", "label": "Entertainment", "kicker": "Arts & Culture",
 "topic": "entertainment", "query": None,
 "head": "ENTERTAINMENT", "sub": "Film, music, arts & cultural affairs"},
```

GNews supported topics: `breaking-news`, `world`, `nation`, `business`, `technology`, `entertainment`, `sports`, `science`, `health`

---

MIT License
