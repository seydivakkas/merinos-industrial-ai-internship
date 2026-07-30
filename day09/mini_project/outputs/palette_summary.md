# Day 09: Dominant Renk Paleti ve CIEDE2000 Benchmark Raporu

## 1. K-Means Alt-Örnekleme Performans Kıyaslaması (512x512)

| Örnekleme Boyutu | Ortalama Süre (ms) | Throughput (FPS) | İnertia |
| :--- | :--- | :--- | :--- |
| 5,000 | 592.2 ms | 1.7 FPS | 33580.75 |
| 15,000 | 49.13 ms | 20.4 FPS | 100244.67 |
| 50,000 | 131.68 ms | 7.6 FPS | 332308.15 |
| Full (262,144) | 336.06 ms | 3.0 FPS | 1734056.83 |

## 2. Metrik Hesaplama Hızı (10,000 Renk Çifti)

- **CIE 1976 (Öklid):** 0.33 ms (30,084,235 çift/sn)
- **CIEDE2000:** 4.76 ms (2,100,840 çift/sn)

## 3. Sharma et al. (2005) Standart Doğrulama Çiftleri

| Çift | Hesaplanan | Beklenen | Mutlak Hata | Durum |
| :--- | :--- | :--- | :--- | :--- |
| Çift 1 | 2.0425 | 2.0425 | 4e-05 | PASSED |
| Çift 2 | 2.8615 | 2.8615 | 1e-05 | PASSED |
| Çift 3 | 1.6982 | 1.6982 | 7e-06 | PASSED |
| Çift 4 | 2.2549 | 2.2549 | 3e-05 | PASSED |
| Çift 5 | 1.1271 | 1.1271 | 1.4e-05 | PASSED |
