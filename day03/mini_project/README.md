# Day 03 Mini Project: Çok Kaynaklı Veri İşleme Hattı (Pandas, CSV/JSON Parser & Normalizer)

Bu mini proje, Merinos fabrikasyon ortamında farklı sistemlerden (dokuma tezgahı PLC/SCADA CSV logları ve tasarım/e-ticaret JSON katalog beslemeleri) gelen ham verileri birleştiren (merge), temizleyen, birim dönüşümlerini gerçekleştiren ve Day 02'de tanımlanan **Pydantic v2** modelleri ile doğrulayan bir ETL (Extract, Transform, Load) boru hattıdır.

---

## 📁 Proje Yapısı

```bash
day03/mini_project/
├── configs/
│   └── pipeline_config.json      # Birim katsayıları, toleranslar, imputation kuralları
├── fixtures/
│   ├── raw_production_logs.csv   # Tezgah üretim logları (inç/cm karışık ölçüler)
│   ├── raw_catalog_feed.json     # Tasarım/katalog JSON beslemesi (renk paletleri, koleksiyon)
│   └── dirty_records.csv         # Karantina ve stres testi için bozuk/sınır dışı veriler
├── src/
│   ├── __init__.py
│   ├── parsers.py                # Hata toleranslı CsvDataSourceParser & JsonDataSourceParser
│   ├── normalizer.py             # Birim dönüştürücü, metin/hex temizleyici, Pydantic bağlayıcı
│   └── pipeline.py               # DataIngestionPipeline orkestratörü & kalite raporlayıcı
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py          # 8 birim test (parser, dönüşümler, karantina, tam ETL)
├── outputs/
│   ├── normalized_products.json  # Pydantic ile doğrulanmış nihai ürün veri tabanı
│   ├── data_quality_report.json  # Veri kalitesi, başarı oranı ve hata dökümü raporu
│   └── quarantine_records.json   # Karantinaya alınan aykırı/hatalı kayıtlar
└── README.md                     # Bu dokümantasyon
```

---

## ⚙️ Boru Hattı Akışı ve Kuralları

1. **Çıkarma (Extract - `parsers.py`):**
   - CSV ve JSON kaynakları bağımsız olarak okunur.
   - Bozuk satırlar veya eksik birincil anahtarlar (`product_id`) anında `quarantine_records` listesine yönlendirilir.
2. **Birleştirme (Transform/Merge - `pipeline.py`):**
   - `product_id` / `product_code` üzerinden Pandas ile Full Outer Join yapılır.
3. **Normalizasyon (Transform - `normalizer.py`):**
   - **Birim Dönüşümü:** İnç cinsinden gelen ölçüler ($2.54$) ile, milimetre ölçüler ($0.1$) ile santimetreye çevrilir.
   - **Metin Temizliği:** Fazla boşluklar atılır, koleksiyon adları Title Case formatına getirilir.
   - **Hex Renk Formatı:** Kısa 3 basamaklı hex kodları (`#RGB` -> `#RRGGBB`) 7 karaktere genişletilir ve büyük harfe çevrilir.
   - **Malzeme Eşleme:** "yün" -> `WOOL`, "akrilik" -> `ACRYLIC`, "bambu" -> `BAMBOO_SILK` vb.
4. **Doğrulama ve Karantina (Validate & Load):**
   - Kayıtlar `CarpetProduct` Pydantic modeline dökülür.
   - Şema kuralını ihlal eden satırlar (negatif boyut, geçersiz ID formatı, uç en-boy oranı vb.) reddedilir ve nedenleriyle birlikte `quarantine_records.json` içine yazılır.
   - Geçerli kayıtlar `normalized_products.json` içine kaydedilir ve genel bir `data_quality_report.json` üretilir.

---

## 🚀 Nasıl Çalıştırılır?

### 1. Testleri Koşturma
```bash
python -m pytest day03/mini_project/tests/ -v
```

### 2. Boru Hattını Çalıştırma
```bash
python -m day03.mini_project.src.pipeline
```

Çıktılar `day03/mini_project/outputs/` dizininde otomatik oluşturulur.
