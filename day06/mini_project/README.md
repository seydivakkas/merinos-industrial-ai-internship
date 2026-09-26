# Day 06 — Mini Project: NumPy Vectorization and Matrix Computation

## Genel Bakış
Bu mini proje, endüstriyel dokuma matrisleri ve sensör telemetrileri üzerinde saf Python döngülerinin neden olduğu işlemci yükünü ortadan kaldırmak için geliştirilmiş vektörel matris işlemleri (`ArrayOperations`), döngü vs. SIMD karşılaştırma motoru (`VectorizationBenchmark`) ve dokuma yama analitiği (`ImageMatrixToolkit`) modüllerini içerir.

> **Veri Güvenliği ve Sentetik Kuralı:** Canlı makine telemetrisi veya gerçek şirket desenleri kullanılmamaktadır. Tüm matris ve diziler sentetiktir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/array_ops.py`: Vektörel Min-Max, Z-score, matris istatistikleri, broadcasting ve eşikleme.
- `src/vectorization_benchmark.py`: Python döngüleri ile NumPy vektörel işlemlerin süre ve hızlanma karşılaştırması.
- `src/image_matrix.py`: Sentetik dokuma deseni üretimi, yama dilimleme ve enerji hesabı.
- `src/generator.py`: Sentetik özellik matris üreteci.
- `tests/test_array_ops.py`: Vektörel işlemler ve benchmark birim testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -v
```
