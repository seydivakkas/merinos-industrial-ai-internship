# Day 06 — NumPy ve Vektörel Hesaplama: Büyük Ölçekli Matris İşlemleri ve Performans

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** NumPy ve Vektörel Hesaplama: Büyük Ölçekli Matris İşlemleri ve Performans (Yaprak 11 & 12)

## Goal
Bu günün amacı, Merinos halı fabrikası üretim süreçlerinde ortaya çıkan yüz binlerce satırlık sensör telemetrileri ve milyonlarca piksellik görüntü matrisleri üzerinde saf Python `for` döngülerinin yarattığı işlemci darboğazını ortadan kaldırmaktır. NumPy kütüphanesinin `ndarray` veri yapısı, C düzeyinde ardışık bellek yerleşimi (C-contiguous strides), yayınlama (broadcasting) kuralları ve SIMD (Single Instruction Multiple Data) vektörizasyon teknikleri kullanılarak 20x–100x hesaplama hızlanması sağlayan ölçekleme ve matris manipülasyon modülleri (`StandardScaler`, `MinMaxScaler`) geliştirmektir.

---

## Engineer Research Assignment
- CPython dinamik tip denetimi ve nesne paketleme (boxing/unboxing) maliyetlerinin saf Python döngülerinde oluşturduğu gecikmeyi mikrosaniye hassasiyetinde profillemek.
- NumPy `ndarray` yapısının donanım L1/L2/L3 önbellek hatlarına (cache line) tam oturan ardışık bellek adımlarını (strides) ve önbellek yerelliği (cache locality) avantajlarını incelemek.
- Bellek kopyalaması yapmadan farklı boyutlu tensörleri işleme sokan yayınlama (broadcasting) kurallarını analiz etmek.
- Vektörel Z-score standardizasyonu ve Min-Max ölçekleme sınıflarını tasarlayarak sayısal doğruluk (`np.allclose`) ve döngüsüz hesaplama başarımı elde etmek.

---

## Concepts
- **`ndarray` Mimarisi ve Bellek Adımları (Strides):** Çok boyutlu dizilerin tek boyutlu ardışık bellek adreslerine satır bazlı (row-major / C-order) eşlenmesi formülü:
  $$\text{ByteOffset}(i, j) = i \cdot s_0 + j \cdot s_1$$
- **SIMD Vektörizasyonu:** Tek bir işlemci komutuyla birden çok veri noktası üzerinde paralel hesaplama yürütülmesi.
- **Yayınlama (Broadcasting):** Boyutları uyumlu ($d_1 = d_2$ veya birisi $1$) olan matrislerin bellek tüketmeden sanal olarak hizalanması.
- **Vektörel Ölçekleme:**
  - Min-Max: $X_{\text{norm}} = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$
  - Z-score: $X_{\text{std}} = \frac{X - \mu}{\sigma}$
- **Hızlanma Faktörü (Speedup Factor):** $\mathcal{S} = T_{\text{loop}} / T_{\text{vec}}$

---

## Libraries
- `numpy`: SIMD vektörizasyonu, broadcasting, BLAS matris çarpımları ve sayısal işlemler.
- `time`: Yüksek çözünürlüklü performans sayaçları (`time.perf_counter`).
- `matplotlib`: Hesaplama süreleri ve logaritmik başarım grafikleri.
- `pytest`: Sayısal eşitlik ve birim testler.

---

## Functions / Classes Studied
- `StandardScaler`, `MinMaxScaler`, `L2Normalizer`
- `np.ndarray.strides`, `np.allclose()`, `np.dot()`, `np.mean()`, `np.std()`
- `CurseOfDimensionalityAnalyzer`, `VectorSimilaritySearchEngine`

---

## Notebook
- **Dosya:** [`day06_numpy_vektorel_hesaplama.ipynb`](day06_numpy_vektorel_hesaplama.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Saf Python döngüleri ile NumPy vektörel matris çarpımı arasındaki 20x–100x başarım farkını ve boyut uyuşmazlığı hatalarını inceler.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `numpy-vectorization-and-matrix-computation`
- **Modüller:**
  - `src/scalers.py`: Vektörel `StandardScaler`, `MinMaxScaler` ve `L2Normalizer` sınıfları.
  - `src/metrics.py`: Vektörize uzaklık ve benzerlik fonksiyonları.
  - `src/curse_analyzer.py`: Yüksek boyutlu uzayda mesafe analitiği modülü.
  - `src/search.py`: Vektörel arama motoru.
  - `src/generator.py`: Sentetik özellik matris üreteci.
  - `tests/test_similarity.py`: Vektörel ölçekleyiciler ve matris hesaplama birim testleri.

---

## Architecture
```
day06/
├── README.md
├── day06_numpy_vektorel_hesaplama.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── scalers.py
    │   ├── metrics.py
    │   ├── curse_analyzer.py
    │   ├── search.py
    │   └── generator.py
    ├── tests/
    │   ├── __init__.py
    │   └── test_similarity.py
    └── outputs/
```

---

## Experiments
1. **Döngü vs Vektörizasyon Hız Kıyaslaması:**
   - 500.000 satırlık 3 kanallı sentetik görüntü matrisi üzerinde luma ağırlıklandırma işlemi test edildi.
   - Python `for` döngüsü ile tahmini süre saniyeler mertebesindeyken, NumPy `@` matris çarpımı mikrosaniye mertebesinde tamamlanarak **30x+ hızlanma** sağladı.
2. **Standardizasyon Doğrulaması:**
   - Standardize edilen matrisin sütun ortalamasının 0 ($\pm 10^{-7}$) ve standart sapmasının 1 ($\pm 10^{-7}$) olduğu `np.allclose` ile doğrulandı.

---

## Validation
- Pytest ile 10 adet birim test icra edildi:
  - `test_scalers_standard_and_minmax`
  - `test_vector_similarity_metrics`
  - `test_search_engine_top_k`
  - `test_curse_of_dimensionality`
- Tüm testler **%100 başarıyla (10 passed)** geçti.

---

## Results
- Büyük ölçekli telemetri ve piksel matrislerinde saf Python döngülerinin elenerek C seviyesinde vektörizasyona geçilmesi garanti altına alınmıştır.
- Standartlaştırıcı sınıflar deterministik ve yüksek performanslı olarak doğrulanmıştır.

---

## Limitations
- GPU tensör hızlandırması (PyTorch CUDA tensörleri) bu aşamada değil, Faz 2 (Day 16) ve sonrasında kullanılacaktır; bu günde saf CPU SIMD optimizasyonuna odaklanılmıştır.
- Belleğe sığmayan (out-of-core) devasa veri setleri için bellek haritalı (memmap) yapılar ilerleyen fazlarda incelenecektir.

---

## Files
- `day06/README.md`
- `day06/day06_numpy_vektorel_hesaplama.ipynb`
- `day06/mini_project/README.md`
- `day06/mini_project/src/__init__.py`
- `day06/mini_project/src/scalers.py`
- `day06/mini_project/src/metrics.py`
- `day06/mini_project/src/curse_analyzer.py`
- `day06/mini_project/src/search.py`
- `day06/mini_project/src/generator.py`
- `day06/mini_project/tests/__init__.py`
- `day06/mini_project/tests/test_similarity.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day06/mini_project/tests/ -v
```

---

## Next Day
- **Day 07:** Uzaklık ve Benzerlik Yöntemleri: Vektör Uzayı ve Boyut Laneti — Öklid, Manhattan, Kosinüs metrikleri ve k-En Yakın Komşu (k-NN) örüntü eşleme.