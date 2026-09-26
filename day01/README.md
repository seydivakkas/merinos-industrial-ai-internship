# Day 01 — Firma ve Çalışma Ortamının Tanınması

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Firma ve Çalışma Ortamının Tanınması (Yaprak 1 & 2)

## Goal
Bu ilk günde amaç, Merinos halı üretim işletmesinde bilgisayar mühendisliği uygulama alanlarını, üretim hatlarından doğan heterojen veri türlerini (sayısal sensör telemetrisi, görsel halı yüzeyi/desen görüntüleri, teknik bakım ve işletim dokümanları) ve yerel PoC geliştirme ortamının donanım kapasitesini (CPU, RAM, Python çalışma ortamı) analiz etmektir. İlk gün oryantasyon ve yarım gün olduğundan kapsam; firma çalışma ortamının tanınması, veri modaliteleri taksonomisinin modellenmesi ve yerel geliştirme ortamının denetlenmesi ile sınırlandırılmıştır.

---

## Engineer Research Assignment
- Kurumsal bir tekstil üretim tesisinde bilgisayar mühendisliği problemlerini (sayısal telemetri, bilgisayarlı görü ve teknik dokümantasyon analitiği) sınıflandırmak.
- Heterojen veri türlerinin (yapılandırılmış sensör verileri, yarı yapılandırılmış kataloglar ve yapılandırılmamış görsel/metin verileri) depolama ve işleme gereksinimlerini karşılaştırmak.
- Yerel PoC (Proof of Concept) iş istasyonunun donanım profilini (CPU çekirdekleri, sistem belleği, CUDA hızlandırıcı varlığı) yazılımsal olarak denetleyen modüler bir profilleyici geliştirmek.
- Üretim ortamını riske atmadan sentetik ve örnek verilerle güvenli yerel geliştirme sınırlarını belirlemek.

---

## Concepts
- **Veri Modaliteleri (Modalities):** Sayısal (Numerical telemetri), Görsel (Visual halı desenleri/kamera kareleri), Metinsel (Textual teknik el kitapları ve bakım yönergeleri).
- **Sistem Profilleme (Environment Profiling):** Çalışma istasyonunun mantıksal işlemci çekirdek sayısı, RAM kapasitesi ve işletim sistemi mimarisini çalışma zamanında denetleme.
- **Deterministik Bağımlılık ve Paket Denetimi:** Python sürümü ve zorunlu kütüphanelerin mevcudiyetini doğrulamak.
- **Yerel PoC Sınırları:** Canlı SCADA ve üretim hatlarına müdahale etmeden, izole ortamda sentetik varlıklarla çalışarak geliştirme güvenliği sağlama.

---

## Libraries
- `sys`, `platform`, `importlib.metadata`: Python standart kütüphanesi ortam sorgulama araçları.
- `psutil`: İşletim sistemi süreçleri ve bellek kullanım analitiği.
- `pathlib`: İşletim sisteminden bağımsız nesne yönelimli dosya yolu yönetimi.
- `pydantic` (v2): Çalışma zamanı veri şeması, tip güvenliği ve alan doğrulama.
- `pytest`: Otomatik birim test çatısı.
- `torch`: Donanım ve CUDA kullanılabilirlik denetleyicisi.

---

## Functions / Classes Studied
- `psutil.virtual_memory()`, `os.cpu_count()`
- `sys.version_info`, `platform.system()`, `platform.machine()`
- `importlib.metadata.version()`
- `torch.cuda.is_available()`, `torch.cuda.get_device_name()`, `torch.cuda.get_device_properties()`
- `pydantic.BaseModel`, `pydantic.Field`
- `pytest.fixture`

---

