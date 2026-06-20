import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
import os
import altair as alt

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="Sistem Peringatan Dini Risiko Pemasok",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .risk-low {
        background: linear-gradient(135deg, #d4edda, #b7e4c7);
        border-left: 6px solid #28a745;
    }
    .risk-high {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border-left: 6px solid #dc3545;
    }
    .stButton > button {
        background-color: #2a5298;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #1e3c72;
        transform: scale(1.02);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔔 Sistem Peringatan Dini Risiko Pemasok</h1>
    <p style="margin:0; opacity:0.9;">Berbasis XGBoost dengan 5 Fitur Utama | Supply Chain Risk Management</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD MODEL & SCALER
# ==========================================
@st.cache_resource
def load_model():
    model_file = 'model_xgb_5fitur_ok.pkl'
    scaler_file = 'scaler_5fitur_ok.pkl'
    
    if os.path.exists(model_file) and os.path.exists(scaler_file):
        model = joblib.load(model_file)
        scaler = joblib.load(scaler_file)
        return model, scaler
    else:
        st.error("""
        ❌ **File model atau scaler tidak ditemukan!**
        
        **Solusi:**
        1. Pastikan file `model_xgb_5fitur_ok.pkl` dan `scaler_5fitur_ok.pkl` ada di folder yang sama dengan `app.py`.
        2. Atau upload kedua file di bawah ini:
        """)
        
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            uploaded_model = st.file_uploader("Upload file model (.pkl)", type=['pkl'], key='model_upload')
        with col_up2:
            uploaded_scaler = st.file_uploader("Upload file scaler (.pkl)", type=['pkl'], key='scaler_upload')
        
        if uploaded_model and uploaded_scaler:
            with open(model_file, 'wb') as f:
                f.write(uploaded_model.getbuffer())
            with open(scaler_file, 'wb') as f:
                f.write(uploaded_scaler.getbuffer())
            st.success("✅ File berhasil diupload! Silakan refresh halaman.")
            st.stop()
        return None, None

model, scaler = load_model()
if model is None:
    st.stop()

# ==========================================
# 3. SESSION STATE UNTUK HISTORY
# ==========================================
if 'history' not in st.session_state:
    st.session_state.history = []

# ==========================================
# 4. SIDEBAR INPUT DATA
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.header("📥 Input Data Pemasok")

with st.sidebar.form("input_form", clear_on_submit=False):
    st.markdown("**Masukkan skor pemasok (0 - 1):**")
    
    col1, col2 = st.columns(2)
    with col1:
        financial = st.slider("💰 Financial", 0.0, 1.0, 0.7, 0.01, help="Stabilitas keuangan pemasok")
        delivery = st.slider("🚚 Delivery", 0.0, 1.0, 0.7, 0.01, help="Ketepatan waktu pengiriman")
        quality = st.slider("✅ Quality", 0.0, 1.0, 0.7, 0.01, help="Kepatuhan kualitas produk")
    with col2:
        regulatory = st.slider("📜 Regulatory", 0.0, 1.0, 0.7, 0.01, help="Kepatuhan terhadap regulasi")
        sustainability = st.slider("🌿 Sustainability", 0.0, 1.0, 0.7, 0.01, help="Skor keberlanjutan")
    
    submitted = st.form_submit_button("🔍 Prediksi Risiko", use_container_width=True)

# ==========================================
# 5. LOGIKA PREDIKSI (jika tombol ditekan)
# ==========================================
if submitted:
    # Input array
    input_data = np.array([[financial, delivery, quality, regulatory, sustainability]])
    
    # Normalisasi
    feature_names = ['Financial_Stability_Score', 'Delivery_Performance_Score', 
                     'Quality_Compliance_Score', 'Regulatory_Adherence_Score', 
                     'Sustainability_Score']
    input_scaled = scaler.transform(pd.DataFrame(input_data, columns=feature_names))
    
    # Prediksi
    prediksi = model.predict(input_scaled)[0]
    proba = model.predict_proba(input_scaled)[0]
    proba_low = float(proba[0])
    proba_high = float(proba[1])
    
    # ========== HASIL PREDIKSI ==========
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if prediksi == 0:
            st.markdown("""
            <div class="risk-card risk-low">
                <h2 style="margin:0; color:#155724;">✅ Risiko Rendah (Low)</h2>
                <p style="margin:5px 0 0 0; font-size:1.1rem;">Pemasok ini tergolong aman, namun tetap perlu dipantau.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="risk-card risk-high">
                <h2 style="margin:0; color:#721c24;">⚠️ Risiko Tinggi (High)</h2>
                <p style="margin:5px 0 0 0; font-size:1.1rem;">Segera lakukan mitigasi! Pemasok ini berpotensi mengganggu rantai pasok.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("📊 Probabilitas")
        col_met1, col_met2 = st.columns(2)
        col_met1.metric("🟢 Low", f"{proba_low*100:.1f}%")
        col_met2.metric("🔴 High", f"{proba_high*100:.1f}%")
        st.progress(proba_high, text=f"Tingkat Risiko: {proba_high*100:.1f}%")
    
    with col2:
        proba_df = pd.DataFrame({
            'Kategori': ['Low', 'High'],
            'Probabilitas': [proba_low, proba_high]
        })
        chart = alt.Chart(proba_df).mark_bar().encode(
            x='Kategori',
            y='Probabilitas',
            color=alt.Color('Kategori', scale=alt.Scale(domain=['Low', 'High'], range=['#28a745', '#dc3545']))
        ).properties(title='Probabilitas Risiko')
        st.altair_chart(chart, use_container_width=True)
    
    # ========== TABEL SKOR ==========
    st.markdown("---")
    st.subheader("📋 Detail Skor Pemasok")
    scores = {
        'Fitur': ['💰 Financial', '🚚 Delivery', '✅ Quality', '📜 Regulatory', '🌿 Sustainability'],
        'Skor': [financial, delivery, quality, regulatory, sustainability],
        'Status': []
    }
    for s in scores['Skor']:
        if s >= 0.7:
            scores['Status'].append('🟢 Baik')
        elif s >= 0.4:
            scores['Status'].append('🟡 Sedang')
        else:
            scores['Status'].append('🔴 Buruk')
    df_scores = pd.DataFrame(scores)
    st.dataframe(df_scores, use_container_width=True, hide_index=True)
    
    # ========== FEATURE IMPORTANCE ==========
    st.markdown("---")
    st.subheader("📊 Faktor Penyebab Risiko (Feature Importance)")
    short_names = ['Financial', 'Delivery', 'Quality', 'Regulatory', 'Sustainability']
    importance = model.feature_importances_
    feat_imp = pd.Series(importance, index=short_names).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(feat_imp.index, feat_imp.values, color='coral')
    ax.set_xlabel('Tingkat Pengaruh')
    ax.set_title('Kontribusi Fitur terhadap Risiko')
    for bar, val in zip(bars, feat_imp.values):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center')
    st.pyplot(fig)
    
    # ========== SHAP ==========
    st.markdown("---")
    st.subheader("🧠 Mengapa Pemasok Ini Diprediksi Seperti Itu? (SHAP)")
    st.caption("Grafik di bawah menunjukkan pengaruh setiap fitur terhadap hasil prediksi. Panah ke kanan (merah) = meningkatkan risiko High, panah ke kiri (biru) = menurunkan risiko.")
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(input_scaled)
        shap.initjs()
        force_plot = shap.force_plot(
            explainer.expected_value,
            shap_values[0],
            input_scaled[0],
            feature_names=short_names,
            matplotlib=True,
            show=False
        )
        st.pyplot(force_plot)
    except Exception as e:
        st.warning(f"⚠️ SHAP plot tidak dapat ditampilkan: {e}")
    
    # ========== REKOMENDASI ==========
    st.markdown("---")
    st.subheader("💡 Rekomendasi Mitigasi")
    scores_dict = {
        '💰 Financial Stability': financial,
        '🚚 Delivery Performance': delivery,
        '✅ Quality Compliance': quality,
        '📜 Regulatory Adherence': regulatory,
        '🌿 Sustainability': sustainability
    }
    min_feat = min(scores_dict, key=scores_dict.get)
    max_feat = max(scores_dict, key=scores_dict.get)
    min_val = scores_dict[min_feat]
    max_val = scores_dict[max_feat]
    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.warning(f"""
        **⚠️ Fitur Terlemah:**  
        **{min_feat}** dengan skor **{min_val:.2f}**
        
        **Rekomendasi:**
        - Segera lakukan audit mendalam pada aspek ini.
        - Tetapkan target perbaikan minimum 0.7.
        - Pantau perkembangan secara mingguan.
        """)
    with col_rec2:
        if max_val >= 0.7:
            st.success(f"""
            **✅ Fitur Terkuat:**  
            **{max_feat}** dengan skor **{max_val:.2f}**
            
            **Rekomendasi:**
            - Pertahankan kinerja ini sebagai standar.
            - Jadikan best practice untuk pemasok lain.
            """)
        else:
            st.info(f"""
            **📌 Catatan:**  
            Semua fitur masih di bawah standar (0.7).  
            **Prioritas utama:** Perbaiki **{min_feat}** terlebih dahulu, lalu tingkatkan fitur lainnya secara bertahap.
            """)
    
    # ========== SIMPAN KE RIWAYAT ==========
    st.markdown("---")
    col_hist1, col_hist2 = st.columns([3, 1])
    with col_hist1:
        if st.button("💾 Simpan Prediksi ke Riwayat", use_container_width=True):
            record = {
                'Financial': financial,
                'Delivery': delivery,
                'Quality': quality,
                'Regulatory': regulatory,
                'Sustainability': sustainability,
                'Prediksi': 'High' if prediksi == 1 else 'Low',
                'Prob_High': proba_high
            }
            st.session_state.history.append(record)
            st.success("✅ Berhasil disimpan ke riwayat! Halaman akan refresh...")
            st.rerun()  # ← INI YANG MEMBUAT RIWAYAT LANGSUNG MUNCUL

# ==========================================
# 6. TAMPILKAN RIWAYAT (SELALU MUNCUL DI BAWAH)
# ==========================================
st.markdown("---")
st.subheader("📜 Riwayat Prediksi (Sesi Ini)")

if len(st.session_state.history) > 0:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
    
    col_del1, col_del2 = st.columns([3, 1])
    with col_del1:
        if st.button("🗑️ Hapus Semua Riwayat", use_container_width=True):
            st.session_state.history = []
            st.rerun()
else:
    st.info("Belum ada riwayat prediksi. Lakukan prediksi terlebih dahulu, lalu klik 'Simpan Prediksi ke Riwayat'.")

# ==========================================
# 7. SIDEBAR INFORMASI MODEL
# ==========================================
st.sidebar.markdown("---")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=40)
st.sidebar.subheader("📌 Informasi Model")

st.sidebar.info("""
**⚙️ Spesifikasi Model:**
- **Algoritma:** XGBoost
- **Fitur:** 5 (Financial, Delivery, Quality, Regulatory, Sustainability)
- **Data Latih:** 80% (dengan SMOTE)
- **Data Uji:** 20%
- **Akurasi:** ~95%
- **AUC:** ~0.99

**🔍 Interpretasi SHAP:**
Nilai **merah** pada grafik SHAP berarti fitur tersebut **meningkatkan** risiko High.  
Nilai **biru** berarti **menurunkan** risiko.
""")

st.sidebar.markdown("---")
st.sidebar.caption("Dibuat untuk Progres Report MRP | Kelompok 8")