# Day 13: Klasik Segmentasyon Kıyaslama Özeti

| Yöntem | Ortalama Süre (ms) | Throughput (FPS) | IoU | Dice | BF-Score | Kapsama (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OTSU** | 0.845 ms | 1183.9 FPS | 0.9028 | 0.9489 | 0.7540 | %28.63 |
| **WATERSHED** | 11.78 ms | 84.9 FPS | 0.9386 | 0.9683 | 0.7595 | %28.13 |
| **GRABCUT** | 484.545 ms | 2.1 FPS | 0.9364 | 0.9672 | 0.7724 | %29.63 |

- **Önerilen Canlı Hat Yöntemi:** `WATERSHED`
- **Önerilen Laboratuvar Yöntemi:** `GRABCUT`
