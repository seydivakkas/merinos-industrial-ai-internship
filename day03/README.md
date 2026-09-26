# Day 03 — Problemin Bilgisayar Mühendisliği Açısından Tanımlanması

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Problemin Bilgisayar Mühendisliği Açısından Tanımlanması (Yaprak 5 & 6)

---

## Goal
Bu günün amacı, Merinos halı üretim tesisinde karşılaşılan mühendislik problemlerini biçimsel olarak tanımlamak; girdi (input contract), beklenen çıktı (output contract), hedef optimizasyon metriği (Accuracy, Top-1 Precision) ve gecikme toleransı (Latency SLA) sınırlarını netleştirmektir. Geliştirilecek herhangi bir yapay zekâ modelinin başarısını ölçmek üzere en basit başlangıç yöntemi (baseline heuristic) referansını belirlemek ve aday modellerin baseline'a göre göreceli kazancını (relative improvement) nesnel olarak hesaplamaktır.

---

## Engineer Research Assignment
- "Halılar benzer mi?" veya "Tezgahta atkı hatası var mı?" gibi gayriresmî soruları, bilgisayar mühendisliği açısından doğrulanabilir biçimsel girdi ve çıktı sözleşmelerine dönüştürmek.
- Basit bir başlangıç yönteminin (örneğin çoğunluk sınıfı tahmini veya sabit kural tabanlı sezgisel eşikleme) belirlenmesinin model geliştirme sürecindeki vazgeçilmezliğini araştırmak.
- Karmaşık bir modelin sağladığı doğruluk artışını, ek hesaplama maliyeti ve gecikme (latency SLA) parametreleriyle karşılaştıran bir değerlendirici (`BaselineEvaluator`) kurgulamak.
- Sentetik problem tanımları üzerinde kural tabanlı başlangıç modellerini (`MajorityClassBaseline`, `MeanThresholdBaseline`) çalıştırarak baseline metriklerini hesaplamak.

---

## Concepts
- **Biçimsel Problem Şartnamesi (Problem Specification):** Sistemin çözeceği görevin kimliği, hedefleri ve kısıtlarının açıkça tanımlanması.
- **Girdi / Çıktı Sözleşmesi (Input/Output Contract):** Sistemin kabul edeceği veri tipleri (örn: `ndarray`, `float`) ile üreteceği yanıt biçiminin (örn: `List[Tuple[str, float]]`, `bool`) kesin sınırları.
- **Başarı Ölçütü (Evaluation Metric):** Algoritmanın doğruluğunu ölçen nicel kriterler (Doğruluk, Hassasiyet, F1 skoru, SLA gecikme süresi).
- **En Basit Başlangıç Yöntemi (Baseline Heuristic):** Sıfır veya asgari maliyetle elde edilen referans performans; her aday model bu eşiği anlamlı şekilde aşmak zorundadır.
- **Göreceli Kazanç (Relative Improvement):** Aday modelin baseline skoru üzerine sağladığı yüzdesel iyileşme $((M_{cand} - M_{base}) / M_{base}) \times 100$.

---

## Libraries
- `pydantic` (v2): Problem şartnamesi ve değerlendirme modelleri şemaları.
- `typing`: Tip açıklamaları ve sözleşme tanımları.
- `pathlib`: Dosya ve konfigürasyon yolları yönetimi.
- `numpy`: Sayısal eşik hesaplamaları.
- `json`: Şartname ve karşılaştırma sonuçlarının serileştirilmesi.
- `pytest`: Birim testleri ve değerlendirme senaryoları.

---

## Functions / Classes Studied
- `ProblemSpecification`, `EvaluationComparison`, `BaselineEvaluator`
- `MajorityClassBaseline`, `MeanThresholdBaseline`
- `BaselineEvaluator.evaluate()`
- `pydantic.BaseModel`, `pydantic.Field`

---

