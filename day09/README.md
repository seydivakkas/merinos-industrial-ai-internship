# Day 09 — OpenCV ile Görüntü İşleme Temelleri

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** OpenCV ile Görüntü İşleme Temelleri (Yaprak 17 & 18)

## Goal
Bu günün amacı, Merinos halı üretim hatlarındaki optik muayene kameralarından gelen ham görsel verilerin OpenCV kütüphanesi ile okunması, BGR kanal mimarisinin RGB/Gri seviyeye dönüştürülmesi, en-boy oranını koruyarak standart çözünürlüğe ölçeklenmesi, Gauss filtresi ile sensör gürültüsünün bastırılması ve CLAHE (Contrast Limited Adaptive Histogram Equalization) ile yerel kontrastın iyileştirilmesini sağlayan modüler bir ön işleme boru hattı (`ImagePreprocessor`) geliştirmektir.

---

## Engineer Research Assignment
- OpenCV'nin tarihsel nedenlerle kullandığı BGR (Blue-Green-Red) piksel dizilimi ile modern görüntüleme ve derin öğrenme kütüphanelerinin (RGB) uyuşmazlığının sebep olduğu kanal kayması anomalilerini araştırmak.
- Halı yüzey fotoğraflarında kamera sensör gürültüsünü (salt-and-pepper / Gaussian noise) bastırırken dokuma ilmek sınırlarını ve motif detaylarını koruyacak Gauss çekirdeği ($k=5$) parametrizasyonunu belirlemek.
- Düşük aydınlatmalı veya homojen olmayan fabrika ışıklandırmalarında global histogram eşitlemenin (HE) yarattığı aşırı pozlama sorununu CLAHE ile (lokal $8 \times 8$ ızgara ve $2.0$ clip limit) çözmek.
- `ImagePreprocessor` ile uçtan uca ön işleme hattını (`preprocess_pipeline`) doğrulamak.

---

## Concepts
- **BGR vs RGB Kanal Mimarisi:** Bellek matrisinde kanalların sıralanışı; yanlış renk uzayı dönüşümünde kırmızı ipliklerin mavi olarak algılanması riski.
- **Gri Seviye Dönüşümü (Grayscale):** İnsan gözünün yeşile duyarlılığını temel alan luma formülü:
  $$Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
- **Gauss Yumuşatma (Gaussian Blur):** 2B Gauss çekirdeği ile konvolüsyon:
  $$G(x, y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2+y^2}{2\sigma^2}}$$
- **CLAHE (Contrast Limited Adaptive Histogram Equalization):** Görüntüyü örtüşmeyen ızgaralara bölerek gürültü yükselmesini sınırlandıran yerel histogram eşitleme.
- **Interpolasyon:** Boyut küçültmede piksel alan ortalaması (`INTER_AREA`), büyütmede iki doğrusal (`INTER_LINEAR`) veya kübik (`INTER_CUBIC`) interpolasyon.

---

## Libraries
- `opencv-python` (`cv2`): Görüntü okuma, renk dönüşümleri, konvolüsyonel filtreler ve CLAHE.
- `numpy`: Piksel tensörleri (`ndarray`) ve matris şekil manipülasyonu.
- `pytest`: Görüntü ön işleme ve boyut doğrulama testleri.

---

## Functions / Classes Studied
- `ImagePreprocessor`
- `ImagePreprocessor.preprocess_pipeline()`, `ImagePreprocessor.to_grayscale()`
- `cv2.cvtColor()`, `cv2.COLOR_BGR2GRAY`, `cv2.COLOR_BGR2RGB`
- `cv2.GaussianBlur()`, `cv2.createCLAHE()`, `cv2.resize()`

---

