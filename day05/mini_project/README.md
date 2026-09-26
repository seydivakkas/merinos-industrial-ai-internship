# Day 05 — Mini Project: Pandas Data Pipeline and Data Quality

## Genel Bakış
Bu mini proje, çok kaynaklı üretim verilerini (CSV üretim logları ve JSON halı katalog kayıtları) Pandas ile birleştiren, normalleştiren, eksik/aykırı değerleri karantinaya ayıran ve Great Expectations benzeri kural kümeleri (`ExpectationSuite`) ile istatistiksel veri kalitesi profillemesi (`AutomatedDataProfiler`) yapan kapsamlı bir veri mühendisliği boru hattıdır.

> **Veri Güvenliği ve Sentetik Kuralı:** Gerçek endüstriyel veri veya canlı SCADA bağlantısı yoktur. Tüm telemetri ve katalog beslemeleri sentetiktir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/pandas_pipeline.py`: Pandas tabular temizleme, eksik veri tamamlama ve karantina ayrımı.
- `src/parsers.py`: CSV ve JSON veri kaynakları ayrıştırıcıları.
- `src/normalizer.py`: Nümerik veri ölçekleyici ve standartlaştırıcı.
- `src/etl_pipeline.py`: Çok kaynaklı ETL boru hattı (`DataIngestionPipeline`).
- `src/expectations.py`: Sütun düzeyinde doğrulama beklentileri (Null, Benzersizlik, Aralık, Regex vb.).
- `src/suite.py`: Beklenti paketi yöneticisi ve sonuç toplayıcı (`ExpectationSuite`, `SuiteValidator`).
- `src/profiler.py`: Otomatik istatistiksel profilleyici (`AutomatedDataProfiler`).
- `src/quality_pipeline.py`: Kalite denetim hattı (`DataQualityPipeline`).
- `src/generator.py`: Sentetik desen ve dokuma matrisi üreteci.
- `src/benchmark.py`: Vektörizasyon ve işlem süresi karşılaştırma motoru.
- `src/memory_analyzer.py`: Bellek düzeni ve tüketim analizörü.
- `src/operations.py`: Temel nümerik operasyonlar.

## Testler
- `tests/test_pandas_pipeline.py`: Veri kalitesi, eksik veri ve karantina testleri.
- `tests/test_etl_pipeline.py`: Çok kaynaklı ayrıştırma, birleştirme ve karantina testleri.
- `tests/test_quality_validation.py`: Kural paketleri ve profilleme motoru testleri.
- `tests/test_benchmarks.py`: Nümerik manipülasyon ve başarım testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -v
```
