# Day 13 Mini Proje: Klasik Segmentasyon Kıyaslama Laboratuvarı (Otsu, Watershed, GrabCut)

Bu paket, **Merinos Halı Sanayi ve Ticaret A.Ş.** üretim ve kalite denetim hatlarında (jakarlı dokuma tezgâhı çıkışı, apre, motif kontrolü ve konfeksiyon) halı desen motiflerinin zemin kumaşından piksel seviyesinde ayrıştırılması amacıyla geliştirilmiş endüstriyel makine görüşü modülüdür.

Sistem, **Otsu Global & Multi-Otsu Eşikleme**, **İşaretçi Kontrollü Watershed (Havza)** ve **GrabCut (GMM Tabanlı Grafik Kesme)** algoritmalarını hem işlem hızı ($FPS, ms$) hem de piksel doğruluğu ($IoU, Dice, BF-Score$) yönünden kıyaslar.

---

## 📁 Dizin Yapısı

```
day13/mini_project/
├── configs/
│   └── segmentation_config.json                 # Otsu, Watershed ve GrabCut hiperparametreleri
├── fixtures/
│   └── synthetic_carpets/                       # Sentetik halılar ve piksel-örtüşümlü GT maskeleri
│       ├── carpet_medallion_classic.png
│       ├── carpet_medallion_classic_gt_mask.png
│       ├── carpet_medallion_classic_gt_multiclass.png
│       ├── carpet_geometric_modern.png
│       └── carpet_geometric_modern_gt_mask.png
├── outputs/                                     # Çıktı maskeleri, görsel paneller ve benchmark raporları
│       ├── benchmark_comparison_grid.png
│       ├── carpet_medallion_classic_segmentation_comparison_grid.png
│       ├── carpet_medallion_classic_otsu_mask.png
│       ├── carpet_medallion_classic_watershed_mask.png
│       ├── carpet_medallion_classic_grabcut_mask.png
│       ├── segmentation_benchmark.json
│       └── segmentation_summary.md
├── src/
│   ├── __init__.py
│   ├── models.py                                # Pydantic modelleri (Metrics, Benchmark, Report)
│   ├── otsu_segmenter.py                        # Otsu global ve 3 seviyeli Multi-Otsu motoru
│   ├── watershed_segmenter.py                   # Mesafe dönüşümü tohumlamalı Watershed motoru
│   ├── grabcut_segmenter.py                     # Bounding-box ve tohum rafineli GrabCut motoru
│   ├── evaluator.py                             # IoU, Dice, Pixel Accuracy, Boundary F1 motoru
│   ├── generator.py                             # Sentetik jakarlı halı ve GT maske üretici
│   ├── benchmark.py                             # Hız vs doğruluk kıyaslama laboratuvarı motoru
│   └── cli.py                                   # Komut satırı arayüzü (CLI)
└── tests/
    ├── __init__.py
    └── test_segmentation.py                     # 10 adet kapsamlı birim ve entegrasyon testi
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Halı ve Ground Truth Fikstürlerini Üretme
```bash
python -m day13.mini_project.src.cli generate-fixtures
```

### 2. Segmentasyon Çalıştırma ve Maskeleri Kaydetme
```bash
python -m day13.mini_project.src.cli segment \
    --image day13/mini_project/fixtures/synthetic_carpets/carpet_medallion_classic.png \
    --method ALL \
    --gt-mask day13/mini_project/fixtures/synthetic_carpets/carpet_medallion_classic_gt_mask.png
```

### 3. Tahmin Maskesini Ground Truth ile Değerlendirme
```bash
python -m day13.mini_project.src.cli evaluate \
    --pred-mask day13/mini_project/outputs/carpet_medallion_classic_otsu_mask.png \
    --gt-mask day13/mini_project/fixtures/synthetic_carpets/carpet_medallion_classic_gt_mask.png
```

### 4. Algoritma Kıyaslama Laboratuvarını Çalıştırma
```bash
python -m day13.mini_project.src.cli benchmark
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
