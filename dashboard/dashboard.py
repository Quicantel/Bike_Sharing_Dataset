import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Bike Sharing Dashboard 🚲", layout="wide")
sns.set_theme(style="whitegrid")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    day_df = pd.read_csv(os.path.join(base_dir, "day.csv"))
    hour_df = pd.read_csv(os.path.join(base_dir, "hour.csv"))
    
    # INI KUNCINYA: Memaksa kolom menjadi datetime agar sinkron dengan filter tanggal
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    day_df['season_label'] = day_df['season'].map(season_mapping)
    hour_df['season_label'] = hour_df['season'].map(season_mapping)
    
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png", width=200)
    st.title("🚲 Dashboard Filter")
    
    # Filter Tanggal
    min_date, max_date = day_df["dteday"].min(), day_df["dteday"].max()
    date_range = st.date_input(
        label='Rentang Waktu:', 
        value=[min_date, max_date], 
        min_value=min_date, 
        max_value=max_date
    )
    
    # Pengamanan input tanggal agar tidak error saat user baru memilih satu tanggal
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Filter Musim (Sinkron dengan grafik)
    selected_seasons = st.multiselect(
        "Pilih Musim:",
        options=day_df["season_label"].unique(),
        default=day_df["season_label"].unique()
    )

# --- PROSES FILTERING (MENGHUBUNGKAN FITUR KE DATA) ---

# Sinkronisasi filter untuk data harian (Metrik & Grafik Kiri)
main_day_df = day_df[
    (day_df["dteday"] >= pd.to_datetime(start_date)) & 
    (day_df["dteday"] <= pd.to_datetime(end_date)) &
    (day_df["season_label"].isin(selected_seasons))
].copy()

# Sinkronisasi filter untuk data per jam (Grafik Kanan)
main_hour_df = hour_df[
    (hour_df["dteday"] >= pd.to_datetime(start_date)) & 
    (hour_df["dteday"] <= pd.to_datetime(end_date)) &
    (hour_df["season_label"].isin(selected_seasons))
].copy()

# --- MAIN PAGE ---
st.title("📊 Bike Sharing Performance Dashboard")
# Indikator pembuktian filter jalan:
st.write(f"Periode: **{start_date}** s/d **{end_date}** | Data Terfilter: **{len(main_day_df)} Hari**")

# Metrik Utama (Menggunakan data yang sudah difilter)
m1, m2, m3 = st.columns(3)
m1.metric("Total Penyewaan", value=f"{main_day_df.cnt.sum():,}")
m2.metric("Registered", value=f"{main_day_df.registered.sum():,}")
m3.metric("Casual", value=f"{main_day_df.casual.sum():,}")

st.divider()

# --- VISUALISASI ---
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Pengaruh Suhu Terhadap Penyewaan")
    if not main_day_df.empty:
        # 1. Selalu buat Figure baru di dalam kolom
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        
        # 2. Tambahkan pengecekan hue_order agar Seaborn tidak bingung
        # jika datanya hanya terdiri dari satu musim saja
        sns.scatterplot(
            data=main_day_df, 
            x='atemp', 
            y='cnt', 
            hue='season_label', 
            hue_order=['Spring', 'Summer', 'Fall', 'Winter'], # Paksa urutan kategori
            palette='viridis', 
            ax=ax1
        )
        
        ax1.set_title(f"Data Terfilter ({len(main_day_df)} Hari)")
        st.pyplot(fig1)
    else:
        st.warning("Data kosong untuk filter ini.")

with col_r:
    st.subheader("Pola Penyewaan pada Jam Sibuk")
    # Menggunakan main_hour_df yang sudah terfilter rentang tanggalnya
    rush_hour_df = main_hour_df[
        (main_hour_df['workingday'] == 1) & (main_hour_df['hr'].isin([7, 8, 9, 17, 18, 19]))
    ]
    
    if not rush_hour_df.empty:
        rush_hour_avg = rush_hour_df.groupby('hr')[['casual', 'registered']].mean().reset_index()
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.bar(rush_hour_avg['hr'], rush_hour_avg['registered'], label='Registered', color='#2E86C1')
        ax2.bar(rush_hour_avg['hr'], rush_hour_avg['casual'], bottom=rush_hour_avg['registered'], label='Casual', color='#AED6F1')
        ax2.set_xticks([7, 8, 9, 17, 18, 19])
        ax2.legend()
        st.pyplot(fig2)
    else:
        st.warning("Tidak ada data jam kerja pada rentang waktu ini.")

st.caption(f"Copyright © 2026 | Project Akhir Analisis Data - Calvin Valentino Hariyanto")
