import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import altair as alt
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ─── Timestamp Indonesia ───────────────────────────────────────────────────────
def get_indo_timestamp():
    now = datetime.now()
    bulan = {"January":"Jan","February":"Feb","March":"Mar","April":"Apr",
              "May":"Mei","June":"Jun","July":"Jul","August":"Agu",
              "September":"Sep","October":"Okt","November":"Nov","December":"Des"}
    return now.strftime(f"%d {bulan.get(now.strftime('%B'), now.strftime('%B'))} %Y  •  %H:%M WIB")

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Risk Monitor",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, .stText, button, input, select, textarea {
    font-family: 'Inter', sans-serif !important;
}

/* ── Background ── */
.stApp { background: #f0f4ff !important; }

/* ── Main container ── */
[data-testid="block-container"] {
    padding: 1.2rem 2.5rem 2rem 2.5rem !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════
   SIDEBAR — full reset + restyle
══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    min-width: 300px !important;
    max-width: 300px !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

[data-testid="stSidebarUserContent"] {
    padding: 1.2rem 1rem !important;
}

/* All sidebar text default */
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}

/* ── Sidebar Form ── */
[data-testid="stSidebar"] [data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

/* ── Expanders ── */
[data-testid="stSidebar"] details {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}

[data-testid="stSidebar"] details > summary {
    color: #e2e8f0 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
    cursor: pointer !important;
    list-style: none !important;
    display: flex !important;
    align-items: center !important;
    background: transparent !important;
}

[data-testid="stSidebar"] details > summary:hover {
    background: rgba(255,255,255,0.06) !important;
}

[data-testid="stSidebar"] details[open] > summary {
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] details > div {
    padding: 10px 12px !important;
}

/* ── Slider labels ── */
[data-testid="stSidebar"] .stSlider {
    padding-bottom: 0.4rem !important;
}

[data-testid="stSidebar"] .stSlider > label,
[data-testid="stSidebar"] .stSlider > div > label {
    font-size: 0.75rem !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.4px !important;
    display: block !important;
    margin-bottom: 4px !important;
}

/* Slider value display */
[data-testid="stSidebar"] [data-testid="stSlider"] p,
[data-testid="stSidebar"] [data-testid="stSlider"] span {
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
}

/* Slider track */
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {
    background: #2563eb !important;
}

/* ── Number inputs — ultra-aggressive selectors ── */
[data-testid="stSidebar"] [data-testid="stNumberInput"],
[data-testid="stSidebar"] .stNumberInput {
    margin-bottom: 0.5rem !important;
}

/* Label */
[data-testid="stSidebar"] [data-testid="stNumberInput"] label,
[data-testid="stSidebar"] .stNumberInput label {
    font-size: 0.75rem !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.4px !important;
    display: block !important;
    margin-bottom: 4px !important;
}

/* The actual input box — target every possible selector */
[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] input[aria-label],
[data-testid="stSidebar"] [data-testid="stNumberInput"] input,
[data-testid="stSidebar"] .stNumberInput input {
    background-color: #1e3a5f !important;
    background: #1e3a5f !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid rgba(96,165,250,0.4) !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 8px 10px !important;
    text-align: center !important;
    caret-color: #ffffff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] input[type="number"]:focus,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input:focus {
    background-color: #1e3a5f !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.4) !important;
    outline: none !important;
}

/* Disable browser autofill color overrides */
[data-testid="stSidebar"] input:-webkit-autofill,
[data-testid="stSidebar"] input:-webkit-autofill:hover,
[data-testid="stSidebar"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0px 1000px #1e3a5f inset !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

/* +/- step buttons */
[data-testid="stSidebar"] [data-testid="stNumberInput"] button,
[data-testid="stSidebar"] .stNumberInput button {
    background: rgba(37,99,235,0.25) !important;
    color: #93c5fd !important;
    border: 1px solid rgba(96,165,250,0.3) !important;
    border-radius: 6px !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    margin: 0 2px !important;
    transition: background 0.2s !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button:hover,
[data-testid="stSidebar"] .stNumberInput button:hover {
    background: rgba(37,99,235,0.5) !important;
    color: #fff !important;
}

/* ── Submit button ── */
[data-testid="stSidebar"] .stFormSubmitButton > button,
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1rem !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
    margin-top: 0.8rem !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.35) !important;
    letter-spacing: 0.3px !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] .stFormSubmitButton > button:hover,
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(37,99,235,0.45) !important;
}

/* ══════════════════════════════════════
   MAIN CONTENT
══════════════════════════════════════ */

/* ── Card containers ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid rgba(226,232,240,0.8) !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px rgba(15,23,42,0.06), 0 1px 3px rgba(15,23,42,0.04) !important;
    padding: 1.4rem !important;
    margin-bottom: 1rem !important;
    transition: box-shadow 0.25s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 30px rgba(37,99,235,0.10), 0 2px 8px rgba(15,23,42,0.06) !important;
}

/* ── KPI cards ── */
.kpi-wrap {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
    display: flex;
    align-items: center;
    gap: 14px;
    border: 1px solid rgba(226,232,240,0.8);
    box-shadow: 0 2px 12px rgba(15,23,42,0.06);
    transition: all 0.25s ease;
    margin-bottom: 0.8rem;
}
.kpi-wrap:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(37,99,235,0.12);
}
.kpi-icon {
    width: 46px; height: 46px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0;
}
.ic-red   { background: linear-gradient(135deg,#fee2e2,#fecaca); }
.ic-blue  { background: linear-gradient(135deg,#dbeafe,#bfdbfe); }
.ic-green { background: linear-gradient(135deg,#dcfce7,#bbf7d0); }
.ic-amber { background: linear-gradient(135deg,#fef3c7,#fde68a); }
.kpi-lbl  { font-size: 0.72rem; font-weight: 700; color: #94a3b8;
            text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 2px; }
.kpi-val  { font-size: 1.4rem; font-weight: 800; line-height: 1.1; margin: 0; }
.kpi-sub  { font-size: 0.72rem; color: #94a3b8; font-weight: 500; margin-top: 2px; }

/* ── Section titles ── */
.sec-title {
    font-size: 0.95rem; font-weight: 700; color: #1e293b;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid #f0f4ff;
}

/* ── Status badge ── */
.badge {
    display: inline-block; font-size: 0.7rem; font-weight: 700;
    padding: 2px 9px; border-radius: 20px; letter-spacing: 0.3px;
}
.badge-green  { background:#dcfce7; color:#15803d; }
.badge-yellow { background:#fef9c3; color:#a16207; }
.badge-red    { background:#fee2e2; color:#b91c1c; }
.badge-gray   { background:#f1f5f9; color:#475569; }

/* ── Metric bar row ── */
.metric-row {
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f8fafc;
}
.metric-label { font-size: 0.82rem; font-weight: 600; color: #334155; }
.bar-track {
    height: 6px; background: #f1f5f9; border-radius: 99px;
    margin: 5px 0 3px 0; overflow: hidden;
}
.bar-fill { height: 100%; border-radius: 99px; }
.bar-blue   { background: linear-gradient(90deg,#2563eb,#60a5fa); }
.bar-green  { background: linear-gradient(90deg,#16a34a,#4ade80); }
.bar-yellow { background: linear-gradient(90deg,#d97706,#fbbf24); }
.bar-red    { background: linear-gradient(90deg,#dc2626,#f87171); }
.metric-val { font-size: 0.78rem; font-weight: 700; color: #0f172a; }

/* ── Alert box ── */
.alert-box {
    padding: 0.8rem 1rem; border-radius: 12px;
    display: flex; gap: 10px; align-items: flex-start;
    margin-top: 0.9rem; font-size: 0.84rem; line-height: 1.4;
}
.alert-high {
    background: linear-gradient(135deg,#fef2f2,#fee2e2);
    border: 1px solid #fca5a5; color: #991b1b;
}
.alert-low {
    background: linear-gradient(135deg,#f0fdf4,#dcfce7);
    border: 1px solid #86efac; color: #166534;
}

/* ── Rec items ── */
.rec-item {
    padding: 0.9rem 1rem; border-radius: 12px;
    margin-bottom: 0.7rem; font-size: 0.83rem; line-height: 1.5;
}
.rec-danger  { background:#fef2f2; border-left:3px solid #ef4444; color:#991b1b; }
.rec-success { background:#f0fdf4; border-left:3px solid #22c55e; color:#166534; }
.rec-warning { background:#fffbeb; border-left:3px solid #f59e0b; color:#92400e; }
.rec-info    { background:#eff6ff; border-left:3px solid #2563eb; color:#1e40af; }

/* ── Welcome banner ── */
.welcome-banner {
    background: linear-gradient(135deg,#1e40af,#2563eb,#3b82f6);
    border-radius: 20px; padding: 2.5rem 2rem;
    text-align: center; color: white;
    box-shadow: 0 10px 40px rgba(37,99,235,0.3);
    margin: 1rem 0;
}
.welcome-banner h2 { font-size: 1.6rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.welcome-banner p  { font-size: 1rem; opacity: 0.85; margin: 0; }

/* ── Header ── */
.main-header {
    background: linear-gradient(135deg,#1e3a8a,#1e40af,#2563eb);
    border-radius: 16px; padding: 1.1rem 1.6rem;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(37,99,235,0.25);
}
.main-header h1 {
    margin:0; font-size:1.25rem; font-weight:800; color:#fff;
    letter-spacing: -0.3px;
}
.main-header p  { margin:2px 0 0 0; font-size:0.78rem; color:rgba(255,255,255,0.7); }
.header-time {
    background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 0.45rem 1rem; border-radius: 10px;
    color: rgba(255,255,255,0.9); font-size: 0.78rem; font-weight: 600;
    white-space: nowrap;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #fff !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid #e2e8f0 !important;
    gap: 2px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    margin-bottom: 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    padding: 0.45rem 1.1rem !important;
    color: #64748b !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#2563eb,#1d4ed8) !important;
    color: #fff !important;
    box-shadow: 0 3px 10px rgba(37,99,235,0.3) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg,#2563eb,#60a5fa) !important;
    border-radius: 99px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#f1f5f9; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#94a3b8; }

/* ── Fix: make sure sidebar header logo area visible ── */
[data-testid="stSidebar"] .sidebar-logo-area {
    text-align: center;
    margin-bottom: 1.2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* Hide number input spin arrows (cleaner look) */
[data-testid="stSidebar"] input[type="number"]::-webkit-inner-spin-button,
[data-testid="stSidebar"] input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] input[type="number"] {
    -moz-appearance: textfield !important;
}
</style>
""", unsafe_allow_html=True)

# ─── JS fallback: force number input colors in sidebar ────────────────────────
st.markdown("""
<script>
(function applyInputStyles() {
    const style = {
        backgroundColor: '#1e3a5f',
        color: '#ffffff',
        border: '1px solid rgba(96,165,250,0.4)',
        borderRadius: '8px',
        fontWeight: '700',
        fontSize: '0.95rem',
        textAlign: 'center',
    };
    function paint() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        sidebar.querySelectorAll('input[type="number"], input[aria-label]').forEach(el => {
            Object.assign(el.style, style);
        });
    }
    // Run immediately and observe DOM changes
    paint();
    const observer = new MutationObserver(paint);
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)


# ─── Load Model ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model_file = 'model_xgb_9fitur.pkl'
    if os.path.exists(model_file):
        return joblib.load(model_file)
    else:
        st.error("❌ File `model_xgb_9fitur.pkl` tidak ditemukan di folder yang sama.")
        up = st.file_uploader("Upload file model (.pkl)", type=['pkl'], key='model_upload')
        if up:
            with open(model_file, 'wb') as f:
                f.write(up.getbuffer())
            st.success("✅ Upload berhasil! Silakan refresh halaman.")
            st.stop()
        return None

model = load_model()


# ─── KPI Cards ────────────────────────────────────────────────────────────────
def draw_kpi_metrics(rec):
    c1, c2, c3, c4 = st.columns(4)

    if rec:
        is_high  = "High" in rec['Prediksi']
        r_icon   = "🚨" if is_high else "✅"
        r_label  = "HIGH RISK" if is_high else "LOW RISK"
        r_sub    = "Perlu tindakan segera" if is_high else "Pemasok aman"
        r_color  = "#ef4444" if is_high else "#16a34a"
        r_ic_cls = "ic-red" if is_high else "ic-green"
        score    = rec['Prob_High'] * 100
        sc_sub   = "Prob. High Risk"
    else:
        r_icon = "🔷"; r_label = "SIAP"; r_sub = "Menunggu prediksi"
        r_color = "#2563eb"; r_ic_cls = "ic-blue"; score = 0.0; sc_sub = "Belum ada data"

    with c1:
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-icon {r_ic_cls}">{r_icon}</div>
            <div>
                <div class="kpi-lbl">Status Risiko</div>
                <div class="kpi-val" style="color:{r_color};">{r_label}</div>
                <div class="kpi-sub">{r_sub}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    with c2:
        bar_color = "#ef4444" if score >= 70 else "#f59e0b" if score >= 40 else "#16a34a"
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-icon ic-blue">📊</div>
            <div style="width:100%">
                <div class="kpi-lbl">Risk Score</div>
                <div class="kpi-val" style="color:{bar_color};">{score:.1f}%</div>
                <div class="kpi-sub">{sc_sub}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-icon ic-green">🎯</div>
            <div>
                <div class="kpi-lbl">Model Accuracy</div>
                <div class="kpi-val" style="color:#16a34a;">91.0%</div>
                <div class="kpi-sub">XGBoost · 9 Fitur</div>
            </div>
        </div>""", unsafe_allow_html=True)

    with c4:
        waktu_now = datetime.now().strftime("%H:%M WIB")
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-icon ic-amber">🕐</div>
            <div>
                <div class="kpi-lbl">Waktu Analisis</div>
                <div class="kpi-val" style="color:#d97706;">{waktu_now}</div>
                <div class="kpi-sub">Prediksi terakhir</div>
            </div>
        </div>""", unsafe_allow_html=True)


# ─── Gauge (matplotlib) ───────────────────────────────────────────────────────
def create_gauge(val):
    fig, ax = plt.subplots(figsize=(4.2, 2.6), subplot_kw={'projection': 'polar'})

    segs = [
        (np.pi, np.pi * 0.6,       '#22c55e'),
        (np.pi * 0.6, np.pi * 0.3, '#f59e0b'),
        (np.pi * 0.3, 0,           '#ef4444'),
    ]
    for start, end, col in segs:
        ax.plot(np.linspace(start, end, 60), [1]*60,
                color=col, lw=16, solid_capstyle='butt', alpha=0.9)

    angle = np.pi - (val / 100.0) * np.pi
    ax.annotate('', xy=(angle, 0.88), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#0f172a',
                                lw=2.5, mutation_scale=14))
    ax.plot(0, 0, 'o', color='#0f172a', ms=9, zorder=5)

    for theta, lbl in [(np.pi, '0'), (np.pi*0.6, '40'), (np.pi*0.3, '70'), (0, '100')]:
        ax.text(theta, 1.28, lbl, ha='center', va='center',
                fontsize=7.5, fontweight='bold', color='#64748b')

    ax.text(-np.pi/2, 0.38, f"{val:.1f}%",
            ha='center', va='center', fontsize=20, fontweight='800', color='#0f172a')

    risk_lbl = "🔴 HIGH RISK" if val >= 70 else "🟡 MEDIUM" if val >= 40 else "🟢 LOW RISK"
    ax.text(-np.pi/2, 0.72, risk_lbl,
            ha='center', va='center', fontsize=8, fontweight='700', color='#475569')

    ax.set_ylim(0, 1.15)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.grid(False); ax.set_xticklabels([]); ax.set_yticklabels([])
    ax.spines['polar'].set_visible(False)
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    plt.tight_layout(pad=0.3)
    return fig


# ─── Donut chart ──────────────────────────────────────────────────────────────
def draw_donut_chart(proba_low, proba_high):
    df = pd.DataFrame({'Kategori': ['Low Risk','High Risk'],
                       'Probabilitas': [proba_low, proba_high]})
    base = alt.Chart(df).mark_arc(innerRadius=50, outerRadius=80, padAngle=0.03,
                                   cornerRadius=4).encode(
        theta=alt.Theta('Probabilitas:Q'),
        color=alt.Color('Kategori:N',
                        scale=alt.Scale(domain=['Low Risk','High Risk'],
                                        range=['#22c55e','#ef4444']),
                        legend=alt.Legend(orient='bottom', title=None,
                                          labelFontSize=11, symbolSize=80)),
        tooltip=[alt.Tooltip('Kategori:N'), alt.Tooltip('Probabilitas:Q', format='.1%')]
    )
    return base.properties(width=180, height=190).configure_view(strokeWidth=0)


# ─── Feature importance bar ───────────────────────────────────────────────────
def draw_feature_importance_chart(rec):
    names = ['Financial','Delivery','Quality','Regulatory','Sustainability',
             'Past Risk','ERP Trans.','Incidents','MCDM']
    df = pd.DataFrame({'Fitur': names,
                       'Pengaruh': rec['feature_importances']
                       }).sort_values('Pengaruh', ascending=False)
    chart = alt.Chart(df).mark_bar(cornerRadiusEnd=5, height=16).encode(
        x=alt.X('Pengaruh:Q', title='Tingkat Pengaruh', axis=alt.Axis(format='.2f')),
        y=alt.Y('Fitur:N', sort='-x', title=None),
        color=alt.condition(
            alt.datum.Pengaruh > df['Pengaruh'].median(),
            alt.value('#2563eb'), alt.value('#93c5fd')
        ),
        tooltip=['Fitur', alt.Tooltip('Pengaruh:Q', format='.4f')]
    ).properties(height=240).configure_view(strokeWidth=0).configure_axis(
        labelFontSize=11, titleFontSize=11
    )
    return chart


# ─── Metric bar rows ──────────────────────────────────────────────────────────
def draw_score_rows(rec):
    items = [
        ('💰', 'Financial Stability',  rec['financial'],        False, False),
        ('🚚', 'Delivery Performance', rec['delivery'],         False, False),
        ('✅', 'Quality Compliance',   rec['quality'],          False, False),
        ('📜', 'Regulatory Adherence', rec['regulatory'],       False, False),
        ('🌿', 'Sustainability Score', rec['sustainability'],    False, False),
        ('⚠️', 'Past Risk Level',      rec['past_risk'],        True,  False),
        ('💻', 'ERP Transactions',     rec['erp_transactions'], False, True),
        ('🚨', 'Incidents Count',      rec['incidents'],        False, True),
        ('📊', 'MCDM Score',           rec['mcdm_score'],       False, False),
    ]
    for icon, label, val, is_risk, is_count in items:
        if is_count:
            val_str = f"{int(val)}"
            if 'ERP' in label:
                max_v = 1000
                pct   = min(val / max_v, 1.0)
                if val >= 500:
                    badge_cls="badge-green";  badge_txt="Aktif";   bar_cls="bar-green"
                elif val >= 200:
                    badge_cls="badge-yellow"; badge_txt="Sedang";  bar_cls="bar-yellow"
                else:
                    badge_cls="badge-red";    badge_txt="Rendah";  bar_cls="bar-red"
            else:
                max_v = 50
                pct   = min(val / max_v, 1.0)
                if val <= 2:
                    badge_cls="badge-green";  badge_txt="Aman";    bar_cls="bar-green"
                elif val <= 10:
                    badge_cls="badge-yellow"; badge_txt="Waspada"; bar_cls="bar-yellow"
                else:
                    badge_cls="badge-red";    badge_txt="Kritis";  bar_cls="bar-red"
        elif is_risk:
            pct = val
            val_str = f"{val:.2f}"
            if val <= 0.3:
                badge_cls="badge-green";  badge_txt="Rendah"; bar_cls="bar-green"
            elif val <= 0.6:
                badge_cls="badge-yellow"; badge_txt="Sedang"; bar_cls="bar-yellow"
            else:
                badge_cls="badge-red";    badge_txt="Tinggi"; bar_cls="bar-red"
        else:
            pct = val; val_str = f"{val:.2f}"
            if val >= 0.7:
                badge_cls="badge-green";  badge_txt="Baik";   bar_cls="bar-green"
            elif val >= 0.4:
                badge_cls="badge-yellow"; badge_txt="Sedang"; bar_cls="bar-yellow"
            else:
                badge_cls="badge-red";    badge_txt="Buruk";  bar_cls="bar-red"

        width_pct = round(pct * 100)
        st.markdown(f"""
        <div class="metric-row">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span class="metric-label">{icon} {label}</span>
                <span class="badge {badge_cls}">{badge_txt}</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill {bar_cls}" style="width:{width_pct}%;"></div>
            </div>
            <div class="metric-val">{val_str}</div>
        </div>""", unsafe_allow_html=True)


# ─── Recommendations ──────────────────────────────────────────────────────────
def get_recommendation_html(rec):
    if not rec:
        return "<p style='color:#94a3b8;'>Silakan lakukan prediksi terlebih dahulu.</p>"
    scores = {
        'Financial Stability':  rec['financial'],
        'Delivery Performance': rec['delivery'],
        'Quality Compliance':   rec['quality'],
        'Regulatory Adherence': rec['regulatory'],
        'Sustainability Score': rec['sustainability'],
    }
    min_f, min_v = min(scores.items(), key=lambda x: x[1])
    max_f, max_v = max(scores.items(), key=lambda x: x[1])
    inc, pr = rec['incidents'], rec['past_risk']

    h  = f'<div class="rec-item rec-danger"><strong>⚠️ Aspek Terlemah: {min_f} ({min_v:.2f})</strong><br>'
    h += '• Audit mendalam diperlukan segera.<br>• Target perbaikan minimum 0.70.<br>• Pantau secara berkala.</div>'

    if max_v >= 0.7:
        h += f'<div class="rec-item rec-success"><strong>✅ Aspek Terkuat: {max_f} ({max_v:.2f})</strong><br>'
        h += '• Pertahankan sebagai standar kinerja.<br>• Jadikan best practice.</div>'
    else:
        h += f'<div class="rec-item rec-warning"><strong>📌 Semua Aspek Di Bawah Standar</strong><br>'
        h += f'Nilai tertinggi {max_f} hanya {max_v:.2f}. Tingkatkan secara bertahap.</div>'

    if inc > 5 or pr > 0.6:
        h += f'<div class="rec-item rec-warning"><strong>🚨 Perhatian Khusus</strong><br>'
        h += f'Ditemukan <b>{inc} insiden</b> dan risiko historis <b>{pr:.2f}</b>. Perlu kontinjensi cadangan.</div>'
    else:
        h += f'<div class="rec-item rec-info"><strong>ℹ️ Status Risiko Tambahan</strong><br>'
        h += f'Insiden ({inc}) dan risiko historis ({pr:.2f}) masih terkendali.</div>'
    return h


# ─── Session State ────────────────────────────────────────────────────────────
if 'latest_record' not in st.session_state:
    st.session_state.latest_record = None


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / title area
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.2rem; padding-bottom:1rem;
                border-bottom:1px solid rgba(255,255,255,0.08);">
        <div style="width:52px;height:52px;background:linear-gradient(135deg,#2563eb,#1d4ed8);
                    border-radius:14px;display:inline-flex;align-items:center;justify-content:center;
                    font-size:1.5rem; margin-bottom:0.6rem;
                    box-shadow:0 4px 15px rgba(37,99,235,0.4);">🔷</div>
        <div style="color:#f1f5f9 !important;font-weight:800;font-size:0.9rem;letter-spacing:0.5px;">
            INPUT DATA PEMASOK
        </div>
        <div style="color:#64748b !important;font-size:0.72rem;margin-top:2px;">
            Isi semua field lalu klik Prediksi
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("input_form", clear_on_submit=False):

        with st.expander("💰 Kinerja Keuangan", expanded=True):
            financial = st.slider("Financial Stability", 0.0, 1.0, 0.71, 0.01,
                                  help="Stabilitas keuangan pemasok (0–1)")

        with st.expander("⚙️ Kinerja Operasional", expanded=True):
            delivery      = st.slider("Delivery Performance", 0.0, 1.0, 0.70, 0.01)
            quality       = st.slider("Quality Compliance",   0.0, 1.0, 0.70, 0.01)
            regulatory    = st.slider("Regulatory Adherence", 0.0, 1.0, 0.70, 0.01)
            sustainability = st.slider("Sustainability Score", 0.0, 1.0, 0.70, 0.01)

        with st.expander("⚠️ Riwayat & Risiko", expanded=True):
            past_risk = st.slider("Past Risk Level", 0.0, 1.0, 0.30, 0.01)

        with st.expander("📊 Metrik Tambahan", expanded=True):
            erp_transactions = st.number_input("ERP Transactions", min_value=0, max_value=1000,
                                               value=300, step=1)
            incidents        = st.number_input("Incidents Count",  min_value=0, max_value=50,
                                               value=2,   step=1)
            mcdm_score       = st.slider("MCDM Score", 0.0, 1.0, 0.60, 0.01)

        submitted = st.form_submit_button("🔍  Prediksi Risiko", use_container_width=True)


# ─── Prediction Logic ─────────────────────────────────────────────────────────
if submitted and model is not None:
    input_data = pd.DataFrame([{
        'Financial_Stability_Score':  float(financial),
        'Delivery_Performance_Score': float(delivery),
        'Quality_Compliance_Score':   float(quality),
        'Regulatory_Adherence_Score': float(regulatory),
        'Sustainability_Score':       float(sustainability),
        'Past_Risk_Level':            float(past_risk),
        'ERP_Transactions':           float(erp_transactions),
        'Incidents_Count':            float(incidents),
        'MCDM_Score':                 float(mcdm_score)
    }]).astype(np.float64)

    prediksi   = model.predict(input_data)[0]
    proba      = model.predict_proba(input_data)[0]
    proba_low  = float(proba[0])
    proba_high = float(proba[1])

    st.session_state.latest_record = {
        'financial': financial, 'delivery': delivery, 'quality': quality,
        'regulatory': regulatory, 'sustainability': sustainability,
        'past_risk': past_risk, 'erp_transactions': erp_transactions,
        'incidents': incidents, 'mcdm_score': mcdm_score,
        'Prediksi': 'High Risk' if prediksi == 1 else 'Low Risk',
        'prediksi_val': int(prediksi),
        'Prob_High': proba_high, 'Prob_Low': proba_low,
        'feature_importances': model.feature_importances_.tolist(),
    }

latest = st.session_state.latest_record


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <div>
        <h1>🔷 Supply Chain Risk Monitor</h1>
        <p>Sistem Peringatan Dini Risiko Pemasok · XGBoost · 9 Fitur</p>
    </div>
    <div class="header-time">🕐 {get_indo_timestamp()}</div>
</div>
""", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊  Dashboard", "ℹ️  Tentang Model"])


# ══════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════
with tab1:
    if latest:
        draw_kpi_metrics(latest)

        col_g, col_d = st.columns([1, 1])

        with col_g:
            with st.container(border=True):
                st.markdown('<div class="sec-title">📈 Ringkasan Risiko</div>', unsafe_allow_html=True)
                fig = create_gauge(latest['Prob_High'] * 100)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                is_h = latest['prediksi_val'] == 1
                st.markdown(f"""
                <div class="alert-box {'alert-high' if is_h else 'alert-low'}">
                    <span style="font-size:1.2rem;">{'🚨' if is_h else '✅'}</span>
                    <div>
                        <strong>{'Risiko Tinggi — Perlu Tindakan!' if is_h else 'Risiko Rendah — Pemasok Aman'}</strong><br>
                        {'Segera lakukan evaluasi dan mitigasi rantai pasok.' if is_h
                          else 'Pemasok ini tergolong aman. Tetap pantau secara rutin.'}
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_d:
            with st.container(border=True):
                st.markdown('<div class="sec-title">🍩 Distribusi Probabilitas</div>', unsafe_allow_html=True)
                st.altair_chart(draw_donut_chart(latest['Prob_Low'], latest['Prob_High']),
                                use_container_width=True)

                st.markdown(f"""
                <div style="margin-top:0.5rem;">
                    <div style="display:flex;justify-content:space-between;
                                font-size:0.78rem;font-weight:600;color:#64748b;margin-bottom:4px;">
                        <span>🟢 Low Risk</span><span>{latest['Prob_Low']*100:.1f}%</span>
                    </div>
                    <div class="bar-track">
                        <div class="bar-fill bar-green" style="width:{latest['Prob_Low']*100:.1f}%;"></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;
                                font-size:0.78rem;font-weight:600;color:#64748b;margin:8px 0 4px 0;">
                        <span>🔴 High Risk</span><span>{latest['Prob_High']*100:.1f}%</span>
                    </div>
                    <div class="bar-track">
                        <div class="bar-fill bar-red" style="width:{latest['Prob_High']*100:.1f}%;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="sec-title">📊 Faktor Penyebab Risiko (Feature Importance)</div>',
                        unsafe_allow_html=True)
            st.altair_chart(draw_feature_importance_chart(latest), use_container_width=True)

        col_s, col_r = st.columns([1, 1])

        with col_s:
            with st.container(border=True):
                st.markdown('<div class="sec-title">📋 Detail Skor Pemasok</div>', unsafe_allow_html=True)
                draw_score_rows(latest)

        with col_r:
            with st.container(border=True):
                st.markdown('<div class="sec-title">💡 Rekomendasi</div>', unsafe_allow_html=True)
                st.markdown(get_recommendation_html(latest), unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="welcome-banner">
            <h2>👋 Selamat Datang!</h2>
            <p>Isi data pemasok di sidebar kiri, lalu klik <strong>🔍 Prediksi Risiko</strong><br>
               untuk memulai analisis risiko rantai pasok secara komprehensif.</p>
        </div>""", unsafe_allow_html=True)

        ca, cb, cc = st.columns(3)
        for col, icon, title, desc in [
            (ca, "🤖", "XGBoost Model", "Algoritma gradient boosting dengan akurasi ~91% pada data uji"),
            (cb, "📊", "9 Fitur Analisis", "Financial, Delivery, Quality, Regulatory, Sustainability, dan lebih"),
            (cc, "⚡", "Prediksi Real-time", "Hasil instan dengan visualisasi gauge, donut chart & rekomendasi"),
        ]:
            with col:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="text-align:center;padding:0.5rem 0;">
                        <div style="font-size:2rem;margin-bottom:0.4rem;">{icon}</div>
                        <div style="font-weight:700;color:#1e293b;font-size:0.95rem;">{title}</div>
                        <div style="font-size:0.8rem;color:#64748b;margin-top:4px;">{desc}</div>
                    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# TAB 2 — TENTANG MODEL
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown("<h3 style='margin:0 0 1rem 0;color:#1e293b;font-weight:800;'>ℹ️ Tentang Model</h3>",
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("**⚙️ Spesifikasi Model**")
            st.markdown("""
| Parameter | Nilai |
|-----------|-------|
| Algoritma | XGBoost |
| Jumlah Fitur | 9 Fitur |
| Akurasi Test | ~91% |
| F1-Score Test | ~91% |
| AUC-ROC | ~0.96 |
| Max Depth | 4 |
| Learning Rate | 0.1 |
| N Estimators | 100 |
""")

    with c2:
        with st.container(border=True):
            st.markdown("**📋 Fitur yang Digunakan**")
            fitur_list = [
                ("💰", "Financial Stability Score",  "Stabilitas keuangan pemasok"),
                ("🚚", "Delivery Performance Score", "Ketepatan waktu pengiriman"),
                ("✅", "Quality Compliance Score",   "Kepatuhan kualitas produk"),
                ("📜", "Regulatory Adherence Score", "Kepatuhan regulasi"),
                ("🌿", "Sustainability Score",       "Skor keberlanjutan"),
                ("⚠️", "Past Risk Level",            "Tingkat risiko historis"),
                ("💻", "ERP Transactions",           "Volume transaksi ERP"),
                ("🚨", "Incidents Count",            "Jumlah insiden operasional"),
                ("📊", "MCDM Score",                 "Skor multi-criteria decision"),
            ]
            for icon, name, desc in fitur_list:
                st.markdown(f"**{icon} {name}** — {desc}")

    with st.container(border=True):
        st.markdown("**📖 Cara Membaca Hasil**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""
🟢 **LOW RISK (< 40%)**
Pemasok aman dan terpercaya. Pantau rutin setiap kuartal.
""")
        with col_b:
            st.markdown("""
🟡 **MEDIUM RISK (40–70%)**
Perlu perhatian khusus. Lakukan review bulanan dan audit selektif.
""")
        with col_c:
            st.markdown("""
🔴 **HIGH RISK (> 70%)**
Tindakan segera diperlukan. Pertimbangkan alternatif pemasok.
""")

    st.markdown(
        "<p style='color:#94a3b8;font-size:0.75rem;text-align:center;margin-top:1rem;'>"
        "Dibuat untuk Progres Report MRP · Kelompok 8 · 2024"
        "</p>", unsafe_allow_html=True)