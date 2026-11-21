# Draf Bagian "Metode Analitik dan Hasil" untuk Artikel – Kelompok 5

## Metode Analitik
Pemodelan dilakukan dengan klasifikasi biner untuk memprediksi pembatalan pesanan (Batal atau Selesai) pada 20.598 transaksi yang memiliki status akhir pasti. Untuk mencegah kebocoran data pasca-transaksi (Kaufman dkk., 2012), enam variabel yang nilainya baru terbentuk setelah pesanan berakhir dikeluarkan dari fitur, yaitu total pembayaran, ongkos kirim yang dibayar pembeli, potongan ongkos kirim, jumlah barang yang dikembalikan, alasan pembatalan, dan label pengiriman tanpa kurir.

Sebanyak 16 fitur pra-pemenuhan disusun, meliputi transformasi logaritmik berat paket dan perkiraan ongkos kirim, rasio berat per barang, tarif ongkir per kilogram, penggunaan diskon, tingkat layanan pengiriman, metode pembayaran, kategori produk utama, provinsi tujuan, dan bulan transaksi. Data dibagi secara kronologis menjadi data latih (Desember 2023–Maret 2025; n = 13.415), data validasi (April–Juli 2025; n = 3.024), dan data uji (Agustus–November 2025; n = 4.159). Algoritme Random Forest (Breiman, 2001; 300 pohon, kedalaman maksimum 12, pembobotan kelas balanced_subsample, random_state = 42) dibandingkan dengan baseline kelas mayoritas dan Logistic Regression, dengan penyesuaian ambang keputusan pada data validasi (0,53).

## Hasil
Pada data uji kronologis, Random Forest memperoleh PR-AUC 0,213 (baseline 0,100) dan ROC-AUC 0,679, lebih tinggi daripada Logistic Regression (PR-AUC 0,174; ROC-AUC 0,639). Pada ambang 0,53, model memperoleh F1 0,280 dengan recall 47,84%, precision 19,84%, dan accuracy 75,45%. Perkiraan ongkos kirim, tarif ongkir per kilogram, berat paket, metode pembayaran, dan kategori produk merupakan fitur yang paling banyak dipakai model, tanpa implikasi sebab-akibat. Recall lebih tinggi pada pengiriman ke luar Pulau Jawa (54,2%) dan pembayaran COD (52,6%), sedangkan kesalahan prediksi yang tersisa diduga berkaitan dengan pembatalan oleh pembeli setelah pesanan dibuat, yang tidak tercatat pada fitur.

## Referensi
- Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.
- Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. ACM Transactions on Knowledge Discovery from Data, 6(4), Article 15.
