# Merinos Görüntü Analitiği ve Zenginleştirme Kıyaslama Raporu

> **Tarih:** 2026-09-04  
> **Kapsam:** Day 07 - OpenCV Görüntü İşleme ve Analitik Araç Kiti  
> **Lisans:** Özel Lisans — Tüm Hakları Saklıdır (c) 2026 Seydi Eryılmaz  

## 1. Operasyon Performans ve Kalite Tablosu

| Operasyon | Ortalama Gecikme (ms) | Throughput (FPS) | Kontrast Farkı (RMS) | Entropi Değişimi | Keskinlik Değişimi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gaussian Filter (5x5)** | `0.136 ms` | **7370.6 FPS** | `-7.2057` | `-0.2010` | `-16242.64` |
| **Median Filter (k=5)** | `0.971 ms` | **1030.3 FPS** | `-3.2665` | `-1.0029` | `-15477.87` |
| **Bilateral Filter (d=9)** | `13.321 ms` | **75.1 FPS** | `-0.7950` | `-1.7471` | `-1668.14` |
| **Unsharp Mask (strength=1.5)** | `4.77 ms` | **209.7 FPS** | `+3.3950` | `+0.4777` | `+2915.20` |
| **CLAHE Perceptual (LAB L*)** | `1.928 ms` | **518.8 FPS** | `+5.9449` | `+1.6988` | `+127.70` |
| **CLAHE Perceptual (YCrCb Y)** | `1.297 ms` | **770.9 FPS** | `+6.8909` | `+1.6825` | `+147.25` |
| **Global HE Perceptual (LAB L*)** | `1.598 ms` | **625.7 FPS** | `+57.5816` | `+0.4376` | `+2359.19` |
| **Letterbox Resize (512x512)** | `0.528 ms` | **1894.2 FPS** | `+21.8322` | `-0.4599` | `-698.88` |

## 2. Temel Mühendislik Çıkarımları
- **CLAHE (CIELAB L*):** Düşük kontrastlı halı görüntüsünde renk tonlarını bozmadan RMS kontrastını belirgin şekilde artırır.
- **Bilateral Filtre:** İplik dokusu dalgalanmalarını pürüzsüzleştirirken bordür ve madalyon keskinliğini korur (Kenar korumalı yumuşatma).
- **Letterbox Resizing:** Halıların özgün en-boy oranını bozmadan derin öğrenme modelleri için 512x512 kare tensör üretir.
