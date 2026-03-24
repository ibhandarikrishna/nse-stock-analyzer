# NSE Stock Swing & Dip Analyzer
Real NSE data via Yahoo Finance. Free to host. No API key needed.

---

## 🚀 Deploy FREE on Render (5 min, no credit card)

### Step 1 — Upload to GitHub
1. Go to https://github.com → click **New repository**
2. Name it `nse-stock-analyzer` → click **Create repository**
3. Upload ALL files from this folder:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `templates/index.html`  ← make sure this is inside a `templates/` folder

### Step 2 — Deploy on Render
1. Go to https://render.com → Sign up free (use GitHub login)
2. Click **New +** → **Web Service**
3. Click **Connect a repository** → pick `nse-stock-analyzer`
4. Render will auto-detect the settings from `render.yaml`
5. Click **Deploy** — takes ~2 minutes
6. You'll get a live URL like: `https://nse-stock-analyzer.onrender.com`

That's it! Share the link with anyone.

---

## 💻 Run Locally

```bash
pip install -r requirements.txt
python app.py
```
Then open http://localhost:5000

---

## 📁 File structure

```
nse-stock-analyzer/
├── app.py                  # Flask backend (fetches Yahoo Finance data)
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deploy config
└── templates/
    └── index.html          # Web UI
```

---

## ⚠️ Notes
- Render free tier **sleeps after 15 min of inactivity** — first load after sleep takes ~30 sec to wake up
- Yahoo Finance data may have 15-min delay for live prices
- For NSE stocks, symbols are auto-appended with `.NS` (e.g. RELIANCE → RELIANCE.NS)
- Weekend dates return no data (markets closed)