## Notebook
- **Dosya:** [`day09_opencv_temelleri.ipynb`](day09_opencv_temelleri.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). OpenCV BGR okuma, Gauss filtreleme ve CLAHE kontrast iyileştirmeyi adım adım gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `opencv-image-analytics-toolkit`
- **Modüller:**
  - `src/image_preprocessor.py`: `ImagePreprocessor` sınıfı (Resize, Grayscale, Gauss Blur, CLAHE).
  - `src/io_validator.py`: `ImageIOValidator` Unicode güvenli okuma/yazma ve meta veri çıkarıcı.
  - `src/color_spaces.py`: `ColorSpaceConverter` renk uzayı dönüşümleri ve kanal istatistikleri.
  - `src/filters.py`: `IndustrialFilterPipeline` Gauss, Medyan, Bilateral ve Unsharp Mask filtreleri.
  - `src/equalization.py`: `HistogramEqualizer` Global HE ve CLAHE (CIELAB L* ve YCrCb Y).
  - `src/resizer.py`: `AspectPreservingResizer` en-boy oranı koruyarak letterbox boyutlandırma.
  - `src/analytics.py`: `ImageAnalyticsEngine` RMS kontrast, Shannon entropi ve Laplacian keskinlik analizi.
  - `src/generator.py`: `SyntheticCarpetGenerator` sentetik benchmark halı fikstürleri üretici.
  - `src/cli.py`: Terminal arayüzü ve uçtan uca kıyaslama benchmark orkestratörü.
  - `tests/test_image_preprocessor.py`: Ön işleme boru hattı birim testleri.
  - `tests/test_toolkit.py`: Araç kiti kapsamlı birim testleri (10 test).

---

## Architecture
```
day09/
├── README.md
├── day09_opencv_temelleri.ipynb
└── mini_project/
    ├── README.md
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

## Experiments
1. **Görüntü Ön İşleme Boru Hattı Deneyi:**
   - $400 \times 600 \times 3$ boyutundaki sentetik BGR görüntü, hedef çözünürlük olan $256 \times 256$ boyutuna dönüştürüldü.
   - Gri seviyeye çevrilip $5 \times 5$ Gauss çekirdeği ile filtrelendi ve CLAHE uygulanarak kontrastı dengelendi.
   - Çıktının $256 \times 256$ tek kanallı `uint8` formatında olduğu doğrulandı.
2. **Kapsamlı Filtreleme ve Kontrast Kıyaslama Benchmark'ı:**
   - Gauss, Medyan ($k=5$), Bilateral ($d=9$), Unsharp Mask, CLAHE (CIELAB $L^*$) ve Letterbox (512x512) operasyonlarının ortalama gecikme ve throughput (FPS) değerleri ölçüldü; RMS kontrast kazancı ve Laplacian keskinlik değişimleri raporlandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_image_preprocessing_pipeline`
  - `test_image_io_unicode_safe_read_write`
  - `test_image_io_metadata_extraction`
  - `test_color_space_conversions`
  - `test_aspect_preserving_resizer_letterbox`
  - `test_median_filter_salt_pepper_removal`
  - `test_bilateral_filter_edge_preservation`
  - `test_unsharp_masking_laplacian_variance`
  - `test_clahe_vs_global_equalization_luminance`
  - `test_image_analytics_entropy_and_contrast`
  - `test_cli_pipeline_execution_and_reports`
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Faz 2 Bilgisayarlı Görü zincirinin ilk adımı olan sağlam, standart ve gürültüden arındırılmış görüntü besleme hattı kurulmuştur.
- Halı yüzey analizleri için CLAHE ile zenginleştirilmiş gri tonlamalı girdi üretimi temin edilmiştir.

---

## Limitations
- Bu aşamada temel morfolojik ve kenar algoritmaları henüz eklenmemiştir; bunlar Day 13'te ele alınacaktır.
- Sentetik görüntüler üzerinde doğrulanmıştır; üretim hattı kamera kalibrasyon matrisleri homografi gününde (Day 12) devreye girecektir.

---

## Files
- `day09/README.md`
- `day09/day09_opencv_temelleri.ipynb`
- `day09/mini_project/README.md`
- `day09/mini_project/configs/toolkit_config.json`
- `day09/mini_project/fixtures/synthetic_carpets/`
- `day09/mini_project/src/__init__.py`
- `day09/mini_project/src/analytics.py`
- `day09/mini_project/src/color_spaces.py`
- `day09/mini_project/src/equalization.py`
- `day09/mini_project/src/filters.py`
- `day09/mini_project/src/generator.py`
- `day09/mini_project/src/image_preprocessor.py`
- `day09/mini_project/src/io_validator.py`
- `day09/mini_project/src/resizer.py`
- `day09/mini_project/src/cli.py`
- `day09/mini_project/tests/__init__.py`
- `day09/mini_project/tests/test_image_preprocessor.py`
- `day09/mini_project/tests/test_toolkit.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day09/mini_project/tests/ -v

# Uçtan uca kıyaslama benchmark'ını çalıştırma
python -m day09.mini_project.src.cli benchmark
```

---

## Next Day
- **Day 10:** Renk Uzayları ve Renk Farkı Analizi — RGB, HSV, CIE Lab uzayları ve algısal renk farkı ($\Delta E_{00}$, CIEDE2000).