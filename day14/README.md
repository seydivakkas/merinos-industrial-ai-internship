# Day 14 — Klasik Segmentasyon Yöntemleri

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Klasik Segmentasyon Yöntemleri (Yaprak 27 & 28)

## Goal
Bu günün amacı, Merinos halı desenlerindeki ana motifleri (çiçek, madalyon, bordür figürleri) arka plan iplik dokusundan piksel seviyesinde ayrıştırmaktır. Otsu bimodal eşikleme yöntemi ile global eşik değerini otomatik belirlemek; kontur analiziyle ayrıştırılan her bölgenin alan, çevre, sınırlayıcı kutu (bounding box) ve dairesellik (circularity / form factor) morfolojik özniteliklerini çıkaran `CarpetSegmenter` motorunu inşa etmektir.

---

## Engineer Research Assignment
- Bimodal (çift tepeli) histograma sahip tekstil görüntülerinde sınıflar arası varyansı ($\sigma_B^2$) maksimize ederek optimal eşik değerini $O(L)$ sürede hesaplayan Otsu algoritmasının matematiksel türetimini incelemek:
  $$\sigma_B^2(t) = \omega_0(t) \omega_1(t) [\mu_0(t) - \mu_1(t)]^2$$
- Birbirine dokunan veya komşu olan halı motiflerinin aşırı birleşmesini önlemede mesafe dönüşümü (`cv2.distanceTransform`) ve havza çizgileri (Watershed markers) yönteminin etkinliğini analiz etmek.
- Kontur çevre ($P$) ve alan ($A$) bağıntısından hesaplanan dairesellik metriğinin ($C = 4\pi A / P^2$) yuvarlak madalyon desenlerini (ideal daire için $C \approx 1.0$) köşeli bordürlerden ayırt etmedeki rolünü incelemek.
- `CarpetSegmenter` ile sentetik dairesel ve karesel motiflerin doğru geometrik etiketlerle ayrıştırıldığını birim testlerle doğrulamak.

---

## Concepts
- **Otsu Bimodal Eşikleme:** Gri tonlamalı görüntüyü zemin ve nesne pikselleri arasındaki varyansı en büyük yapacak eşik ($t^*$) ile siyah-beyaza dönüştürme.
- **Dış Kontur Analizi (`cv2.RETR_EXTERNAL`):** Zemin üzerinde yer alan bağımsız motif adacıklarının sınır piksellerini topolojik olarak zincirleme.
- **Dairesellik (Circularity / Isoperimetric Quotient):**
  $$C = \frac{4\pi \cdot \text{Alan}}{\text{Çevre}^2} \quad (0 < C \le 1)$$
- **Sınırlayıcı Kutu (Bounding Box):** Motifi çevreleyen asgari eksen-hizalı dikdörtgen $(x, y, w, h)$.
- **Minimum Alan Filtreleme:** İplik dokusundan kaynaklanan mikro gürültü noktalarını ($A < 20 \text{ px}$) eleyerek yalnız ana tasarım öğelerine odaklanma.

---

## Libraries
- `opencv-python` (`cv2`): `threshold()`, `THRESH_OTSU`, `findContours()`, `contourArea()`, `arcLength()`, `boundingRect()`.
- `numpy`: Gri seviye piksel matrisleri ve rastgele sentetik görüntü üretimi.
- `pydantic` (v2): `SegmentedRegion` veri modeli.
- `pytest`: Eşikleme değeri ve morfolojik dairesellik doğrulama testleri.

---

## Functions / Classes Studied
- `CarpetSegmenter`, `SegmentedRegion`
- `CarpetSegmenter.segment_otsu()`, `CarpetSegmenter.extract_regions()`
- `cv2.threshold()`, `cv2.findContours()`, `cv2.arcLength()`, `cv2.boundingRect()`

---

## Notebook
- **Dosya:** [`day14_klasik_segmentasyon.ipynb`](day14_klasik_segmentasyon.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Gürültülü zeminde yer alan yuvarlak ve kare motiflerin Otsu ile bölütlenmesini ve dairesellik analizini adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `classical-image-segmentation`
- **Modüller:**
  - `src/carpet_segmenter.py`: `CarpetSegmenter` ve `SegmentedRegion` sınıfları.
  - `src/color_histogram.py`, `src/glcm_engine.py`, `src/keypoint_engine.py`: Destekleyici öznitelik modülleri.
  - `tests/test_carpet_segmenter.py`: Otsu eşiği ve dairesellik birim testleri.
  - `tests/test_features.py`: Geleneksel öznitelik testleri.

---

## Architecture
```
day14/
├── README.md
├── day14_klasik_segmentasyon.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── carpet_segmenter.py
    │   ├── color_histogram.py
    │   ├── glcm_engine.py
    │   ├── keypoint_engine.py
    │   ├── feature_fusion.py
    │   └── models.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_carpet_segmenter.py
    │   └── test_features.py
    └── outputs/
```

---

## Experiments
1. **Otsu Eşikleme ve Bölge Çıkarım Deneyi:**
   - Düşük parlaklıktaki gürültülü zemin üzerine çizilen 1 dairesel ve 1 karesel motif üzerinde Otsu eşikleme çalıştırıldı.
   - Eşik değeri $35.0 \le t \le 200.0$ aralığında otomatik tespit edildi.
   - En az 2 bağımsız bölge ayrıştırıldı ve dairesel motifin dairesellik katsayısının $C > 0.75$ olduğu doğrulandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_otsu_and_region_extraction`
  - `test_features_*` (destekleyici öznitelik testleri)
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Halı desenlerinin arka plan dokumasından ayrıştırılarak bağımsız motif bölgelerine bölünmesi sağlanmıştır.
- Geometrik öznitelik çıkarımı ile sonraki aşamadaki desen sınıflandırma motoru için yapısal girdiler üretilmiştir.

---

## Limitations
- Otsu algoritması global bir eşik belirlediğinden, aşırı gölgeli veya aydınlatması homojen olmayan fabrika ortamlarında adaptif eşikleme (Adaptive Thresholding) veya Watershed ile desteklenmelidir.
- Testler sentetik zemin ve geometrik motifler üzerinde icra edilmiştir.

---

## Files
- `day14/README.md`
- `day14/day14_klasik_segmentasyon.ipynb`
- `day14/mini_project/README.md`
- `day14/mini_project/src/__init__.py`
- `day14/mini_project/src/carpet_segmenter.py`
- `day14/mini_project/tests/__init__.py`
- `day14/mini_project/tests/test_carpet_segmenter.py`
- `day14/mini_project/tests/test_features.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day14/mini_project/tests/ -v
```

---

## Next Day
- **Day 15:** Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu — Renk histogramları, GLCM doku öznitelikleri, ORB anahtar noktaları ve Faz 2 Bilgisayarlı Görü Zincirinin konsolidasyonu.