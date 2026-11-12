"""Konfigurasi bersama untuk semua skrip. Jalankan skrip dari folder src/."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
MONTHLY_DIR = RAW_DIR / "monthly_clean"
PROC_DIR = ROOT / "data" / "processed"
TABLES = ROOT / "tables"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"

RAW_CSV = RAW_DIR / "all_months_clean.csv"
CLEAN_CSV = PROC_DIR / "ecom_clean.csv"

# Pengaturan baca CSV (sesuai laporan: titik-koma, UTF-8 dengan BOM)
CSV_KW = dict(sep=";", encoding="utf-8-sig")

DATASET_NAME = "Indonesia E-Commerce Sales & Shipping 2023-2025 (BakiTacos, Kaggle)"
DATASET_URL = ("https://www.kaggle.com/datasets/bakitacos/"
               "indonesia-e-commerce-sales-and-shipping-20232025")
LICENSE = "CC BY-SA 4.0"
VERSION = "CLEAN version (Kaggle tidak mencantumkan nomor versi)"
ACCESS_DATE = "2026-09-06"   # GANTI bila tanggal unduh sebenarnya berbeda
PARAMETER = "Unduh manual (archive.zip), tanpa filter"

# Nama kolom
C_ID = "order_id"
C_QTY = "total_qty"
C_WEIGHT = "total_weight_gr"
C_RET = "total_returned_qty"
C_DISC = "Total Diskon"
C_CATS = "product_categories"
C_NCATS = "num_product_categories"
C_STATUS = "Status Pesanan"
C_REASON = "Alasan Pembatalan"
C_SHIP = "Opsi Pengiriman"
C_PAY = "Metode Pembayaran"
C_CITY = "Kota/Kabupaten"
C_PROV = "Provinsi"
C_FEE_PAID = "Ongkos Kirim Dibayar oleh Pembeli"
C_FEE_DISC = "Estimasi Potongan Biaya Pengiriman"
C_TOTAL = "Total Pembayaran"
C_FEE_EST = "Perkiraan Ongkos Kirim"
C_TIME = "Waktu Pesanan Dibuat"
C_SRC = "source_file"

NUM_COLS = [C_QTY, C_WEIGHT, C_RET, C_DISC, C_NCATS,
            C_FEE_PAID, C_FEE_DISC, C_TOTAL, C_FEE_EST]

MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}


def parse_periode(name):
    """'DecemberSales2024.xlsx' -> '2024-12'. None jika tidak terbaca."""
    stem = Path(str(name)).stem.lower()
    m = re.search("(" + "|".join(MONTHS) + r")\D*?(\d{4})", stem)
    if not m:
        return None
    return f"{m.group(2)}-{MONTHS[m.group(1)]:02d}"


def ensure_dirs():
    for d in (RAW_DIR, MONTHLY_DIR, PROC_DIR, TABLES, FIGURES, DOCS):
        d.mkdir(parents=True, exist_ok=True)


def load_raw():
    import pandas as pd
    return pd.read_csv(RAW_CSV, **CSV_KW)
