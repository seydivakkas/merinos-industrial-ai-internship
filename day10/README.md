# Day 10 — Renk Uzayları ve Renk Farkı

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Renk Uzayları ve Renk Farkı (Yaprak 19 & 20)

## Goal
Bu günün amacı, Merinos boyahane ve dokuma tesislerinde iplik ve halı yüzeylerinin renk kalitesini matematiksel ve algısal olarak denetlemektir. Donanım tabanlı RGB/BGR renk uzayının homojen olmama sorununu gidermek üzere insan görme sistemini modelleyen CIE $L^*a^*b^*$ ve renk tonu/doygunluğunu ayrıştıran HSV uzaylarına dönüşüm yapmak; iki numune arasındaki algısal renk sapmasını $\Delta E$ (CIE76) formülasyonu ile hesaplayarak boya partisi kalite derecelendirmesi (Pass/Fail) yapan `ColorDifferenceAnalyzer` motorunu inşa etmektir.

---

## Engineer Research Assignment
- RGB uzayında eşit geometrik mesafelerin insan gözü tarafından eşit renk farkı olarak algılanmamasının (Non-uniformity) endüstriyel kumaş/iplik denetiminde yol açtığı tolerans hatalarını araştırmak.
- CIE $L^*a^*b^*$ uzayının $L^*$ (Açıklık/Lightness $[0, 100]$), $a^*$ (Yeşil-Kırmızı $[-128, +127]$) ve $b^*$ (Mavi-Sarı $[-128, +127]$) eksenlerinin fiziksel boya formülasyonlarındaki karşılıklarını incelemek.
- $\Delta E$ renk farkı standartlarının endüstriyel kalite eşiklerini belirlemek:
  - $\Delta E < 1.0$: İnsan gözüyle ayırt edilemeyen mükemmel eşleşme.
  - $\Delta E \le 2.5$: Ticari dokuma ve iplik boyama için kabul edilebilir sınır.
  - $\Delta E > 5.0$: Müşteri tarafından iade sebebi sayılan kritik ton sapması (Red).
- HSV uzayında ton (Hue $[0, 180^\circ]$) ve doygunluk (Saturation $[0, 255]$) bileşenlerinin aydınlatma değişimlerine karşı dayanıklılığını test etmek.

---

## Concepts
- **Algısal Homojenlik (Perceptual Uniformity):** Renk uzayındaki matematiksel Öklid mesafesinin insanın hissettiği renk farkıyla orantılı olması.
- **CIE $L^*a^*b^*$ Renk Uzayı:** Cihazdan bağımsız, insan görme eşiğini referans alan endüstriyel standart renk uzayı.
- **$\Delta E$ (CIE76) Renk Farkı:**
  $$\Delta E_{ab}^* = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}$$
- **HSV (Hue-Saturation-Value) Uzayı:** Rengin türünü (H), saflığını (S) ve parlaklığını (V) ayrıştıran silindirik renk modeli.
- **Endüstriyel Boya Partisi Toleransı:** Referans iplik standardı ile gelen bobin numunesi arasındaki renk tutarlılığı testi.

---

## Libraries
- `opencv-python` (`cv2`): `COLOR_BGR2Lab`, `COLOR_BGR2HSV` dönüşümleri.
- `numpy`: 3B tensör matrisleri ve Öklid normu (`np.linalg.norm`).
- `pytest`: Renk uzayı dönüşümü ve $\Delta E$ eşik testleri.

---

## Functions / Classes Studied
- `ColorDifferenceAnalyzer`, `bgr_to_cielab()`, `bgr_to_hsv()`, `delta_e_cie76()`
- `ColorDifferenceAnalyzer.grade_color_match()`
- `cv2.cvtColor()`, `np.linalg.norm()`

---

## Notebook
- **Dosya:** [`day10_renk_uzaylari_ve_farki.ipynb`](day10_renk_uzaylari_ve_farki.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). BGR'den Lab ve HSV'ye geçişi, $\Delta E$ hesaplamasını ve boya partisi kabul/red testlerini adım adım inceler.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `color-spaces-and-delta-e-grading`
- **Modüller:**
  - `src/color_difference.py`: Temel renk uzayı dönüşümleri, $\Delta E$ (CIE76) hesaplayıcı ve `ColorDifferenceAnalyzer`.
  - `src/conversions.py`: BGR, RGB, CIELAB, HSV renk uzayı dönüşüm motoru (`ColorConverter`).
  - `src/delta_e.py`: Endüstriyel boya partisi kalite derecelendirmesi yapan `DeltaECalculator` (PASS, WARNING, REJECT).
  - `src/ciede2000.py`: ISO/CIE 11664-6:2014 CIEDE2000 algısal renk farkı motoru (`ciede2000_scalar`, `ciede2000_vectorized`).
  - `src/thresholding.py`: `HSVColorThresholder`, `MaskMorphologyCleaner`, `PerceptualDeltaEThresholder`.
  - `src/analyzer.py`: Uçtan uca boya partisi drift denetimi ve renk kompozisyonu (`CarpetColorAnalyzer`).
  - `src/generator.py`: Sentetik boya partisi halı fikstürleri üretici (`SyntheticCarpetPaletteGenerator`).
  - `src/yarn_matcher.py` & `src/yarn_catalog_models.py`: Sertifikalı iplik kataloğu eşleştirme ve bobin atama.
  - `src/cli.py`: Terminal komut arayüzü ve benchmark orkestratörü.
  - `tests/test_color_analysis.py`: 10 birim test (dönüşümler, eşikleme, drift, CLI benchmark).
  - `tests/test_color_difference.py`: 3 birim test (dönüşüm, özdeşlik, tolerans grading).

