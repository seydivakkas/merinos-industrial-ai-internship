# Merinos Halı Sanayi A.Ş. — Day 26: Vektör Veritabanı Optimizasyonu & İndeksleme

Bu modül, **Merinos Gaziantep Tesisleri** teknik bakım, dokuma arıza tespit ve kalite kontrol vektör arama operasyonlarında yüksek hızlı (sub-millisecond latency, >10.000 QPS) ve düşük bellek tüketimli vektör sorgulaması gerçekleştirmek üzere geliştirilmiş **Vektör İndeksleme ve Kuantizasyon Motoru**'dur.

Sistem, saf kaba kuvvet (Exact Flat) aramasından, K-Means Voronoi hücrelerine dayalı **Inverted File Index (IVF)**, çok katmanlı atlama grafiği tabanlı **Hierarchical Navigable Small World (HNSW)** ve **Skaler/Ürün Kuantizasyonu (SQ8 / PQ)** ile **Qdrant Bellek İçi Vektör Veritabanı** entegrasyonunu ve yük (payload) ön-filtreleme (pre-filtering) mekanizmalarını bünyesinde barındırır.

---

## 1. İndeksleme ve Kuantizasyon Mimarileri

### A. Kaba Kuvvet (Exact Flat Index)
Tüm korpus vektörleri $\mathbf{v}_i \in \mathbb{R}^d$ ($i=1,\dots,N$) ile sorgu vektörü $\mathbf{q}$ arasında tam kosinüs mesafesi hesaplar:
$$d_{\cos}(\mathbf{q}, \mathbf{v}_i) = 1 - \frac{\mathbf{q} \cdot \mathbf{v}_i}{\|\mathbf{q}\|_2 \|\mathbf{v}_i\|_2}$$
- **Zaman Karmaşıklığı:** $\mathcal{O}(N \cdot d)$
- **Doğruluk (Recall@K):** $\%100.0$ (Altın standart zemin gerçekliği)
- **Kısıt:** Korpus büyüdükçe latans doğrusal olarak artar, büyük endüstriyel veri setlerinde ölçeklenemez.

### B. Ters Çevrilmiş Dosya İndeksi (Inverted File Index - IVF)
Vektör uzayı $k$-Means kümeleme ile $nlist$ adet Voronoi hücresine bölünür. Her hücrenin bir merkez vektörü $\mathbf{c}_j$ bulunur:
$$\mathcal{C}_j = \{ \mathbf{v}_i \mid \arg\min_k \|\mathbf{v}_i - \mathbf{c}_k\|_2 = j \}$$
Sorgu anında sorguya en yakın $nprobe$ adet merkez seçilir ve arama sadece bu hücrelerdeki vektörlerle sınırlandırılır:
- **Hızlanma:** $\mathcal{O}\left(nlist \cdot d + \frac{nprobe}{nlist} \cdot N \cdot d\right)$
- **Takas (Trade-off):** Yüksek QPS (>15.000 QPS), hücre sınırındaki komşuların kaçırılması nedeniyle $\%85$ Recall@K seviyesinde denge.

### C. Hiyerarşik Gezinilebilir Küçük Dünya Grafiği (HNSW)
Vektörler çok katmanlı ($\ell = 0, \dots, L$) bir atlama grafiği (skip-graph) üzerinde organize edilir. Üst katmanlarda uzun mesafeli atlamalar yapılırken, taban katmanda ($\ell=0$) yerel en yakın komşular taranır:
- **Parametreler:** $M$ (düğüm başına maksimum kenar sayısı), $efConstruction$ (inşa arama derinliği), $efSearch$ (sorgu arama derinliği).
- **Zaman Karmaşıklığı:** $\mathcal{O}(\log N)$
- **Başarım:** $\%100.0$ Recall@K, son derece yüksek doğruluk ve graf üzerinde yerel arama gücü.

### D. Skaler Kuantizasyon (Scalar Quantization - SQ8) ve Ürün Kuantizasyonu (PQ)
32-bit kayan noktalı sayıları ($\text{float32}$) 8-bit tam sayılara ($\text{int8}$) dönüştürür:
$$\mathbf{z} = \text{round}\left( \frac{\mathbf{x} - \mu}{\sigma} \right), \quad \hat{\mathbf{x}} = \mathbf{z} \cdot \sigma + \mu$$
- **Bellek Tasarrufu:** %60'ın üzerinde RAM sıkıştırması (115.5 KB $\to$ 41.7 KB).
- **Kayıp:** $< 0.005$ rekonstrüksiyon hatası (MSE), pratik olarak sıfır Recall kaybı.
- **Product Quantization (PQ):** Vektörü $M$ alt uzaya böler, her alt uzayı $k$-Means ile $k^*$ kod kelimesine kuantize eder ve Asymmetric Distance Computation (ADC) ile arar.

