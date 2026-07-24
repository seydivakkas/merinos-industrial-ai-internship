# Day 04 Mini Project: Otomatik Veri Kalitesi Doğrulama ve Profilleme Hattı (Expectation Suites & Profiling)

Bu mini proje, Merinos fabrikasyon ve veri hazırlık süreçlerinde üretim logları, sensör telemetrisi ve ürün katalog verilerinin otomatik olarak istatistiksel profillenmesini, deklaratif kalite kuralları (Expectation Suites) ile şema/değer/dağılım düzeyinde doğrulanmasını ve interaktif bir HTML veri paneli üretilmesini sağlayan kurumsal bir veri güvence (Data Quality & Observability) motorudur.

---

## 📁 Proje Yapısı

```bash
day04/mini_project/
├── configs/
│   └── expectation_suite_config.json      # Deklaratif kalite beklentileri ve tolerans aralıkları
├── fixtures/
│   ├── clean_production_data.csv          # Beklentileri %100 karşılayan temiz referans veri seti
│   ├── dirty_production_data.csv          # Null, duplicate, sınır dışı boyutlar içeren anomali seti
│   └── drifted_production_data.csv        # Tezgâh tansiyon kaymasını modelleyen drift veri seti
├── src/
│   ├── __init__.py
│   ├── expectations.py                    # Deklaratif kural primitifleri (Null, Unique, Between, InSet, Regex, Mean)
│   ├── suite.py                           # ExpectationSuite derleyicisi ve SuiteValidator
│   ├── profiler.py                        # AutomatedDataProfiler (İstatistiksel analiz & HTML raporlayıcı)
│   └── pipeline.py                        # DataQualityPipeline orkestratörü
├── tests/
│   ├── __init__.py
│   └── test_quality_validation.py         # 10 birim ve entegrasyon testi
├── outputs/
│   ├── validation_report.json             # Kural kural detaylı doğrulama çıktısı
│   ├── data_profile.json                  # Sütun metrikleri, dağılımlar ve bellek özeti
│   ├── data_quality_dashboard.html        # Bağımsız, modern CSS interaktif HTML gösterge paneli
│   └── anomalous_records.csv              # Kurallara takılan izole edilmiş satırlar
└── README.md                              # Bu dokümantasyon
```

---

## ⚙️ Bileşenler ve Mimari

1. **Expectation Engine (`src/expectations.py`):**
   - `ExpectTableRowCountToBeBetween`: Satır sayısının minimum ve maksimum sınırlar arasında olduğunu denetler.
   - `ExpectColumnValuesToNotBeNull`: Sütunlardaki eksik değerleri tespit eder, `mostly` tolerans oranı desteği sunar.
   - `ExpectColumnValuesToBeUnique`: Birincil anahtarların (`product_id`) tekilliğini garantiler.
   - `ExpectColumnValuesToBeBetween`: Halı eni, boyu ve hav yüksekliği gibi fiziksel değerlerin spesifikasyon sınırlarında olduğunu doğrular.
   - `ExpectColumnValuesToBeInSet`: Malzeme ve koleksiyonların izin verilen katalog kümesinde olduğunu denetler.
   - `ExpectColumnValuesToMatchRegex`: Ürün kodu (`^MRP-[0-9]{4}$`) ve hex renk kodlarının (`^#[0-9A-Fa-f]{6}$`) doğruluğunu denetler.
   - `ExpectColumnMeanToBeBetween`: Sayısal sütunların aritmetik ortalamasını denetleyerek tezgâh kalibrasyon ve dağılım kaymalarını (drift) yakalar.

2. **Expectation Suite & Validator (`src/suite.py`):**
   - JSON konfigürasyon dosyasını parse eder, kuralları nesneye dönüştürür.
   - Pandas DataFrame üzerinde kuralları vektörize ve optimize şekilde çalıştırarak `ValidationResult` çıktısı üretir.

3. **Automated Data Profiler (`src/profiler.py`):**
   - Bellek tüketimi, mükerrer kayıtlar, hücre bazlı eksiklik oranları, sayısal sütunlarda min, Q25, medyan, Q75, max, çarpıklık ve sıfır oranlarını hesaplar.
   - Kategorik sütunlarda en sık görülen değerleri ve metin uzunluk dağılımlarını çıkarır.
   - Sıfır dış CDN bağımlılığıyla çalışan, modern koyu temalı tek sayfalık interaktif HTML dashboard (`data_quality_dashboard.html`) üretir.

4. **Kalite Hattı Orkestratörü (`src/pipeline.py`):**
   - Veriyi alır, profiller, doğrular, aykırı satırları `anomalous_records.csv`'ye ayırır ve kümülatif Veri Kalite Skorunu ($Q_{\text{score}}$) hesaplar.

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day04/mini_project/tests/ -v
```

## 🚀 Boru Hattını Çalıştırma

```bash
python -m day04.mini_project.src.pipeline
```
Çıktılar `day04/mini_project/outputs/` dizininde otomatik oluşturulur.
