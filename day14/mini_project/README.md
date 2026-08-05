# Day 14 Mini Proje: Geleneksel Öznitelik Çıkarımı ve Jakarlı Halı Desen Sınıflandırması

Bu paket, **Merinos Halı Sanayi ve Ticaret A.Ş.** üretim, tasarım arşivleme ve kalite güvence hatlarında jakarlı halı desenlerinin (Madalyon Klasik, Geometrik Modern, Geleneksel Çiçekli, Vintage Bukle) otomatik olarak sınıflandırılması, desen taklit denetimi ve katalog içi benzerlik sorgulaması (Visual Retrieval) amacıyla geliştirilmiş klasik bilgisayarlı görü öznitelik çıkarım modülüdür.

Sistem; **ORB** ve **SIFT** yerel anahtar nokta tanımlayıcılarını, **GLCM (Gri Seviye Eş-Oluşum Matrisi)** Haralick doku analizini ve **3D HSV Renk Histogramlarını** çok modlu bir öznitelik füzyon mimarisinde birleştirir.

---

## 📁 Dizin Yapısı

```
day14/mini_project/
├── configs/
│   └── feature_config.json                 # ORB, SIFT, GLCM ve Renk Histogramı hiperparametreleri
├── fixtures/
│   └── synthetic_carpets/                 # 4 desen sınıfında sentetik jakarlı halı görselleri
│       ├── carpet_class_medallion_classic.png
│       ├── carpet_class_geometric_modern.png
│       ├── carpet_class_floral_traditional.png
│       └── carpet_class_vintage_distressed.png
├── outputs/                               # Üretilen öznitelik haritaları, görsel paneller ve benchmark raporları
│   ├── retrieval_benchmark.json
│   ├── feature_summary_panel.png
│   ├── feature_summary.md
│   ├── sample_medallion_features.json
│   └── match_medallion_vs_floral.png
├── src/
│   ├── __init__.py
│   ├── models.py                          # Pydantic veri modelleri (KeypointStats, GLCMFeatures, FusedVector vb.)
│   ├── keypoint_engine.py                 # ORB ve SIFT çıkarıcı, Lowe ratio testi ve RANSAC eşleştirici
│   ├── glcm_engine.py                     # GLCM doku matrisi ve Haralick öznitelik çıkarıcı
│   ├── color_histogram.py                 # 3D HSV çok kanallı normalize renk histogramı motoru
│   ├── feature_fusion.py                  # Doku + Renk + Anahtar Nokta füzyonu ve k-NN sınıflandırıcı
│   ├── generator.py                       # 4 Merinos desen sınıfında sentetik halı jeneratörü
│   ├── benchmark.py                       # Hız (FPS / ms) ve sınıflandırma başarısı kıyaslama motoru
│   └── cli.py                             # Komut satırı arayüzü (CLI)
└── tests/
    ├── __init__.py
    └── test_features.py                   # 10 adet kapsamlı birim ve entegrasyon testi
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Halı Desen Fikstürlerini Üretme
```bash
python -m day14.mini_project.src.cli generate-fixtures
```

### 2. Tek Bir Halıdan Tüm Öznitelikleri Çıkarma
```bash
python -m day14.mini_project.src.cli extract \
    --image day14/mini_project/fixtures/synthetic_carpets/carpet_class_medallion_classic.png \
    --keypoint-type ORB \
    --output-json day14/mini_project/outputs/sample_medallion_features.json
```

### 3. İki Halı Arasında Anahtar Nokta Eşleştirme (ORB veya SIFT)
```bash
python -m day14.mini_project.src.cli match \
    --image1 day14/mini_project/fixtures/synthetic_carpets/carpet_class_medallion_classic.png \
    --image2 day14/mini_project/fixtures/synthetic_carpets/carpet_class_floral_traditional.png \
    --method ORB \
    --output-vis day14/mini_project/outputs/match_medallion_vs_floral.png
```

### 4. Halı Desenini Sınıflandırma ve Katalogda Benzerlerini Bulma
```bash
python -m day14.mini_project.src.cli classify \
    --query day14/mini_project/fixtures/synthetic_carpets/carpet_class_geometric_modern.png \
    --top-k 3
```

### 5. Kapsamlı Hız ve Başarı Benchmark Testi
```bash
python -m day14.mini_project.src.cli benchmark
```

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day14/mini_project/tests/ -v
```

---

## 🔒 Lisans

Özel Lisans — Tüm Hakları Saklıdır.  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
