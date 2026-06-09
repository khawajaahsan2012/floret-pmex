"""
Floret Capitals — Newsletter Generator
Streamlit app: team enters PKR rates + central bank rates, everything else is auto-fetched.
Run: streamlit run newsletter_app.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import warnings, base64, re

warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Floret Capitals — PMEX Newsletter Generator",
    page_icon="https://floretcapitals.com/wp-content/uploads/2024/10/cropped-Floret-Icon-150x150.png",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&family=Karla:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
    /* Base font */
    html, body, [class*="css"] {
        font-family: 'Karla', sans-serif !important;
    }

    /* Force light theme */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    [data-testid="stMain"],
    [data-testid="block-container"] {
        background-color: #F0F2F5 !important;
        color: #111827 !important;
    }

    /* All text */
    p, span, label, div, h1, h2, h3, h4, li, a {
        color: #111827 !important;
        font-family: 'Karla', sans-serif !important;
    }

    /* Inputs */
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    input[type="number"], input[type="text"] {
        background-color: #FAFAFA !important;
        color: #111827 !important;
        border: 1px solid #DADBDD !important;
        border-radius: 7px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 14px !important;
    }

    /* Labels */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] > div,
    [data-testid="stDateInput"] label,
    [data-testid="stNumberInput"] label { color: #374151 !important; font-weight: 600 !important; }

    /* Radio */
    [data-testid="stRadio"] > div > label > div:first-child > div {
        border-color: #E39E3D !important;
    }

    /* Primary button */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #E39E3D, #F5B855) !important;
        color: #1A1A2E !important;
        font-weight: 700 !important;
        font-family: 'Rubik', sans-serif !important;
        font-size: 14px !important;
        letter-spacing: .05em !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 24px !important;
        box-shadow: 0 2px 8px rgba(227,158,61,.35) !important;
    }
    [data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #F5B855, #E39E3D) !important;
        box-shadow: 0 4px 16px rgba(227,158,61,.5) !important;
    }

    /* Download button */
    [data-testid="stDownloadButton"] > button {
        background: #1A1A2E !important;
        color: #E39E3D !important;
        font-weight: 700 !important;
        font-family: 'Rubik', sans-serif !important;
        border: 1px solid #E39E3D !important;
        border-radius: 6px !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
    }

    /* Divider */
    hr { border-color: #E5E7EB !important; margin: 16px 0 !important; }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }

    /* ── Custom components ── */
    .fc-topbar {
        background: #1A1A2E;
        padding: 0;
        margin: -1rem -1rem 0 -1rem;
        border-bottom: 3px solid #E39E3D;
    }
    .fc-topbar-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 32px;
    }
    .fc-logo-row { display: flex; align-items: center; gap: 14px; }
    .fc-brand-name {
        font-family: 'Rubik', sans-serif !important;
        font-size: 20px; font-weight: 700;
        color: #FFFFFF !important; letter-spacing: .04em;
    }
    .fc-brand-name span { color: #E39E3D !important; }
    .fc-brand-tag {
        font-size: 9px; font-weight: 600; letter-spacing: .18em;
        text-transform: uppercase; color: rgba(255,255,255,.4) !important;
        margin-top: 2px;
    }
    .fc-topbar-right {
        display: flex; align-items: center; gap: 24px;
    }
    .fc-topbar-stat { text-align: center; }
    .fc-topbar-stat-val {
        font-family: 'Rubik', sans-serif !important;
        font-size: 18px; font-weight: 700; color: #E39E3D !important; line-height: 1.1;
    }
    .fc-topbar-stat-lbl {
        font-size: 9px; font-weight: 500; letter-spacing: .1em;
        text-transform: uppercase; color: rgba(255,255,255,.4) !important;
    }
    .fc-topbar-divider {
        width: 1px; height: 36px; background: rgba(255,255,255,.1);
    }
    .fc-secp-badge {
        background: rgba(227,158,61,.12); border: 1px solid rgba(227,158,61,.3);
        padding: 5px 12px; border-radius: 4px;
        font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
        color: #E39E3D !important;
    }

    .fc-amber-strip {
        height: 3px;
        background: linear-gradient(90deg, #CC1818 0%, #E39E3D 40%, #F5B855 100%);
        margin: 0 -1rem 24px -1rem;
    }

    .fc-section-label {
        font-size: 10px !important; font-weight: 700 !important;
        letter-spacing: .18em; text-transform: uppercase;
        color: #E39E3D !important; margin-bottom: 10px; display: block;
    }

    .fc-form-panel {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 12px;
    }
    .fc-form-panel-title {
        font-family: 'Rubik', sans-serif !important;
        font-size: 13px; font-weight: 600;
        color: #1A1A2E !important; margin-bottom: 14px;
        padding-bottom: 10px; border-bottom: 1px solid #F3F4F6;
        display: flex; align-items: center; gap: 8px;
    }
    .fc-form-panel-title .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #E39E3D; display: inline-block;
    }

    .fc-ready-panel {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 48px 32px;
        text-align: center;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .fc-ready-title {
        font-family: 'Rubik', sans-serif !important;
        font-size: 22px; font-weight: 700;
        color: #1A1A2E !important; margin: 20px 0 8px;
    }
    .fc-ready-sub {
        font-size: 13px; color: #6B7280 !important; line-height: 1.7; max-width: 380px;
    }
    .fc-ready-pills {
        display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 20px;
    }
    .fc-ready-pill {
        font-size: 10px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
        padding: 4px 12px; border: 1px solid #E5E7EB;
        color: #6B7280 !important; background: #F9FAFB; border-radius: 20px;
    }
    .fc-ready-pill.active {
        background: rgba(227,158,61,.1); border-color: #E39E3D;
        color: #92400E !important;
    }
    .fc-features {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
        margin-top: 28px; width: 100%; max-width: 440px;
    }
    .fc-feature {
        background: #F9FAFB; border: 1px solid #F0F0F0; border-radius: 6px;
        padding: 12px 14px; text-align: left;
    }
    .fc-feature-icon { font-size: 18px; margin-bottom: 4px; }
    .fc-feature-title {
        font-family: 'Rubik', sans-serif !important;
        font-size: 12px; font-weight: 600; color: #1A1A2E !important;
    }
    .fc-feature-desc { font-size: 11px; color: #6B7280 !important; margin-top: 2px; }

    .fc-status-ok {
        background: #DCFCE7; border: 1px solid #16A34A; border-radius: 6px;
        padding: 10px 16px; color: #166534 !important; font-size: 13px; margin-bottom: 14px;
        display: flex; align-items: center; gap: 8px;
    }
    .fc-status-warn {
        background: #FEF3C7; border: 1px solid #D97706; border-radius: 6px;
        padding: 10px 16px; color: #92400E !important; font-size: 13px; margin-bottom: 14px;
    }

    .fc-contact-bar {
        background: #1A1A2E; border-radius: 6px; padding: 12px 18px;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 12px;
    }
    .fc-contact-bar span { color: rgba(255,255,255,.5) !important; font-size: 11px; }
    .fc-contact-bar strong { color: #E39E3D !important; }
</style>
""", unsafe_allow_html=True)

