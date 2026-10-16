import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD Faktur Viewer", page_icon="🌐", layout="wide"
)

st.title("🚀 Alfastore - Detail Kiriman Faktur LPB")
st.write(
    "Aplikasi untuk mengecek daftar faktur dan melihat isi detail faktur"
    " secara lengkap."
)

# Sidebar / Form Input
st.sidebar.header("Filter & Parameter Input")
store_id = st.sidebar.text_input(
    "Masukkan Store ID:", value="M1Z7", help="Contoh: M1Z7"
)
filter_val = st.sidebar.text_input(
    "Filter (Opsional):", value="", help="Nilai filter jika ada"
)

# Endpoint API
endpoint_list = "/prd/api/lpb/tablet/lpb/get_faktur/"
endpoint_detail = "/prd/api/lpb/tablet/lpb/get_det_faktur_bkl/"

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

if st.sidebar.button("Muat Daftar Faktur"):
  url = f"https://app.alfastore.co.id{endpoint_list}"
  params = {"storeId": store_id, "filter": filter_val}

  with st.spinner("Menghubungkan ke server..."):
    try:
      response = requests.get(url, headers=headers, params=params, timeout=15)

      if response.status_code == 200:
        res_json = response.json()
        st.success(
            f"Berhasil mengambil daftar faktur untuk Store ID: **{store_id}**"
        )

        items = res_json.get("data", [])

        if isinstance(items, list) and len(items) > 0:
          # Simpan daftar faktur ke session_state agar tidak hilang saat diklik
          st.session_state["faktur_items"] = items
          st.session_state["store_id"] = store_id
        else:
          st.warning("Data faktur kosong atau tidak ditemukan.")
          st.json(res_json)
      else:
        st.error(f"Gagal mengambil data. Status Code: {response.status_code}")
        st.text(response.text)

    except Exception as e:
      st.error(f"Terjadi kesalahan koneksi: {e}")

# Tampilkan tabel daftar faktur jika sudah dimuat
if "faktur_items" in st.session_state:
  items = st.session_state["faktur_items"]
  current_store = st.session_state["store_id"]

  st.markdown("---")
  st.subheader("📦 Daftar Faktur Tersedia")
  df_list = pd.DataFrame(items)
  st.dataframe(df_list, use_container_width=True)

  st.markdown("---")
  st.subheader("🔍 Lihat Isi / Detail Faktur")

  list_faktur = [item.get("faktur") for item in items if "faktur" in item]

  if list_faktur:
    selected_faktur = st.selectbox(
        "Pilih Nomor Faktur yang ingin dilihat isinya:", list_faktur
    )

    if st.button("👁️ View / Lihat Isi Faktur"):
      detail_url = f"https://app.alfastore.co.id{endpoint_detail}"
      detail_params = {"storeId": current_store, "faktur": selected_faktur}

      with st.spinner(f"Mengambil isi detail faktur {selected_faktur}..."):
        try:
          det_response = requests.get(
              detail_url, headers=headers, params=detail_params, timeout=15
          )

          if det_response.status_code == 200:
            det_json = det_response.json()
            st.success(
                f"Berhasil memuat isi faktur: **{selected_faktur}**"
            )

            # Cek struktur data isi detail faktur (biasanya berupa list produk/barang di dalam key 'data' atau langsung)
            det_items = (
                det_json.get("data", det_json)
                if isinstance(det_json, dict)
                else det_json
            )

            if isinstance(det_items, list) and len(det_items) > 0:
              df_detail = pd.DataFrame(det_items)
              st.dataframe(df_detail, use_container_width=True)

              # Tombol Download CSV untuk isi faktur
              csv_data = df_detail.to_csv(index=False).encode("utf-8")
              st.download_button(
                  label=(
                      f"📥 Download Isi Faktur {selected_faktur} sebagai CSV"
                  ),
                  data=csv_data,
                  file_name=f"detail_faktur_{selected_faktur}.csv",
                  mime="text/csv",
              )
            else:
              st.info(
                  "Detail data diterima, tetapi format berupa JSON murni:"
              )
              st.json(det_json)
          else:
            st.error(
                "Gagal mengambil detail faktur. Status Code:"
                f" {det_response.status_code}"
            )
            st.text(det_response.text)

        except Exception as e:
          st.error(f"Terjadi kesalahan koneksi saat mengambil detail: {e}")
else:
  st.info(
      "Silakan masukkan Store ID di panel kiri, lalu klik **Muat Daftar"
      " Faktur** terlebih dahulu."
  )
