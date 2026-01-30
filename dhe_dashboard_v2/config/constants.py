"""
DHE Dashboard - Sabitler ve Konfigürasyon
==========================================
Tüm sabit değerler, haritalar ve dönüşüm tabloları burada tanımlanır.
"""

# =============================================================================
# KURUMSAL RENK PALETİ
# =============================================================================
# =============================================================================
# KURUMSAL RENK PALETİ
# =============================================================================
CORPORATE_COLORS = ['#0C141F', '#C4121F', '#E5E7EB']

COLORS = {
    "PRIMARY": "#C4121F",       # DHE Kırmızısı
    "SECONDARY": "#1E293B",     # Koyu Arkaplan
    "SUCCESS": "#10B981",       # Yeşil
    "WARNING": "#F59E0B",       # Turuncu
    "DANGER": "#EF4444",        # Kırmızı
    "INFO": "#3B82F6",          # Mavi
    "VIP": "#FACC15",           # Altın Sarısı
    "TEXT_DARK": "#111827",
    "TEXT_LIGHT": "#F9FAFB",
    "TEXT_MUTED": "#9CA3AF"
}

# =============================================================================
# TARİH VE ZAMAN AYARLARI
# =============================================================================
from datetime import datetime
CURRENT_YEAR = datetime.now().year
# Otomatik olarak: Geçen Yıl, Bu Yıl, Gelecek Yıl
# Otomatik olarak: Geçen Yıl, Bu Yıl (Gelecek Yıl opsiyonel)
YEARS_TO_FETCH = ["2024", "2025", "2026"] # Yüksel Page requires 2024 data
# Eğer Gelecek Yıl sekmesi oluşturulduysa burayı + 2 yapabilirsiniz.


# =============================================================================
# DÖVİZ KURLARI (YILLIK ORTALAMALAR)
# =============================================================================
# Base: 1 Birim = X EUR (Sistem doğrudan bu çarpanı kullanır)
# Örn: 100 USD * 0.88 = 88 EUR
YEARLY_EXCHANGE_RATES = {
    2017: {"EUR": 1.0, "USD": 0.89, "GBP": 1.14, "TL": 0.235, "TRY": 0.235},
    2018: {"EUR": 1.0, "USD": 0.85, "GBP": 1.13, "TL": 0.185, "TRY": 0.185},
    2019: {"EUR": 1.0, "USD": 0.89, "GBP": 1.14, "TL": 0.160, "TRY": 0.160},
    2020: {"EUR": 1.0, "USD": 0.88, "GBP": 1.13, "TL": 0.125, "TRY": 0.125},
    2021: {"EUR": 1.0, "USD": 0.85, "GBP": 1.17, "TL": 0.096, "TRY": 0.096},
    2022: {"EUR": 1.0, "USD": 0.96, "GBP": 1.18, "TL": 0.058, "TRY": 0.058},
    2023: {"EUR": 1.0, "USD": 0.93, "GBP": 1.15, "TL": 0.039, "TRY": 0.039},
    2024: {"EUR": 1.0, "USD": 0.93, "GBP": 1.18, "TL": 0.029, "TRY": 0.029},
    2025: {"EUR": 1.0, "USD": 0.90, "GBP": 1.17, "TL": 0.023, "TRY": 0.023},
    2026: {"EUR": 1.0, "USD": 0.92, "GBP": 1.18, "TL": 0.022, "TRY": 0.022},
}

# =============================================================================
# PERSONEL EŞLEŞTİRMESİ
# =============================================================================
# Excel'deki kısa kodlar -> Tam isimler
PERSONEL_MAP = {
    # Uzun kodlar (Sayfa2 - Siparişler)
    "MERTGUNE": "Mert Güneş",
    "OGUZHANB": "Oğuzhan Bayır",
    "FATIHARS": "Fatih Arslan",
    "KAANAKKO": "Kaan Akkocaoğlu",
    "ALIRIZA": "Ali Rıza Çınar",
    "YUKSELKA": "Yüksel Kaya",
    "SAMETACA": "Samet Acar",
    "OZLEMSUL": "Özlem Suludere",
    # Kısa kodlar (Sayfa3 - Müşteriler)
    "MERT": "Mert Güneş",
    "OGUZHAN": "Oğuzhan Bayır",
    "FATIH": "Fatih Arslan",
    "KAAN": "Kaan Akkocaoğlu",
    "YUKSEL": "Yüksel Kaya",
    "SAMET": "Samet Acar",
    "OZLEM": "Özlem Suludere"
}

