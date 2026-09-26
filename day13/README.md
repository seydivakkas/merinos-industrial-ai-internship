# Day 13 — Morfolojik İşlemler, Kenar ve Çizgi Tespiti

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Morfolojik İşlemler ve Kenar Tespiti (Yaprak 25 & 26)

## Goal
Bu günün amacı, Merinos jakarlı halı dokuma ve konfeksiyon hatlarında ortaya çıkan mikro dokuma hatalarını (iplik kopuşu, delik/patlak, düğüm/slub, yağ lekesi) matematiksel morfoloji (aşındırma, genişletme, açma, kapama, Top-Hat ve Black-Hat dönüşümleri) ile izole etmek; aynı zamanda Sobel, Scharr, Laplacian ve Canny kenar gradyan filtreleri ile Olasılıksal Hough Çizgi Dönüşümü (`HoughLinesP`) algoritmalarını birleştirerek halı bordür paralelliğini, kenar doğrusallığını ve 90° ortogonalitesini gerçek zamanlı denetleyen endüstriyel `CarpetBorderAnalyzer` ve `CarpetDefectDetector` motorlarını inşa etmektir.

---

## Engineer Research Assignment
- İkili (binary) kumaş maskelerinde izole gürültü noktalarını yok eden Açma ($A \circ B = (A \ominus B) \oplus B$) ile küçük delik ve çatlakları dolduran Kapama ($A \bullet B = (A \oplus B) \ominus B$) operatörlerinin $3 \times 3$ ve $5 \times 5$ yapısal elemanlarla davranışını incelemek.
- Beyaz Tepe Şapkası (White Top-Hat: $I - (I \circ B)$) ile parlak düğüm/slub hatalarını, Siyah Tepe Şapkası (Black Top-Hat: $(I \bullet B) - I$) ile koyu delik ve iplik kopuşlarını yerel zemin gradyanından bağımsız olarak ayrıştırmak.
- Gradyan operatörlerinin rotasyonel izotropisini (Sobel vs. Scharr vs. Laplacian) ve Canny çift eşikli histerezis ($T_{\text{low}}, T_{\text{high}}$) dinamiklerini karşılaştırmak.
- Hough parametre uzayında ($r, \theta$) çizgileri kümeleyerek üst, alt, sol ve sağ bordürleri doğrusal regrese etmek; tezgâhtaki atkı eğriliği (weft bow/skew) sapmalarını hesaplamak.

---

## Concepts
- **Aşındırma (Erosion) ve Genişletme (Dilation):**
  $$(A \ominus B) = \{z \mid (B)_z \subseteq A\}, \quad (A \oplus B) = \{z \mid (\hat{B})_z \cap A \neq \emptyset\}$$
- **Top-Hat Dönüşümleri:**
  - **White Top-Hat:** Yapısal elemandan daha küçük parlak anomalileri (düğüm, yabancı elyaf) filtreler.
  - **Black Top-Hat:** Yapısal elemandan daha küçük koyu anomalileri (delik, iplik kopuğu, yağ lekesi) filtreler.
- **Canny Kenar Tespiti:** Gauss yumuşatma, yönlü gradyan, yerel olmayan maksimumların bastırılması (NMS) ve çift eşikli histerezis adımları.
- **Olasılıksal Hough Dönüşümü (Probabilistic Hough Transform):** Kenar piksellerinden geçen doğruları sonlu doğru parçaları ($x_1, y_1, x_2, y_2$) olarak döndürür.
- **Bordür Paralelliği ve Ortogonalite:** Karşılıklı bordürlerin açısal farkı $\Delta\theta \le 0.50^\circ$ ve komşu bordürlerin iç açısı $|90^\circ - \theta| \le 0.75^\circ$ endüstriyel kabul kriteridir.

---

