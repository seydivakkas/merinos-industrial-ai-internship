# Day 11 — K-Means ile Baskın Renk ve Palet Çıkarımı

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** K-Means ile Baskın Renk ve Palet Çıkarımı (Yaprak 21 & 22)

## Goal
Bu günün amacı, Merinos jakarlı halı dokuma tezgâhlarının mekanik iplik bobini sınırları (genellikle tezgâh başına 8–12 farklı renk bobini / creel kapasitesi) doğrultusunda, zengin renk geçişli dijital desen fotoğraflarından gözetimsiz K-Means kümeleme algoritması ile $K$ adet baskın rengi ve bu renklerin yüzeydeki alan oranlarını ($\%$) çıkaran, iplik reçetesi için HEX kodlu palet üreten bir kuantizasyon motoru (`KMeansPaletteExtractor`) inşa etmektir.

---

## Engineer Research Assignment
- Sürekli 24-bit RGB renk uzayındaki milyonlarca rengin, jakarlı tezgâhın ayrık bobin kapasitesine indirgenmesinde (renk kuantizasyonu) K-Means optimizasyon amaç fonksiyonunu formüle etmek:
  $$J = \sum_{j=1}^k \sum_{i \in S_j} \|x_i - \mu_j\|^2$$
- Milyonlarca piksellik yüksek çözünürlüklü halı taramalarında işlemci ve bellek darboğazını engellemek için deterministik çekirdekli rastgele alt-örnekleme ($N = 50.000$ piksel) uygulamasının hız/temsil gücü başarımını incelemek.
- Küme merkezlerinin (`cluster_centers_`) yuvarlanarak RGB ve HEX formatlarına dönüştürülmesi ve her kümenin etiket sıklığı (`np.bincount`) ile yüzey dağılım yüzdesinin hesaplanması.
- `KMeansPaletteExtractor` ile çıkarılan paletin alan yüzdelerinin toplamının %100'e denk geldiğini test etmek.

---

## Concepts
- **K-Means Kümeleme:** Piksel renk vektörlerini ($R, G, B$) en yakın küme merkezine atayarak küme içi varyansı (inertia) minimize etme.
- **Renk Kuantizasyonu (Color Quantization):** Görsel kalitesini koruyarak benzersiz renk sayısını tezgâhın iplik sayısına düşürme.
- **İplik Bobin (Creel) Tahsisi:** Dokuma tezgâhında hangi renk ipliklerin hangi oranlarda sarılacağını belirleyen üretim reçetesi.
- **Yüzey Alan Dağılımı:** Her baskın rengin halı desenindeki kapladığı piksel yüzdesi ($P_k = \frac{N_k}{N_{\text{total}}} \times 100$).
- **Rastgele Alt-Örnekleme (Random Downsampling):** Temsili renk dağılımını bozmadan kümeleme süresini saniyeler mertebesinde tutma.

---

## Libraries
- `scikit-learn`: `KMeans` kümeleme algoritması.
- `opencv-python` (`cv2`): `COLOR_BGR2RGB` renk dönüşümü.
- `numpy`: Piksel matrislerinin düzleştirilmesi (`reshape(-1, 3)`) ve `np.bincount`.
- `pydantic` (v2): `ColorCluster` ve `DominantPaletteResult` modelleri.
- `pytest`: Palet çıkarımı ve oran bütünlüğü birim testleri.

---

## Functions / Classes Studied
- `KMeansPaletteExtractor`, `ColorCluster`, `DominantPaletteResult`
- `KMeansPaletteExtractor.extract_palette()`
- `sklearn.cluster.KMeans.fit_predict()`, `KMeans.cluster_centers_`
- `np.bincount()`, `np.random.RandomState.choice()`

---

