# Merinos Dense Retrieval & Cross-Encoder Re-ranking Engine

> **Aşama:** Faz 4: Retrieval & Hibrit Arama (Day 22–28)  
> **Konu:** Day 23: Yoğun Getirme Motoru (Dense Retrieval: Bi-Encoder & Cross-Encoder Mimarisi)  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.  
> **Lisans Badge:** ![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. Gaziantep 4. OSB tesislerindeki devasa makine parkurunda (Van de Wiele jakarlı dokuma tezgâhları, BCF ekstrüzyon, Schlafhorst büküm, Superba fiksaj), operatörlerin ve bakım teknisyenlerinin teknik arıza bildirimleri çoğu zaman kılavuzlardaki birebir kelimelerle örtüşmez. 

Örneğin bir teknisyen *"çözgü ipleri çok gevşek levent durmuyor"* dediğinde, leksikal (kelime bazlı) arama başarısız olabilir; ancak anlamsal (semantik) arama bu ifadenin *"Van de Wiele Çözgü Gerilim Ayar Prosedürü ve Levent Fren Balatası"* dokümanına karşılık geldiğini tespit etmelidir.

**Day 23**, iki aşamalı modern bilgi getirme mimarisini (Two-Stage Retrieve & Re-rank) devreye almıştır:
1. **1. Aşama (First Stage Dense Retrieval):** `all-MiniLM-L6-v2` Bi-Encoder modeli ile 384 boyutlu anlamsal metin vektörleri üretilir ve **Qdrant Vektör Veritabanı** üzerinde HNSW indeksleme ile kosinüs benzerliği üzerinden milisaniyeler içinde Top-10 aday getirilir.
2. **2. Aşama (Second Stage Deep Re-ranking):** `cross-encoder/ms-marco-TinyBERT-L-2-v2` modeli ile (Sorgu, Doküman) çiftleri tam çapraz dikkat (cross-attention) katmanından geçirilerek derin anlamsal uygunluk puanı hesaplanır ve en doğru ilk 3 doküman sıralanır.

---

## 📐 Matematiksel ve Algoritmik Temeller

### 1. Bi-Encoder ve Kosinüs Benzerliği
Sorgu ($q$) ve doküman ($d$) birbirinden bağımsız olarak yoğun vektör uzayına eşlenir:
$$\mathbf{u} = \text{BiEncoder}(q) \in \mathbb{R}^{384}, \quad \mathbf{v} = \text{BiEncoder}(d) \in \mathbb{R}^{384}$$

$L_2$ normalizasyonu uygulanmış vektörlerde kosinüs benzerliği nokta çarpımına (dot product) eşittir:
$$\text{Sim}_{\text{Dense}}(q, d) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \mathbf{u}_{\text{norm}} \cdot \mathbf{v}_{\text{norm}}^T$$

### 2. Qdrant Vektör Veritabanı ve HNSW İndeksi
Vektörler Qdrant koleksiyonuna PointStruct olarak yüklenir. HNSW (Hierarchical Navigable Small World) graf yapısı üzerinden logaritmik karmaşıklıkta ($\mathcal{O}(\log N)$) en yakın komşu araması yapılır. Meta-veri filtreleme (örn: `category = 'DOKUMA_TEZGAHI_BAKIM'`) vektör araması öncesinde yük (payload) seviyesinde uygulanır.

### 3. Cross-Encoder Çapraz Dikkat Re-Ranker
Bi-Encoder sorgu ve dokümanı bağımsız işlerken, Cross-Encoder her iki metni tek bir sekans olarak modelin girişine verir:
$$\mathbf{x} = \text{[CLS]} \circ q \circ \text{[SEP]} \circ d \circ \text{[SEP]}$$
Tüm kelimeler birbirine tam dikkat (full cross-attention) uygular. [CLS] tokeni üzerinden logit $z$ üretilir ve Sigmoid ile kalibre edilir:
$$\text{Score}_{\text{CE}}(q, d) = \sigma(z) = \frac{1}{1 + e^{-z}} \in [0, 1]$$

---

## 📂 Paket Mimarisi

```
day23/mini_project/
├── configs/
│   └── dense_retrieval_config.json             # Bi-Encoder, Cross-Encoder ve Qdrant hiperparametreleri
├── fixtures/
│   └── merinos_technical_corpus.json           # 52 adet kurumsal Merinos arıza ve bakım dokümanı
├── outputs/
│   ├── dense_retrieval_benchmark.json          # BM25 vs Bi-Encoder vs Re-ranked kıyaslama raporu
│   └── dense_retrieval_panel.png               # 2x2 master teşhis ve kalibrasyon paneli
├── src/
│   ├── __init__.py                             # Paket başlatıcı
│   ├── models.py                               # Pydantic v2 veri şemaları
│   ├── bi_encoder.py                           # Cümle gömmeleri ve kosinüs benzerlik motoru
│   ├── vector_store.py                         # Qdrant vektör veritabanı koleksiyon yönetimi
│   ├── cross_encoder_reranker.py               # Çapraz dikkat tabanlı re-ranker motoru
│   ├── pipeline.py                             # İki aşamalı (Retrieve + Rerank) uçtan uca arama hattı
│   ├── evaluator.py                            # 15 teknik sorguda P@K, Recall@K, MRR, NDCG@K motoru
│   ├── visualizer.py                           # Matplotlib 2x2 master panel çizici
│   └── cli.py                                  # Argparse tabanlı terminal arayüzü
├── tests/
│   └── test_dense_retrieval.py                 # 10 adet birim ve entegrasyon testi
└── README.md                                   # Bu teknik doküman
```

---

## 🚀 Komut Satırı Arayüzü (CLI) Kullanımı

```bash
# 1. Külliyatı vektörleştir ve Qdrant koleksiyonuna yükle
python -m day23.mini_project.src.cli index-vectors

# 2. Bi-Encoder ve Qdrant ile semantik arama yap
python -m day23.mini_project.src.cli search-dense --query "çözgü gerilim levent fren hidrolik basıncı arızası" --top-k 3

# 3. İki aşamalı getirme + Cross-Encoder re-ranking yap
python -m day23.mini_project.src.cli rerank --query "çözgü gerilim levent fren hidrolik basıncı arızası" --first-stage-top-k 10 --final-top-k 3

# 4. 15 teknik sorguda Benchmark çalıştır
python -m day23.mini_project.src.cli benchmark --runs 3

# 5. 2x2 Master Teşhis Panelini çizdir
python -m day23.mini_project.src.cli plot
```

---

## 📊 Karşılaştırmalı Performans Sonuçları (Benchmark)

15 kurumsal teknik sorgu üzerinde elde edilen sonuçlar:

| Model / Mimari | Precision@1 | Precision@3 | Recall@5 | MRR | NDCG@5 | Gecikme (ms) | İşlem Hızı (QPS) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Okapi BM25 (Day 22)** | %100.0 | %33.3 | %100.0 | 1.0000 | 1.0000 | 0.13 ms | 7,592.2 |
| **Bi-Encoder (MiniLM / Qdrant)** | %60.0 | %22.2 | %73.3 | 0.6500 | 0.6708 | 41.61 ms | 24.0 |
| **Two-Stage Re-ranked (Bi-Enc + Cross-Enc)** | **%80.0** | **%26.7** | **%80.0** | **0.8000** | **0.8000** | 48.82 ms | 20.5 |

> **Kritik Çıkarım:** Bi-Encoder tek başına %60.0 P@1 ve 0.6500 MRR üretirken, Cross-Encoder re-ranking katmanı başarıyı **%80.0 P@1 ve 0.8000 MRR** seviyesine çıkarmıştır (+%20 net artış). Çıkarım süresi sadece ~7 ms artarak 48.82 ms seviyesinde kalmıştır.

---

## 🧪 Birim ve Entegrasyon Testleri

```bash
python -m pytest day23/mini_project/tests/test_dense_retrieval.py -v
```

10 adet kapsamlı test:
1. `test_bi_encoder_embedding_generation_and_norm`: 384 boyut ve $L_2$ normalizasyon testi.
2. `test_bi_encoder_search_exact_and_semantic`: Semantik getirme ve Top-K sıralama doğrulaması.
3. `test_qdrant_vector_store_initialization_and_upsert`: Qdrant koleksiyon yönetimi ve point upsert.
4. `test_qdrant_search_and_category_filtering`: Kategori bazlı payload filtreleme denetimi.
5. `test_cross_encoder_predict_pairs_and_sigmoid`: Metin çifti alaka puanlaması ve sigmoid aralığı $[0, 1]$.
6. `test_cross_encoder_rerank_candidates`: Cross-Encoder ile aday dokümanların yeniden sıralanması.
7. `test_two_stage_pipeline_end_to_end`: Uçtan uca Retrieve + Re-rank hattının çalışması.
8. `test_evaluator_metrics_calculation`: P@K, Recall@K, MRR ve NDCG@K matematiksel hassasiyeti.
9. `test_cli_commands_execution`: CLI komutlarının hatasız çalışması.
10. `test_dense_retrieval_benchmark_and_panel_generation`: Benchmark ve 2x2 panel PNG üretim doğrulaması.

---

## 📜 Lisans

```
ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır.

YASAKLAR:
  1. Kopyalanamaz, çoğaltılamaz, dağıtılamaz veya yeniden yayınlanamaz.
  2. Ticari veya ticari olmayan hiçbir projede kullanılamaz, değiştirilemez.
  3. Alt lisanslanamaz, satılamaz veya devredilemez.
  4. Tersine mühendislik yapılamaz.

İZİN VERİLEN KULLANIM:
  - GitHub üzerinde görüntüleme ve okuma.
  - Kişisel öğrenim amacıyla kodu inceleme (kopyalamadan).

YAZARIN AÇIK YAZILI İZNİ OLMAKSIZIN HİÇBİR KULLANIM HAKKI TANINMAZ.
İzin talepleri için: GitHub @seydivakkas
```
