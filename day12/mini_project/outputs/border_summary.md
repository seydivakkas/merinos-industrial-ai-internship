# Day 12: Kenar ve Çizgi Tespiti Benchmark Özeti

## Operatör Hızları (1024x1024)

| Operatör | Ortalama Süre (ms) | Throughput (FPS) |
| :--- | :--- | :--- |
| Sobel (3x3) | 42.964 ms | 23.3 FPS |
| Scharr (3x3) | 43.154 ms | 23.2 FPS |
| Laplacian (3x3) | 39.274 ms | 25.5 FPS |
| Canny | 2.448 ms | 408.6 FPS |

## Uçtan Uca Hat Ölçekleme

| Çözünürlük | Megapiksel | Toplam Süre (ms) | FPS |
| :--- | :--- | :--- | :--- |
| 512x512 | 0.26 MP | 3.75 ms | 266.3 FPS |
| 1024x1024 | 1.05 MP | 8.88 ms | 112.6 FPS |
| 2048x2048 | 4.19 MP | 20.79 ms | 48.1 FPS |
