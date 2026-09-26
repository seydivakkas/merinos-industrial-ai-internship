# Day 08 — Keşifsel Veri Analizi (EDA): Dağılım, Aykırı Değer ve Korelasyon Analizi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Keşifsel Veri Analizi (EDA): Dağılım, Aykırı Değer ve Korelasyon Analizi (Yaprak 15 & 16)

---

## Goal
Bu günün amacı, makine öğrenmesi model eğitimine geçmeden önce dokuma tezgâhı telemetrileri ve halı ürün parametrelerinin istatistiksel dağılımlarını (ortalama, medyan, standart sapma, çeyrekler, çarpıklık ve basıklık), değişkenler arasındaki korelasyon ilişkilerini ve sensör arızalarından kaynaklanan ekstrem aykırı değerleri (outliers) Çeyrekler Arası Açıklık (IQR) ve Z-Score yöntemleriyle inceleyen otomatik bir Keşifsel Veri Analizi motoru (`EDAToolkit`) inşa etmektir. Faz 1'in son günü olarak ham veriden modelleme aşamasına giden analitik köprü kurulmuştur.

---

## Engineer Research Assignment
- Tekstil üretim süreçlerinde simetrik olmayan çarpık (skewed) dağılımlarda ortalama yerine medyanın; standart sapma yerine Çeyrekler Arası Açıklığın ($IQR$) merkezi eğilim ve yayılım ölçüsü olarak kullanılmasının önemini araştırmak.
- Tukey'in aykırı değer sınır formülü olan $[Q_1 - 1.5 \cdot IQR, \; Q_3 + 1.5 \cdot IQR]$ ve $Z > 3.0$ mekanizmalarının ekstrem sensör sıçramalarını ve veri tabanı hatalarını tespitteki etkinliğini formüle etmek.
- Çok boyutlu üretim değişkenleri arasında Pearson korelasyon matrisi çıkararak, birbiriyle yüksek korelasyon ($|r| > 0.85$) gösteren ve çoklu doğrusal bağlantı (multicollinearity) riski taşıyan öznitelikleri belirlemek.
- `EDAToolkit` ile tüm nümerik kolonların istatistiksel özetini (`ColumnSummary`), histogram frekanslarını ve kutu grafiği metriklerini (`BoxplotSummary`) tek bir yapısal nesnede (`EDAReport`) toplamak.

---

## Concepts
- **Betimsel İstatistikler (Descriptive Statistics):** Ortalama ($\mu$), medyan ($Q_2$), standart sapma ($\sigma$), çeyrekler ($Q_1, Q_3$), çarpıklık (skewness) ve basıklık (kurtosis).
- **Aykırı Değer Tespiti (Outlier Detection):**
  - **IQR Yöntemi:** $IQR = Q_3 - Q_1$, $\text{Alt Sınır} = Q_1 - 1.5 \cdot IQR$, $\text{Üst Sınır} = Q_3 + 1.5 \cdot IQR$
  - **Z-Score Yöntemi:** $Z = |x - \mu| / \sigma > 3.0$
- **Korelasyon Matrisi (Pearson $r$):** İki değişken arasındaki doğrusal ilişki katsayısı:
  $$r_{xy} = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Kutu Grafiği (Boxplot) İstatistiği:** Beş sayılı özet (Min, Q25, Medyan, Q75, Max) ve Tukey bıyık (whisker) sınırları.

---

## Libraries
- `pandas`: Tabular veri işleme, çeyrek hesapları ve korelasyon matrisi çıkarma.
- `numpy`: Sayısal vektörel işlemler, histogram hesapları ve NaN maskeleme.
- `pydantic` (v2): İstatistiksel özet (`ColumnSummary`), kutu grafiği (`BoxplotSummary`) ve rapor (`EDAReport`) veri modelleri.
- `pytest`: EDA analitik motoru birim testleri.

---

## Functions / Classes Studied
- `EDAToolkit`, `EDAReport`, `ColumnSummary`, `BoxplotSummary`
- `EDAToolkit.analyze()`, `EDAToolkit.compute_histogram()`, `EDAToolkit.compute_boxplot_stats()`
- `pd.Series.quantile()`, `pd.DataFrame.corr()`, `pd.DataFrame.select_dtypes()`, `np.histogram()`

---

## Notebook
- **Dosya:** [`day08_kesifsel_veri_analizi.ipynb`](day08_kesifsel_veri_analizi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Halı üretim parametrelerinin betimsel analizini, IQR aykırı değer tespitini ve korelasyon ısı haritasını adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `exploratory-data-analysis-toolkit`
- **Modüller:**
  - `src/eda_toolkit.py`: `EDAToolkit`, `EDAReport`, `ColumnSummary` ve `BoxplotSummary` sınıfları.
  - `src/generator.py`: Sentetik veri üreteci.
  - `tests/test_eda_toolkit.py`: İstatistiksel özet, IQR/Z-score aykırı değer, korelasyon, histogram ve kutu grafiği testleri.

> *Not:* Renk modelleri, renk uzayı dönüşümleri ve Delta-E renk farkı analitiği (`color_models.py`, `conversions.py`, `delta_e.py`, `thresholding.py`, `test_color_analysis.py`), müfredat uyumu doğrultusunda **Day 10 (Renk Uzayları ve Renk Farkı Analizi)** projesine aktarılmıştır.

---

## Architecture
```
day08/
├── README.md
├── day08_kesifsel_veri_analizi.ipynb
└── mini_project/
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── eda_toolkit.py
    │   └── generator.py
    └── tests/
        ├── __init__.py
        └── test_eda_toolkit.py
```

---

## Experiments
1. **Aykırı Değer Tespiti Deneyi:**
   - 135°C olarak enjekte edilen ekstrem sıcaklık anomalisi hem IQR hem de Z-score kurallarıyla başarıyla yakalandı (`outlier_count_iqr: 1`).
2. **Korelasyon Analizi:**
   - Sıcaklık ile tezgâh devri (RPM) arasındaki $r > 0.85$ doğrusal bağıntı en yüksek korelasyonlu çift olarak otomatik sıralandı.
3. **Histogram ve Kutu Grafiği İstatistikleri:**
   - 10 aralıklı frekans dağılımı ve çeyrek bıyık sınırları analitik olarak doğrulandı.

---

## Validation
- Pytest ile 4 adet birim test icra edildi:
  - `test_eda_toolkit_analysis`
  - `test_eda_histogram_computation`
  - `test_eda_boxplot_stats`
  - `test_eda_toolkit_error_on_non_numeric`
- Tüm testler **%100 başarıyla (4 passed)** geçti.

---

## Results
- Üretim veri setlerindeki çarpıklıklar, aykırı değerler ve çoklu doğrusal bağlantılar modellere girmeden önce tespit edildi.
- Tüm veriler sentetik test senaryolarından oluşmaktadır.

---

## Limitations
- Çok değişkenli (multivariate) aykırı değer tespiti (Isolation Forest veya Mahalanobis uzaklığı) Faz 2 makine öğrenmesi aşamalarında ele alınacaktır.

---

## Files
- `day08/README.md`
- `day08/day08_kesifsel_veri_analizi.ipynb`
- `day08/mini_project/README.md`
- `day08/mini_project/src/__init__.py`
- `day08/mini_project/src/eda_toolkit.py`
- `day08/mini_project/src/generator.py`
- `day08/mini_project/tests/test_eda_toolkit.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day08/mini_project/tests/ -v
```

---

## Next Day
- **Day 09:** OpenCV Temelleri — Görüntü I/O, renk uzayı dönüşümleri, filtreleme, boyutlandırma ve histogram eşitleme.