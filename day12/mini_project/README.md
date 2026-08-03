# Day 12 Mini Proje: Kenar ve Çizgi Tespiti & Jakarlı Halı Bordür Paralellik Analizi

Bu paket, **Merinos Halı Sanayi ve Ticaret A.Ş.** üretim hatlarında (jakarlı dokuma çıkışı, traşlama, apre ve overlok konfeksiyon hatları) halı dış ve iç bordür kenarlarının paralelliğini, doğrusallığını ve ortogonalitesini (90° diklik) gerçek zamanlı analiz eden endüstriyel makine görüşü modülüdür.

---

## 📁 Dizin Yapısı

```
day12/mini_project/
├── configs/
│   └── border_config.json                 # Kenar operatörü ve paralellik tolerans parametreleri
├── fixtures/
│   └── synthetic_carpets/                 # Sentetik referans ve kusurlu halı bordür görselleri
│       ├── carpet_border_clean_parallel.png
│       ├── carpet_border_skewed_angular.png
│       ├── carpet_border_wavy_distortion.png
│       └── carpet_border_broken_edge.png
├── outputs/                               # Üretilen kenar haritaları, overlay ve benchmark raporları
│   ├── edge_line_benchmark.json
│   ├── border_summary.md
│   ├── sample_border_report.json
│   └── sample_border_analysis_overlay.png
├── src/
│   ├── __init__.py
│   ├── models.py                          # Pydantic veri modelleri (LineSegment, BorderEdge, Report)
│   ├── edge_operators.py                  # Sobel, Scharr, Laplacian ve Canny motoru
│   ├── hough_engine.py                    # Olasılıksal Hough Çizgi Dönüşümü ve bordür fit motoru
│   ├── border_analyzer.py                 # Uçtan uca CarpetBorderAnalyzer
│   ├── generator.py                       # Sentetik jakarlı halı bordür fikstür jeneratörü
│   └── cli.py                             # CLI arayüzü
└── tests/
    ├── __init__.py
    └── test_edge_lines.py                 # 10 adet kapsamlı birim ve entegrasyon testi
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Fikstürleri Üretme
```bash
python -m day12.mini_project.src.cli generate-fixtures
```

### 2. Kenar Operatörlerini Çalıştırma ve Görselleştirme
```bash
python -m day12.mini_project.src.cli detect-edges \
    --image day12/mini_project/fixtures/synthetic_carpets/carpet_border_clean_parallel.png \
    --operator ALL \
    --output-dir day12/mini_project/outputs
```

### 3. Halı Bordür Paralellik ve Ortogonalite Analizi
```bash
python -m day12.mini_project.src.cli analyze-borders \
    --image day12/mini_project/fixtures/synthetic_carpets/carpet_border_skewed_angular.png \
    --output-image day12/mini_project/outputs/sample_border_analysis_overlay.png \
    --output-report day12/mini_project/outputs/sample_border_report.json
```

### 4. Benchmark Laboratuvarını Çalıştırma
```bash
python -m day12.mini_project.src.cli benchmark
```

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day12/mini_project/tests/ -v
```
