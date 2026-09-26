# Day 13 — Morfolojik İşlemler ve Kenar Tespiti

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Morfolojik İşlemler ve Kenar Tespiti (Yaprak 25 & 26)

## Goal
Bu günün amacı, Merinos halı dokuma tezgahlarında ortaya çıkan mikro parazitleri, toz lekelerini ve ilmek kaçıklarını gidermek; matematiksel morfoloji (aşındırma, genişletme, açma, kapama), Canny histerezis kenar detektörü ve Olasılıksal Hough Çizgi Dönüşümü yöntemleriyle halı bordür paralelliğini ve çözgü/atkı iplik hizalarını tespit eden `MorphologyEdgeEngine` analiz motorunu geliştirmektir.

---

## Engineer Research Assignment
- İkili (binary) kumaş maskelerinde izole gürültü noktalarını yok eden Açma ($A \circ B = (A \ominus B) \oplus B$) ile küçük delik ve çatlakları dolduran Kapama ($A \bullet B = (A \oplus B) \ominus B$) operatörlerinin $3 \times 3$ ve $5 \times 5$ yapısal elemanlarla davranışını modellemek.
- Canny kenar tespit algoritmasının 4 temel aşamasını (Gauss filtresi, Sobel yönlü gradyan hesaplama, Non-Maximum Suppression ile inceltme, çift eşikli Hysteresis) incelemek.
- Parametre uzayında ($r, \theta$) oylama yapan Hough Çizgi Dönüşümü (`HoughLinesP`) ile halı bordür doğrularını saptayarak tezgâhtaki atkı eğriliği (weft bow/skew) sapmalarını belirlemek.
- `MorphologyEdgeEngine` ile yapısal morfolojik operasyonların piksel alanı üzerindeki genişletici ve daraltıcı etkilerini birim testlerle doğrulamak.

---

## Concepts
- **Aşındırma (Erosion):** Yapısal elemanın nesne sınırlarını kemirerek küçük beyaz parazitleri yok etmesi:
  $$(A \ominus B) = \{z \mid (B)_z \subseteq A\}$$
- **Genişletme (Dilation):** Nesne sınırlarına yapısal eleman kadar piksel ekleyerek boşlukları kapatması:
  $$(A \oplus B) = \{z \mid (\hat{B})_z \cap A \neq \emptyset\}$$
- **Açma ve Kapama (Opening & Closing):** Açma küçük çıkıntı ve noktaları eler; kapama ise küçük iç delikleri birleştirir.
- **Canny Kenar Tespiti:** Gradyan şiddeti ve yönüne göre yerel maksimumları koruyan ve zayıf kenarları güçlü kenarlara bağlayan optimal filtre.
- **Olasılıksal Hough Dönüşümü:** Kenar piksellerinden geçen doğruları sonlu çizgi parçaları ($x_1, y_1, x_2, y_2$) olarak döndüren dönüşüm.

---

## Libraries
- `opencv-python` (`cv2`): `morphologyEx()`, `Canny()`, `HoughLinesP()`.
- `numpy`: 2B ikili ve gri seviye görüntü tensörleri.
- `pytest`: Morfolojik alan değişimi ve çizgi tespiti testleri.

---

## Functions / Classes Studied
- `MorphologyEdgeEngine`
- `MorphologyEdgeEngine.apply_morphology()`, `MorphologyEdgeEngine.detect_canny_edges()`, `MorphologyEdgeEngine.detect_lines_hough()`
- `cv2.getStructuringElement()`, `cv2.morphologyEx()`, `cv2.Canny()`, `cv2.HoughLinesP()`

---

## Notebook
- **Dosya:** [`day13_morfoloji_ve_kenar.ipynb`](day13_morfoloji_ve_kenar.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Sentetik dokuma deseninde aşındırma, genişletme, Canny kenar tespiti ve dikey/yatay çizgi tespitini adım adım gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `morphology-edge-and-line-engine`
- **Modüller:**
  - `src/morphology_lines.py`: `MorphologyEdgeEngine` sınıfı.
  - `src/otsu_segmenter.py`, `src/watershed_segmenter.py`, `src/grabcut_segmenter.py`: Destekleyici segmentasyon modülleri.
  - `tests/test_morphology_lines.py`: Aşındırma, genişletme, Canny ve Hough birim testleri.
  - `tests/test_segmentation.py`: Bölütleme testleri.

---

## Architecture
```
day13/
├── README.md
├── day13_morfoloji_ve_kenar.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── morphology_lines.py
    │   ├── otsu_segmenter.py
    │   ├── watershed_segmenter.py
    │   ├── grabcut_segmenter.py
    │   ├── benchmark.py
    │   └── evaluator.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_morphology_lines.py
    │   └── test_segmentation.py
    └── outputs/
```

---

## Experiments
1. **Morfolojik Alan Değişimi Deneyi:**
   - $50 \times 50$ siyah zemin üzerine çizilen $10 \times 10$ kare nesneye $3 \times 3$ aşındırma uygulandığında toplam beyaz piksel sayısının azaldığı (`eroded.sum() < img.sum()`); genişletme uygulandığında arttığı (`dilated.sum() > img.sum()`) doğrulandı.
2. **Canny ve Hough ile Dikey Çizgi Tespiti:**
   - Görüntüye eklenen dikey çizgi Canny ile tespit edildi ve HoughLinesP ile doğrunun koordinatları yakalanarak eğimi doğrulandı ($|x_1 - x_2| \le 2$).

---

## Validation
- Pytest ile 12 adet birim test icra edildi:
  - `test_morphology_operations`
  - `test_canny_and_hough_lines`
  - `test_segmentation_*` (destekleyici algoritma testleri)
- Tüm testler **%100 başarıyla (12 passed)** geçti.

---

## Results
- Halı yüzeyindeki dokuma kusurlarını ve yabancı maddeleri filtreleyen matematiksel morfoloji araçları hayata geçirilmiştir.
- Bordür ve çizgi hizalamasını ölçen Hough detektörü doğrulanmıştır.

---

## Limitations
- Çok karmaşık çiçekli veya oryantal madalyonlu desenlerde kenarlar aşırı yoğun çıkabilir; bu tür desenlerde kenar filtreleri öncesi bilateral veya median filtreleme tercih edilmelidir.
- Testler sentetik şekiller ve çizgiler üzerinde yürütülmüştür.

---

## Files
- `day13/README.md`
- `day13/day13_morfoloji_ve_kenar.ipynb`
- `day13/mini_project/README.md`
- `day13/mini_project/src/__init__.py`
- `day13/mini_project/src/morphology_lines.py`
- `day13/mini_project/tests/__init__.py`
- `day13/mini_project/tests/test_morphology_lines.py`
- `day13/mini_project/tests/test_segmentation.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day13/mini_project/tests/ -v
```

---

## Next Day
- **Day 14:** Klasik Segmentasyon Yöntemleri — Eşikleme (Otsu), Havza (Watershed) ve GrabCut algoritmaları ile zemin-motif ayrıştırma ve Dice/IoU kıyaslaması.