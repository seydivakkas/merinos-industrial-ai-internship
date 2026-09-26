# Day 05 — Pandas ve Veri Hattı: Çok Kaynaklı Veri Bütünleştirme ve Veri Kalitesi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Pandas ve Veri Hattı: Çok Kaynaklı Veri Bütünleştirme ve Veri Kalitesi (Yaprak 9 & 10)

---

## Goal
Bu günün amacı, Merinos üretim sahasında ortaya çıkan çok kaynaklı heterojen verileri (dokuma tezgâhı telemetrisi, vardiya çizelgeleri, iplik bobin lotları ve kalite kontrol formları) Pandas kütüphanesi ile birleştirmek; veri kalitesini tamlık (completeness), geçerlilik (validity) ve tutarlılık (consistency) boyutlarında denetleyen, hatalı kayıtları karantinaya ayıran ve eksik değerleri impute eden otomatik bir veri boru hattı (`PandasDataPipeline`, `DataIngestionPipeline`, `DataQualityPipeline`) inşa etmektir.

---

## Engineer Research Assignment
- Endüstriyel sensör kesintilerinde veya operatör veri giriş hatalarında eksik verilerin doğrudan satır silme (drop) yerine istatistiksel imputasyon (medyan/ortalama) ile tamamlanmasının makine öğrenmesi modelleri üzerindeki etkilerini araştırmak.
- Fiziksel sınırların dışına çıkan (örneğin motor sıcaklığı <10°C veya >120°C, pnömatik basınç tolerans dışı) hatalı telemetri kayıtlarının boru hattını çökertmeden karantinaya (`quarantine_df`) ayrılması mimarisini tasarlamak.
- Çok kaynaklı tabular veri setlerinin tezgâh kimliği (`loom_id`) ve zaman damgası üzerinden kayıpsız birleştirilmesinde (inner vs outer join) referans bütünlüğü risklerini analiz etmek.
- Büyük ölçekli veri kalite beklenti kümelerini (Expectation Suites) ve profilleme motorunu veri hattına entegre etmek.

---

## Concepts
- **Veri Kalitesi Boyutları:**
  - **Tamlık (Completeness):** Veri kümesindeki hücrelerin eksik (NaN/Null) olmama oranı.
  - **Geçerlilik (Validity):** Nümerik değerlerin tanımlı fiziksel veya endüstriyel aralık sınırları içerisinde bulunması.
  - **Tutarlılık (Consistency):** İlişkili tablolar arasında yabancı anahtar (foreign key) ve format uyumu.
- **Karantina Ayrımı (Quarantine Isolation):** Hatalı veya sınır dışı kayıtların temiz analiz kümesinden ayrı bir veri çerçevesine (`quarantine_df`) taşınarak loglanması.
- **İstatistiksel İmputasyon (Imputation):** Eksik verilerin dağılımı bozmadan kolon medyanı ile doldurulması.
- **Çok Kaynaklı Veri Entegrasyonu:** Farklı sistemlerden toplanan operasyonel kayıtların Pandas `merge`/`join` yöntemleriyle birleştirilmesi.
- **Otomatik Veri Profilleme ve Beklenti Kümeleri:** Sütun dağılımları, tipleri ve sınır değerlerinin otomatik kural kümeleriyle doğrulanması.

---

## Libraries
- `pandas`: Tabular veri manipülasyonu, filtreleme, birleştirme ve eksik veri analitiği.
- `numpy`: Sayısal vektörizasyon, NaN değer yönetimi ve istatistiksel fonksiyonlar.
- `pydantic` (v2): Veri kalitesi rapor şeması ve sözleşme modelleri.
- `pathlib`: Dosya ve veri yolları yönetimi.
- `pytest`: Veri kalitesi ve boru hattı birim testleri.

---

## Functions / Classes Studied
- `PandasDataPipeline`, `DataQualityReport`
- `CsvDataSourceParser`, `JsonDataSourceParser`, `DataNormalizer`
- `DataIngestionPipeline`, `DataQualityPipeline`
- `BaseExpectation`, `ExpectationSuite`, `SuiteValidator`, `AutomatedDataProfiler`
- `pd.DataFrame.merge()`, `pd.DataFrame.fillna()`, `pd.DataFrame.isnull()`, `pd.Series.between()`

---

