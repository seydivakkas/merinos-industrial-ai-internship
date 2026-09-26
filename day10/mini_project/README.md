# Merinos Renk Uzayları ve Algısal Renk Farkı Analiz Motoru (Mini Proje)

> **Modül:** Day 10 Mini Project  
> **Konu:** RGB, HSV, CIE $L^*a^*b^*$ Uzayları, $\Delta E$ (CIE76) / CIEDE2000 Algısal Renk Farkı ve Boya Partisi Muayenesi  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 📌 Genel Bakış

Merinos boyahane ve dokuma tesislerinde iplik ve halı yüzeylerinin renk kalitesini matematiksel ve algısal olarak denetleyen modüler bir sistemdir. Donanım tabanlı RGB/BGR renk uzayının homojen olmama sorununu gidermek üzere insan görme sistemini modelleyen CIE $L^*a^*b^*$ ve renk tonu/doygunluğunu ayrıştıran HSV uzaylarına dönüşüm yapar; iki numune arasındaki algısal renk sapmasını $\Delta E$ (CIE76) ve ISO/CIE 11664-6:2014 CIEDE2000 formülasyonu ile hesaplayarak boya partisi kalite derecelendirmesi (PASS, WARNING, REJECT) sunar.

Bu mini proje:
1. **Renk Uzayı Dönüşümleri (`ColorConverter` & `color_difference`):** BGR, RGB, CIELAB ve HSV dönüşümleri gerçekleştirir.
2. **Algısal Renk Farkı Hesaplayıcıları (`DeltaECalculator` & `ciede2000`):** CIE76 Öklid mesafesi ve CIEDE2000 formülasyonu ile endüstriyel boya partisi tolerans derecelendirmesi (PASS $\le 2.0$, WARNING $\le 5.0$, REJECT $> 5.0$) yapar.
3. **Renk Eşikleme ve Morfoloji (`HSVColorThresholder`, `PerceptualDeltaEThresholder`):** Renk tonu süreksizliği (Hue wrap-around) gözeten HSV ve CIELAB $\Delta E$ tabanlı iplik segmentasyonu ve morfolojik temizlik uygular.
4. **Halı Renk Kompozisyonu ve Boya Sapma Denetimi (`CarpetColorAnalyzer`):** Halı yüzeyindeki iplik renk kompozisyon oranlarını (`%`) ve referans master palete göre boya partisi sapma miktarını denetler.
5. **İplik Kataloğu Eşleştirme (`YarnMatcher`):** Çıkarılan renkleri fabrika sertifikalı bobin kataloğu ile eşleştirir.

---

## 📁 Dizin Yapısı

```
day10/mini_project/
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

## 🚀 CLI Kullanımı

### 1. Renk Analizi ve Boya Partisi Muayenesi
```bash
python -m day10.mini_project.src.cli inspect --image fixtures/synthetic_carpets/carpet_lot_drift_warning.png
```

### 2. İki Renk / Numune Arasında Delta E Hesaplama
```bash
python -m day10.mini_project.src.cli delta-e --ref 76 43 26 --sample 82 48 32
```

### 3. Kapsamlı Benchmark ve Rapor Üretimi
```bash
python -m day10.mini_project.src.cli benchmark
```

---

## 🧪 Birim Testleri

```bash
python -m pytest day10/mini_project/tests/ -v
```

13 birim testi şunları doğrular:
1. `test_color_conversions_accuracy`: BGR -> RGB -> CIELAB -> HSV dönüşümlerinin sayısal doğruluğu.
2. `test_delta_e_cie76_identical_and_known`: Özdeş renklerde $\Delta E = 0.0$ ve bilinen fark doğrulaması.
3. `test_delta_e_tolerance_grading`: PASS, WARNING ve REJECT tolerans sınıflandırması.
4. `test_hsv_thresholding_hue_wraparound`: Kırmızı renk için dairesel ($0^\circ \leftrightarrow 180^\circ$) çift aralık eşiklemesi.
5. `test_hsv_illumination_invariance`: Değişen aydınlatma altında HSV ton kararlılığı.
6. `test_cielab_delta_e_thresholding_mask`: $\Delta E$ tabanlı hassas piksel maskesi çıkarma.
7. `test_mask_morphological_cleanup`: Açma/kapama morfolojisi ile iplik gürültüsü temizleme.
8. `test_carpet_color_composition_sum`: Segmentasyon oranlarının toplamının $\%100$ etmesi.
9. `test_dye_lot_drift_detection`: Dört farklı boya partisinin drift analizinin doğruluğu.
10. `test_cli_color_analysis_pipeline_and_artifacts`: CLI benchmark ve JSON/Markdown rapor bütünlüğü.
11. `test_color_space_conversions`: Temel BGR, LAB ve HSV dönüşüm testleri.
12. `test_delta_e_identical`: Temel sıfır mesafe testi.
13. `test_color_difference_grading`: Tolerans eşik testi.
