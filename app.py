import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD Public App", page_icon="🌐", layout="wide"
)

st.title("🚀 Alfastore CEXP-CLOUD Container & Store Viewer")
st.write(
    "Aplikasi untuk mengecek isi kontainer dan mengelola data per kode toko."
)

# Sidebar / Form Input
st.sidebar.header("Filter & Parameter Input")
kode_toko = st.sidebar.text_input(
    "Masukkan Kode Toko:", value="T001", help="Contoh: T001, T002"
)
endpoint = st.sidebar.text_input(
    "Endpoint API path:", value="/api/v1/container"
)

# Header yang Anda sediakan
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 11; Mobile) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Api-Key": "iVOZX9MLmKrj1L8R23uF1aryMR1vGMXG",
    "x-api-key": "iVOZX9MLmKrj1L8R23uF1aryMR1vGMXG",
    "App-Name": "CEXP-CLOUD",
    "Platform": "ANDROID",
    "Accept-Encoding": "gzip",
}

if st.sidebar.button("Muat Data Kontainer"):
  url = f"https://app.alfastore.co.id{endpoint}"

  with st.spinner("Menghubungkan ke server..."):
    try:
      response = requests.get(
          url, headers=headers, params={"kode_toko": kode_toko}, timeout=15
      )

      if response.status_code == 200:
        data = response.json()

        st.success(
            f"Berhasil mengambil data untuk Kode Toko: **{kode_toko}**"
        )

        if isinstance(data, list) and len(data) > 0:
          df = pd.DataFrame(data)
          df["Kode Toko"] = kode_toko
          st.subheader("📦 Tabel Isi Kontainer")
          st.dataframe(df, use_container_width=True)

          col1, col2, col3 = st.columns(3)
          col1.metric("Total Kontainer / Item", len(df))
          col2.metric("Kode Toko Active", kode_toko)
          col3.metric("Status Server", "200 OK")

        elif isinstance(data, dict):
          st.subheader("📦 Detail Kontainer")
          data["Kode Toko Input"] = kode_toko
          st.json(data)
        else:
          st.warning("Data kosong atau format response tidak dikenali.")
      else:
        st.error(f"Gagal mengambil data. Status Code: {response.status_code}")
        st.text(response.text)

    except Exception as e:
      st.error(f"Terjadi kesalahan koneksi: {e}")
else:
  st.info(
      "Masukkan Kode Toko dan Endpoint di panel sebelah kiri, lalu klik **Muat"
      " Data Kontainer**."
  )
