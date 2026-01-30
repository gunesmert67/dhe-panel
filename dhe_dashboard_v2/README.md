# DHE Endüstriyel Dashboard (v2.4.0)

DHE Endüstriyel yönetim, finans ve saha operasyon takibi için geliştirilmiş kapsamlı Streamlit uygulaması.

## 📂 Proje Yapısı

```
dhe_dashboard_v2/
├── app.py                    # Ana uygulama giriş noktası
├── dhe_baslat.bat            # Windows başlatma scripti
├── loophole_baslat.bat       # Uzaktan erişim scripti
├── requirements.txt          # Python bağımlılıkları
│
├── core/                     # Çekirdek modüller
│   ├── data_loader.py        # Veri yükleme ve caching
│   ├── gsheets.py            # Google Sheets API
│   ├── transforms.py         # Veri dönüşümleri
│   ├── bellis_loader.py      # Bellis makine verileri
│   ├── validator.py          # Veri doğrulama
│   ├── utils.py              # Yardımcı fonksiyonlar
│   └── date_utils.py         # Tarih işlemleri
│
├── views/                    # Sayfa görünümleri
│   ├── landing_page.py       # Ana Sayfa
│   ├── integrated_dashboard.py # Servis Performansı
│   ├── field_ops.py          # Saha Ekibi
│   ├── crm.py                # CRM Analizi
│   ├── customers.py          # Müşteri Yönetimi
│   ├── islem_ozeti.py        # İşlem Özeti
│   └── bellis.py             # Bellis Makine Verileri
│
├── components/               # UI bileşenleri
│   ├── cards.py              # KPI kartları
│   ├── charts.py             # Grafik wrapperları
│   ├── dashboard_*.py        # Dashboard bileşenleri
│   ├── field_*.py            # Saha bileşenleri
│   ├── layout.py             # Sayfa düzeni
│   └── styles.py             # CSS stilleri
│
├── config/                   # Ayarlar
│   ├── constants.py          # Sabit değişkenler
│   └── city_coordinates.py   # Şehir koordinatları
│
├── data/                     # Yerel veri dosyaları
└── tests/                    # Test dosyaları
    ├── test_data_loader.py
    ├── test_date_utils.py
    └── test_utils.py
```

## 🚀 Kurulum ve Çalıştırma

1. Python 3.10+ kurulu olduğundan emin olun.

2. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```
   veya `dhe_baslat.bat` dosyasına çift tıklayın.

## 🔑 Önemli Notlar

- **Veri Kaynağı**: "DHE_Data" ve "2025 SERVİS PROGRAMI" Google Sheets dosyaları
- **Yetkilendirme**: `service_account.json` dosyası `.streamlit/` veya kök dizinde bulunmalıdır
- **Cache**: Veriler 1 saat süreyle önbellekte tutulur

## 📊 Sayfalar

| Sayfa | Açıklama |
|-------|----------|
| **Ana Sayfa** | Genel özet ve navigasyon |
| **Servis Performansı** | Finansal KPI'lar, teklif/sipariş analizi |
| **Saha Ekibi** | Teknisyen takibi, verimlilik analizi |
| **CRM Analizi** | Müşteri segmentasyonu, risk takibi |
| **Müşteri Yönetimi** | Müşteri bazlı detaylı geçmiş |
| **İşlem Özeti** | Özel müşteri raporları |
| **Bellis** | Makine/IoT verileri |

---
*DHE Yazılım Ekibi | 2026*
