# Day 06 Mini Project: Vektör Benzerlik Laboratuvarı (Cosine, L1/L2, Mahalanobis & Ölçekleme)

Bu mini proje, Merinos fabrikasyon ortamında dokuma tezgâhı parametreleri, ürün katalogları ve derin öğrenme öznitelik embedding'leri üzerinde en uygun mesafe ve benzerlik metriklerinin seçilmesini, özellik ölçekleme (StandardScaler, MinMaxScaler, L2Normalizer) etkilerini, k-NN benzer ürün getirme motorunu (`VectorSimilaritySearchEngine`) ve boyutsallık lanetinin (Curse of Dimensionality / Distance Concentration) matematiksel analizini gerçekleştiren kurumsal bir laboratuvar paketidir.

---

## 📁 Proje Yapısı

```bash
day06/mini_project/
├── configs/
│   └── similarity_config.json          # Metrik tanımları, boyutlar, Top-K arama parametreleri
├── fixtures/
│   └── carpet_feature_embeddings.npz   # 100 halılık sentetik 32-d / 128-d ve fiziksel öznitelik havuzu
├── src/
│   ├── __init__.py
│   ├── metrics.py                      # Vektörize L1, L2, Kosinüs, Mahalanobis ve Minkowski metrikleri
│   ├── scalers.py                      # StandardScaler, MinMaxScaler ve L2Normalizer
│   ├── generator.py                    # CarpetEmbeddingGenerator (Sentetik embedding ve fiziksel veri)
│   ├── search.py                       # VectorSimilaritySearchEngine (Top-K getirme ve kıyaslama)
│   └── curse_analyzer.py               # CurseOfDimensionalityAnalyzer (Boyutsallık laneti analizörü)
├── tests/
│   ├── __init__.py
│   └── test_similarity.py              # 10 kapsamlı birim ve matematiksel doğrulama testi
├── outputs/
│   ├── similarity_benchmark.json       # Metrik bazlı hesaplama süresi ve throughput
│   ├── curse_of_dimensionality_report.json # D=2'den D=1024'e bağıl kontrast kayıp raporu
│   ├── topk_search_sample.json         # Örnek sorgu için Top-K benzer ürün listeleri
│   └── similarity_metrics_summary.md   # Kurumsal Markdown özet tablosu
└── README.md                           # Bu dokümantasyon
```

---

## ⚙️ Uygulanan Metrikler ve Matematiksel Tanımlar

1. **Öklid (L2) Mesafesi:**
   $$d_2(\mathbf{u}, \mathbf{v}) = \|\mathbf{u} - \mathbf{v}\|_2 = \sqrt{\sum_{i=1}^D (u_i - v_i)^2}$$
2. **Manhattan (L1) Mesafesi:**
   $$d_1(\mathbf{u}, \mathbf{v}) = \|\mathbf{u} - \mathbf{v}\|_1 = \sum_{i=1}^D |u_i - v_i|$$
3. **Kosinüs (Cosine) Benzerliği ve Mesafesi:**
   $$S_C(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}, \quad d_C(\mathbf{u}, \mathbf{v}) = 1 - S_C(\mathbf{u}, \mathbf{v})$$
4. **Birim Vektörde Kosinüs-Öklid Bağıntısı:**
   $$\|\mathbf{u}\| = \|\mathbf{v}\| = 1 \implies d_2^2(\mathbf{u}, \mathbf{v}) = 2(1 - S_C) = 2 \cdot d_C$$
5. **Mahalanobis Mesafesi (Kovaryans Düzeltmeli):**
   $$d_M(\mathbf{u}, \mathbf{v}) = \sqrt{(\mathbf{u} - \mathbf{v})^T \Sigma^{-1} (\mathbf{u} - \mathbf{v})}$$
6. **Minkowski ($L_p$) Genellemesi:**
   $$d_p(\mathbf{u}, \mathbf{v}) = \left( \sum_{i=1}^D |u_i - v_i|^p \right)^{1/p}$$

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day06/mini_project/tests/ -v
```

## 🚀 Laboratuvar Boru Hattını Çalıştırma

```bash
python -m day06.mini_project.src.search
```
Çıktılar `day06/mini_project/outputs/` dizininde otomatik oluşturulur.
