import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD LOV Container Viewer", page_icon="📦", layout="wide"
)

st.title("🚀 Alfastore - LOV Container & Detail PO")
st.write(
    "Aplikasi untuk mengecek daftar faktur, ringkasan kontainer (LOV Container),"
    " serta detail item per kontainer."
)

# Daftar Store ID yang diizinkan (Whitelist)
ALLOWED_STORES = [
    "M1U8",
    "M953",
    "M885",
    "M1S6",
    "M1S4",
    "M750",
    "M1Z4",
    "M898",
    "M888",
    "M2A7",
    "M1Z3",
    "2MC5",
    "M1T7",
    "2M71",
    "M2C1",
    "M812",
    "M1Z7",
    "M1Y5",
]

# Sidebar / Form Input
st.sidebar.header("Filter & Parameter Input")
store_id_input = st.sidebar.text_input(
    "Masukkan Store ID:", value="M888", help="Contoh: M888"
)
store_id = store_id_input.strip().upper()

filter_val = st.sidebar.text_input(
    "Filter (Opsional):", value="", help="Nilai filter jika ada"
)

# Endpoint API
endpoint_list = "/prd/api/lpb/tablet/lpb/get_faktur/"
endpoint_detail = "/to/api/lpb/tablet/lpb/detail_faktur_unchecking/"

