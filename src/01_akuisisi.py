"""Akuisisi: catat versi, tanggal akses, parameter, ukuran, checksum SHA-256,
lalu kunci data mentah menjadi read-only. Data mentah TIDAK diubah."""
import hashlib, os, stat
import pandas as pd
import config as c

c.ensure_dirs()
if not c.RAW_CSV.exists():
    raise SystemExit(f"Berkas tidak ditemukan: {c.RAW_CSV}\n"
                     "Salin all_months_clean.csv dari Kaggle ke data/raw/ dulu.")


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(chunk), b""):
            h.update(blok)
    return h.hexdigest()


df = c.load_raw()
tgl = pd.to_datetime(df[c.C_TIME], errors="coerce")
info = [
    ("Dataset", c.DATASET_NAME), ("URL", c.DATASET_URL),
    ("Lisensi", c.LICENSE), ("Versi", c.VERSION),
    ("Berkas", c.RAW_CSV.name), ("Parameter", c.PARAMETER),
    ("Tanggal akses", c.ACCESS_DATE),
    ("Pemisah / encoding", "titik-koma (;) / UTF-8 dengan BOM"),
    ("SHA-256", sha256(c.RAW_CSV)),
    ("Ukuran (byte)", os.path.getsize(c.RAW_CSV)),
    ("Jumlah baris", len(df)), ("Jumlah kolom", df.shape[1]),
    ("Tanggal terawal", tgl.min()), ("Tanggal terakhir", tgl.max()),
]
if c.MONTHLY_DIR.exists():
    for f in sorted(c.MONTHLY_DIR.glob("*.xlsx")):
        info.append((f"SHA-256 {f.name}", sha256(f)))

out = pd.DataFrame(info, columns=["item", "nilai"])
out.to_csv(c.TABLES / "akuisisi_log.csv", index=False)
with open(c.DOCS / "akuisisi_log.md", "w", encoding="utf-8") as f:
    f.write("# Log Akuisisi Data\n\n| Item | Nilai |\n|---|---|\n")
    for k, v in info:
        f.write(f"| {k} | {v} |\n")

# kunci read-only (pencegahan edit tak sengaja)
targets = [c.RAW_CSV] + (list(c.MONTHLY_DIR.glob("*.xlsx")) if c.MONTHLY_DIR.exists() else [])
for p in targets:
    os.chmod(p, stat.S_IREAD)
print(out.to_string(index=False))
print("\nData mentah dikunci read-only. Log: tables/akuisisi_log.csv")
