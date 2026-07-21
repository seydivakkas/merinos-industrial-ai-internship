# Day 01 — Firma ve Çalışma Ortamının Tanınması

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)
> **Resmi Staj Defteri Konusu:** Firma ve Çalışma Ortamının Tanınması (Yaprak 1 & 2)
> **Müfredat Hizalama Durumu:** Bu klasörün mevcut uygulama içeriği yeni müfredatla ayrıca hizalanmalıdır.

## Goal
Bu ilk günde amaç, 40 günlük endüstriyel yapay zeka staj portföyü için tekrarlanabilir, izole, tip güvenli ve endüstriyel standartlara uygun temel bir geliştirme ortamı (development environment) kurmak; Python, bağımlılık yöneticisi, Git kancaları ve donanım hızlandırıcı (CUDA/GPU) denetim mekanizmasını hayata geçirmektir. İlk gün yarım gün olduğundan kapsam repo bootstrap ve ortam doğrulama ile sınırlandırılmıştır.

---

## Engineer Research Assignment
- Kurumsal bir işletmede yerel ortam ile üretim sunucuları arasındaki ortam sapmalarının (dependency drift) kök nedenlerini araştırmak.
- Sanal ortamlar (venv), Poetry deterministik paket kitleme (`poetry.lock`) ve Docker konteynerizasyonunun tekrarlanabilirlikteki rollerini karşılaştırmak.
- Statik kod analizi (Ruff) ve biçimlendiricilerin (Black) pre-commit seviyesinde zorunlu kılınmasının yazılım kalitesine etkisini incelemek.
- Donanım hızlandırma katmanında CUDA mimarisinin PyTorch ile nasıl iletişim kurduğunu ve çalışma zamanı tespiti pratiklerini öğrenmek.

---

## Concepts
- **Sanal Ortam İzolasyonu (Virtual Environment):** Küresel sistem paketlerini kirletmeden projeye özel izole çalışma alanı.
- **Deterministik Bağımlılık Yönetimi (Lockfile):** Paketlerin alt bağımlılıklarını ve SHA256 sağlama toplamlarını sabitleyerek ortamlar arası tam eşleşme sağlama.
- **Statik Kod Analizi (Linting & Formatting):** Kodun çalıştırılmadan önce syntax hataları, PEP 8 ihlalleri ve tip uyuşmazlıkları açısından taranması.
- **Git Kancaları (Pre-commit Hooks):** Hatalı veya biçimlendirilmemiş kodun depoya girmesini engelleyen yerel otomasyon kalkanı.
- **Donanım Algılama (Hardware Probing):** Çalışma zamanında GPU varlığını, modelini ve VRAM kapasitesini dinamik olarak tespit etme.

---

## Libraries
- `sys`, `platform`, `importlib.metadata`: Python standart kütüphanesi ortam sorgulama araçları.
- `pathlib`: İşletim sisteminden bağımsız nesne yönelimli dosya yolu yönetimi.
- `dataclasses`: Tip korumalı ve serileştirilebilir veri yapıları.
- `pydantic`: Çalışma zamanı veri doğrulama ve şema yönetimi.
- `pytest`: Otomatik birim test çatısı.
- `torch`: Donanım ve CUDA kullanılabilirlik denetleyicisi.

---

## Functions / Classes Studied
- `sys.version_info`, `platform.system()`, `platform.machine()`
- `importlib.metadata.version()`
- `torch.cuda.is_available()`, `torch.cuda.get_device_name()`, `torch.cuda.get_device_properties()`
- `dataclasses.asdict()`
- `pytest.fixture`

---

