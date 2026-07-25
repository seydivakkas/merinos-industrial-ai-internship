# Day 05 Mini Project: NumPy Vektörize Operasyonlar ve Matris Hesaplama Laboratuvarı

Bu mini proje, Merinos fabrikasyon ortamında dokuma tezgâhı koordinatörleri, optik kalite kontrol kameraları ve desen tarayıcılarından gelen yüksek çözünürlüklü 2D ve 3D matrisler ($H \times W \times C$) üzerinde saf Python döngüleri (naive loop), NumPy SIMD vektörizasyonu, broadcasting kuralları ve Einstein Summation (`np.einsum`) arasındaki başarım farklarını ölçümleyen kapsamlı bir benchmark ve bellek analizi motorudur.

---

## 📁 Proje Yapısı

```bash
day05/mini_project/
├── configs/
│   └── benchmark_config.json        # Matris çözünürlükleri, ısınma/tekrar parametreleri
├── fixtures/
│   └── synthetic_patterns.npz       # Çok çözünürlüklü sentetik halı desen ve ilmek tensörleri
├── src/
│   ├── __init__.py
│   ├── generator.py                 # Sentetik halı deseni ve ilmek yoğunluğu matris üreteci
│   ├── operations.py                # Naive vs Vectorized vs Einsum operasyon çiftleri
│   ├── memory_analyzer.py           # C/F-Contiguous bellek düzeni, strides ve önbellek analizi
│   └── benchmark.py                 # BenchmarkEngine, istatistiksel zamanlayıcı ve raporlayıcı
├── tests/
│   ├── __init__.py
│   └── test_benchmarks.py           # 10 kapsamlı birim ve performans testi
├── outputs/
│   ├── benchmark_results.json       # Milisaniye gecikme, bellek tüketimi ve hızlanma oranları
│   ├── memory_layout_report.json    # Strides, bellek boyutu ve CPU önbellek yerelliği raporu
│   └── performance_summary.md       # Kurumsal Markdown özet tablosu
└── README.md                        # Bu dokümantasyon
```

---

## ⚙️ Uygulanan Operasyonlar ve Matematiksel Formüller

1. **Luma Kanal Ağırlıklandırması (RGB $\rightarrow$ Grayscale):**
   $$Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
   - *Naive:* 3 iç içe Python döngüsü.
   - *Vectorized:* NumPy broadcasting ile `np.sum(img * weights, axis=-1)`.
   - *Einsum:* `np.einsum('hwc,c->hw', img, weights)`.

2. **Min-Max Normalizasyonu:**
   $$X_{\text{norm}} = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$$
   - *Naive:* Döngüyle min/max bulma ve ölçekleme.
   - *Vectorized:* NumPy SIMD min/max ve dizi tensör çıkarma/bölme.

3. **Z-Score Standardizasyonu:**
   $$X_{\text{std}} = \frac{X - \mu}{\sigma}$$
   - *Naive:* Ortalama ve varyansı döngüyle toplama.
   - *Vectorized:* `(X - np.mean(X)) / np.std(X)`.

4. **Gram Matrisi (Doku & Stil Özellik Matrisi):**
   $$G_{ij} = \sum_{k=1}^N F_{ik} F_{jk} \quad \implies \quad G = F \cdot F^T$$
   - *Naive:* 3 iç içe döngü ($C \times C \times N$).
   - *Vectorized:* BLAS hızlandırmalı `np.matmul(F, F.T)`.
   - *Einsum:* `np.einsum('ik,jk->ij', F, F)`.

5. **Mekânsal Kutu Filtreleme (2D Spatial Box Blur):**
   - *Naive:* 4 iç içe döngü ile kayan pencere ortalaması.
   - *Vectorized:* `np.lib.stride_tricks.sliding_window_view` ile sıfır kopyalı görünüm ve eksen bazlı ortalama.

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day05/mini_project/tests/ -v
```

## 🚀 Kıyaslama Motorunu Çalıştırma

```bash
python -m day05.mini_project.src.benchmark
```
Çıktılar `day05/mini_project/outputs/` dizinine otomatik kaydedilir.
