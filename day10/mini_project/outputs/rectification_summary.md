# Day 10: Perspektif Düzeltme ve Homografi Benchmark Raporu

## 1. Farklı Perspektif Açılarında Düzeltme Performansı

| Açı Durumu | Köşe Tespiti (ms) | Tam Düzeltme (ms) | FPS | Ham Skew (°) | Düzeltilmiş Skew (°) | Cond(H) | Kalite |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Oblique 25 deg | 5.98 ms | 2.66 ms | 375.9 FPS | 8.01° | 0.0° | 42310.37 | PASS |
| Conveyor 35 deg | 5.39 ms | 1.88 ms | 531.9 FPS | 13.24° | 0.0° | 91469.47 | PASS |
| Severe 45 deg | 5.35 ms | 2.26 ms | 442.5 FPS | 23.75° | 0.0° | 178495.85 | WARNING |

## 2. Çözünürlük Ölçekleme Performansı (Homografi Warping)

| Çözünürlük | Megapiksel | Ortalama Süre (ms) | Throughput (FPS) |
| :--- | :--- | :--- | :--- |
| 512x512 | 0.26 MP | 1.58 ms | 632.9 FPS |
| 1024x1024 | 1.05 MP | 5.13 ms | 194.9 FPS |
| 2048x2048 | 4.19 MP | 9.18 ms | 108.9 FPS |
