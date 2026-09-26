# Day 12 — Perspektif Düzeltme ve Homografi

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Perspektif Düzeltme ve Homografi (Yaprak 23 & 24)

## Goal
Bu günün amacı, Merinos halı üretim ve kalite kontrol hatlarında konveyör veya muayene masası üzerine yerleştirilen endüstriyel kameraların montaj açılarından kaynaklanan perspektif bozulmalarını (trapezoidal / projective distortion) matematiksel olarak gidermektir. Halının dört köşe koordinatını deterministik olarak saat yönünde sıralayan (`order_points`, `order_four_points`), 8 serbestlik dereceli $3 \times 3$ projektif homografi matrisi ($H$) kestiren (`compute_homography`, `HomographyRectifier`) ve görüntüyü ortorektifiye metrik düzleme dönüştürerek standart Merinos katalog ebatlarına (160x230, 200x290 vb.) uyarlayan `CarpetPerspectiveRectifier` pipeline'ını kurmaktır.

---

## Engineer Research Assignment
- Projektif geometride iki düzlem arasındaki 2B homografi ilişkisini homojen koordinatlar cinsinden formüle etmek:
  $$s \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$
- $3 \times 3$ matrisin 8 serbestlik derecesi (DoF) bulunduğundan, çözüm için en az 4 eşlenik nokta çiftinin ($x_i, y_i \leftrightarrow x_i', y_i'$) Doğrudan Lineer Dönüşüm (DLT) ile tekil değer ayrışımı (SVD) üzerinden nasıl kestirildiğini incelemek.
- Köşelerin sıralanmasında toplam ($x+y$) ve fark ($y-x$) algoritmalarını kodlayarak sol-üst (TL), sağ-üst (TR), sağ-alt (BR) ve sol-alt (BL) sırasını garanti altına almak; ters dönme (mirroring/flipping) risklerini bertaraf etmek.
- Rektifiye edilen halı yüzeyinin iç açı sapmalarını hesaplayarak 90° dikliği ve en-boy oranını (aspect ratio) endüstriyel QA kriterlerine göre derecelendirmek.

---

## Concepts
- **Perspektif Bozulması (Perspective Distortion):** Kameranın optik ekseninin halı yüzeyine tam dik olmaması nedeniyle dikdörtgen halının yamuk (trapezoid) görünmesi.
- **Homografi Matrisi ($H \in \mathbb{R}^{3 \times 3}$):** İki projektif düzlem arasındaki doğrusal izdüşümsel eşleme.
- **Köşe Noktalarının Sıralanması (Quad Ordering):**
  - Sol-üst (TL): $\min(x + y)$
  - Sağ-alt (BR): $\max(x + y)$
  - Sağ-üst (TR): $\min(y - x)$
  - Sol-alt (BL): $\max(y - x)$
- **Ortorektifikasyon (Orthorectification):** Halı yüzeyindeki desenlerin, bordürlerin ve piksel boyutlarının fiziksel milimetrelerle birebir oranlı hale getirilmesi.
- **Endüstriyel Kalite Güvence Değerlendirmesi (QA Grade):** Rektifiye edilmiş dörtgenin iç açılarının 90°'den sapma derecesine göre `PASS` ($\le 1.5^\circ$), `WARNING` ($1.5^\circ - 4.0^\circ$) veya `REJECT` ($> 4.0^\circ$) kararı üretilmesi.

---

## Libraries
- `opencv-python` (`cv2`): `getPerspectiveTransform()`, `warpPerspective()`, köşe tespit ve kontur filtreleme.
- `numpy`: Koordinat tensörleri, köşe toplam/fark hesapları ve $3 \times 3$ homografi matris işlemleri.
- `pydantic`: Tip kontrollü veri modelleri (`Point2D`, `QuadCorners`, `HomographyResult`, `RectificationReport`).
- `pytest`: Köşe sıralama, homografi dönüşüm ve rektifikasyon entegrasyon testleri.

---

## Functions / Classes Studied
- `CornerDetector`, `order_points`, `order_four_points`
- `compute_homography`, `transform_points`, `warp_perspective`
- `HomographyRectifier`, `CarpetPerspectiveRectifier`
- `Point2D`, `QuadCorners`, `StandardCarpetRatio`, `HomographyResult`, `QAGrade`, `RectificationReport`

---

