# Jejak-Tumbuh
<div align="center">

<img src="https://raw.githubusercontent.com/adindaadeliafutri6-gif/jejak-tumbuh/main/jejak%20tumbuh%20(2).jpeg" alt="Logo JEJAK TUMBUH" width="140">

# JEJAK TUMBUH
### Posyandu Digital: Pantau Tumbuh Kembang Balita dan Kesehatan Ibu Hamil

Aplikasi web untuk mendigitalkan layanan Posyandu: pencatatan pemeriksaan, perhitungan status gizi otomatis berdasarkan **standar antropometri WHO**, skrining risiko ibu hamil mengacu **Kemenkes RI**, serta laporan siap cetak.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB)
![Flask](https://img.shields.io/badge/Flask-3.1-000000)
![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75)
![Versi](https://img.shields.io/badge/versi-5.0-A68A76)

</div>

---

## Daftar Isi

- [Tentang Proyek](#tentang-proyek)
- [Fitur Utama](#fitur-utama)
- [Peran Pengguna](#peran-pengguna)
- [Teknologi](#teknologi)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi dan Menjalankan](#instalasi-dan-menjalankan)
- [Akun Demo](#akun-demo)
- [Metode Perhitungan](#metode-perhitungan)
- [Pengujian](#pengujian)
- [Catatan dan Batasan](#catatan-dan-batasan)
- [Tim Pengembang](#tim-pengembang)

---

## Tentang Proyek

Pencatatan Posyandu yang masih manual sering menyulitkan kader dalam memantau perkembangan anak dari waktu ke waktu, dan orang tua pun sulit melihat riwayat pemeriksaan buah hatinya. **JEJAK TUMBUH** hadir untuk menjembatani hal tersebut:

- **Kader** mencatat hasil pemeriksaan dan langsung mendapat klasifikasi status gizi atau risiko kehamilan.
- **Orang tua** dan **ibu hamil** dapat melihat riwayat, grafik pertumbuhan, dan jadwal kunjungan berikutnya dari akun masing-masing.
- **Laporan bulanan** dapat dibuat dan diekspor ke Excel maupun PDF hanya dengan beberapa klik.

---

## Fitur Utama

| Fitur | Deskripsi |
|---|---|
| **Landing Page 3 Tahap** | Sambutan, petunjuk penggunaan, lalu login atau registrasi, dengan tombol akun demo sekali klik. |
| **Pemeriksaan Balita** | Input BB, TB, lingkar kepala, vitamin A, dan imunisasi. Pratinjau Z-Score WHO (BB/U, TB/U) dan status gizi tampil langsung. |
| **Pemeriksaan Ibu Hamil** | Input usia kehamilan, LILA, tekanan darah, Hb, TFU, DJJ, dan tablet Fe. Deteksi KEK, anemia, hipertensi, dan tingkat risiko otomatis. |
| **Kurva Pertumbuhan (KMS Digital)** | Grafik interaktif Plotly dengan garis -3SD, -2SD, median, +2SD, +3SD. |
| **Buku KIA Digital** | Riwayat kunjungan ANC, taksiran persalinan (HPL), dan tanda bahaya kehamilan. |
| **Kalender Kunjungan** | Jadwal bersumber dari kolom `jadwal_berikutnya` pada setiap pemeriksaan. |
| **Laporan Rekapitulasi** | Rekap bulanan dengan filter periode, arsip laporan, dan status penyerahan ke Puskesmas. |
| **Ekspor Excel dan PDF** | Excel multi-sheet (ringkasan, detail balita, detail ibu hamil) dan PDF dengan kop surat serta lembar pengesahan. |
| **Pusat Edukasi** | Materi gizi, MP-ASI, dan kehamilan sehat, plus saran pertumbuhan yang disesuaikan dengan hasil pemeriksaan. |
| **Akses Berbasis Peran** | Menu dan halaman menyesuaikan peran pengguna (Kader, Orang Tua Balita, Ibu Hamil). |
| **Antarmuka Cream Mocha** | Sidebar yang melebar saat di-hover, notifikasi toast, responsif di seluler, dan menghormati pengaturan *reduced motion*. |

---

## Peran Pengguna

| Peran | Yang bisa dilakukan |
|---|---|
| **Kader Posyandu** | Dashboard Posyandu, kelola data peserta, entri pemeriksaan balita dan ibu hamil, laporan, arsip, ekspor Excel/PDF. |
| **Orang Tua Balita** | Dashboard tumbuh kembang, grafik KMS dan Z-Score, riwayat penimbangan, tambah data balita, edukasi MP-ASI. |
| **Ibu Hamil** | Dashboard kehamilan, Buku KIA digital, riwayat ANC, edukasi kehamilan sehat. |

> Registrasi mandiri hanya tersedia untuk **Orang Tua Balita** dan **Ibu Hamil**. Akun **Kader** dibuat oleh pengelola.

---

## Teknologi

| Lapisan | Teknologi |
|---|---|
| **Backend** | Python, Flask |
| **Frontend** | Jinja2 Templates, HTML, CSS, JavaScript, Plotly |
| **Penyimpanan Data** | Berkas CSV lokal (folder `data/`) |
| **Pengolahan Data** | pandas, NumPy |
| **Ekspor Dokumen** | openpyxl (Excel), ReportLab (PDF) |
| **Antarmuka Alternatif** | Streamlit (`app_streamlit.py`) |

---

## Struktur Proyek

```text
posyandu-digital/
├── app.py                  # Aplikasi utama Flask (routing dan logika halaman)
├── app_streamlit.py        # Versi alternatif berbasis Streamlit
├── run.py                  # Launcher singkat
├── gizi.py                 # Z-Score WHO dan skrining risiko maternal
├── export_utils.py         # Pembuat laporan Excel dan PDF
├── gen_data.py             # Generator data sintetis
├── requirements.txt
│
├── database/               # Lapisan akses data
│   ├── users.py
│   ├── peserta.py
│   ├── pemeriksaan.py
│   ├── laporan.py
│   └── edukasi.py
│
├── backend/                # Konfigurasi, repositories, dan services
│
├── frontend/
│   ├── templates/          # Halaman HTML (landing, dashboard, pemeriksaan, laporan, dll.)
│   ├── static/             # CSS, JS, dan gambar
│   ├── components/         # Komponen UI (carousel edukasi, animasi, tabel)
│   └── assets/             # Logo
│
├── data/                   # Dataset CSV (peserta, pemeriksaan, users, dll.)
└── tests/                  # Pengujian otomatis
```

---

## Instalasi dan Menjalankan

### Prasyarat

- **Python 3.12** atau lebih baru
- `pip` dan sebaiknya *virtual environment*

### Langkah-langkah

**1. Clone repositori**

```bash
git clone https://github.com/angeliiee/Posyandu-Digitall.git
cd Posyandu-Digitall
```

**2. Buat dan aktifkan virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Pasang dependensi**

```bash
pip install -r requirements.txt
```

**4. Jalankan aplikasi**

```bash
python run.py
```

**5. Buka di peramban**

```text
http://127.0.0.1:5000
```

### Menjalankan versi Streamlit (opsional)

```bash
streamlit run app_streamlit.py
```

Dibuka di `http://localhost:8501`.

### Variabel Lingkungan Opsional

| Variabel | Fungsi | Bawaan |
|---|---|---|
| `PORT` | Port server Flask | `5000` |
| `SECRET_KEY` | Kunci penandatangan sesi | nilai bawaan pengembangan |

---

## Akun Demo

Data contoh sintetis (sekitar 150 peserta) sudah tersedia. Di landing page tahap 3, klik kartu peran untuk masuk otomatis, atau isi manual:

| Peran | Username | Password |
|---|---|---|
| Kader Posyandu | `kader1` | `kader123` |
| Orang Tua Balita | `ort001` | `demo123` |
| Ibu Hamil | `ibu001` | `demo123` |

> Akun di atas hanya untuk demonstrasi. Hapus atau ganti sebelum aplikasi dipakai dengan data sebenarnya.

---

## Metode Perhitungan

### Status Gizi Balita

Z-Score dihitung dengan rumus `(nilai ukur - median) / SD`, menggunakan median dan SD rujukan WHO per jenis kelamin yang diinterpolasi linear terhadap usia (0 sampai 60 bulan).

| Indikator | Kondisi | Klasifikasi |
|---|---|---|
| **TB/U** | Z < -3 | Sangat Pendek |
| | -3 <= Z < -2 | Pendek (Stunting) |
| | -2 <= Z <= 3 | Normal |
| **BB/U** | Z < -3 | Berat Badan Sangat Kurang |
| | -3 <= Z < -2 | Berat Badan Kurang |
| | -2 <= Z <= 1 | Normal |
| | Z > 1 | Risiko Berat Badan Lebih |

**Status ringkas:** `Stunting` (Z TB/U < -2), lalu `Gizi kurang` (Z BB/U < -2), lalu `Risiko gizi lebih` (Z BB/U > 2), selain itu `Normal`.

### Risiko Ibu Hamil

| Faktor | Ambang batas |
|---|---|
| **KEK** | LILA < 23,5 cm |
| **Anemia** | Hb < 11 g/dL |
| **Hipertensi** | Sistol >= 140 atau diastol >= 90 mmHg |

| Tingkat risiko | Kondisi |
|---|---|
| **Risiko tinggi** | Hipertensi, atau Hb < 8 g/dL, atau dua faktor atau lebih terpenuhi |
| **Perlu pemantauan** | Satu faktor terpenuhi |
| **Risiko rendah** | Tidak ada faktor risiko |

---

## Pengujian

```bash
# Modul antropometri WHO, autentikasi, dan registrasi
python tests/test_suite.py

# Alur aplikasi web: login, form pemeriksaan, laporan, dan ekspor
python tests/test_web_app.py
```

---

## Catatan dan Batasan

- **Bukan alat diagnosis.** Hasil klasifikasi bersifat skrining awal dan tidak menggantikan penilaian tenaga kesehatan.
- **Rujukan WHO disederhanakan.** Median dan SD berasal dari tabel ringkas yang diinterpolasi, bukan tabel LMS lengkap WHO.
- **Data bersifat sintetis.** Seluruh data contoh dibuat oleh `gen_data.py` dan bukan data pasien nyata.
- **Sebelum produksi:** atur `SECRET_KEY` yang kuat dan acak, serta jangan membagikan berkas `.env` maupun `credentials.json`.

---

## Tim Pengembang

**Kelompok Jejak Tumbuh**

| No | Nama | NIM |
|---|---|---|
| 1 | Adinda Adelia Futri | 52250055 |
| 2 | Angelica Florentina M | 52250063 |
| 3 | Kayla Aprilia | 52250057 |
| 4 | Naifa Edria Arta | 52250056 |
| 5 | Adinda Maiza Ishfahani | 52250074 |

**Dosen Pengampu:** Dr. Andi Pujo Rahadi, S.T., M.Sc

Repositori: [github.com/angeliiee/Posyandu-Digitall](https://github.com/angeliiee/Posyandu-Digitall)
