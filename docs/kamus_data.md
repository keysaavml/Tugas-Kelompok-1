# Kamus Data

- Kunci: `order_id`
- Grain: 1 baris = 1 pesanan
- Target: `Status Pesanan` (Batal vs Selesai)
- *Satuan Rupiah adalah asumsi (dataset tidak menyebut mata uang).

| variabel | arti | tipe | satuan | peran | tipe_pandas | pct_kosong | n_unik |
|---|---|---|---|---|---|---|---|
| order_id | ID pesanan (anonim) | teks | - | Kunci | str | 0.0 | 20848 |
| total_qty | Jumlah barang dalam pesanan | angka | unit | Fitur | int64 | 0.0 | 59 |
| total_weight_gr | Berat total pesanan | angka | gram | Fitur | int64 | 0.0 | 632 |
| total_returned_qty | Jumlah barang dikembalikan | angka | unit | Waspada bocor | int64 | 0.0 | 10 |
| Total Diskon | Total potongan harga | angka | Rupiah* | Fitur | int64 | 0.0 | 49 |
| product_categories | Kategori produk (dipisah koma) | teks | - | Fitur | str | 0.0 | 679 |
| num_product_categories | Banyak kategori dalam satu pesanan | angka | jumlah | Fitur | int64 | 0.0 | 10 |
| Status Pesanan | Status akhir pesanan | kategori | - | TARGET | str | 0.0 | 11 |
| Alasan Pembatalan | Alasan batal (kosong bila tidak batal) | kategori | - | Jangan dipakai (bocor) | str | 86.43 | 18 |
| Opsi Pengiriman | Layanan kirim | kategori | - | Fitur (waspada) | str | 0.0 | 45 |
| Metode Pembayaran | Cara pembeli membayar | kategori | - | Fitur | str | 0.0 | 12 |
| Kota/Kabupaten | Kota/kabupaten tujuan | kategori | - | Fitur | str | 0.0 | 424 |
| Provinsi | Provinsi tujuan | kategori | - | Fitur | str | 0.0 | 34 |
| Ongkos Kirim Dibayar oleh Pembeli | Ongkir yang ditanggung pembeli | angka | Rupiah* | Waspada bocor | int64 | 0.0 | 500 |
| Estimasi Potongan Biaya Pengiriman | Subsidi/potongan ongkir | angka | Rupiah* | Waspada bocor | int64 | 0.0 | 333 |
| Total Pembayaran | Total yang dibayar pembeli | angka | Rupiah* | Waspada bocor | int64 | 0.0 | 5809 |
| Perkiraan Ongkos Kirim | Perkiraan biaya kirim sebenarnya | angka | Rupiah* | Fitur | int64 | 0.0 | 693 |
| Waktu Pesanan Dibuat | Tanggal dan jam pesanan dibuat | waktu | - | Fitur waktu | str | 9.5 | 18591 |
| source_file | Nama file bulanan asal | teks | - | Metadata | str | 0.0 | 24 |
