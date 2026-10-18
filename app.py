import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD Faktur & Kontainer Viewer", page_icon="🌐", layout="wide"
)

st.title("🚀 Alfastore - Data Faktur & Kontainer LPB")
st.write(
    "Aplikasi untuk mengecek daftar faktur, melihat isi detail per kontainer, "
    "dan mengunduh data."
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
endpoint_detail = "/prd/api/lpb/tablet/lpb/TotalFaktur/"

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

# Fungsi format angka ke format Rupiah Indonesia (Rp 17.663.374)
def format_rupiah(val):
    try:
        num = float(str(val).replace("Rp", "").replace(".", "").replace(",", ".").strip())
        return f"Rp {num:,.0f}".replace(",", ".")
    except Exception:
        return str(val)

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
    st.subheader("📋 PO Kiriman (Daftar Faktur)")
    
    df_list = pd.DataFrame(items)
    
    # Format kolom total_faktur ke format Rupiah jika ada
    if "total_faktur" in df_list.columns:
        df_list["total_faktur"] = df_list["total_faktur"].apply(format_rupiah)

    st.dataframe(df_list, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Lihat Isi / Detail PO")

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
                                f"Berhasil memuat detail PO: **{selected_faktur}**"
                            )

                            # Menghitung Total Nominal Rupiah dari items jika ada kolom harga/total
                            col_total = next(
                                (c for c in df_detail.columns if any(k in c.lower() for k in ["total", "harga", "nominal", "subtotal", "amount", "rp"])),
                                None,
                            )
                            
                            total_rp_val = 0.0
                            if col_total:
                                total_rp_val = pd.to_numeric(
                                    df_detail[col_total].astype(str).str.replace(r"[^\d.]", "", regex=True),
                                    errors="coerce",
                                ).sum()

                            col_m1, col_m2, col_m3 = st.columns(3)
                            col_m1.metric("Total Jenis Item", f"{len(df_detail)} PLU")
                            
                            if col_total and total_rp_val > 0:
                                col_m2.metric("Total Faktur", format_rupiah(total_rp_val))
                            elif "qty_po" in df_detail.columns:
                                total_qty = pd.to_numeric(df_detail["qty_po"], errors="coerce").sum()
                                col_m2.metric("Total QTY (PO)", f"{total_qty:,.0f} Pcs")

                            if "kontainer" in df_detail.columns:
                                total_knt = len(df_detail["kontainer"].dropna().unique())
                                col_m3.metric("Total Kontainer", f"{total_knt} Kontainer")

                            st.markdown("---")

                            # Tampilkan Daftar Kontainer
                            if "kontainer" in df_detail.columns:
                                daftar_kontainer = df_detail["kontainer"].dropna().unique()

                                st.subheader("📦 Daftar Kontainer")

                                # Dropdown Filter Kontainer
                                pilihan_kontainer = st.selectbox(
                                    "Pilih Kontainer Spesifik:",
                                    ["Semua Kontainer"] + [str(k) for k in daftar_kontainer],
                                )

                                if pilihan_kontainer != "Semua Kontainer":
                                    df_sub_pilihan = df_detail[df_detail["kontainer"].astype(str) == str(pilihan_kontainer)]
                                    st.write(f"### 📥 Isi Kontainer: **{pilihan_kontainer}**")
                                    st.dataframe(df_sub_pilihan, use_container_width=True)
                                else:
                                    st.dataframe(df_detail, use_container_width=True)

                                st.write("---")
                                st.write("### 📂 Detail Per Kontainer")

                                # Loop Kartu Kontainer (Sesuai tampilan qty X item di gambar)
                                for kontainer in daftar_kontainer:
                                    df_sub = df_detail[df_detail["kontainer"].astype(str) == str(kontainer)]
                                    jumlah_item = len(df_sub)

                                    label_expander = f"📦 {kontainer}  |  qty {jumlah_item} item"

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
                                st.warning("Kolom kontainer tidak ditemukan pada data API.")
                                st.dataframe(df_detail, use_container_width=True)

                            # Tombol Download Seluruh Isi Faktur
                            csv_data = df_detail.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                label=f"📥 Download Seluruh Isi Faktur {selected_faktur} (CSV)",
                                data=csv_data,
                                file_name=f"detail_faktur_{selected_faktur}.csv",
                                mime="text/csv",
                            )

                        else:
                            st.info("Detail data diterima, tetapi format berupa JSON murni/kosong:")
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
        st.info("Tidak ada faktur yang tersedia untuk dipilih.")
else:
    st.info(
        "Silakan masukkan Store ID di panel sebelah kiri, lalu klik **Muat Daftar"
        " Faktur** terlebih dahulu."
    )
