# Day 01 Mini Project — Environment Bootstrap

Bu mini proje, endüstriyel yapay zeka projelerinde tekrarlanabilirlik (reproducibility) ve bağımlılık izolasyonunu sağlamak amacıyla geliştirilmiş ortam denetleme ve repository bootstrap motorudur.

---

## Mimari ve Bileşenler

```
mini_project/
├── configs/
│   └── env_spec.json       # Asgari sistem ve paket gereksinimleri spesifikasyonu
├── src/
│   ├── env_checker.py      # Python, işletim sistemi, CUDA/GPU ve paket denetleyicisi
│   └── repo_bootstrap.py   # Depo hiyerarşisi doğrulama motoru
├── tests/
│   └── test_env_checker.py # Otomatik pytest birim testleri
└── outputs/
    └── env_report.json     # Gerçek donanım ve ortam analiz çıktısı
```

---

## Nasıl Çalıştırılır?

### 1. Ortam Raporunu Üretme
```bash
python src/env_checker.py
```
Bu komut, sistem donanımını (CUDA, VRAM, CPU mimarisi) ve Python paketlerini tarayarak `outputs/env_report.json` dosyasına kaydeder.

### 2. Birim Testleri Koşma
```bash
pytest tests/ -v
```

---

## Test Sonuçları (Gerçekleştirilmiş)
```
day01/mini_project/tests/test_env_checker.py::test_python_version_check PASSED
day01/mini_project/tests/test_env_checker.py::test_hardware_check PASSED
day01/mini_project/tests/test_env_checker.py::test_package_check_installed_and_missing PASSED
day01/mini_project/tests/test_env_checker.py::test_full_check_and_report_serialization PASSED
day01/mini_project/tests/test_env_checker.py::test_repository_bootstrap_validation PASSED
5 passed in 13.67s
```
