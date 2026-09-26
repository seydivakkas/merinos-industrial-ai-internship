# Day 04 — Python Geliştirme Ortamı ve Veri Sözleşmesi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Python Geliştirme Ortamı ve Veri Sözleşmesi (Yaprak 7 & 8)

---

## Goal
Bu günün amacı, Python geliştirme ortamında izole sanal ortam (venv) ve deterministik bağımlılık yönetimini kurmak; tezgâh telemetrileri ve ürün teknik şartnamelerinden gelen verilerin sistem sınırında (inbound validation) katı bir Veri Sözleşmesi (Data Contract) ile denetlenmesini sağlamaktır. Pydantic v2 kütüphanesi kullanılarak tip güvenliği, alan düzeyinde (`field_validator`) ve model düzeyinde (`model_validator`) doğrulamalar ile endüstriyel veri kalitesi kurallarını hayata geçirmektir.

---

## Engineer Research Assignment
- Kurumsal üretim ortamında Python sanal ortamlarının (venv), bağımlılık kitleme ve deterministik ortam tekrarlanabilirliğindeki kritik rolünü incelemek.
- Tezgâh sensörlerinden (sıcaklık, pnömatik basınç, çözgü gerginliği) veya operatör panellerinden gelen verilerin sisteme girmeden sınırda (inbound validation) reddedilmesinin boru hattı çöküşlerini nasıl engellediğini modellemek.
- Pydantic v2 ile fiziksel kısıtların (örn. tezgah en-boy oranı tolerans sınırı, geçerli HEX renk formatı, motor termal eşikleri) çalışma zamanı mikro-saniyelik doğrulamalarını kodlamak.
- Yerel çalışma istasyonunun donanım profilini (CPU, RAM, hızlandırıcılar) ve paket bağımlılıklarını yazılımsal olarak denetleyen modülleri (`env_checker`, `environment_profiler`, `repo_bootstrap`) kurgulamak.

---

## Concepts
- **Sanal Ortam İzolasyonu (Virtual Environment):** Proje bağımlılıklarını sistem düzeyindeki paketlerden izole ederek sürüm çatışmalarını engelleme.
- **Deterministik Bağımlılık Denetimi:** Python sürümü ve zorunlu kütüphanelerin mevcudiyetini ve sürümlerini çalışma zamanında denetleme.
- **Veri Sözleşmesi (Data Contract):** Veri üreten sistemler ile tüketen yapay zekâ boru hatları arasında kesin ve bağlayıcı şema mutabakatı.
- **Sınırda Doğrulama (Inbound Validation):** Hatalı verinin veri tabanına veya model eğitimine ulaşmadan API sınırında yakalanması.
- **Alan ve Model Düzeyinde Doğrulayıcılar (Field & Model Validators):** Regex ile HEX renk kodu denetimi ve çoklu alan oran kısıtları (en-boy mekanik dokuma sınırı).

---

## Libraries
- `pydantic` (v2): Katı şema tanımları, tip güvenliği ve mikro-saniye seviyesinde çalışma zamanı validasyonu.
- `psutil`: Sistem belleği ve CPU çekirdek profillemesi.
- `platform`, `sys`, `importlib.metadata`: Python sürümü ve paket metaveri sorgulama.
- `datetime`: UTC zaman damgası yönetimi ve zaman serisi hizalaması.
- `re`: HEX renk kodları ve kimlik biçimleri için düzenli ifadeler.
- `pytest`: Sözleşme ve ortam validasyonu birim testleri.

---

## Functions / Classes Studied
- `CarpetSpecificationContract`, `LoomTelemetryContract`, `ContractValidationError`
- `EnvironmentChecker`, `EnvironmentProfiler`, `RepositoryBootstrap`
- `pydantic.BaseModel`, `pydantic.ConfigDict`, `pydantic.Field`
- `pydantic.field_validator`, `pydantic.model_validator`
- `psutil.virtual_memory()`, `os.cpu_count()`

---

