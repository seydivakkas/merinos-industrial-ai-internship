# Day 14 — Klasik Görüntü Segmentasyonu

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Klasik Segmentasyon Yöntemleri (Yaprak 27 & 28)

## Goal
Bu günün amacı, Merinos jakarlı halı üretim ve kalite denetim hatlarında (jakarlı tezgâh çıkışı, apre, motif kontrolü ve konfeksiyon) halı desen motiflerinin zemin kumaşından piksel seviyesinde ayrıştırılmasıdır. **Otsu Global & Multi-Otsu Eşikleme**, **Mesafe Dönüşümü Tohumlamalı Watershed (Havza)** ve **GMM Tabanlı GrabCut (Grafik Kesme)** algoritmalarını entegre eden; segmentasyon kalitesini piksel bazlı metriklerle ($IoU$, $Dice$, $BF\text{-}Score$) ve yürütme hızıyla ($FPS, ms$) kıyaslayan endüstriyel `CarpetSegmenter`, `OtsuSegmenter`, `WatershedSegmenter` ve `GrabCutSegmenter` motorlarını inşa etmektir.

---

## Engineer Research Assignment
- Bimodal ve multimodal histogramlarda sınıflar arası varyansı ($\sigma_B^2$) maksimize ederek optimal eşik değerlerini $O(L)$ sürede hesaplayan Otsu ve Multi-Otsu algoritmalarını incelemek:
  $$\sigma_B^2(t) = \omega_0(t) \omega_1(t) [\mu_0(t) - \mu_1(t)]^2$$
- Birbirine dokunan veya komşu olan halı motiflerinin aşırı birleşmesini (over-segmentation / under-segmentation) önlemede Öklid mesafe dönüşümü (`cv2.distanceTransform`) ile tohum işaretçisi (marker) üreterek Watershed gradyan havzasında sınır yakalamayı araştırmak.
- Ön plan ve arka plan Gauss Karışım Modelleri (GMM) ile piksel komşuluk enerji fonksiyonunu iteratif minimum kesme (min-cut / max-flow) ile çözen GrabCut algoritmasını incelemek.
- Segmentasyon başarımını Ground Truth maskelerine göre Jaccard İndeksi ($IoU = \frac{|A \cap B|}{|A \cup B|}$), Dice Katsayısı ($Dice = \frac{2|A \cap B|}{|A| + |B|}$) ve Boundary F1 skoru üzerinden ölçmek.

---

## Concepts
- **Otsu Bimodal & Multi-Otsu Eşikleme:** Histogram ayrımı ile zemin ve motif ayrımı; 3 veya 4 seviyeli çok sınıflı kumaş ayrıştırma.
- **İşaretçi Tabanlı Watershed:** Görüntü gradyanını topoğrafik yüzey, mesafe dönüşümü tepe noktalarını su kaynakları kabul ederek havza çizgilerini bulma.
- **GrabCut Algoritması:** Kullanıcı veya sistem sınırlayıcı kutusu (bounding box) içinde renk GMM'leri ve Markov Rasgele Alanları (MRF) ile enerji minimizasyonu.
- **Segmentasyon Değerlendirme Metrikleri:**
  - **IoU (Intersection over Union):** Maske örtüşüm oranı.
  - **Dice Katsayısı:** Ön plan sınıf F1 skoru.
  - **Boundary F1 (BF-Score):** Kenar konturlarının 1-2 piksel toleransla örtüşme hassasiyeti.
- **Endüstriyel Dağıtım Kriteri:** Canlı hat için yüksek FPS ($> 50 \text{ FPS}$) sunan Otsu/Watershed; çevrimdışı desen doğrulama laboratuvarı için yüksek kenar hassasiyeti sağlayan GrabCut seçimi.

---

## Libraries
- `opencv-python` (`cv2`): `threshold()`, `distanceTransform()`, `watershed()`, `grabCut()`, `findContours()`.
- `numpy`: 2B/3B piksel tensörleri, maske mantıksal işlemleri.
- `pydantic` (v2): `EvaluationMetrics`, `AlgorithmBenchmarkResult`, `CarpetSegmentationReport`.
- `pytest`: 11 adet kapsamlı birim ve entegrasyon testi.

---

## Functions / Classes Studied
- `CarpetSegmenter`, `SegmentedRegion`
- `OtsuSegmenter`, `WatershedSegmenter`, `GrabCutSegmenter`
- `SegmentationEvaluator`, `SegmentationBenchmarkEngine`
- `CarpetSegmentationFixtureGenerator`

---

