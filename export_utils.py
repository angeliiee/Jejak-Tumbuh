"""
====================================================================
JEJAK TUMBUH — POSYANDU DIGITAL
Modul Generator Ekspor Laporan Resmi (Excel .xlsx & PDF)
====================================================================
"""
import io
from datetime import date
from typing import Dict, Any
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_excel_report(periode: str, balita_df: pd.DataFrame, ibu_df: pd.DataFrame, rekap: Dict[str, Any]) -> io.BytesIO:
    """
    Menghasilkan berkas Excel (.xlsx) resmi laporan posyandu
    dengan format multi-sheet rapi dan styling Cream Mocha.
    """
    wb = openpyxl.Workbook()
    
    # ── PALET WARNA OPENPYXL ──
    FILL_HEADER = PatternFill(start_color="A68A76", end_color="A68A76", fill_type="solid") # Mocha
    FILL_SUB = PatternFill(start_color="E8DCCB", end_color="E8DCCB", fill_type="solid")    # Beige
    FILL_ZEBRA = PatternFill(start_color="FAF7F2", end_color="FAF7F2", fill_type="solid")
    
    FONT_TITLE = Font(name="Segoe UI", size=14, bold=True, color="46372E")
    FONT_HEADER = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    FONT_BOLD = Font(name="Segoe UI", size=10, bold=True, color="46372E")
    FONT_BODY = Font(name="Segoe UI", size=9, color="333333")
    
    THIN_BORDER = Border(
        left=Side(style="thin", color="DECFC0"),
        right=Side(style="thin", color="DECFC0"),
        top=Side(style="thin", color="DECFC0"),
        bottom=Side(style="thin", color="DECFC0")
    )
    
    # ── SHEET 1: RINGKASAN EKSEKUTIF ──
    ws1 = wb.active
    ws1.title = "Ringkasan Laporan"
    ws1.views.sheetView[0].showGridLines = True
    
    ws1.append(["POSYANDU DIGITAL — JEJAK TUMBUH"])
    ws1.append([f"LAPORAN REKAPITULASI PELAYANAN BULANAN (PERIODE: {periode})"])
    ws1.append([f"Tanggal Unduh: {date.today().strftime('%d %B %Y')}"])
    ws1.append([])
    
    ws1["A1"].font = FONT_TITLE
    ws1["A2"].font = FONT_BOLD
    ws1["A3"].font = FONT_BODY
    
    # Tabel Ringkasan Balita
    ws1.append(["REKAPITULASI INDIKATOR BALITA (WHO)"])
    ws1.merge_cells("A5:C5")
    ws1["A5"].font = FONT_HEADER
    ws1["A5"].fill = FILL_HEADER
    
    ws1.append(["Status Antropometri / Indikator", "Jumlah Balita", "Persentase"])
    for cell in ws1[6]:
        cell.font = FONT_BOLD
        cell.fill = FILL_SUB
        cell.border = THIN_BORDER
        
    balita_stats = [
        ["Normal / Gizi Baik", rekap.get("balita_normal", 0), f"{rekap.get('balita_normal_pct', 0)}%"],
        ["Gizi Kurang (Underweight)", rekap.get("balita_kurang", 0), f"{rekap.get('balita_kurang_pct', 0)}%"],
        ["Stunting (Pendek / Sangat Pendek)", rekap.get("balita_stunting", 0), f"{rekap.get('balita_stunting_pct', 0)}%"],
        ["Risiko Gizi Lebih", rekap.get("balita_lebih", 0), f"{rekap.get('balita_lebih_pct', 0)}%"],
        ["TOTAL BALITA DIPERIKSA", rekap.get("total_balita_diperiksa", 0), "100.0%"]
    ]
    for row in balita_stats:
        ws1.append(row)
        for cell in ws1[ws1.max_row]:
            cell.font = FONT_BODY
            cell.border = THIN_BORDER
    
    ws1.append([])
    
    # Tabel Ringkasan Ibu Hamil
    ws1.append(["REKAPITULASI KESEHATAN IBU HAMIL (KEMENKES RI)"])
    ws1.merge_cells(f"A{ws1.max_row}:C{ws1.max_row}")
    ws1[f"A{ws1.max_row}"].font = FONT_HEADER
    ws1[f"A{ws1.max_row}"].fill = FILL_HEADER
    
    ws1.append(["Indikator Faktor Risiko Maternal", "Jumlah Ibu", "Keterangan Medis"])
    for cell in ws1[ws1.max_row]:
        cell.font = FONT_BOLD
        cell.fill = FILL_SUB
        cell.border = THIN_BORDER
        
    ibu_stats = [
        ["Total Ibu Hamil Diperiksa ANC", rekap.get("total_ibu_diperiksa", 0), "Kunjungan terdaftar"],
        ["Kurang Energi Kronis (KEK)", rekap.get("ibu_kek", 0), "LILA < 23.5 cm"],
        ["Anemia Gestasional", rekap.get("ibu_anemia", 0), "Hb < 11.0 g/dL"],
        ["Hipertensi / Preeklamsia", rekap.get("ibu_hipertensi", 0), "TD >= 140/90 mmHg"],
        ["Ibu Hamil Risiko Tinggi", rekap.get("ibu_risiko_tinggi", 0), "Perlu rujukan faskes"]
    ]
    for row in ibu_stats:
        ws1.append(row)
        for cell in ws1[ws1.max_row]:
            cell.font = FONT_BODY
            cell.border = THIN_BORDER
            
    ws1.column_dimensions["A"].width = 38
    ws1.column_dimensions["B"].width = 16
    ws1.column_dimensions["C"].width = 24
    
    # ── SHEET 2: DATA PEMERIKSAAN BALITA ──
    ws2 = wb.create_sheet(title="Detail Pemeriksaan Balita")
    ws2.views.sheetView[0].showGridLines = True
    
    headers_balita = [
        "Tanggal Periksa", "ID Peserta", "Nama Balita", "Jenis Kelamin",
        "Usia (Bulan)", "Berat (kg)", "Tinggi (cm)", "Lingkar Kepala (cm)",
        "Z-BB/U", "Z-TB/U", "Status Gizi WHO", "Vitamin A", "Imunisasi", "Nama Orang Tua", "Dusun"
    ]
    ws2.append(headers_balita)
    for cell in ws2[1]:
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(horizontal="center")
        
    if not balita_df.empty:
        for idx, r in balita_df.iterrows():
            tgl_str = str(r.get("tanggal_pemeriksaan", ""))[:10]
            row_vals = [
                tgl_str, str(r.get("id_peserta", "")), str(r.get("nama", "")),
                str(r.get("jenis_kelamin", "")), r.get("usia_bulan", ""),
                r.get("berat_kg", ""), r.get("tinggi_cm", ""), r.get("lingkar_kepala_cm", ""),
                r.get("z_bb_u", ""), r.get("z_tb_u", ""), str(r.get("status_gizi", "")),
                str(r.get("vitamin_a", "")), str(r.get("imunisasi", "")),
                str(r.get("nama_orang_tua", "")), str(r.get("alamat_dusun", ""))
            ]
            ws2.append(row_vals)
            for cell in ws2[ws2.max_row]:
                cell.font = FONT_BODY
                cell.border = THIN_BORDER
                if idx % 2 == 1:
                    cell.fill = FILL_ZEBRA
                    
    for col in ws2.columns:
        col_letter = col[0].column_letter
        ws2.column_dimensions[col_letter].width = 18
    ws2.column_dimensions["C"].width = 24
    ws2.column_dimensions["N"].width = 24
    
    # ── SHEET 3: DATA PEMERIKSAAN IBU HAMIL ──
    ws3 = wb.create_sheet(title="Detail Pemeriksaan Ibu Hamil")
    ws3.views.sheetView[0].showGridLines = True
    
    headers_ibu = [
        "Tanggal Periksa", "ID Peserta", "Nama Ibu", "Usia Ibu (Th)",
        "Usia Hamil (Mgg)", "Berat (kg)", "LILA (cm)", "Tekanan Darah",
        "Hb (g/dL)", "TFU (cm)", "DJJ (bpm)", "Tablet Fe",
        "Status KEK", "Status Anemia", "Tingkat Risiko", "Dusun"
    ]
    ws3.append(headers_ibu)
    for cell in ws3[1]:
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(horizontal="center")
        
    if not ibu_df.empty:
        for idx, r in ibu_df.iterrows():
            tgl_str = str(r.get("tanggal_pemeriksaan", ""))[:10]
            td_str = f"{r.get('sistol', '')}/{r.get('diastol', '')}"
            row_vals = [
                tgl_str, str(r.get("id_peserta", "")), str(r.get("nama", "")),
                r.get("usia_ibu_tahun", ""), r.get("usia_kehamilan_minggu", ""),
                r.get("berat_kg", ""), r.get("lila_cm", ""), td_str,
                r.get("hb_gdl", ""), r.get("tfu_cm", ""), r.get("djj_bpm", ""),
                str(r.get("tablet_fe", "")), str(r.get("status_kek", "")),
                str(r.get("status_anemia", "")), str(r.get("risiko", "")),
                str(r.get("alamat_dusun", ""))
            ]
            ws3.append(row_vals)
            for cell in ws3[ws3.max_row]:
                cell.font = FONT_BODY
                cell.border = THIN_BORDER
                if idx % 2 == 1:
                    cell.fill = FILL_ZEBRA
                    
    for col in ws3.columns:
        col_letter = col[0].column_letter
        ws3.column_dimensions[col_letter].width = 18
    ws3.column_dimensions["C"].width = 24

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_pdf_report(periode: str, balita_df: pd.DataFrame, ibu_df: pd.DataFrame, rekap: Dict[str, Any]) -> io.BytesIO:
    """
    Menghasilkan berkas PDF formal laporan rekapitulasi posyandu
    dengan tata letak resmi siap cetak dan lembar pengesahan tanda tangan.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    style_kop1 = ParagraphStyle(
        "Kop1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=1, # Center
        textColor=colors.HexColor("#46372E")
    )
    style_kop2 = ParagraphStyle(
        "Kop2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#8C715E")
    )
    style_sub = ParagraphStyle(
        "KopSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#6E5B50")
    )
    
    style_sec = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#46372E")
    )
    style_cell = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#333333")
    )
    style_cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#46372E")
    )

    story = []
    
    # ── KOP SURAT RESMI ──
    story.append(Paragraph("PEMERINTAH KABUPATEN / KOTA — DINAS KESEHATAN", style_kop1))
    story.append(Paragraph("PUSAT PELAYANAN TERPADU (POSYANDU) DIGITAL — JEJAK TUMBUH", style_kop2))
    story.append(Paragraph("Sistem Integrasi Standar Pertumbuhan WHO & Pemantauan Maternal Kemenkes RI", style_sub))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#46372E"), spaceAfter=10))
    
    # ── JUDUL LAPORAN ──
    story.append(Paragraph(f"<b>LAPORAN BULANAN REKAPITULASI PELAYANAN POSYANDU</b>", style_kop2))
    story.append(Paragraph(f"Periode Pelayanan: <b>{periode}</b> &bull; Tanggal Cetak: {date.today().strftime('%d %B %Y')}", style_sub))
    story.append(Spacer(1, 12))
    
    # ── TABEL REKAPITULASI RINGKASAN EKSEKUTIF ──
    story.append(Paragraph("1. RINGKASAN INDIKATOR KESEHATAN POSYANDU", style_sec))
    story.append(Spacer(1, 4))
    
    data_rekap = [
        [
            Paragraph("<b>Indikator Balita (WHO)</b>", style_cell_bold),
            Paragraph("<b>Jumlah</b>", style_cell_bold),
            Paragraph("<b>Indikator Ibu Hamil (ANC)</b>", style_cell_bold),
            Paragraph("<b>Jumlah</b>", style_cell_bold)
        ],
        [
            Paragraph("Total Balita Diperiksa", style_cell),
            Paragraph(f"{rekap.get('total_balita_diperiksa', 0)} anak", style_cell),
            Paragraph("Total Ibu Hamil Diperiksa", style_cell),
            Paragraph(f"{rekap.get('total_ibu_diperiksa', 0)} ibu", style_cell)
        ],
        [
            Paragraph("Gizi Baik / Normal", style_cell),
            Paragraph(f"{rekap.get('balita_normal', 0)} ({rekap.get('balita_normal_pct', 0)}%)", style_cell),
            Paragraph("Kurang Energi Kronis (KEK)", style_cell),
            Paragraph(f"{rekap.get('ibu_kek', 0)} kasus", style_cell)
        ],
        [
            Paragraph("Stunting (Pendek / Sgt Pendek)", style_cell),
            Paragraph(f"<b>{rekap.get('balita_stunting', 0)} ({rekap.get('balita_stunting_pct', 0)}%)</b>", style_cell),
            Paragraph("Anemia Gestasional", style_cell),
            Paragraph(f"{rekap.get('ibu_anemia', 0)} kasus", style_cell)
        ],
        [
            Paragraph("Gizi Kurang (Underweight)", style_cell),
            Paragraph(f"{rekap.get('balita_kurang', 0)} ({rekap.get('balita_kurang_pct', 0)}%)", style_cell),
            Paragraph("Hipertensi / Preeklamsia", style_cell),
            Paragraph(f"{rekap.get('ibu_hipertensi', 0)} kasus", style_cell)
        ],
        [
            Paragraph("Risiko Gizi Lebih", style_cell),
            Paragraph(f"{rekap.get('balita_lebih', 0)} ({rekap.get('balita_lebih_pct', 0)}%)", style_cell),
            Paragraph("<b>Ibu Hamil Risiko Tinggi</b>", style_cell_bold),
            Paragraph(f"<b>{rekap.get('ibu_risiko_tinggi', 0)} kasus</b>", style_cell_bold)
        ]
    ]
    
    t_rekap = Table(data_rekap, colWidths=[150, 100, 160, 100])
    t_rekap.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8DCCB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#46372E")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DECFC0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_rekap)
    story.append(Spacer(1, 14))
    
    # ── TABEL DAFTAR KASUS PERHATIAN: BALITA STUNTING / GIZI KURANG ──
    story.append(Paragraph("2. DAFTAR BALITA PERLU INTERVENSI GIZI & PEMANTAUAN KHUSUS", style_sec))
    story.append(Spacer(1, 4))
    
    stunting_list = []
    if not balita_df.empty:
        stunting_df = balita_df[
            balita_df["status_gizi"].astype(str).str.contains("Stunting|Sangat|kurang", case=False, na=False)
        ].head(8)
        
        table_stunting_data = [
            [
                Paragraph("<b>ID / Nama Balita</b>", style_cell_bold),
                Paragraph("<b>Usia</b>", style_cell_bold),
                Paragraph("<b>BB (kg)</b>", style_cell_bold),
                Paragraph("<b>TB (cm)</b>", style_cell_bold),
                Paragraph("<b>Z-TB/U</b>", style_cell_bold),
                Paragraph("<b>Status Gizi</b>", style_cell_bold),
                Paragraph("<b>Orang Tua</b>", style_cell_bold)
            ]
        ]
        for _, b in stunting_df.iterrows():
            table_stunting_data.append([
                Paragraph(f"{b.get('id_peserta', '')} — {b.get('nama', '')}", style_cell),
                Paragraph(f"{b.get('usia_bulan', '')} bln", style_cell),
                Paragraph(str(b.get('berat_kg', '')), style_cell),
                Paragraph(str(b.get('tinggi_cm', '')), style_cell),
                Paragraph(str(b.get('z_tb_u', '')), style_cell),
                Paragraph(str(b.get('status_gizi', '')), style_cell),
                Paragraph(str(b.get('nama_orang_tua', '')), style_cell),
            ])
            
        if len(table_stunting_data) > 1:
            t_stunt = Table(table_stunting_data, colWidths=[120, 45, 45, 45, 50, 115, 90])
            t_stunt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F5EFE6")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DECFC0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(t_stunt)
        else:
            story.append(Paragraph("<i>Tidak ada kasus balita stunting atau gizi kurang pada periode ini.</i>", style_cell))
    
    story.append(Spacer(1, 20))
    
    # ── LEMBAR PENGESAHAN TANDA TANGAN ──
    ttd_data = [
        [
            Paragraph("Mengetahui,<br/><b>Bidan Desa / Koordinator Puskesmas</b>", style_kop2),
            Paragraph("Dilaporkan oleh,<br/><b>Kader Posyandu Digital</b>", style_kop2)
        ],
        [
            Spacer(1, 40),
            Spacer(1, 40)
        ],
        [
            Paragraph("____________________________<br/>NIP. .....................................", style_sub),
            Paragraph("<b>Kader Citra Wijaya</b><br/>ID Kader: KAD001", style_sub)
        ]
    ]
    t_ttd = Table(ttd_data, colWidths=[255, 255])
    t_ttd.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_ttd)
    
    doc.build(story)
    buf.seek(0)
    return buf