## Notebook
- **Dosya:** [`day01_environment_setup.ipynb`](day01_environment_setup.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, API İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Ortam izolasyonunu ve CUDA tespitini interaktif olarak açıklar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `environment-bootstrap`
- **Modüller:**
  - `src/env_checker.py`: Donanım ve paket uyumluluğunu denetleyen ve `EnvironmentReport` nesnesi üreten sınıf.
  - `src/repo_bootstrap.py`: Depo kök dizinindeki zorunlu klasör ve sözleşme dosyalarını doğrulayan motor.
  - `configs/env_spec.json`: Asgari sistem ve paket gereksinimleri bildirimi.
  - `tests/test_env_checker.py`: Pytest birim testleri (5 test).
  - `outputs/env_report.json`: Yerel makinede üretilen gerçek sistem raporu.

---

## Architecture
```
day01/
├── README.md
├── day01_environment_setup.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── env_spec.json
    ├── src/
    │   ├── __init__.py
    │   ├── env_checker.py
    │   └── repo_bootstrap.py
    ├── tests/
    │   ├── __init__.py
    │   └── test_env_checker.py
    └── outputs/
        └── env_report.json
```

---

## Experiments
1. **Yerel Ortam Taraması:**
   - İşletim Sistemi: Windows 11 (AMD64)
   - Python Yorumlayıcı: Python 3.14.3
   - Hızlandırıcı: NVIDIA GeForce RTX 4070 Laptop GPU (CUDA 12.6, 8.0 GB VRAM)
   - Paket Denetimi: `numpy (2.4.3)`, `pydantic (2.13.3)`, `pytest (9.0.3)`, `torch (2.11.0+cu126)`, `fastapi (0.139.0)`, `celery (5.6.3)`, `redis (6.4.0)` tespit edildi.

---

## Validation
- Pytest ile 5 adet birim test icra edildi:
  - `test_python_version_check` (Python >= 3.11 kontrolü)
  - `test_hardware_check` (CUDA ve GPU veri tipleri kontrolü)
  - `test_package_check_installed_and_missing` (Var olan ve eksik paket tespiti)
  - `test_full_check_and_report_serialization` (JSON rapor serileştirme doğrulaması)
  - `test_repository_bootstrap_validation` (Kök dizin sözleşme doğrulaması)
- Tüm testler **%100 başarıyla (5 passed in 13.67s)** geçti.

---

## Results
- Geliştirme ortamının endüstriyel yapay zeka gereksinimlerini tam olarak karşıladığı ve `is_compliant: true` olduğu doğrulandı.
- Üretilen gerçek sistem raporu [`mini_project/outputs/env_report.json`](mini_project/outputs/env_report.json) dosyasına kaydedildi.

---

## Limitations
- İlk gün oryantasyon ve yarım gün olduğundan derin öğrenme model eğitimi veya veri boru hatları henüz başlatılmamıştır.
- Docker daemon yerel sistemde çalışmakla birlikte konteyner derlemesi Faz 6'da (Day 37) detaylandırılacaktır.

---

## Files
- `day01/README.md`
- `day01/day01_environment_setup.ipynb`
- `day01/mini_project/README.md`
- `day01/mini_project/configs/env_spec.json`
- `day01/mini_project/src/__init__.py`
- `day01/mini_project/src/env_checker.py`
- `day01/mini_project/src/repo_bootstrap.py`
- `day01/mini_project/tests/__init__.py`
- `day01/mini_project/tests/test_env_checker.py`
- `day01/mini_project/outputs/env_report.json`

---

## How to Run
```bash
# Ortam denetimini çalıştırma ve rapor üretme
python day01/mini_project/src/env_checker.py

# Birim testleri koşma
python -m pytest day01/mini_project/tests/ -v
```

---

## Next Day
- **Day 02:** Problem Uzayının Tanımlanması — Endüstriyel görsel ve metadata veri modellerinin Pydantic v2 ile kurgulanması ve doğrulama kural kümelerinin oluşturulması.

---

## AI Coding Agent Prompt
```markdown
Build Day 01 of an Industrial AI internship portfolio.

The first day was a half-day, therefore do not exaggerate the implementation.

Create a professional repository bootstrap using:
- Poetry
- Docker
- pre-commit
- Ruff
- Black
- Pytest
- .env.example
- project package structure

Create:
day01/day01_environment_setup.ipynb
day01/README.md
day01/mini_project/

The notebook must explain reproducibility, environments and dependency isolation.

Run basic environment checks.

Do not fabricate company infrastructure.
```