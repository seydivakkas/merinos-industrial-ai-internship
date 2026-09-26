# Day 05 — Pandas ve Veri Hattı: Çok Kaynaklı Veri Bütünleştirme ve Veri Kalitesi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Pandas ve Veri Hattı: Çok Kaynaklı Veri Bütünleştirme ve Veri Kalitesi (Yaprak 9 & 10)

## Goal
Bu günün amacı, Merinos üretim sahasında ortaya çıkan çok kaynaklı heterojen verileri (dokuma tezgâhı telemetrisi, vardiya çizelgeleri, iplik bobin lotları ve kalite kontrol formları) Pandas kütüphanesi ile birleştirmek; veri kalitesini tamlık (completeness), geçerlilik (validity) ve tutarlılık (consistency) boyutlarında denetleyen, hatalı kayıtları karantinaya ayıran ve eksik değerleri impute eden otomatik bir veri boru hattı (`PandasDataPipeline`) inşa etmektir.

---

## Engineer Research Assignment
- Endüstriyel sensör kesintilerinde veya operatör veri giriş hatalarında eksik verilerin doğrudan satır silme (drop) yerine istatistiksel imputasyon (medyan/ortalama) ile tamamlanmasının makine öğrenmesi modelleri üzerindeki etkilerini araştırmak.
- Fiziksel sınırların dışına çıkan (örneğin motor sıcaklığı <10°C veya >120°C, pnömatik basınç tolerans dışı) hatalı telemetri kayıtlarının boru hattını çökertmeden karantinaya (`quarantine_df`) ayrılması mimarisini tasarlamak.
- Çok kaynaklı tabular veri setlerinin tezgâh kimliği (`loom_id`) ve zaman damgası üzerinden kayıpsız birleştirilmesinde (inner vs outer join) referans bütünlüğü risklerini analiz etmek.
- Veri kalitesi metriklerini nicel bir sağlık puanına (`DataQualityReport`) dönüştürmek.

---

## Concepts
- **Veri Kalitesi Boyutları:**
  - **Tamlık (Completeness):** Veri kümesindeki hücrelerin eksik (NaN/Null) olmama oranı.
  - **Geçerlilik (Validity):** Nümerik değerlerin tanımlı fiziksel veya endüstriyel aralık sınırları içerisinde bulunması.
  - **Tutarlılık (Consistency):** İlişkili tablolar arasında yabancı anahtar (foreign key) ve format uyumu.
- **Karantina Ayrımı (Quarantine Isolation):** Hatalı veya sınır dışı kayıtların temiz analiz kümesinden ayrı bir veri çerçevesine (`quarantine_df`) taşınarak loglanması.
- **İstatistiksel İmputasyon (Imputation):** Eksik verilerin dağılımı bozmadan kolon medyanı ile doldurulması.
- **Çok Kaynaklı Veri Entegrasyonu:** Farklı sistemlerden toplanan operasyonel kayıtların Pandas `merge`/`join` yöntemleriyle birleştirilmesi.

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
- `PandasDataPipeline.clean_and_profile()`
- `pd.DataFrame.merge()`, `pd.DataFrame.fillna()`, `pd.DataFrame.isnull()`, `pd.Series.between()`
- `CarpetPatternGenerator`, `BenchmarkEngine`, `MemoryLayoutAnalyzer`

---

## Notebook
- **Dosya:** [`day05_pandas_ve_veri_kalitesi.ipynb`](day05_pandas_ve_veri_kalitesi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Çok kaynaklı verilerin temizlenmesi, karantina ayrımı ve kalite metriklerinin hesaplanmasını adım adım gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `pandas-data-pipeline-and-quality`
- **Modüller:**
  - `src/pandas_pipeline.py`: `PandasDataPipeline` ve `DataQualityReport` sınıfları.
  - `src/generator.py`: Sentetik dokuma tezgâhı ve halı matrisi üreteci.
  - `src/benchmark.py`: Veri işleme gecikme ve bellek tüketim analiz motoru.
  - `src/memory_analyzer.py`: Tabular ve tensör veri bellek düzeni analiz modülü.
  - `src/operations.py`: Temel nümerik veri dönüşümleri.
  - `tests/test_pandas_pipeline.py`: Veri kalitesi, eksik veri ve karantina testleri.
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
    ├── src/
    │   ├── __init__.py
    │   ├── pandas_pipeline.py
    │   ├── generator.py
    │   ├── benchmark.py
    │   ├── memory_analyzer.py
    │   └── operations.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_pandas_pipeline.py
    │   └── test_benchmarks.py
    └── outputs/
```

---

## Experiments
1. **Veri Kalitesi ve Karantina Deneyi:**
   - 5 satırlık tezgâh telemetri verisinde eksik değer (`NaN`) içeren satır tespit edildi ve başarıyla medyan ile tamamlandı.
   - Tanımlı sıcaklık sınırının (120°C) üzerinde olan (145.0°C) aykırı kayıt `quarantine_df` kümesine aktarılarak temiz veriden ayrıştırıldı.
   - Tamlık skoru %95.0, geçerlilik skoru %80.0 olarak hesaplandı.
2. **Boş Veri Çerçevesi Hata Denetimi:**
   - Boş DataFrame verildiğinde boru hattının `ValueError` fırlattığı doğrulandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_pandas_pipeline_cleaning_and_quality_report`
  - `test_empty_dataframe_raises_value_error`
  - `test_benchmarks_*` (vektörize işlemler ve bellek analizleri)
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Çok kaynaklı üretim verilerinin eksik ve sınır dışı değerlerden arındırılarak güvenli analiz kümesine dönüştürülmesi temin edilmiştir.
- Hatalı tezgâh verileri karantinaya alınarak model eğitimi için veri bütünlüğü garanti altına alınmıştır.

---

## Limitations
- İleri aşamalarda gerçek zamanlı akış motorları (Stream processing) yerine bu günde batch (toplu) tabular veri kümeleri üzerinde çalışılmıştır.
- Veri kalitesi denetimi sentetik endüstriyel telemetri kayıtları üzerinden doğrulanmıştır.

---

## Files
- `day05/README.md`
- `day05/day05_pandas_ve_veri_kalitesi.ipynb`
- `day05/mini_project/README.md`
- `day05/mini_project/src/__init__.py`
- `day05/mini_project/src/pandas_pipeline.py`
- `day05/mini_project/src/generator.py`
- `day05/mini_project/src/benchmark.py`
- `day05/mini_project/src/memory_analyzer.py`
- `day05/mini_project/src/operations.py`
- `day05/mini_project/tests/__init__.py`
- `day05/mini_project/tests/test_pandas_pipeline.py`
- `day05/mini_project/tests/test_benchmarks.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day05/mini_project/tests/ -v
```

---

## Next Day
- **Day 06:** NumPy ve Vektörel Hesaplama: Büyük Ölçekli Matris İşlemleri ve Performans — SIMD vektörizasyonu, bellek düzeni (C vs Fortran) ve broadcasting optimizasyonu.