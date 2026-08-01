# Day 11: Morfolojik Operasyonlar ve Kusur Tespiti Benchmark Raporu

## 1. Operatör Bazlı Gecikme ve Throughput (1024x1024 px)

| Operatör | Ortalama Süre (ms) | Throughput (FPS) |
| :--- | :--- | :--- |
| Erosion (11x11) | 0.45 ms | 2221.7 FPS |
| Dilation (11x11) | 0.44 ms | 2266.8 FPS |
| Opening (11x11) | 0.66 ms | 1519.7 FPS |
| Closing (11x11) | 0.66 ms | 1523.5 FPS |
| Morph Gradient (11x11) | 0.95 ms | 1050.0 FPS |
| White Top-Hat (11x11) | 0.70 ms | 1426.7 FPS |
| Black Top-Hat (11x11) | 0.71 ms | 1412.2 FPS |
| Directional Weft BTH (1x17) | 0.72 ms | 1393.5 FPS |

## 2. Çözünürlük Ölçekleme Performansı (Tam Pipeline)

| Çözünürlük | Megapiksel | Ortalama Süre (ms) | Throughput (FPS) |
| :--- | :--- | :--- | :--- |
| 512x512 | 0.26 MP | 4.37 ms | 228.9 FPS |
| 1024x1024 | 1.05 MP | 17.08 ms | 58.6 FPS |
| 2048x2048 | 4.19 MP | 66.50 ms | 15.0 FPS |