## Libraries
- `opencv-python` (`cv2`): `morphologyEx()`, `Sobel()`, `Scharr()`, `Laplacian()`, `Canny()`, `HoughLinesP()`.
- `numpy`: 2B/3B matrisler, gradyan yön açıları ve vektörel çizgi filtreleme.
- `pydantic`: Tip kontrollü endüstriyel rapor ve kusur veri modelleri.
- `pytest`: 22 kapsamlı birim ve entegrasyon testi.

---

## Functions / Classes Studied
- `MorphologyEngine`, `MorphologyEdgeEngine`, `CarpetDefectDetector`
- `EdgeOperatorEngine`, `HoughLineEngine`, `CarpetBorderAnalyzer`
- `CarpetBorderFixtureGenerator`, `create_woven_fabric_texture`, `inject_hole`, `inject_yarn_break`
- `LineSegment`, `BorderEdge`, `BorderParallelismReport`, `DetectedDefect`, `MorphologyInspectionReport`

---

## Notebook
- **Dosya:** [`day13_morfoloji_ve_kenar.ipynb`](day13_morfoloji_ve_kenar.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Sentetik dokuma deseninde aşındırma, genişletme, Canny kenar tespiti ve dikey/yatay çizgi tespitini adım adım gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `morphology-edge-and-line-engine`
- **Modüller:**
  - `src/morphology_engine.py`: Temel morfolojik operasyonlar (erode, dilate, open, close, tophat, blackhat).
  - `src/morphology_lines.py`: `MorphologyEdgeEngine` sınıfı.
  - `src/defect_detector.py`: Endüstriyel `CarpetDefectDetector` pipeline motoru.
  - `src/edge_operators.py`: Sobel, Scharr, Laplacian ve Canny kenar motoru.
  - `src/hough_engine.py`: Olasılıksal Hough ve bordür kümeleme motoru.
  - `src/border_analyzer.py`: Uçtan uca `CarpetBorderAnalyzer` bordür paralellik analizörü.
  - `src/generator.py`: Sentetik bordür ve dokuma kusur fikstür jeneratörleri.
  - `src/cli.py`: Birleşik Day 13 komut satırı arayüzü.
  - `configs/border_config.json`, `configs/defect_config.json`: Tolerans konfigürasyonları.

---

## Architecture
```
day13/
├── README.md
├── day13_morfoloji_ve_kenar.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   ├── border_config.json
    │   └── defect_config.json
    ├── fixtures/
    │   ├── borders/
    │   │   ├── carpet_border_broken_edge.png
    │   │   ├── carpet_border_clean_parallel.png
    │   │   ├── carpet_border_skewed_angular.png
    │   │   └── carpet_border_wavy_distortion.png
    │   └── defects/
    │       ├── carpet_clean_reference.png
    │       ├── carpet_defect_hole_puncture.png
    │       ├── carpet_defect_oil_slub.png
    │       └── carpet_defect_yarn_break.png
    ├── src/
    │   ├── __init__.py
    │   ├── border_analyzer.py
    │   ├── border_cli.py
    │   ├── border_generator.py
    │   ├── border_models.py
    │   ├── cli.py
    │   ├── defect_cli.py
    │   ├── defect_detector.py
    │   ├── defect_generator.py
    │   ├── defect_models.py
    │   ├── edge_operators.py
    │   ├── generator.py
    │   ├── hough_engine.py
    │   ├── models.py
    │   ├── morphology_engine.py
    │   └── morphology_lines.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_edge_lines.py
    │   ├── test_morphology_defects.py
    │   └── test_morphology_lines.py
    └── outputs/
```

---

## Experiments
1. **Morfolojik Alan Değişimi ve Filtreleme:**
   - $50 \times 50$ zeminde $10 \times 10$ kareye $3 \times 3$ aşındırma uygulandığında $8 \times 8$ alana indiği (`eroded.sum() < img.sum()`); genişletme uygulandığında $8 \times 8$ nesnenin büyüdüğü doğrulandı.
2. **Top-Hat ile Kumaş Hatalarını Yakalama:**
   - White Top-Hat ile dokuma düğümleri zemin dokusundan tamamen ayrıştırıldı; Black Top-Hat ile iplik kopukları ve delikler lokalize edildi.
3. **Bordür Paralellik ve Ortogonalite Analizi:**
   - Sentetik paralel halıda $0.50^\circ$ altı paralellik sapması ile `ACCEPT` kararı üretildi; 1.85° açısal eğikliğe sahip bozuk halıda `REJECT` kararı başarıyla tetiklendi.

---

## Validation
- Pytest ile 22 adet birim test icra edildi:
  - `test_edge_lines.py` (10 test: Sobel, Scharr, Laplacian, Canny, Hough, Clustering, Pass/Reject kararları)
  - `test_morphology_defects.py` (10 test: Erode, Dilate, Open, Close, Top-Hat, Black-Hat, Generator, Inspector)
  - `test_morphology_lines.py` (2 test: Temel morfoloji ve Canny/Hough doğrulaması)
- Tüm testler **%100 başarıyla (22 passed)** geçti.

---

## Results
- Jakarlı halı kumaş yüzeyindeki mikro kusurların (delik, iplik kaçığı, yağ lekesi) tespiti ve sınıflandırılması sağlanmıştır.
- Dış ve iç bordür kenarlarının paralellik ve diklik analizleri milimetrik hassasiyetle raporlanabilir hale getirilmiştir.

---

## Limitations
- Çok karmaşık çiçekli veya oryantal madalyonlu desenlerde kenarlar aşırı yoğun çıkabilir; bu tür desenlerde kenar filtreleri öncesi bilateral veya median filtreleme tercih edilmelidir.
- Testler yerel prototip sentetik fikstürler üzerinde yürütülmüştür; canlı tezgâh kamerası bağlı değildir.

---

## Files
- `day13/README.md`
- `day13/day13_morfoloji_ve_kenar.ipynb`
- `day13/mini_project/README.md`
- `day13/mini_project/configs/border_config.json`
- `day13/mini_project/configs/defect_config.json`
- `day13/mini_project/src/__init__.py`
- `day13/mini_project/src/border_analyzer.py`
- `day13/mini_project/src/cli.py`
- `day13/mini_project/src/defect_detector.py`
- `day13/mini_project/src/edge_operators.py`
- `day13/mini_project/src/generator.py`
- `day13/mini_project/src/hough_engine.py`
- `day13/mini_project/src/models.py`
- `day13/mini_project/src/morphology_engine.py`
- `day13/mini_project/src/morphology_lines.py`
- `day13/mini_project/tests/test_edge_lines.py`
- `day13/mini_project/tests/test_morphology_defects.py`
- `day13/mini_project/tests/test_morphology_lines.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day13/mini_project/tests/ -v

# Kenar tespit CLI
python -m day13.mini_project.src.cli detect-edges --image day13/mini_project/fixtures/borders/carpet_border_clean_parallel.png

# Bordür paralellik analizi
python -m day13.mini_project.src.cli analyze-borders --image day13/mini_project/fixtures/borders/carpet_border_skewed_angular.png

# Dokuma kusuru tespiti
python -m day13.mini_project.src.cli inspect-defects --input day13/mini_project/fixtures/defects/carpet_defect_hole_puncture.png
```

---

## Next Day
- **Day 14:** Klasik Görüntü Segmentasyonu — Eşikleme (Otsu), Havza (Watershed) ve GrabCut algoritmaları ile zemin-motif ayrıştırma ve Dice/IoU kıyaslaması.

---

## AI Coding Agent Prompt
"Day 13 Morfolojik İşlemler, Kenar ve Çizgi Tespiti mini projesini çalıştırın, 22 birim testi doğrulayın ve standalone jupyter notebook'u hatasız koşun."