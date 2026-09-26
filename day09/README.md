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
- **Adı:** `opencv-image-preprocessing`
- **Modüller:**
  - `src/image_preprocessor.py`: `ImagePreprocessor` sınıfı (Resize, Grayscale, Gauss Blur, CLAHE).
  - `src/kmeans_palette.py`, `src/ciede2000.py`, `src/color_models.py`: Destekleyici renk analiz bileşenleri.
  - `tests/test_image_preprocessor.py`: Ön işleme boru hattı birim testleri.
  - `tests/test_palette_and_ciede2000.py`: Renk ve palet hesaplama testleri.

---

## Architecture
```
day09/
├── README.md
├── day09_opencv_temelleri.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── image_preprocessor.py
    │   ├── kmeans_palette.py
    │   ├── ciede2000.py
    │   ├── color_models.py
    │   ├── quantizer.py
    │   └── yarn_matcher.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_image_preprocessor.py
    │   └── test_palette_and_ciede2000.py
    └── outputs/
```

---

## Experiments
1. **Görüntü Ön İşleme Boru Hattı Deneyi:**
   - $400 \times 600 \times 3$ boyutundaki sentetik BGR görüntü, hedef çözünürlük olan $256 \times 256$ boyutuna dönüştürüldü.
   - Gri seviyeye çevrilip $5 \times 5$ Gauss çekirdeği ile filtrelendi ve CLAHE uygulanarak kontrastı dengelendi.
   - Çıktının $256 \times 256$ tek kanallı `uint8` formatında olduğu doğrulandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_image_preprocessing_pipeline`
  - `test_palette_and_ciede2000_*` (destekleyici palet testleri)
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
- `day09/mini_project/src/__init__.py`
- `day09/mini_project/src/image_preprocessor.py`
- `day09/mini_project/tests/__init__.py`
- `day09/mini_project/tests/test_image_preprocessor.py`
- `day09/mini_project/tests/test_palette_and_ciede2000.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day09/mini_project/tests/ -v
```

---

## Next Day
- **Day 10:** Renk Uzayları ve Renk Farkı — BGR, HSV, CIE Lab uzayları ve algısal renk farkı ($\Delta E$).