# Header API
headers = {
    "User-Agent": (
        "Dalvik/2.1.0 (Linux; U; Android 11; RMX1971 Build/RKQ1.201217.002)"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "App-Name": "LPB-CLOUD",
    "Version-App": "V.2024.10.15",
    "Version-Code": "11",
    "App-Uid": "10269",
    "User-Id": "0",
    "Store-Id": store_id,
    "Api-Key": "iVOZX9MLmKrj1L8R23uF1aryMR1vGMXG",
    "Platform": "ANDROID",
    "Host": "app.alfastore.co.id",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}


# Fungsi Format Rupiah Presisi
def format_rupiah_murni(val):
  try:
    if pd.isna(val) or val == "":
      return "Rp 0"
    clean_val = str(val).split(".")[0]
    num = int("".join(filter(str.isdigit, clean_val)))
    return f"Rp {num:,}".replace(",", ".")
  except Exception:
    return str(val)


if st.sidebar.button("Muat Daftar Faktur"):
  # Validasi Whitelist Store ID
  if store_id not in ALLOWED_STORES:
    st.error(
        f"❌ **Akses Ditolak!** Store ID **'{store_id}'** tidak terdaftar"
        " memiliki hak akses ke aplikasi ini."
    )
  else:
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
          st.error(
              f"Gagal mengambil data. Status Code: {response.status_code}"
          )
          st.text(response.text)

      except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")

# Tampilkan data jika sudah dimuat
if "faktur_items" in st.session_state:
  items = st.session_state["faktur_items"]
  current_store = st.session_state["store_id"]

  st.markdown("---")
  st.subheader("📋 PO Kiriman (Daftar Faktur)")

  df_list = pd.DataFrame(items)

  if "total_faktur" in df_list.columns:
    df_list["total_faktur"] = df_list["total_faktur"].apply(format_rupiah_murni)

  # Menampilkan tabel daftar faktur tanpa kolom indeks
  st.dataframe(df_list, use_container_width=True, hide_index=True)

  st.markdown("---")
  st.subheader("🔍 Lihat LOV Container & Isi PO")

  list_faktur = [item.get("faktur") for item in items if "faktur" in item]

  if list_faktur:
    selected_faktur = st.selectbox("Pilih Nomor Faktur:", list_faktur)

    selected_row = next(
        (item for item in items if item.get("faktur") == selected_faktur), {}
    )
    raw_total_faktur = selected_row.get("total_faktur", 0)
    formatted_total_rp = format_rupiah_murni(raw_total_faktur)

    if st.button("👁️ Buka LOV Container / Lihat Isi"):
      detail_url = f"https://app.alfastore.co.id{endpoint_detail}"
      detail_params = {"storeId": current_store, "faktur": selected_faktur}

      with st.spinner(f"Memuat LOV Container untuk Faktur {selected_faktur}..."):
        try:
          det_response = requests.post(
              detail_url, headers=headers, params=detail_params, timeout=15
          )

          if det_response.status_code == 200:
            det_json = det_response.json()
            det_items = det_json.get("data", [])

            if isinstance(det_items, list) and len(det_items) > 0:
              df_detail = pd.DataFrame(det_items)

              # Menghapus kolom 'conv2' jika ada
              if "conv2" in df_detail.columns:
                df_detail = df_detail.drop(columns=["conv2"])

              st.success(
                  f"Berhasil memuat LOV Container untuk PO: **{selected_faktur}**"
              )

              # Ringkasan Metrik
              col_m1, col_m2, col_m3 = st.columns(3)
              col_m1.metric("Total Jenis Item", f"{len(df_detail)} PLU")
              col_m2.metric("Total Faktur", formatted_total_rp)

              if "kontainer" in df_detail.columns:
                total_knt = len(df_detail["kontainer"].dropna().unique())
                col_m3.metric("Total Kontainer", f"{total_knt} Kontainer")
              else:
                col_m3.metric("Total Kontainer", "-")

              st.markdown("---")

              # Ringkasan LOV Container
              if "kontainer" in df_detail.columns:
                qty_col = (
                    "qty_ship"
                    if "qty_ship" in df_detail.columns
                    else (
                        "qty_pick"
                        if "qty_pick" in df_detail.columns
                        else df_detail.columns[0]
                    )
                )

                lov_summary = (
                    df_detail.groupby("kontainer")
                    .agg(
                        Item=("plu", "count"),
                        Qty=(qty_col, "sum"),
                    )
                    .reset_index()
                )
                lov_summary.columns = ["Container", "Item", "Qty"]

                st.subheader("📦 LOV CONTAINER (Ringkasan)")
                st.dataframe(
                    lov_summary, use_container_width=True, hide_index=True
                )

                st.markdown("---")
                st.subheader("🔍 Detail Item Per Kontainer (Dropdown / Filter)")

                daftar_kontainer = lov_summary["Container"].tolist()
                pilihan_kontainer = st.selectbox(
                    "Pilih Kontainer Spesifik:", daftar_kontainer
                )

                if pilihan_kontainer:
                  df_sub = df_detail[
                      df_detail["kontainer"].astype(str)
                      == str(pilihan_kontainer)
                  ]
                  st.info(
                      f"Daftar Item dalam Kontainer: **{pilihan_kontainer}**"
                      f" (Total: {len(df_sub)} item)"
                  )
                  st.dataframe(
                      df_sub, use_container_width=True, hide_index=True
                  )

                st.markdown("---")
                st.subheader("📂 Daftar Semua Kontainer (Kartu / Expander)")

                for kontainer in daftar_kontainer:
                  df_sub_exp = df_detail[
                      df_detail["kontainer"].astype(str) == str(kontainer)
                  ]
                  jml_item = len(df_sub_exp)
                  total_qty_sub = pd.to_numeric(
                      df_sub_exp[qty_col], errors="coerce"
                  ).sum()

                  label_expander = (
                      f"📦 Container: {kontainer}  |  Item: {jml_item}  |  Qty:"
                      f" {total_qty_sub:,.0f}"
                  )

                  with st.expander(label_expander):
                    st.dataframe(
                        df_sub_exp, use_container_width=True, hide_index=True
                    )

            else:
              st.info("Detail data kosong.")
          else:
            st.error(
                f"Gagal mengambil detail. Status: {det_response.status_code}"
            )

        except Exception as e:
          st.error(f"Terjadi kesalahan: {e}")
  else:
    st.info("Tidak ada faktur yang tersedia untuk dipilih.")
else:
  st.info(
      "Silakan masukkan Store ID di panel sebelah kiri, lalu klik **Muat Daftar"
      " Faktur** terlebih dahulu."
  )