## Notebook
- **Dosya:** [`day05_pandas_ve_veri_kalitesi.ipynb`](day05_pandas_ve_veri_kalitesi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Çok kaynaklı verilerin temizlenmesi, karantina ayrımı, eksik veri tamamlama ve kalite metriklerinin hesaplanmasını adım adım gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `pandas-data-pipeline-and-quality`
- **Modüller:**
  - `src/pandas_pipeline.py`: `PandasDataPipeline` ve `DataQualityReport` sınıfları.
  - `src/parsers.py`: Çok kaynaklı CSV ve JSON veri ayrıştırıcıları (`CsvDataSourceParser`, `JsonDataSourceParser`).
  - `src/normalizer.py`: Nümerik ölçekleme ve standartlaştırma (`DataNormalizer`).
  - `src/etl_pipeline.py`: CSV telemetri ve JSON katalog beslemelerini birleştiren ETL hattı (`DataIngestionPipeline`).
  - `src/expectations.py`: Sütun bazlı veri kalitesi kural ve beklenti sınıfları.
  - `src/suite.py`: Kural paketleri ve otomatik doğrulama motoru (`ExpectationSuite`, `SuiteValidator`).
  - `src/profiler.py`: İstatistiksel veri profilleme motoru (`AutomatedDataProfiler`).
  - `src/quality_pipeline.py`: Uçtan uca veri kalitesi denetim hattı (`DataQualityPipeline`).
  - `src/generator.py`: Sentetik dokuma tezgâhı ve halı matrisi üreteci.
  - `src/benchmark.py`: Veri işleme gecikme ve bellek tüketim analiz motoru.
  - `src/memory_analyzer.py`: Tabular ve tensör veri bellek düzeni analiz modülü.
  - `src/operations.py`: Temel nümerik veri dönüşümleri.
  - `tests/test_pandas_pipeline.py`: Veri kalitesi, eksik veri ve karantina testleri.
  - `tests/test_etl_pipeline.py`: Çok kaynaklı ayrıştırma, birleştirme ve karantina testleri.
  - `tests/test_quality_validation.py`: Beklenti paketleri ve profilleme motoru testleri.
  - `tests/test_benchmarks.py`: Nümerik manipülasyon ve başarım testleri.

---

## Architecture
```
day05/
├── README.md
├── day05_pandas_ve_veri_kalitesi.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   ├── etl_pipeline_config.json
    │   └── expectation_suite_config.json
    ├── fixtures/
    │   ├── clean_production_data.csv
    │   ├── dirty_production_data.csv
    │   ├── dirty_records.csv
    │   ├── drifted_production_data.csv
    │   ├── raw_catalog_feed.json
    │   ├── raw_production_logs.csv
    │   └── synthetic_patterns.npz
    ├── src/
    │   ├── __init__.py
    │   ├── benchmark.py
    │   ├── etl_pipeline.py
    │   ├── expectations.py
    │   ├── generator.py
    │   ├── memory_analyzer.py
    │   ├── normalizer.py
    │   ├── operations.py
    │   ├── pandas_pipeline.py
    │   ├── parsers.py
    │   ├── profiler.py
    │   ├── quality_pipeline.py
    │   └── suite.py
    └── tests/
        ├── __init__.py
        ├── test_benchmarks.py
        ├── test_etl_pipeline.py
        ├── test_pandas_pipeline.py
        └── test_quality_validation.py
```

---

## Experiments
1. **Çok Kaynaklı Veri Entegrasyonu ve Karantina:**
   - 10 telemetri kaydı ile 5 katalog kaydı başarıyla birleştirildi; hatalı kayıtlar temiz kümeden karantinaya ayrıldı.
2. **Eksik Veri ve Tip Dönüşümü:**
   - Boş hücreler kolon medyanı ile impute edildi; `quality_score` metriği hesaplandı.
3. **Veri Kalitesi Beklenti Kümeleri Doğrulaması:**
   - Değer aralıkları, regex desenleri ve benzersizlik kuralları `ExpectationSuite` ile denetlendi.

---

## Validation
- Pytest ile 29 adet birim test icra edildi:
  - `test_pandas_pipeline.py` (2 test)
  - `test_benchmarks.py` (10 test)
  - `test_etl_pipeline.py` (8 test)
  - `test_quality_validation.py` (9 test)
- Tüm testler **%100 başarıyla (29 passed)** geçti.

---

## Results
- Heterojen veri kaynakları kayıpsız birleştirildi, eksik ve aykırı veriler güvenle yönetildi.
- Otomatik kalite raporlama ve kural doğrulama altyapısı kuruldu.
- Tüm veriler sentetik test senaryolarından oluşmaktadır.

---

## Limitations
- Veriler yerel Pandas DataFrame nesneleri üzerinde işlenmiştir; Spark veya Dask gibi dağıtık büyük veri işleme araçları Faz 1 kapsamında değildir.
- Gerçek zamanlı akış yerine mikro-küme (batch) simülasyonu uygulanmıştır.

---

## Files
- `day05/README.md`
- `day05/day05_pandas_ve_veri_kalitesi.ipynb`
- `day05/mini_project/README.md`
- `day05/mini_project/src/__init__.py`
- `day05/mini_project/src/pandas_pipeline.py`
- `day05/mini_project/src/etl_pipeline.py`
- `day05/mini_project/src/parsers.py`
- `day05/mini_project/src/normalizer.py`
- `day05/mini_project/src/expectations.py`
- `day05/mini_project/src/suite.py`
- `day05/mini_project/src/profiler.py`
- `day05/mini_project/src/quality_pipeline.py`
- `day05/mini_project/src/generator.py`
- `day05/mini_project/src/benchmark.py`
- `day05/mini_project/src/memory_analyzer.py`
- `day05/mini_project/src/operations.py`
- `day05/mini_project/tests/test_pandas_pipeline.py`
- `day05/mini_project/tests/test_etl_pipeline.py`
- `day05/mini_project/tests/test_quality_validation.py`
- `day05/mini_project/tests/test_benchmarks.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day05/mini_project/tests/ -v
```

---

## Next Day
- **Day 06:** NumPy ve Vektörel Hesaplama — Tensör temsilleri, matris operasyonları ve CPU vektörizasyonu.