## Notebook
- **Dosya:** [`day14_klasik_segmentasyon.ipynb`](day14_klasik_segmentasyon.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Gürültülü zeminde yer alan yuvarlak ve kare motiflerin Otsu ile bölütlenmesini ve dairesellik analizini adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `classical-image-segmentation`
- **Modüller:**
  - `src/carpet_segmenter.py`: `CarpetSegmenter` ve morfolojik bölge çıkarıcı.
  - `src/otsu_segmenter.py`: Otsu Global ve Multi-Otsu motoru.
  - `src/watershed_segmenter.py`: Mesafe dönüşümlü Watershed motoru.
  - `src/grabcut_segmenter.py`: Enerji minimizasyonlu GrabCut motoru.
  - `src/evaluator.py`: IoU, Dice, Pixel Accuracy, Boundary F1 motoru.
  - `src/benchmark.py`: Hız vs doğruluk kıyaslama laboratuvarı.
  - `src/generator.py`: Sentetik jakarlı madalyon ve geometrik halı GT üretici.
  - `src/cli.py`: Segmentasyon CLI arayüzü.
  - `configs/segmentation_config.json`: Segmentasyon hiperparametreleri.

---

## Architecture
```
day14/
├── README.md
├── day14_klasik_segmentasyon.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── segmentation_config.json
    ├── fixtures/
    │   └── synthetic_carpets/
    │       ├── carpet_medallion_classic.png
    │       ├── carpet_medallion_classic_gt_mask.png
    │       ├── carpet_medallion_classic_gt_multiclass.png
    │       ├── carpet_geometric_modern.png
    │       └── carpet_geometric_modern_gt_mask.png
    ├── src/
    │   ├── __init__.py
    │   ├── benchmark.py
    │   ├── carpet_segmenter.py
    │   ├── cli.py
    │   ├── evaluator.py
    │   ├── generator.py
    │   ├── grabcut_segmenter.py
    │   ├── models.py
    │   ├── otsu_segmenter.py
    │   └── watershed_segmenter.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_carpet_segmenter.py
    │   └── test_segmentation.py
    └── outputs/
```

---

## Experiments
1. **Otsu Global ve Multi-Otsu Eşikleme:**
   - İki modlu dağılımda $IoU > 0.95$ örtüşme elde edildi. 3 seviyeli Multi-Otsu ile zemin kumaşı, bordür ve ana motif 3 farklı sınıfa ayrıştırıldı.
2. **Watershed ile Bitişik Motif Ayrıştırma:**
   - Mesafe dönüşümü yerel maksimumları tohum alınarak dokunan motif sınırları başarıyla ayrıştırıldı.
3. **GrabCut Enerji Minimizasyonu:**
   - 5 iterasyon sonunda madalyon konturlarına yüksek uyum ($IoU > 0.90$) sağlandı.
4. **Algoritma Benchmark Kıyaslaması:**
   - Otsu: Ultra hızlı ($> 100 \text{ FPS}$), canlı üretim hattı için tavsiye edildi.
   - Watershed: Dengeli ($~ 40\text{--}60 \text{ FPS}$), karmaşık desen ayrımı için optimize.
   - GrabCut: Yüksek hassasiyet ($~ 5\text{--}10 \text{ FPS}$), çevrimdışı laboratuvar için tavsiye edildi.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_otsu_and_region_extraction`
  - `test_otsu_global_threshold_accuracy`
  - `test_multi_otsu_segmentation_classes`
  - `test_watershed_distance_transform_markers`
  - `test_watershed_boundary_adherence`
  - `test_grabcut_energy_minimization`
  - `test_evaluator_perfect_overlap_metrics`
  - `test_evaluator_disjoint_masks_metrics`
  - `test_otsu_vs_watershed_vs_grabcut_on_synthetic_carpet`
  - `test_segmentation_robustness_to_texture_noise`
  - `test_report_serialization_and_cli`
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Halı desenlerinin arka plan dokumasından ayrıştırılarak bağımsız motif bölgelerine bölünmesi sağlanmıştır.
- Canlı hat ve laboratuvar için net mühendislik kararları ($FPS$ vs $IoU$) raporlanmıştır.

---

## Limitations
- Otsu algoritması homojen aydınlatma varsayar; dengesiz ortam ışığında Watershed veya derin öğrenme maskelemesi gereklidir.
- Testler yerel prototip sentetik görüntülerle gerçekleştirilmiştir.

---

## Files
- `day14/README.md`
- `day14/day14_klasik_segmentasyon.ipynb`
- `day14/mini_project/README.md`
- `day14/mini_project/configs/segmentation_config.json`
- `day14/mini_project/src/__init__.py`
- `day14/mini_project/src/benchmark.py`
- `day14/mini_project/src/carpet_segmenter.py`
- `day14/mini_project/src/cli.py`
- `day14/mini_project/src/evaluator.py`
- `day14/mini_project/src/generator.py`
- `day14/mini_project/src/grabcut_segmenter.py`
- `day14/mini_project/src/models.py`
- `day14/mini_project/src/otsu_segmenter.py`
- `day14/mini_project/src/watershed_segmenter.py`
- `day14/mini_project/tests/test_carpet_segmenter.py`
- `day14/mini_project/tests/test_segmentation.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day14/mini_project/tests/ -v

# Segmentasyon CLI çalıştırma
python -m day14.mini_project.src.cli segment --image day14/mini_project/fixtures/synthetic_carpets/carpet_medallion_classic.png --method ALL
```

---

## Next Day
- **Day 15:** Görsel Özellik Çıkarımı ve Entegrasyon — Renk histogramları, GLCM doku öznitelikleri, ORB/SIFT anahtar noktaları ve Faz 2 Bilgisayarlı Görü Boru Hattının konsolidasyonu.

---

## AI Coding Agent Prompt
"Day 14 Klasik Görüntü Segmentasyonu mini projesini çalıştırın, 11 birim testi doğrulayın ve standalone jupyter notebook'u hatasız koşun."