---

## Architecture
```
day10/
├── README.md
├── day10_renk_uzaylari_ve_farki.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── color_config.json
    ├── fixtures/
    │   └── synthetic_carpets/
    │       ├── carpet_palette_master.png
    │       ├── carpet_lot_drift_pass.png
    │       ├── carpet_lot_drift_warning.png
    │       └── carpet_lot_drift_reject.png
    ├── src/
    │   ├── __init__.py
    │   ├── analyzer.py
    │   ├── ciede2000.py
    │   ├── color_difference.py
    │   ├── color_models.py
    │   ├── conversions.py
    │   ├── delta_e.py
    │   ├── generator.py
    │   ├── thresholding.py
    │   ├── yarn_catalog_models.py
    │   ├── yarn_matcher.py
    │   └── cli.py
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_color_analysis.py
    │   └── test_color_difference.py
    └── outputs/
        ├── dye_lot_inspection_report.json
        ├── color_analysis_benchmark.json
        └── color_analysis_summary.md
```

---

## Experiments
1. **$\Delta E$ Özdeşlik Deneyi:**
   - Aynı Lab vektörü kendisiyle kıyaslandığında $\Delta E$ tam $0.0$ olarak hesaplandı.
2. **Endüstriyel Boya Toleransı Kabul/Red Deneyi:**
   - Referans BGR $[200, 100, 50]$ ile yakın numune $[202, 101, 51]$ kıyaslandığında $\Delta E < 3.0$ bulundu ve `is_acceptable: True` ("ACCEPTABLE") kararı verildi.
   - Uzak numune $[50, 200, 200]$ kıyaslandığında $\Delta E > 10.0$ çıktı ve `is_acceptable: False` ("REJECTED") kararıyla elendi.
3. **Boya Partisi (Dye Lot) Drift Denetimi Deneyi:**
   - Master palete kıyasla Pass partisinde $\Delta E < 2.0$, Warning partisinde $2.0 < \Delta E \le 5.0$, Reject partisinde $\Delta E > 5.0$ tespit edilerek otomatik kalite kararları üretildi.

---

## Validation
- Pytest ile 13 adet birim test icra edildi:
  - `test_color_conversions_accuracy`
  - `test_delta_e_cie76_identical_and_known`
  - `test_delta_e_tolerance_grading`
  - `test_hsv_thresholding_hue_wraparound`
  - `test_hsv_illumination_invariance`
  - `test_cielab_delta_e_thresholding_mask`
  - `test_mask_morphological_cleanup`
  - `test_carpet_color_composition_sum`
  - `test_dye_lot_drift_detection`
  - `test_cli_color_analysis_pipeline_and_artifacts`
  - `test_color_space_conversions`
  - `test_delta_e_identical`
  - `test_color_difference_grading`
- Tüm testler **%100 başarıyla (13 passed)** geçti.

---

## Results
- Boya partisi sapmalarını insan gözü algısıyla tam uyumlu olarak denetleyen $\Delta E$ (CIE76) ve CIEDE2000 kalite kontrol modülü geliştirilmiştir.
- BGR kanalının yanıltıcı etkileri giderilerek CIE $L^*a^*b^*$ standardına geçilmiş; aydınlatma değişimlerine karşı HSV ve morfolojik segmentasyon temizliği sağlanmıştır.

---

## Limitations
- Ölçümler standart sentetik ve kalibre edilmiş halı modelleri üzerinden simüle edilmiştir.
- Geometrik distorsiyon ve kamera açısı düzeltmeleri homografi aşamasında (Day 12) devreye alınacaktır.

---

## Files
- `day10/README.md`
- `day10/day10_renk_uzaylari_ve_farki.ipynb`
- `day10/mini_project/README.md`
- `day10/mini_project/configs/color_config.json`
- `day10/mini_project/fixtures/synthetic_carpets/`
- `day10/mini_project/src/__init__.py`
- `day10/mini_project/src/analyzer.py`
- `day10/mini_project/src/ciede2000.py`
- `day10/mini_project/src/color_difference.py`
- `day10/mini_project/src/color_models.py`
- `day10/mini_project/src/conversions.py`
- `day10/mini_project/src/delta_e.py`
- `day10/mini_project/src/generator.py`
- `day10/mini_project/src/thresholding.py`
- `day10/mini_project/src/yarn_catalog_models.py`
- `day10/mini_project/src/yarn_matcher.py`
- `day10/mini_project/src/cli.py`
- `day10/mini_project/tests/__init__.py`
- `day10/mini_project/tests/conftest.py`
- `day10/mini_project/tests/test_color_analysis.py`
- `day10/mini_project/tests/test_color_difference.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day10/mini_project/tests/ -v

# Boya partisi analiz benchmark'ını çalıştırma
python -m day10.mini_project.src.cli benchmark
```

---

## Next Day
- **Day 11:** Renk Kuantizasyonu ve Palet Çıkarma — K-Means ile renk kümeleme, renk paletleri ve renk indirgeme.