## Notebook
- **Dosya:** [`day01_firma_ve_calisma_ortami.ipynb`](day01_firma_ve_calisma_ortami.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Firma çalışma ortamını, veri modalitelerini ve iş istasyonu profillemesini interaktif olarak açıklar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `environment-profiler-and-taxonomy`
- **Modüller:**
  - `src/models.py`: `DataModality`, `DataAsset`, `SystemResourceRequirements` ve `WorkstationAuditResult` veri modelleri.
  - `src/environment_profiler.py`: İş istasyonu donanım kapasitesini ve veri modalitesi envanterini denetleyen profilleyici sınıf.
  - `src/env_checker.py`: Python sürümü, donanım hızlandırıcı ve paket bağımlılıklarını denetleyen sınıf.
  - `src/repo_bootstrap.py`: Depo kök dizinindeki klasör ve sözleşme bütünlüğünü doğrulayan motor.
  - `configs/env_spec.json`: Asgari sistem ve paket gereksinimleri bildirimi.
  - `tests/test_environment_profiler.py`: Varlık sınıflandırma ve donanım denetimi birim testleri.
  - `tests/test_env_checker.py`: Ortam ve bağımlılık doğrulama birim testleri.
  - `outputs/env_report.json`: Yerel makinede üretilen sistem ortam denetim raporu.

---

## Architecture
```
day01/
├── README.md
├── day01_firma_ve_calisma_ortami.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── env_spec.json
    ├── src/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── environment_profiler.py
    │   ├── env_checker.py
    │   └── repo_bootstrap.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_environment_profiler.py
    │   └── test_env_checker.py
    └── outputs/
        └── env_report.json
```

---

## Experiments
1. **İş İstasyonu Donanım Profili Taraması:**
   - İşletim Sistemi: Windows 11 (AMD64)
   - Mantıksal CPU Çekirdek Sayısı: `os.cpu_count()` ile dinamik tespit
   - RAM: `psutil.virtual_memory()` ile dinamik tespit
   - Hızlandırıcı: CUDA GPU kullanılabilirlik denetimi
2. **Veri Varlıkları Modalite Dağılımı:**
   - Sayısal sensör telemetrisi, görsel jakarlı halı desenleri ve metinsel teknik bakım yönergeleri `EnvironmentProfiler` ile taranarak kategorize edildi.

---

## Validation
- Pytest ile 7 adet birim test icra edildi:
  - `test_workstation_audit` (İş istasyonu CPU, RAM ve uyumluluk denetimi)
  - `test_data_asset_registration_and_distribution` (Sayısal, görsel ve metinsel modalite dağılımı ve JSON çıktısı)
  - `test_python_version_check` (Python sürüm denetimi)
  - `test_hardware_check` (CUDA ve GPU veri tipleri kontrolü)
  - `test_package_check_installed_and_missing` (Paket bağımlılık tespiti)
  - `test_full_check_and_report_serialization` (JSON rapor serileştirme doğrulaması)
  - `test_repository_bootstrap_validation` (Depo sözleşme doğrulaması)
- Tüm testler **%100 başarıyla (7 passed)** geçti.

---

## Results
- Geliştirme ortamının endüstriyel yapay zekâ gereksinimlerini tam olarak karşıladığı ve `is_compliant: true` olduğu doğrulandı.
- Üretilen sistem raporu [`mini_project/outputs/env_report.json`](mini_project/outputs/env_report.json) dosyasına kaydedildi.

---

## Limitations
- İlk gün oryantasyon ve yarım gün olduğundan derin öğrenme model eğitimi veya karmaşık boru hatları başlatılmamıştır.
- Canlı PLC/SCADA veya gerçek halı tezgahı telemetrisi yerine sentetik veri varlıkları ve yerel iş istasyonu parametreleri kullanılmıştır.

---

## Files
- `day01/README.md`
- `day01/day01_firma_ve_calisma_ortami.ipynb`
- `day01/mini_project/README.md`
- `day01/mini_project/configs/env_spec.json`
- `day01/mini_project/src/__init__.py`
- `day01/mini_project/src/models.py`
- `day01/mini_project/src/environment_profiler.py`
- `day01/mini_project/src/env_checker.py`
- `day01/mini_project/src/repo_bootstrap.py`
- `day01/mini_project/tests/__init__.py`
- `day01/mini_project/tests/test_environment_profiler.py`
- `day01/mini_project/tests/test_env_checker.py`
- `day01/mini_project/outputs/env_report.json`

---

## How to Run
```bash
# Donanım ve ortam denetimini çalıştırma
python day01/mini_project/src/env_checker.py

# Birim testleri koşma
pytest day01/mini_project/tests/ -v
```

---

## Next Day
- **Day 02:** Veri Türleri ve Temel Veri Modelleme — Yapılandırılmış, yarı yapılandırılmış ve yapılandırılmamış veri ilişkilerinin modellenmesi ve Pydantic v2 ile şema dönüşümleri.