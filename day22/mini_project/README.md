# Merinos Sparse Retrieval Engine: TF-IDF & Okapi BM25

> **Aşama:** Faz 4: Retrieval & Hibrit Arama (Day 22–28)  
> **Konu:** Day 22: Metinlerin Sayısal Temsili ve Seyrek Getirme Motoru (Sparse Retrieval)  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.  
> **Lisans Badge:** ![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. Gaziantep 4. OSB tesislerinde yüzlerce Van de Wiele jakarlı dokuma tezgâhı, iplik ekstrüzyon hatları, büküm ve fikse makineleri ile boyahane fırınları 7/24 kesintisiz çalışmaktadır. Bu devasa makine parkurunun teknik servis el kitapçıkları, arıza kod tabloları (örn. `ERR-W-204`, `ERR-J-108`), periyodik bakım kılavuzları ve kalite şartnameleri yüzlerce teknik doküman oluşturmaktadır.

Saha teknisyenleri veya otonom arıza teşhis asistanları için ilk ve en kritik adım, serbest metinli teknik arıza sorgularına karşılık gelen doğru bakım protokolünü milisaniyeler içerisinde getirebilmektir. **Day 22**, bu ihtiyacı karşılamak amacıyla saf Python ve NumPy ile sıfırdan geliştirilen yüksek performanslı **Ters İndeks (Inverted Index)**, **Türkçe Karakter Duyarlı Tokenizasyon**, **TF-IDF Vektörleme** ve **Okapi BM25 Probabilistik Sıralama Motoru**'nu içermektedir.

---

## 📐 Matematiksel ve Algoritmik Temeller

### 1. Türkçe Karakter Duyarlı Tokenizasyon & Ters İndeks
Metinler önce küçük harfe dönüştürülür. Türkçe karakter kuralına göre:
$$I \to \text{ı}, \quad \dot{I} \to \text{i}$$
Noktalama işaretleri temizlenir, Türkçe durak sözcükler (stopwords) elenir ve 2-gram kombinasyonları üretilir.

Ters İndeks yapısı, sözlükteki her $t$ terimini o terimin geçtiği doküman kimlikleri ($d$) ve frekanslarıyla ($f_{t,d}$) eşler:
$$\text{Postings}(t) = \{(d_1, f_{t, d_1}), (d_2, f_{t, d_2}), \dots\}$$

### 2. Alt Doğrusal TF-IDF (Sublinear TF & Smooth IDF)
Standart terim frekansı yerine terim sıklığındaki aşırı artışı sönümleyen alt doğrusal (sublinear) TF kullanılır:
$$\text{TF}_{\text{sublinear}}(t, d) = \begin{cases} 1 + \log(f_{t,d}), & \text{eğer } f_{t,d} > 0 \\ 0, & \text{aksi halde} \end{cases}$$

Sıfıra bölme hatasını önleyen düzleştirilmiş ters doküman frekansı (Smooth IDF):
$$\text{IDF}_{\text{smooth}}(t, D) = \log\left( \frac{1 + N}{1 + n_t} \right) + 1$$
burada $N$ külliyattaki toplam doküman sayısı, $n_t$ ise $t$ terimini içeren doküman sayısıdır.

Sorgu-doküman benzerliği $L_2$ normalizasyonu yapılmış kosinüs benzerliği ile puanlanır:
$$\text{Score}_{\text{TF-IDF}}(q, d) = \frac{\sum_{t \in q \cap d} \mathbf{v}_{q}(t) \cdot \mathbf{v}_{d}(t)}{\|\mathbf{v}_q\|_2 \cdot \|\mathbf{v}_d\|_2}$$

### 3. Okapi BM25 Probabilistik Sıralama Modeli
Okapi BM25, bilgi getirme teorisinde terim doygunluğu ($k_1$) ve doküman uzunluk normalizasyonu ($b$) sağlayan endüstri standardı algoritmadır:

$$\text{BM25}(D, Q) = \sum_{q \in Q} \text{IDF}_{\text{BM25}}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

- **BM25 IDF Formülü:**
  $$\text{IDF}_{\text{BM25}}(q) = \log\left( \frac{N - n(q) + 0.5}{n(q) + 0.5} + 1 \right)$$
- **Terim Frekansı Doygunluğu ($k_1 = 1.5$):** Bir kelimenin dokümanda 1 kez yerine 10 kez geçmesi skoru 10 katına çıkarmaz; asimptotik olarak sınırlandırır.
- **Doküman Uzunluk Cezası ($b = 0.75$):** Ortalama doküman uzunluğundan ($\text{avgdl}$) uzun dokümanlarda terimlerin tesadüfen geçme olasılığı yüksek olduğu için skor cezalandırılır; kısa ve yoğun dokümanlar öne çıkarılır.

### 4. Bilgi Getirme Değerlendirme Metrikleri
- **Precision@K:** Getirilen ilk $K$ doküman içerisindeki ilgili doküman oranı.
- **Recall@K:** Zemin gerçekteki tüm ilgili dokümanların ilk $K$'da yakalanma oranı.
- **MRR (Mean Reciprocal Rank):** İlk doğru dokümanın bulunduğu sıranın çarpmaya göre tersi:
  $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
- **NDCG@K (Normalized Discounted Cumulative Gain):** Sıralama kalitesini logaritmik sıra indirimi ile ölçer:
  $$\text{DCG}@K = \sum_{i=1}^K \frac{\text{rel}_i}{\log_2(i + 1)}, \quad \text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$

---

## 📂 Paket Mimarisi

```
day22/mini_project/
├── configs/
│   └── retrieval_config.json               # BM25 k1/b, n-gram ve sorgu hiperparametreleri
├── fixtures/
│   └── merinos_technical_corpus.json       # 52 adet kurumsal Merinos arıza ve bakım dokümanı
├── outputs/
│   ├── inverted_index.json                 # Ters indeks sözlük ve postings listesi
│   ├── sparse_retrieval_benchmark.json     # BM25 vs TF-IDF karşılaştırmalı performans raporu
│   └── sparse_retrieval_panel.png          # 2x2 master teşhis ve kıyas paneli
├── src/
│   ├── __init__.py                         # Paket kökü
│   ├── models.py                           # Pydantic v2 veri şemaları
│   ├── tokenizer.py                        # Türkçe uyumlu tokenizasyon motoru
│   ├── inverted_index.py                   # Ters indeksleme ve istatistik motoru
│   ├── tfidf_engine.py                     # Sublinear TF-IDF getirme motoru
│   ├── bm25_engine.py                      # Okapi BM25 getirme motoru
│   ├── evaluator.py                        # P@K, R@K, MRR, NDCG@K değerlendirme motoru
│   ├── visualizer.py                       # Matplotlib 2x2 master panel görselleştirici
│   └── cli.py                              # Argparse tabanlı terminal arayüzü
├── tests/
│   └── test_sparse_retrieval.py            # 10 adet birim ve entegrasyon testi
└── README.md                               # Bu teknik doküman
```

---

## 🚀 Komut Satırı Arayüzü (CLI) Kullanımı

Tüm operasyonlar modüler CLI aracılığıyla tetiklenebilir:

```bash
# 1. Külliyatı oku ve Ters İndeksi inşa et
python -m day22.mini_project.src.cli build-index

# 2. Okapi BM25 ile arıza sorgusu yap
python -m day22.mini_project.src.cli search-bm25 --query "atkı ipliği kopması IRO Stella arıza" --top-k 3

# 3. TF-IDF ile teknik sorgu yap
python -m day22.mini_project.src.cli search-tfidf --query "jakar deseni kayması enkoder senkronizasyon" --top-k 3

# 4. Kıyaslama (Benchmark) çalıştır ve metrikleri kaydet
python -m day22.mini_project.src.cli benchmark

# 5. 2x2 Master Teşhis Panelini üret
python -m day22.mini_project.src.cli plot
```

---

## 📊 Karşılaştırmalı Performans Sonuçları (Benchmark)

15 kurumsal teknik sorgu üzerinde 52 dokümanlık Merinos külliyatında yapılan değerlendirme sonuçları:

| Model | Precision@1 | Precision@3 | Precision@5 | Recall@5 | MRR | NDCG@5 | Ort. Gecikme (ms) | QPS (Sorgu/sn) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Okapi BM25** ($k_1=1.5, b=0.75$) | **%100.0** | **%64.4** | **%44.0** | **%100.0** | **1.0000** | **1.0000** | **0.072 ms** | **13,870.9** |
| **TF-IDF (Sublinear + Cosine)** | %93.3 | %62.2 | %42.7 | %93.3 | 0.9667 | 0.9742 | 0.145 ms | 6,897.4 |

> **Önemli Çıkarım:** Okapi BM25, uzunluk normalizasyonu ($b=0.75$) sayesinde gereksiz uzun ve genel dokümanların skorunu düşürerek doğrudan hedefe yönelik bakım protokollerini en başa (MRR: 1.0000) taşımıştır.

---

## 🧪 Birim ve Entegrasyon Testleri

```bash
python -m pytest day22/mini_project/tests/test_sparse_retrieval.py -v
```

10 adet kapsamlı test:
1. `test_turkish_tokenizer_lower_and_punctuation`: Türkçe karakter uyumu ($I \to \text{ı}$, $\dot{I} \to \text{i}$).
2. `test_turkish_tokenizer_ngrams_and_stopwords`: Stopword temizliği ve 2-gram üretimi.
3. `test_inverted_index_creation_and_lookup`: Postings ve ortalama doküman boyu doğrulaması.
4. `test_inverted_index_serialization`: JSON kaydetme ve geri yükleme determinizmi.
5. `test_tfidf_engine_search_exact_match`: TF-IDF tam eşleşme ve snippet çıkarımı.
6. `test_bm25_engine_search_relevance`: BM25 ile arıza kodu eşleştirme ve pozitif skor denetimi.
7. `test_bm25_length_normalization_penalty`: Uzunluk cezasının ($b=0.75$) doğrulanması.
8. `test_evaluator_metrics_calculation`: MRR, P@K, Recall@K ve NDCG@K hesaplama hassasiyeti.
9. `test_cli_execution_full_pipeline`: CLI argümanlarının uçtan uca hatasız çalışması.
10. `test_benchmark_comparison_bm25_superior_or_equal_to_tfidf`: BM25'in TF-IDF'e göre üstünlük testi.

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
