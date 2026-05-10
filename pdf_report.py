from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import matplotlib.font_manager as fm

def temizle_metin(metin):
    metin = str(metin)

    metin = metin.replace("🔴", "")
    metin = metin.replace("🟠", "")
    metin = metin.replace("🟡", "")
    metin = metin.replace("🟢", "")

    return metin.strip()

    for eski, yeni in ceviri.items():
        metin = metin.replace(eski, yeni)

    return metin.strip()


def pdf_rapor_olustur(kayit):
    dosya_adi = "risk_analiz_raporu.pdf"

    font_path = fm.findfont("DejaVu Sans")
    bold_font_path = fm.findfont("DejaVu Sans:bold")

    pdfmetrics.registerFont(TTFont("DejaVu", font_path))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold_font_path))



    c = canvas.Canvas(dosya_adi, pagesize=A4)
    width, height = A4

    y = height - 60

    c.setFont("DejaVu-Bold", 16)
    c.drawString(50, y, "AI Destekli FMEA Risk Analiz Raporu")

    y -= 30
    c.setFont("DejaVu", 10)
    c.drawString(50, y, f"Rapor Tarihi: {datetime.now(ZoneInfo('Europe/Istanbul')).strftime('%d.%m.%Y %H:%M')}")

    y -= 40
    c.setFont("DejaVu-Bold", 12)
    c.drawString(50, y, "Risk Analiz Bilgileri")

    y -= 25
    c.setFont("DejaVu", 10)

    bilgiler = [
        ("Hata Kodu", kayit.get("hata_kodu", "")),
        ("Hata Türü", kayit.get("hata_turu", "")),
        ("Proses", kayit.get("proses", "")),
        ("İstasyon", kayit.get("istasyon", "")),
        ("Vardiya", kayit.get("vardiya", "")),
        ("O", kayit.get("O", "")),
        ("S", kayit.get("S", "")),
        ("D", kayit.get("D", "")),
        ("Geleneksel RPN", kayit.get("geleneksel_rpn", "")),
        ("Ağırlıklı RPN", kayit.get("agirlikli_rpn", "")),
        ("ML Tahmin RPN", kayit.get("ml_rpn", "")),
        ("Risk Seviyesi", kayit.get("risk_seviyesi", "")),
    ]

    for baslik, deger in bilgiler:
        c.drawString(60, y, f"{baslik}: {temizle_metin(deger)}")
        y -= 20

    y -= 20
    c.setFont("DejaVu-Bold", 12)
    c.drawString(50, y, "Önerilen Önlem")

    y -= 25
    c.setFont("DejaVu", 10)

    onlem = temizle_metin(kayit.get("onlem", ""))

    for i in range(0, len(onlem), 85):
        c.drawString(60, y, onlem[i:i+85])
        y -= 18

    y -= 30
    c.setFont("DejaVu-Bold", 11)
    c.drawString(50, y, "Sonuç")

    y -= 20
    c.setFont("DejaVu", 10)
    c.drawString(
        60,
        y,
        "Bu rapor, FMEA ve makine öğrenmesi tabanlı risk önceliklendirme sistemi tarafından oluşturulmuştur."
    )

    c.save()

    return dosya_adi