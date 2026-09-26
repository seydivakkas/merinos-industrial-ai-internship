# Day 39 Mini Project — Model Compression & Edge Deployment (Gereksinim 8)

![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)
![Tests](https://img.shields.io/badge/tests-8%20%2F%208%20passed-brightgreen?style=flat-square)
![Quantization](https://img.shields.io/badge/INT8-74%25%20reduction-blue?style=flat-square)

```
ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır.

YASAKLAR:
  1. Kopyalanamaz, çoğaltılamaz, dağıtılamaz veya yeniden yayınlanamaz.
  2. Ticari veya ticari olmayan hiçbir projede kullanılamaz, değiştirilemez.
  3. Alt lisanslanamaz, satılamaz veya devredilemez.
  4. Tersine mühendislik yapılamaz.

İZİN VERİLEN KULLANIM:
  - GitHub üzerinde görüntüleme ve okuma.
  - Kişisel öğrenim amacıyla kodu inceleme (kopyalamadan).

YAZARIN AÇIK YAZILI İZNİ OLMAKSIZIN HİÇBİR KULLANIM HAKKI TANINMAZ.
İzin talepleri için: GitHub @seydivakkas
```

---

## Proje Özeti

Bu mini proje, Gaziantep Merinos Halı Fabrikası dokuma salonundaki fansız Endüstriyel Panel PC'lerde (Edge IPC) arıza teşhis kılavuzlarına tezgâh başından sıfır ağ bağımlılığıyla mikro-saniye (< 0.1 ms) gecikmeyle erişilmesini sağlayan yerel kenar yapay zekâ (Edge AI) altyapısını içerir.

PyTorch modelleri ONNX formatına ihraç edilmekte, Post-Training Dynamic INT8 Kuantizasyon (PTQ) uygulanarak model boyutları 4 kat (~%74) küçültülmekte ve optimize edilmiş C++ ONNX Runtime oturumları ile çalıştırılmaktadır.

---

## Dizin Yapısı

```
mini_project/
├── configs/
│   └── edge_deployment_config.json                 # IPC kısıtları ve kuantizasyon konfigürasyonu
├── models/
│   ├── bi_encoder_fp32.onnx                        # 793,275 bayt
│   ├── bi_encoder_int8.onnx                        # 208,908 bayt (%73.67 küçülme)
│   ├── cross_encoder_fp32.onnx                     # 859,703 bayt
│   └── cross_encoder_int8.onnx                     # 221,878 bayt (%74.08 küçülme)
├── outputs/
│   ├── edge_profiling_report.json                  # Detaylı JSON benchmark raporu
│   └── edge_performance_dashboard.png              # 300 DPI 4 panelli performans grafiği
├── src/
│   ├── __init__.py
│   ├── models.py                                   # Pydantic DTO ve rapor sınıfları
│   ├── onnx_exporter.py                            # ONNX FP32 ihraç motoru
│   ├── quantizer.py                                # Dynamic INT8 kuantizasyon sınıfı
│   ├── edge_engine.py                              # ONNX Runtime oturum ve C++ motor yöneticisi
│   ├── profiler.py                                 # Gecikme persentilleri ve doğruluk profilleyicisi
│   ├── edge_pipeline.py                            # İki aşamalı Tezgâh Başı Arama Hattı (Bi + Cross)
│   ├── visualizer.py                               # 300 DPI profesyonel dashboard motoru
│   └── cli.py                                      # Komut satırı yönetim arayüzü
└── tests/
    └── test_edge_deployment.py                     # 8 adet birim ve entegrasyon testi
```

---

## Hızlı Başlangıç

### 1. Testleri Koşturma
```bash
pytest day39/mini_project/tests/ -v
```

### 2. Modelleri ONNX FP32 Formatına Derleme
```bash
python -m day39.mini_project.src.cli export
```

### 3. Dinamik INT8 Kuantizasyon Uygulama
```bash
python -m day39.mini_project.src.cli quantize
```

### 4. Edge Benchmark ve 300 DPI Görsel Teşhis Paneli Üretme
```bash
python -m day39.mini_project.src.cli benchmark-edge
```

### 5. Tezgâh Başı Yerel Arama Testi
```bash
python -m day39.mini_project.src.cli edge-search --query "Van de Wiele jakarlı tezgâhta E-401 motor sıcaklığı arızasında ne yapılmalıdır?" --loom-id "TEZGAH-01"
```

---

## Temel Performans Çıktıları

- **Model Boyut Tasarrufu**:
  - Bi-Encoder: 0.757 MB $\rightarrow$ 0.199 MB (%73.67 küçülme, 3.80x sıkıştırma)
  - Cross-Encoder: 0.816 MB $\rightarrow$ 0.212 MB (%74.08 küçülme, 3.86x sıkıştırma)
- **Çıkarım Gecikmesi (INT8)**:
  - Bi-Encoder: 0.056 ms
  - Cross-Encoder: 0.057 ms
- **Kosinüs Sadakati (FP32 vs INT8)**:
  - Bi-Encoder: %95.5
  - Cross-Encoder: %100.0
- **Throughput (INT8, 16 threads)**:
  - Bi-Encoder: 1,284 sorgu/saniye
  - Cross-Encoder: 1,736 sorgu/saniye
