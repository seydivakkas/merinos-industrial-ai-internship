# Merinos Industrial AI Internship — Day 24
## Hibrit Arama ve Karşılıklı Sıra Füzyonu (Hybrid Retrieval: BM25 + Dense Qdrant Fusion via RRF)

Bu modül, **Merinos Halı Sanayi ve Ticaret A.Ş.** Gaziantep 4. OSB üretim tesislerindeki dokuma tezgahı bakım, jakar yönetimi, iplik laboratuvarı ve kalite güvence teknik külliyatı üzerinde leksikal (Okapi BM25) ve anlamsal (Qdrant Dense Bi-Encoder) arama motorlarının çıktılarını birleştiren kurumsal hibrit getirme motorunu sunar.

---

### 🏛️ Mimari Tasarım & 3 Aşamalı Hat

```
                                  [ Kullanıcı Teknik Sorgusu ]
                                                |
                 +------------------------------+------------------------------+
                 |                                                             |
                 v                                                             v
       [ 1. Aşama (Leksikal) ]                                       [ 1. Aşama (Semantik) ]
       Okapi BM25 Sparse Motor                                       Qdrant Dense Bi-Encoder
       k1=1.5, b=0.75                                                all-MiniLM-L6-v2 (384-d)
       (Teknik terim & parça kodları)                                (Eş anlam & arıza semantiği)
                 |                                                             |
                 +------------------------------+------------------------------+
                                                |
                                                v
                                     [ 2. Aşama: Sıra Füzyonu ]
                 +-------------------------------------------------------------+
                 |  A) Reciprocal Rank Fusion (RRF, k=60):                     |
                 |     RRF_Score(d) = sum_{m in {bm25, dense}} 1 / (60 + r_m)  |
                 |                                                             |
                 |  B) Min-Max Normalize Ağırlıklı Doğrusal Füzyon:           |
                 |     S_hybrid = alpha * Norm(S_bm25) + (1-alpha)*Norm(S_dense)
                 +-------------------------------------------------------------+
                                                |
                                                v
                                  [ 3. Aşama: Derin Re-ranking ]
                                  Cross-Encoder (ms-marco-TinyBERT)
                                  (Sorgu-Doküman Çifti Tam Dikkat)
                                                |
                                                v
                                   [ Nihai Sıralı Teknik Çözüm ]
```

---

### 📐 Matematiksel Formülasyon

#### 1. Reciprocal Rank Fusion (RRF)
Farklı ölçekteki ham alaka skorlarından (BM25 log-odds vs. Kosinüs benzerliği $[-1, 1]$) bağımsız çalışan, rank temelli sıralama füzyon algoritmasıdır:

$$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{w_m}{k + r_m(d)}$$

- $M = \{\text{BM25}, \text{Dense}\}$
- $k = 60$ (Cormack et al., 2009 standart sabiti)
- $r_m(d) \in [1, N]$ dokümanın $m$ motorundaki sıralaması
- $w_m = 1.0$ (Kanal ağırlıkları)

#### 2. Min-Max Normalize Ağırlıklı Doğrusal Füzyon (Weighted Score Fusion)
Ham skorların $[0, 1]$ aralığına normalize edilmesi sonrası doğrusal kombinasyonu:

$$\text{Norm}(S_m(d)) = \frac{S_m(d) - \min(S_m)}{\max(S_m) - \min(S_m) + \epsilon}$$

$$S_{\text{hybrid}}(d) = \alpha \cdot \text{Norm}(S_{\text{sparse}}(d)) + (1 - \alpha) \cdot \text{Norm}(S_{\text{dense}}(d))$$

$\alpha \in [0.0, 1.0]$ hiperparametresi grid search ile optimize edilir ($\alpha = 0.50$ dengeli mod).

---

### 📂 Modül Dizin Yapısı

```
day24/mini_project/
├── configs/
│   └── hybrid_config.json                 # RRF (k=60), BM25, Qdrant ve Cross-Encoder ayarları
├── fixtures/
│   └── merinos_technical_corpus.json      # 52 dokümanlık kurumsal teknik arıza külliyatı
├── outputs/
│   ├── hybrid_retrieval_benchmark.json    # 5 model kıyaslama raporu (15 teknik sorgu)
│   └── hybrid_retrieval_panel.png         # 2x2 Master Teşhis Paneli
├── src/
│   ├── __init__.py                        # Paket başlatıcı
│   ├── models.py                          # Pydantic v2 veri şemaları
│   ├── rrf_fusion.py                      # RRF (k=60) ve Min-Max Weighted Fusion motoru
│   ├── hybrid_engine.py                   # BM25 + Qdrant orkestrasyonu
│   ├── pipeline.py                        # 3 Aşamalı (Retrieve + Fuse + Re-rank) pipeline
│   ├── evaluator.py                       # 15 sorgu ve 5 model benchmark motoru
│   ├── visualizer.py                      # 2x2 Master Teşhis Paneli çizici
│   └── cli.py                             # Argparse komut satırı arayüzü
├── tests/
│   └── test_hybrid_retrieval.py           # 10 birim ve entegrasyon testi
└── README.md                              # Modül teknik dokümantasyonu
```

---

### 💻 CLI Kullanımı

```bash
# 1. RRF ile Hibrit Arama
python -m day24.mini_project.src.cli search-hybrid -q "rapierli tezgah dişli yağlama döngüsü" -m rrf -k 5

# 2. Ağırlıklı (Weighted) Hibrit Arama + Cross-Encoder Re-ranking
python -m day24.mini_project.src.cli search-hybrid -q "tarak ayarı ve jakar atkı hatası" -m weighted --alpha 0.6 -r -k 3

# 3. 5 Model Büyük Kıyaslama Benchmark'ı
python -m day24.mini_project.src.cli benchmark -k 5

# 4. Alpha Katsayısı Grid Search Optimizasyonu
python -m day24.mini_project.src.cli tune-alpha -k 5

# 5. 2x2 Master Teşhis Paneli Oluşturma
python -m day24.mini_project.src.cli plot
```

---

### 🔒 Lisans
ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
