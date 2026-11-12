"""Profiling: kamus data, null, duplikasi, outlier (IQR), distribusi,
inkonsistensi label, konsistensi logika. Hasil ke tables/profil_*.csv."""
import pandas as pd
import config as c

c.ensure_dirs()
df = c.load_raw()
n = len(df)

# ---- 1. Kamus data ----------------------------------------------------------
KAMUS = [
    (c.C_ID, "ID pesanan (anonim)", "teks", "-", "Kunci"),
    (c.C_QTY, "Jumlah barang dalam pesanan", "angka", "unit", "Fitur"),
    (c.C_WEIGHT, "Berat total pesanan", "angka", "gram", "Fitur"),
    (c.C_RET, "Jumlah barang dikembalikan", "angka", "unit", "Waspada bocor"),
    (c.C_DISC, "Total potongan harga", "angka", "Rupiah*", "Fitur"),
    (c.C_CATS, "Kategori produk (dipisah koma)", "teks", "-", "Fitur"),
    (c.C_NCATS, "Banyak kategori dalam satu pesanan", "angka", "jumlah", "Fitur"),
    (c.C_STATUS, "Status akhir pesanan", "kategori", "-", "TARGET"),
    (c.C_REASON, "Alasan batal (kosong bila tidak batal)", "kategori", "-", "Jangan dipakai (bocor)"),
    (c.C_SHIP, "Layanan kirim", "kategori", "-", "Fitur (waspada)"),
    (c.C_PAY, "Cara pembeli membayar", "kategori", "-", "Fitur"),
    (c.C_CITY, "Kota/kabupaten tujuan", "kategori", "-", "Fitur"),
    (c.C_PROV, "Provinsi tujuan", "kategori", "-", "Fitur"),
    (c.C_FEE_PAID, "Ongkir yang ditanggung pembeli", "angka", "Rupiah*", "Waspada bocor"),
    (c.C_FEE_DISC, "Subsidi/potongan ongkir", "angka", "Rupiah*", "Waspada bocor"),
    (c.C_TOTAL, "Total yang dibayar pembeli", "angka", "Rupiah*", "Waspada bocor"),
    (c.C_FEE_EST, "Perkiraan biaya kirim sebenarnya", "angka", "Rupiah*", "Fitur"),
    (c.C_TIME, "Tanggal dan jam pesanan dibuat", "waktu", "-", "Fitur waktu"),
    (c.C_SRC, "Nama file bulanan asal", "teks", "-", "Metadata"),
]
kamus = pd.DataFrame(KAMUS, columns=["variabel", "arti", "tipe", "satuan", "peran"])
kamus["tipe_pandas"] = kamus["variabel"].map(lambda v: str(df[v].dtype) if v in df else "tidak ada")
kamus["pct_kosong"] = kamus["variabel"].map(lambda v: round(df[v].isna().mean() * 100, 2) if v in df else None)
kamus["n_unik"] = kamus["variabel"].map(lambda v: df[v].nunique() if v in df else None)
kamus.to_csv(c.TABLES / "kamus_data.csv", index=False)
with open(c.DOCS / "kamus_data.md", "w", encoding="utf-8") as f:
    f.write("# Kamus Data\n\n- Kunci: `order_id`\n- Grain: 1 baris = 1 pesanan\n"
            "- Target: `Status Pesanan` (Batal vs Selesai)\n"
            "- *Satuan Rupiah adalah asumsi (dataset tidak menyebut mata uang).\n\n")
    f.write("| " + " | ".join(kamus.columns) + " |\n")
    f.write("|" + "---|" * len(kamus.columns) + "\n")
    for _, r in kamus.iterrows():
        f.write("| " + " | ".join(str(x) for x in r.values) + " |\n")

# ---- 2. Null ----------------------------------------------------------------
nul = pd.DataFrame({"kolom": df.columns, "n_kosong": df.isna().sum().values})
nul["pct_kosong"] = (nul.n_kosong / n * 100).round(2)
nul.to_csv(c.TABLES / "profil_null.csv", index=False)
tgl_kosong = df[df[c.C_TIME].isna()][c.C_SRC].value_counts()
tgl_kosong.rename("n_tanggal_kosong").to_csv(c.TABLES / "profil_null_tanggal_per_file.csv")