## Notebook
- **Dosya:** [`day11_kmeans_baskin_renk.ipynb`](day11_kmeans_baskin_renk.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Sentetik halı deseninden $K=3$ ve $K=8$ baskın renk kümelerini, yüzey alan pasta grafiklerini ve HEX paletlerini adım adım gösterir.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `kmeans-dominant-palette-extractor`
- **Modüller:**
  - `src/kmeans_palette_engine.py`: Hafif scikit-learn / Pydantic `KMeansPaletteExtractor`, `DominantPaletteResult` ve `ColorCluster` sınıfları.
  - `src/kmeans_palette.py`: K-Means baskın renk paleti çıkarıcı ve 15,000 piksellik uzamsal alt-örnekleme (`Subsampling`) hızlandırıcısı.
  - `src/quantizer.py`: `CarpetQuantizer` (deseni tezgâh ipliklerine indirgeyen indeksli kuantizasyon ve hata haritası simülatörü).
  - `src/yarn_matcher.py`: Merinos 16 ipliklik üretim kataloğu ile eşleştirme ve tezgâh cağlık planlama motoru (`YarnMatcher`).
  - `src/color_models.py`: Pydantic veri modelleri (`CatalogYarn`, `ExtractedColor`, `MatchGrade`, `CreelAllocationPlan`, `QuantizationReport`).
  - `src/ciede2000.py`: ISO/CIE 11664-6:2014 CIEDE2000 skaler, vektörize ve hata haritası hesaplayıcıları.
  - `src/generator.py`: Sentetik klasik madalyon, modern geometrik ve monokrom dokulu halı üretici.
  - `src/cli.py`: `extract`, `match`, `quantize`, `benchmark` komut satırı arayüzü.
  - `tests/test_kmeans_palette_engine.py`: Temel K-Means küme sayısı, HEX kodu ve yüzde toplamı testleri.
  - `tests/test_palette_and_quantizer.py`: 10 kapsamlı birim ve entegrasyon testi (Sharma standart test çiftleri, subsampling, kuantizasyon).

---

## Architecture
```
day11/
├── README.md
├── day11_kmeans_baskin_renk.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── palette_config.json
    ├── fixtures/
    │   └── synthetic_carpets/
    │       ├── carpet_oriental_classic.png
    │       ├── carpet_modern_geometric.png
    │       └── carpet_monochrome_textured.png
    ├── src/
    │   ├── __init__.py
    │   ├── color_models.py
    │   ├── ciede2000.py
    │   ├── kmeans_palette.py
    │   ├── kmeans_palette_engine.py
    │   ├── yarn_matcher.py
    │   ├── quantizer.py
    │   ├── generator.py
    │   └── cli.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_kmeans_palette_engine.py
    │   └── test_palette_and_quantizer.py
    └── outputs/
        ├── sample_palette_extraction.json
        ├── yarn_creel_allocation_report.json
        ├── ciede2000_benchmark.json
        └── palette_summary.md
```

---

## Experiments
1. **Baskın Renk Paleti Çıkarımı Deneyi:**
   - 4 farklı renk alanına sahip sentetik halı deseni üzerinde $K=4$ kümeleme çalıştırıldı.
   - Her bir kümenin HEX kodu (`#...`) ve yüzey kaplama oranı üretildi; oranların toplamının tam $\%100.0$ olduğu doğrulandı.
2. **K-Means Alt-Örnekleme (Subsampling) Hızlanma Deneyi:**
   - 512x512 piksellik halı görseli üzerinde 15,000 piksellik örneklem ile tam görsele kıyasla $10\times$ hızlanma elde edildi; centroid kaymasının $< 1.5 \Delta E_{00}$ toleransında kaldığı doğrulandı.
3. **Sharma et al. (2005) Standart Doğrulama Deneyi:**
   - CIEDE2000 formülasyonu Sharma et al. standart test çiftleri üzerinde test edildi ve sayısal sapmanın $< 10^{-3}$ olduğu doğrulandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_kmeans_palette_extraction`
  - `test_palette_extraction`
  - `test_ciede2000_identical_colors_zero`
  - `test_ciede2000_standard_sharma_pairs`
  - `test_ciede2000_blue_region_rotation_significance`
  - `test_ciede2000_achromatic_numerical_stability`
  - `test_kmeans_palette_extraction_proportions_sum_to_100`
  - `test_kmeans_palette_rgb_vs_lab_clustering`
  - `test_subsampling_acceleration_and_fidelity`
  - `test_carpet_quantization_and_distortion_metric`
  - `test_yarn_matching`
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Dijital halı desenlerinin jakarlı tezgah bobin kapasitesine uygun olarak $K$ adet ana renge kuantize edilmesi sağlanmıştır.
- Dokuma hazırlık departmanı için gerekli iplik tüketim yüzdeleri, cağlık bobin yerleşim planı ve $m^2$ başına tahmini iplik maliyeti otomatikleştirilmiştir.

---

## Limitations
- K-Means küme sayısı ($K$) kullanıcı tarafından tezgâh kapasitesine göre belirlenmektedir; dirsek yöntemi (elbow method) veya siluet skoru gibi otomatik $K$ belirleyiciler sonraki fazlarda değerlendirilecektir.
- Algoritma sentetik halı desenleri ve Merinos standart renk kataloğu üzerinden doğrulanmıştır.

---

## Files
- `day11/README.md`
- `day11/day11_kmeans_baskin_renk.ipynb`
- `day11/mini_project/README.md`
- `day11/mini_project/configs/palette_config.json`
- `day11/mini_project/fixtures/synthetic_carpets/`
- `day11/mini_project/src/__init__.py`
- `day11/mini_project/src/color_models.py`
- `day11/mini_project/src/ciede2000.py`
- `day11/mini_project/src/kmeans_palette.py`
- `day11/mini_project/src/kmeans_palette_engine.py`
- `day11/mini_project/src/yarn_matcher.py`
- `day11/mini_project/src/quantizer.py`
- `day11/mini_project/src/generator.py`
- `day11/mini_project/src/cli.py`
- `day11/mini_project/tests/__init__.py`
- `day11/mini_project/tests/test_kmeans_palette_engine.py`
- `day11/mini_project/tests/test_palette_and_quantizer.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day11/mini_project/tests/ -v

# Uçtan uca palet ve benchmark testini çalıştırma
python -m day11.mini_project.src.cli benchmark
```

---

## Next Day
- **Day 12:** Perspektif Düzeltme ve Homografi — Açısal çekim bozulmalarının düzeltilmesi, köşe tespiti ve $3 \times 3$ homografi matrisi ile kuşbakışı (top-down) projeksiyon.