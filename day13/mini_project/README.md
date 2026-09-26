# Day 13 Mini Proje: Morfolojik İşlemler, Kenar ve Çizgi Tespiti & Halı Bordür Analitiği

Bu paket, **Merinos Halı Sanayi ve Ticaret A.Ş.** üretim hatlarında (jakarlı dokuma çıkışı, traşlama, apre, overlok ve kalite muayene istasyonları) kumaş yüzeyindeki mikro dokuma kusurlarını (iplik kopuşu, delik/patlak, slub/düğüm, yağ lekesi) matematiksel morfoloji ile tespit etmek; aynı zamanda Sobel, Scharr, Laplacian, Canny kenar filtreleri ve Olasılıksal Hough Çizgi Dönüşümü (`HoughLinesP`) ile halı dış ve iç bordür kenarlarının paralelliğini, doğrusallığını ve ortogonalitesini (90° diklik) analiz etmek üzere geliştirilmiş endüstriyel makine görüşü modülüdür.

---

## 📁 Dizin Yapısı

```
day13/mini_project/
├── configs/
│   ├── border_config.json                 # Kenar operatörü ve paralellik tolerans parametreleri
│   └── defect_config.json                 # Morfolojik kusur eşikleri ve toleranslar
├── fixtures/
│   ├── borders/                           # Sentetik bordür ve paralellik test görselleri
│   │   ├── carpet_border_broken_edge.png
│   │   ├── carpet_border_clean_parallel.png
│   │   ├── carpet_border_skewed_angular.png
│   │   └── carpet_border_wavy_distortion.png
│   └── defects/                           # Sentetik kumaş dokusu ve fiziksel kusur görselleri
│       ├── carpet_clean_reference.png
│       ├── carpet_defect_hole_puncture.png
│       ├── carpet_defect_oil_slub.png
│       └── carpet_defect_yarn_break.png
├── outputs/                               # Üretilen kenar haritaları, maskeler ve raporlar
├── src/
│   ├── __init__.py
│   ├── border_analyzer.py                 # Uçtan uca CarpetBorderAnalyzer motoru
│   ├── border_cli.py                      # Bordür analizi CLI
│   ├── border_generator.py                # Sentetik bordür fikstür jeneratörü
│   ├── border_models.py                   # LineSegment, BorderEdge, BorderParallelismReport
│   ├── cli.py                             # Birleşik komut satırı arayüzü
│   ├── defect_cli.py                      # Dokuma kusurları CLI
│   ├── defect_detector.py                 # CarpetDefectDetector (Top-Hat & Morfoloji)
│   ├── defect_generator.py                # Kumaş dokusu ve sentetik kusur enjektörü
│   ├── defect_models.py                   # DetectedDefect, MorphologyInspectionReport
│   ├── edge_operators.py                  # Sobel, Scharr, Laplacian ve Canny motoru
│   ├── generator.py                       # Birleşik fikstür jeneratörü
│   ├── hough_engine.py                    # Olasılıksal Hough ve bordür regrese motoru
│   ├── models.py                          # Birleşik Pydantic veri modelleri
│   ├── morphology_engine.py               # Erode, Dilate, Open, Close, Top-Hat motoru
│   └── morphology_lines.py                # MorphologyEdgeEngine sınıfı
└── tests/
    ├── __init__.py
    ├── test_edge_lines.py                 # 10 adet kenar ve bordür testi
    ├── test_morphology_defects.py         # 10 adet morfolojik kusur testi
    └── test_morphology_lines.py           # 2 adet temel morfoloji ve çizgi testi
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Bordür Fikstürlerini Üretme
```bash
python -m day13.mini_project.src.cli generate-fixtures
```

### 2. Kenar Operatörlerini Çalıştırma (Canny, Sobel vb.)
```bash
python -m day13.mini_project.src.cli detect-edges \
    --image day13/mini_project/fixtures/borders/carpet_border_clean_parallel.png \
    --operator ALL \
    --output-dir day13/mini_project/outputs
```

### 3. Halı Bordür Paralellik ve Ortogonalite Analizi
```bash
python -m day13.mini_project.src.cli analyze-borders \
    --image day13/mini_project/fixtures/borders/carpet_border_skewed_angular.png \
    --output-image day13/mini_project/outputs/sample_border_overlay.png \
    --output-report day13/mini_project/outputs/sample_border_report.json
```

### 4. Morfolojik Dokuma Kusuru Muayenesi
```bash
python -m day13.mini_project.src.defect_cli inspect \
    --input day13/mini_project/fixtures/defects/carpet_defect_hole_puncture.png \
    --output-dir day13/mini_project/outputs
```

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day13/mini_project/tests/ -v
```

---

## 🔒 Lisans

Özel Lisans — Tüm Hakları Saklıdır.  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
