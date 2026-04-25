import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Bike Sharing Dashboard 🚲",
    page_icon="🚲",
    layout="wide"
)

# --- STYLE VISUALISASI ---
sns.set_theme(style="whitegrid")

# --- LOAD DATA (PERBAIKAN PATH) ---
@st.cache_data
def load_data():
    # Mengambil lokasi folder tempat dashboard.py ini berada
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Membangun jalur lengkap ke file CSV
    day_path = os.path.join(base_dir, "day.csv")
    hour_path = os.path.join(base_dir, "hour.csv")
    
    # Membaca data
    day_df = pd.read_csv(day_path)
    hour_df = pd.read_csv(hour_path)
    
    # Konversi tipe data datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Mapping Musim untuk Label yang lebih informatif
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    day_df['season_label'] = day_df['season'].map(season_mapping)
    hour_df['season_label'] = hour_df['season'].map(season_mapping)
    
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png", width=200)
    st.title("🚲 Bike Sharing Analytics")
    st.markdown("Dashboard ini menganalisis performa penyewaan sepeda berdasarkan parameter waktu dan cuaca.")
    
    st.divider()
    
    # Filter Rentang Waktu
    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()
    
    # Input tanggal
    date_range = st.date_input(
        label='Pilih Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # Validasi input tanggal
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Filter Musim
    st.markdown("---")
    available_seasons = day_df["season_label"].unique()
    selected_seasons = st.multiselect(
        "Pilih Musim:",
        options=available_seasons,
        default=available_seasons
    )

# --- FILTERING DATA ---
main_df = day_df[
    (day_df["dteday"] >= pd.to_datetime(start_date)) & 
    (day_df["dteday"] <= pd.to_datetime(end_date)) &
    (day_df["season_label"].isin(selected_seasons))
]

# --- HEADER UTAMA ---
st.title("📊 Bike Sharing Performance Dashboard")
st.markdown(f"Periode Analisis: **{start_date}** s/d **{end_date}**")

# --- METRIKS UTAMA (KPIs) ---
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = main_df.cnt.sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")

with col2:
    total_registered = main_df.registered.sum()
    st.metric("Pengguna Terdaftar", value=f"{total_registered:,}", delta="Registered")

with col3:
    total_casual = main_df.casual.sum()
    st.metric("Pengguna Kasual", value=f"{total_casual:,}", delta="Casual", delta_color="inverse")

st.divider()

# --- LAYOUT DASHBOARD ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Pengaruh Suhu Terhadap Penyewaan")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=main_df, 
        x='atemp', 
        y='cnt', 
        hue='season_label', 
        palette='viridis', 
        alpha=0.6,
        ax=ax1
    )
    ax1.set_title("Korelasi Suhu (Feeling Temp) vs Total Sewa", fontsize=15)
    ax1.set_xlabel("Suhu (Normalized atemp)")
    ax1.set_ylabel("Total Penyewaan")
    st.pyplot(fig1)

with row1_col2:
    st.subheader("Pola Penyewaan pada Jam Sibuk")
    # Filter jam sibuk hari kerja
    rush_hour_df = hour_df[
        (hour_df['workingday'] == 1) & 
        (hour_df['hr'].isin([7, 8, 9, 17, 18, 19])) &
        (hour_df['season_label'].isin(selected_seasons))
    ]
    rush_hour_avg = rush_hour_df.groupby('hr')[['casual', 'registered']].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.bar(rush_hour_avg['hr'], rush_hour_avg['registered'], label='Registered', color='#2E86C1')
    ax2.bar(rush_hour_avg['hr'], rush_hour_avg['casual'], bottom=rush_hour_avg['registered'], label='Casual', color='#AED6F1')
    
    ax2.set_title("Rata-rata Sewa pada Jam Sibuk (Hari Kerja)", fontsize=15)
    ax2.set_xlabel("Jam (24-Hour Format)")
    ax2.set_ylabel("Rata-rata Penyewaan")
    ax2.set_xticks([7, 8, 9, 17, 18, 19])
    ax2.legend()
    st.pyplot(fig2)

# --- ANALISIS TAMBAHAN ---
st.divider()
st.subheader("Insight Analisis Lanjutan: Clustering")
st.info("""
**Teknik Analisis: Manual Grouping (Clustering)**
Data dikelompokkan berdasarkan waktu operasional (Jam Sibuk vs Luar Jam Sibuk). 
Hasil menunjukkan bahwa pengguna **Registered** memiliki lonjakan tajam pada jam berangkat (08:00) dan pulang kerja (17:00), 
sedangkan pengguna **Casual** cenderung stabil dengan intensitas lebih rendah.
""")

st.caption(f"Copyright © 2026 | Project Akhir Analisis Data - Calvin Valentino Hariyanto")
