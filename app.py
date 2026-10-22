import datetime
import pandas as pd
import requests
import streamlit as st

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CEXP-CLOUD LOV Container Viewer",
    page_icon="📦",
    layout="wide",
)

# 2. Injeksi CSS Lengkap (Sembunyikan Header, Footer, Watermark, & Menu Streamlit)
hide_streamlit_style = """
    <style>
    /* Sembunyikan Header, Footer, & Menu Titik Tiga Bawaan */
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    footer[data-testid="stFooter"] {display: none !important; visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* Sembunyikan Toolbar & Status Widget */
    div[data-testid="stToolbar"] {visibility: hidden !important; height: 0px !important;}
    div[data-testid="stDecoration"] {visibility: hidden !important; width: 0px !important; height: 0px !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    
    /* Sembunyikan "Hosted with Streamlit" & Badge Kanan Bawah */
    .stApp > footer {display: none !important; visibility: hidden !important;}
    [data-testid="stAppViewBlockContainer"] + div {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="stAppViewerBadges"] {display: none !important;}
    iframe[title="Streamlit App Viewer"] {display: none !important;}
    
    /* Optimasi Jarak Layar */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🚀 Alfastore - LOV Container & Detail PO")
st.write(
    "Aplikasi untuk mengecek daftar faktur, ringkasan kontainer (LOV Container),"
    " serta detail item per kontainer."
)

# Kamus / Dictionary Store ID dan Nama Toko
STORE_OPTIONS = {
    "M1U8": "M1U8 - KARANGTALUN TLA",
    "M953": "M953 - KALIDAWIR TLG",
    "M885": "M885 - JABON TULUNGAGUNG",
    "M1S6": "M1S6 - NGUNUT KRAJAN TLA",
    "M1S4": "M1S4 - TUGU TULUNGAGUNG",
    "M750": "M750 - KALANGAN TULUNGAGUNG",
    "M1Z4": "M1Z4 - PAKISREJO TLA",
    "M898": "M898 - KALIWUNGU T.A",
    "M888": "M888 - KACANGAN TULUNGAGUNG",
    "M2A7": "M2A7 - PANDEAN TLA",
    "M1Z3": "M1Z3 - KSO+ NGUNUT",
    "2MC5": "2MC5 - NGUNUT BARU TLA",
    "M1T7": "M1T7 - SAMBIDOPLANG TLA",
    "M2C1": "M2C1 - SUMBERAGUNG TLA",
    "M812": "M812 - REJOTANGAN TLG",
    "M1Z7": "M1Z7 - SELOREJO TLA",
    "2M71": "2M71 - KALIWUNGU BARU",
    "M1Y5": "M1Y5 - BALESONO TLA",
}

# =========================================================
# FORM INPUT TOKO & TANGGAL DI HALAMAN UTAMA
# =========================================================
st.markdown("---")
st.subheader("🏪 Pilih Toko & Parameter Input")

col_input1, col_input2, col_input3 = st.columns([2, 1, 1])

with col_input1:
    selected_store_label = st.selectbox(
        "Pilih Toko (Store ID):",
        options=list(STORE_OPTIONS.values()),
        index=8,  # Default M888 KACANGAN TULUNGAGUNG
    )

with col_input2:
    selected_date = st.date_input(
        "Pilih Tanggal:",
        value=datetime.date.today()
    )

with col_input3:
    filter_val = st.text_input(
        "Filter (Opsional):", value="", help="Nilai filter jika ada"
    )

# Mengambil Kode Store ID (4 karakter pertama) dan Format Tanggal
store_id = selected_store_label.split(" - ")[0]
date_str = selected_date.strftime("%Y-%m-%d")

# Tombol Muat Daftar Faktur
btn_load = st.button("🔄 Muat Daftar Faktur", use_container_width=True)

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
    "User-Id": "24123825",
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


if btn_load:
    url = f"https://app.alfastore.co.id{endpoint_list}"
    # Parameter diperbarui dengan menyertakan tanggal (date/tanggal)
    params = {"storeId": store_id, "date": date_str, "filter": filter_val}

    with st.spinner("Menghubungkan ke server..."):
        try:
            # Pemanggilan API dengan penanganan status code lengkap
            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                res_json = response.json()
                items = res_json.get("data", [])

                if isinstance(items, list) and len(items) > 0:
                    st.success(
                        f"Berhasil mengambil daftar faktur untuk Store: **{selected_store_label}** (Tanggal: {date_str})"
                    )
                    st.session_state["faktur_items"] = items
                    st.session_state["store_id"] = store_id
                    st.session_state["store_label"] = selected_store_label
                else:
                    st.warning("⚠️ Data kosong dari server untuk toko dan tanggal ini.")
                    if "faktur_items" in st.session_state:
                        del st.session_state["faktur_items"]

            elif response.status_code == 204:
                # Tangani Status Code 204 secara khusus
                st.warning(
                    "⚠️ Tidak ada data faktur / LOV Container yang ditemukan untuk toko dan tanggal ini (Status 204)."
                )
                if "faktur_items" in st.session_state:
                    del st.session_state["faktur_items"]

            else:
                st.error(f"Gagal mengambil data. Status Code: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Terjadi kesalahan koneksi: {e}")

# Tampilkan data jika sudah dimuat
if "faktur_items" in st.session_state:
    items = st.session_state["faktur_items"]
    current_store = st.session_state["store_id"]
    current_label = st.session_state.get("store_label", current_store)

    st.markdown("---")
    st.subheader(f"📋 PO Kiriman ({current_label})")

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

                            st.session_state["df_detail"] = df_detail
                            st.session_state["faktur_active"] = selected_faktur
                            st.session_state["formatted_total_rp"] = formatted_total_rp
                        else:
                            st.info("Detail data kosong.")
                    elif det_response.status_code == 204:
                        st.warning("⚠️ Detail data faktur ini kosong (Status 204).")
                    else:
                        st.error(
                            f"Gagal mengambil detail. Status: {det_response.status_code}"
                        )

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

        # Tampilkan Detail jika sudah dimuat dalam session state
        if (
            "df_detail" in st.session_state
            and st.session_state.get("faktur_active") == selected_faktur
        ):
            df_detail = st.session_state["df_detail"]
            formatted_total_rp = st.session_state["formatted_total_rp"]

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

            # FITUR 1: PENCARIAN PLU & NAMA BARANG (DESCP)
            st.subheader("🔍 Cari Lokasi Kontainer Barang")
            search_query = st.text_input(
                "🔎 Cari PLU atau Nama Barang (Descp):",
                value="",
                placeholder="Ketik kode PLU atau nama barang (misal: Indomie)...",
            )

            if search_query.strip():
                q = search_query.strip().lower()

                mask = pd.Series(False, index=df_detail.index)
                if "plu" in df_detail.columns:
                    mask = mask | df_detail["plu"].astype(str).str.lower().str.contains(q)
                if "descp" in df_detail.columns:
                    mask = (
                        mask | df_detail["descp"].astype(str).str.lower().str.contains(q)
                    )

                df_search_res = df_detail[mask]

                if not df_search_res.empty:
                    st.success(
                        f"Ditemukan **{len(df_search_res)}** item hasil pencarian:"
                    )
                    st.dataframe(
                        df_search_res, use_container_width=True, hide_index=True
                    )
                else:
                    st.warning(
                        f"Barang dengan kata kunci **'{search_query}'** tidak ditemukan"
                        " pada PO ini."
                    )
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
                st.dataframe(lov_summary, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("🔍 Detail Item Per Kontainer (Dropdown / Filter)")

                daftar_kontainer = lov_summary["Container"].tolist()
                pilihan_kontainer = st.selectbox(
                    "Pilih Kontainer Spesifik:", daftar_kontainer
                )

                if pilihan_kontainer:
                    df_sub = df_detail[
                        df_detail["kontainer"].astype(str) == str(pilihan_kontainer)
                    ]
                    st.info(
                        f"Daftar Item dalam Kontainer: **{pilihan_kontainer}**"
                        f" (Total: {len(df_sub)} item)"
                    )
                    st.dataframe(df_sub, use_container_width=True, hide_index=True)

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
        st.info("Tidak ada faktur yang tersedia untuk dipilih.")
else:
    st.info(
        "Silakan pilih Toko dan Tanggal di atas, lalu klik **Muat Daftar Faktur** terlebih"
        " dahulu."
    )
