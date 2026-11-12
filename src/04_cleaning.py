"""Cleaning, integrasi, transformasi: data/raw -> data/processed/ecom_clean.csv.
Tidak ada baris yang dihapus; outlier hanya DITANDAI. Semua langkah dicatat
ke tables/catatan_cleaning.csv dan docs/catatan_cleaning.md."""
import pandas as pd
import config as c

c.ensure_dirs()
df = c.load_raw()
catatan = []


def log(langkah, sebelum, sesudah, alasan):
    catatan.append({"langkah": langkah, "baris_sebelum": sebelum,
                    "baris_sesudah": sesudah, "alasan": alasan})


# 1. rapikan spasi pada kolom teks
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    df[col] = df[col].astype(object).where(df[col].notna(), None)
log("Rapikan spasi kolom teks", len(df), len(df), "Mencegah satu kategori tercatat ganda karena spasi.")

# 2. duplikat penuh
n0 = len(df)
df = df.drop_duplicates().reset_index(drop=True)
log("Hapus baris duplikat penuh", n0, len(df), f"{n0 - len(df)} baris duplikat.")

# 3. tanggal
df[c.C_TIME] = pd.to_datetime(df[c.C_TIME], errors="coerce")
df["tanggal_kosong"] = df[c.C_TIME].isna()
log("Ubah ke datetime + penanda tanggal_kosong", len(df), len(df),
    f"{int(df['tanggal_kosong'].sum())} baris kosong (umumnya file bulanan tanpa kolom tanggal).")

# 4. periode dari nama file
df["periode"] = df[c.C_SRC].map(c.parse_periode)
df["tahun"] = df["periode"].str[:4].astype("Int64")
df["bulan"] = df["periode"].str[5:7].astype("Int64")
gagal = int(df["periode"].isna().sum())
log("Buat periode/tahun/bulan dari source_file", len(df), len(df),
    f"Memulihkan bulan untuk baris tanpa tanggal. Gagal terbaca: {gagal} baris.")
if gagal:
    print("PERINGATAN: ada source_file yang tidak terbaca ->",
          df.loc[df.periode.isna(), c.C_SRC].unique()[:5])


# 5. status
def std_status(s):
    t = str(s).strip().lower()
    if t == "selesai":
        return "Selesai"
    if t == "batal":
        return "Batal"
    if t.startswith("pesanan diterima"):
        return "Diterima (masa pengembalian)"
    if t in ("sedang dikirim", "telah dikirim"):
        return "Dalam pengiriman"
    return "Lainnya"


df["status_final"] = df[c.C_STATUS].map(std_status)
df["is_batal"] = (df["status_final"] == "Batal").astype(int)
df["dipakai_klasifikasi"] = df["status_final"].isin(["Selesai", "Batal"])
log("Standardisasi Status Pesanan", len(df), len(df),
    f"{df[c.C_STATUS].nunique()} varian -> {df['status_final'].nunique()} kelompok; target = Selesai vs Batal.")


# 6. alasan pembatalan (aturan kata kunci; CEK terhadap tables/profil_label_alasan.csv)
def std_alasan(s):
    if pd.isna(s):
        return (None, None)
    t = str(s).lower()
    if any(k in t for k in ("belum dibayar", "belum membayar", "tidak dibayar", "unpaid", "not paid", "pembayaran belum")):
        return ("Belum dibayar", "Sistem")
    if "alamat" in t or "address" in t:
        return ("Ubah alamat", "Pembeli")
    if "ubah pesanan" in t or "modify" in t or "change order" in t or "perubahan pesanan" in t:
        return ("Ubah pesanan", "Pembeli")
    if "stok" in t or "stock" in t:
        return ("Stok habis", "Penjual")
    if "voucher" in t:
        return ("Masalah voucher", "Pembeli")
    if "kurir" in t or "pengiriman" in t or "courier" in t or "shipping" in t or "delivery" in t:
        return ("Masalah pengiriman", "Sistem")
    if "pembayaran" in t or "payment" in t:
        return ("Masalah pembayaran", "Sistem")
    if "pikiran" in t or "lainnya" in t or "other" in t or "mind" in t:
        return ("Lainnya/berubah pikiran", "Pembeli")
    return ("Lainnya/berubah pikiran", "Pembeli")


