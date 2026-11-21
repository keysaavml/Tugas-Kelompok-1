# Penilaian Risiko dan Keterbatasan – Tugas 3 (Kelompok 5)

## Penilaian risiko
| Aspek | Temuan pada data dan model | Pihak terdampak | Langkah pencegahan | Sisa risiko |
|---|---|---|---|---|
| Privasi | Tidak ada nama atau alamat pembeli, tetapi gabungan tanggal, kota kecil, dan kategori produk dapat dikenali bila digabung dengan data lain | Pembeli dan penjual di kota kecil | Hanya memakai bulan (bukan jam), tidak digabung dengan data luar, dilaporkan dalam bentuk ringkasan | Rendah |
| Bias wilayah | 75,7% pesanan berasal dari Pulau Jawa; data Indonesia Timur sangat sedikit | Pembeli dan penjual di luar Pulau Jawa | Kota/kabupaten tidak dipakai sebagai fitur; performa dicek terpisah untuk Jawa dan luar Jawa | Sedang |
| Sampel kecil | Indomaret (43) dan Alfamart (36) batal sekitar 48%, tetapi kurang dari 0,4% transaksi | Pembeli yang membayar tunai lewat minimarket | `min_samples_leaf=10` agar model tidak membentuk aturan ekstrem dari sampel kecil | Rendah–Sedang |
| Fairness dan penyalahgunaan | Jika skor dipakai langsung untuk memblokir COD, sekitar 21,5% pembeli sah (804 dari 3.743 pesanan Selesai pada data uji) ikut ditolak. FPR per segmen dilaporkan di `tables/model_fpr_segmen.csv` | Pembeli sah dan penjual yang kehilangan pesanan | Skor hanya dipakai sebagai pengingat konfirmasi alamat atau pesan kepada pembeli, bukan menolak pesanan otomatis | Sedang |
| Keamanan dan reproduksi | Berkas mentah dapat berubah atau hasil berbeda saat skrip dijalankan ulang | Peneliti dan dosen penguji | Pengecekan SHA-256 berkas mentah, `random_state=42`, kode lengkap di GitHub | Sangat rendah |
| Pergeseran data (drift) | Proporsi batal berubah (14,26% latih, 16,57% validasi, 10,00% uji); precision turun dari 0,304 ke 0,198, sehingga ambang 0,53 dapat tidak sesuai bila pola berubah | Penjual dan operator platform | Pantau PR-AUC dan proporsi batal tiap bulan, tinjau ulang ambang pada data terbaru, latih ulang model berkala | Sedang |

## Keterbatasan
- Data berasal dari satu platform dan satu periode 24 bulan sehingga belum tentu berlaku untuk e-commerce Indonesia secara umum.
- Identitas pembeli tidak tersedia, sehingga tidak dapat dipastikan pembeli yang sama tidak muncul pada data latih dan data uji.
- Alasan utama pembatalan (perubahan niat pembeli) tidak tercatat saat checkout, sehingga batas kemampuan prediksi dari fitur yang ada rendah.
- Pembatalan oleh pembeli, sistem, dan penjual digabung dalam satu label.
- Ambang 0,53 dipilih pada data validasi (proporsi batal 16,57%) yang berbeda dari data uji (10,00%), sehingga precision pada penggunaan nyata dapat berubah.
- FPR per segmen belum diuji signifikansinya dan jumlah pesanan pada beberapa segmen kecil, sehingga belum cukup untuk menyimpulkan ada atau tidaknya perlakuan tidak adil.
- Importance fitur dan hasil per segmen adalah pola prediktif, tidak boleh ditafsirkan sebagai sebab-akibat.
- Cross-validation 5-fold bersifat acak dan tidak memperhitungkan urutan waktu; kesimpulan utama bertumpu pada split temporal dan metrik per bulan.
- Fitur bulan (1–12) dipakai bersama split temporal: bulan Agustus–November pada data uji hanya pernah dilihat model pada 2024 dan tidak ada fitur tahun, sehingga pola musiman dan tren belum dapat dipisahkan.
- Importance memakai ukuran bawaan Random Forest yang dapat condong ke fitur kontinu (Strobl dkk., 2007); permutation importance belum dihitung.
- Hanya satu algoritme pohon dan satu pembanding linear yang dibandingkan; gradient boosting dan kalibrasi probabilitas belum diuji.
