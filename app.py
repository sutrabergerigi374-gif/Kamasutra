import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD Faktur Viewer", page_icon="🌐", layout="wide"
)

st.title("🚀 Alfastore - Data Faktur LPB Tablet")
st.write("Aplikasi untuk mengecek data faktur berdasarkan Store ID.")

# Sidebar / Form Input
st.sidebar.header("Filter & Parameter Input")
store_id = st.sidebar.text_input(
    "Masukkan Store ID:", value="M1Z7", help="Contoh: M1Z7"
)
filter_val = st.sidebar.text_input(
    "Filter (Opsional):", value="", help="Nilai filter jika ada"
)

# Endpoint API yang benar sesuai request Anda
endpoint = "/prd/api/lpb/tablet/lpb/get_faktur/"

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

if st.sidebar.button("Muat Data Faktur"):
  url = f"https://app.alfastore.co.id{endpoint}"
  params = {"storeId": store_id, "filter": filter_val}

  with st.spinner("Menghubungkan ke server..."):
    try:
      response = requests.get(url, headers=headers, params=params, timeout=15)

      # Menampilkan informasi URL yang di-request untuk debugging
      st.info(f"URL Request: `{response.url}`")

      if response.status_code == 200:
        data = response.json()
        st.success(
            f"Berhasil mengambil data untuk Store ID: **{store_id}**"
        )

        # Cek format data response (biasanya list atau dict di dalam key tertentu)
        if isinstance(data, list) and len(data) > 0:
          df = pd.DataFrame(data)
          st.subheader("📦 Tabel Data Faktur")
          st.dataframe(df, use_container_width=True)
          st.metric("Total Baris Data", len(df))
        elif isinstance(data, dict):
          st.subheader("📦 Detail Response JSON")
          st.json(data)
        else:
          st.warning("Data kosong atau format response tidak dikenali.")
          st.json(data)
      else:
        st.error(f"Gagal mengambil data. Status Code: {response.status_code}")
        st.text(response.text)

    except Exception as e:
      st.error(f"Terjadi kesalahan koneksi: {e}")
else:
  st.info(
      "Masukkan Store ID di panel sebelah kiri, lalu klik **Muat Data Faktur**."
  )
