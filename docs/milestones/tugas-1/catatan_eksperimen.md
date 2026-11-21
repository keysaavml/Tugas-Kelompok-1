# Catatan Eksperimen dan Keputusan Model – Tugas 3 (Kelompok 5)

| Item | Keterangan |
|---|---|
| Versi data | `data/processed/ecom_clean.csv` (20.848 baris, 35 kolom), diturunkan dari `all_months_clean.csv` (SHA-256 `da9594dd8444c342…`, 3.865.251 byte) pada Tugas 2 |
| Data dipakai | 20.598 pesanan (`dipakai_klasifikasi == True`, berstatus Selesai atau Batal); 250 pesanan masih dalam pengiriman/pengembalian tidak diikutkan |
| Unit evaluasi | Satu baris = satu pesanan (`order_id`) |
| Target | `is_batal` (1 = Batal: 2.830 pesanan atau 13,74%; 0 = Selesai: 17.768 pesanan atau 86,26%) |
| Random seed | 42 |
| Fold | 5-fold stratified cross-validation pada data latih (seed 42), hanya pemeriksaan kestabilan pendukung |
| Split | Temporal: latih Des 2023–Mar 2025 (13.415), validasi Apr–Jul 2025 (3.024), uji Agu–Nov 2025 (4.159) |
| Baseline | Kelas mayoritas (menebak semua Selesai) |
| Model pembanding | Logistic Regression, class_weight balanced |
| Model utama | Random Forest: `n_estimators=300`, `max_depth=12`, `min_samples_leaf=10`, `class_weight="balanced_subsample"`, `random_state=42` |
| Fitur | 16 fitur dasar pra-pemenuhan (berat, ongkir, rasio, diskon, tier kirim, metode bayar/COD, kategori produk, provinsi, penanda Jawa, bulan) |
| Fitur dikeluarkan (anti-leakage) | Total Pembayaran, Ongkos Kirim Dibayar oleh Pembeli, Estimasi Potongan Biaya Pengiriman, total_returned_qty, Alasan Pembatalan, label kurir "Belum ditentukan" |
| Ambang keputusan | Awal 0,50, disesuaikan menjadi 0,53 berdasarkan F1 pada data validasi, lalu dikunci untuk data uji |
| Metrik utama | PR-AUC, ROC-AUC, F1 kelas Batal (accuracy hanya pelengkap) |
| Keputusan model | Random Forest dipilih karena PR-AUC tertinggi pada validasi (0,298 vs 0,254 Logistic Regression) dan uji (0,213 vs 0,174) |
| Penggunaan data uji | Data uji tidak dipakai untuk memilih model maupun ambang |
| Lingkungan | Python, scikit-learn; lihat `requirements.txt` |

## Hasil ringkas (data uji, n = 4.159)
| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| Baseline | 90,00% | 0,000 | 0,000 | 0,000 | 0,500 | 0,100 |
| Logistic Regression | 65,14% | 0,152 | 0,548 | 0,238 | 0,639 | 0,174 |
| Random Forest (0,53) | 75,45% | 0,198 | 0,478 | 0,280 | 0,679 | 0,213 |

Confusion matrix Random Forest (0,53): TN 2.939, FP 804, FN 217, TP 199.

## Recall per segmen (data uji, batas 0,53)
Luar Pulau Jawa 54,2%; Pulau Jawa 45,1%; COD 52,6%; non-COD 41,3%; seluruh data uji 47,8%.

## Catatan
- Proporsi batal berubah antarperiode: 14,26% latih, 16,57% validasi, 10,00% uji. Hal ini menurunkan precision pada data uji.
- Importance fitur adalah ukuran bawaan Random Forest dan menunjukkan pola prediktif, bukan sebab-akibat. Permutation importance belum dihitung.

Release: https://github.com/keysaavml/Tugas-Kelompok-1/releases/tag/tugas-3
