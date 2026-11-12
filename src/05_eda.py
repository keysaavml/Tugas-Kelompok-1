"""EDA untuk lima pertanyaan penelitian. Tabel -> tables/eda_*.csv,
grafik -> figures/01..08 (.png). Hasil berupa asosiasi, bukan sebab-akibat."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import config as c

c.ensure_dirs()
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .3})
BLUE, RED, GREY, GOLD = "#1f5fa8", "#d9534f", "#78909c", "#dba02d"
df = pd.read_csv(c.CLEAN_CSV, sep=";", encoding="utf-8-sig")
nb = df[df["is_batal"] == 0]                      # non-batal (nilai uang valid)
sel = df[df["status_final"] == "Selesai"]
cls = df[df["dipakai_klasifikasi"]]


def save(fig, nama):
    fig.tight_layout()
    fig.savefig(c.FIGURES / nama)
    plt.close(fig)


# ---- Statistik ringkas ------------------------------------------------------
cols = [c.C_QTY, c.C_WEIGHT, c.C_TOTAL, c.C_FEE_PAID, c.C_FEE_EST, c.C_DISC]
stat = nb[cols].agg(["mean", "std", "min", "median", "max"]).T.round(1)
stat.to_csv(c.TABLES / "eda_statistik_ringkas.csv")
print("Statistik ringkas (non-batal):\n", stat, "\n")

# ---- Q1: tren bulanan ------------------------------------------------------
m = df.groupby("periode").size().rename("jumlah_pesanan")
m_val = sel.groupby("periode")[c.C_TOTAL].sum().rename("total_pembayaran_selesai")
q1 = pd.concat([m, m_val], axis=1).reset_index()
q1.to_csv(c.TABLES / "eda_q1_tren_bulanan.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(q1["periode"], q1["jumlah_pesanan"], marker="o", color=BLUE)
imax, imin = q1["jumlah_pesanan"].idxmax(), q1["jumlah_pesanan"].idxmin()
for i, lab in [(imax, "Puncak"), (imin, "Terendah")]:
    ax.annotate(f"{lab}: {q1.jumlah_pesanan[i]:,}\n({q1.periode[i]})".replace(",", "."),
                (i, q1.jumlah_pesanan[i]), textcoords="offset points", xytext=(12, 8), fontsize=7)
ax.set_title("Jumlah pesanan per bulan"); ax.set_ylabel("jumlah pesanan")
ax.set_xticks(range(len(q1))); ax.set_xticklabels(q1["periode"], rotation=60, ha="right", fontsize=7)
save(fig, "01_pesanan_per_bulan.png")

# ---- Q2: kategori produk ---------------------------------------------------
ex = df.assign(kat=df[c.C_CATS].fillna("").str.split(",")).explode("kat")
ex["kat"] = ex["kat"].str.strip()
ex = ex[ex["kat"] != ""]
q2n = ex.groupby("kat")[c.C_ID].nunique().sort_values(ascending=False).rename("jumlah_pesanan").reset_index()
q2n["persen_pesanan"] = (q2n["jumlah_pesanan"] / len(df) * 100).round(2)
q2n.to_csv(c.TABLES / "eda_kategori_jumlah.csv", index=False)
q2v = (nb.groupby("kategori_utama")[c.C_TOTAL].agg(total_pembayaran="sum", jumlah_pesanan="size")
       .sort_values("total_pembayaran", ascending=False).reset_index())
q2v.to_csv(c.TABLES / "eda_kategori_utama_nilai.csv", index=False)
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
t = q2n.head(10).iloc[::-1]
axs[0].barh(t["kat"], t["jumlah_pesanan"], color=BLUE); axs[0].set_title("10 kategori terbanyak (jumlah pesanan)")
t = q2v.head(10).iloc[::-1]
axs[1].barh(t["kategori_utama"], t["total_pembayaran"] / 1e6, color=GOLD); axs[1].set_title("10 kategori utama bernilai tertinggi (juta Rp)")
for a in axs: a.tick_params(axis="y", labelsize=7)
save(fig, "02_kategori_produk.png")

# ---- Q3: metode pembayaran -------------------------------------------------
q3 = df[c.C_PAY].value_counts().rename("jumlah").reset_index()
q3["persen"] = (q3["jumlah"] / len(df) * 100).round(2)
q3.to_csv(c.TABLES / "eda_metode_pembayaran.csv", index=False)
fig, ax = plt.subplots(figsize=(8, 4.2))
t = q3.iloc[::-1]
ax.barh(t[c.C_PAY], t["jumlah"], color=BLUE)
for i, v in enumerate(t["jumlah"]): ax.text(v, i, f" {v:,}".replace(",", "."), va="center", fontsize=7)
ax.set_title(f"Jumlah pesanan menurut metode pembayaran (total {len(df):,})".replace(",", "."))
ax.tick_params(axis="y", labelsize=8)
save(fig, "03_metode_pembayaran.png")

# ---- Q4: pembatalan --------------------------------------------------------
st = df["status_final"].value_counts().rename("jumlah").reset_index()
st.to_csv(c.TABLES / "eda_status.csv", index=False)
bt = df[df["is_batal"] == 1]
pb = bt["pembatal"].value_counts().rename("jumlah").reset_index()
pb.to_csv(c.TABLES / "eda_pembatal.csv", index=False)
bt["alasan_baku"].value_counts().rename("jumlah").reset_index().to_csv(c.TABLES / "eda_alasan_batal.csv", index=False)
bulan = cls.groupby("periode")["is_batal"].agg(n="size", batal="sum")
bulan["pct_batal"] = (bulan.batal / bulan.n * 100).round(2)
bulan.reset_index().to_csv(c.TABLES / "eda_batal_per_bulan.csv", index=False)


def rate(col, min_n=1, drop=None):
    d = cls if drop is None else cls[~cls[col].isin(drop)]
    r = d.groupby(col)["is_batal"].agg(n="size", batal="sum")
    r["pct_batal"] = (r.batal / r.n * 100).round(1)
    return r[r.n >= min_n].sort_values("pct_batal", ascending=False).reset_index()


rate(c.C_PAY).to_csv(c.TABLES / "eda_batal_metode.csv", index=False)
rate("kategori_utama", 100).to_csv(c.TABLES / "eda_batal_kategori.csv", index=False)
rate("kurir", 1, ["Belum ditentukan"]).to_csv(c.TABLES / "eda_batal_kurir.csv", index=False)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
colors = {"Selesai": BLUE, "Batal": RED}
axs[0].bar(st["status_final"], st["jumlah"], color=[colors.get(s, GREY) for s in st["status_final"]])
axs[0].set_yscale("log"); axs[0].set_title("Status pesanan (skala log)"); axs[0].tick_params(axis="x", labelsize=7)
for i, v in enumerate(st["jumlah"]): axs[0].text(i, v, f"{v:,}".replace(",", "."), ha="center", va="bottom", fontsize=7)
axs[1].bar(pb["pembatal"], pb["jumlah"], color=[BLUE, GOLD, RED][:len(pb)])
axs[1].set_title(f"Siapa yang membatalkan? ({len(bt):,} pesanan)".replace(",", "."))
save(fig, "04_status_dan_pembatal.png")

# ---- Q5: ongkir ------------------------------------------------------------
prov = (nb.groupby(c.C_PROV).agg(pesanan_nonbatal=(c.C_ID, "size"),
                                  rata_ongkir_dibayar=(c.C_FEE_PAID, "mean"),
                                  rata_perkiraan_ongkir=(c.C_FEE_EST, "mean"),
                                  pct_ongkir_gratis=("ongkir_gratis", lambda s: s.mean() * 100))
        .round(1).sort_values("pesanan_nonbatal", ascending=False).reset_index())
prov.to_csv(c.TABLES / "eda_ongkir_provinsi.csv", index=False)
top = prov.head(10).iloc[::-1]
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
axs[0].barh(top[c.C_PROV], top["pesanan_nonbatal"], color=BLUE); axs[0].set_title("Pesanan non-batal (10 provinsi teratas)")
y = range(len(top))
axs[1].barh([i + .2 for i in y], top["rata_ongkir_dibayar"], height=.4, color=BLUE, label="Dibayar pembeli")
axs[1].barh([i - .2 for i in y], top["rata_perkiraan_ongkir"], height=.4, color=RED, label="Perkiraan total")
axs[1].set_title("Rata-rata ongkir (Rp)"); axs[1].legend(fontsize=7)
for a in axs: a.tick_params(axis="y", labelsize=7)
save(fig, "05_ongkir_provinsi.png")

nb2 = nb.copy()
nb2["kuartil"] = pd.qcut(nb2[c.C_TOTAL].rank(method="first"), 4, labels=["Q1 (terendah)", "Q2", "Q3", "Q4 (tertinggi)"])
kq = (nb2.groupby("kuartil", observed=True).agg(rata_ongkir_dibayar=(c.C_FEE_PAID, "mean"),
                                                 rata_perkiraan_ongkir=(c.C_FEE_EST, "mean"),
                                                 pct_ongkir_gratis=("ongkir_gratis", lambda s: s.mean() * 100))
      .round(1).reset_index())
kq.to_csv(c.TABLES / "eda_ongkir_kuartil.csv", index=False)
fig, ax = plt.subplots(figsize=(5.5, 3.8))
ax.bar(kq["kuartil"].astype(str), kq["pct_ongkir_gratis"], color=BLUE)
for i, v in enumerate(kq["pct_ongkir_gratis"]): ax.text(i, v, f"{v:.0f}%", ha="center", va="bottom", fontsize=8)
ax.set_ylim(0, 100); ax.set_ylabel("% pesanan ongkir gratis"); ax.set_title("Ongkir gratis menurut kuartil nilai transaksi")
ax.tick_params(axis="x", labelsize=7)
save(fig, "06_ongkir_gratis_kuartil.png")

rho = nb[[c.C_WEIGHT, c.C_FEE_EST]].corr(method="spearman").iloc[0, 1]
pd.DataFrame([("Spearman berat vs perkiraan ongkir", round(rho, 3)),
              ("% non-batal ongkir gratis", round(nb["ongkir_gratis"].mean() * 100, 1)),
              ("% perkiraan = dibayar + potongan",
               round((nb[c.C_FEE_EST] == nb[c.C_FEE_PAID] + nb[c.C_FEE_DISC]).mean() * 100, 2))],
             columns=["metrik", "nilai"]).to_csv(c.TABLES / "eda_ongkir_ringkas.csv", index=False)

# ---- Distribusi & outlier --------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
v = nb[nb[c.C_TOTAL] > 0][c.C_TOTAL]
axs[0].hist(v, bins=60, color=BLUE); axs[0].set_yscale("log")
axs[0].set_title("Total Pembayaran (non-batal, > 0; sumbu y log)"); axs[0].set_xlabel("Rupiah")
axs[1].hist(nb[c.C_FEE_EST], bins=60, color=GOLD); axs[1].set_yscale("log")
axs[1].set_title("Perkiraan ongkir (non-batal; sumbu y log)"); axs[1].set_xlabel("Rupiah")
save(fig, "07_histogram.png")
fig, axs = plt.subplots(1, 4, figsize=(11, 3.6))
for a, col in zip(axs, [c.C_QTY, c.C_WEIGHT, c.C_TOTAL, c.C_FEE_EST]):
    a.boxplot(nb[col].dropna(), showfliers=True, flierprops={"markersize": 2}); a.set_yscale("symlog")
    a.set_title(col, fontsize=8); a.set_xticks([])
save(fig, "08_boxplot.png")

# ---- Kebocoran: ringkas ----------------------------------------------------
leak = []
for col in [c.C_TOTAL, c.C_FEE_PAID, c.C_FEE_DISC, c.C_FEE_EST, c.C_DISC]:
    leak.append({"fitur": col, "pct_nol_batal": round((bt[col] == 0).mean() * 100, 1),
                 "pct_nol_nonbatal": round((nb[col] == 0).mean() * 100, 1)})
leak.append({"fitur": "Opsi pengiriman tanpa kurir",
             "pct_nol_batal": round((bt["kurir"] == "Belum ditentukan").mean() * 100, 1),
             "pct_nol_nonbatal": round((nb["kurir"] == "Belum ditentukan").mean() * 100, 1)})
pd.DataFrame(leak).to_csv(c.TABLES / "eda_kebocoran.csv", index=False)

base = (cls["is_batal"] == 0).mean() * 100
print(f"Pesanan Selesai/Batal: {len(cls)}; batal = {cls.is_batal.mean()*100:.2f}%; baseline akurasi = {base:.2f}%")
print("EDA selesai. Tabel: tables/eda_*.csv, grafik: figures/01-08")
