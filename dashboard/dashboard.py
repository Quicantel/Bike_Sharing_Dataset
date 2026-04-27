import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(page_title="Bike Sharing Dashboard 🚲", layout="wide")
sns.set_theme(style="whitegrid")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    day_df = pd.read_csv(os.path.join(base_dir, "day.csv"))
    hour_df = pd.read_csv(os.path.join(base_dir, "hour.csv"))

    # Konversi ke datetime & hilangkan jam
    day_df['dteday'] = pd.to_datetime(day_df['dteday']).dt.normalize()
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday']).dt.normalize()

    # Mapping season
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    day_df['season_label'] = day_df['season'].map(season_mapping)
    hour_df['season_label'] = hour_df['season'].map(season_mapping)

    return day_df, hour_df


day_df, hour_df = load_data()

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.title("🚲 Dashboard Filter")

    min_date = day_df["dteday"].min().date()
    max_date = day_df["dteday"].max().date()

    date_range = st.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date), 
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    selected_seasons = st.multiselect(
        "Pilih Musim",
        options=day_df["season_label"].unique(),
        default=day_df["season_label"].unique()
    )

# ==============================
# FUNGSI FILTER
# ==============================
def apply_filter(df):
    return df[
        (df["dteday"].dt.date >= start_date) &
        (df["dteday"].dt.date <= end_date) &
        (df["season_label"].isin(selected_seasons))
    ].copy()


main_day_df = apply_filter(day_df)
main_hour_df = apply_filter(hour_df)

# ==============================
# MAIN PAGE
# ==============================
st.title("📊 Bike Sharing Dashboard")

st.write(
    f"📅 Periode: **{start_date} → {end_date}** | "
    f"📊 Data: **{len(main_day_df)} hari**"
)

# ==============================
# METRIK
# ==============================
col1, col2, col3 = st.columns(3)

col1.metric("Total Penyewaan", f"{main_day_df['cnt'].sum():,}")
col2.metric("Registered", f"{main_day_df['registered'].sum():,}")
col3.metric("Casual", f"{main_day_df['casual'].sum():,}")

st.divider()

# ==============================
# VISUALISASI
# ==============================
col_l, col_r = st.columns(2)

#  Scatter Plot 
with col_l:
    st.subheader("Pengaruh Suhu terhadap Penyewaan")

    if not main_day_df.empty:
        fig, ax = plt.subplots()

        sns.scatterplot(
            data=main_day_df,
            x='atemp',
            y='cnt',
            hue='season_label',
            palette='viridis',
            ax=ax
        )

        ax.set_title("Scatter Plot Penyewaan")
        st.pyplot(fig)
    else:
        st.warning("Data kosong")

#  Bar Chart 
with col_r:
    st.subheader("Jam Sibuk")

    rush_df = main_hour_df[
        (main_hour_df['workingday'] == 1) &
        (main_hour_df['hr'].isin([7, 8, 9, 17, 18, 19]))
    ]

    if not rush_df.empty:
        grouped = rush_df.groupby('hr')[['casual', 'registered']].mean().reset_index()

        fig, ax = plt.subplots()

        ax.bar(grouped['hr'], grouped['registered'], label='Registered')
        ax.bar(grouped['hr'], grouped['casual'], bottom=grouped['registered'], label='Casual')

        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Tidak ada data")

# ==============================
# DEBUG PANEL
# ==============================
with st.expander("🔍 DEBUG MODE"):
    st.write("start_date:", start_date)
    st.write("end_date:", end_date)
    st.write("type:", type(date_range))
    st.write("Jumlah data sebelum filter:", len(day_df))
    st.write("Jumlah data setelah filter:", len(main_day_df))

    st.write("Sample data:")
    st.dataframe(main_day_df.head())

# ==============================
# FOOTER
# ==============================
st.caption("© 2026 Dashboard Debug Version")
