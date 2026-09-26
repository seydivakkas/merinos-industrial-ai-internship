# Day 01 — Mini Project: Industrial Observation Catalog

## Genel Bakış
Bu mini proje, Merinos halı üretim tesisinde karşılaşılan heterojen veri türlerini (sayısal telemetri, görsel desen/kamera görüntüleri ve metinsel teknik dokümantasyon) sınıflandıran, özetleyen ve serileştiren yerel bir veri taksonomisi ve gözlem kataloğudur.

> **Veri Güvenliği ve Sentetik Kuralı:** Bu projede gerçek şirket verisi veya canlı telemetri kullanılmamaktadır. Tüm varlıklar ve açıklamalar sentetiktir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/models.py`: Pydantic v2 `DataModality` ve `DataAsset` veri sınıfları.
- `src/observation_catalog.py`: Varlık kayıt, filtreleme, özet istatistik ve JSON aktarım yöneticisi.
- `configs/catalog_config.json`: Problem alanları ve desteklenen veri modaliteleri tanımı.
- `tests/test_observation_catalog.py`: Tip doğrulama ve katalog operasyonları testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -q
```