# ---- 3. Duplikasi -----------------------------------------------------------
dup = pd.DataFrame([("baris duplikat penuh", int(df.duplicated().sum())),
                    ("order_id ganda", int(df[c.C_ID].duplicated().sum()))],
                   columns=["pemeriksaan", "jumlah"])
dup.to_csv(c.TABLES / "profil_duplikat.csv", index=False)

# ---- 4. Outlier & distribusi ------------------------------------------------
out = []
for col in c.NUM_COLS:
    s = pd.to_numeric(df[col], errors="coerce")
    q1, q3 = s.quantile(.25), s.quantile(.75)
    batas = q3 + 1.5 * (q3 - q1)
    out.append({"kolom": col, "min": s.min(), "q1": q1, "median": s.median(),
                "q3": q3, "maks": s.max(), "rata2": round(s.mean(), 2),
                "std": round(s.std(), 2), "skew": round(s.skew(), 2),
                "batas_atas_iqr": batas, "n_outlier": int((s > batas).sum()),
                "pct_outlier": round((s > batas).mean() * 100, 2),
                "n_negatif": int((s < 0).sum()), "n_nol": int((s == 0).sum())})
pd.DataFrame(out).to_csv(c.TABLES / "profil_outlier.csv", index=False)

# ---- 5. Inkonsistensi label -------------------------------------------------
for nama, col in [("status", c.C_STATUS), ("alasan", c.C_REASON),
                  ("opsi_pengiriman", c.C_SHIP), ("metode_pembayaran", c.C_PAY)]:
    vc = df[col].value_counts(dropna=False).rename_axis("nilai").reset_index(name="jumlah")
    vc.to_csv(c.TABLES / f"profil_label_{nama}.csv", index=False)
    print(f"{col}: {df[col].nunique()} varian -> tables/profil_label_{nama}.csv")

# ---- 6. Konsistensi logika & kebocoran -------------------------------------
batal = df[c.C_STATUS].astype(str).str.strip().str.lower().eq("batal")
cek = [
    ("Alasan terisi tetapi status bukan Batal", int((df[c.C_REASON].notna() & ~batal).sum())),
    ("Status Batal tetapi alasan kosong", int((df[c.C_REASON].isna() & batal).sum())),
    ("Dikembalikan > dibeli", int((df[c.C_RET] > df[c.C_QTY]).sum())),
    ("num_product_categories != jumlah kategori di teks",
     int((df[c.C_CATS].fillna("").str.split(",").map(
         lambda x: len([i for i in x if i.strip()])) != df[c.C_NCATS]).sum())),
    ("Pesanan dengan barang dikembalikan (>0)", int((df[c.C_RET] > 0).sum())),
    ("Total Pembayaran = 0", int((df[c.C_TOTAL] == 0).sum())),
    ("Perkiraan ongkir = ongkir dibayar + potongan",
     int((df[c.C_FEE_EST] == df[c.C_FEE_PAID] + df[c.C_FEE_DISC]).sum())),
]
pd.DataFrame(cek, columns=["pemeriksaan", "baris"]).to_csv(c.TABLES / "profil_logika.csv", index=False)

# kebocoran: % nol pada Batal vs non-Batal
rows = []
for col in [c.C_TOTAL, c.C_FEE_PAID, c.C_FEE_DISC, c.C_FEE_EST, c.C_DISC]:
    rows.append({"fitur": col,
                 "pct_nol_batal": round((df.loc[batal, col] == 0).mean() * 100, 1),
                 "pct_nol_nonbatal": round((df.loc[~batal, col] == 0).mean() * 100, 1)})
pd.DataFrame(rows).to_csv(c.TABLES / "profil_kebocoran.csv", index=False)

print(f"\nBaris: {n}, kolom: {df.shape[1]}")
print(dup.to_string(index=False)); print(pd.DataFrame(cek, columns=['cek','baris']).to_string(index=False))
print("Profiling selesai. Tabel di tables/profil_*.csv")
