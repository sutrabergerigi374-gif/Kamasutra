import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD Faktur Viewer", page_icon="🌐", layout="wide"
)

st.title("🚀 Alfastore - Data Faktur LPB Tablet")
st.write(
    "Aplikasi untuk mengecek, melihat detail, dan mengunduh faktur dengan"
    " aman."
)

# Sidebar / Form Input
st.sidebar.header("Filter & Parameter Input")
store_id = st.sidebar.text_input(
    "Masukkan Store ID:", value="M1Z7", help="Contoh: M1Z7"
)
filter_val = st.sidebar.text_input(
    "Filter (Opsional):", value="", help="Nilai filter jika ada"
)

# Endpoint API Faktur
endpoint = "/prd/api/lpb/tablet/lpb/get_faktur/"

# Header API
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

      if response.status_code == 200:
        res_json = response.json()
        st.success(
            f"Berhasil mengambil data untuk Store ID: **{store_id}**"
        )

        items = res_json.get("data", [])

        if isinstance(items, list) and len(items) > 0:
          df = pd.DataFrame(items)

          st.subheader("📦 Daftar Faktur Tersedia")
          st.dataframe(df, use_container_width=True)

          st.markdown("---")
          st.subheader("🔍 Pilih & Unduh Detail Faktur")

          list_faktur = [item.get("faktur") for item in items if "faktur" in item]

          if list_faktur:
            selected_faktur = st.selectbox(
                "Pilih Nomor Faktur:", list_faktur
            )

            detail_data = next(
                (item for item in items if item.get("faktur") == selected_faktur),
                None,
            )

            if detail_data:
              st.info(f"Detail Informasi untuk Faktur: {selected_faktur}")
              st.json(detail_data)

              # Format teks rapi untuk diunduh sebagai file .txt
              text_content = (
                  f"=== DETAIL FAKTUR ALFASTORE ===\nStore ID: {store_id}\n"
              )
              for k, v in detail_data.items():
                text_content += f"{k}: {v}\n"

              # Tombol Download Text (.txt)
              st.download_button(
                  label=f"📥 Download Faktur {selected_faktur} (TXT)",
                  data=text_content,
                  file_name=f"faktur_{selected_faktur}.txt",
                  mime="text/plain",
              )

              # Tombol Download CSV
              csv_data = pd.DataFrame([detail_data]).to_csv(index=False).encode("utf-8")
              st.download_button(
                  label=f"📥 Download Faktur {selected_faktur} (CSV)",
                  data=csv_data,
                  file_name=f"faktur_{selected_faktur}.csv",
                  mime="text/csv",
              )
        else:
          st.warning("Data faktur kosong atau tidak ditemukan.")
          st.json(res_json)
      else:
        st.error(f"Gagal mengambil data. Status Code: {response.status_code}")
        st.text(response.text)

    except Exception as e:
      st.error(f"Terjadi kesalahan koneksi: {e}")
else:
  st.info(
      "Masukkan Store ID di panel sebelah kiri, lalu klik **Muat Data Faktur**."
  )
