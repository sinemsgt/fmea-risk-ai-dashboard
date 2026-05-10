HATA_TURLERI = {
    "M01": {
        "isim": "Yanlış Terminal Krimpleme",
        "proses": "K-10 Kablo & Alt Parça Montajı",
        "etki": "Elektrik iletiminde kesilme / fonksiyon kaybı",
        "aciklamalar": [
            "terminal krimplemesi uygun değil yüksek direnç",
            "krimpleme kuvveti yetersiz kopma riski var",
            "terminal düzgün oturmamış elektrik bağlantısı bozuk",
            "yanlış terminal tipi kullanılmış",
            "krimpleme makinesi kalibrasyon hatası",
        ],
        "O_aralik": (5, 9), "S_aralik": (6, 10), "D_aralik": (2, 6),
        "onlem": "Elektrik test board (Poka-Yoke) + krimpleme force monitörü",
    },
    "M02": {
        "isim": "İzolasyon Hasarı",
        "proses": "K-10 Kablo & Alt Parça Montajı",
        "etki": "Kısa devre ve yangın riski",
        "aciklamalar": [
            "kablo izolasyonu soyulmuş kısa devre tehlikesi",
            "izolasyon kesiti hasarlı iletken görünüyor",
            "dış kılıf çatlak nem geçişi mümkün",
            "izolasyon kalınlığı standart altı",
            "bükme yarıçapı aşılmış kılıf yırtılmış",
        ],
        "O_aralik": (3, 7), "S_aralik": (7, 10), "D_aralik": (3, 7),
        "onlem": "5S denetimleri + görsel kontrol + elektrik test (Poka-Yoke)",
    },
    "M03": {
        "isim": "Hatalı Pin Yerleşimi",
        "proses": "K-20 Kablo & Alt Parça Montajı",
        "etki": "Yeniden işçilik ve fonksiyon kaybı",
        "aciklamalar": [
            "pin yanlış pozisyona takılmış konektör hatalı",
            "pin hizalaması bozuk elektrik bağlantısı yok",
            "yanlış renk kodlu kablo yanlış pine takıldı",
            "pin eksik konektörde boşluk var",
            "pin kılavuzu uyumsuz montaj hatası",
        ],
        "O_aralik": (4, 8), "S_aralik": (5, 9), "D_aralik": (3, 7),
        "onlem": "Elektrik test board (Poka-Yoke) + dikkatsizlik eğitimi",
    },
    "M04": {
        "isim": "İletken Kopması",
        "proses": "K-10 Kablo & Alt Parça Montajı",
        "etki": "Tam devre kesintisi",
        "aciklamalar": [
            "iletken kopmuş bağlantı yok",
            "tel kesiti yetersiz aşırı akım kopması",
            "iletken yorulma kırığı görülüyor",
            "kesme bıçağı aşınmış kablo ezilmiş",
            "kablo gerilmesi kopma noktasına ulaşmış",
        ],
        "O_aralik": (2, 6), "S_aralik": (8, 10), "D_aralik": (1, 5),
        "onlem": "Çekme kuvveti testi + kesit analizi + kalibrasyon",
    },
    "M05": {
        "isim": "Yanlış Barkod Etiketi",
        "proses": "A-10 Komponent Kabulü",
        "etki": "Uygunsuz malzeme sürece girer",
        "aciklamalar": [
            "barkod etiketi yanlış ürün kodu eşleşmiyor",
            "etiket okunamıyor sistem kaydı yapılamıyor",
            "tedarikçi etiketi standart dışı tarayıcı okuyamıyor",
            "barkod konumu hatalı tarama başarısız",
            "etiket üzerine etiket yapıştırılmış çakışma var",
        ],
        "O_aralik": (2, 5), "S_aralik": (3, 6), "D_aralik": (1, 4),
        "onlem": "Barkod okuyucu (Poka-Yoke) + çift kontrol prosedürü",
    },
    "M06": {
        "isim": "SAP Stok Uyumsuzluğu",
        "proses": "B-10 Komponent Depolama",
        "etki": "Stok eksikliği üretim durması",
        "aciklamalar": [
            "SAP sisteminde stok bilgisi gerçekle uyuşmuyor",
            "malzeme fiziksel olarak yok sistem kayıtlı gösteriyor",
            "yanlış depo konumu girilmiş malzeme bulunamıyor",
            "sipariş miktarı SAP hatalı girilmiş",
            "fire kayıt edilmemiş stok fazla görünüyor",
        ],
        "O_aralik": (3, 6), "S_aralik": (5, 8), "D_aralik": (4, 8),
        "onlem": "MRP sistemi + Barkod okuyucu (Poka-Yoke)",
    },
    "M07": {
        "isim": "Kablo Etiketi Eksikliği",
        "proses": "K-20 Kablo & Alt Parça Montajı – Malzeme",
        "etki": "Yanlış kablo tanımlama",
        "aciklamalar": [
            "kablo üzerinde etiket yok tanımlama yapılamıyor",
            "etiket düşmüş kablo kimliksiz",
            "baskı solmuş okunamıyor",
            "etiket boyutu uygun değil yapışmıyor",
            "yanlış yazıcı şablonu kullanılmış",
        ],
        "O_aralik": (2, 5), "S_aralik": (2, 5), "D_aralik": (3, 6),
        "onlem": "Görsel kontrol + Poka-Yoke test board",
    },
    "M08": {
        "isim": "Klips Uyumsuzluğu",
        "proses": "K-20 Kablo & Alt Parça Montajı – Malzeme",
        "etki": "Klipsler delikleri karşılayamıyor",
        "aciklamalar": [
            "klips boyutu yanlış deliğe girmiyor",
            "klips tipi uyumsuz araç gövdesine takılmıyor",
            "yanlış klips kullanılmış serbest bırakıyor",
            "klips kırılgan kırılma riski var",
            "klips eksik montaj yapılamıyor",
        ],
        "O_aralik": (3, 6), "S_aralik": (4, 7), "D_aralik": (2, 5),
        "onlem": "5S denetimleri + görsel kontrol + Poka-Yoke",
    },
    "M09": {
        "isim": "Oluk Sayısı Yetersizliği",
        "proses": "K-20 Kablo & Alt Parça Montajı – Malzeme",
        "etki": "Yanlış yerleştirme riski",
        "aciklamalar": [
            "oluk sayısı yetersiz kablo sığmıyor",
            "kanal kapasitesi aşılmış kablo sıkışıyor",
            "yanlış kanalama planı uygulanmış",
            "oluk genişliği dar kablo hasarı oluşuyor",
            "routing şeması güncellenmemiş eski plan uygulandı",
        ],
        "O_aralik": (2, 5), "S_aralik": (3, 6), "D_aralik": (3, 7),
        "onlem": "5S denetimleri + görsel kontrol + elektrik test board",
    },
}

ISTASYON_LISTESI = [
    "İst-01 Kesim", "İst-02 Soyma", "İst-03 Krimpleme",
    "İst-04 Montaj-A", "İst-05 Montaj-B", "İst-06 Test",
    "İst-07 Etiketleme", "İst-08 Paketleme"
]
OPERATORLER = [f"OP-{i:03d}" for i in range(1, 21)]
VARDIYALAR = ["Sabah (06-14)", "Öğleden Sonra (14-22)", "Gece (22-06)"]

RENK_PALETI = ["#1f4e79", "#2e75b6", "#9dc3e6", "#c00000",
               "#ff6961", "#f4a261", "#2a9d8f", "#6a4c93", "#264653"]