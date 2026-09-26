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
  - `src/kmeans_palette_engine.py`: `KMeansPaletteExtractor`, `DominantPaletteResult` ve `ColorCluster` sınıfları.
  - `src/morphology_engine.py`, `src/defect_detector.py`: Destekleyici morfolojik kusur analiz modülleri.
  - `tests/test_kmeans_palette_engine.py`: Küme sayısı, yüzdelik toplamı ve HEX format testleri.
  - `tests/test_morphology_defects.py`: Morfolojik analiz testleri.

---

## Architecture
```
day11/
├── README.md
├── day11_kmeans_baskin_renk.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── kmeans_palette_engine.py
    │   ├── morphology_engine.py
    │   ├── defect_detector.py
    │   ├── models.py
    │   └── generator.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_kmeans_palette_engine.py
    │   └── test_morphology_defects.py
    └── outputs/
```

---

## Experiments
1. **Baskın Renk Paleti Çıkarımı Deneyi:**
   - Mavi, yeşil ve kırmızı bölgelerden oluşan sentetik halı deseni üzerinde $K=3$ kümeleme çalıştırıldı.
   - 3 adet küme merkezi tespit edildi; her bir kümenin HEX kodu (`#...`) üretildi.
   - Dağılım yüzdelerinin toplamının $\approx \%100.0$ olduğu doğrulandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_kmeans_palette_extraction`
  - `test_morphology_defects_*` (destekleyici morfoloji testleri)
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Dijital halı desenlerinin jakarlı tezgah bobin kapasitesine uygun olarak $K$ adet ana renge kuantize edilmesi sağlanmıştır.
- Dokuma hazırlık departmanı için gerekli iplik tüketim yüzdeleri ve renk reçetesi otomatikleştirilmiştir.

---

## Limitations
- K-Means küme sayısı ($K$) kullanıcı tarafından tezgâh kapasitesine göre belirlenmektedir; dirsek yöntemi (elbow method) veya siluet skoru gibi otomatik $K$ belirleyiciler sonraki fazlarda değerlendirilecektir.
- Algoritma sentetik halı desenleri üzerinde test edilmiştir.

---

## Files
- `day11/README.md`
- `day11/day11_kmeans_baskin_renk.ipynb`
- `day11/mini_project/README.md`
- `day11/mini_project/src/__init__.py`
- `day11/mini_project/src/kmeans_palette_engine.py`
- `day11/mini_project/tests/__init__.py`
- `day11/mini_project/tests/test_kmeans_palette_engine.py`
- `day11/mini_project/tests/test_morphology_defects.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day11/mini_project/tests/ -v
```

---

## Next Day
- **Day 12:** Perspektif Düzeltme ve Homografi — Açısal çekim bozulmalarının düzeltilmesi, köşe tespiti ve $3 \times 3$ homografi matrisi ile kuşbakışı (top-down) projeksiyon.