# Merinos Industrial AI — Day 06: Vektör Benzerlik ve Mesafe Metrikleri Raporu

> **Aşama:** Faz 1: Çevre & Veri Temelleri (Kapanış)  
> **Tarih:** 2026-09-04 08:17:49  

## 1. Çiftli (Pairwise) Mesafe Hesaplama Performansı (100x100 Matris, 128 Boyut)

| Metrik | Gecikme (ms) | Throughput (Çift/sn) | Matematiksel Formül | Endüstriyel Özellik |
| **Cosine** | **`0.146 ms`** | `68,308,343` | S_C = (u . v) / (||u|| ||v||) | Normdan bağımsız, açısal yönelim |
| **Euclidean (L2)** | **`0.071 ms`** | `140,944,326` | d_2 = ||u - v||_2 | Geometrik mesafe, ölçeğe duyarlı |
| **Manhattan (L1)** | **`2.995 ms`** | `3,339,372` | d_1 = sum |u_i - v_i| | Aykırı değerlere (outliers) dayanıklı |
| **Mahalanobis** | **`10.144 ms`** | `985,762` | d_M = sqrt((u-v)^T Sigma^-1 (u-v)) | Kovaryans ve korelasyon düzeltmeli |

## 2. Boyutsallık Laneti (Curse of Dimensionality / Distance Concentration)

- **İncelenen Boyut Aralığı:** D = 2 ile D = 1024
- **Kontrast Azalma Çarpanı:** **`5214.3x`** kayıp
- **D=2 Kontrastı:** `934.9244` -> **D=1024 Kontrastı:** `0.1793`

## 3. Top-K Arama Karşılaştırması (`MRP-1001` için İlk 3 Sonuç)

- **Sorgu:** `MRP-1001` (Koleksiyon: `Prestij`)
- **Cosine:** `MRP-1019` (Prestij: 0.0343), `MRP-1016` (Prestij: 0.0345), `MRP-1011` (Prestij: 0.0355)
- **Euclidean:** `MRP-1016` (Prestij: 5.9388), `MRP-1019` (Prestij: 6.0393), `MRP-1011` (Prestij: 6.0561)
- **Manhattan:** `MRP-1016` (Prestij: 51.0338), `MRP-1011` (Prestij: 52.6267), `MRP-1019` (Prestij: 53.3015)
- **Mahalanobis:** `MRP-1092` (ModernLine: 13.6035), `MRP-1091` (ModernLine: 13.6437), `MRP-1084` (ModernLine: 13.6689)

## 4. Faz 1 Mühendislik Çıkarımları
1. **Birim Vektörde Kosinüs-Öklid Eşitliği:** $L_2$ normalize vektörlerde $d_E^2 = 2(1 - S_C)$ olduğundan, yüksek hızlı iç çarpım (dot product) doğrudan Öklid sıralamasını verir.
2. **Ölçekleme Zorunluluğu:** Fiziksel üretim metrikleri (hav: 10 mm, ilmek: 500,000) bir arada arandığında MinMaxScaler / StandardScaler uygulanmazsa mesafe tek bir sütun tarafından domine edilir.
3. **Faz 2'ye Geçiş:** Faz 1 (Veri & Çevre) başarıyla mühürlenmiş; Faz 2'de (OpenCV ve Bilgisayarlı Görü) pikseller üzerinden renk uzayları, homografi ve doku analizine geçilmeye hazır olunmuştur.