# Day 04 — Mini Project: Python Environment and Data Contracts

## Genel Bakış
Bu mini proje, yerel geliştirme iş istasyonunun donanım profilini (CPU, RAM, hızlandırıcılar) ve paket bağımlılıklarını yazılımsal olarak denetleyen modüller ile tezgâh sensör telemetrileri ve halı şartnamelerini sistem sınırında doğrulayan Pydantic v2 veri sözleşmelerini içerir.

> **Veri Güvenliği ve Sentetik Kuralı:** Canlı PLC/SCADA veya kurum içi veri tabanı bağlantısı yoktur. Tüm telemetri ve ürün kayıtları sentetiktir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/data_contracts.py`: `CarpetSpecificationContract` ve `LoomTelemetryContract` Pydantic v2 modelleri.
- `src/env_checker.py`: Python sürümü, GPU/CUDA durumu ve paket bağımlılıkları denetleyicisi.
- `src/environment_profiler.py`: İş istasyonu kaynak denetim profilleyicisi.
- `src/repo_bootstrap.py`: Dizin ve dosya yapısı sözleşmesini doğrulayan motor.
- `src/models.py`: Ortam denetim ve sistem gereksinimleri modelleri.
- `configs/env_spec.json`: Sistem ve bağımlılık gereksinimleri bildirimi.
- `configs/environment_config.json`: Ortam çalışma konfigürasyonu.
- `tests/test_data_contracts.py`: Veri sözleşmeleri ve sınır doğrulaması testleri.
- `tests/test_env_checker.py`: Ortam ve paket denetim testleri.
- `tests/test_environment_profiler.py`: Donanım ve varlık profilleme testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -v
```