tmp = df[c.C_REASON].map(std_alasan)
df["alasan_baku"] = tmp.map(lambda x: x[0])
df["pembatal"] = tmp.map(lambda x: x[1])
# penanda eksplisit pada teks mengalahkan tebakan kata kunci
t = df[c.C_REASON].astype(str).str.lower()
df.loc[t.str.contains("penjual|seller", regex=True) & df[c.C_REASON].notna(), "pembatal"] = "Penjual"
df.loc[t.str.contains("sistem|otomatis|system|automatic", regex=True) & df[c.C_REASON].notna(), "pembatal"] = "Sistem"
log("Standardisasi Alasan Pembatalan", len(df), len(df),
    f"{df[c.C_REASON].nunique()} varian -> {df['alasan_baku'].nunique()} alasan baku + pihak pembatal.")


# 7. opsi pengiriman -> layanan & kurir
def kurir_of(s):
    t = str(s).lower()
    if "spx" in t or "shopee express" in t:
        return "SPX"
    if "jne" in t:
        return "JNE"
    if "j&t" in t or "jnt" in t or "j & t" in t:
        return "J&T"
    if any(k in t for k in ("instan", "same day", "sameday", "grab", "gosend", "go-send", "ninja", "sicepat", "anteraja", "lion", "pos")):
        return "Instan/lainnya"
    return "Belum ditentukan"


df["layanan_kirim"] = df[c.C_SHIP].astype("string").str.replace(r"\s*\(\s*", " (", regex=True).str.strip()
df["kurir"] = df[c.C_SHIP].map(kurir_of)
log("Standardisasi Opsi Pengiriman", len(df), len(df),
    f"{df[c.C_SHIP].nunique()} varian -> {df['layanan_kirim'].nunique()} layanan; kurir dikelompokkan "
    "SPX, JNE, J&T, Instan/lainnya, Belum ditentukan.")

# 8. kolom bantu EDA
df["kategori_utama"] = df[c.C_CATS].astype("string").str.split(",").str[0].str.strip()
df["ongkir_gratis"] = (df[c.C_FEE_PAID] == 0).astype(int)
df["pembayaran_nol"] = (df[c.C_TOTAL] == 0).astype(int)
df["ongkir_per_kg"] = (df[c.C_FEE_EST] / (df[c.C_WEIGHT] / 1000)).round(2)
q1, q3 = df[c.C_TOTAL].quantile([.25, .75])
df["outlier_pembayaran"] = (df[c.C_TOTAL] > q3 + 1.5 * (q3 - q1)).astype(int)
log("Kolom bantu EDA", len(df), len(df),
    "kategori_utama, ongkir_gratis, pembayaran_nol, ongkir_per_kg, outlier_pembayaran. Outlier hanya ditandai.")

df.to_csv(c.CLEAN_CSV, index=False, encoding="utf-8-sig", sep=";")
cat = pd.DataFrame(catatan)
cat.to_csv(c.TABLES / "catatan_cleaning.csv", index=False)
with open(c.DOCS / "catatan_cleaning.md", "w", encoding="utf-8") as f:
    f.write("# Catatan Cleaning\n\n| Langkah | Baris sebelum | Baris sesudah | Alasan |\n|---|---|---|---|\n")
    for r in catatan:
        f.write(f"| {r['langkah']} | {r['baris_sebelum']} | {r['baris_sesudah']} | {r['alasan']} |\n")

print(cat.to_string(index=False))
print(f"\nHasil: {c.CLEAN_CSV}  ({len(df)} baris, {df.shape[1]} kolom)")
print(df["status_final"].value_counts().to_string())
print("\nCek hasil pemetaan (sesuaikan aturan jika ada yang janggal):")
print(df.groupby([c.C_REASON, "alasan_baku", "pembatal"], dropna=True).size().to_string())
