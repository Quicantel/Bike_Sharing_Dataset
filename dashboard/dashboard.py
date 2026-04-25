import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set konfigurasi halaman
st.set_page_config(page_title="Bike Sharing Dashboard 🚲", layout="wide")

@st.cache_data
def load_data():
    # Mendapatkan path absolut dari folder tempat dashboard.py berada
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Menggabungkan path folder dengan nama file csv
    day_path = os.path.join(base_dir, "day.csv")
    hour_path = os.path.join(base_dir, "hour.csv")
    
    # Membaca file menggunakan path yang sudah pasti benar
    day_df = pd.read_csv(day_path)
    hour_df = pd.read_csv(hour_path)
    
    # Proses cleaning selanjutnya tetap sama...
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    # ... dst
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png") # Opsional: Logo Dicoding atau gambar sepeda
    st.title("Filter Analisis")
    
    # Filter Rentang Waktu
    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan input sidebar
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                    (day_df["dteday"] <= str(end_date))]

# --- HEADER ---
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown(f"Menampilkan data dari **{start_date}** hingga **{end_date}**")

# --- METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_df.cnt.sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")

with col2:
    total_registered = main_df.registered.sum()
    st.metric("Pengguna Registered", value=f"{total_registered:,}")

with col3:
    total_casual = main_df.casual.sum()
    st.metric("Pengguna Casual", value=f"{total_casual:,}")

st.divider()

# --- VISUALISASI 1: PENGARUH SUHU (Pertanyaan 2) ---
st.subheader("Hubungan Suhu (atemp) terhadap Jumlah Penyewaan")
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(
    data=main_df, 
    x='atemp', 
    y='cnt', 
    hue='season_label', 
    palette='Set2', 
    alpha=0.7,
    ax=ax
)
ax.set_xlabel("Normalized Temperature (atemp)")
ax.set_ylabel("Total Rentals")
st.pyplot(fig)

# --- VISUALISASI 2: JAM SIBUK (Pertanyaan 1) ---
st.subheader("Pola Penyewaan pada Jam Sibuk (Hari Kerja)")
# Filter jam sibuk tahun 2012 di hari kerja
rush_hour_df = hour_df[(hour_df['workingday'] == 1) & (hour_df['hr'].isin([7,8,9,17,18,19]))]
rush_hour_avg = rush_hour_df.groupby('hr')[['casual', 'registered']].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(12, 6))
# Palet warna minimalis: Light Grey dan Cream/Tan
sns.barplot(x='hr', y='registered', data=rush_hour_avg, color='#D3D3D3', label='Registered', ax=ax2)
sns.barplot(x='hr', y='casual', data=rush_hour_avg, color='#F5DEB3', label='Casual', ax=ax2)
ax2.set_xlabel("Jam (Hour)")
ax2.set_ylabel("Rata-rata Penyewaan")
ax2.legend()
st.pyplot(fig2)

st.caption("Copyright © 2026 - Calvin Valentino Hariyanto")
