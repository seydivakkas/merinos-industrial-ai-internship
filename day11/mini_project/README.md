# Merinos Halı Dokuma Kusur Tespiti ve Morfolojik Operasyonlar (Mini Proje)

> **Modül:** Day 11 Mini Project  
> **Konu:** Matematiksel Morfoloji (Erosion, Dilation, Opening, Closing, Top-Hat, Black-Hat), Yönlü Çekirdekler ve Jakarlı Halı Kusur Tespiti  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 📌 Genel Bakış

Merinos Halı üretim tesislerinde tezgâhtan çıkan dokuma kumaşlarda iplik kopması (atkı/çözgü kaçığı), dokuma delikleri, iplik düğüm ve topaklanmaları (slub/knot) ile makine yağ damlamaları gibi fiziksel kusurlar meydana gelebilir. Bu kusurların insan gözüyle incelenmesi göz yorgunluğu ve hat hızları ($15-25\text{ m/dk}$) nedeniyle yetersiz kalır.

Bu mini proje:
1. **Temel Morfolojik Filtreleme (`MorphologyEngine`):** İkili ve gri seviye erozyon ($\ominus$), genişleme ($\oplus$), açma ($\circ$), kapama ($\bullet$) ve morfolojik gradyan operatörlerini yüksek hızlı SIMD desteğiyle işletir.
2. **Artık Haritalama (Residual Transforms):**
   - **Beyaz Üst Şapka (White Top-Hat):** $WTH(f) = f - (f \circ b)$ ile kumaş zemininden daha parlak olan iplik topak ve düğümlerini izole eder.
   - **Siyah Taban Şapka (Black Top-Hat):** $BTH(f) = (f \bullet b) - f$ ile kumaş zemininden daha koyu olan delik, yırtık ve yağ lekelerini izole eder.
3. **Yönlü Köprüleme Çekirdekleri (Directional Structuring Elements):**
   - Dikey çekirdek ($19 \times 1$) ile yatay atkı kaçıklarını (weft break),
   - Yatay çekirdek ($1 \times 19$) ile dikey çözgü kaçıklarını (warp break) köprüleyerek yakalar.
4. **Geometrik Sınıflandırma ve Karar Motoru (`CarpetDefectDetector`):** Tespit edilen kusurları en-boy oranı ($AR \ge 3.2$), dairesellik ve alan büyüklüğüne göre sınıflandırır; kritiklik derecesine göre rulo için `PASS / REPAIR / REJECT` kararı üretir.

---

## 📁 Dizin Yapısı

```
day11/mini_project/
├── configs/
│   └── defect_config.json           # Çekirdek boyutları, eşik değerleri ve kalite sınırları
├── fixtures/
│   └── synthetic_carpets/          # Sentetik kusurlu ve temiz kumaş numuneleri
│       ├── carpet_clean_reference.png       # Kusursuz zemin kontrol kumaşı
│       ├── carpet_defect_yarn_break.png     # Atkı ve çözgü iplik kaçığı
│       ├── carpet_defect_hole_puncture.png  # Dokuma delikleri
│       └── carpet_defect_oil_slub.png       # Yağ lekesi ve iplik düğümü
├── src/
│   ├── __init__.py
│   ├── models.py                   # Pydantic v2 veri modelleri (DefectType, Severity, Report)
│   ├── morphology_engine.py        # Temel ve gelişmiş morfoloji operatörleri
│   ├── defect_detector.py          # Kusur segmentasyonu, sınıflandırma ve görselleştirme
│   ├── generator.py                # Sentetik dokuma kumaş ve kusur üretici
│   └── cli.py                      # inspect, benchmark, generate-fixtures CLI arayüzü
├── tests/
│   ├── __init__.py
│   └── test_morphology_defects.py  # 10 kapsamlı birim ve entegrasyon testi
└── outputs/                        # Analiz çıktıları ve benchmark raporları
    ├── sample_defect_overlay.png
    ├── sample_inspection_report.json
    ├── morphology_benchmark.json
    └── morphology_summary.md
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Fikstürleri Üretme
```bash
python -m day11.mini_project.src.cli generate-fixtures
```

### 2. Halı Kumaşını İnceleme ve Kusur Raporu Üretme
```bash
python -m day11.mini_project.src.cli inspect \
    --image day11/mini_project/fixtures/synthetic_carpets/carpet_defect_hole_puncture.png \
    --output-image day11/mini_project/outputs/sample_defect_overlay.png \
    --output-report day11/mini_project/outputs/sample_inspection_report.json
```

### 3. Hız ve Throughput Benchmark Testi
```bash
python -m day11.mini_project.src.cli benchmark
```

---

## 🧪 Birim Testleri

Test paketini çalıştırmak için:
```bash
python -m pytest day11/mini_project/tests/ -v
```
Tüm 10 test morfolojik dualite, idempotentlik, yönlü çekirdek yanıtı, sıfır yalancı pozitif ve hata ciddiyet sınıflandırmasını doğrular.