# ── Top navigation bar ─────────────────────────────────────────────────────────
st.markdown("""
<div class="fc-topbar">
  <div class="fc-topbar-inner">
    <div class="fc-logo-row">
      <img src="https://floretcapitals.com/wp-content/uploads/2024/10/cropped-cropped-Floret-Icon-80x76.png"
           width="38" height="36" alt="Floret Capitals"
           onerror="this.style.display='none'"/>
      <div>
        <div class="fc-brand-name">FLORET <span>CAPITALS</span></div>
        <div class="fc-brand-tag">PMEX Division · Research Tool</div>
      </div>
    </div>
    <div class="fc-topbar-right">
      <div class="fc-topbar-stat">
        <div class="fc-topbar-stat-val">12,000+</div>
        <div class="fc-topbar-stat-lbl">Clients</div>
      </div>
      <div class="fc-topbar-divider"></div>
      <div class="fc-topbar-stat">
        <div class="fc-topbar-stat-val">10+</div>
        <div class="fc-topbar-stat-lbl">Years</div>
      </div>
      <div class="fc-topbar-divider"></div>
      <div class="fc-topbar-stat">
        <div class="fc-topbar-stat-val">26</div>
        <div class="fc-topbar-stat-lbl">Countries</div>
      </div>
      <div class="fc-topbar-divider"></div>
      <div class="fc-secp-badge">✓ SECP Licensed</div>
    </div>
  </div>
</div>
<div class="fc-amber-strip"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA FETCHING
# ══════════════════════════════════════════════════════════════════════════════

TICKERS = {
    "gold":    "GC=F",
    "silver":  "SI=F",
    "wti":     "CL=F",
    "brent":   "BZ=F",
    "natgas":  "NG=F",
    "copper":  "HG=F",
    "sp500":   "^GSPC",
    "nasdaq":  "^NDX",
    "vix":     "^VIX",
    "dxy":     "DX-Y.NYB",
    "us10y":   "^TNX",
    "eurusd":  "EURUSD=X",
    "gbpusd":  "GBPUSD=X",
    "usdjpy":  "JPY=X",
    "usdchf":  "CHF=X",
    "audusd":  "AUDUSD=X",
    "usdcad":  "CAD=X",
    "usdcny":  "CNY=X",
    "eurgbp":  "EURGBP=X",
}

def compute_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_g = gain.ewm(com=period - 1, adjust=False).mean()
    avg_l = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_g / avg_l.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).iloc[-1]

def compute_50dma(series):
    if len(series) >= 50:
        return series.rolling(50).mean().iloc[-1]
    return series.mean()

def bias_label(price, dma, rsi):
    above = price > dma
    if rsi >= 70:
        return "OVERBOUGHT"
    if rsi <= 30:
        return "OVERSOLD"
    return "BULLISH" if above else "BEARISH"

def intraday_levels(df):
    last  = df.iloc[-1]
    hi, lo, cl = last["High"], last["Low"], last["Close"]
    pivot = (hi + lo + cl) / 3
    res   = 2 * pivot - lo
    sup   = 2 * pivot - hi
    return round(sup, 4), round(res, 4), round(pivot, 4)

def weekly_levels(df):
    recent = df.tail(5)
    sup = recent["Low"].min()
    res = recent["High"].max()
    return round(sup, 4), round(res, 4)

def pct_chg(df):
    if len(df) < 2:
        return 0.0
    return ((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]) * 100

def sparkline_path(df, width=100, height=26):
    prices = df["Close"].tail(20).values
    if len(prices) < 2:
        return ""
    mn, mx = prices.min(), prices.max()
    rng = mx - mn if mx != mn else 1
    xs = np.linspace(0, width, len(prices))
    ys = height - ((prices - mn) / rng) * (height - 4) - 2
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    return pts

@st.cache_data(ttl=300)
def fetch_all():
    data = {}
    errors = []
    for key, ticker in TICKERS.items():
        try:
            df = yf.Ticker(ticker).history(period="3mo", interval="1d")
            if df.empty:
                errors.append(key)
                continue
            df.index = pd.to_datetime(df.index)
            data[key] = df
        except Exception as e:
            errors.append(key)
    return data, errors

def get_val(data, key, field="Close"):
    df = data.get(key)
    if df is None or df.empty:
        return None
    return df[field].iloc[-1]

def get_prev(data, key):
    df = data.get(key)
    if df is None or len(df) < 2:
        return None
    return df["Close"].iloc[-2]

# ══════════════════════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════════════════════

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    # Edition type panel
    st.markdown("""
    <div class="fc-form-panel">
      <div class="fc-form-panel-title"><span class="dot"></span> Edition Settings</div>
    </div>
    """, unsafe_allow_html=True)

    edition_type = st.radio("Edition Type", ["Daily", "Weekly"], horizontal=True)
    edition_date = st.date_input("Edition Date", value=date.today())

    if edition_type == "Weekly":
        c1, c2 = st.columns(2)
        with c1:
            cal_start = st.date_input("Week Start", value=date.today())
        with c2:
            cal_end = st.date_input("Week End", value=date.today() + timedelta(days=6))
        cal_window = f"Week of {cal_start.strftime('%b %-d')} – {cal_end.strftime('%b %-d, %Y')}"
    else:
        cal_window = edition_date.strftime("%B %-d, %Y")

    st.markdown("---")

    # PKR rates panel
    st.markdown("""
    <div class="fc-form-panel" style="margin-bottom:8px;">
      <div class="fc-form-panel-title"><span class="dot"></span> PKR Exchange Rates</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<span class="fc-section-label">Enter today\'s interbank rates</span>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        usd_pkr = st.number_input("USD / PKR", value=278.50, format="%.2f")
        gbp_pkr = st.number_input("GBP / PKR", value=355.72, format="%.2f")
    with c2:
        eur_pkr = st.number_input("EUR / PKR", value=316.05, format="%.2f")
        sar_pkr = st.number_input("SAR / PKR", value=74.27,  format="%.2f")

    aed_pkr = round(usd_pkr / 3.6725, 2)

    if edition_type == "Weekly":
        st.markdown("---")
        st.markdown("""
        <div class="fc-form-panel" style="margin-bottom:8px;">
          <div class="fc-form-panel-title"><span class="dot"></span> Central Bank Rates</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<span class="fc-section-label">Current policy rates</span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fed_rate = st.number_input("FED (%)", value=4.50, step=0.25, format="%.2f")
            boj_rate = st.number_input("BOJ (%)", value=0.75, step=0.25, format="%.2f")
        with c2:
            ecb_rate = st.number_input("ECB (%)", value=2.00, step=0.25, format="%.2f")
            sbp_rate = st.number_input("SBP (%)", value=12.0, step=0.25, format="%.2f")
    else:
        fed_rate, ecb_rate, boj_rate, sbp_rate = 4.50, 2.00, 0.75, 12.0

    st.markdown("---")

    # Contact bar
    st.markdown("""
    <div class="fc-contact-bar">
      <span>📞 <strong>+92 311 1000183</strong></span>
      <span>contact@floretcapitals.com</span>
    </div>
    """, unsafe_allow_html=True)

    generate_btn = st.button("🚀 Generate Newsletter", type="primary", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════════════════════════

with col_right:
    if generate_btn:
        with st.spinner("Fetching live market data…"):
            data, errors = fetch_all()

        if errors:
            st.markdown(f'<div class="fc-status-warn">⚠️ Could not fetch: {", ".join(errors)} — using placeholder values.</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="fc-status-ok">✅ Live data fetched · {len(data)} instruments loaded · {datetime.now().strftime("%H:%M PKT")}</div>', unsafe_allow_html=True)

        # ── Live prices ──
        def safe(key, fallback=0.0, field="Close"):
            v = get_val(data, key, field)
            return float(v) if v is not None else fallback

        gold_p    = safe("gold",   4351.40)
        silver_p  = safe("silver",   68.55)
        wti_p     = safe("wti",      89.72)
        brent_p   = safe("brent",    93.02)
        natgas_p  = safe("natgas",    3.184)
        copper_p  = safe("copper",    6.378)
        sp_p      = safe("sp500",  7405.73)
        nq_p      = safe("nasdaq",29414.26)
        vix_p     = safe("vix",      18.2)
        dxy_p     = safe("dxy",      99.9)
        us10y_p   = safe("us10y",     4.55)

        gold_chg   = pct_chg(data["gold"])   if "gold"   in data else 0.36
        silver_chg = pct_chg(data["silver"]) if "silver" in data else 0.18
        wti_chg    = pct_chg(data["wti"])    if "wti"    in data else -1.73
        brent_chg  = pct_chg(data["brent"])  if "brent"  in data else -1.31
        natgas_chg = pct_chg(data["natgas"]) if "natgas" in data else 1.18
        copper_chg = pct_chg(data["copper"]) if "copper" in data else 0.77
        sp_chg     = pct_chg(data["sp500"])  if "sp500"  in data else 0.30
        nq_chg     = pct_chg(data["nasdaq"]) if "nasdaq" in data else 1.58

        gs_ratio   = round(gold_p / silver_p, 1) if silver_p else 63.5

        # FX
        eurusd_p = safe("eurusd", 1.1542)
        gbpusd_p = safe("gbpusd", 1.3369)
        usdjpy_p = safe("usdjpy", 160.20)
        usdchf_p = safe("usdchf", 0.7972)
        audusd_p = safe("audusd", 0.7050)
        usdcad_p = safe("usdcad", 1.3940)
        usdcny_p = safe("usdcny", 6.7721)
        eurgbp_p = safe("eurgbp", 0.8630)

        def prev_safe(key, fallback):
            v = get_prev(data, key)
            return float(v) if v is not None else fallback

        eurusd_prev = prev_safe("eurusd", 1.1523)
        gbpusd_prev = prev_safe("gbpusd", 1.3336)
        usdjpy_prev = prev_safe("usdjpy", 160.33)
        usdchf_prev = prev_safe("usdchf", 0.7964)
        audusd_prev = prev_safe("audusd", 0.7043)
        usdcad_prev = prev_safe("usdcad", 1.3944)
        usdcny_prev = prev_safe("usdcny", 6.7655)
        eurgbp_prev = prev_safe("eurgbp", 0.8640)

        # ── Technicals ──
        def tech(key, fallback_price):
            df = data.get(key)
            if df is None or len(df) < 15:
                p = fallback_price
                return {"rsi": 50, "dma50": p, "bias": "NEUTRAL", "sup": round(p * 0.98, 4), "res": round(p * 1.02, 4), "pivot": round(p, 4)}
            p    = df["Close"].iloc[-1]
            rsi  = compute_rsi(df["Close"])
            dma  = compute_50dma(df["Close"])
            bias = bias_label(p, dma, rsi)
            if edition_type == "Weekly":
                sup, res = weekly_levels(df)
                pivot    = round((sup + res + p) / 3, 4)
            else:
                sup, res, pivot = intraday_levels(df)
            return {"rsi": round(rsi, 1), "dma50": round(dma, 4), "bias": bias, "sup": sup, "res": res, "pivot": pivot}

        T = {
            "gold":   tech("gold",   gold_p),
            "wti":    tech("wti",    wti_p),
            "silver": tech("silver", silver_p),
            "natgas": tech("natgas", natgas_p),
            "sp500":  tech("sp500",  sp_p),
            "nasdaq": tech("nasdaq", nq_p),
            "eurusd": tech("eurusd", eurusd_p),
            "usdjpy": tech("usdjpy", usdjpy_p),
        }

        def bias_badge(b):
            cls = {"BULLISH":"badge-bull","BEARISH":"badge-bear","OVERSOLD":"badge-watch","OVERBOUGHT":"badge-bear","NEUTRAL":"badge-neut"}.get(b,"badge-neut")
            return f'<span class="a-badge {cls}">{b}</span>'

        def chg_str(c):
            return f"▲ +{c:.2f}%" if c >= 0 else f"▼ {c:.2f}%"

        def chg_cls(c):
            return "up" if c >= 0 else "dn"

        def spark_svg(key, color="#E39E3D"):
            df = data.get(key)
            if df is None:
                return ""
            pts = sparkline_path(df)
            if not pts:
                return ""
            stroke = color
            return f"""
            <svg class="sparkline" viewBox="0 0 100 26" preserveAspectRatio="none">
              <defs><linearGradient id="sl_{key}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="{stroke}" stop-opacity=".3"/>
                <stop offset="100%" stop-color="{stroke}" stop-opacity="0"/>
              </linearGradient></defs>
              <polyline points="{pts} 100,26 0,26" fill="url(#sl_{key})"/>
              <polyline points="{pts}" stroke="{stroke}" stroke-width="1.5" fill="none"/>
            </svg>"""

        def fx_spark(key, up=True):
            color = "#16A34A" if up else "#DC2626"
            return spark_svg(key, color)

        def fx_chg_badge(live, prev):
            diff = live - prev
            cls  = "up" if diff >= 0 else "dn"
            sym  = "▲" if diff >= 0 else "▼"
            return f'<span class="fx-badge {cls}">{sym} {abs(diff):.4f}</span>'

        def fx_3m_range(key):
            df = data.get(key)
            if df is None or df.empty:
                return "—"
            mn = df["Close"].min()
            mx = df["Close"].max()
            return f"{mn:.4f}–{mx:.4f}"

        # ── Determine session status ──
        now_hour = datetime.utcnow().hour
        now_pkt  = (now_hour + 5) % 24
        sessions = {
            "sydney":  (2,  11),
            "tokyo":   (5,  14),
            "london":  (13, 22),
            "newyork": (18, 3),
        }
        def sess_active(name):
            s, e = sessions[name]
            if s < e:
                return s <= now_pkt < e
            return now_pkt >= s or now_pkt < e

        sess_dot = lambda n: "● ACTIVE NOW" if sess_active(n) else "● CLOSED"
        sess_cls = lambda n: "active-session" if sess_active(n) else ""

        # ── Strategy corner ──
        def strategy_corner():
            oversold = [k for k, v in T.items() if v["bias"] in ("OVERSOLD",)]
            overbought = [k for k, v in T.items() if v["bias"] == "OVERBOUGHT"]
            bearish = [k for k, v in T.items() if v["bias"] == "BEARISH"]

            if wti_chg < -1.0:
                title = "Crude Oversold — Mean-Reversion Watch"
                body  = "Crude is oversold — be cautious chasing shorts and watch for a snapback:"
            elif gold_chg > 0.5:
                title = "Gold Breaking Higher — Momentum Play"
                body  = "Gold is gaining momentum above key levels — consider adding on dips:"
            else:
                title = f"{'High-Impact Events This Week' if edition_type == 'Weekly' else 'Quiet Session — Be Selective'}"
                body  = "No dominant directional theme — size down and be selective:"

            lvl_word = "weekly" if edition_type == "Weekly" else "intraday"
            return title, body, f"""
            <li>Gold GO1OZ: Trend {'soft' if T['gold']['bias']=='BEARISH' else 'constructive'} — be selective; watch ${T['gold']['sup']:,.2f} support. Margin 5.75%.</li>
            <li>WTI CRUDE10: {'Under pressure' if wti_chg < 0 else 'Recovering'} — rallies toward ${T['wti']['res']:,.2f} may offer {'shorts' if wti_chg < 0 else 'longs'}. Margin 17%.</li>
            <li>Silver SL10: Gold/Silver ratio at {gs_ratio}x. Support ${T['silver']['sup']:,.2f}, resistance ${T['silver']['res']:,.2f}.</li>
            <li>Risk management: Widen stops 20–30% around high-impact releases. Size to PMEX margins shown in specs. Avoid max leverage in volatile windows.</li>"""

        strat_title, strat_body, strat_bullets = strategy_corner()

        ed_label   = "WEEKLY INTELLIGENCE" if edition_type == "Weekly" else "DAILY INTELLIGENCE"
        brief_type = "Weekly" if edition_type == "Weekly" else "Daily"
        date_str   = edition_date.strftime("%B %-d, %Y")
        date_short = edition_date.strftime("%-d %b %Y")
        now_str    = datetime.now().strftime("%-d %b %Y, %H:%M")

        def fmt_p(v, decimals=2):
            if v >= 1000:
                return f"{v:,.2f}"
            if v >= 10:
                return f"{v:.2f}"
            return f"{v:.{decimals}f}"

        # ── HTML ──────────────────────────────────────────────────────────────
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Floret Capitals — PMEX {brief_type} Intelligence · {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&family=Karla:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
:root{{
  --amber:#E39E3D;--amber2:#F5B855;--amber3:#FDE8BC;
  --red:#CC1818;--red2:#E53535;--red3:#FEE2E2;
  --grey:#69727D;--grey2:#F4F5F6;--grey3:#E8EAEC;--grey4:#D1D5DB;
  --dark:#1A1A2E;--dark2:#252540;--text:#111827;--text2:#374151;
  --muted:#6B7280;--green:#16A34A;--green2:#DCFCE7;
  --neg:#DC2626;--neg2:#FEE2E2;--white:#FFFFFF;--border:#E5E7EB;
  --serif:'Rubik',sans-serif;--body:'Karla',sans-serif;--mono:'DM Mono',monospace;
}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
body{{background:#F0F2F5;font-family:var(--body);color:var(--text);width:794px;margin:0 auto;padding:0;font-size:14px;line-height:1.6;}}

/* HERO */
.hero{{background:var(--dark);position:relative;overflow:hidden;padding:0;}}
.hero-pattern{{position:absolute;inset:0;background-image:radial-gradient(circle at 15% 50%,rgba(227,158,61,.12) 0%,transparent 50%),radial-gradient(circle at 85% 20%,rgba(204,24,24,.08) 0%,transparent 45%);pointer-events:none;}}
.hero-grid-bg{{position:absolute;inset:0;background-image:linear-gradient(rgba(227,158,61,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(227,158,61,.05) 1px,transparent 1px);background-size:36px 36px;pointer-events:none;}}
.hero-inner{{position:relative;z-index:2;display:flex;align-items:stretch;min-height:180px;}}
.hero-left{{flex:1;padding:28px 36px;display:flex;flex-direction:column;justify-content:center;}}
.logo-row{{display:flex;align-items:center;gap:14px;margin-bottom:10px;}}
.logo-img{{width:44px;height:auto;filter:brightness(1.1);}}
.brand-name{{font-family:var(--serif);font-size:24px;font-weight:700;color:var(--white);letter-spacing:.03em;line-height:1.1;}}
.brand-name span{{color:var(--amber);}}
.brand-tagline{{font-size:10px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.45);margin-top:3px;}}
.hero-headline{{font-family:var(--serif);font-size:15px;font-weight:400;color:rgba(255,255,255,.75);line-height:1.6;margin-bottom:16px;max-width:360px;}}
.hero-headline strong{{color:var(--amber2);font-weight:600;}}
.hero-pills{{display:flex;gap:8px;flex-wrap:wrap;}}
.hero-pill{{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;padding:4px 10px;border:1px solid rgba(227,158,61,.35);color:rgba(255,255,255,.6);background:rgba(227,158,61,.06);}}
.hero-pill.active{{background:var(--amber);color:var(--dark);border-color:var(--amber);}}
.hero-right{{width:240px;flex-shrink:0;padding:16px 16px 16px 0;display:flex;align-items:center;}}
.amber-strip{{height:4px;background:linear-gradient(90deg,var(--red) 0%,var(--amber) 40%,var(--amber2) 100%);}}
.edition-bar{{background:var(--dark2);padding:8px 36px;display:flex;align-items:center;justify-content:space-between;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.4);}}
.edition-bar .em{{color:var(--amber);font-weight:600;}}
.edition-sep{{color:rgba(255,255,255,.15);}}

/* BODY */
.body-wrap{{background:var(--white);padding:28px 32px 24px;}}

/* Section heads */
.sec-head{{display:flex;align-items:center;gap:12px;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid var(--grey3);position:relative;}}
.sec-head::after{{content:'';position:absolute;bottom:-2px;left:0;width:40px;height:2px;background:var(--amber);}}
.sec-tag{{font-size:9px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;background:var(--amber);color:var(--dark);padding:3px 8px;}}
.sec-title{{font-family:var(--serif);font-size:16px;font-weight:600;color:var(--dark);}}
.sec-meta{{margin-left:auto;font-size:10px;color:var(--muted);letter-spacing:.06em;}}
.mb-section{{margin-bottom:24px;}}

/* PKR RATES STRIP */
.pkr-strip{{display:grid;grid-template-columns:repeat(5,1fr);gap:0;border:1px solid var(--border);margin-bottom:24px;}}
.pkr-cell{{padding:12px 10px;text-align:center;border-right:1px solid var(--border);}}
.pkr-cell:last-child{{border-right:none;}}
.pkr-pair{{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;}}
.pkr-val{{font-family:var(--mono);font-size:16px;font-weight:600;color:var(--dark);}}
.pkr-tag{{display:inline-block;font-size:8px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:var(--green2);color:var(--green);padding:1px 5px;margin-top:3px;}}

/* SNAPSHOT */
.snap-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:24px;}}
.snap-card{{background:var(--white);border:1px solid var(--border);border-top:3px solid var(--grey3);padding:12px 12px 8px;}}
.snap-card.up-card{{border-top-color:var(--green);}}
.snap-card.dn-card{{border-top-color:var(--neg);}}
.snap-row1{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3px;}}
.snap-name{{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);}}
.snap-chg{{font-size:10px;font-weight:700;font-family:var(--mono);padding:1px 5px;}}
.snap-chg.up{{background:var(--green2);color:var(--green);}}
.snap-chg.dn{{background:var(--neg2);color:var(--neg);}}
.snap-price{{font-family:var(--mono);font-size:15px;font-weight:500;color:var(--dark);}}
.snap-unit{{font-size:8px;color:var(--muted);margin-top:1px;}}
.sparkline{{width:100%;height:24px;margin-top:6px;display:block;}}

/* MACRO */
.macro-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:24px;}}
.macro-card{{border:1px solid var(--border);padding:12px;text-align:center;background:var(--grey2);}}
.macro-lbl{{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}}
.macro-val{{font-family:var(--mono);font-size:20px;font-weight:600;color:var(--dark);}}
.macro-sub{{font-size:9px;color:var(--muted);margin-top:3px;}}

/* FX TABLE */
.fx-table-wrap{{border:1px solid var(--border);overflow:hidden;margin-bottom:24px;}}
.fx-thead{{display:grid;grid-template-columns:110px 90px 80px 90px 1fr;background:var(--grey2);padding:7px 12px;border-bottom:1px solid var(--border);font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);gap:8px;}}
.fx-row{{display:grid;grid-template-columns:110px 90px 80px 90px 1fr;padding:8px 12px;border-bottom:1px solid var(--grey3);align-items:center;gap:8px;}}
.fx-row:last-child{{border-bottom:none;}}
.fx-row:nth-child(even){{background:rgba(244,245,246,.5);}}
.fx-pair{{font-weight:700;font-size:13px;color:var(--dark);letter-spacing:.04em;}}
.fx-rate{{font-family:var(--mono);font-size:12px;color:var(--text2);}}
.fx-badge{{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:700;padding:2px 6px;}}
.fx-badge.up{{background:var(--green2);color:var(--green);}}
.fx-badge.dn{{background:var(--neg2);color:var(--neg);}}
.fx-range{{font-size:10px;color:var(--muted);font-family:var(--mono);}}

/* CALENDAR */
.cal-table{{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:12px;}}
.cal-table thead tr{{background:var(--grey2);}}
.cal-table th{{padding:7px 10px;text-align:left;font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--border);}}
.cal-table td{{padding:7px 10px;border-bottom:1px solid var(--grey3);vertical-align:middle;}}
.cal-table tr:last-child td{{border-bottom:none;}}
.imp-h{{background:var(--neg2);color:var(--neg);font-size:8px;font-weight:700;padding:2px 6px;letter-spacing:.08em;}}
.imp-m{{background:#FEF3C7;color:#92400E;font-size:8px;font-weight:700;padding:2px 6px;}}
.imp-l{{background:#EFF6FF;color:#1D4ED8;font-size:8px;font-weight:700;padding:2px 6px;}}
.cal-quiet{{background:var(--grey2);border:1px solid var(--border);padding:16px;text-align:center;color:var(--muted);font-size:12px;margin-bottom:24px;}}

/* CENTRAL BANKS */
.cb-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:24px;}}
.cb-card{{border:1px solid var(--border);padding:14px;}}
.cb-name{{font-size:9px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}}
.cb-fullname{{font-family:var(--serif);font-size:12px;font-weight:600;color:var(--dark);margin-bottom:8px;}}
.cb-rate{{font-family:var(--mono);font-size:22px;font-weight:600;color:var(--amber);}}
.cb-stance{{display:inline-block;font-size:8px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:2px 6px;background:var(--green2);color:var(--green);margin-top:4px;}}
.cb-next{{font-size:10px;color:var(--muted);margin-top:6px;}}
.cb-note{{font-size:10px;color:var(--text2);margin-top:4px;line-height:1.5;}}

/* ANALYSIS CARDS */
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:24px;}}
.a-card{{border:1px solid var(--border);overflow:hidden;}}
.a-top-band{{height:4px;}}
.band-amber{{background:linear-gradient(90deg,var(--amber),var(--amber2));}}
.band-red{{background:linear-gradient(90deg,var(--red),var(--red2));}}
.band-blue{{background:linear-gradient(90deg,#1D4ED8,#3B82F6);}}
.band-green{{background:linear-gradient(90deg,#059669,#34D399);}}
.band-purp{{background:linear-gradient(90deg,#6D28D9,#8B5CF6);}}
.a-body{{padding:12px 14px;}}
.a-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;}}
.a-name{{font-family:var(--serif);font-size:14px;font-weight:600;color:var(--dark);}}
.a-sub{{font-size:9px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:2px;}}
.a-badge{{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:3px 8px;flex-shrink:0;}}
.badge-bull{{background:var(--green2);color:var(--green);}}
.badge-bear{{background:var(--neg2);color:var(--neg);}}
.badge-neut{{background:#FEF3C7;color:#92400E;}}
.badge-watch{{background:#EFF6FF;color:#1D4ED8;}}
.a-text{{font-size:11px;color:var(--text2);line-height:1.7;margin-bottom:8px;}}
.a-levels{{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin-top:8px;}}
.lv{{background:var(--grey2);border:1px solid var(--grey3);padding:5px 5px;text-align:center;}}
.lv-lbl{{font-size:7px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:2px;}}
.lv-val{{font-family:var(--mono);font-size:11px;font-weight:600;}}
.lv-res{{color:var(--neg);}}
.lv-sup{{color:var(--green);}}
.lv-spot{{color:var(--amber);}}
.lv-piv{{color:#3B82F6;}}

/* SIGNAL SUMMARY */
.signal-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:24px;}}
.sig-card{{border:1px solid var(--border);padding:14px;text-align:center;}}
.sig-name{{font-family:var(--serif);font-size:12px;font-weight:600;color:var(--dark);margin-bottom:2px;}}
.sig-sub{{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;}}
.sig-rsi{{font-family:var(--mono);font-size:22px;font-weight:600;margin-bottom:4px;}}
.sig-bias{{font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;}}

/* STRATEGY */
.strategy-box{{background:linear-gradient(135deg,#FFF9EF,#FFF3DC);border-left:4px solid var(--amber);padding:16px 20px;margin-bottom:24px;}}
.strat-header{{font-family:var(--serif);font-size:15px;font-weight:700;color:var(--dark);margin-bottom:4px;}}
.strat-sub{{font-size:11px;color:var(--text2);margin-bottom:10px;}}
.strat-list{{font-size:11.5px;color:var(--text2);line-height:1.9;padding-left:16px;}}

/* RISK */
.risk-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:24px;}}
.risk-card{{border:1px solid var(--border);padding:14px;}}
.risk-lbl{{font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;}}
.risk-val{{font-family:var(--mono);font-size:18px;font-weight:600;color:var(--dark);margin-bottom:6px;}}
.risk-bar-wrap{{background:var(--grey3);height:5px;border-radius:3px;overflow:hidden;}}
.risk-bar{{height:5px;border-radius:3px;}}
.risk-note{{font-size:10px;color:var(--muted);margin-top:6px;line-height:1.5;}}

/* CONTRACT SPECS */
.specs-table{{width:100%;border-collapse:collapse;margin-bottom:12px;font-size:11px;}}
.specs-table thead tr{{background:var(--dark);color:white;}}
.specs-table th{{padding:7px 8px;font-size:8.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;text-align:left;}}
.specs-table td{{padding:7px 8px;border-bottom:1px solid var(--grey3);}}
.specs-table tr:nth-child(even) td{{background:var(--grey2);}}
.specs-section-head{{font-family:var(--serif);font-size:13px;font-weight:600;color:var(--dark);padding:10px 0 4px;}}

/* SESSIONS */
.sess-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:24px;}}
.sess-card{{border:1px solid var(--border);padding:12px;text-align:center;}}
.sess-card.active-sess{{border-color:var(--amber);background:#FFFBF0;}}
.sess-name{{font-family:var(--serif);font-size:12px;font-weight:600;color:var(--dark);margin-bottom:2px;}}
.sess-time{{font-size:9px;font-family:var(--mono);color:var(--muted);margin-bottom:4px;}}
.sess-focus{{font-size:9px;color:var(--muted);margin-bottom:6px;}}
.sess-status{{font-size:10px;font-weight:700;}}
.sess-status.on{{color:var(--green);}} .sess-status.off{{color:var(--muted);}}

/* PULL */
.pull{{background:linear-gradient(135deg,#FFF9EF,#FFF3DC);border-left:4px solid var(--amber);padding:14px 18px;margin-bottom:24px;display:flex;gap:14px;align-items:flex-start;}}
.pull-icon{{width:30px;height:30px;background:var(--amber);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:14px;}}
.pull-text{{font-family:var(--serif);font-size:13px;font-style:italic;color:var(--text2);line-height:1.7;}}
.pull-source{{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--amber);margin-top:5px;}}

/* FOOTER */
.footer{{background:var(--dark);padding:20px 32px 16px;}}
.footer-top{{display:flex;align-items:center;justify-content:space-between;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:12px;}}
.footer-brand-name{{font-family:var(--serif);font-size:13px;font-weight:600;color:var(--amber);letter-spacing:.1em;}}
.footer-contact{{font-size:11px;color:rgba(255,255,255,.5);text-align:right;line-height:1.7;}}
.footer-contact strong{{color:var(--amber);font-weight:600;}}
.footer-disc{{font-size:9px;color:rgba(255,255,255,.3);line-height:1.7;max-width:680px;margin-bottom:12px;}}
.footer-links{{display:flex;align-items:center;gap:12px;font-size:9px;letter-spacing:.1em;text-transform:uppercase;}}
.footer-links a{{color:rgba(255,255,255,.35);text-decoration:none;}}
.footer-sep{{color:rgba(255,255,255,.12);}}
.copy{{font-size:9px;color:rgba(255,255,255,.2);margin-top:8px;letter-spacing:.06em;}}

@media print{{
  body{{width:794px;}}
  *{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
}}
</style>
</head>
<body>

<!-- HERO -->
<div class="hero">
  <div class="hero-pattern"></div>
  <div class="hero-grid-bg"></div>
  <div class="hero-inner">
    <div class="hero-left">
      <div class="logo-row">
        <img class="logo-img"
             src="https://floretcapitals.com/wp-content/uploads/2024/10/cropped-cropped-Floret-Icon-80x76.png"
             alt="Floret Capitals" onerror="this.style.display='none'"/>
        <div>
          <div class="brand-name">FLORET <span>CAPITALS</span></div>
          <div class="brand-tagline">SECP Licensed · PMEX Division · Pakistan</div>
        </div>
      </div>
      <div class="hero-headline">
        {'Your weekly <strong>Commodities &amp; Forex</strong> intelligence brief — covering PMEX markets from a Pakistani investor&apos;s perspective.' if edition_type == 'Weekly' else 'Your daily <strong>market snapshot</strong> — live prices, technicals and key events for PMEX traders.'}
      </div>
      <div class="hero-pills">
        <div class="hero-pill active">GOLD</div>
        <div class="hero-pill active">SILVER</div>
        <div class="hero-pill active">CRUDE</div>
        <div class="hero-pill active">FOREX</div>
        <div class="hero-pill active">PMEX</div>
      </div>
    </div>
    <div class="hero-right">
      <svg viewBox="0 0 220 140" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;">
        <defs>
          <linearGradient id="hg1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E39E3D" stop-opacity=".35"/><stop offset="100%" stop-color="#E39E3D" stop-opacity="0"/></linearGradient>
          <linearGradient id="hg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#CC1818" stop-opacity=".2"/><stop offset="100%" stop-color="#CC1818" stop-opacity="0"/></linearGradient>
        </defs>
        <line x1="0" y1="35" x2="220" y2="35" stroke="rgba(227,158,61,.1)" stroke-width="1"/>
        <line x1="0" y1="70" x2="220" y2="70" stroke="rgba(227,158,61,.1)" stroke-width="1"/>
        <line x1="0" y1="105" x2="220" y2="105" stroke="rgba(227,158,61,.1)" stroke-width="1"/>
        <path d="M0,100 L22,92 L44,97 L66,82 L88,74 L110,79 L132,63 L154,55 L176,47 L198,35 L220,24 L220,130 L0,130Z" fill="url(#hg1)"/>
        <path d="M0,100 L22,92 L44,97 L66,82 L88,74 L110,79 L132,63 L154,55 L176,47 L198,35 L220,24" stroke="#E39E3D" stroke-width="2" fill="none"/>
        <path d="M0,42 L22,46 L44,42 L66,50 L88,56 L110,52 L132,60 L154,66 L176,64 L198,72 L220,80 L220,130 L0,130Z" fill="url(#hg2)" opacity=".6"/>
        <path d="M0,42 L22,46 L44,42 L66,50 L88,56 L110,52 L132,60 L154,66 L176,64 L198,72 L220,80" stroke="#CC1818" stroke-width="1.5" fill="none" stroke-dasharray="5,3"/>
        <text x="180" y="20" font-size="8" fill="#E39E3D" font-family="DM Mono,monospace">GOLD ▲ {chg_str(gold_chg)}</text>
        <text x="180" y="77" font-size="8" fill="#CC1818" font-family="DM Mono,monospace">OIL {chg_str(wti_chg)}</text>
        <text x="2"   y="127" font-size="7" fill="rgba(227,158,61,.45)" font-family="DM Mono,monospace">3MO AGO</text>
        <text x="180" y="127" font-size="7" fill="rgba(227,158,61,.45)" font-family="DM Mono,monospace">{date_short}</text>
        <circle cx="220" cy="24" r="4" fill="#E39E3D"/>
        <circle cx="220" cy="24" r="7" fill="none" stroke="#E39E3D" stroke-width="1" opacity=".4"/>
        <circle cx="220" cy="80" r="3" fill="#CC1818" opacity=".8"/>
      </svg>
    </div>
  </div>
</div>

<div class="amber-strip"></div>
<div class="edition-bar">
  <div>PMEX {brief_type} Intelligence &nbsp;·&nbsp; <span class="em">{ed_label}</span></div>
  <div>SECP LICENSED <span class="edition-sep">|</span> <span class="em">LIVE: {now_str}</span></div>
  <div>floretcapitals.com</div>
</div>

<!-- BODY -->
<div class="body-wrap">

  <!-- EXECUTIVE SUMMARY -->
  <div class="pull" style="margin-bottom:20px;">
    <div class="pull-icon">■</div>
    <div>
      <div class="pull-text" style="font-style:normal;font-size:12px;line-height:1.8;">
        <strong style="color:var(--amber);">{brief_type.upper()} EXECUTIVE SUMMARY · AUTO-GENERATED FROM LIVE DATA</strong><br/>
        Gold <strong>${gold_p:,.2f}</strong> ({chg_str(gold_chg)}) — {'trend soft below 50-DMA.' if T['gold']['bias']=='BEARISH' else 'trend constructive above 50-DMA.'} GO1OZ AU26.<br/>
        WTI <strong>${wti_p:.2f}</strong> ({chg_str(wti_chg)}) — {'under pressure.' if wti_chg < 0 else 'gaining momentum.'} CRUDE10 JY26.<br/>
        DXY {dxy_p:.1f} · VIX {vix_p:.1f} — dollar &amp; volatility backdrop {'supportive' if dxy_p < 100 else 'headwind'} for commodities.<br/>
        Gold/Silver {gs_ratio}x · US 10Y {us10y_p:.2f}% — USD/PKR {usd_pkr:.2f}. Silver ${silver_p:.2f}.
      </div>
    </div>
  </div>

  <!-- PKR RATES -->
  <div class="sec-head mb-section">
    <span class="sec-tag">PKR Rates</span>
    <span class="sec-title">Rupee Exchange Rates</span>
    <span class="sec-meta">Interbank · {date_str}</span>
  </div>
  <div class="pkr-strip" style="margin-bottom:24px;">
    <div class="pkr-cell"><div class="pkr-pair">USD / PKR</div><div class="pkr-val">{usd_pkr:.2f}</div><div class="pkr-tag">entered</div></div>
    <div class="pkr-cell"><div class="pkr-pair">EUR / PKR</div><div class="pkr-val">{eur_pkr:.2f}</div><div class="pkr-tag">entered</div></div>
    <div class="pkr-cell"><div class="pkr-pair">GBP / PKR</div><div class="pkr-val">{gbp_pkr:.2f}</div><div class="pkr-tag">entered</div></div>
    <div class="pkr-cell"><div class="pkr-pair">SAR / PKR</div><div class="pkr-val">{sar_pkr:.2f}</div><div class="pkr-tag">entered</div></div>
    <div class="pkr-cell"><div class="pkr-pair">AED / PKR</div><div class="pkr-val">{aed_pkr:.2f}</div><div class="pkr-tag">derived</div></div>
  </div>

  <!-- MARKETS SNAPSHOT -->
  <div class="sec-head">
    <span class="sec-tag">Live Prices</span>
    <span class="sec-title">Markets Snapshot</span>
    <span class="sec-meta">Live · {now_str}</span>
  </div>
  <div class="snap-grid">
    <div class="snap-card {'up' if gold_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">GOLD (GO1OZ)</div><span class="snap-chg {'up' if gold_chg>=0 else 'dn'}">{chg_str(gold_chg)}</span></div>
      <div class="snap-price">${gold_p:,.2f}</div><div class="snap-unit">troy oz · GO1OZ AU26</div>
      {spark_svg("gold", "#E39E3D" if gold_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if silver_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">SILVER (SL10)</div><span class="snap-chg {'up' if silver_chg>=0 else 'dn'}">{chg_str(silver_chg)}</span></div>
      <div class="snap-price">${silver_p:.2f}</div><div class="snap-unit">troy oz · SL10 JY26</div>
      {spark_svg("silver", "#16A34A" if silver_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if wti_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">WTI (CRUDE10)</div><span class="snap-chg {'up' if wti_chg>=0 else 'dn'}">{chg_str(wti_chg)}</span></div>
      <div class="snap-price">${wti_p:.2f}</div><div class="snap-unit">barrel · CRUDE10 JY26</div>
      {spark_svg("wti", "#16A34A" if wti_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if brent_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">BRENT (BRENT10)</div><span class="snap-chg {'up' if brent_chg>=0 else 'dn'}">{chg_str(brent_chg)}</span></div>
      <div class="snap-price">${brent_p:.2f}</div><div class="snap-unit">barrel · BRENT10 AU26</div>
      {spark_svg("brent", "#16A34A" if brent_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if natgas_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">NAT GAS (NGAS1K)</div><span class="snap-chg {'up' if natgas_chg>=0 else 'dn'}">{chg_str(natgas_chg)}</span></div>
      <div class="snap-price">${natgas_p:.3f}</div><div class="snap-unit">MMBtu · NGAS1K JY26</div>
      {spark_svg("natgas", "#16A34A" if natgas_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if copper_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">COPPER</div><span class="snap-chg {'up' if copper_chg>=0 else 'dn'}">{chg_str(copper_chg)}</span></div>
      <div class="snap-price">${copper_p:.3f}</div><div class="snap-unit">lb · COPPER JY26</div>
      {spark_svg("copper", "#16A34A" if copper_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if sp_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">S&amp;P 500</div><span class="snap-chg {'up' if sp_chg>=0 else 'dn'}">{chg_str(sp_chg)}</span></div>
      <div class="snap-price">{sp_p:,.2f}</div><div class="snap-unit">index · ^GSPC</div>
      {spark_svg("sp500", "#16A34A" if sp_chg>=0 else "#DC2626")}
    </div>
    <div class="snap-card {'up' if nq_chg>=0 else 'dn'}-card">
      <div class="snap-row1"><div class="snap-name">NASDAQ 100</div><span class="snap-chg {'up' if nq_chg>=0 else 'dn'}">{chg_str(nq_chg)}</span></div>
      <div class="snap-price">{nq_p:,.2f}</div><div class="snap-unit">index · ^NDX</div>
      {spark_svg("nasdaq", "#16A34A" if nq_chg>=0 else "#DC2626")}
    </div>
  </div>

  <!-- MACRO -->
  <div class="sec-head">
    <span class="sec-tag">Macro</span>
    <span class="sec-title">Global Macro Dashboard</span>
    <span class="sec-meta">Live</span>
  </div>
  <div class="macro-grid" style="margin-bottom:24px;">
    <div class="macro-card">
      <div class="macro-lbl">VIX · Fear Index</div>
      <div class="macro-val">{vix_p:.1f}</div>
      <div class="macro-sub">{'▲ Low Volatility' if vix_p < 20 else '▲ Elevated Volatility' if vix_p < 30 else '▲ HIGH VOLATILITY'}</div>
    </div>
    <div class="macro-card">
      <div class="macro-lbl">DXY · Dollar Index</div>
      <div class="macro-val">{dxy_p:.1f}</div>
      <div class="macro-sub">{'▲ Dollar Weakness' if dxy_p < 100 else '▲ Dollar Strength'}</div>
    </div>
    <div class="macro-card">
      <div class="macro-lbl">Gold / Silver Ratio</div>
      <div class="macro-val">{gs_ratio}x</div>
      <div class="macro-sub">▲ Relative value</div>
    </div>
    <div class="macro-card">
      <div class="macro-lbl">US 10Y Treasury</div>
      <div class="macro-val">{us10y_p:.2f}%</div>
      <div class="macro-sub">▼ Yield backdrop</div>
    </div>
  </div>

  <!-- FX TABLE -->
  <div class="sec-head">
    <span class="sec-tag">FX Markets</span>
    <span class="sec-title">Forex Market Pulse</span>
    <span class="sec-meta">Prev Close → Live</span>
  </div>
  <div class="fx-table-wrap">
    <div class="fx-thead"><div>Pair</div><div>Prev Close</div><div>Live</div><div>CHG</div><div>Range (3M)</div></div>
    {''.join([
      f'<div class="fx-row"><div class="fx-pair">{pair}</div><div class="fx-rate">{prev:.4f}</div><div class="fx-rate">{live:.4f}</div><div>{fx_chg_badge(live, prev)}</div><div class="fx-range">{fx_3m_range(key)}</div></div>'
      for pair, key, live, prev in [
        ("EUR/USD","eurusd",eurusd_p,eurusd_prev),("GBP/USD","gbpusd",gbpusd_p,gbpusd_prev),
        ("USD/JPY","usdjpy",usdjpy_p,usdjpy_prev),("USD/CHF","usdchf",usdchf_p,usdchf_prev),
        ("AUD/USD","audusd",audusd_p,audusd_prev),("USD/CAD","usdcad",usdcad_p,usdcad_prev),
        ("USD/CNY","usdcny",usdcny_p,usdcny_prev),("EUR/GBP","eurgbp",eurgbp_p,eurgbp_prev),
      ]
    ])}
  </div>

  <!-- ECONOMIC CALENDAR -->
  <div class="sec-head">
    <span class="sec-tag">Calendar</span>
    <span class="sec-title">{'High-Impact Events — This Week' if edition_type == 'Weekly' else "Today's High-Impact Events"}</span>
    <span class="sec-meta">Live feed · PKT (UTC+5)</span>
  </div>
  {'<div class="cal-quiet">No high-impact events scheduled today.<br/><span style="font-size:11px;">A quiet day on the economic calendar — no market-moving releases. See the Weekly edition for the week ahead.</span></div>' if edition_type == 'Daily' else '''
  <table class="cal-table" style="margin-bottom:24px;">
    <thead><tr><th>Date &amp; Time (PKT)</th><th>🌍</th><th>Event</th><th>Prev</th><th>Estimate</th><th>Impact</th><th>PMEX</th></tr></thead>
    <tbody>
      <tr><td colspan="7" style="color:var(--muted);font-size:11px;font-style:italic;padding:12px 8px;">Weekly economic calendar — team to add key events for the week ahead. See ForexFactory.com or Investing.com for the live feed.</td></tr>
    </tbody>
  </table>'''}

  <!-- CENTRAL BANK WATCH -->
  <div class="sec-head">
    <span class="sec-tag">Central Banks</span>
    <span class="sec-title">Central Bank Watch</span>
    <span class="sec-meta">Policy Rates (entered)</span>
  </div>
  <div class="cb-grid">
    <div class="cb-card">
      <div class="cb-name">FED</div><div class="cb-fullname">US Federal Reserve</div>
      <div class="cb-rate">{fed_rate:.2f}%</div>
      <div class="cb-stance">EASING</div>
      <div class="cb-next">Next: Jun 18</div>
      <div class="cb-note">Rate path data-dependent. NFP is the key near-term catalyst.</div>
    </div>
    <div class="cb-card">
      <div class="cb-name">ECB</div><div class="cb-fullname">European Central Bank</div>
      <div class="cb-rate">{ecb_rate:.2f}%</div>
      <div class="cb-stance">EASING</div>
      <div class="cb-next">Next: Jul 10</div>
      <div class="cb-note">Lagarde data-dependent; CPI flash shapes guidance.</div>
    </div>
    <div class="cb-card">
      <div class="cb-name">BOJ</div><div class="cb-fullname">Bank of Japan</div>
      <div class="cb-rate">{boj_rate:.2f}%</div>
      <div class="cb-stance" style="background:#FEF3C7;color:#92400E;">HAWKISH</div>
      <div class="cb-next">Next: Jun 20</div>
      <div class="cb-note">Tightening bias amid rising CPI. Yen watch 142.00.</div>
    </div>
    <div class="cb-card">
      <div class="cb-name">SBP</div><div class="cb-fullname">State Bank of Pakistan</div>
      <div class="cb-rate">{sbp_rate:.1f}%</div>
      <div class="cb-stance">EASING</div>
      <div class="cb-next">Next: Jun 26</div>
      <div class="cb-note">Cutting cycle continues; PKR stable at {usd_pkr:.2f}.</div>
    </div>
  </div>

  <!-- ANALYSIS -->
  <div class="sec-head">
    <span class="sec-tag">Analysis</span>
    <span class="sec-title">Commodities &amp; Indices Deep Dive</span>
    <span class="sec-meta">Live technicals · RSI / 50-DMA / {'weekly' if edition_type=='Weekly' else 'intraday'} levels</span>
  </div>

  <div class="two-col">
    <!-- GOLD -->
    <div class="a-card">
      <div class="a-top-band band-amber"></div>
      <div class="a-body">
        <div class="a-header">
          <div><div class="a-name">Gold · GO1OZ AU26</div><div class="a-sub">PMEX · COMEX LINKED · AUG 2026</div></div>
          {bias_badge(T['gold']['bias'])}
        </div>
        <p class="a-text">Gold is {'below' if T['gold']['bias']=='BEARISH' else 'above'} its 50-day average, keeping the trend {'defensive' if T['gold']['bias']=='BEARISH' else 'constructive'}. RSI at {T['gold']['rsi']:.0f} {'is neutral' if 40<=T['gold']['rsi']<=60 else 'signals oversold conditions — a bounce is possible' if T['gold']['rsi']<40 else 'signals overbought conditions — watch for a pullback'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at ${T['gold']['sup']:,.2f} with resistance at ${T['gold']['res']:,.2f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">${T['gold']['res']:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">${gold_p:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">${T['gold']['sup']:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">{'50-DMA' if edition_type=='Weekly' else 'Pivot'}</div><div class="lv-val lv-piv">${T['gold']['dma50' if edition_type=='Weekly' else 'pivot']:,.2f}</div></div>
        </div>
      </div>
    </div>
    <!-- WTI -->
    <div class="a-card">
      <div class="a-top-band band-red"></div>
      <div class="a-body">
        <div class="a-header">
          <div><div class="a-name">WTI Crude · CRUDE10 JY26</div><div class="a-sub">PMEX · NYMEX LINKED · JUL 2026</div></div>
          {bias_badge(T['wti']['bias'])}
        </div>
        <p class="a-text">WTI Crude is {'below' if T['wti']['bias'] in ('BEARISH','OVERSOLD') else 'above'} its 50-day average, keeping the trend {'defensive' if T['wti']['bias'] in ('BEARISH','OVERSOLD') else 'constructive'}. RSI at {T['wti']['rsi']:.0f} {'signals oversold conditions — a bounce is possible' if T['wti']['rsi']<30 else 'is neutral' if 40<=T['wti']['rsi']<=60 else 'signals overbought conditions'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at ${T['wti']['sup']:.2f} with resistance at ${T['wti']['res']:.2f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">${T['wti']['res']:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">${wti_p:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">${T['wti']['sup']:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">{'50-DMA' if edition_type=='Weekly' else 'Pivot'}</div><div class="lv-val lv-piv">${T['wti']['dma50' if edition_type=='Weekly' else 'pivot']:.2f}</div></div>
        </div>
      </div>
    </div>
    <!-- SILVER -->
    <div class="a-card">
      <div class="a-top-band band-blue"></div>
      <div class="a-body">
        <div class="a-header">
          <div><div class="a-name">Silver · SL10 JY26</div><div class="a-sub">PMEX · COMEX LINKED · JUL 2026</div></div>
          {bias_badge(T['silver']['bias'])}
        </div>
        <p class="a-text">Silver is {'below' if T['silver']['bias'] in ('BEARISH','OVERSOLD') else 'above'} its 50-day average, keeping the trend {'defensive' if T['silver']['bias'] in ('BEARISH','OVERSOLD') else 'constructive'}. RSI at {T['silver']['rsi']:.0f} {'signals oversold conditions — a bounce is possible' if T['silver']['rsi']<30 else 'is neutral'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at ${T['silver']['sup']:.2f} with resistance at ${T['silver']['res']:.2f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">${T['silver']['res']:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">${silver_p:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">${T['silver']['sup']:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">{'50-DMA' if edition_type=='Weekly' else 'Pivot'}</div><div class="lv-val lv-piv">${T['silver']['dma50' if edition_type=='Weekly' else 'pivot']:.2f}</div></div>
        </div>
      </div>
    </div>
    <!-- NAT GAS -->
    <div class="a-card">
      <div class="a-top-band band-green"></div>
      <div class="a-body">
        <div class="a-header">
          <div><div class="a-name">Natural Gas · NGAS1K JY26</div><div class="a-sub">PMEX · HENRY HUB · JUL 2026</div></div>
          {bias_badge(T['natgas']['bias'])}
        </div>
        <p class="a-text">Natural Gas is {'above' if T['natgas']['bias']=='BULLISH' else 'below'} its 50-day average, {'confirming a constructive trend' if T['natgas']['bias']=='BULLISH' else 'keeping the trend defensive'}. RSI at {T['natgas']['rsi']:.0f} {'is neutral' if 40<=T['natgas']['rsi']<=60 else 'signals oversold conditions' if T['natgas']['rsi']<40 else 'signals overbought conditions'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at ${T['natgas']['sup']:.3f} with resistance at ${T['natgas']['res']:.3f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">${T['natgas']['res']:.3f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">${natgas_p:.3f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">${T['natgas']['sup']:.3f}</div></div>
          <div class="lv"><div class="lv-lbl">{'50-DMA' if edition_type=='Weekly' else 'Pivot'}</div><div class="lv-val lv-piv">${T['natgas']['dma50' if edition_type=='Weekly' else 'pivot']:.3f}</div></div>
        </div>
      </div>
    </div>
    <!-- S&P 500 -->
    <div class="a-card">
      <div class="a-top-band band-purp"></div>
      <div class="a-body">
        <div class="a-header">
          <div><div class="a-name">S&amp;P 500</div><div class="a-sub">PMEX INDICES · US LARGE-CAP</div></div>
          {bias_badge(T['sp500']['bias'])}
        </div>
        <p class="a-text">S&amp;P 500 is {'above' if T['sp500']['bias']=='BULLISH' else 'below'} its 50-day average, {'confirming a constructive trend' if T['sp500']['bias']=='BULLISH' else 'keeping the trend defensive'}. RSI at {T['sp500']['rsi']:.0f} {'is neutral' if 40<=T['sp500']['rsi']<=60 else 'signals oversold conditions' if T['sp500']['rsi']<40 else 'signals overbought conditions'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at {T['sp500']['sup']:,.2f} with resistance at {T['sp500']['res']:,.2f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">{T['sp500']['res']:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">{sp_p:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">{T['sp500']['sup']:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">{'50-DMA' if edition_type=='Weekly' else 'Pivot'}</div><div class="lv-val lv-piv">{T['sp500']['dma50' if edition_type=='Weekly' else 'pivot']:,.2f}</div></div>
        </div>
      </div>
    </div>
    <!-- NASDAQ -->
    <div class="a-card">
      <div class="a-top-band band-amber"></div>
      <div class="a-body">
        <div class="a-header">
          <div><div class="a-name">Nasdaq 100</div><div class="a-sub">PMEX INDICES · US TECH</div></div>
          {bias_badge(T['nasdaq']['bias'])}
        </div>
        <p class="a-text">Nasdaq 100 is {'above' if T['nasdaq']['bias']=='BULLISH' else 'below'} its 50-day average, {'confirming a constructive trend' if T['nasdaq']['bias']=='BULLISH' else 'keeping the trend defensive'}. RSI at {T['nasdaq']['rsi']:.0f} {'is neutral' if 40<=T['nasdaq']['rsi']<=60 else 'signals oversold conditions' if T['nasdaq']['rsi']<40 else 'signals overbought conditions'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at {T['nasdaq']['sup']:,.2f} with resistance at {T['nasdaq']['res']:,.2f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">{T['nasdaq']['res']:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">{nq_p:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">{T['nasdaq']['sup']:,.2f}</div></div>
          <div class="lv"><div class="lv-lbl">{'50-DMA' if edition_type=='Weekly' else 'Pivot'}</div><div class="lv-val lv-piv">{T['nasdaq']['dma50' if edition_type=='Weekly' else 'pivot']:,.2f}</div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- FX ANALYSIS -->
  <div class="sec-head">
    <span class="sec-tag">FX Analysis</span>
    <span class="sec-title">Currency Pair Outlook</span>
    <span class="sec-meta">{'Weekly' if edition_type=='Weekly' else 'Intraday'} pivot levels</span>
  </div>
  <div class="two-col">
    <div class="a-card">
      <div class="a-top-band band-blue"></div>
      <div class="a-body">
        <div class="a-header"><div><div class="a-name">EUR/USD</div><div class="a-sub">MAJOR · EURO VS US DOLLAR</div></div>{bias_badge(T['eurusd']['bias'])}</div>
        <p class="a-text">EUR/USD is {'below' if T['eurusd']['bias']=='BEARISH' else 'above'} its 50-day average. RSI at {T['eurusd']['rsi']:.0f} {'is neutral' if 40<=T['eurusd']['rsi']<=60 else 'signals oversold' if T['eurusd']['rsi']<40 else 'signals overbought'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at {T['eurusd']['sup']:.4f} with resistance at {T['eurusd']['res']:.4f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">{T['eurusd']['res']:.4f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">{eurusd_p:.4f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">{T['eurusd']['sup']:.4f}</div></div>
          <div class="lv"><div class="lv-lbl">Pivot</div><div class="lv-val lv-piv">{T['eurusd']['pivot']:.4f}</div></div>
        </div>
      </div>
    </div>
    <div class="a-card">
      <div class="a-top-band band-purp"></div>
      <div class="a-body">
        <div class="a-header"><div><div class="a-name">USD/JPY</div><div class="a-sub">MAJOR · USD VS JAPANESE YEN</div></div>{bias_badge(T['usdjpy']['bias'])}</div>
        <p class="a-text">USD/JPY is {'above' if T['usdjpy']['bias'] in ('BULLISH','OVERBOUGHT') else 'below'} its 50-day average. RSI at {T['usdjpy']['rsi']:.0f} {'signals overbought conditions — watch for a pullback' if T['usdjpy']['rsi']>70 else 'is neutral' if 40<=T['usdjpy']['rsi']<=60 else 'signals oversold conditions'}. {'Intraday' if edition_type=='Daily' else 'Weekly'} support sits at {T['usdjpy']['sup']:.2f} with resistance at {T['usdjpy']['res']:.2f}.</p>
        <div class="a-levels">
          <div class="lv"><div class="lv-lbl">Resistance</div><div class="lv-val lv-res">{T['usdjpy']['res']:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Spot</div><div class="lv-val lv-spot">{usdjpy_p:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Support</div><div class="lv-val lv-sup">{T['usdjpy']['sup']:.2f}</div></div>
          <div class="lv"><div class="lv-lbl">Pivot</div><div class="lv-val lv-piv">{T['usdjpy']['pivot']:.2f}</div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- SIGNAL SUMMARY -->
  <div class="sec-head">
    <span class="sec-tag">Technical Bias</span>
    <span class="sec-title">Signal Summary</span>
    <span class="sec-meta">Rule engine · RSI + trend</span>
  </div>
  <div class="signal-grid" style="margin-bottom:24px;">
    {' '.join([
      f'''<div class="sig-card">
        <div class="sig-name">{name}</div><div class="sig-sub">{sub}</div>
        <div class="sig-rsi" style="color:{'var(--neg)' if rsi<40 else 'var(--green)' if rsi>60 else 'var(--amber)'}">{rsi:.0f}</div>
        <div class="sig-bias {'imp-h' if bias in ('BEARISH','OVERSOLD','OVERBOUGHT') else 'imp-l' if bias=='BULLISH' else 'imp-m'}">{bias}</div>
        <div style="font-size:9px;color:var(--muted);margin-top:4px;">RSI {rsi:.0f} · {'Above' if bias in ('BULLISH','OVERBOUGHT') else 'Below'} 50-DMA</div>
      </div>'''
      for name, sub, key, rsi, bias in [
        ("Gold","GO1OZ · RSI","gold",T['gold']['rsi'],T['gold']['bias']),
        ("Crude","CRUDE10 · RSI","wti",T['wti']['rsi'],T['wti']['bias']),
        ("S&P 500","INDEX · RSI","sp500",T['sp500']['rsi'],T['sp500']['bias']),
        ("Nasdaq","INDEX · RSI","nasdaq",T['nasdaq']['rsi'],T['nasdaq']['bias']),
      ]
    ])}
  </div>

  <!-- STRATEGY CORNER -->
  <div class="sec-head">
    <span class="sec-tag">Strategy Corner</span>
    <span class="sec-title">{'Strategy of the Week' if edition_type=='Weekly' else 'Strategy of the Day'}</span>
    <span class="sec-meta">Auto-derived from live signals</span>
  </div>
  <div class="strategy-box">
    <div class="strat-header">💡 {strat_title}</div>
    <div class="strat-sub">{strat_body}</div>
    <ul class="strat-list">{strat_bullets}</ul>
  </div>

  <!-- RISK DASHBOARD -->
  <div class="sec-head">
    <span class="sec-tag">Risk</span>
    <span class="sec-title">Risk Environment Dashboard</span>
    <span class="sec-meta">Live</span>
  </div>
  <div class="risk-grid" style="margin-bottom:24px;">
    <div class="risk-card">
      <div class="risk-lbl">Market Volatility (VIX)</div>
      <div class="risk-val">{vix_p:.1f}</div>
      <div class="risk-bar-wrap"><div class="risk-bar" style="width:{min(vix_p/50*100,100):.0f}%;background:{'#16A34A' if vix_p<20 else '#E39E3D' if vix_p<30 else '#DC2626'};"></div></div>
      <div class="risk-note">{'Low volatility — risk-on backdrop. Events may spike vol.' if vix_p<20 else 'Elevated volatility — reduce size and widen stops.' if vix_p<30 else 'HIGH VOLATILITY — extreme caution; reduce exposure.'}</div>
    </div>
    <div class="risk-card">
      <div class="risk-lbl">US Dollar Index (DXY)</div>
      <div class="risk-val">{dxy_p:.1f}</div>
      <div class="risk-bar-wrap"><div class="risk-bar" style="width:{min((dxy_p-90)/30*100,100):.0f}%;background:#E39E3D;"></div></div>
      <div class="risk-note">{'Sub-100 DXY supports gold and USD-priced commodities.' if dxy_p<100 else 'Stronger dollar creates headwind for commodities.'}</div>
    </div>
    <div class="risk-card">
      <div class="risk-lbl">Geopolitical Risk Index</div>
      <div class="risk-val">ELEVATED</div>
      <div class="risk-bar-wrap"><div class="risk-bar" style="width:65%;background:#E39E3D;"></div></div>
      <div class="risk-note">Ongoing tensions sustain a gold risk premium and energy supply risk.</div>
    </div>
  </div>

  <!-- CONTRACT SPECS -->
  <div class="sec-head">
    <span class="sec-tag">Contract Specs</span>
    <span class="sec-title">PMEX Contract Specifications</span>
    <span class="sec-meta">Regular · Intraday</span>
  </div>

  <div class="specs-section-head">✦ Gold (XAU) — Base: GO1OZ AUG 2026 · ${gold_p:,.2f} / OZ</div>
  <table class="specs-table">
    <thead><tr><th>Contract Code</th><th>Description</th><th>Size</th><th>Price</th><th>Tola Equiv.</th><th>Margin (PKR)</th><th>%</th></tr></thead>
    <tbody>
      <tr><td>GO1OZ AU26</td><td>Gold — 1 Troy Ounce</td><td>1 oz</td><td>${gold_p:,.2f}</td><td>2.667 tola</td><td>69,800</td><td>5.75%</td></tr>
      <tr><td>GO1OZ AU26 ID</td><td>Gold 1 Oz INTRADAY</td><td>1 oz</td><td>${gold_p:,.2f}</td><td>2.667 tola</td><td>36,400</td><td>3%</td></tr>
    </tbody>
  </table>

  <div class="specs-section-head">◈ Silver (XAG) — Base: SL10 JUL 2026 · ${silver_p:.2f} / OZ</div>
  <table class="specs-table">
    <thead><tr><th>Contract Code</th><th>Description</th><th>Size</th><th>Price</th><th>Tola Equiv.</th><th>Margin (PKR)</th><th>%</th></tr></thead>
    <tbody>
      <tr><td>SL10 JY26</td><td>Silver — 10 Troy Oz</td><td>10 oz</td><td>${silver_p:.2f}</td><td>26.67 tola</td><td>21,000</td><td>11%</td></tr>
      <tr><td>SL10 JY26 ID</td><td>Silver 10 Oz INTRADAY</td><td>10 oz</td><td>${silver_p:.2f}</td><td>26.67 tola</td><td>10,500</td><td>5.5%</td></tr>
    </tbody>
  </table>

  <div class="specs-section-head">🛢 Crude Oil WTI — Base: CRUDE10 JUL 2026 · ${wti_p:.2f} / BBL</div>
  <table class="specs-table">
    <thead><tr><th>Contract Code</th><th>Description</th><th>Size</th><th>Price</th><th>Margin (PKR)</th><th>%</th></tr></thead>
    <tbody>
      <tr><td>CRUDE10 JY26</td><td>WTI Crude Oil — 10 Barrels</td><td>10 bbl</td><td>${wti_p:.2f}</td><td>43,200</td><td>17%</td></tr>
      <tr><td>CRUDE10 JY26 ID</td><td>WTI Crude 10 Bbl INTRADAY</td><td>10 bbl</td><td>${wti_p:.2f}</td><td>43,200</td><td>17%</td></tr>
    </tbody>
  </table>

  <div class="specs-section-head">⛽ Brent Crude — Base: BRENT10 AUG 2026 · ${brent_p:.2f} / BBL</div>
  <table class="specs-table" style="margin-bottom:24px;">
    <thead><tr><th>Contract Code</th><th>Description</th><th>Size</th><th>Price</th><th>Margin (PKR)</th><th>%</th></tr></thead>
    <tbody>
      <tr><td>BRENT10 AU26</td><td>Brent Crude Oil — 10 Barrels</td><td>10 bbl</td><td>${brent_p:.2f}</td><td>44,600</td><td>17%</td></tr>
    </tbody>
  </table>

  <!-- TRADING SESSIONS -->
  <div class="sec-head">
    <span class="sec-tag">Sessions</span>
    <span class="sec-title">Global Trading Sessions</span>
    <span class="sec-meta">All times PKT (UTC+5)</span>
  </div>
  <div class="sess-grid" style="margin-bottom:24px;">
    <div class="sess-card {'active-sess' if sess_active('sydney') else ''}">
      <div class="sess-name">Sydney</div><div class="sess-time">02:00 AM – 11:00 AM</div>
      <div class="sess-focus">AUD · NZD focus</div>
      <div class="sess-status {'on' if sess_active('sydney') else 'off'}">{sess_dot('sydney')}</div>
    </div>
    <div class="sess-card {'active-sess' if sess_active('tokyo') else ''}">
      <div class="sess-name">Tokyo · Asian</div><div class="sess-time">05:00 AM – 02:00 PM</div>
      <div class="sess-focus">JPY · Gold active</div>
      <div class="sess-status {'on' if sess_active('tokyo') else 'off'}">{sess_dot('tokyo')}</div>
    </div>
    <div class="sess-card {'active-sess' if sess_active('london') else ''}">
      <div class="sess-name">London · European</div><div class="sess-time">01:00 PM – 10:00 PM</div>
      <div class="sess-focus">EUR · GBP · high activity</div>
      <div class="sess-status {'on' if sess_active('london') else 'off'}">{sess_dot('london')}</div>
    </div>
    <div class="sess-card {'active-sess' if sess_active('newyork') else ''}">
      <div class="sess-name">New York · US</div><div class="sess-time">06:00 PM – 03:00 AM</div>
      <div class="sess-focus">USD · Oil · Gold · peak liquidity</div>
      <div class="sess-status {'on' if sess_active('newyork') else 'off'}">{sess_dot('newyork')}</div>
    </div>
  </div>
  <p style="font-size:10px;color:var(--muted);margin-bottom:24px;line-height:1.6;">Highest volatility: the London–New York overlap (06:00 PM – 10:00 PM PKT) sees the heaviest volume in gold, oil and major FX pairs — the prime window for PMEX traders. PMEX itself trades 04:00 AM – 02:00 AM PKT, covering all four sessions.</p>

</div><!-- /body-wrap -->

<!-- FOOTER -->
<footer class="footer">
  <div class="footer-top">
    <div style="display:flex;align-items:center;gap:10px;">
      <img src="https://floretcapitals.com/wp-content/uploads/2024/10/cropped-cropped-Floret-Icon-80x76.png"
           width="28" alt="Floret Capitals" onerror="this.style.display='none'"/>
      <span class="footer-brand-name">FLORET CAPITALS</span>
    </div>
    <div class="footer-contact">
      <strong>+92 311 1000183</strong><br/>
      contact@floretcapitals.com · floretcapitals.com<br/>
      Blue Area, Islamabad · M.M Alam Road, Lahore
    </div>
  </div>
  <p class="footer-disc">Risk Disclaimer: Trading commodities on PMEX involves significant risk of loss; leverage magnifies gains and losses. Live prices via public market feeds (indicative, may be delayed). Margins from the uploaded PMEX margin file; PMEX-listed prices are denominated and settled per exchange contract specs. Technical signals are rule-based and not investment advice. Floret Capitals is SECP-licensed. Past performance is not indicative of future results.</p>
  <div class="footer-links">
    <a href="https://floretcapitals.com">floretcapitals.com</a><span class="footer-sep">·</span>
    <a href="#">Open Account</a><span class="footer-sep">·</span>
    <a href="#">PMEX Portal</a><span class="footer-sep">·</span>
    <a href="#">Unsubscribe</a>
  </div>
  <p class="copy">© 2026 Floret Capitals Ltd. All rights reserved. SECP Licensed · Pakistan.</p>
</footer>

</body>
</html>"""

        # Download
        b64 = base64.b64encode(html.encode()).decode()
        fname = f"floret-{edition_type.lower()}-{edition_date.strftime('%Y-%m-%d')}.html"

        st.download_button(
            label=f"📥 Download {brief_type} Newsletter (HTML)",
            data=html.encode(),
            file_name=fname,
            mime="text/html",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("**How to convert to PDF:**")
        st.markdown("1. Open the downloaded HTML file in Chrome\n2. Press `Ctrl+P` (or `Cmd+P` on Mac)\n3. Set destination to **Save as PDF**\n4. Set margins to **None** → Save")

        st.markdown("---")
        with st.expander("Preview newsletter HTML", expanded=False):
            st.components.v1.html(html, height=600, scrolling=True)

    else:
        st.markdown("""
        <div class="fc-ready-panel">
          <img src="https://floretcapitals.com/wp-content/uploads/2024/10/cropped-cropped-Floret-Icon-80x76.png"
               width="64" alt="Floret Capitals" style="opacity:.9;"
               onerror="this.style.display='none'"/>
          <div class="fc-ready-title">PMEX Newsletter Generator</div>
          <div class="fc-ready-sub">
            Fill in the form on the left and click <strong>Generate Newsletter</strong>.<br/>
            All market data is fetched live and automatically — completely free.
          </div>
          <div class="fc-ready-pills">
            <span class="fc-ready-pill active">Gold · Silver</span>
            <span class="fc-ready-pill active">Crude · Brent</span>
            <span class="fc-ready-pill active">Forex · DXY</span>
            <span class="fc-ready-pill active">RSI · 50-DMA</span>
            <span class="fc-ready-pill">PMEX Specs</span>
            <span class="fc-ready-pill">Strategy Corner</span>
          </div>
          <div class="fc-features">
            <div class="fc-feature">
              <div class="fc-feature-icon">📡</div>
              <div class="fc-feature-title">Live Market Data</div>
              <div class="fc-feature-desc">Auto-fetched via Yahoo Finance — no API key needed</div>
            </div>
            <div class="fc-feature">
              <div class="fc-feature-icon">📊</div>
              <div class="fc-feature-title">Auto Technicals</div>
              <div class="fc-feature-desc">RSI, 50-DMA, support & resistance computed instantly</div>
            </div>
            <div class="fc-feature">
              <div class="fc-feature-icon">🗞️</div>
              <div class="fc-feature-title">Daily & Weekly</div>
              <div class="fc-feature-desc">Two editions — intraday or weekly swing levels</div>
            </div>
            <div class="fc-feature">
              <div class="fc-feature-icon">📥</div>
              <div class="fc-feature-title">Download HTML</div>
              <div class="fc-feature-desc">Open in Chrome → Print → Save as PDF in seconds</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
