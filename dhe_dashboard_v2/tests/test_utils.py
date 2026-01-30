import unittest
import sys
import os

# Proje kök dizinini path'e ekle (Testlerin modülleri bulabilmesi için)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import (
    clean_money_text, 
    clean_currency_code, 
    tr_upper, 
    tr_lower,
    get_exchange_rate,
    calculate_delta
)

class TestUtils(unittest.TestCase):
    
    def test_clean_money_text(self):
        """Para formatı temizleme fonksiyonunu test eder."""
        self.assertEqual(clean_money_text("1.000,50 TL"), 1000.50)
        self.assertEqual(clean_money_text("500"), 500.0)
        self.assertEqual(clean_money_text(123.45), 123.45)
        self.assertEqual(clean_money_text(""), 0.0)
        self.assertEqual(clean_money_text(None), 0.0)
        self.assertEqual(clean_money_text("Hatalı Veri"), 0.0)

    def test_clean_currency_code(self):
        """Para birimi kodu temizleme fonksiyonunu test eder."""
        self.assertEqual(clean_currency_code("EUR"), "EUR")
        self.assertEqual(clean_currency_code("usd "), "USD")
        self.assertEqual(clean_currency_code(" tl"), "TL")
        self.assertIsNone(clean_currency_code("XYZ"))  # Geçersiz
        self.assertIsNone(clean_currency_code(""))
        self.assertIsNone(clean_currency_code(None))

    def test_turkish_characters(self):
        """Türkçe karakter dönüşümlerini test eder."""
        # Upper
        self.assertEqual(tr_upper("izmir"), "İZMİR")
        self.assertEqual(tr_upper("istanbul"), "İSTANBUL")
        self.assertEqual(tr_upper("çanakkale"), "ÇANAKKALE")
        
        # Lower
        self.assertEqual(tr_lower("IĞDIR"), "ığdır")
        self.assertEqual(tr_lower("İSTANBUL"), "istanbul")
        self.assertEqual(tr_lower("ÇORUM"), "çorum")

    def test_calculate_delta(self):
        """Yüzdesel değişim hesaplamasını test eder."""
        self.assertEqual(calculate_delta(150, 100), 50.0)   # %50 Artış
        self.assertEqual(calculate_delta(50, 100), -50.0)   # %50 Azalış
        self.assertEqual(calculate_delta(100, 100), 0.0)    # Değişim yok
        
        # Sıfıra bölme kontrolü
        self.assertEqual(calculate_delta(100, 0), 100.0)    # Önceki 0 ise %100 kabul et
        self.assertEqual(calculate_delta(0, 0), 0.0)

    def test_get_exchange_rate(self):
        """Döviz kuru getirme fonksiyonunu test eder."""
        # Constants dosyasındaki veriye bağımlı olduğu için 
        # sadece fonksiyonun çökmediğini ve mantıklı tip döndürdüğünü test ediyoruz.
        rate = get_exchange_rate("USD", 2024)
        self.assertIsInstance(rate, float)
        self.assertGreaterEqual(rate, 0.0)
        
        # Geçersiz durumlar
        self.assertEqual(get_exchange_rate("XYZ", 2024), 0.0)
        self.assertEqual(get_exchange_rate(None, 2024), 0.0)

if __name__ == '__main__':
    unittest.main()