### E. Ön-Filtreleme vs Son-Filtreleme (Payload Pre-filtering vs Post-filtering)
Endüstriyel filtreleme sorgularında (`department == 'dokuma_salonu_1'`):
- **Son-Filtreleme (Post-filtering):** Önce en yakın $K$ vektör bulunur, ardından filtre uygulanır. Filtre seçiciliği düşükse ($\le \%10$), dönen adayların hiçbiri kriteri sağlamayabilir veya eksik $K$ sonuç döner!
- **Ön-Filtreleme (Pre-filtering):** Mesafe hesaplanmadan veya graf gezintisi sırasında sadece filtreyi sağlayan düğümler değerlendirilir. Qdrant payload indexleri ile $\%100$ kesin sonuç garantilenir.

---

## 2. Dizin Yapısı

```
day26/mini_project/
├── configs/
│   └── vector_index_config.json          # IVF, HNSW, SQ ve Qdrant hiperparametreleri
├── fixtures/
│   ├── merinos_vector_corpus.json        # 66 adet 384-boyutlu endüstriyel teknik vektör ve zengin payload
│   └── filtered_benchmark_queries.json   # 15 adet filtrelenmiş teknik kıyaslama sorgusu
├── outputs/
│   ├── vector_index_benchmark_report.json # Kapsamlı QPS, latans, bellek ve Recall kıyaslama raporu
│   └── vector_index_diagnostic_panel.png  # 2x2 Master Tanı Paneli (300 DPI)
├── src/
│   ├── __init__.py                       # Paket başlatıcı
│   ├── models.py                         # Pydantic v2 veri modelleri
│   ├── quantization.py                   # ScalarQuantizer (SQ8) & ProductQuantizer (PQ)
│   ├── ivf_index.py                      # InvertedFileIndex (Voronoi K-Means)
│   ├── hnsw_index.py                     # HNSWVectorIndex (Multi-layer skip graph)
│   ├── qdrant_manager.py                 # In-Memory QdrantVectorStore entegrasyonu
│   ├── benchmarker.py                    # Vektör indeks kıyaslayıcı motor
│   ├── visualizer.py                     # 2x2 Matplotlib Master Tanı Paneli
│   └── cli.py                            # Argparse komut satırı arayüzü
├── tests/
│   └── test_vector_indexing.py           # 10 adet birim ve entegrasyon testi
└── README.md                             # Bu dokümantasyon
```

---

## 3. Kurulum ve CLI Kullanımı

### Arama Komutu (Search)
```bash
# HNSW indeksi ile dokuma salonu filtresi uygulayarak arama yap
python -m day26.mini_project.src.cli search --index-type hnsw --query-index 0 --filter-dept dokuma_salonu_1 --top-k 5

# Qdrant bellek içi vektör veritabanı ile ön-filtreli arama yap
python -m day26.mini_project.src.cli search --index-type qdrant --query-index 1 --top-k 3
```

### Büyük Kıyaslama ve Tanı Paneli (Benchmark)
```bash
python -m day26.mini_project.src.cli benchmark --plot
```

---

## 4. Kıyaslama Sonuçları ve Başarım Analizi

Merinos 384-boyutlu vektör korpusu ve 15 teknik arıza sorgusu üzerinde yürütülen test sonuçları:

| İndeks Türü | İnşa Süresi (ms) | Latans (ms) | QPS (Sorgu/sn) | Bellek (KB) | Recall@5 | Filtreli Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Exact Flat** | 1.0 | 0.06 | **16,264** | 99.0 | **%100.0** | **%100.0** |
| **IVF (nlist=8, nprobe=3)** | 1740.5 | 0.06 | **15,501** | 111.5 | %85.3 | %66.7 |
| **HNSW (M=16, ef=64)** | 108.1 | 0.21 | 4,747 | 115.5 | **%100.0** | %74.7 |
| **Quantized HNSW (SQ8)** | 56.9 | 0.24 | 4,229 | **41.7** | **%100.0** | %74.7 |

- **Hız Şampiyonu:** IVF & Exact Flat (>15.000 QPS)
- **Doğruluk Şampiyonu:** HNSW (%100.0 zemin gerçekliği eşleşmesi)
- **Bellek Verimliliği Şampiyonu:** Quantized HNSW (115.5 KB $\to$ 41.7 KB ile **%64 bellek tasarrufu**)

---

## 5. Lisans

ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
