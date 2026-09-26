# Day 06 — NumPy ve Vektörel Hesaplama: Büyük Ölçekli Matris İşlemleri ve Performans

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** NumPy ve Vektörel Hesaplama: Büyük Ölçekli Matris İşlemleri ve Performans (Yaprak 11 & 12)

---

## Goal
Bu günün amacı, Merinos halı fabrikası üretim süreçlerinde ortaya çıkan yüz binlerce satırlık sensör telemetrileri ve milyonlarca piksellik dokuma matrisleri üzerinde saf Python `for` döngülerinin yarattığı işlemci darboğazını ortadan kaldırmaktır. NumPy kütüphanesinin `ndarray` veri yapısı, C düzeyinde ardışık bellek yerleşimi (C-contiguous strides), yayınlama (broadcasting) kuralları ve SIMD (Single Instruction Multiple Data) vektörizasyon teknikleri kullanılarak onlarca kat hesaplama hızlanması sağlayan matris manipülasyon ve başarım ölçüm modülleri (`ArrayOperations`, `VectorizationBenchmark`, `ImageMatrixToolkit`) geliştirmektir.

---

## Engineer Research Assignment
- CPython dinamik tip denetimi ve nesne paketleme (boxing/unboxing) maliyetlerinin saf Python döngülerinde oluşturduğu gecikmeyi mikrosaniye hassasiyetinde profillemek.
- NumPy `ndarray` yapısının donanım L1/L2/L3 önbellek hatlarına (cache line) tam oturan ardışık bellek adımlarını (strides) ve önbellek yerelliği (cache locality) avantajlarını incelemek.
- Bellek kopyalaması yapmadan farklı boyutlu tensörleri işleme sokan yayınlama (broadcasting) kurallarını analiz etmek.
- Vektörel Z-score standardizasyonu, Min-Max ölçekleme ve eşikleme fonksiyonlarını döngüsüz olarak kodlamak.

---

## Concepts
- **`ndarray` Mimarisi ve Bellek Adımları (Strides):** Çok boyutlu dizilerin tek boyutlu ardışık bellek adreslerine satır bazlı (row-major / C-order) eşlenmesi formülü:
  $$\text{ByteOffset}(i, j) = i \cdot s_0 + j \cdot s_1$$
- **SIMD Vektörizasyonu:** Tek bir işlemci komutuyla birden çok veri noktası üzerinde paralel hesaplama yürütülmesi.
- **Yayınlama (Broadcasting):** Boyutları uyumlu ($d_1 = d_2$ veya birisi $1$) olan matrislerin bellek tüketmeden sanal olarak hizalanması.
- **Vektörel Ölçekleme ve Eşikleme:** Döngüsüz Min-Max, Z-score ve boolean maskeleme.
- **Hızlanma Faktörü (Speedup Factor):** $\mathcal{S} = T_{\text{loop}} / T_{\text{vec}}$

---

## Libraries
- `numpy`: SIMD vektörizasyonu, broadcasting, matris çarpımları ve sayısal işlemler.
- `time`: Yüksek çözünürlüklü performans sayaçları (`time.perf_counter`).
- `pytest`: Sayısal eşitlik ve birim testler.

---

## Functions / Classes Studied
- `ArrayOperations`, `VectorizationBenchmark`, `ImageMatrixToolkit`
- `np.ndarray.strides`, `np.allclose()`, `np.dot()`, `np.mean()`, `np.std()`, `np.meshgrid()`
- `CarpetEmbeddingGenerator`

---

## Notebook
- **Dosya:** [`day06_numpy_vektorel_hesaplama.ipynb`](day06_numpy_vektorel_hesaplama.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Saf Python döngüleri ile NumPy vektörel matris işlemleri arasındaki hızlanmayı ve boyut uyuşmazlığı hatalarını inceler.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `numpy-vectorization-and-matrix-computation`
- **Modüller:**
  - `src/array_ops.py`: Vektörel Min-Max, Z-score, matris istatistikleri, renk kanalı öteleme (broadcasting) ve eşikleme modülü.
  - `src/vectorization_benchmark.py`: Python döngüleri ile NumPy SIMD vektörizasyonunu süre ve hızlanma faktörüyle karşılaştıran benchmark motoru.
  - `src/image_matrix.py`: Sentetik dokuma deseni üretimi, adım bazlı yama (patch) dilimleme ve enerji hesaplama araçları.
  - `src/generator.py`: Sentetik özellik matris üreteci.
  - `tests/test_array_ops.py`: Vektörel operasyonlar, broadcasting ve benchmark birim testleri.

> *Not:* Uzaklık metrikleri ve yüksek boyutlu benzerlik arama motoru (`metrics.py`, `scalers.py`, `curse_analyzer.py`, `search.py`), müfredat uyumu doğrultusunda **Day 07 (Uzaklık ve Benzerlik Ölçümleri)** projesine aktarılmıştır.

---

## Architecture
```
day06/
├── README.md
├── day06_numpy_vektorel_hesaplama.ipynb
└── mini_project/
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── array_ops.py
    │   ├── generator.py
    │   ├── image_matrix.py
    │   └── vectorization_benchmark.py
    └── tests/
        ├── __init__.py
        └── test_array_ops.py
```

---

## Experiments
1. **Döngü vs. Vektörizasyon Hızlanma Deneyi:**
   - 50.000 elemanlı toplama işleminde NumPy SIMD vektörizasyonu saf Python döngüsüne kıyasla 20x'in üzerinde hızlanma sağladı (`is_vectorized_faster: true`).
2. **Broadcasting ile Renk Kanalı Ötelemesi:**
   - $(H, W, 3)$ görsel matrisine $(3,)$ renk vektörü tek satırda döngüsüz olarak eklendi.
3. **Dokuma Deseni Yama Dilimleme:**
   - Sentetik dokuma matrisi bellek kopyalaması yapmadan alt yamalara bölündü ve yama enerjileri hesaplandı.

---

## Validation
- Pytest ile 7 adet birim test icra edildi:
  - `test_normalize_min_max`
  - `test_standardize_z_score`
  - `test_matrix_statistics`
  - `test_broadcast_color_bias`
  - `test_threshold_matrix`
  - `test_vectorization_benchmark`
  - `test_image_matrix_toolkit`
- Tüm testler **%100 başarıyla (7 passed)** geçti.

---

## Results
- Saf Python döngülerinin getirdiği işlemci darboğazı NumPy vektörizasyonu ile giderildi.
- Sentetik matris ve tensör operasyonları başarıyla doğrulandı.

---

## Limitations
- İşlemler CPU SIMD (AVX/SSE) üzerinde yürütülmüştür; GPU tensör çekirdekleri (CUDA) derin öğrenme aşamalarında ele alınacaktır.

---

## Files
- `day06/README.md`
- `day06/day06_numpy_vektorel_hesaplama.ipynb`
- `day06/mini_project/README.md`
- `day06/mini_project/src/__init__.py`
- `day06/mini_project/src/array_ops.py`
- `day06/mini_project/src/vectorization_benchmark.py`
- `day06/mini_project/src/image_matrix.py`
- `day06/mini_project/src/generator.py`
- `day06/mini_project/tests/test_array_ops.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day06/mini_project/tests/ -v
```

---

## Next Day
- **Day 07:** Uzaklık ve Benzerlik Ölçümleri — Öklid, Kosinüs ve Manhattan uzaklıkları, vektör benzerlik araması ve boyutsallık laneti.