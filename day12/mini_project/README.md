# Day 12 Mini Proje: Halı Perspektif Düzeltme ve Homografi Motoru

Bu paket, **Merinos Halı Sanayi ve Ticaret A.Ş.** üretim ve kalite muayene hatlarında konveyör veya kontrol masası kameralarının montaj açılarından kaynaklanan perspektif bozulmalarını (trapezoidal / projective distortion) gidermek, dört köşe koordinatını sıralamak ve görüntüyü kuşbakışı (top-down / orthorectified) düzleme dönüştürmek için tasarlanmış endüstriyel bilgisayarlı görü modülüdür.

---

## 📁 Dizin Yapısı

```
day12/mini_project/
├── configs/
│   └── rectification_config.json          # Rektifikasyon ve QA tolerans parametreleri
├── fixtures/
│   └── synthetic_carpets/                 # Sentetik açılı halı fikstürleri
│       ├── carpet_skewed_oblique_25deg.png
│       ├── carpet_skewed_conveyor_35deg.png
│       └── carpet_skewed_severe_45deg.png
├── outputs/                               # Rektifiye edilmiş görüntüler ve raporlar
├── src/
│   ├── __init__.py
│   ├── models.py                          # Point2D, QuadCorners, HomographyResult, RectificationReport
│   ├── corner_detector.py                 # Köşe tespiti ve [TL, TR, BR, BL] sıralama algoritması
│   ├── homography.py                      # 3x3 homografi matris hesaplama ve nokta projeksiyonu
│   ├── homography_rectifier.py            # Hızlı HomographyRectifier sınıfı
│   ├── rectifier.py                       # CarpetPerspectiveRectifier pipeline motoru
│   ├── generator.py                       # Sentetik açılı halı fikstür jeneratörü
│   └── cli.py                             # CLI arayüzü
└── tests/
    ├── __init__.py
    ├── test_corner_detector.py            # Köşe tespit ve sıralama testleri
    ├── test_homography.py                 # Homografi ve nokta izdüşüm testleri
    ├── test_homography_cli.py             # CLI çalışma testleri
    ├── test_homography_rectifier.py       # Temel rektifikasyon testleri
    ├── test_order_points.py               # Sıralama matematik testleri
    └── test_rectification.py              # Uçtan uca rektifikasyon entegrasyon testleri
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Fikstürleri Üretme
```bash
python -m day12.mini_project.src.cli generate-fixtures
```

### 2. Perspektif Düzeltme (Adaptive Mod)
```bash
python -m day12.mini_project.src.cli rectify \
    --input day12/mini_project/fixtures/synthetic_carpets/carpet_skewed_conveyor_35deg.png \
    --mode adaptive \
    --output day12/mini_project/outputs/rectified_conveyor.png \
    --report day12/mini_project/outputs/rectified_conveyor_report.json
```

### 3. Standart Katalog Oranına Göre Rektifikasyon (160x230)
```bash
python -m day12.mini_project.src.cli rectify \
    --input day12/mini_project/fixtures/synthetic_carpets/carpet_skewed_oblique_25deg.png \
    --mode standard \
    --standard-ratio 160x230 \
    --output day12/mini_project/outputs/rectified_160x230.png
```

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day12/mini_project/tests/ -v
```
