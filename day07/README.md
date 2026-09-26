# Day 07 — Uzaklık ve Benzerlik Yöntemleri: Vektör Uzayı ve Boyut Laneti

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Uzaklık ve Benzerlik Yöntemleri (Yaprak 13 & 14)

---

## Goal
Bu günün amacı, halı desenleri, renk dağılımları ve üretim telemetrileri gibi vektörel özniteliklerin birbirine benzerliğini sayısal olarak hesaplamak; Öklid ($L_2$), Manhattan ($L_1$), Minkowski ($L_p$) ve Kosinüs benzerliği metriklerini formüle etmektir. Vektör boyutu arttıkça en yakın ile en uzak mesafe oranının 1'e yaklaşması olgusu olan Boyut Laneti'ni (Curse of Dimensionality) analiz etmek, vektörel normalizasyon ve k-En Yakın Komşu (`KNNPatternMatcher`, `VectorSimilaritySearchEngine`) mantığıyla desen arama altyapısı inşa etmektir.

---

## Engineer Research Assignment
- Halı yüzey analizinde mutlak büyüklüklere duyarlı metrikler ($L_1, L_2$) ile yalnızca vektörlerin açısal yönelimine odaklanan Kosinüs benzerliği arasındaki teorik farkları araştırmak.
- Öznitelik boyutu $D$ arttıkça ($D=2 \to 1024$) uzaydaki noktaların birbirine olan mesafelerinin homojenleşmesini ve bunun kümeleme/arama algoritmalarında yarattığı başarım kaybını simüle etmek.
- Vektörel ikili mesafe matrislerini (`compute_pairwise_distances`) NumPy yayınlama mekanizmasıyla döngüsüz hesaplamak.
- Bir sorgu vektörüne karşı katalogdaki en yakın $k$ deseni getiren `VectorSimilaritySearchEngine` ve `KNNPatternMatcher` sınıflarını tasarlamak.

---

## Concepts
- **Öklid Mesafesi ($L_2$ Norm):** İki vektör arasındaki doğrudan geometrik mesafe:
  $$d_2(u, v) = \sqrt{\sum_{i=1}^n (u_i - v_i)^2}$$
- **Manhattan Mesafesi ($L_1$ Norm):** Eksenler boyunca katedilen dik mesafelerin toplamı:
  $$d_1(u, v) = \sum_{i=1}^n |u_i - v_i|$$
- **Minkowski Mesafesi ($L_p$ Norm):** $L_1$ ve $L_2$'yi kapsayan genel metrik ($p=1 \to \text{Manhattan}$, $p=2 \to \text{Öklid}$):
  $$d_p(u, v) = \left( \sum_{i=1}^n |u_i - v_i|^p \right)^{1/p}$$
- **Kosinüs Benzerliği:** Vektör normlarından bağımsız açısal benzerlik:
  $$\cos(\theta) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
- **Boyut Laneti (Curse of Dimensionality):** Boyut arttıkça hacmin üstel büyümesi ve mesafelerin homojenleşmesi:
  $$\lim_{D \to \infty} \frac{d_{\max} - d_{\min}}{d_{\min}} = 0$$
- **k-En Yakın Komşu (k-NN) Vektör Arama:** Sorgu embedding'ine en yakın ilk $k$ örneğin çıkarılması.

---

## Libraries
- `numpy`: Vektörel norm hesapları, matris çarpımı ve mesafe matrisleri.
- `pytest`: Mesafe ve benzerlik birim testleri.
- `pathlib`: Dosya yolları yönetimi.

---

## Functions / Classes Studied
- `euclidean_distance()`, `manhattan_distance()`, `minkowski_distance()`, `cosine_similarity()`
- `compute_pairwise_distances()`, `KNNPatternMatcher`
- `StandardScaler`, `MinMaxScaler`, `L2Normalizer`
- `CurseOfDimensionalityAnalyzer`, `VectorSimilaritySearchEngine`
- `np.linalg.norm()`, `np.dot()`, `np.argsort()`

---

