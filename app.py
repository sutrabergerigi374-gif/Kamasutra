import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD Faktur & Kontainer Viewer", page_icon="🌐", layout="wide"
)

st.title("🚀 Alfastore - Data Faktur & Kontainer LPB")
st.write(
    "Aplikasi untuk mengecek daftar faktur, melihat total nilai faktur (dalam juta), "
    "serta menampilkan dan memisahkan isi barang per kontainer."
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

            det_items = (
                det_json.get("data", det_json)
                if isinstance(det_json, dict)
                else det_json
            )

            if isinstance(det_items, list) and len(det_items) > 0:
              df_detail = pd.DataFrame(det_items)

              st.success(
                  f"Berhasil memuat detail faktur: **{selected_faktur}**"
              )

              # --- HITUNG TOTAL NILAI FAKTUR & JUTA RUPIAH ---
              # Deteksi kolom harga / total nominal
              col_total = next(
                  (
                      c
                      for c in df_detail.columns
                      if any(
                          k in c.lower()
                          for k in [
                              "total",
                              "rp",
                              "harga",
                              "subtotal",
                              "nominal",
                              "amount",
                              "nilai",
                          ]
                      )
                  ),
                  None,
              )

              # Deteksi kolom QTY & Harga Satuan jika total bersih tidak ditemukan
              col_qty = next(
                  (c for c in df_detail.columns if "qty" in c.lower() or "jumlah" in c.lower()),
                  None,
              )

              total_nominal = 0.0
              if col_total:
                # Bersihkan format string ke numerik
                total_nominal = (
                    pd.to_numeric(
                        df_detail[col_total]
                        .astype(str)
                        .str.replace(r"[^\d.]", "", regex=True),
                        errors="coerce",
                    )
                    .sum()
                )

              total_juta = total_nominal / 1_000_000.0

              # METRIK RINGKASAN FAKTUR
              col_m1, col_m2, col_m3 = st.columns(3)
              col_m1.metric("Total Jenis Item", f"{len(df_detail)} Item")
              if col_total:
                col_m2.metric("Total Nilai Faktur", f"Rp {total_nominal:,.0f}")
                col_m3.metric("Nominal (Juta Rupiah)", f"Rp {total_juta:,.2f} Juta")
              else:
                col_m2.metric("Total QTY Barang", f"{pd.to_numeric(df_detail[col_qty], errors='coerce').sum() if col_qty else '-'}")
                col_m3.metric("Nominal", "Kolom Harga Tidak Ditemukan")

              st.markdown("---")

              # Tampilkan kolom API
              st.write(
                  "**Daftar Kolom yang tersedia dari API:**",
                  df_detail.columns.tolist(),
              )

              # --- PENGECEKAN KOLOM KONTAINER ---
              col_kontainer = next(
                  (
                      c
                      for c in df_detail.columns
                      if any(
                          k in c.lower()
                          for k in [
                              "kontainer",
                              "container",
                              "bag",
                              "box",
                              "truk",
                              "no_knt",
                          ]
                      )
                  ),
                  None,
              )

              if col_kontainer:
                daftar_kontainer = df_detail[col_kontainer].unique()

                st.subheader("📦 Filter & Tampilan Per Kontainer")
                
                # Dropdown Pilihan Kontainer Spesifik
                pilihan_kontainer = st.selectbox(
                    "Pilih Kontainer untuk ditampilkan khusus:",
                    ["Semua Kontainer"] + list(daftar_kontainer),
                )

                if pilihan_kontainer != "Semua Kontainer":
                  df_sub_pilihan = df_detail[df_detail[col_kontainer] == pilihan_kontainer]
                  st.write(f"### 📥 Isi Khusus Kontainer: **{pilihan_kontainer}**")
                  st.dataframe(df_sub_pilihan, use_container_width=True)
                else:
                  # Tampilkan Seluruh Kontainer
                  st.dataframe(df_detail, use_container_width=True)

                st.write("---")
                st.write("### 📂 Rincian Kartu Per Kontainer")

                for kontainer in daftar_kontainer:
                  df_sub = df_detail[df_detail[col_kontainer] == kontainer]
                  jumlah_item = len(df_sub)

                  # Hitung total per kontainer jika ada nominal
                  sub_nominal = 0.0
                  if col_total:
                    sub_nominal = (
                        pd.to_numeric(
                            df_sub[col_total]
                            .astype(str)
                            .str.replace(r"[^\d.]", "", regex=True),
                            errors="coerce",
                        )
                        .sum()
                    )
                  sub_juta = sub_nominal / 1_000_000.0

                  label_expander = f"📦 Kontainer: {kontainer}  |  QTY Item: {jumlah_item}"
                  if col_total:
                    label_expander += f"  |  Total: Rp {sub_juta:,.2f} Juta"

                  with st.expander(label_expander):
                    st.write(f"**Isi Kontainer: {kontainer}**")
                    st.dataframe(df_sub, use_container_width=True)

                    csv_sub = df_sub.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=f"📥 Download Isi Kontainer {kontainer} (CSV)",
                        data=csv_sub,
                        file_name=f"kontainer_{kontainer}_{selected_faktur}.csv",
                        mime="text/csv",
                        key=f"dl_{kontainer}",
                    )
              else:
                st.warning(
                    "Kolom pengelompokan kontainer belum terdeteksi secara otomatis."
                )
                st.dataframe(df_detail, use_container_width=True)

              # Tombol Download Seluruh Faktur
              csv_data = df_detail.to_csv(index=False).encode("utf-8")
              st.download_button(
                  label=f"📥 Download Seluruh Isi Faktur {selected_faktur} (CSV)",
                  data=csv_data,
                  file_name=f"detail_faktur_{selected_faktur}.csv",
                  mime="text/csv",
              )

            else:
              st.info("Detail data diterima, tetapi format berupa JSON murni:")
              st.json(det_json)
          else:
            st.error(f"Gagal mengambil detail faktur. Status Code: {det_response.status_code}")
            st.text(det_response.text)

        except Exception as e:
          st.error(f"Terjadi kesalahan koneksi saat mengambil detail: {e}")
  else:
    st.info("Tidak ada faktur yang tersedia untuk dipilih.")
else:
  st.info(
      "Silakan masukkan Store ID di panel sebelah kiri, lalu klik **Muat Daftar Faktur** terlebih dahulu."
  )
