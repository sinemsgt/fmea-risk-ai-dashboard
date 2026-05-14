"""
==============================================================================
MELEZ RİSK ÖNCELİKLENDİRME MODELİ — STREAMLİT WEB UYGULAMASI
Bütünleşik FMEA ve Makine Öğrenimi | Kablo Donanımı Üretimi
------------------------------------------------------------------------------
Kütahya Dumlupınar Üniversitesi | Endüstri Mühendisliği Bölümü
Öğrenciler: Sinem SÖĞÜT, Elmas Eda ELİBOL, Ebrar DEMİR
Danışman  : Prof. Dr. Şafak KOCAKALAY
==============================================================================
ÇALIŞTIRMAK İÇİN:
    pip install streamlit pandas numpy matplotlib seaborn scikit-learn openpyxl
    streamlit run app.py
==============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from io import BytesIO
import json

import streamlit as st
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import (
    mean_absolute_error, r2_score,
    classification_report, confusion_matrix
)
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from modules.data import *
from modules.ml_models import *
from database import kayit_ekle, kayitlari_getir
from pdf_report import pdf_rapor_olustur

# ─── SAYFA AYARLARI ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FMEA & ML Dashboard — Kablo Donanımı",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Arka plan */
.stApp {
    background: #0a0e1a;
    color: #e8eaf0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1220;
    border-right: 1px solid #1e2d50;
}

/* Başlık kutusu */
.hero-box {
    background: linear-gradient(135deg, #0d1f3c 0%, #091429 60%, #0a1a33 100%);
    border: 1px solid #1e3a6e;
    border-left: 4px solid #2e75b6;
    border-radius: 8px;
    padding: 24px 30px 20px 30px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-box::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(46,117,182,0.12) 0%, transparent 70%);
}
.hero-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.45rem;
    font-weight: 600;
    color: #5ba4e6;
    letter-spacing: 0.03em;
    margin: 0 0 4px 0;
}
.hero-sub {
    font-size: 0.82rem;
    color: #6b7fa8;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.05em;
}

/* Metrik kartları */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
.metric-card {
    background: #0d1626;
    border: 1px solid #1a2d50;
    border-top: 3px solid;
    border-radius: 6px;
    padding: 16px 18px;
    transition: transform 0.15s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card.blue  { border-top-color: #2e75b6; }
.metric-card.red   { border-top-color: #c00000; }
.metric-card.green { border-top-color: #2a9d8f; }
.metric-card.amber { border-top-color: #e76f51; }
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #5a7098;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #e8eaf0;
    line-height: 1;
}
.metric-delta {
    font-size: 0.72rem;
    color: #4a6080;
    margin-top: 4px;
}

/* Section başlıkları */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    color: #2e75b6;
    text-transform: uppercase;
    border-bottom: 1px solid #1a2d50;
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

/* Risk badge'ler */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
}
.badge-kritik  { background: #3d0000; color: #ff6b6b; border: 1px solid #c00000; }
.badge-yuksek  { background: #3d1a00; color: #ffab76; border: 1px solid #e76f51; }
.badge-orta    { background: #2d2200; color: #ffd06b; border: 1px solid #d4a017; }
.badge-dusuk   { background: #003d20; color: #6bffb8; border: 1px solid #2a9d8f; }

/* Tahmin kutusu */
.pred-box {
    background: #091020;
    border: 1px solid #1a2d50;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}
.pred-rpn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1;
}

/* Info kutusu */
.info-box {
    background: #091829;
    border: 1px solid #1a3a5c;
    border-left: 3px solid #2e75b6;
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 0.83rem;
    color: #8aa8cc;
    margin: 10px 0;
}

/* Tablo stili */
.dataframe { font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VERİ & MODEL TANIMLAMALARI (önbelleğe alınır)
# ══════════════════════════════════════════════════════════════════════════════




@st.cache_data
def veri_seti_olustur(n=211, seed=42):
    np.random.seed(seed)
    kayitlar = []
    agirliklar = [25, 20, 22, 18, 15, 24, 14, 20, 17]
    agirliklar = [a / sum(agirliklar) for a in agirliklar]
    kod_listesi = list(HATA_TURLERI.keys())
    sayilar = np.round(np.array(agirliklar) * n).astype(int)
    sayilar[-1] += n - sayilar.sum()

    kayit_id = 1
    for kod, sayi in zip(kod_listesi, sayilar):
        ht = HATA_TURLERI[kod]
        for _ in range(sayi):
            O = int(np.random.randint(ht["O_aralik"][0], ht["O_aralik"][1] + 1))
            S = int(np.random.randint(ht["S_aralik"][0], ht["S_aralik"][1] + 1))
            D = int(np.random.randint(ht["D_aralik"][0], ht["D_aralik"][1] + 1))
            RPN = O * S * D
            aRPN = round(0.5 * S + 0.3 * O + 0.2 * D, 2)
            aciklama = np.random.choice(ht["aciklamalar"])
            ekler = ["", " tekrar oluştu", " acil inceleme gerekli",
                     " 3. kez aynı problem", " vardiya sonu raporlandı"]
            aciklama += np.random.choice(ekler)
            kayitlar.append({
                "Kayit_ID": f"REC-{kayit_id:04d}",
                "Hata_Kodu": kod,
                "Hata_Turu": ht["isim"],
                "Proses_Adimi": ht["proses"],
                "Etki": ht["etki"],
                "Hata_Aciklamasi": aciklama,
                "O": O, "S": S, "D": D,
                "RPN": RPN,
                "Agirlikli_RPN": aRPN,
                "Istasyon": np.random.choice(ISTASYON_LISTESI),
                "Operator_ID": np.random.choice(OPERATORLER),
                "Vardiya": np.random.choice(VARDIYALAR),
                "Ay": np.random.randint(1, 11),
                "Hafta": np.random.randint(1, 41),
            })
            kayit_id += 1

    df = pd.DataFrame(kayitlar)
    df["Risk_Seviyesi"] = pd.cut(
        df["RPN"], bins=[0, 100, 200, 500, 1000],
        labels=["Düşük", "Orta", "Yüksek", "Kritik"]
    )
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


@st.cache_data
def fmea_analizi(df):
    ozet = df.groupby(["Hata_Kodu", "Hata_Turu", "Proses_Adimi"]).agg(
        Kayit_Sayisi=("RPN", "count"),
        Ort_O=("O", "mean"), Ort_S=("S", "mean"), Ort_D=("D", "mean"),
        Ort_RPN=("RPN", "mean"), Max_RPN=("RPN", "max"),
        Ort_aRPN=("Agirlikli_RPN", "mean"),
    ).reset_index()
    for col in ["Ort_O", "Ort_S", "Ort_D", "Ort_RPN", "Ort_aRPN"]:
        ozet[col] = ozet[col].round(2)
    ozet = ozet.sort_values("Ort_RPN", ascending=False).reset_index(drop=True)
    ozet["RPN_Sirasi"] = ozet.index + 1
    ozet["Onlem"] = ozet["Hata_Kodu"].map({k: v["onlem"] for k, v in HATA_TURLERI.items()})
    return ozet










def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# UYGULAMA — SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size:0.9rem;
                color:#5ba4e6; font-weight:600; letter-spacing:0.05em; margin-bottom:4px;'>
        ⚡ FMEA & ML
    </div>
    <div style='font-size:0.72rem; color:#4a6080; margin-bottom:20px; font-family: IBM Plex Mono;'>
        Kablo Donanımı Analiz Platformu
    </div>
    """, unsafe_allow_html=True)

    sayfa = st.radio(
        "Modül",
        ["📊 Genel Bakış",
         "📋 FMEA Analizi",
         "🔤 NLP Sınıflandırıcı",
         "🌲 Random Forest",
         "🔍 Pattern Recognition",
         "🔮 Canlı RPN Tahmini",
         "🗂 Kayıtlı Analizler",
         "📤 Firma Verisi Yükle",
         "⚙️ Vardiya Ayarları"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem; color:#3a5070; font-family: IBM Plex Mono;'>
    AYARLAR
    </div>""", unsafe_allow_html=True)
    n_kayit = st.slider("Kayıt Sayısı", 100, 500, 211, 10)
    seed = st.number_input("Random Seed", 0, 999, 42)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.68rem; color:#2a4060; font-family: IBM Plex Mono; line-height:1.6;'>
    Kütahya Dumlupınar Üniv.<br>
    Endüstri Mühendisliği<br>
    <span style='color:#1a3050;'>── 2025 ──</span>
    </div>""", unsafe_allow_html=True)

# ─── VERİ YÜKLEME ─────────────────────────────────────────────────────────────
with open("vardiyalar.json", "r", encoding="utf-8") as f:
    vardiya_listesi = json.load(f)

df = veri_seti_olustur(n=n_kayit, seed=int(seed))
fmea_ozet = fmea_analizi(df)

# ══════════════════════════════════════════════════════════════════════════════
# SAYFA: GENEL BAKIŞ
# ══════════════════════════════════════════════════════════════════════════════

if sayfa == "📊 Genel Bakış":

    st.markdown("""
    <div class='hero-box'>
        <div class='hero-title'>MELEZ RİSK ÖNCELİKLENDİRME MODELİ</div>
        <div class='hero-sub'>BÜTÜNLEŞİK FMEA & MAKİNE ÖĞRENİMİ — KABLO DONANIMI ÜRETİMİ</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Kartları ──
    kritik = int((df["RPN"] >= 200).sum())
    max_rpn = int(df["RPN"].max())
    ort_rpn = float(df["RPN"].mean())
    en_riskli = fmea_ozet.iloc[0]["Hata_Kodu"]

    st.markdown(f"""
    <div class='metric-grid'>
        <div class='metric-card blue'>
            <div class='metric-label'>Toplam Kayıt</div>
            <div class='metric-value'>{len(df)}</div>
            <div class='metric-delta'>{df['Hata_Kodu'].nunique()} hata türü</div>
        </div>
        <div class='metric-card red'>
            <div class='metric-label'>Kritik Kayıt (RPN≥200)</div>
            <div class='metric-value'>{kritik}</div>
            <div class='metric-delta'>%{kritik/len(df)*100:.1f} oranında</div>
        </div>
        <div class='metric-card amber'>
            <div class='metric-label'>Ortalama RPN</div>
            <div class='metric-value'>{ort_rpn:.0f}</div>
            <div class='metric-delta'>Maks: {max_rpn}</div>
        </div>
        <div class='metric-card green'>
            <div class='metric-label'>En Riskli Hata</div>
            <div class='metric-value' style='font-size:1.4rem;'>{en_riskli}</div>
            <div class='metric-delta'>{fmea_ozet.iloc[0]['Hata_Turu'][:22]}…</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Grafikler ──
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='section-header'>▸ PARETO — ORTALAMA RPN'E GÖRE HATA TÜRLERİ</div>", unsafe_allow_html=True)
        fig, ax1 = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#0a0e1a")
        ax1.set_facecolor("#0d1220")
        renkler = plt.cm.RdYlGn_r(np.linspace(0.15, 0.85, len(fmea_ozet)))
        bars = ax1.bar(fmea_ozet["Hata_Kodu"], fmea_ozet["Ort_RPN"],
                       color=renkler, edgecolor="#1a2d50", linewidth=0.8)
        ax2 = ax1.twinx()
        kum = fmea_ozet["Ort_RPN"].cumsum() / fmea_ozet["Ort_RPN"].sum() * 100
        ax2.plot(fmea_ozet["Hata_Kodu"], kum, "o--", color="#5ba4e6",
                 linewidth=2, markersize=6)
        ax2.axhline(80, color="#ff6961", linestyle=":", linewidth=1.2, alpha=0.6)
        ax2.set_ylabel("Kümülatif %", color="#5ba4e6", fontsize=9)
        ax2.tick_params(colors="#5ba4e6", labelsize=8)
        ax2.set_ylim(0, 115)
        ax1.set_ylabel("Ortalama RPN", color="#8aa8cc", fontsize=9)
        ax1.tick_params(axis="x", colors="#8aa8cc", labelsize=9)
        ax1.tick_params(axis="y", colors="#8aa8cc", labelsize=8)
        for spine in ax1.spines.values():
            spine.set_edgecolor("#1a2d50")
        for bar, val in zip(bars, fmea_ozet["Ort_RPN"]):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                     f"{val:.0f}", ha="center", va="bottom", fontsize=8,
                     color="white", fontweight="bold")
        plt.tight_layout()
        st.image(fig_to_bytes(fig), use_container_width=True)
        plt.close()

    with col2:
        st.markdown("<div class='section-header'>▸ RİSK SEVİYESİ</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(4.5, 4))
        fig.patch.set_facecolor("#0a0e1a")
        ax.set_facecolor("#0d1220")
        risk_say = df["Risk_Seviyesi"].value_counts()
        renkler_risk = {"Düşük": "#2a9d8f", "Orta": "#d4a017", "Yüksek": "#e76f51", "Kritik": "#c00000"}
        w_renkler = [renkler_risk.get(r, "grey") for r in risk_say.index]
        wedges, texts, autotexts = ax.pie(
            risk_say, labels=risk_say.index, autopct="%1.1f%%",
            colors=w_renkler, startangle=140,
            textprops={"fontsize": 9, "color": "#c8d8f0"},
            pctdistance=0.75, wedgeprops={"linewidth": 2, "edgecolor": "#0a0e1a"}
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")
        plt.tight_layout()
        st.image(fig_to_bytes(fig), use_container_width=True)
        plt.close()

    # ── Aylık Trend ──
    st.markdown("<div class='section-header'>▸ AYLIK ORTALAMA RPN TRENDİ</div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(14, 3.2))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#0d1220")
    aylik = df.groupby("Ay")["RPN"].mean()
    ax.plot(aylik.index, aylik.values, "o-", color="#2e75b6", linewidth=2.5, markersize=9)
    ax.fill_between(aylik.index, aylik.values, alpha=0.15, color="#2e75b6")
    for ay, val in zip(aylik.index, aylik.values):
        ax.annotate(f"{val:.0f}", (ay, val), textcoords="offset points",
                    xytext=(0, 10), ha="center", color="#9dc3e6", fontsize=8.5)
    ax.set_xlabel("Ay", color="#4a6080")
    ax.set_ylabel("Ort. RPN", color="#4a6080")
    ax.set_xticks(aylik.index)
    ax.tick_params(colors="#4a6080")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1a2d50")
    ax.grid(axis="y", color="#1a2d50", linewidth=0.5)
    plt.tight_layout()
    st.image(fig_to_bytes(fig), use_container_width=True)
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# SAYFA: FMEA ANALİZİ
# ══════════════════════════════════════════════════════════════════════════════

elif sayfa == "📋 FMEA Analizi":
    st.markdown("<div class='section-header'>▸ FMEA ÖZET TABLOSU — RPN'E GÖRE RİSK ÖNCELİKLENDİRMESİ</div>", unsafe_allow_html=True)

    def risk_renk(rpn):
        if rpn >= 300:
            return "🔴 Kritik"
        elif rpn >= 200:
            return "🟠 Yüksek"
        elif rpn >= 100:
            return "🟡 Orta"
        return "🟢 Düşük"

    goster = fmea_ozet[["RPN_Sirasi", "Hata_Kodu", "Hata_Turu",
                          "Kayit_Sayisi", "Ort_O", "Ort_S", "Ort_D",
                          "Ort_RPN", "Max_RPN", "Onlem"]].copy()
    goster["Risk"] = goster["Ort_RPN"].apply(risk_renk)
    st.dataframe(
        goster.rename(columns={
            "RPN_Sirasi": "#", "Hata_Kodu": "Kod", "Hata_Turu": "Hata Türü",
            "Kayit_Sayisi": "Kayıt", "Ort_O": "Ort.O", "Ort_S": "Ort.S",
            "Ort_D": "Ort.D", "Ort_RPN": "Ort.RPN", "Max_RPN": "Max.RPN",
            "Onlem": "Önerilen Önlem"
        }),
        use_container_width=True, height=380, hide_index=True
    )

    st.markdown("<div class='section-header'>▸ GELENEKSEL VE AĞIRLIKLI RPN KARŞILAŞTIRMASI</div>", unsafe_allow_html=True)
    st.markdown("""<div class='info-box'>
    Geleneksel RPN = O × S × D  |  
    Ağırlıklı RPN = 0.5×S + 0.3×O + 0.2×D 
    (Literatür: yüksek şiddetli hatalar daha ağır ağırlıklandırılır)
    </div>""", unsafe_allow_html=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    for ax in axes:
        ax.set_facecolor("#0d1220")
        fig.patch.set_facecolor("#0a0e1a")

    x = np.arange(len(fmea_ozet))
    w = 0.35
    axes[0].bar(x - w/2, fmea_ozet["Ort_RPN"] / fmea_ozet["Ort_RPN"].max() * 100,
                w, label="Geleneksel RPN", color="#2e75b6", alpha=0.9)
    axes[0].bar(x + w/2, fmea_ozet["Ort_aRPN"] / fmea_ozet["Ort_aRPN"].max() * 100,
                w, label="Ağırlıklı RPN", color="#c00000", alpha=0.9)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(fmea_ozet["Hata_Kodu"], color="#8aa8cc", fontsize=9)
    axes[0].set_ylabel("Normalleştirilmiş Skor (%)", color="#8aa8cc")
    axes[0].tick_params(axis="y", colors="#4a6080")
    axes[0].legend(fontsize=9, facecolor="#0d1220", labelcolor="#8aa8cc")
    for spine in axes[0].spines.values():
        spine.set_edgecolor("#1a2d50")
    axes[0].set_title("Normalleştirilmiş RPN Karşılaştırması", color="#8aa8cc", fontsize=10)

    corr = df[["O", "S", "D", "RPN", "Agirlikli_RPN"]].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=axes[1],
                linewidths=0.5, annot_kws={"size": 9, "color": "white"},
                cbar_kws={"shrink": 0.8})
    axes[1].set_title("Korelasyon Matrisi", color="#8aa8cc", fontsize=10)
    axes[1].tick_params(colors="#8aa8cc")

    plt.tight_layout()
    st.image(fig_to_bytes(fig), use_container_width=True)
    plt.close()

    # İndirme butonu
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Ham_Veri", index=False)
        fmea_ozet.to_excel(w, sheet_name="FMEA_Ozet", index=False)
    st.download_button("⬇ FMEA Verisini Excel Olarak İndir",
                       data=buf.getvalue(),
                       file_name="fmea_analizi.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ══════════════════════════════════════════════════════════════════════════════
# SAYFA: NLP SINIFLANDIRICI
# ══════════════════════════════════════════════════════════════════════════════

elif sayfa == "🔤 NLP Sınıflandırıcı":
    st.markdown("<div class='section-header'>▸ TF-IDF + NAİVE BAYES — HATA KODU SINIFLANDIRICI</div>", unsafe_allow_html=True)
    st.markdown("""<div class='info-box'>
    Operatörün doğal dille girdiği hata açıklamasından otomatik olarak hata kodu (M01–M09) tahmin edilir.
    TF-IDF karakter n-gramları (2–4) özellik çıkarımı için kullanılır.
    </div>""", unsafe_allow_html=True)

    with st.spinner("NLP modeli eğitiliyor..."):
        nlp_model, nlp_vec, nlp_le, nlp_rapor, nlp_cv = nlp_modeli_egit(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Test Doğruluğu", f"%{nlp_rapor['accuracy']*100:.1f}")
    col2.metric("5-Fold CV Ortalaması", f"%{nlp_cv.mean()*100:.1f}")
    col3.metric("CV Standart Sapma", f"±{nlp_cv.std()*100:.1f}%")

    siniflar = nlp_le.classes_
    precisions = [nlp_rapor[s]["precision"] for s in siniflar]
    recalls    = [nlp_rapor[s]["recall"]    for s in siniflar]
    f1s        = [nlp_rapor[s]["f1-score"]  for s in siniflar]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for ax in axes:
        ax.set_facecolor("#0d1220")
        fig.patch.set_facecolor("#0a0e1a")

    x = np.arange(len(siniflar))
    w = 0.25
    axes[0].bar(x - w, precisions, w, label="Precision", color="#2e75b6")
    axes[0].bar(x,     recalls,    w, label="Recall",    color="#2a9d8f")
    axes[0].bar(x + w, f1s,        w, label="F1-Score",  color="#c00000")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(siniflar, color="#8aa8cc", fontsize=9)
    axes[0].set_ylim(0, 1.2)
    axes[0].set_ylabel("Skor", color="#8aa8cc")
    axes[0].tick_params(axis="y", colors="#4a6080")
    axes[0].legend(facecolor="#0d1220", labelcolor="#8aa8cc")
    axes[0].set_title("Sınıf Bazında Precision / Recall / F1", color="#8aa8cc")
    for spine in axes[0].spines.values():
        spine.set_edgecolor("#1a2d50")

    cv_renkler = ["#c00000" if s == nlp_cv.max() else "#2e75b6" for s in nlp_cv]
    axes[1].bar(range(1, 6), nlp_cv * 100, color=cv_renkler, edgecolor="#1a2d50")
    axes[1].axhline(nlp_cv.mean() * 100, color="#f4a261", linestyle="--",
                    linewidth=1.5, label=f"Ortalama: %{nlp_cv.mean()*100:.1f}")
    axes[1].set_xlabel("Fold", color="#8aa8cc")
    axes[1].set_ylabel("Doğruluk (%)", color="#8aa8cc")
    axes[1].tick_params(colors="#4a6080")
    axes[1].set_title("5-Fold Çapraz Doğrulama Sonuçları", color="#8aa8cc")
    axes[1].legend(facecolor="#0d1220", labelcolor="#8aa8cc")
    for spine in axes[1].spines.values():
        spine.set_edgecolor("#1a2d50")

    plt.tight_layout()
    st.image(fig_to_bytes(fig), use_container_width=True)
    plt.close()

    # Canlı test
    st.markdown("<div class='section-header'>▸ CANLI HATA AÇIKLAMASI TEST</div>", unsafe_allow_html=True)
    test_aciklama = st.text_input(
        "Hata açıklaması girin:",
        placeholder="Örn: terminal krimplemesi uygun değil yüksek direnç",
        label_visibility="collapsed"
    )
    if test_aciklama:
        x_vec = nlp_vec.transform([test_aciklama])
        pred_enc = nlp_model.predict(x_vec)[0]
        pred_kod = nlp_le.inverse_transform([pred_enc])[0]
        proba = nlp_model.predict_proba(x_vec)[0]
        guven = proba.max() * 100
        ht = HATA_TURLERI[pred_kod]
        st.markdown(f"""
        <div class='pred-box' style='border-color:#2e75b6;'>
            <div class='metric-label'>TAHMİN EDİLEN HATA KODU</div>
            <div class='pred-rpn' style='color:#5ba4e6;'>{pred_kod}</div>
            <div style='color:#8aa8cc; margin:8px 0 4px;'>{ht['isim']}</div>
            <div style='color:#4a6080; font-size:0.82rem;'>
                Güven: %{guven:.1f} &nbsp;|&nbsp; Proses: {ht['proses']}
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SAYFA: RANDOM FOREST
# ══════════════════════════════════════════════════════════════════════════════

elif sayfa == "🌲 Random Forest":
    st.markdown("<div class='section-header'>▸ RANDOM FOREST REGRESSOR — RPN TAHMİN MODELİ</div>", unsafe_allow_html=True)

    with st.spinner("Random Forest eğitiliyor (200 ağaç)..."):
        rf, rf_enc, mae, r2, importances, y_test_rf, y_pred_rf = rf_modeli_egit(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("MAE (Ort. Hata)", f"{mae:.2f} RPN")
    col2.metric("R² Skoru", f"{r2:.4f}")
    col3.metric("Açıklanan Varyans", f"%{r2*100:.1f}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax in axes:
        ax.set_facecolor("#0d1220")
        fig.patch.set_facecolor("#0a0e1a")

    # Gerçek vs Tahmin
    axes[0].scatter(y_test_rf, y_pred_rf, alpha=0.5, color="#2e75b6",
                    edgecolors="#5ba4e6", s=45, linewidth=0.4)
    mn = min(y_test_rf.min(), y_pred_rf.min())
    mx = max(y_test_rf.max(), y_pred_rf.max())
    axes[0].plot([mn, mx], [mn, mx], "--", color="#c00000", linewidth=2)
    axes[0].set_xlabel("Gerçek RPN", color="#8aa8cc")
    axes[0].set_ylabel("Tahmin Edilen RPN", color="#8aa8cc")
    axes[0].set_title(f"Gerçek vs Tahmin | R²={r2:.3f}", color="#8aa8cc")
    axes[0].tick_params(colors="#4a6080")
    for spine in axes[0].spines.values():
        spine.set_edgecolor("#1a2d50")

    # Değişken Önemi
    imp_sorted = importances.sort_values()
    renk_imp = ["#c00000" if v > 0.15 else "#2e75b6" for v in imp_sorted]
    axes[1].barh(imp_sorted.index, imp_sorted.values,
                 color=renk_imp, edgecolor="#1a2d50")
    axes[1].set_title("Değişken Önemi (Feature Importance)", color="#8aa8cc")
    axes[1].set_xlabel("Önem Skoru", color="#8aa8cc")
    axes[1].tick_params(colors="#8aa8cc")
    for spine in axes[1].spines.values():
        spine.set_edgecolor("#1a2d50")
    for i, v in enumerate(imp_sorted.values):
        axes[1].text(v + 0.002, i, f"{v:.3f}", va="center",
                     fontsize=8, color="#8aa8cc")

    # Artık dağılımı
    artik = np.array(y_test_rf) - y_pred_rf
    axes[2].hist(artik, bins=25, color="#2a9d8f", edgecolor="#0a0e1a", alpha=0.9)
    axes[2].axvline(0, color="#c00000", linestyle="--", linewidth=2)
    axes[2].set_title("Artık (Residual) Dağılımı", color="#8aa8cc")
    axes[2].set_xlabel("Hata (Gerçek − Tahmin)", color="#8aa8cc")
    axes[2].tick_params(colors="#4a6080")
    axes[2].text(0.97, 0.95, f"μ={artik.mean():.1f}\nσ={artik.std():.1f}",
                 transform=axes[2].transAxes, ha="right", va="top",
                 color="#8aa8cc", fontsize=9,
                 bbox=dict(boxstyle="round", fc="#0d1220", alpha=0.9))
    for spine in axes[2].spines.values():
        spine.set_edgecolor("#1a2d50")

    plt.tight_layout()
    st.image(fig_to_bytes(fig), use_container_width=True)
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# SAYFA: PATTERN RECOGNITION
# ══════════════════════════════════════════════════════════════════════════════

elif sayfa == "🔍 Pattern Recognition":
    st.markdown("<div class='section-header'>▸ K-MEANS KÜMELEME — TEKRARLAYAN HATA ÖRÜNTÜLERİ</div>", unsafe_allow_html=True)
    st.markdown("""<div class='info-box'>
    Üretim hattında tekrarlayan hata örüntüleri K-Means ile tespit edilir.
    PCA ile 2 boyuta indirgenerek görselleştirilir. Yüksek RPN'li kümeler öncelikli müdahale gerektirir.
    </div>""", unsafe_allow_html=True)

    df2 = df.copy()
    for col in ["Hata_Kodu", "Vardiya", "Istasyon"]:
        le = LabelEncoder()
        df2[col + "_enc"] = le.fit_transform(df2[col])

    ozellikler = ["O", "S", "D", "RPN", "Hata_Kodu_enc", "Vardiya_enc", "Istasyon_enc"]
    X_scaled = MinMaxScaler().fit_transform(df2[ozellikler])

    inertias = []
    for k in range(2, 9):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    k_en_iyi = st.slider("Küme Sayısı (k)", 2, 8, 4)
    kmeans = KMeans(n_clusters=k_en_iyi, random_state=42, n_init=10)
    df2["Kume"] = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df2["PCA1"] = X_pca[:, 0]
    df2["PCA2"] = X_pca[:, 1]

    KUME_RENKLERI = ["#2e75b6", "#c00000", "#2a9d8f", "#f4a261",
                     "#6a4c93", "#264653", "#e9c46a", "#a8dadc"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax in axes:
        ax.set_facecolor("#0d1220")
        fig.patch.set_facecolor("#0a0e1a")

    axes[0].plot(range(2, 9), inertias, "o-", color="#2e75b6", linewidth=2, markersize=8)
    axes[0].axvline(k_en_iyi, color="#c00000", linestyle="--", linewidth=1.5)
    axes[0].set_title("Dirsek Yöntemi", color="#8aa8cc")
    axes[0].set_xlabel("k", color="#8aa8cc")
    axes[0].set_ylabel("Inertia", color="#8aa8cc")
    axes[0].tick_params(colors="#4a6080")
    for spine in axes[0].spines.values():
        spine.set_edgecolor("#1a2d50")

    for kume_no in range(k_en_iyi):
        mask = df2["Kume"] == kume_no
        axes[1].scatter(df2.loc[mask, "PCA1"], df2.loc[mask, "PCA2"],
                        c=KUME_RENKLERI[kume_no], label=f"Küme {kume_no+1}",
                        alpha=0.65, s=45, edgecolors="white", linewidth=0.3)
    axes[1].set_title("PCA 2D Küme Dağılımı", color="#8aa8cc")
    axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", color="#8aa8cc")
    axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", color="#8aa8cc")
    axes[1].legend(fontsize=8, facecolor="#0d1220", labelcolor="#8aa8cc")
    axes[1].tick_params(colors="#4a6080")
    for spine in axes[1].spines.values():
        spine.set_edgecolor("#1a2d50")

    kume_rpn = df2.groupby("Kume")["RPN"].mean().sort_values(ascending=False)
    renk_rpn = [KUME_RENKLERI[int(k)] for k in kume_rpn.index]
    axes[2].bar([f"Küme {k+1}" for k in kume_rpn.index], kume_rpn.values,
                color=renk_rpn, edgecolor="#1a2d50")
    axes[2].set_title("Küme Bazında Ortalama RPN", color="#8aa8cc")
    axes[2].set_ylabel("Ort. RPN", color="#8aa8cc")
    axes[2].tick_params(colors="#4a6080")
    for spine in axes[2].spines.values():
        spine.set_edgecolor("#1a2d50")
    for i, v in enumerate(kume_rpn.values):
        axes[2].text(i, v + 2, f"{v:.0f}", ha="center", color="white",
                     fontsize=11, fontweight="bold")

    plt.tight_layout()
    st.image(fig_to_bytes(fig), use_container_width=True)
    plt.close()

    # Küme istatistikleri
    st.markdown("<div class='section-header'>▸ KÜME İSTATİSTİKLERİ</div>", unsafe_allow_html=True)
    kume_stats = df2.groupby("Kume").agg(
        Kayit_Sayisi=("RPN", "count"),
        Ort_RPN=("RPN", "mean"),
        Max_RPN=("RPN", "max"),
        Ort_O=("O", "mean"),
        Ort_S=("S", "mean"),
        Ort_D=("D", "mean"),
    ).round(2).reset_index()
    kume_stats["Küme"] = kume_stats["Kume"].apply(lambda x: f"Küme {x+1}")
    st.dataframe(kume_stats.drop("Kume", axis=1).rename(columns={"Küme": "Küme"}),
                 use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# SAYFA: CANLI RPN TAHMİNİ
# ══════════════════════════════════════════════════════════════════════════════

elif sayfa == "🔮 Canlı RPN Tahmini":
    st.markdown("<div class='section-header'>▸ CANLI RPN TAHMİN ARACI</div>", unsafe_allow_html=True)
    st.markdown("""<div class='info-box'>
    O, S, D değerlerini ve proses bilgilerini girerek Random Forest modelinin RPN tahminini anlık görün.
    Geleneksel RPN ve Ağırlıklı RPN ile karşılaştırın.
    </div>""", unsafe_allow_html=True)

    with st.spinner("Model yükleniyor..."):
        rf, rf_enc, mae, r2, importances, _, _ = rf_modeli_egit(df)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Parametreler**")
        O_val = st.slider("Oluşma Sıklığı (O)", 1, 10, 5)
        S_val = st.slider("Şiddet (S)", 1, 10, 7)
        D_val = st.slider("Tespit Edilebilirlik (D)", 1, 10, 4)
        hata_kodu = st.selectbox("Hata Kodu", list(HATA_TURLERI.keys()),
                                  format_func=lambda k: f"{k} — {HATA_TURLERI[k]['isim']}")
        vardiya_secenekleri = [
            f"{v['isim']} ({v['baslangic']} - {v['bitis']})"
            for v in vardiya_listesi
        ]

        vardiya = st.selectbox(
            "Vardiya",
            vardiya_secenekleri
        )
        istasyon = st.selectbox("İstasyon", ISTASYON_LISTESI)
        hafta = st.slider("Haftalık Hata Sayısı", 1, 10, 5)
        ay = st.slider("Aylık Hata Sayısı", 1, 40, 20)

        if ay < hafta:
            st.error("Aylık hata sayısı haftalık hata sayısından küçük olamaz. Lütfen değerleri kontrol edin.")
            st.stop()

    with col2:
        # Tahmin
        hk_enc = rf_enc["Hata_Kodu"].transform([hata_kodu])[0]
        try:
            v_enc = rf_enc["Vardiya"].transform([vardiya])[0]
        except ValueError:
            v_enc = 0
        i_enc  = rf_enc["Istasyon"].transform([istasyon])[0]
        X_input = pd.DataFrame([[O_val, S_val, D_val, hk_enc, v_enc, i_enc, ay, hafta]],
                                columns=["O", "S", "D", "Hata_Kodu_enc",
                                         "Vardiya_enc", "Istasyon_enc", "Ay", "Hafta"])
        rpn_tahmin = float(rf.predict(X_input)[0])
        rpn_geleneksel = O_val * S_val * D_val
        rpn_agirlikli = 0.5 * S_val + 0.3 * O_val + 0.2 * D_val

        if rpn_tahmin >= 300:
            risk_renk_hex, risk_etiket = "#c00000", "🔴 KRİTİK"
        elif rpn_tahmin >= 200:
            risk_renk_hex, risk_etiket = "#e76f51", "🟠 YÜKSEK"
        elif rpn_tahmin >= 100:
            risk_renk_hex, risk_etiket = "#d4a017", "🟡 ORTA"
        else:
            risk_renk_hex, risk_etiket = "#2a9d8f", "🟢 DÜŞÜK"

        st.markdown(f"""
        <div class='pred-box' style='border-color:{risk_renk_hex}; margin-bottom:14px;'>
            <div class='metric-label'>ML TAHMİN EDİLEN RPN</div>
            <div class='pred-rpn' style='color:{risk_renk_hex};'>{rpn_tahmin:.0f}</div>
            <div style='color:#8aa8cc; font-size:1rem; margin-top:8px;'>{risk_etiket}</div>
        </div>
        """, unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        col3.markdown(f"""
        <div class='pred-box' style='border-color:#2e75b6;'>
            <div class='metric-label'>GELENEKSELrpn</div>
            <div style='font-family:IBM Plex Mono; font-size:2rem; color:#5ba4e6;
                        font-weight:700;'>{rpn_geleneksel}</div>
            <div style='color:#4a6080; font-size:0.75rem;'>O × S × D</div>
        </div>""", unsafe_allow_html=True)

        col4.markdown(f"""
        <div class='pred-box' style='border-color:#2a9d8f;'>
            <div class='metric-label'>AĞIRLIKLI RPN</div>
            <div style='font-family:IBM Plex Mono; font-size:2rem; color:#2a9d8f;
                        font-weight:700;'>{rpn_agirlikli:.2f}</div>
            <div style='color:#4a6080; font-size:0.75rem;'>0.5S+0.3O+0.2D</div>
        </div>""", unsafe_allow_html=True)

        # Önlem
        ht = HATA_TURLERI[hata_kodu]
        
        if st.button("💾 Tahmini Veritabanına Kaydet"):

            kayit_ekle(
                hata_kodu=hata_kodu,
                hata_turu=ht["isim"],
                proses=ht["proses"],
                istasyon=istasyon,
                vardiya=vardiya,
                O=O_val,
                S=S_val,
                D=D_val,
                geleneksel_rpn=rpn_geleneksel,
                agirlikli_rpn=rpn_agirlikli,
                ml_rpn=round(rpn_tahmin, 2),
                risk_seviyesi=risk_etiket,
                onlem=ht["onlem"]
            )

            st.success("Tahmin veritabanına kaydedildi.")

            kayit = {
                "hata_kodu": hata_kodu,
                "hata_turu": ht["isim"],
                "proses": ht["proses"],
                "istasyon": istasyon,
                "vardiya": vardiya,
                "O": O_val,
                "S": S_val,
                "D": D_val,
                "geleneksel_rpn": rpn_geleneksel,
                "agirlikli_rpn": rpn_agirlikli,
                "ml_rpn": round(rpn_tahmin, 2),
                "risk_seviyesi": risk_etiket,
                "onlem": ht["onlem"]
            }

            try:
                pdf_dosya = pdf_rapor_olustur(kayit)

                with open(pdf_dosya, "rb") as file:
                    st.download_button(
                        label="📄 PDF Risk Raporunu İndir",
                        data=file,
                        file_name="AI_FMEA_Risk_Raporu.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.warning("Kayıt başarıyla alındı ancak PDF oluşturulurken hata oluştu.")
                st.error(str(e))

        st.markdown(f"""
        <div class='info-box' style='margin-top:14px;'>
            <strong style='color:#5ba4e6;'>Önerilen Önlem:</strong><br>
            {ht['onlem']}
        </div>
        <div class='info-box'>
            <strong style='color:#5ba4e6;'>Etki:</strong> {ht['etki']}<br>
            <strong style='color:#5ba4e6;'>Proses:</strong> {ht['proses']}
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='info-box' style='margin-top:14px;'>
            <strong style='color:#5ba4e6;'>Önerilen Önlem:</strong><br>
            {ht['onlem']}
        </div>
        <div class='info-box'>
            <strong style='color:#5ba4e6;'>Etki:</strong> {ht['etki']}<br>
            <strong style='color:#5ba4e6;'>Proses:</strong> {ht['proses']}
        </div>
        """, unsafe_allow_html=True)

        # Gösterge grafiği
        fig, ax = plt.subplots(figsize=(5, 1.8))
        fig.patch.set_facecolor("#091020")
        ax.set_facecolor("#091020")
        ax.barh(["Geleneksel", "Ağırlıklı×50", "ML Tahmin"],
                [rpn_geleneksel, rpn_agirlikli * 50, rpn_tahmin],
                color=["#2e75b6", "#2a9d8f", risk_renk_hex], height=0.5)
        ax.set_xlim(0, 1000)
        ax.axvline(200, color="#ffd06b", linestyle=":", linewidth=1, alpha=0.6)
        ax.axvline(400, color="#ff6961", linestyle=":", linewidth=1, alpha=0.6)
        ax.tick_params(colors="#4a6080", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#1a2d50")
        plt.tight_layout()
        st.image(fig_to_bytes(fig), use_container_width=True)
        plt.close()

elif sayfa == "🗂 Kayıtlı Analizler":

    st.markdown("<div class='section-header'>▸ KAYITLI RİSK ANALİZLERİ</div>", unsafe_allow_html=True)

    kayitlar = kayitlari_getir()

    st.write("Toplam kayıt sayısı:", len(kayitlar))

    if kayitlar.empty:
        st.info("Henüz kayıtlı analiz bulunmuyor.")
    else:
        st.dataframe(kayitlar, use_container_width=True, hide_index=True)

elif sayfa == "📤 Firma Verisi Yükle":

    st.markdown("<div class='section-header'>▸ FİRMA VERİSİ YÜKLEME PANELİ</div>", unsafe_allow_html=True)

    st.info("Firma verisini Excel veya CSV formatında yükleyebilirsiniz.")

    uploaded_file = st.file_uploader(
        "Excel veya CSV dosyası yükleyin",
        type=["xlsx", "csv"]
    )

    if uploaded_file is not None:

        if uploaded_file.name.endswith(".csv"):
            firma_df = pd.read_csv(uploaded_file)
        else:
            firma_df = pd.read_excel(uploaded_file)

        zorunlu_sutunlar = [
            "Hata_Kodu",
            "Hata_Turu",
            "Proses_Adimi",
            "Etki",
            "Hata_Aciklamasi",
            "O",
            "S",
            "D",
            "Istasyon",
            "Operator_ID",
            "Vardiya",
            "Ay",
            "Hafta"
        ]

        eksik_sutunlar = [s for s in zorunlu_sutunlar if s not in firma_df.columns]

        if eksik_sutunlar:
            st.error("Yüklenen dosyada eksik sütunlar var:")
            st.write(eksik_sutunlar)

        else:
            firma_df["RPN"] = firma_df["O"] * firma_df["S"] * firma_df["D"]
            firma_df["Agirlikli_RPN"] = (
                0.5 * firma_df["S"] +
                0.3 * firma_df["O"] +
                0.2 * firma_df["D"]
            )

            firma_df["Risk_Seviyesi"] = pd.cut(
                firma_df["RPN"],
                bins=[0, 100, 200, 500, 1000],
                labels=["Düşük", "Orta", "Yüksek", "Kritik"]
            )

            st.success("Firma verisi başarıyla yüklendi ve analiz edildi.")

            st.dataframe(firma_df, use_container_width=True, hide_index=True)

            csv = firma_df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                "⬇ Analiz Edilmiş Firma Verisini İndir",
                data=csv,
                file_name="firma_fmea_analizli_veri.csv",
                mime="text/csv"
            )

elif sayfa == "⚙️ Vardiya Ayarları":

    st.markdown("<div class='section-header'>▸ VARDİYA AYARLARI</div>", unsafe_allow_html=True)

    st.info("Bu ekrandan vardiya adlarını ve saatlerini düzenleyebilirsiniz.")

    st.subheader("Mevcut Vardiyalar")

    vardiya_df = pd.DataFrame(vardiya_listesi)
    st.dataframe(vardiya_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Yeni Vardiya Ekle")

    yeni_isim = st.text_input("Vardiya Adı", placeholder="Örn: Sabah")
    yeni_baslangic = st.time_input("Başlangıç Saati")
    yeni_bitis = st.time_input("Bitiş Saati")

    if st.button("➕ Vardiya Ekle"):
        if yeni_isim.strip() == "":
            st.error("Vardiya adı boş olamaz.")
        else:
            yeni_vardiya = {
                "isim": yeni_isim,
                "baslangic": yeni_baslangic.strftime("%H:%M"),
                "bitis": yeni_bitis.strftime("%H:%M")
            }

            vardiya_listesi.append(yeni_vardiya)

            with open("vardiyalar.json", "w", encoding="utf-8") as f:
                json.dump(vardiya_listesi, f, ensure_ascii=False, indent=4)

            st.success("Yeni vardiya eklendi. Sayfayı yenileyin.")

    st.markdown("---")
    st.subheader("Vardiya Sil")

    silinecek_vardiya = st.selectbox(
        "Silinecek vardiyayı seçin",
        [f"{v['isim']} ({v['baslangic']} - {v['bitis']})" for v in vardiya_listesi]
    )

    if st.button("🗑 Seçili Vardiyayı Sil"):
        vardiya_listesi = [
            v for v in vardiya_listesi
            if f"{v['isim']} ({v['baslangic']} - {v['bitis']})" != silinecek_vardiya
        ]

        with open("vardiyalar.json", "w", encoding="utf-8") as f:
            json.dump(vardiya_listesi, f, ensure_ascii=False, indent=4)

        st.success("Vardiya silindi. Sayfayı yenileyin.")