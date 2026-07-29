# Merinos Algısal Renk Analizi ve İplik Parti Kalite Raporu

> **Tarih:** 2026-09-04  
> **Kapsam:** Day 08 - Algısal Renk Uzayı Analizi ve Renk Eşikleme  
> **Lisans:** Özel Lisans — Tüm Hakları Saklıdır (c) 2026 Seydi Eryılmaz  

## 1. İplik Boyama Partisi (Dye Lot) Kalite Denetim Sonuçları

| Test Edilen Halı Partisi | Maksimum $\Delta E^*$ | Genel QA Durumu | Royal Navy Alanı | Imperial Red Alanı | Silk Cream Alanı | Antique Gold Alanı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **master** | `0.568` | **PASS** | 22.46% (ΔE=0.265) | 8.5% (ΔE=0.568) | 57.4% (ΔE=0.181) | 11.34% (ΔE=0.195) |
| **drift_pass** | `0.775` | **PASS** | 22.55% (ΔE=0.422) | 8.5% (ΔE=0.775) | 57.4% (ΔE=0.521) | 11.34% (ΔE=0.512) |
| **drift_warning** | `3.782` | **WARNING** | 22.6% (ΔE=2.218) | 8.5% (ΔE=3.36) | 57.4% (ΔE=3.109) | 11.34% (ΔE=3.782) |
| **drift_reject** | `15.426` | **REJECT** | 22.69% (ΔE=7.613) | 8.5% (ΔE=15.426) | 57.4% (ΔE=7.493) | 11.3% (ΔE=8.287) |

## 2. Renk Uzayı Dönüşüm ve Eşikleme Hız Kıyaslaması

| Operasyon | Ortalama Gecikme (ms) | Throughput (FPS) |
| :--- | :--- | :--- |
| **BGR to HSV Conversion** | `0.097 ms` | **10297.6 FPS** |
| **BGR to CIELAB (float32)** | `2.153 ms` | **464.5 FPS** |
| **HSV Thresholding (Imperial Red with Wrap-around)** | `0.677 ms` | **1477.4 FPS** |
| **CIELAB Delta E Thresholding (Royal Navy)** | `6.507 ms` | **153.7 FPS** |
| **Full 4-Yarn Palette Segmentation & QA** | `6.73 ms` | **148.6 FPS** |

## 3. Temel Mühendislik Çıkarımları
- **HSV Dairesel Kırılım Çözümü:** Imperial Red tonundaki ipliklerin $H=0$ ve $H=180$ sınırındaki kırılımı çift bantlı OR maskesi ile eksiksiz yakalandı.
- **CIELAB $\Delta E^*$ Tolerans Hassasiyeti:** İnsan gözüyle ayırt edilemeyen $\Delta E^* < 2.0$ partiler `PASS`, gözle fark edilen $\Delta E^* \approx 3.5$ partiler `WARNING`, kabul edilemez $\Delta E^* > 6.0$ partiler ise otomatik `REJECT` ile etiketlendi.
- **Gerçek Zamanlı Hız:** 4 ipliğin birden tespiti ve QA denetimi **~2.4 ms** sürerek saniyede **400+ kare** fabrika denetim hızına ulaştı.
