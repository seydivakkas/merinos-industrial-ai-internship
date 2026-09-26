# OpenCV Görüntü İşleme ve Analitik Araç Kiti (Mini Proje)

> **Modül:** Day 09 Mini Project  
> **Konu:** OpenCV ile Endüstriyel Görüntü Ön İşleme, Gürültü Filtreleme, CLAHE Kontrast İyileştirme ve En-Boy Oranı Koruyan Letterbox Yeniden Boyutlandırma  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 📌 Genel Bakış

Merinos halı üretim hatlarındaki optik muayene kameralarından gelen ham görsel verilerin OpenCV kütüphanesi ile okunması, BGR kanal mimarisinin RGB/Gri seviyeye dönüştürülmesi, en-boy oranını koruyarak standart çözünürlüğe ölçeklenmesi, Gauss filtresi ile sensör gürültüsünün bastırılması ve CLAHE (Contrast Limited Adaptive Histogram Equalization) ile yerel kontrastın iyileştirilmesini sağlayan modüler bir ön işleme ve görüntü analitiği araç kitidir.

Bu mini proje:
1. **Güvenli Görüntü Giriş/Çıkış (`ImageIOValidator`):** Türkçe veya boşluklu dosya yollarını Windows ortamında hatasız okumak için `cv2.imdecode` ve `np.fromfile` tabanlı Unicode güvenli I/O sağlar.
2. **Kanal Mimarisi ve Renk Dönüşümleri (`ColorSpaceConverter`):** BGR, RGB, Gri seviye, CIELAB ve HSV dönüşümleri ile kanal istatistiklerini hesaplar.
3. **Endüstriyel Filtreleme Boru Hattı (`IndustrialFilterPipeline`):** Gauss filtresi, tuz-biber gürültüsü temizleme için Medyan filtre, kenar korumalı yumuşatma için Bilateral filtre ve keskinleştirme için Unsharp Masking sunar.
4. **Perseptüel Kontrast İyileştirme (`HistogramEqualizer`):** Renk tonu bozulmalarını önlemek için CIELAB uzayının $L^*$ parlaklık kanalı veya YCrCb uzayının $Y$ kanalı üzerinde CLAHE ve Global Histogram Eşitleme uygular.
5. **En-Boy Oranı Koruyan Yeniden Boyutlandırma (`AspectPreservingResizer`):** Halının özgün en-boy oranını bozmadan derin öğrenme modelleri için siyah dolgulu (letterbox) kare tensörler üretir.
6. **Görüntü Analitiği ve Profilleme (`ImageAnalyticsEngine`):** Shannon entropisi, RMS kontrastı, dinamik aralık ve Laplacian varyansı ile keskinlik ölçümü yapar.

---

## 📁 Dizin Yapısı

```
day09/mini_project/
├── configs/
│   └── toolkit_config.json
├── fixtures/
│   └── synthetic_carpets/
│       ├── carpet_normal.png
│       ├── carpet_low_contrast.png
│       ├── carpet_noisy.png
│       └── carpet_uneven_illumination.png
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── color_spaces.py
│   ├── equalization.py
│   ├── filters.py
│   ├── generator.py
│   ├── image_preprocessor.py
│   ├── io_validator.py
│   ├── resizer.py
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── test_image_preprocessor.py
│   └── test_toolkit.py
└── outputs/
    ├── sample_analysis_report.json
    ├── image_enhancement_benchmark.json
    └── toolkit_summary.md
```

---

## 🚀 CLI Kullanımı

### 1. Görüntü Analizi ve İstatistiksel Profil
```bash
python -m day09.mini_project.src.cli analyze --input fixtures/synthetic_carpets/carpet_normal.png
```

### 2. CLAHE ile Kontrast İyileştirme
```bash
python -m day09.mini_project.src.cli enhance --input fixtures/synthetic_carpets/carpet_low_contrast.png --method clahe_lab --output outputs/enhanced.png
```

### 3. Letterbox Yeniden Boyutlandırma
```bash
python -m day09.mini_project.src.cli resize --input fixtures/synthetic_carpets/carpet_normal.png --size 512 512 --output outputs/resized.png
```

### 4. Uçtan Uca Kıyaslama Benchmark'ı
```bash
python -m day09.mini_project.src.cli benchmark
```

---

## 🧪 Birim Testleri

```bash
python -m pytest day09/mini_project/tests/ -v
```

11 birim testi şunları doğrular:
1. `test_image_preprocessing_pipeline`: Pipeline uçtan uca boyut ve tür doğrulaması.
2. `test_image_io_unicode_safe_read_write`: Unicode güvenli dosya okuma ve yazma.
3. `test_image_io_metadata_extraction`: Görüntü meta verisi çıkarımı.
4. `test_color_space_conversions`: BGR, RGB, GRAY, LAB dönüşümleri ve kanal istatistikleri.
5. `test_aspect_preserving_resizer_letterbox`: En-boy oranı korumalı letterbox ölçekleme.
6. `test_median_filter_salt_pepper_removal`: Tuz-biber gürültüsü temizleme.
7. `test_bilateral_filter_edge_preservation`: Kenar korumalı yumuşatma.
8. `test_unsharp_masking_laplacian_variance`: Laplacian keskinlik artışı.
9. `test_clahe_vs_global_equalization_luminance`: CLAHE ve yerel histogram eşitleme.
10. `test_image_analytics_entropy_and_contrast`: RMS kontrastı ve Shannon entropisi analizi.
11. `test_cli_pipeline_execution_and_reports`: CLI rapor ve benchmark üretimi.
