"""
Türkiye Şehir Koordinatları
===========================
81 il için enlem/boylam bilgileri (WGS84).
Plotly scatter_mapbox için kullanılır.
"""

# Format: "ŞEHİR_ADI": (ENLEM, BOYLAM)
CITY_COORDINATES = {
    "ADANA": (37.0, 35.3213),
    "ADIYAMAN": (37.7648, 38.2786),
    "AFYON": (38.7507, 30.5567),
    "AFYONKARAHISAR": (38.7507, 30.5567),
    "AĞRI": (39.7191, 43.0503),
    "AKSARAY": (38.3687, 34.0370),
    "AMASYA": (40.6499, 35.8353),
    "ANKARA": (39.9334, 32.8597),
    "ANTALYA": (36.8969, 30.7133),
    "ARDAHAN": (41.1105, 42.7022),
    "ARTVİN": (41.1828, 41.8183),
    "AYDIN": (37.8560, 27.8416),
    "BALIKESİR": (39.6484, 27.8826),
    "BARTIN": (41.6344, 32.3375),
    "BATMAN": (37.8812, 41.1351),
    "BAYBURT": (40.2552, 40.2249),
    "BİLECİK": (40.0567, 30.0665),
    "BİNGÖL": (38.8854, 40.4966),
    "BİTLİS": (38.4004, 42.1095),
    "BOLU": (40.7391, 31.6089),
    "BURDUR": (37.7203, 30.2900),
    "BURSA": (40.1885, 29.0610),
    "ÇANAKKALE": (40.1553, 26.4142),
    "ÇANKIRI": (40.6013, 33.6134),
    "ÇORUM": (40.5506, 34.9556),
    "DENİZLİ": (37.7765, 29.0864),
    "DİYARBAKIR": (37.9144, 40.2306),
    "DÜZCE": (40.8438, 31.1565),
    "EDİRNE": (41.6818, 26.5623),
    "ELAZIĞ": (38.6810, 39.2264),
    "ERZİNCAN": (39.7500, 39.5000),
    "ERZURUM": (39.9000, 41.2700),
    "ESKİŞEHİR": (39.7767, 30.5206),
    "GAZİANTEP": (37.0662, 37.3833),
    "GİRESUN": (40.9128, 38.3895),
    "GÜMÜŞHANE": (40.4386, 39.5086),
    "HAKKARİ": (37.5833, 43.7333),
    "HATAY": (36.4018, 36.3498),
    "IĞDIR": (39.9237, 44.0450),
    "ISPARTA": (37.7648, 30.5566),
    "İSTANBUL": (41.0082, 28.9784),
    "İZMİR": (38.4237, 27.1428),
    "KAHRAMANMARAŞ": (37.5858, 36.9371),
    "KARABÜK": (41.2061, 32.6204),
    "KARAMAN": (37.1811, 33.2150),
    "KARS": (40.6167, 43.1000),
    "KASTAMONU": (41.3887, 33.7827),
    "KAYSERİ": (38.7312, 35.4787),
    "KIRIKKALE": (39.8468, 33.5153),
    "KIRKLARELİ": (41.7333, 27.2167),
    "KIRŞEHİR": (39.1425, 34.1709),
    "KİLİS": (36.7184, 37.1212),
    "KOCAELİ": (40.8533, 29.8815),
    "KONYA": (37.8746, 32.4932),
    "KÜTAHYA": (39.4167, 29.9833),
    "MALATYA": (38.3552, 38.3095),
    "MANİSA": (38.6191, 27.4289),
    "MARDİN": (37.3212, 40.7245),
    "MERSİN": (36.8121, 34.6415),
    "MUĞLA": (37.2153, 28.3636),
    "MUŞ": (38.9462, 41.7539),
    "NEVŞEHİR": (38.6939, 34.6857),
    "NİĞDE": (37.9667, 34.6833),
    "ORDU": (40.9839, 37.8764),
    "OSMANİYE": (37.0742, 36.2478),
    "RİZE": (41.0201, 40.5234),
    "SAKARYA": (40.7569, 30.3781),
    "SAMSUN": (41.2867, 36.33),
    "SİİRT": (37.9333, 41.95),
    "SİNOP": (42.0231, 35.1531),
    "SİVAS": (39.7477, 37.0179),
    "ŞANLIURFA": (37.1591, 38.7969),
    "ŞIRNAK": (37.5164, 42.4611),
    "TEKİRDAĞ": (40.9833, 27.5167),
    "TOKAT": (40.3167, 36.5500),
    "TRABZON": (41.0015, 39.7178),
    "TUNCELİ": (39.1079, 39.5401),
    "UŞAK": (38.6823, 29.4082),
    "VAN": (38.4891, 43.4089),
    "YALOVA": (40.6500, 29.2667),
    "YOZGAT": (39.8181, 34.8147),
    "ZONGULDAK": (41.4564, 31.7987),

    # KIBRIS
    "LEFKOŞA": (35.1856, 33.3823),
    "GİRNE": (35.3353, 33.3173),
    "GAZİMAĞUSA": (35.1250, 33.9500),
    "MAGUSA": (35.1250, 33.9500),

    # IRAK
    "BAĞDAT": (33.3152, 44.3661),
    "ERBİL": (36.1901, 44.0091),
    "SÜLEYMANİYE": (35.5575, 45.4308),
    "MUSUL": (36.3350, 43.1189),
    "KERKÜK": (35.4667, 44.3750),
    "DUHOK": (36.8667, 42.9889),
    "BASRA": (30.5081, 47.7835),

    # GENEL ÜLKE TANIMLARI (Merkezleri)
    "AZERBAYCAN": (40.4093, 49.8671), # Bakü
    "BAKU": (40.4093, 49.8671),
    "BAKÜ": (40.4093, 49.8671),
    "IRAK": (33.3152, 44.3661),       # Bağdat (Merkez kabul edildi)
    "KIBRIS": (35.1856, 33.3823),     # Lefkoşa (Merkez kabul edildi)
}

# Türkiye 7 Coğrafi Bölgesi
TURKEY_REGIONS = {
    1: "Marmara",
    2: "Ege",
    3: "Akdeniz",
    4: "İç Anadolu",
    5: "Karadeniz",
    6: "Doğu Anadolu",
    7: "Güneydoğu Anadolu"
}

# Bölge Renkleri (Harita için)
REGION_COLORS = {
    1: "#3B82F6",  # Marmara - Mavi
    2: "#10B981",  # Ege - Yeşil
    3: "#F59E0B",  # Akdeniz - Turuncu
    4: "#8B5CF6",  # İç Anadolu - Mor
    5: "#06B6D4",  # Karadeniz - Camgöbeği
    6: "#EF4444",  # Doğu Anadolu - Kırmızı
    7: "#EC4899",  # Güneydoğu - Pembe
}

# Servis Sağlayıcı Renkleri
SERVICE_PROVIDER_COLORS = {
    "DHE": "#C4121F",       # DHE Kırmızısı
    "CER": "#3B82F6",       # Mavi
    "ERT Compressor": "#10B981",  # Yeşil
    "Out of service": "#9CA3B8",  # Gri
    "No information": "#D1D5DB",  # Açık gri
}
