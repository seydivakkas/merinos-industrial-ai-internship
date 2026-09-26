# Day 07 — Uzaklık ve Benzerlik Yöntemleri: Vektör Uzayı ve Boyut Laneti

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Uzaklık ve Benzerlik Yöntemleri (Yaprak 13 & 14)

## Goal
Bu günün amacı, halı desenleri, renk dağılımları ve üretim telemetrileri gibi vektörel özniteliklerin birbirine benzerliğini sayısal olarak hesaplamak; Öklid ($L_2$), Manhattan ($L_1$), Minkowski ($L_p$) ve Kosinüs benzerliği metriklerini formüle etmektir. Vektör boyutu arttıkça en yakın ile en uzak mesafe oranının 1'e yaklaşması olgusu olan Boyut Laneti'ni (Curse of Dimensionality) analiz etmek ve k-En Yakın Komşu (`KNNPatternMatcher`) mantığıyla desen eşleme altyapısı inşa etmektir.

---

## Engineer Research Assignment
- Halı yüzey analizinde mutlak büyüklüklere duyarlı metrikler ($L_1, L_2$) ile yalnızca vektörlerin açısal yönelimine odaklanan Kosinüs benzerliği arasındaki teorik farkları araştırmak.
- Öznitelik boyutu $D$ arttıkça ($D=2 \to 1024$) uzaydaki noktaların birbirine olan mesafelerinin homojenleşmesini ve bunun kümeleme/arama algoritmalarında yarattığı başarım kaybını simüle etmek.
- Vektörel ikili mesafe matrislerini (`compute_pairwise_distances`) NumPy yayınlama mekanizmasıyla $O(N^2)$ sürede döngüsüz hesaplamak.
- Bir sorgu vektörüne karşı katalogdaki en yakın $k$ deseni getiren `KNNPatternMatcher` sınıfını tasarlamak.

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
- **Boyut Laneti (Curse of Dimensionality):** Boyut arttıkça hacmin üstel büyümesi ve mesafelerin anlamsızlaşması:
  $$\lim_{D \to \infty} \frac{d_{\max} - d_{\min}}{d_{\min}} = 0$$
- **k-En Yakın Komşu (k-NN):** Sorgu özniteliğine en düşük mesafedeki ilk $k$ örneğin getirilmesi.

---

## Libraries
- `numpy`: Vektörel norm hesapları, matris çarpımı ve mesafe matrisleri.
- `pytest`: Mesafe ve benzerlik birim testleri.
- `pathlib`: Dosya yolları yönetimi.

---

## Functions / Classes Studied
- `euclidean_distance()`, `manhattan_distance()`, `minkowski_distance()`, `cosine_similarity()`
- `compute_pairwise_distances()`, `KNNPatternMatcher`
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
  - `src/distance_similarity.py`: Uzaklık metrikleri, ikili mesafe matrisi ve `KNNPatternMatcher`.
  - `src/analytics.py`, `src/color_spaces.py`, `src/equalization.py`, `src/filters.py`: Destekleyici görsel analitik modülleri.
  - `tests/test_distance_similarity.py`: Mesafe ve k-NN eşleme testleri.
  - `tests/test_toolkit.py`: Görsel araç seti ve girdi doğrulama testleri.

---

## Architecture
```
day07/
├── README.md
├── day07_uzaklik_ve_benzerlik.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── distance_similarity.py
    │   ├── analytics.py
    │   ├── color_spaces.py
    │   ├── equalization.py
    │   ├── filters.py
    │   ├── generator.py
    │   ├── io_validator.py
    │   └── resizer.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_distance_similarity.py
    │   └── test_toolkit.py
    └── outputs/
```

---

## Experiments
1. **Mesafe ve Benzerlik Doğrulama Deneyi:**
   - $u = [1, 2, 3]$ ve $v = [4, 6, 3]$ vektörleri için Öklid mesafesi tam $5.0$, Manhattan mesafesi $7.0$, Minkowski ($p=2$) mesafesi $5.0$ olarak doğrulandı.
   - Kendisiyle kıyaslanan vektörün Kosinüs benzerliği tam $1.0$ çıktı.
2. **k-NN Halı Deseni Eşleme:**
   - Kırmızı ağırlıklı sorgu vektörü ($[0.9, 0.1, 0.0]$), veri tabanındaki desenler arasından en yakın aday olarak `carpet_red` örneğini 1. sırada getirdi.

---

## Validation
- Pytest ile 13 adet birim test icra edildi:
  - `test_distance_metrics` (Öklid, Manhattan, Kosinüs, Minkowski)
  - `test_knn_pattern_matcher` (k-NN en yakın komşu doğrulaması)
  - `test_pairwise_distance_matrix` (İkili mesafe simetrisi ve diyagonal sıfır kontrolü)
  - `test_toolkit_*` (Görsel öznitelik ve histogram testleri)
- Tüm testler **%100 başarıyla (13 passed)** geçti.

---

## Results
- Halı desenleri ve telemetrileri için matematiksel olarak tutarlı uzaklık ve benzerlik altyapısı kurulmuştur.
- k-NN arama motorunun referans baseline olarak çalışabileceği teyit edilmiştir.

---

## Limitations
- k-NN algoritması büyük kataloglarda ($N > 100.000$) doğrusal arama ($O(N)$) yaptığından yavaşlayabilir; yaklaşık en yakın komşu (ANN / HNSW / Faiss) yaklaşımları Vektör Arama fazında (Day 23) devreye alınacaktır.
- Testler sentetik özellik vektörleri ile yürütülmüştür.

---

## Files
- `day07/README.md`
- `day07/day07_uzaklik_ve_benzerlik.ipynb`
- `day07/mini_project/README.md`
- `day07/mini_project/src/__init__.py`
- `day07/mini_project/src/distance_similarity.py`
- `day07/mini_project/tests/__init__.py`
- `day07/mini_project/tests/test_distance_similarity.py`
- `day07/mini_project/tests/test_toolkit.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day07/mini_project/tests/ -v
```

---

## Next Day
- **Day 08:** Keşifsel Veri Analizi (EDA): Dağılım, Aykırı Değer ve Korelasyon Analizi — İstatistiksel özetler, çeyrekler arası aralık (IQR), Z-skoru ve korelasyon ısı haritaları.