## Notebook
- **Dosya:** [`day12_perspektif_ve_homografi.ipynb`](day12_perspektif_ve_homografi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Açılı çekilmiş sentetik halı görüntüsünün köşe noktalarından $3 \times 3$ homografi ile kuşbakışı düzeltilmesini adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `perspective-rectification-and-homography`
- **Modüller:**
  - `src/models.py`: Pydantic veri modelleri ve kalite güvence sınıfları.
  - `src/corner_detector.py`: Dörtgen köşe tespiti ve [TL, TR, BR, BL] sıralama algoritması.
  - `src/homography.py`: $3 \times 3$ projektif homografi kestirimi ve nokta dönüşümleri.
  - `src/homography_rectifier.py`: Hızlı homografi rektifikasyon motoru.
  - `src/rectifier.py`: Endüstriyel `CarpetPerspectiveRectifier` pipeline'ı.
  - `src/generator.py`: Sentetik açılı halı fikstürleri üretici (25°, 35°, 45°).
  - `src/cli.py`: Komut satırı arayüzü.
  - `configs/rectification_config.json`: Rektifikasyon parametreleri ve QA toleransları.

---

## Architecture
```
day12/
├── README.md
├── day12_perspektif_ve_homografi.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── rectification_config.json
    ├── fixtures/
    │   └── synthetic_carpets/
    │       ├── carpet_skewed_oblique_25deg.png
    │       ├── carpet_skewed_conveyor_35deg.png
    │       └── carpet_skewed_severe_45deg.png
    ├── src/
    │   ├── __init__.py
    │   ├── cli.py
    │   ├── corner_detector.py
    │   ├── generator.py
    │   ├── homography.py
    │   ├── homography_rectifier.py
    │   ├── models.py
    │   └── rectifier.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_corner_detector.py
    │   ├── test_homography.py
    │   ├── test_homography_cli.py
    │   ├── test_homography_rectifier.py
    │   ├── test_order_points.py
    │   └── test_rectification.py
    └── outputs/
```

---

## Experiments
1. **Dört Köşe Noktası Sıralama Deneyi:**
   - Sırasız verilen 4 köşe koordinatı $[(200, 300), (10, 20), (210, 15), (15, 310)]$ başarıyla TL, TR, BR, BL düzenine dizildi.
2. **Homografi Projeksiyon ve Nokta Dönüşüm Deneyi:**
   - Kaynak ve hedef koordinatlar eşleştirildiğinde birim matris stabilitesi ve piksellerin doğru düzleme izdüşümü doğrulandı.
3. **Endüstriyel Rektifikasyon ve Standart Oran Deneyi:**
   - Açılı çekilmiş sentetik halı fikstürleri (25° ve 35°) rektifiye edilerek iç açı sapması $< 1.0^\circ$ düzeyine indirildi ve `PASS` kalite derecesi elde edildi.

---

## Validation
- Pytest ile 12 adet birim test icra edildi:
  - `test_detect_corners_on_synthetic`
  - `test_corner_detector_returns_four_points`
  - `test_homography_identity`
  - `test_homography_point_warping`
  - `test_cli_runs`
  - `test_order_four_points`
  - `test_homography_rectification_shape`
  - `test_order_points_basic`
  - `test_order_points_rotated`
  - `test_rectify_preserves_content`
  - `test_rectify_output_size`
  - `test_rectify_on_realistic_synthetic`
- Tüm testler **%100 başarıyla (12 passed)** geçti.

---

## Results
- Üretim hattındaki açılı kamera çekimleri standart kuşbakışı görünüme dönüştürülmüştür.
- Boyut ölçümü, desen hizalama ve bordür doğrusallığı analizleri için gereken metrik doğruluk garanti edilmiştir.

---

## Limitations
- Köşe tespiti yüksek kontrastlı halı/zemin geçişlerinde etkilidir; çok benzer tondaki zeminlerde veya püsküllü kenarlarda derin öğrenme segmentasyonu ile desteklenmesi önerilir.
- Testler yerel prototip sentetik görüntülerle gerçekleştirilmiştir; canlı fabrika kamerası bağlı değildir.

---

## Files
- `day12/README.md`
- `day12/day12_perspektif_ve_homografi.ipynb`
- `day12/mini_project/README.md`
- `day12/mini_project/configs/rectification_config.json`
- `day12/mini_project/src/__init__.py`
- `day12/mini_project/src/cli.py`
- `day12/mini_project/src/corner_detector.py`
- `day12/mini_project/src/generator.py`
- `day12/mini_project/src/homography.py`
- `day12/mini_project/src/homography_rectifier.py`
- `day12/mini_project/src/models.py`
- `day12/mini_project/src/rectifier.py`
- `day12/mini_project/tests/test_corner_detector.py`
- `day12/mini_project/tests/test_homography.py`
- `day12/mini_project/tests/test_homography_cli.py`
- `day12/mini_project/tests/test_homography_rectifier.py`
- `day12/mini_project/tests/test_order_points.py`
- `day12/mini_project/tests/test_rectification.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day12/mini_project/tests/ -v

# CLI kullanımı
python -m day12.mini_project.src.cli --help
```

---

## Next Day
- **Day 13:** Morfolojik İşlemler, Kenar ve Çizgi Tespiti — Aşındırma (Erosion), Genişletme (Dilation), Açma/Kapama, Canny kenar operatörü ve Hough doğrusal çizgi dönüşümü ile halı bordür doğrusallığı ve dokuma kusuru tespiti.

---

## AI Coding Agent Prompt
"Day 12 Perspektif Düzeltme ve Homografi mini projesini çalıştırın, 12 birim testi doğrulayın ve standalone jupyter notebook'u hatasız koşun."