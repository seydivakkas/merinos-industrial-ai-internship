# Day 12 — Perspektif Düzeltme ve Homografi

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Perspektif Düzeltme ve Homografi (Yaprak 23 & 24)

## Goal
Bu günün amacı, Merinos halı dokuma salonlarında konveyör veya kalite muayene masası üzerine yerleştirilen endüstriyel kameraların açılı duruşundan kaynaklanan perspektif bozulmalarını (trapezoidal distorsiyon) gidermektir. Halının dört köşe koordinatını saat yönünde sıralayan (`order_four_points`) ve 8 serbestlik dereceli $3 \times 3$ projektif homografi matrisi ($H$) hesaplayarak görüntüyü kuşbakışı (top-down / orthorectified) metrik düzleme dönüştüren `HomographyRectifier` motorunu inşa etmektir.

---

## Engineer Research Assignment
- Projektif geometride iki düzlem arasındaki 2B homografi ilişkisini ve homojen koordinatlar cinsinden formülasyonunu incelemek:
  $$s \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$
- $3 \times 3$ matrisin 8 serbestlik derecesi (DoF) bulunduğundan, çözüm için en az 4 eşlenik nokta çiftinin ($x_i, y_i \leftrightarrow x_i', y_i'$) Doğrudan Lineer Dönüşüm (DLT) ile tekil değer ayrışımı (SVD) üzerinden nasıl bulunduğunu araştırmak.
- Köşelerin sıralanmasında toplam ($x+y$) ve fark ($y-x$) algoritmalarını kodlayarak sol-üst (TL), sağ-üst (TR), sağ-alt (BR) ve sol-alt (BL) sırasını garanti altına almak; ters dönme (mirroring/flipping) risklerini bertaraf etmek.
- `cv2.getPerspectiveTransform` ve `cv2.warpPerspective` fonksiyonlarıyla metrik doğrulamayı gerçekleştirmek.

---

## Concepts
- **Perspektif Bozulması (Perspective Distortion):** Kameranın optik ekseninin halı yüzeyine tam dik olmaması nedeniyle dikdörtgen halının yamuk (trapezoid) görünmesi.
- **Homografi Matrisi ($H \in \mathbb{R}^{3 \times 3}$):** İki projektif düzlem arasındaki doğrusal izdüşümsel eşleme.
- **Köşe Noktalarının Sıralanması (Quad Ordering):**
  - Sol-üst: $\min(x + y)$
  - Sağ-alt: $\max(x + y)$
  - Sağ-üst: $\min(y - x)$
  - Sol-alt: $\max(y - x)$
- **Ortorektifikasyon (Orthorectification):** Halı yüzeyindeki desenlerin, bordürlerin ve piksel boyutlarının fiziksel milimetrelerle birebir oranlı hale getirilmesi.

---

## Libraries
- `opencv-python` (`cv2`): `getPerspectiveTransform()`, `warpPerspective()`.
- `numpy`: Koordinat matrisleri, köşe toplam/fark hesapları ve $3 \times 3$ homografi tensörü.
- `pytest`: Köşe sıralama ve homografi dönüşüm testleri.

---

## Functions / Classes Studied
- `HomographyRectifier`, `order_four_points`
- `HomographyRectifier.rectify()`
- `cv2.getPerspectiveTransform()`, `cv2.warpPerspective()`
- `EdgeOperatorEngine`, `HoughLineEngine`, `CarpetBorderAnalyzer`

---

## Notebook
- **Dosya:** [`day12_perspektif_ve_homografi.ipynb`](day12_perspektif_ve_homografi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Açılı çekilmiş sentetik halı görüntüsünün köşe noktalarından $3 \times 3$ homografi ile kuşbakışı düzeltilmesini adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `perspective-rectification-and-homography`
- **Modüller:**
  - `src/homography_rectifier.py`: Dört nokta sıralayıcı ve `HomographyRectifier` sınıfı.
  - `src/border_analyzer.py`, `src/edge_operators.py`, `src/hough_engine.py`: Destekleyici geometrik bordür araçları.
  - `tests/test_homography_rectifier.py`: Köşe sıralama ve homografi şekil testleri.
  - `tests/test_edge_lines.py`: Kenar ve çizgi analizi testleri.

---

## Architecture
```
day12/
├── README.md
├── day12_perspektif_ve_homografi.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── homography_rectifier.py
    │   ├── border_analyzer.py
    │   ├── edge_operators.py
    │   ├── hough_engine.py
    │   └── models.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_homography_rectifier.py
    │   └── test_edge_lines.py
    └── outputs/
```

---

## Experiments
1. **Dört Köşe Noktası Sıralama Deneyi:**
   - Sırasız verilen 4 köşe koordinatı $[(200, 300), (10, 20), (210, 15), (15, 310)]$ başarıyla TL, TR, BR, BL düzenine dizildi.
2. **Kuşbakışı Düzeltme Deneyi:**
   - Yamuk köşe noktaları tanımlanan $500 \times 500$ piksel sentetik görüntü, hedef $300 \times 400$ çözünürlüğe gerilerek $3 \times 3$ homografi matrisi ve rektifiye görüntü üretildi.

---

## Validation
- Pytest ile 12 adet birim test icra edildi:
  - `test_order_four_points`
  - `test_homography_rectification_shape`
  - `test_edge_lines_*` (destekleyici bordür testleri)
- Tüm testler **%100 başarıyla (12 passed)** geçti.

---

## Results
- Üretim hattındaki açılı kamera çekimleri standart kuşbakışı görünüme dönüştürülmüştür.
- Boyut ölçümü ve desen hizalama için gerekli metrik doğruluk garanti edilmiştir.

---

## Limitations
- Köşe noktaları bu aşamada manuel veya kural tabanlı koordinatlar olarak beslenmiştir; aşırı desenli ve kenarları püsküllü halılarda otomatik köşe bulma derin öğrenme modelleri (Faz 2 sonu) ile güçlendirilecektir.
- Testler sentetik görüntülerle gerçekleştirilmiştir.

---

## Files
- `day12/README.md`
- `day12/day12_perspektif_ve_homografi.ipynb`
- `day12/mini_project/README.md`
- `day12/mini_project/src/__init__.py`
- `day12/mini_project/src/homography_rectifier.py`
- `day12/mini_project/tests/__init__.py`
- `day12/mini_project/tests/test_homography_rectifier.py`
- `day12/mini_project/tests/test_edge_lines.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day12/mini_project/tests/ -v
```

---

## Next Day
- **Day 13:** Morfolojik İşlemler ve Kenar Tespiti — Aşındırma (Erosion), Genişletme (Dilation), Açma/Kapama ve Canny/Sobel kenar filtreleri ile dokuma kusuru tespiti.