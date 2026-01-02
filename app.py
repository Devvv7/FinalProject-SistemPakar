import streamlit as st
from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "12345678"

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        print(result.single())
    print("Koneksi Sukses!")
except Exception as e:
    print("Error:", e)

# Function menjalankan query
def run_query(query, params=None):
    with driver.session() as session:
        return session.run(query, params).data()


# ==========================================================
# 2️⃣ AMBIL DATA DARI NEO4J
# ==========================================================
def get_all_gejala():
    q = """
    MATCH (g:Gejala)
    RETURN g.kode AS kode, g.nama AS nama, g.bobot AS bobot
    ORDER BY g.kode
    """
    return run_query(q)

def get_all_penyakit():
    q = """
    MATCH (p:Penyakit)
    RETURN p.kode AS kode, p.nama AS nama
    """
    return run_query(q)

def get_gejala_penyakit(kode_penyakit):
    q = """
    MATCH (:Penyakit {kode: $kode})-[:MEMILIKI_GEJALA]->(g:Gejala)
    RETURN g.kode AS kode, g.bobot AS bobot
    """
    return run_query(q, {"kode": kode_penyakit})


def get_solusi(penyakit_kode):
    q = """
    MATCH (p:Penyakit {kode: $kode})-[:MEMILIKI_SOLUSI]->(s:Solusi)
    RETURN s.teks AS solusi
    """
    return run_query(q, {"kode": penyakit_kode})


# ==========================================================
# 3️⃣ HITUNG CERTAINTY FACTOR
# ==========================================================
def hitung_cf(user_gejala, gejala_penyakit):
    """
    user_gejala      : list kode gejala yang dipilih user → ["G01","G03",...]
    gejala_penyakit  : list dict dari Neo4j → [{"kode": "G01", "bobot": 0.8}, ...]
    """

    cf_total = None        # digunakan saat combine pertama kali
    logs = []              # menyimpan proses perhitungan CF

    for g in gejala_penyakit:
        kode = g["kode"].upper()
        bobot = g.get("bobot", 0)

        if kode in user_gejala:

            # user yakin karena memilih gejalanya → 1
            cf_user = 1.0
            cf_pakar = bobot

            # CF pertama
            cf = cf_user * cf_pakar

            # combine CF jika sudah ada CF sebelumnya
            if cf_total is None:
                cf_total = cf
            else:
                cf_total = cf_total + (cf * (1 - cf_total))

            # simpan proses langkah per langkah
            logs.append({
                "kode_gejala": kode,
                "bobot_pakar": bobot,
                "cf_user": cf_user,
                "cf_hitung": cf,
                "cf_total_after_combine": cf_total
            })

    # kalau tidak ada gejala yang match
    if cf_total is None:
        return 0, logs

    return cf_total, logs


# ==========================================================
# 4️⃣ STREAMLIT UI
# ==========================================================
st.title("🐶 Sistem Pakar Penyakit Kulit Anjing")
st.write("Metode: **Certainty Factor (CF)** + **Neo4j Graph Database**")

st.header("🩺 Input Gejala")
gejala = get_all_gejala()

user_gejala = []

# Checkbox untuk setiap gejala
for g in gejala:
    if st.checkbox(f"{g['kode']} - {g['nama']}"):
        user_gejala.append(g["kode"])

st.write("### ✔ Gejala yang dipilih:", user_gejala)

if st.button("Diagnosa Penyakit"):
    if not user_gejala:
        st.warning("Pilih minimal satu gejala.")
    else:
        penyakit_list = get_all_penyakit()  # [{"kode":..., "nama":...}, ...]
        hasil_list = []      # untuk tabel
        log_all = {}         # untuk menyimpan log setiap penyakit

        # Hitung CF setiap penyakit
        for p in penyakit_list:
            kode_p = p["kode"]
            nama_p = p["nama"]

            gejala_p = get_gejala_penyakit(kode_p)  # [{"kode":..., "bobot":...}, ...]

            cf_value, logs = hitung_cf(user_gejala, gejala_p)

            hasil_list.append({
                "kode": kode_p,
                "nama": nama_p,
                "cf": cf_value
            })

            log_all[nama_p] = logs

        # Urutkan hasil berdasarkan CF terbesar → terkecil
        hasil_list = sorted(hasil_list, key=lambda x: x["cf"], reverse=True)

        # ==========================
        # 🔵 Tampilkan tabel hasil CF
        # ==========================
        st.header("📊 Hasil Perhitungan CF")

        import pandas as pd
        hasil_df = pd.DataFrame(hasil_list)

        if not hasil_df.empty:
            hasil_df["cf"] = hasil_df["cf"].apply(lambda v: f"{v:.4f}")
            hasil_df = hasil_df.rename(columns={
                "kode": "Kode",
                "nama": "Penyakit",
                "cf": "Nilai CF"
            })
            st.dataframe(hasil_df, use_container_width=True)
        else:
            st.write("Tidak ada penyakit di database.")

        # ==========================
        # 🔵 Prediksi penyakit tertinggi
        # ==========================
        if hasil_list and hasil_list[0]["cf"] > 0:
            top = hasil_list[0]
            prediksi_nama = top["nama"]
            prediksi_kode = top["kode"]
            nilai_cf = top["cf"]

            st.subheader("🐾 Prediksi Penyakit Paling Mungkin:")
            st.success(f"{prediksi_nama} (Kode: {prediksi_kode}) — CF = {nilai_cf:.4f}")

            # ==========================
            # 🔵 Tampilkan log perhitungan untuk penyakit teratas
            # ==========================
            st.info("### 📘 Detail Perhitungan CF (Langkah Demi Langkah)")
            logs = log_all.get(prediksi_nama, [])

            if logs:
                for step in logs:
                    st.markdown(f"""
                    **Gejala: {step['kode_gejala']}**

                    - Bobot pakar: `{step['bobot_pakar']}`
                    - CF user   : `{step['cf_user']}`
                    - CF dihitung (CF_user × CF_pakar): `{step['cf_hitung']}`
                    - CF total setelah combine: `{step['cf_total_after_combine']}`
                    ---
                    """)
            else:
                st.write("Tidak ada log perhitungan untuk penyakit ini.")

            # ==========================
            # 🔵 Ambil solusi penyakit
            # ==========================
            solusi = get_solusi(prediksi_kode)

            if solusi:
                st.info("### 💊 Solusi / Penanganan:")
                for s in solusi:
                    teks = s.get("solusi") or s.get("teks") or s.get("deskripsi") or str(s)
                    st.write("- " + teks)
            else:
                st.warning("Solusi penyakit belum tersedia di database.")

        else:
            st.warning("Tidak ditemukan penyakit yang cocok (semua CF = 0).")