## Notebook
- **Dosya:** [`day03_problem_tanimi_ve_baseline.ipynb`](day03_problem_tanimi_ve_baseline.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Halı benzerliği ve kusur tespiti problemlerinin şartnameye dökülmesini ve baseline karşılaştırmasını interaktif olarak gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `problem-specification-and-baseline`
- **Modüller:**
  - `src/problem_spec.py`: `ProblemSpecification`, `EvaluationComparison` ve `BaselineEvaluator` sınıfları.
  - `src/baseline.py`: `MajorityClassBaseline` ve `MeanThresholdBaseline` sezgisel referans modelleri.
  - `configs/problem_definitions.json`: Örnek endüstriyel problem şartnameleri bildirimi.
  - `tests/test_problem_spec.py`: Şartname doğrulama, baseline modelleri ve göreceli kazanç testleri.

> *Not:* ETL veri boru hattı, parser ve normalizasyon modülleri (`parsers.py`, `normalizer.py`, `pipeline.py`) müfredat uyumu doğrultusunda **Day 05 (Pandas, Veri Hattı ve Veri Kalitesi)** projesiyle birleştirilmiştir.

---

## Architecture
```
day03/
├── README.md
├── day03_problem_tanimi_ve_baseline.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── problem_definitions.json
    ├── src/
    │   ├── __init__.py
    │   ├── problem_spec.py
    │   └── baseline.py
    └── tests/
        ├── __init__.py
        └── test_problem_spec.py
```

---

## Experiments
1. **Baseline Karşılaştırma Deneyi (Atkı Kusur Tespiti):**
   - Hedef problem: Dokuma tezgahı atkı hatası tespiti (`PROB-DEFECT-01`).
   - Basit baseline (sabit çoğunluk tahmini): %50.0 doğruluk, 0.01 ms gecikme.
   - Aday model: %90.0 doğruluk, 1.25 ms gecikme.
   - Sonuç: Aday model baseline'a göre %80.0 göreceli kazanç sağladı ve gecikme SLA limitinin (10.0 ms) altında kalarak üstün bulundu (`is_candidate_superior: true`).
2. **Sözleşme Uyuşmazlığı ve Hata Yönetimi:**
   - Tahmin ve yer doğrusu liste uzunlukları uyuşmadığında `BaselineEvaluator` sınıfının `ValueError` fırlattığı doğrulandı.
3. **Kural Tabanlı Eşikleme Baseline:**
   - `MeanThresholdBaseline`, ortalama değerin %20 üzerine çıkan sentetik anomalileri doğru tespit etti.

---

## Validation
- Pytest ile 4 adet birim test icra edildi:
  - `test_baseline_evaluator_candidate_wins`
  - `test_baseline_evaluator_validation_error_on_mismatched_lengths`
  - `test_majority_class_baseline`
  - `test_mean_threshold_baseline`
- Tüm testler **%100 başarıyla (4 passed)** geçti.

---

## Results
- Problem şartnameleri ve girdi/çıktı sözleşmeleri başarıyla standardize edilmiştir.
- Sezgisel baseline kıyaslamasıyla aday modellerin getirdiği katma değerin nesnel ölçümü temin edilmiştir.
- Tüm veriler sentetik test senaryolarından oluşmaktadır.

---

## Limitations
- Aday tahminler simüle edilmiş benchmark listeleridir; derin öğrenme modellerinin kendisi Faz 2 ve Faz 3'te entegre edilecektir.
- Gecikme ölçümleri yerel simülasyon ortamında CPU üzerinden ölçülmüştür.

---

## Files
- `day03/README.md`
- `day03/day03_problem_tanimi_ve_baseline.ipynb`
- `day03/mini_project/README.md`
- `day03/mini_project/configs/problem_definitions.json`
- `day03/mini_project/src/__init__.py`
- `day03/mini_project/src/problem_spec.py`
- `day03/mini_project/src/baseline.py`
- `day03/mini_project/tests/test_problem_spec.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day03/mini_project/tests/ -v
```

---

## Next Day
- **Day 04:** Python Ortamı ve Veri Sözleşmesi — Çalışma ortamı profilleme ve Pydantic v2 veri sözleşmeleri.