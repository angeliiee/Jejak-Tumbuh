"""
====================================================================
JEJAK TUMBUH — POSYANDU DIGITAL (v5.0 PRO)
Full-Stack Flask Web Application — Cream Mocha Modern Minimalist
Referensi Desain: AutoEDA (https://github.com/cahayasemidang-max/AutoEDA)
Integrated with WHO Anthropometry Z-Score & Kemenkes RI Maternal Screening
====================================================================
"""
import os
import sys
import calendar as calendar_module
from datetime import date, datetime
from functools import wraps
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, send_file
)

# Menambahkan direktori root aplikasi ke sys.path
APP_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = APP_DIR / "frontend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import database
import gizi
from export_utils import generate_excel_report, generate_pdf_report
from frontend.components.posyandu_animation import get_posyandu_animation_svg

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "posyandu-digital-jejak-tumbuh-secret-2026")
app.config["TEMPLATES_AUTO_RELOAD"] = True

BULAN_INDONESIA = [
    (1, "Januari"), (2, "Februari"), (3, "Maret"), (4, "April"),
    (5, "Mei"), (6, "Juni"), (7, "Juli"), (8, "Agustus"),
    (9, "September"), (10, "Oktober"), (11, "November"), (12, "Desember")
]


# ====================================================================
# AUTHENTICATION HELPERS & DECORATORS
# ====================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan masuk terlebih dahulu untuk mengakses halaman ini.", "danger")
            return redirect(url_for("landing"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles: List[str]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Silakan masuk terlebih dahulu.", "danger")
                return redirect(url_for("landing"))
            role = session.get("user_role")
            if role not in allowed_roles:
                flash(f"Akses ditolak. Halaman ini khusus untuk {', '.join(allowed_roles)}.", "danger")
                if role == "Kader":
                    return redirect(url_for("kader_dashboard"))
                elif role == "Orang Tua Balita":
                    return redirect(url_for("ortu_dashboard"))
                elif role == "Ibu Hamil":
                    return redirect(url_for("ibu_dashboard"))
                return redirect(url_for("landing"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.context_processor
def inject_global_vars():
    """Menyediakan variabel global ke seluruh template Jinja."""
    today = date.today()
    bulan_dict = dict(BULAN_INDONESIA)
    today_str = f"{today.day} {bulan_dict.get(today.month, '')} {today.year}"
    return {
        "today_str": today_str,
        "today_iso": today.isoformat(),
        "bulan_options": BULAN_INDONESIA,
        "tahun_options": [2024, 2025, 2026, 2027]
    }


# ====================================================================
# 1. LANDING PAGE & AUTENTIKASI
# ====================================================================
@app.route("/")
@app.route("/landing")
def landing():
    """Halaman Landing Page 3-Tahap & Autentikasi."""
    if "user_id" in session:
        role = session.get("user_role")
        if role == "Kader":
            return redirect(url_for("kader_dashboard"))
        elif role == "Orang Tua Balita":
            return redirect(url_for("ortu_dashboard"))
        elif role == "Ibu Hamil":
            return redirect(url_for("ibu_dashboard"))
    return render_template("landing.html", posyandu_art=get_posyandu_animation_svg(is_dark=False, focus_characters=True))


@app.route("/index")
def index():
    return redirect(url_for("landing"))


@app.route("/login", methods=["POST"])
def login():
    """Proses login pengguna (termasuk 1-klik akun demo dosen)."""
    target = request.form.get("username_or_email", "").strip()
    password = request.form.get("password", "")

    if not target or not password:
        flash("Username/email dan kata sandi wajib diisi.", "danger")
        return redirect(url_for("landing"))

    sukses, pesan, user_prof = database.sign_in_user(target, password)

    if sukses and user_prof:
        session["user_id"] = str(user_prof.get("id") or user_prof.get("username") or target)
        session["user_name"] = user_prof.get("nama") or target
        session["user_role"] = user_prof.get("role") or "Kader"
        session["user_email"] = user_prof.get("email") or ""
        session["id_peserta"] = user_prof.get("id_peserta") or ""

        flash(f"Selamat datang, {session['user_name']}! Berhasil masuk sebagai {session['user_role']}.", "success")

        if session["user_role"] == "Kader":
            return redirect(url_for("kader_dashboard"))
        elif session["user_role"] == "Orang Tua Balita":
            return redirect(url_for("ortu_dashboard"))
        elif session["user_role"] == "Ibu Hamil":
            return redirect(url_for("ibu_dashboard"))
        return redirect(url_for("landing"))
    else:
        flash(pesan or "Login gagal. Periksa kembali username/email dan kata sandi Anda.", "danger")
        return redirect(url_for("landing"))


@app.route("/register", methods=["POST"])
def register():
    """Proses pendaftaran akun pengguna baru mandiri."""
    role = request.form.get("role", "Orang Tua Balita").strip()
    nama = request.form.get("nama", "").strip()
    email = request.form.get("email", "").strip()
    pw = request.form.get("password", "")
    pw_conf = request.form.get("password_confirm", "")

    # Akun kader tetap dibuat oleh pengelola; pendaftaran mandiri hanya
    # tersedia untuk ibu hamil dan orang tua balita.
    if role not in {"Ibu Hamil", "Orang Tua Balita"}:
        flash("Pendaftaran mandiri hanya tersedia untuk Ibu Hamil dan Orang Tua Balita.", "danger")
        return redirect(url_for("landing"))

    if not nama or not email or not pw:
        flash("Seluruh kolom bertanda bintang wajib diisi.", "danger")
        return redirect(url_for("landing"))

    if pw != pw_conf:
        flash("Konfirmasi kata sandi tidak cocok. Silakan ulangi.", "danger")
        return redirect(url_for("landing"))

    alamat = request.form.get("alamat", "").strip()
    rt = request.form.get("rt", "").strip()
    rw = request.form.get("rw", "").strip()
    dusun = request.form.get("alamat_dusun", "").strip()
    if not alamat or not rt or not rw or not dusun:
        flash("Alamat, RT, RW, dan dusun wajib dilengkapi.", "danger")
        return redirect(url_for("landing"))
    alamat_lengkap = f"{alamat}, RT {rt}, RW {rw}, Dusun {dusun}"

    if role == "Ibu Hamil":
        nama_suami = request.form.get("nama_suami", "").strip()
        try:
            usia_ibu = int(request.form.get("usia_ibu_tahun", ""))
            usia_kehamilan = int(request.form.get("usia_kehamilan_minggu", ""))
        except (TypeError, ValueError):
            flash("Usia ibu dan usia kandungan harus berupa angka.", "danger")
            return redirect(url_for("landing"))
        if not nama_suami or not 10 <= usia_ibu <= 60 or not 1 <= usia_kehamilan <= 45:
            flash("Lengkapi nama pendamping, usia ibu (10–60 tahun), dan usia kandungan (1–45 minggu).", "danger")
            return redirect(url_for("landing"))
        biodata = {
            "nama": nama,
            "nama_suami": nama_suami,
            "usia_ibu_tahun": usia_ibu,
            "usia_kehamilan_minggu": usia_kehamilan,
            "alamat_dusun": dusun,
            "alamat_lengkap": alamat_lengkap,
            "email": email,
        }
    else:
        nama_balita = request.form.get("nama_balita", "").strip()
        tanggal_lahir = request.form.get("tanggal_lahir", "").strip()
        jenis_kelamin = request.form.get("jenis_kelamin", "").strip()
        try:
            tanggal_lahir_obj = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
        except ValueError:
            flash("Tanggal lahir balita tidak valid.", "danger")
            return redirect(url_for("landing"))
        if tanggal_lahir_obj > date.today() or not nama_balita or jenis_kelamin not in {"Laki-laki", "Perempuan"}:
            flash("Lengkapi nama, tanggal lahir, dan jenis kelamin balita dengan benar.", "danger")
            return redirect(url_for("landing"))
        usia_bulan = max(0, (date.today().year - tanggal_lahir_obj.year) * 12 + date.today().month - tanggal_lahir_obj.month
                         + (date.today().day - tanggal_lahir_obj.day) / 30.4375)
        biodata = {
            "nama_orang_tua": nama,
            "nama_balita": nama_balita,
            "tanggal_lahir": tanggal_lahir,
            "usia_bulan": round(usia_bulan, 1),
            "jenis_kelamin": jenis_kelamin,
            "alamat_dusun": dusun,
            "alamat_lengkap": alamat_lengkap,
            "email": email,
        }

    sukses, pesan, new_user = database.sign_up_user(email, pw, role, nama)
    if sukses:
        user_id = (new_user or {}).get("id")
        if not user_id:
            flash("Akun berhasil dibuat, tetapi ID pengguna tidak tersedia untuk menyimpan biodata. Hubungi pengelola.", "danger")
            return redirect(url_for("landing"))
        if role == "Ibu Hamil":
            biodata_ok, biodata_message, _ = database.save_ibu_biodata(user_id, biodata)
        else:
            biodata_ok, biodata_message, _ = database.save_ortu_and_balita_biodata(user_id, biodata)
        if biodata_ok:
            flash(f"Pendaftaran berhasil. {biodata_message} Silakan masuk.", "success")
        else:
            flash(f"Akun berhasil dibuat, tetapi biodata belum tersimpan: {biodata_message}", "danger")
    else:
        flash(pesan or "Gagal melakukan pendaftaran. Silakan coba lagi.", "danger")

    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    """Keluar dari sesi aplikasi."""
    database.sign_out_user()
    session.clear()
    flash("Anda telah berhasil keluar dari sistem.", "success")
    return redirect(url_for("landing"))


# ====================================================================
# 2. DASHBOARD KADER POSYANDU
# ====================================================================
@app.route("/kader/dashboard")
@login_required
@role_required(["Kader"])
def kader_dashboard():
    """Dashboard utama Kader: Metrik ringkasan, grafik interaktif, dan riwayat terkini."""
    # Ambil filter periode dari query parameter (opsional)
    sel_bulan = request.args.get("bulan", "")
    sel_tahun = request.args.get("tahun", "")

    b_df = database.get_pemeriksaan_balita()
    i_df = database.get_pemeriksaan_ibu()
    all_peserta = database.get_all_peserta()

    # Terapkan filter jika ada
    if sel_bulan:
        try:
            b_num = int(sel_bulan)
            if "bulan" in b_df.columns:
                b_df = b_df[b_df["bulan"] == b_num]
            if "bulan" in i_df.columns:
                i_df = i_df[i_df["bulan"] == b_num]
        except Exception:
            pass

    if sel_tahun:
        try:
            yr_num = int(sel_tahun)
            if "tahun" in b_df.columns:
                b_df = b_df[b_df["tahun"] == yr_num]
            if "tahun" in i_df.columns:
                i_df = i_df[i_df["tahun"] == yr_num]
        except Exception:
            pass

    # Hitung metrik agregat
    total_balita = len(all_peserta[all_peserta["jenis_peserta"] == "Balita"]) if not all_peserta.empty else 0
    total_ibu = len(all_peserta[all_peserta["jenis_peserta"] == "Ibu Hamil"]) if not all_peserta.empty else 0

    pem_balita_count = len(b_df)
    stunting_count = len(b_df[b_df["status_gizi"].astype(str).str.contains("Stunting|Sangat", case=False, na=False)]) if not b_df.empty else 0
    ibu_risiko_count = len(i_df[i_df["risiko"] == "Risiko tinggi"]) if not i_df.empty else 0

    metrics = {
        "total_balita": total_balita,
        "total_ibu": total_ibu,
        "pemeriksaan_balita_count": pem_balita_count,
        "balita_stunting_count": stunting_count,
        "ibu_risiko_tinggi_count": ibu_risiko_count
    }

    # Data Chart Status Gizi Balita (WHO)
    chart_gizi_labels = ["Normal", "Gizi Kurang", "Stunting", "Risiko Gizi Lebih"]
    chart_gizi_values = [0, 0, 0, 0]
    if not b_df.empty and "status_gizi" in b_df.columns:
        counts = b_df["status_gizi"].value_counts()
        chart_gizi_values[0] = int(counts.get("Normal", 0))
        chart_gizi_values[1] = int(counts.get("Gizi kurang", 0))
        stunt_sum = int(counts.get("Stunting", 0)) + int(counts.get("Sangat Pendek (Severely Stunted)", 0)) + int(counts.get("Pendek (Stunted)", 0))
        chart_gizi_values[2] = stunt_sum
        chart_gizi_values[3] = int(counts.get("Risiko gizi lebih", 0))

    # Data Chart Risiko Ibu Hamil
    chart_risiko_labels = ["Risiko Rendah", "Perlu Pemantauan", "Risiko Tinggi"]
    chart_risiko_values = [0, 0, 0]
    if not i_df.empty and "risiko" in i_df.columns:
        r_counts = i_df["risiko"].value_counts()
        chart_risiko_values[0] = int(r_counts.get("Risiko rendah", 0))
        chart_risiko_values[1] = int(r_counts.get("Perlu pemantauan", 0))
        chart_risiko_values[2] = int(r_counts.get("Risiko tinggi", 0))

    # Riwayat balita terbaru (10 teratas)
    recent_balita = []
    if not b_df.empty:
        sort_b = b_df.sort_values("tanggal_pemeriksaan", ascending=False).head(10)
        for _, row in sort_b.iterrows():
            tgl_raw = str(row.get("tanggal_pemeriksaan", ""))[:10]
            recent_balita.append({
                "id_peserta": row.get("id_peserta", ""),
                "nama": row.get("nama", ""),
                "tanggal_str": tgl_raw,
                "usia_bulan": row.get("usia_bulan", ""),
                "berat_kg": row.get("berat_kg", ""),
                "tinggi_cm": row.get("tinggi_cm", ""),
                "z_bb_u": row.get("z_bb_u", ""),
                "z_tb_u": row.get("z_tb_u", ""),
                "status_gizi": row.get("status_gizi", "Normal"),
                "alamat_dusun": row.get("alamat_dusun", "")
            })

    return render_template(
        "dashboard_kader.html",
        active_page="dashboard",
        metrics=metrics,
        chart_gizi_labels=chart_gizi_labels,
        chart_gizi_values=chart_gizi_values,
        chart_risiko_labels=chart_risiko_labels,
        chart_risiko_values=chart_risiko_values,
        recent_balita=recent_balita,
        selected_bulan=int(sel_bulan) if sel_bulan.isdigit() else None,
        selected_tahun=int(sel_tahun) if sel_tahun.isdigit() else None
    )


# ====================================================================
# 3. PENCATATAN PEMERIKSAAN BALITA
# ====================================================================
@app.route("/kader/pemeriksaan-balita")
@login_required
@role_required(["Kader"])
def pemeriksaan_balita_view():
    """Halaman pencatatan pemeriksaan balita dan riwayat penimbangan."""
    all_p = database.get_all_peserta()
    balita_options = []
    if not all_p.empty:
        bal_p = all_p[all_p["jenis_peserta"] == "Balita"].sort_values("nama")
        balita_options = bal_p.to_dict(orient="records")

    b_df = database.get_pemeriksaan_balita()
    riwayat_balita = []
    if not b_df.empty:
        sort_b = b_df.sort_values("tanggal_pemeriksaan", ascending=False)
        for _, row in sort_b.iterrows():
            tgl_raw = str(row.get("tanggal_pemeriksaan", ""))[:10]
            riwayat_balita.append({
                "id_peserta": row.get("id_peserta", ""),
                "nama": row.get("nama", ""),
                "tanggal_str": tgl_raw,
                "jenis_kelamin": row.get("jenis_kelamin", ""),
                "usia_bulan": row.get("usia_bulan", ""),
                "berat_kg": row.get("berat_kg", ""),
                "tinggi_cm": row.get("tinggi_cm", ""),
                "z_bb_u": row.get("z_bb_u", ""),
                "z_tb_u": row.get("z_tb_u", ""),
                "status_gizi": row.get("status_gizi", "Normal"),
                "imunisasi": row.get("imunisasi", "-"),
                "vitamin_a": row.get("vitamin_a", "-"),
                "nama_orang_tua": row.get("nama_orang_tua", "")
            })

    return render_template(
        "pemeriksaan_balita.html",
        active_page="pemeriksaan_balita",
        balita_options=balita_options,
        riwayat_balita=riwayat_balita
    )


@app.route("/kader/pemeriksaan-balita/simpan", methods=["POST"])
@login_required
@role_required(["Kader"])
def simpan_pemeriksaan_balita():
    """Menyimpan data pemeriksaan balita baru dan menghitung Z-score WHO."""
    data = {
        "id_peserta": request.form.get("id_peserta", "").strip().upper(),
        "tanggal_pemeriksaan": request.form.get("tanggal_pemeriksaan", str(date.today())),
        "berat_kg": request.form.get("berat_kg", 0),
        "tinggi_cm": request.form.get("tinggi_cm", 0),
        "lingkar_kepala_cm": request.form.get("lingkar_kepala_cm", 0),
        "vitamin_a": request.form.get("vitamin_a", "Tidak"),
        "imunisasi": request.form.get("imunisasi", "Lengkap sesuai usia"),
        "catatan": request.form.get("catatan", "")
    }

    sukses, pesan, record = database.add_pemeriksaan_balita(data)
    if sukses:
        flash(f"Pemeriksaan balita {data['id_peserta']} berhasil disimpan! Status Gizi: {record.get('status_gizi', '-')}.", "success")
    else:
        flash(pesan or "Gagal menyimpan data pemeriksaan balita.", "danger")

    return redirect(url_for("pemeriksaan_balita_view"))


# ====================================================================
# 4. PENCATATAN PEMERIKSAAN IBU HAMIL
# ====================================================================
@app.route("/kader/pemeriksaan-ibu")
@login_required
@role_required(["Kader"])
def pemeriksaan_ibu_view():
    """Halaman pencatatan pemeriksaan ANC ibu hamil dan skrining risiko."""
    all_p = database.get_all_peserta()
    ibu_options = []
    if not all_p.empty:
        ibu_p = all_p[all_p["jenis_peserta"] == "Ibu Hamil"].sort_values("nama")
        ibu_options = ibu_p.to_dict(orient="records")

    i_df = database.get_pemeriksaan_ibu()
    riwayat_ibu = []
    if not i_df.empty:
        sort_i = i_df.sort_values("tanggal_pemeriksaan", ascending=False)
        for _, row in sort_i.iterrows():
            tgl_raw = str(row.get("tanggal_pemeriksaan", ""))[:10]
            riwayat_ibu.append({
                "id_peserta": row.get("id_peserta", ""),
                "nama": row.get("nama", ""),
                "tanggal_str": tgl_raw,
                "usia_kehamilan_minggu": row.get("usia_kehamilan_minggu", ""),
                "berat_kg": row.get("berat_kg", ""),
                "lila_cm": row.get("lila_cm", ""),
                "sistol": row.get("sistol", ""),
                "diastol": row.get("diastol", ""),
                "hb_gdl": row.get("hb_gdl", ""),
                "status_kek": row.get("status_kek", "Normal"),
                "status_anemia": row.get("status_anemia", "Normal"),
                "risiko": row.get("risiko", "Risiko rendah"),
                "tablet_fe": row.get("tablet_fe", "-")
            })

    return render_template(
        "pemeriksaan_ibu.html",
        active_page="pemeriksaan_ibu",
        ibu_options=ibu_options,
        riwayat_ibu=riwayat_ibu
    )


@app.route("/kader/pemeriksaan-ibu/simpan", methods=["POST"])
@login_required
@role_required(["Kader"])
def simpan_pemeriksaan_ibu():
    """Menyimpan data pemeriksaan ibu hamil baru dan skrining risiko."""
    data = {
        "id_peserta": request.form.get("id_peserta", "").strip().upper(),
        "tanggal_pemeriksaan": request.form.get("tanggal_pemeriksaan", str(date.today())),
        "usia_kehamilan_minggu": request.form.get("usia_kehamilan_minggu", 20),
        "berat_kg": request.form.get("berat_kg", 60.0),
        "lila_cm": request.form.get("lila_cm", 25.0),
        "sistol": request.form.get("sistol", 115),
        "diastol": request.form.get("diastol", 75),
        "hb_gdl": request.form.get("hb_gdl", 12.0),
        "tfu_cm": request.form.get("tfu_cm", 20.0),
        "djj_bpm": request.form.get("djj_bpm", 140),
        "tablet_fe": request.form.get("tablet_fe", "Diberikan"),
        "catatan": request.form.get("catatan", "")
    }

    sukses, pesan, record = database.add_pemeriksaan_ibu(data)
    if sukses:
        flash(f"Pemeriksaan ibu {data['id_peserta']} berhasil disimpan! Evaluasi Risiko: {record.get('risiko', '-')}.", "success")
    else:
        flash(pesan or "Gagal menyimpan pemeriksaan ibu hamil.", "danger")

    return redirect(url_for("pemeriksaan_ibu_view"))


# ====================================================================
# 5. DATA PESERTA POSYANDU
# ====================================================================
@app.route("/kader/peserta")
@login_required
@role_required(["Kader"])
def peserta_list():
    """Daftar seluruh peserta posyandu (Balita & Ibu Hamil)."""
    q = request.args.get("q", "")
    jenis = request.args.get("jenis", "Semua")
    df = database.search_peserta(q, jenis)
    peserta_list_data = df.to_dict(orient="records") if not df.empty else []

    return render_template(
        "peserta.html",
        active_page="peserta",
        peserta_list=peserta_list_data
    )


@app.route("/kader/peserta/tambah", methods=["POST"])
@login_required
@role_required(["Kader"])
def tambah_peserta_baru():
    """Pendaftaran peserta baru oleh kader posyandu."""
    jenis = request.form.get("jenis_peserta", "Balita")
    nama = request.form.get("nama", "").strip()
    dusun = request.form.get("alamat_dusun", "Melati")

    prefix = "BLT" if jenis == "Balita" else "IBU"
    new_id = database.generate_next_id(prefix)

    data = {
        "id_peserta": new_id,
        "jenis_peserta": jenis,
        "nama": nama,
        "alamat_dusun": dusun,
        "email": "",
        "status": "Terdaftar",
        "tanggal_daftar": str(date.today())
    }

    if jenis == "Balita":
        data["jenis_kelamin"] = request.form.get("jenis_kelamin", "Laki-laki")
        data["tanggal_lahir"] = request.form.get("tanggal_lahir", str(date.today()))
        data["usia_bulan"] = float(request.form.get("usia_bulan", 0))
        data["nama_orang_tua"] = request.form.get("nama_orang_tua", "")
    else:
        data["jenis_kelamin"] = "Perempuan"
        data["usia_ibu_tahun"] = int(request.form.get("usia_ibu_tahun", 25))
        data["usia_kehamilan_minggu"] = int(request.form.get("usia_kehamilan_minggu", 16))

    sukses, pesan, created_id = database.create_peserta(data)
    if sukses:
        flash(f"Peserta baru {nama} berhasil didaftarkan dengan ID {created_id or new_id}!", "success")
    else:
        flash(pesan or "Gagal menambahkan peserta baru.", "danger")

    return redirect(url_for("peserta_list"))


# ====================================================================
# 6. LAPORAN, REKAPITULASI & EKSPOR DOKUMEN (EXCEL & PDF)
# ====================================================================
def _calculate_rekap_stats(b_df: pd.DataFrame, i_df: pd.DataFrame) -> Dict[str, Any]:
    """Helper kalkulasi ringkasan statistik rekapitulasi Posyandu."""
    tot_bal = len(b_df)
    tot_ibu = len(i_df)

    bal_normal = len(b_df[b_df["status_gizi"].astype(str).str.lower() == "normal"]) if not b_df.empty else 0
    bal_kurang = len(b_df[b_df["status_gizi"].astype(str).str.contains("kurang", case=False, na=False)]) if not b_df.empty else 0
    bal_stunt = len(b_df[b_df["status_gizi"].astype(str).str.contains("stunting|sangat", case=False, na=False)]) if not b_df.empty else 0
    bal_lebih = len(b_df[b_df["status_gizi"].astype(str).str.contains("lebih", case=False, na=False)]) if not b_df.empty else 0

    ibu_kek = len(i_df[i_df["status_kek"] == "KEK"]) if not i_df.empty else 0
    ibu_anemia = len(i_df[i_df["status_anemia"] == "Anemia"]) if not i_df.empty else 0
    ibu_hip = len(i_df[i_df["status_hipertensi"] == "Hipertensi"]) if not i_df.empty else 0
    ibu_risiko = len(i_df[i_df["risiko"] == "Risiko tinggi"]) if not i_df.empty else 0

    def pct(val, tot):
        return round((val / tot * 100), 1) if tot > 0 else 0.0

    return {
        "total_balita_diperiksa": tot_bal,
        "balita_normal": bal_normal,
        "balita_normal_pct": pct(bal_normal, tot_bal),
        "balita_kurang": bal_kurang,
        "balita_kurang_pct": pct(bal_kurang, tot_bal),
        "balita_stunting": bal_stunt,
        "balita_stunting_pct": pct(bal_stunt, tot_bal),
        "balita_lebih": bal_lebih,
        "balita_lebih_pct": pct(bal_lebih, tot_bal),
        "total_ibu_diperiksa": tot_ibu,
        "ibu_kek": ibu_kek,
        "ibu_anemia": ibu_anemia,
        "ibu_hipertensi": ibu_hip,
        "ibu_risiko_tinggi": ibu_risiko
    }


@app.route("/kader/laporan")
@login_required
@role_required(["Kader"])
def laporan_view():
    """Halaman rekapitulasi laporan bulanan dan riwayat penyerahan."""
    sel_bulan = request.args.get("bulan", "")
    sel_tahun = request.args.get("tahun", "")

    b_df = database.get_pemeriksaan_balita()
    i_df = database.get_pemeriksaan_ibu()

    periode_label = "Semua Periode"
    if sel_bulan:
        try:
            b_num = int(sel_bulan)
            b_df = b_df[b_df["bulan"] == b_num] if "bulan" in b_df.columns else b_df
            i_df = i_df[i_df["bulan"] == b_num] if "bulan" in i_df.columns else i_df
            b_dict = dict(BULAN_INDONESIA)
            periode_label = f"{b_dict.get(b_num, '')}"
        except Exception:
            pass

    if sel_tahun:
        try:
            yr_num = int(sel_tahun)
            b_df = b_df[b_df["tahun"] == yr_num] if "tahun" in b_df.columns else b_df
            i_df = i_df[i_df["tahun"] == yr_num] if "tahun" in i_df.columns else i_df
            periode_label = f"{periode_label} {yr_num}".strip()
        except Exception:
            pass

    rekap_stats = _calculate_rekap_stats(b_df, i_df)
    riwayat_lap_df = database.get_all_laporan()
    riwayat_laporan = riwayat_lap_df.to_dict(orient="records") if not riwayat_lap_df.empty else []

    return render_template(
        "laporan.html",
        active_page="laporan",
        rekap=rekap_stats,
        riwayat_laporan=riwayat_laporan,
        selected_bulan=int(sel_bulan) if sel_bulan.isdigit() else None,
        selected_tahun=int(sel_tahun) if sel_tahun.isdigit() else None,
        selected_periode_str=periode_label
    )


@app.route("/kader/laporan/simpan", methods=["POST"])
@login_required
@role_required(["Kader"])
def simpan_arsip_laporan():
    """Menyimpan arsip laporan rekapitulasi ke database."""
    periode = request.form.get("periode", "Periode Berjalan")
    catatan = request.form.get("catatan", "")
    kader = session.get("user_name", "Kader Posyandu")

    sukses, pesan, new_id = database.save_laporan(
        periode=periode,
        kelompok="Balita & Ibu Hamil",
        variabel="Antropometri WHO & Maternal",
        dibuat_oleh=kader,
        catatan=catatan
    )

    if sukses:
        flash(f"Laporan {new_id} periode {periode} berhasil disimpan ke arsip!", "success")
    else:
        flash(pesan or "Gagal mengarsipkan laporan.", "danger")

    return redirect(url_for("laporan_view"))


@app.route("/kader/laporan/serahkan/<id_laporan>", methods=["POST"])
@login_required
@role_required(["Kader"])
def serahkan_laporan_ke_puskesmas(id_laporan):
    """Memperbarui status penyerahan laporan ke Puskesmas."""
    sukses, pesan = database.update_status_laporan(id_laporan, status="Diserahkan ke Puskesmas")
    if sukses:
        flash(f"Laporan {id_laporan} berhasil diserahkan ke Puskesmas!", "success")
    else:
        flash(pesan or "Gagal memperbarui status penyerahan.", "danger")

    return redirect(url_for("laporan_view"))


@app.route("/laporan/ekspor/excel")
@login_required
def ekspor_excel():
    """Ekspor laporan lengkap ke format Excel (.xlsx)."""
    sel_bulan = request.args.get("bulan", "")
    sel_tahun = request.args.get("tahun", "")

    b_df = database.get_pemeriksaan_balita()
    i_df = database.get_pemeriksaan_ibu()

    periode_label = "Semua_Periode"
    if sel_bulan and sel_bulan.isdigit():
        b_num = int(sel_bulan)
        b_df = b_df[b_df["bulan"] == b_num] if "bulan" in b_df.columns else b_df
        i_df = i_df[i_df["bulan"] == b_num] if "bulan" in i_df.columns else i_df
        periode_label = f"Bulan_{b_num}"

    if sel_tahun and sel_tahun.isdigit():
        yr_num = int(sel_tahun)
        b_df = b_df[b_df["tahun"] == yr_num] if "tahun" in b_df.columns else b_df
        i_df = i_df[i_df["tahun"] == yr_num] if "tahun" in i_df.columns else i_df
        periode_label = f"{periode_label}_{yr_num}"

    rekap_stats = _calculate_rekap_stats(b_df, i_df)
    buf = generate_excel_report(periode_label.replace("_", " "), b_df, i_df, rekap_stats)

    filename = f"Laporan_Posyandu_{periode_label}.xlsx"
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/laporan/ekspor/pdf")
@login_required
def ekspor_pdf():
    """Cetak berkas PDF formal laporan posyandu untuk Puskesmas."""
    sel_bulan = request.args.get("bulan", "")
    sel_tahun = request.args.get("tahun", "")

    b_df = database.get_pemeriksaan_balita()
    i_df = database.get_pemeriksaan_ibu()

    periode_label = "Semua Periode"
    if sel_bulan and sel_bulan.isdigit():
        b_num = int(sel_bulan)
        b_df = b_df[b_df["bulan"] == b_num] if "bulan" in b_df.columns else b_df
        i_df = i_df[i_df["bulan"] == b_num] if "bulan" in i_df.columns else i_df
        b_dict = dict(BULAN_INDONESIA)
        periode_label = f"{b_dict.get(b_num, '')}"

    if sel_tahun and sel_tahun.isdigit():
        yr_num = int(sel_tahun)
        b_df = b_df[b_df["tahun"] == yr_num] if "tahun" in b_df.columns else b_df
        i_df = i_df[i_df["tahun"] == yr_num] if "tahun" in i_df.columns else i_df
        periode_label = f"{periode_label} {yr_num}".strip()

    rekap_stats = _calculate_rekap_stats(b_df, i_df)
    buf = generate_pdf_report(periode_label, b_df, i_df, rekap_stats)

    return send_file(
        buf,
        as_attachment=False,
        download_name=f"Laporan_Posyandu_{periode_label.replace(' ', '_')}.pdf",
        mimetype="application/pdf"
    )


# ====================================================================
# 7. DASHBOARD ORANG TUA BALITA
# ====================================================================
@app.route("/ortu/dashboard")
@login_required
@role_required(["Orang Tua Balita"])
def ortu_dashboard():
    """Dashboard tumbuh kembang anak balita bagi orang tua."""
    user_id = session.get("user_id", "")
    id_peserta = session.get("id_peserta", "")

    # Temukan balita yang terhubung dengan akun ini
    kids_df = database.get_children_by_parent_user_id(user_id)
    if kids_df.empty and id_peserta:
        # Fallback pencarian balita dengan id_orang_tua = id_peserta
        all_p = database.get_all_peserta()
        if not all_p.empty and "id_orang_tua" in all_p.columns:
            kids_df = all_p[all_p["id_orang_tua"].astype(str).str.upper() == id_peserta.upper()]

    kids = kids_df.to_dict(orient="records") if not kids_df.empty else []

    latest_exam = {}
    exam_history = []
    chart_kms_data = None

    if kids:
        current_kid = kids[0]
        k_id = current_kid.get("id_peserta", "")
        hist_df = database.get_pemeriksaan_by_peserta(k_id)

        if not hist_df.empty:
            hist_df["tanggal_str"] = pd.to_datetime(hist_df["tanggal_pemeriksaan"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("-")
            exam_history = hist_df.to_dict(orient="records")
            latest_exam = exam_history[0]

            # Siapkan kurva rujukan WHO untuk Plotly
            sex = current_kid.get("jenis_kelamin", "Perempuan")
            who_df = gizi.get_who_growth_curves(sex, "bb")

            # Data anak aktual yang terurut tanggal
            child_growth = hist_df.sort_values("usia_bulan")
            child_ages = child_growth["usia_bulan"].tolist()
            child_weights = child_growth["berat_kg"].tolist()

            chart_kms_data = {
                "ages": who_df["usia_bulan"].tolist(),
                "minus_2sd": who_df["minus_2sd"].tolist(),
                "median": who_df["median"].tolist(),
                "plus_2sd": who_df["plus_2sd"].tolist(),
                "child_ages": child_ages,
                "child_weights": child_weights
            }

    return render_template(
        "dashboard_ortu.html",
        active_page="dashboard",
        kids=kids,
        latest_exam=latest_exam,
        exam_history=exam_history,
        chart_kms_data=chart_kms_data
    )


# ====================================================================
# 8. DASHBOARD IBU HAMIL
# ====================================================================
@app.route("/ibu/dashboard")
@login_required
@role_required(["Ibu Hamil"])
def ibu_dashboard():
    """Dashboard kesehatan kehamilan & Buku KIA Digital."""
    user_id = session.get("user_id", "")
    id_peserta = session.get("id_peserta", "")

    ibu_data = database.get_peserta_by_user_id(user_id)
    if not ibu_data and id_peserta:
        ibu_data = database.get_peserta_by_id(id_peserta)

    latest_exam = {}
    exam_history = []

    if ibu_data:
        i_id = ibu_data.get("id_peserta", "")
        hist_df = database.get_pemeriksaan_by_peserta(i_id)
        if not hist_df.empty:
            hist_df["tanggal_str"] = pd.to_datetime(hist_df["tanggal_pemeriksaan"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("-")
            exam_history = hist_df.to_dict(orient="records")
            latest_exam = exam_history[0]

    return render_template(
        "dashboard_ibu.html",
        active_page="dashboard",
        ibu_data=ibu_data,
        latest_exam=latest_exam,
        exam_history=exam_history
    )


# ====================================================================
# 9. PUSAT EDUKASI KESEHATAN
# ====================================================================
@app.route("/edukasi")
@login_required
def edukasi_view():
    """Pusat edukasi kesehatan posyandu, nutrisi, MP-ASI & imunisasi."""
    return render_template("edukasi.html", active_page="edukasi")


@app.route("/kegiatan")
@login_required
@role_required(["Kader", "Orang Tua Balita", "Ibu Hamil"])
def kegiatan_view():
    """Kalender jadwal kontrol dari tanggal kunjungan berikutnya yang tersimpan."""
    today = date.today()
    try:
        year = int(request.args.get("tahun", today.year))
        month = int(request.args.get("bulan", today.month))
        if not 1 <= month <= 12 or not 2000 <= year <= 2100:
            raise ValueError
    except (TypeError, ValueError):
        year, month = today.year, today.month

    role = session.get("user_role")
    user_id = str(session.get("user_id", ""))
    participant_ids = set()
    participant_names = {}
    if role == "Kader":
        participants = database.get_all_peserta()
        if not participants.empty and "id_peserta" in participants:
            participant_ids.update(participants["id_peserta"].dropna().astype(str))
            if "nama" in participants:
                participant_names = dict(zip(participants["id_peserta"].astype(str), participants["nama"].fillna("")))
        balita_df = database.get_pemeriksaan_balita()
        ibu_df = database.get_pemeriksaan_ibu()
    elif role == "Orang Tua Balita":
        children = database.get_children_by_parent_user_id(user_id)
        parent_record_id = str(session.get("id_peserta", ""))
        if children.empty and parent_record_id:
            all_participants = database.get_all_peserta()
            if not all_participants.empty and {"id_orang_tua", "jenis_peserta"}.issubset(all_participants.columns):
                children = all_participants[
                    (all_participants["id_orang_tua"].astype(str) == parent_record_id)
                    & (all_participants["jenis_peserta"].astype(str) == "Balita")
                ]
        if not children.empty and "id_peserta" in children:
            participant_ids.update(children["id_peserta"].dropna().astype(str))
            if "nama" in children:
                participant_names = dict(zip(children["id_peserta"].astype(str), children["nama"].fillna("")))
        balita_df = database.get_pemeriksaan_balita()
        ibu_df = pd.DataFrame()
    else:
        ibu = database.get_peserta_by_user_id(user_id)
        ibu_id = str((ibu or {}).get("id_peserta") or session.get("id_peserta", ""))
        if ibu_id:
            participant_ids.add(ibu_id)
            participant_names[ibu_id] = (ibu or {}).get("nama", session.get("user_name", "Ibu Hamil"))
        ibu_df = database.get_pemeriksaan_by_peserta(ibu_id) if ibu_id else pd.DataFrame()
        balita_df = pd.DataFrame()

    def collect_events(frame, label):
        if frame.empty or "id_peserta" not in frame or "jadwal_berikutnya" not in frame:
            return []
        scoped = frame[frame["id_peserta"].astype(str).isin(participant_ids)]
        rows = []
        for record in scoped.to_dict(orient="records"):
            scheduled = pd.to_datetime(record.get("jadwal_berikutnya"), errors="coerce")
            if pd.isna(scheduled):
                continue
            pid = str(record.get("id_peserta", ""))
            rows.append({
                "date": scheduled.date(),
                "id_peserta": pid,
                "name": record.get("nama") or participant_names.get(pid) or "Peserta Posyandu",
                "type": label,
                "location": record.get("alamat_dusun") or "Posyandu",
                "status": "Terjadwal" if scheduled.date() >= today else "Terlewat",
            })
        return rows

    events = collect_events(balita_df, "Pemeriksaan Balita") + collect_events(ibu_df, "Pemeriksaan Ibu Hamil")
    events.sort(key=lambda item: (item["date"], item["name"]))
    month_events = [event for event in events if event["date"].year == year and event["date"].month == month]
    month_days = {}
    for event in month_events:
        month_days.setdefault(event["date"].day, []).append(event)

    month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    previous_month = 12 if month == 1 else month - 1
    previous_year = year - 1 if month == 1 else year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year
    return render_template(
        "kegiatan.html",
        active_page="kegiatan",
        month_name=month_names[month - 1],
        month=month,
        year=year,
        weeks=calendar_module.monthcalendar(year, month),
        month_days=month_days,
        month_events=month_events,
        weekday_names=["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
        previous_month=previous_month,
        previous_year=previous_year,
        next_month=next_month,
        next_year=next_year,
        today=today,
        event_count=len(month_events),
    )


@app.route("/panduan")
@login_required
def panduan_view():
    """Panduan ringkas menu aplikasi untuk pengguna yang sedang masuk."""
    return render_template("panduan.html", active_page="panduan")


# ====================================================================
# LAUNCHER
# ====================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"============================================================")
    print(f"🌸 JEJAK TUMBUH — POSYANDU DIGITAL (Cream Mocha Edition)")
    print(f"🚀 Server aktif di: http://127.0.0.1:{port}")
    print(f"🩺 Demo Kader: kader1 / kader123")
    print(f"👶 Demo Ortu : ort001 / demo123")
    print(f"🤰 Demo Ibu  : ibu001 / demo123")
    print(f"============================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
