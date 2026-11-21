# Prediksi Pembatalan Pesanan E-Commerce Indonesia 2023–2025

Tugas Kelompok 3 – Pengantar Big Data (Kelompok 5, Kelas 5C)
Program Studi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Singaperbangsa Karawang
Dosen pengampu: Nono Heryana, S.Kom., M.Kom.

## Anggota dan kontribusi
| Nama | NIM | Kontribusi |
|---|---|---|
| Keysa Avmalia | 2410631250013 | Pemodelan (feature engineering, baseline, Random Forest, random seed) dan pengelolaan GitHub release tugas-3 |
| Zahwa Lamini Arsyi Anjuni | 2410631250114 | Evaluasi temporal, error analysis per segmen, penilaian risiko, revisi Tugas 1 dan 2, draf artikel |

## Ringkasan
Model klasifikasi untuk memprediksi apakah pesanan berakhir Batal (1) atau Selesai (0) pada 20.598 pesanan berstatus akhir pasti.
Data dibagi menurut waktu: latih (Des 2023–Mar 2025), validasi (Apr–Jul 2025), uji (Agu–Nov 2025).

Hasil pada data uji (n = 4.159):
| Model | PR-AUC | ROC-AUC |
|---|---|---|
| Baseline (tebak Selesai) | 0,100 | 0,500 |
| Logistic Regression | 0,174 | 0,639 |
| Random Forest (batas 0,53) | 0,213 | 0,679 |

Random Forest pada ambang 0,53: precision 19,8%, recall 47,8%, F1 0,280.
Feature importance dan hasil per segmen adalah pola prediktif, bukan sebab-akibat.

## Cara menjalankan
```bash
pip install -r requirements.txt
python src/06_modeling.py
python src/07_evaluasi_risiko.py
python src/08_stabilitas_segmen.py
```
Input: `data/processed/ecom_clean.csv`. Random seed: 42.

## Struktur folder
```
src/                         kode feature engineering, model, evaluasi
tables/                      tabel metrik, prediksi, error analysis
figures/                     grafik hasil
data/processed/              data bersih dari Tugas 2
docs/milestones/tugas-1/     revisi Tugas 1
docs/milestones/tugas-2/     revisi Tugas 2
docs/milestones/tugas-3/     laporan, catatan eksperimen, penilaian risiko, draf artikel
```

## Dokumen Tugas 3
- `docs/milestones/tugas-3/catatan_eksperimen.md`
- `docs/milestones/tugas-3/penilaian_risiko.md`
- `docs/milestones/tugas-3/draf_metode_dan_hasil.md`

## Release
Tag `tugas-3`: https://github.com/keysaavml/Tugas-Kelompok-1/releases/tag/tugas-3

## Sumber data
BakiTacos. (2025). Indonesia E-Commerce Sales & Shipping 2023–2025. Kaggle.
https://www.kaggle.com/datasets/bakitacos/indonesia-e-commerce-sales-and-shipping-20232025
