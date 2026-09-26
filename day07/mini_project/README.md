# Day 07 — Mini Project: Distance, Similarity Metrics, and k-NN Search Engine

## Genel Bakış
Bu mini proje, çok boyutlu endüstriyel öznitelik ve embedding vektörleri arasındaki geometrik benzerliği ölçmek amacıyla geliştirilmiştir. Öklid, Manhattan, Minkowski ve Kosinüs mesafelerini, Z-score / Min-Max / L2 ölçekleyicilerini, boyut laneti analiz motorunu (`CurseOfDimensionalityAnalyzer`) ve k-En Yakın Komşu vektör arama motorunu (`VectorSimilaritySearchEngine`) barındırır.

> **Veri Güvenliği ve Sentetik Kuralı:** Kurumsal veya gizli şirket verisi içermez. Tüm gömme (embedding) ve öznitelik vektörleri sentetik olarak üretilmiştir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/metrics.py`: Vektörel mesafe çekirdekleri (Öklid, Manhattan, Kosinüs, Mahalanobis).
- `src/scalers.py`: `StandardScaler`, `MinMaxScaler` ve `L2Normalizer`.
- `src/curse_analyzer.py`: Boyutlanma arttıkça mesafe daralması analitiği.
- `src/search.py`: Çoklu metrikli k-NN benzerlik arama motoru.
- `src/distance_similarity.py`: Mesafe fonksiyonları ve `KNNPatternMatcher`.
- `src/generator.py`: Sentetik desen üreteci.
- `tests/test_similarity.py`: Uzaklık metrikleri ve arama motoru testleri.
- `tests/test_distance_similarity.py`: Temel mesafe ve k-NN testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -v
```
