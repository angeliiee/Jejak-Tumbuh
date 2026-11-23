"""
Koneksi Database Supabase untuk Posyandu Digital
Mendukung koneksi langsung ke Supabase (PostgreSQL) serta fallback otomatis
ke penyimpanan lokal jika kredensial belum dikonfigurasikan atau dalam mode offline.
"""
import os
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from dotenv import load_dotenv

# Muat environment variables dari .env (di direktori aplikasi maupun root project)
APP_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = APP_DIR.parent
load_dotenv(APP_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")

_supabase_client = None
_connection_checked = False
_connection_status = "uninitialized"
_connection_error = None


def get_credentials() -> Tuple[str, str]:
    """Mengambil SUPABASE_URL dan SUPABASE_KEY dari st.secrets, .env, atau os.environ."""
    url = ""
    key = ""

    # Coba dari streamlit secrets jika modul streamlit aktif
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "SUPABASE_URL" in st.secrets:
                url = st.secrets["SUPABASE_URL"]
            elif "supabase" in st.secrets and "url" in st.secrets["supabase"]:
                url = st.secrets["supabase"]["url"]

            if "SUPABASE_KEY" in st.secrets:
                key = st.secrets["SUPABASE_KEY"]
            elif "supabase" in st.secrets and "key" in st.secrets["supabase"]:
                key = st.secrets["supabase"]["key"]
    except Exception:
        pass

    # Fallback ke environment variables
    if not url:
        url = os.environ.get("SUPABASE_URL", "").strip()
    if not key:
        key = os.environ.get("SUPABASE_KEY", "").strip()

    # Coba baca langsung dari secrets.toml jika belum ditemukan
    if not url or not key:
        secrets_file = APP_DIR / ".streamlit" / "secrets.toml"
        if secrets_file.exists():
            try:
                for line in secrets_file.read_text(encoding="utf-8").splitlines():
                    if "SUPABASE_URL" in line and "=" in line:
                        url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    elif "SUPABASE_KEY" in line and "=" in line:
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass

    return url, key


def get_supabase_client():
    """Mengembalikan instance Supabase Client jika kredensial valid dan terkoneksi."""
    global _supabase_client, _connection_checked, _connection_status, _connection_error

    if _connection_checked and _supabase_client is not None:
        return _supabase_client

    url, key = get_credentials()

    # Validasi placeholder default
    if not url or not key or "your-project" in url or "your-publishable-key" in key:
        _connection_status = "offline_local"
        _connection_checked = True
        return None

    # Tes konektivitas soket cepat (2 detik) agar tidak blocking saat offline
    import socket
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        if host:
            sock = socket.create_connection((host, 443), timeout=2.0)
            sock.close()
    except Exception:
        _connection_status = "offline_local"
        _connection_checked = True
        return None

    try:
        from supabase import create_client, Client
        client: Client = create_client(url, key)
        # Verifikasi koneksi dengan query ringan
        try:
            client.table("users").select("count", count="exact").limit(1).execute()
            _supabase_client = client
            _connection_status = "connected"
            _connection_error = None
        except Exception as query_err:
            # Jika tabel belum ada atau auth gagal
            err_msg = str(query_err)
            err_lower = err_msg.lower()
            if (
                ("relation" in err_lower and "does not exist" in err_lower)
                or "pgrst205" in err_lower
                or "could not find the table" in err_lower
            ):
                # API dapat dijangkau, tetapi tabel belum ada/terekspos di schema cache.
                _supabase_client = client
                _connection_status = "table_migration_needed"
                _connection_error = err_msg
            else:
                _connection_status = "connection_failed"
                _connection_error = err_msg
                _supabase_client = None
    except Exception as e:
        _connection_status = "error"
        _connection_error = str(e)
        _supabase_client = None

    _connection_checked = True
    return _supabase_client


def is_connected() -> bool:
    """Mengecek apakah Supabase aktif terkoneksi."""
    client = get_supabase_client()
    return client is not None and _connection_status in ("connected", "table_migration_needed")


def get_db_status() -> dict:
    """Mengembalikan status koneksi database untuk ditampilkan di UI."""
    get_supabase_client()
    url, _ = get_credentials()
    if _connection_status == "connected":
        mode_label = "🟢 Supabase (PostgreSQL)"
    elif _connection_status == "table_migration_needed":
        mode_label = "🟠 Supabase terjangkau; tabel belum tersedia di Data API"
    else:
        mode_label = "🟡 Penyimpanan Lokal Terpadu (CSV/SQLite)"
    masked_url = url[:18] + "..." if len(url) > 18 else (url or "Belum diatur")
    return {
        "status": _connection_status,
        "is_supabase": is_connected(),
        "url": masked_url,
        "error": _connection_error,
        "mode_label": mode_label
    }



# Folder data awal yang ikut di repository GitHub
SEED_DATA_DIR = APP_DIR / "data"

# Folder penyimpanan sementara di Vercel
if os.environ.get("VERCEL"):
    DATA_DIR = Path("/tmp/jejak_tumbuh_data")
else:
    DATA_DIR = SEED_DATA_DIR

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Daftar file CSV
CSV_FILES = {
    "users": "users.csv",
    "peserta": "peserta.csv",
    "pemeriksaan_balita": "pemeriksaan_balita.csv",
    "pemeriksaan_ibu_hamil": "pemeriksaan_ibu_hamil.csv",
    "laporan": "laporan.csv",
    "orang_tua": "orang_tua.csv",
}


def load_local_csv(table_name: str) -> pd.DataFrame:
    """Membaca data sementara terlebih dahulu, lalu data awal dari repository."""
    filename = CSV_FILES.get(table_name)

    if not filename:
        return pd.DataFrame()

    # Prioritaskan data yang sudah tersimpan di folder sementara
    path = DATA_DIR / filename

    # Jika belum ada, baca CSV bawaan dari repository
    if not path.exists():
        path = SEED_DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, dtype=str)

        for num_col in [
            "berat_kg", "tinggi_cm", "lingkar_kepala_cm",
            "z_bb_u", "z_tb_u", "usia_bulan", "usia_ibu_tahun",
            "usia_kehamilan_minggu", "lila_cm", "sistol",
            "diastol", "hb_gdl", "tfu_cm", "djj_bpm"
        ]:
            if num_col in df.columns:
                df[num_col] = pd.to_numeric(
                    df[num_col], errors="coerce"
                )

        return df

    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        return pd.DataFrame()


def save_local_csv(table_name: str, df: pd.DataFrame) -> bool:
    """Menyimpan data ke folder lokal atau sementara."""
    filename = CSV_FILES.get(table_name)

    if not filename:
        return False

    try:
        path = DATA_DIR / filename
        df.to_csv(path, index=False)
        return True

    except Exception as e:
        print(f"Error saving to {table_name}: {e}")
        return False