## Notebook
- **Dosya:** [`day04_python_ortami_ve_veri_sozlesmesi.ipynb`](day04_python_ortami_ve_veri_sozlesmesi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Pydantic v2 sözleşmelerini, tezgah telemetrisini, ortam profillemesini ve sınır kontrollerini interaktif olarak simüle eder.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `python-environment-and-data-contracts`
- **Modüller:**
  - `src/data_contracts.py`: `CarpetSpecificationContract` ve `LoomTelemetryContract` modelleri.
  - `src/env_checker.py`: Python sürümü, GPU/CUDA durumu ve paket bağımlılıklarını denetleyen sınıf.
  - `src/environment_profiler.py`: İş istasyonu donanım profilini ve veri türleri envanterini denetleyen profilleyici.
  - `src/repo_bootstrap.py`: Depo dizin ve dosya yapısı sözleşmesini doğrulayan motor.
  - `src/models.py`: Ortam denetim sonuçları ve sistem gereksinimleri modelleri.
  - `configs/env_spec.json`: Python sürümü, asgari donanım ve zorunlu paket gereksinimleri konfigürasyonu.
  - `configs/environment_config.json`: Ortam çalışma konfigürasyonu.
  - `tests/test_data_contracts.py`: Sözleşme ve fiziksel kısıt testleri.
  - `tests/test_env_checker.py`: Ortam ve bağımlılık denetimi testleri.
  - `tests/test_environment_profiler.py`: Donanım profili testleri.

> *Not:* Veri kalitesi beklenti paketi ve profilleme motoru (`expectations.py`, `profiler.py`, `suite.py`, `pipeline.py`) müfredat uyumu doğrultusunda **Day 05 (Pandas, Veri Hattı ve Veri Kalitesi)** projesiyle birleştirilmiştir.

---

## Architecture
```
day04/
├── README.md
├── day04_python_ortami_ve_veri_sozlesmesi.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   ├── env_spec.json
    │   └── environment_config.json
    ├── src/
    │   ├── __init__.py
    │   ├── data_contracts.py
    │   ├── env_checker.py
    │   ├── environment_profiler.py
    │   ├── models.py
    │   └── repo_bootstrap.py
    └── tests/
        ├── __init__.py
        ├── test_data_contracts.py
        ├── test_env_checker.py
        └── test_environment_profiler.py
```

---

## Experiments
1. **Sözleşme Doğrulama ve Fiziksel Sınır Deneyi:**
   - Halı en-boy oranı dokuma tezgahı mekanik sınırını (6:1) aştığında model seviyesi validatörün (`validate_aspect_ratio`) hatayı sınırda engellediği görüldü.
   - Hatalı HEX renk kodları (`#GG1122`) regex validatörü tarafından reddedildi.
2. **Ortam Denetimi Deneyi:**
   - `EnvironmentChecker` ile Python sürümü, donanım kaynakları ve paket gereksinimleri test edildi.
3. **Donanım Profilleme Deneyi:**
   - `EnvironmentProfiler` ile yerel CPU çekirdek sayısı, RAM kapasitesi ve işletim sistemi ortamı başarıyla raporlandı.

---

## Validation
- Pytest ile 10 adet birim test icra edildi:
  - `test_valid_carpet_spec`
  - `test_invalid_hex_color_raises_validation_error`
  - `test_extreme_aspect_ratio_fails_physical_validation`
  - `test_loom_telemetry_valid`
  - `test_loom_telemetry_out_of_range_raises`
  - `test_python_version_check`
  - `test_hardware_check`
  - `test_package_check_installed_and_missing`
  - `test_repo_bootstrap_validates_structure`
  - `test_workstation_audit`
- Tüm testler **%100 başarıyla (10 passed)** geçti.

---

## Results
- Geliştirme ortamı ve bağımlılık gereksinimleri yazılımsal olarak denetlenebilir hâle getirilmiştir.
- Pydantic v2 veri sözleşmeleriyle hatalı veriler sistem sınırında filtrelenmiştir.
- Tüm veriler sentetik test senaryolarından oluşmaktadır.

---

## Limitations
- Veri sözleşmeleri yerel Python nesneleri üzerinde çalışır; Kafka veya MQTT gibi dağıtık mesaj broker entegrasyonu simülasyon düzeyindedir.
- Donanım denetimi yerel makineye özeldir.

---

## Files
- `day04/README.md`
- `day04/day04_python_ortami_ve_veri_sozlesmesi.ipynb`
- `day04/mini_project/README.md`
- `day04/mini_project/configs/env_spec.json`
- `day04/mini_project/configs/environment_config.json`
- `day04/mini_project/src/__init__.py`
- `day04/mini_project/src/data_contracts.py`
- `day04/mini_project/src/env_checker.py`
- `day04/mini_project/src/environment_profiler.py`
- `day04/mini_project/src/models.py`
- `day04/mini_project/src/repo_bootstrap.py`
- `day04/mini_project/tests/test_data_contracts.py`
- `day04/mini_project/tests/test_env_checker.py`
- `day04/mini_project/tests/test_environment_profiler.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day04/mini_project/tests/ -v
```

---

## Next Day
- **Day 05:** Pandas, Veri Hattı ve Veri Kalitesi — Çok kaynaklı veri birleştirme, eksik/aykırı veri temizliği ve otomatik kalite profilleme.