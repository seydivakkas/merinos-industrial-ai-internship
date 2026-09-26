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
  - `src/color_difference.py`: Renk uzayı dönüşümleri, $\Delta E$ hesaplayıcı ve `ColorDifferenceAnalyzer`.
  - `src/corner_detector.py`, `src/homography.py`, `src/rectifier.py`: Destekleyici geometrik analitik araçları.
  - `tests/test_color_difference.py`: Renk uzayı ve $\Delta E$ tolerans testleri.
  - `tests/test_corner_detector.py`, `tests/test_rectification.py`: Geometrik yardımcı testler.

---

## Architecture
```
day10/
├── README.md
├── day10_renk_uzaylari_ve_farki.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── color_difference.py
    │   ├── corner_detector.py
    │   ├── homography.py
    │   ├── rectifier.py
    │   └── models.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_color_difference.py
    │   ├── test_corner_detector.py
    │   └── test_rectification.py
    └── outputs/
```

---

## Experiments
1. **$\Delta E$ Özdeşlik Deneyi:**
   - Aynı Lab vektörü kendisiyle kıyaslandığında $\Delta E$ tam $0.0$ olarak hesaplandı.
2. **Endüstriyel Boya Toleransı Kabul/Red Deneyi:**
   - Referans BGR $[200, 100, 50]$ ile yakın numune $[202, 101, 51]$ kıyaslandığında $\Delta E < 3.0$ bulundu ve `is_acceptable: True` ("ACCEPTABLE") kararı verildi.
   - Uzak numune $[50, 200, 200]$ kıyaslandığında $\Delta E > 10.0$ çıktı ve `is_acceptable: False` ("REJECTED") kararıyla elendi.

---

## Validation
- Pytest ile 13 adet birim test icra edildi:
  - `test_color_space_conversions`
  - `test_delta_e_identical`
  - `test_color_difference_grading`
  - `test_corner_detector_*`, `test_rectification_*`
- Tüm testler **%100 başarıyla (13 passed)** geçti.

---

## Results
- Boya partisi sapmalarını insan gözü algısıyla tam uyumlu olarak denetleyen $\Delta E$ kalite kontrol modülü geliştirilmiştir.
- BGR kanalının yanıltıcı etkileri giderilerek CIE $L^*a^*b^*$ standardına geçilmiştir.

---

## Limitations
- Bu aşamada klasik CIE76 Öklid formülü kullanılmıştır; kroma ve ton asimetrilerini düzelten daha gelişmiş CIEDE2000 formülü ileri aşamalarda karşılaştırma amaçlı değerlendirilebilir.
- Ölçümler standart sentetik BGR pikselleri üzerinden simüle edilmiştir.

---

## Files
- `day10/README.md`
- `day10/day10_renk_uzaylari_ve_farki.ipynb`
- `day10/mini_project/README.md`
- `day10/mini_project/src/__init__.py`
- `day10/mini_project/src/color_difference.py`
- `day10/mini_project/tests/__init__.py`
- `day10/mini_project/tests/test_color_difference.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day10/mini_project/tests/ -v
```

---

## Next Day
- **Day 11:** K-Means ile Baskın Renk ve Palet Çıkarımı — Piksel kümeleme, iplik bobini (creel) tahsisi ve renk kuantizasyonu.