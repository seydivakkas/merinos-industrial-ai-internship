# Day 03 — Mini Project: Problem Specification, Baselines, and Success Metrics

## Genel Bakış
Bu mini proje, endüstriyel halı üretiminde karşılaşılan makine öğrenimi ve bilgisayarlı görü problemlerini biçimsel olarak şartnamelere (`ProblemSpecification`) bağlar; girdi/çıktı sözleşmelerini tanımlar ve basit sezgisel baseline (`MajorityClassBaseline`, `MeanThresholdBaseline`) yöntemleriyle aday çözümlerin göreceli kazançlarını nesnel olarak ölçer.

> **Veri Güvenliği ve Sentetik Kuralı:** Tüm problem tanımları, etiketler ve tahmin listeleri sentetiktir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/problem_spec.py`: `ProblemSpecification`, `EvaluationComparison`, `BaselineEvaluator` modelleri ve karşılaştırma mantığı.
- `src/baseline.py`: Çoğunluk sınıfı (`MajorityClassBaseline`) ve ortalama eşikleme (`MeanThresholdBaseline`) kural tabanlı modelleri.
- `configs/problem_definitions.json`: Örnek problem şartnameleri.
- `tests/test_problem_spec.py`: Problem sözleşmesi, baseline doğrulaması ve metrik testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -v
```
