# Day 04 — Python Geliştirme Ortamı ve Veri Sözleşmesi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Python Geliştirme Ortamı ve Veri Sözleşmesi (Yaprak 7 & 8)

## Goal
Bu günün amacı, Python geliştirme ortamında izole sanal ortam (venv) ve deterministik bağımlılık yönetimini kurmak; tezgâh telemetrileri ve ürün teknik şartnamelerinden gelen verilerin sistem sınırında (inbound validation) katı bir Veri Sözleşmesi (Data Contract) ile denetlenmesini sağlamaktır. Pydantic v2 kütüphanesi kullanılarak tip güvenliği, alan düzeyinde (`field_validator`) ve model düzeyinde (`model_validator`) doğrulamalar ile endüstriyel veri kalitesi kurallarını hayata geçirmektir.

---

## Engineer Research Assignment
- Kurumsal üretim ortamında Python sanal ortamlarının (venv), bağımlılık kitleme ve deterministik ortam tekrarlanabilirliğindeki kritik rolünü incelemek.
- Tezgâh sensörlerinden (sıcaklık, pnömatik basınç, çözgü gerginliği) veya operatör panellerinden gelen verilerin sisteme girmeden sınırda (inbound validation) reddedilmesinin boru hattı çöküşlerini nasıl engellediğini modellemek.
- Pydantic v2 ile fiziksel kısıtların (örn. tezgah en-boy oranı tolerans sınırı, geçerli HEX renk formatı, motor termal eşikleri) çalışma zamanı mikro-saniyelik doğrulamalarını kodlamak.
- Veri kalitesi beklenti kümeleri (Expectation Suites) ve profilleme motoru ile veri bütünlüğünü otomatik test etmek.

---

## Concepts
- **Sanal Ortam İzolasyonu (Virtual Environment):** Proje bağımlılıklarını sistem düzeyindeki paketlerden izole ederek sürüm çatışmalarını engelleme.
- **Veri Sözleşmesi (Data Contract):** Veri üreten sistemler ile tüketen yapay zekâ boru hatları arasında kesin ve bağlayıcı şema mutabakatı.
- **Sınırda Doğrulama (Inbound Validation):** Hatalı verinin veri tabanına veya model eğitimine ulaşmadan API sınırında yakalanması.
- **Alan ve Model Düzeyinde Doğrulayıcılar (Field & Model Validators):** Regex ile HEX renk kodu denetimi ve çoklu alan oran kısıtları (en-boy mekanik dokuma sınırı).
- **Veri Kalitesi Beklentileri (Expectations & Profiling):** Eksik veri oranları, benzersizlik, aralık sınırları ve dağılım istatistiklerinin otomatik denetimi.

---

## Libraries
- `pydantic` (v2): Katı şema tanımları, tip güvenliği ve mikro-saniye seviyesinde çalışma zamanı validasyonu.
- `datetime`: UTC zaman damgası yönetimi ve zaman serisi hizalaması.
- `re`: HEX renk kodları ve kimlik biçimleri için düzenli ifadeler.
- `pandas`: Tabular veri işleme ve kalite profillemesi.
- `pytest`: Sözleşme ve kalite validasyonu birim testleri.

---

## Functions / Classes Studied
- `CarpetSpecificationContract`, `LoomTelemetryContract`, `ContractValidationError`
- `pydantic.BaseModel`, `pydantic.ConfigDict`, `pydantic.Field`
- `pydantic.field_validator`, `pydantic.model_validator`
- `BaseExpectation`, `ExpectationSuite`, `SuiteValidator`, `AutomatedDataProfiler`, `DataQualityPipeline`

---