# =============================================================================
# SAHA EKİBİ (ATÖLYE & MONTAJ)
# =============================================================================
FIELD_TECHNICIANS = [
    "BURAK D. GÜZEL",
    "MEHMET ÇANTA",
    "SADETTİN KUŞCU",
    "ENES ÖZDEMİR",
    "FİKRET İSABETLİ",
    "EMRE KAPLAN",
    "FATİH KURTMAN",
    "YUNUS EMRE AYDIN",
    "FATİH DEMİRTAŞ",
    "TUĞRUL CAN KÜNDÜR",
    "SEZER ÖĞÜT",
    "ULAŞ EGE DEMİR"
]

# =============================================================================
# İŞLEM ÖZETİ PERSONEL LİSTESİ
# =============================================================================
# İşlem Özeti sayfasında gösterilecek personel listesi
ISLEM_OZETI_PERSONEL = [
    "YÜKSEL", 
    "SAMET", 
    "OĞUZHAN", 
    "FATİH", 
    "KAAN", 
    "MERT"
]

# =============================================================================
# AY HARİTALARI
# =============================================================================
AY_MAP = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

AY_KISA = {
    1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 
    5: "May", 6: "Haz", 7: "Tem", 8: "Ağu", 
    9: "Eyl", 10: "Eki", 11: "Kas", 12: "Ara"
}

# =============================================================================
# GOOGLE SHEETS VERİ KAYNAĞI KONFİGÜRASYONU
# =============================================================================
SHEETS_CONFIG = {
    "FILE_NAME": "DHE_Data",  # Google Sheets dosya adı
    "SHEETS": {
        "TEKLIF": "teklif",
        "SIPARIS": "siparis",
        "MUSTERI": "müsteri",
        "URUN": "ürün",
        "KURLAR": "kurlar",
        "PERSONEL": "Personel",
        "TATILLER": "Tatiller",
        "SEHIRLER": "sehirler"
    },
    # Excel Başlıkları -> Kod İçindeki Değişken İsimleri
    "COLUMN_MAPPINGS": {
        "TEKLIF": {
            "Teklif No": "Teklif_No",
            "Müşteri": "Musteri",
            "Sorumlu": "Personel",
            "Tarih": "Tarih",
            "Tutar": "Tutar_Ham",
            "Maliyet": "Maliyet_Ham",
            "İşaret": "Isaret",
            "Para Birimi": "Para_Birimi"
        },
        "SIPARIS": {
            "Sipariş No": "Siparis_No",
            "Müşteri": "Musteri",
            "Sorumlu": "Personel",
            "Tarih": "Tarih",
            "Tutar": "Tutar_Ham",
            "Maliyet": "Maliyet_Ham",
            "Para Birimi": "Para_Birimi"
        },
        "MUSTERI": {
            "Müşteri No": "Musteri_No",
            "Kısa Ad": "Kisa_Ad",
            "Müşteri Adı": "Uzun_Ad",
            "Sorumlu": "Sorumlu"
        },
        "URUN": {
            "Kayıt No": "Kayit_No",
            "Seri No": "Seri_No",
            "Cihaz No": "Cihaz_No",
            "Müşteri": "Musteri",
            "Tarih": "Tarih"
        },
        "PERSONEL": {
            "Ad Soyad": "Ad_Soyad",
            "Departman": "Departman",
            "İşe Giriş": "Ise_Giris",
            "İşten Çıkış": "Isten_Cikis"
        },
        "TATILLER": {
            "Tarih": "Tarih",
            "Açıklama": "Aciklama"
        },
        "SEHIRLER": {
            "SehirAd": "Sehir_Ad",
            "BolgeId": "Bolge_Id",
            "BolgeAd": "Bolge_Ad"
        }
    },
    # Eski liste bazlı yapı geriye dönük uyumluluk için,
    # ancak yeni data_loader COLUMN_MAPPINGS kullanacak.
    "COLUMNS": {
        "TEKLIF": ["Teklif_No", "Musteri", "Personel", "Tarih", "Tutar_Ham", "Maliyet_Ham", "Isaret", "Para_Birimi"],
        "SIPARIS": ["Siparis_No", "Musteri", "Personel", "Tarih", "Tutar_Ham", "Maliyet_Ham", "Para_Birimi"],
        "MUSTERI": ["Musteri_No", "Kisa_Ad", "Uzun_Ad", "Sorumlu"],
        "URUN": ["Kayit_No", "Seri_No", "Cihaz_No", "Musteri", "Tarih"] 
    }
}

# Geriye dönük uyumluluk için alias
EXCEL_CONFIG = SHEETS_CONFIG