## Notebook
- **Dosya:** [`day07_uzaklik_ve_benzerlik.ipynb`](day07_uzaklik_ve_benzerlik.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Mesafe metriklerini, k-NN eşleştirmesini ve boyut laneti simülasyonunu interaktif olarak açıklar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `distance-similarity-and-knn-matcher`
- **Modüller:**
  - `src/metrics.py`: Vektörel ikili Öklid, Manhattan, Kosinüs ve Mahalanobis mesafe çekirdekleri.
  - `src/scalers.py`: Özellik ölçekleyiciler (`StandardScaler`, `MinMaxScaler`, `L2Normalizer`).
  - `src/curse_analyzer.py`: Boyutlanma arttıkça mesafe daralmasını simüle eden analiz motoru.
  - `src/search.py`: Çoklu metrikli k-NN benzerlik arama motoru (`VectorSimilaritySearchEngine`).
  - `src/distance_similarity.py`: Mesafe metrikleri ve `KNNPatternMatcher`.
  - `src/generator.py`: Sentetik desen üreteci.
  - `tests/test_similarity.py`: Uzaklık metrikleri, ölçekleyiciler ve boyut laneti testleri.
  - `tests/test_distance_similarity.py`: k-NN eşleme ve metrik testleri.

> *Not:* OpenCV filtreleme, boyutlandırma ve görüntü araçları (`filters.py`, `equalization.py`, `io_validator.py`, `resizer.py`, `test_toolkit.py`) müfredat uyumu doğrultusunda **Day 09 (OpenCV Temelleri)** projesine aktarılmıştır.

---

## Architecture
```
day07/
├── README.md
├── day07_uzaklik_ve_benzerlik.ipynb
└── mini_project/
    ├── README.md
    ├── fixtures/
    │   └── carpet_feature_embeddings.npz
    ├── src/
    │   ├── __init__.py
    │   ├── curse_analyzer.py
    │   ├── distance_similarity.py
    │   ├── generator.py
    │   ├── metrics.py
    │   ├── scalers.py
    │   └── search.py
    └── tests/
        ├── __init__.py
        ├── test_distance_similarity.py
        └── test_similarity.py
```

---

## Experiments
1. **Mesafe Metrikleri Karşılaştırma Deneyi:**
   - Öklid, Manhattan ve Kosinüs mesafelerinin geometrik özellikleri doğrulandı ($d(u, u) = 0$, simetri).
2. **Boyut Laneti Simülasyonu:**
   - Boyut $D=2$'den $D=512$'ye çıktığında $(d_{\max} - d_{\min}) / d_{\min}$ oranının hızla azalarak mesafelerin birbirine yaklaştığı ampirik olarak kanıtlandı.
3. **k-NN Benzerlik Arama Motoru:**
   - Sentetik halı embedding kataloğunda en yakın 5 komşu başarıyla sorgulandı.

---

## Validation
- Pytest ile 13 adet birim test icra edildi:
  - `test_distance_similarity.py` (3 test)
  - `test_similarity.py` (10 test)
- Tüm testler **%100 başarıyla (13 passed)** geçti.

---

## Results
- Heterojen veri özniteliklerinin benzerlik hesaplamaları matematiksel temellere oturtuldu.
- Boyutsallık lanetinin mesafe ayırt ediciliği üzerindeki sınırları nicel olarak belirlendi.
- Tüm veriler sentetik test senaryolarından oluşmaktadır.

---

## Limitations
- Arama motoru brute-force ($O(N \cdot D)$) mantığıyla çalışmaktadır; ANN (Approximate Nearest Neighbors), IVF ve HNSW gibi endeksleme yapıları Faz 3'te (Day 26) incelenecektir.

---

## Files
- `day07/README.md`
- `day07/day07_uzaklik_ve_benzerlik.ipynb`
- `day07/mini_project/README.md`
- `day07/mini_project/src/__init__.py`
- `day07/mini_project/src/metrics.py`
- `day07/mini_project/src/scalers.py`
- `day07/mini_project/src/curse_analyzer.py`
- `day07/mini_project/src/search.py`
- `day07/mini_project/src/distance_similarity.py`
- `day07/mini_project/src/generator.py`
- `day07/mini_project/tests/test_similarity.py`
- `day07/mini_project/tests/test_distance_similarity.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day07/mini_project/tests/ -v
```

---

## Next Day
- **Day 08:** Keşifsel Veri Analizi (EDA) — İstatistiksel dağılımlar, aykırı değer tespiti (IQR/Z-score) ve korelasyon analizi.