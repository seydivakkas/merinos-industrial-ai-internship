# Day 08 — Mini Project: Exploratory Data Analysis (EDA) Toolkit

## Genel Bakış
Bu mini proje, endüstriyel dokuma tezgâhı telemetrileri ve halı üretim parametreleri üzerinde otomatik istatistiksel dağılım analizi, IQR / Z-score aykırı değer (outlier) tespiti, Pearson korelasyon matrisi, histogram ve kutu grafiği metrikleri üreten modüler bir EDA motorudur (`EDAToolkit`).

> **Veri Güvenliği ve Sentetik Kuralı:** Canlı fabrika sensörü veya kurumsal veri tabanı bağlantısı yoktur. Tüm telemetri verileri sentetiktir ([`docs/DATA_REALITY_POLICY.md`](../../docs/DATA_REALITY_POLICY.md)).

## Modüller
- `src/eda_toolkit.py`: `EDAToolkit`, `EDAReport`, `ColumnSummary` ve `BoxplotSummary` sınıfları.
- `src/generator.py`: Sentetik veri üreteci.
- `tests/test_eda_toolkit.py`: Aykırı değer, korelasyon, histogram ve kutu grafiği testleri.

## Çalıştırma ve Test
```bash
pytest tests/ -v
```
