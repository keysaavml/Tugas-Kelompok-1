"""Integrasi: bandingkan 24 file bulanan (.xlsx) dengan CSV gabungan, dan
periksa perubahan skema (jumlah/nama kolom) antar bulan."""
import pandas as pd
import config as c

c.ensure_dirs()
df = c.load_raw()
files = sorted(c.MONTHLY_DIR.glob("*.xlsx"))
if not files:
    raise SystemExit(f"Tidak ada .xlsx di {c.MONTHLY_DIR}. Salin 24 file bulanan "
                     "ke folder itu (jika ada di arsip Kaggle).")

# jumlah baris per source_file di CSV gabungan
csv_count = (df[c.C_SRC].astype(str).str.replace(r"\.xlsx?$", "", regex=True, case=False)
             .str.strip().str.lower().value_counts())

rows, schema = [], []
all_cols = None
for f in files:
    m = pd.read_excel(f)
    key = f.stem.strip().lower()
    n_csv = int(csv_count.get(key, 0))
    rows.append({"file": f.name, "periode": c.parse_periode(f.name),
                 "baris_xlsx": len(m), "baris_csv": n_csv,
                 "selisih": len(m) - n_csv, "jumlah_kolom": m.shape[1]})
    schema.append({"file": f.name, "kolom": " | ".join(map(str, m.columns))})

res = pd.DataFrame(rows).sort_values("periode")
res.to_csv(c.TABLES / "integrasi_cek_baris.csv", index=False)

sk = pd.DataFrame(schema)
base = sk["kolom"].mode()[0]
sk["sama_dengan_mayoritas"] = sk["kolom"] == base
sk.to_csv(c.TABLES / "integrasi_skema.csv", index=False)

print(res.to_string(index=False))
print(f"\nTotal baris xlsx = {res.baris_xlsx.sum()}, baris CSV = {len(df)}")
print("Selisih tiap bulan semua 0:", bool((res.selisih == 0).all()))
beda = sk[~sk.sama_dengan_mayoritas]
if len(beda):
    print("\nFile dengan skema berbeda dari mayoritas:")
    print(beda[["file", "kolom"]].to_string(index=False))
