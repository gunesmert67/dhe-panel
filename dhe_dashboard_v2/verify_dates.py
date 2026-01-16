
from datetime import date
from core.date_utils import calculate_effective_workdays

def test_effectiveness():
    print("Test 1: Normal Ay")
    # 2024 Ekim: 31 Gün. Hafta sonu: 8 gün. 29 Ekim tatil.
    # Beklenen: 31 - 8 - 1 = 22 gün (Yaklaşık, tatil setine göre değişir)
    cnt = calculate_effective_workdays(2025, 1, start_date=date(2024, 1, 1))
    print(f"2025 Ocak Tam Ay: {cnt}")

    print("\nTest 2: Ay Ortası Giriş")
    # 15 Ocak 2025'te giren biri
    cnt2 = calculate_effective_workdays(2025, 1, start_date=date(2025, 1, 15))
    print(f"15 Ocak Giriş: {cnt2}")

    print("\nTest 3: Ay Ortası Çıkış")
    # 10 Ocak 2025'te çıkan biri
    cnt3 = calculate_effective_workdays(2025, 1, start_date=date(2024, 1, 1), end_date=date(2025, 1, 10))
    print(f"10 Ocak Çıkış: {cnt3}")
    
    print("\nTest 4: Kayıp (None) Çıkış Tarihi")
    cnt4 = calculate_effective_workdays(2025, 1, start_date=date(2024, 1, 1), end_date=None)
    print(f"Çıkış Yok (Hala Çalışıyor): {cnt4}")

if __name__ == "__main__":
    test_effectiveness()