## Notebook
- **Dosya:** [`day04_python_ortami_ve_veri_sozlesmesi.ipynb`](day04_python_ortami_ve_veri_sozlesmesi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Pydantic v2 sözleşmelerini, tezgah telemetrisini ve sınır kontrollerini interaktif olarak simüle eder.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `data-contracts-and-quality-validation`
- **Modüller:**
  - `src/data_contracts.py`: `CarpetSpecificationContract` ve `LoomTelemetryContract` modelleri.
  - `src/expectations.py`: Sütun bazlı veri kalitesi beklenti sınıfları.
  - `src/suite.py`: Beklenti paketleri ve doğrulama motoru.
  - `src/profiler.py`: Otomatik veri kalitesi profilleyicisi.
  - `src/pipeline.py`: Uçtan uca veri kalitesi denetim hattı.
  - `tests/test_data_contracts.py`: Sözleşme ve fiziksel kısıt testleri.
  - `tests/test_quality_validation.py`: Beklenti paketi ve profilleme testleri.

---

## Architecture
```
day04/
├── README.md
├── day04_python_ortami_ve_veri_sozlesmesi.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── data_contracts.py
    │   ├── expectations.py
    │   ├── suite.py
    │   ├── profiler.py
    │   └── pipeline.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_data_contracts.py
    │   └── test_quality_validation.py
    └── outputs/
```

---

## Experiments
1. **Fiziksel En-Boy Oranı Sınır Deneyi:**
   - Genişlik 100 cm, uzunluk 700 cm verildiğinde (oran 7:1, maksimum izin verilen 6:1), `validate_aspect_ratio` kuralı tetiklenmiş ve sözleşme hatası fırlatılmıştır.
2. **HEX Renk Paleti Format Deneyi:**
   - Geçersiz renk kodu (`"RED-99"` veya `"#XYZ123"`) verildiğinde alan validatörü regex kontrolüyle hatayı sınırda yakalamıştır.
3. **Telemetri Termal ve Basınç Eşikleri:**
   - Motor sıcaklığı >120°C veya basınç <5 bar olan tezgâh kayıtları Pydantic doğrulamasından geçmeyerek elenmiştir.

---

## Validation
- Pytest ile 13 adet birim test icra edildi:
  - `test_valid_carpet_specification_contract`
  - `test_invalid_hex_code_raises_validation_error`
  - `test_aspect_ratio_exceeded_raises_error`
  - `test_valid_loom_telemetry_contract`
  - `test_invalid_loom_telemetry_temperature_out_of_bounds`
  - `test_column_not_null_expectation`
  - `test_column_values_between_expectation`
  - `test_column_values_in_set_expectation`
  - `test_suite_validator_execution`
  - `test_profiler_generates_suite`
  - `test_data_quality_pipeline_quarantine`
- Tüm testler **%100 başarıyla (13 passed)** geçti.

---

## Results
- Üretim telemetrileri ve halı ürün özellikleri tip güvenli, doğrulanabilir Pydantic v2 sözleşmelerine bağlanmıştır.
- Veri kalitesi beklenti paketiyle geçersiz kayıtlar karantinaya alınarak boru hattı güvenliği sağlanmıştır.

---

## Limitations
- Doğrulama kuralları yerel bellek üzerinde Pydantic modelleriyle yürütülmüştür; yüksek debili mesaj kuyrukları (Kafka/MQTT) ile entegrasyon ilerleyen fazlarda ele alınacaktır.
- Veriler sentetik dokuma tezgahı sensör simülasyonlarından derlenmiştir.

---

## Files
- `day04/README.md`
- `day04/day04_python_ortami_ve_veri_sozlesmesi.ipynb`
- `day04/mini_project/README.md`
- `day04/mini_project/src/__init__.py`
- `day04/mini_project/src/data_contracts.py`
- `day04/mini_project/src/expectations.py`
- `day04/mini_project/src/suite.py`
- `day04/mini_project/src/profiler.py`
- `day04/mini_project/src/pipeline.py`
- `day04/mini_project/tests/__init__.py`
- `day04/mini_project/tests/test_data_contracts.py`
- `day04/mini_project/tests/test_quality_validation.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day04/mini_project/tests/ -v
```

---

## Next Day
- **Day 05:** Pandas ve Veri Hattı: Çok Kaynaklı Veri Bütünleştirme ve Veri Kalitesi — Heterojen veri kaynaklarının birleştirilmesi ve eksik veri analizleri.