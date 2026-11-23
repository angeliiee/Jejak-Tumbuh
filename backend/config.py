"""
Konfigurasi Aplikasi Posyandu Digital (Jejak Tumbuh)
Menyimpan path direktori, konstanta tema pastel pink cerah, menu navigasi, dan konfigurasi lingkungan.
"""
from pathlib import Path
from datetime import date

# Direktori Utama
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
ASSETS_DIR = ROOT_DIR / "frontend" / "assets"
LOGO_PATH = ASSETS_DIR / "JEJAK_TUMBUH.jpeg"
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "Posyandu Digital"
APP_SUBTITLE = "Jejak Tumbuh"
APP_VERSION = "v4.0 (Modular & Pastel Edition)"
APP_ICON = "🌸"

TODAY = date.today()
BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# PALET WARNA CREAM MOCHA
THEME = {
    "primary": "#A68A76",
    "primary_hover": "#8C715E",
    "primary_light": "#E8DCCB",
    "primary_dark": "#46372E",
    "bg_main": "#F5EFE6",
    "bg_card": "#FFFFFF",            # Card background
    "bg_secondary": "#E8DCCB",
    "bg_peach": "#C8B6A6",
    "accent_peach": "#FB923C",       # Peach accent
    "accent_green": "#10B981",       # Status normal / rujukan WHO median
    "accent_amber": "#F59E0B",       # Perlu pemantauan / gizi kurang
    "accent_red": "#EF4444",         # Stunting / risiko tinggi
    "accent_lavender": "#C084FC",    # Risiko gizi lebih / aksen
    "accent_sky": "#38BDF8",         # Info / aksen anak laki-laki
    "text_main": "#46372E",
    "text_muted": "#6E5B50",
    "text_light": "#968375",
    "border_light": "rgba(166, 138, 118, 0.28)",
    "border_glow": "rgba(166, 138, 118, 0.50)",
    "shadow_soft": "0 8px 24px rgba(70, 55, 46, 0.08)",
    "shadow_hover": "0 14px 32px rgba(70, 55, 46, 0.14)",
}

CHART_PALETTE = [
    THEME["primary"],
    THEME["accent_green"],
    THEME["accent_peach"],
    THEME["accent_lavender"],
    THEME["accent_sky"],
    THEME["accent_red"],
    "#46372E",
    "#14B8A6"
]

FONT_FAMILY = "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"

MENU = {
    "Kader": [
        "🏠 Dashboard Posyandu",
        "👥 Data Peserta & Riwayat",
        "🧒 Pemeriksaan Balita",
        "🤰 Pemeriksaan Ibu Hamil",
        "📊 Laporan Visualisasi Dinamis",
        "🗂️ Riwayat Laporan Puskesmas",
        "📚 Pusat Edukasi Posyandu"
    ],
    "Ibu Hamil": [
        "🏠 Dashboard Kehamilan",
        "📖 Buku KIA Digital",
        "👤 Profil & Biodata Ibu",
        "📚 Pusat Edukasi Posyandu"
    ],
    "Orang Tua Balita": [
        "🏠 Dashboard Tumbuh Kembang",
        "📈 Grafik Z-Score & KMS",
        "👶 Data & Tambah Balita",
        "📚 Pusat Edukasi Posyandu"
    ]
}
