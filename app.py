from flask import Flask, render_template, request, jsonify
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)

PRESETS = {
    "nifty10":  ["RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","HINDUNILVR","BHARTIARTL","ITC","SBIN","KOTAKBANK"],
    "banking":  ["HDFCBANK","ICICIBANK","SBIN","KOTAKBANK","AXISBANK","INDUSINDBK","BANDHANBNK","FEDERALBNK"],
    "it":       ["TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM","MPHASIS","COFORGE"],
    "fmcg":     ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR","MARICO","COLPAL"],
    "auto":     ["TATAMOTORS","MARUTI","M&M","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","ASHOKLEY","TVSMOTOR"],
    "pharma":   ["SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","AUROPHARMA","TORNTPHARM"],
    "metals":   ["TATASTEEL","JSWSTEEL","HINDALCO","SAIL","VEDL","NMDC","COALINDIA"],
}

def get_default_week():
    today = datetime.today()
    offset = today.weekday()
    monday = today - timedelta(days=offset + 7)
    friday = monday + timedelta(days=4)
    return monday.date(), friday.date()

def fetch_and_analyze(symbol, start, end):
    ticker = f"{symbol}.NS"
    end_ex = end + timedelta(days=1)
    try:
        df = yf.download(ticker, start=str(start), end=str(end_ex),
                         interval="1d", progress=False, auto_adjust=True)
        if df is None or df.empty:
            return None
    except Exception:
        return None

    closes  = df["Close"].squeeze().tolist()
    opens   = df["Open"].squeeze().tolist()
    highs   = df["High"].squeeze().tolist()
    lows    = df["Low"].squeeze().tolist()
    volumes = df["Volume"].squeeze().tolist()
    dates   = [str(d.date()) for d in df.index.tolist()]

    if len(closes) == 0:
        return None

    daily_changes = []
    for i in range(len(closes)):
        ref = opens[0] if i == 0 else closes[i-1]
        pct = ((closes[i] - ref) / ref * 100) if ref else 0
        daily_changes.append(round(pct, 2))

    weekly_change = round(((closes[-1] - closes[0]) / closes[0]) * 100, 2) if closes[0] else 0
    max_dip       = round(min(daily_changes), 2)
    intraday      = [round(((h - l) / o) * 100, 2) for h, l, o in zip(highs, lows, opens) if o]
    max_swing     = round(max(intraday), 2) if intraday else 0
    support       = round(min(lows), 2)
    resistance    = round(max(highs), 2)
    avg_vol       = sum(volumes) / len(volumes) if volumes else 0
    vol_spike     = any(v > 1.5 * avg_vol for v in volumes)
    last_close    = round(closes[-1], 2)
    near_support  = abs(last_close - support) / support < 0.015 if support else False
    near_res      = abs(last_close - resistance) / resistance < 0.015 if resistance else False
    day_names     = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    day_labels    = [day_names[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in dates]

    return {
        "symbol":         symbol,
        "last_close":     last_close,
        "weekly_change":  weekly_change,
        "max_dip":        max_dip,
        "max_swing":      max_swing,
        "support":        support,
        "resistance":     resistance,
        "volume_spike":   vol_spike,
        "near_support":   near_support,
        "near_resistance": near_res,
        "daily_changes":  daily_changes,
        "day_labels":     day_labels,
        "dates":          dates,
        "closes":         [round(c, 2) for c in closes],
    }

@app.route("/")
def index():
    mon, fri = get_default_week()
    return render_template("index.html",
                           presets=list(PRESETS.keys()),
                           default_start=str(mon),
                           default_end=str(fri))

@app.route("/analyze", methods=["POST"])
def analyze():
    data       = request.get_json()
    symbols    = [s.strip().upper() for s in data.get("symbols", []) if s.strip()]
    week_start = datetime.strptime(data["week_start"], "%Y-%m-%d").date()
    week_end   = datetime.strptime(data["week_end"],   "%Y-%m-%d").date()

    results, failed = [], []
    for sym in symbols:
        r = fetch_and_analyze(sym, week_start, week_end)
        if r:
            results.append(r)
        else:
            failed.append(sym)

    return jsonify({"results": results, "failed": failed})

@app.route("/preset/<name>")
def preset(name):
    return jsonify({"symbols": PRESETS.get(name, [])})

if __name__ == "__main__":
    app.run(debug=True)
