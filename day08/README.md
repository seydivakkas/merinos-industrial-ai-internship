# Day 08 — Keşifsel Veri Analizi (EDA): Dağılım, Aykırı Değer ve Korelasyon Analizi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Keşifsel Veri Analizi (EDA): Dağılım, Aykırı Değer ve Korelasyon Analizi (Yaprak 15 & 16)

## Goal
Bu günün amacı, makine öğrenmesi model eğitimine geçmeden önce dokuma tezgâhı telemetrileri ve halı ürün parametrelerinin istatistiksel dağılımlarını (ortalama, medyan, standart sapma, çeyrekler), değişkenler arasındaki korelasyon ilişkilerini ve sensör arızalarından kaynaklanan ekstrem aykırı değerleri (outliers) Çeyrekler Arası Açıklık (IQR) yöntemiyle inceleyen otomatik bir Keşifsel Veri Analizi motoru (`EDAToolkit`) inşa etmektir. Faz 1'in son günü olarak ham veriden modelleme aşamasına giden analitik köprü kurulmuştur.

---

## Engineer Research Assignment
- Tekstil üretim süreçlerinde simetrik olmayan çarpık (skewed) dağılımlarda ortalama yerine medyanın; standart sapma yerine Çeyrekler Arası Açıklığın ($IQR$) merkezi eğilim ve yayılım ölçüsü olarak kullanılmasının önemini araştırmak.
- Tukey'in aykırı değer sınır formülü olan $[Q_1 - 1.5 \cdot IQR, \; Q_3 + 1.5 \cdot IQR]$ mekanizmasının ekstrem sensör sıçramalarını ve veri tabanı hatalarını tespitteki etkinliğini formüle etmek.
- Çok boyutlu üretim değişkenleri arasında Pearson korelasyon matrisi çıkararak, birbiriyle yüksek korelasyon ($|r| > 0.85$) gösteren ve çoklu doğrusal bağlantı (multicollinearity) riski taşıyan öznitelikleri belirlemek.
- `EDAToolkit` ile tüm nümerik kolonların istatistiksel özetini ve en yüksek ilişkili öznitelik çiftlerini tek bir yapısal nesnede (`EDAReport`) toplamak.

---

## Concepts
- **Betimsel İstatistikler (Descriptive Statistics):** Ortalama ($\mu$), medyan ($Q_2$), standart sapma ($\sigma$) ve kartiller ($Q_1, Q_3$).
- **Aykırı Değer Tespiti (IQR Method):**
  $$IQR = Q_3 - Q_1$$
  $$\text{Alt Sınır} = Q_1 - 1.5 \cdot IQR, \quad \text{Üst Sınır} = Q_3 + 1.5 \cdot IQR$$
- **Korelasyon Matrisi (Pearson $r$):** İki değişken arasındaki doğrusal ilişki katsayısı:
  $$r_{xy} = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Çoklu Doğrusal Bağlantı (Multicollinearity):** İki veya daha fazla özniteliğin neredeyse aynı bilgiyi taşıması ve katsayı kararsızlığına yol açması.

---

## Libraries
- `pandas`: Tabular veri işleme, çeyrek hesapları ve korelasyon matrisi çıkarma.
- `numpy`: Sayısal vektörel işlemler ve NaN maskeleme.
- `pydantic` (v2): İstatistiksel özet (`ColumnSummary`) ve rapor (`EDAReport`) veri modelleri.
- `matplotlib`: Histogram ve kutu grafiği (boxplot) görselleştirme.
- `pytest`: EDA analitik motoru birim testleri.

---

## Functions / Classes Studied
- `EDAToolkit`, `EDAReport`, `ColumnSummary`
- `EDAToolkit.analyze()`
- `pd.Series.quantile()`, `pd.DataFrame.corr()`, `pd.DataFrame.select_dtypes()`

---

## Notebook
- **Dosya:** [`day08_kesifsel_veri_analizi.ipynb`](day08_kesifsel_veri_analizi.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Halı üretim parametrelerinin betimsel analizini, IQR aykırı değer tespitini ve korelasyon ısı haritasını adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `exploratory-data-analysis-toolkit`
- **Modüller:**
  - `src/eda_toolkit.py`: `EDAToolkit`, `EDAReport` ve `ColumnSummary` sınıfları.
  - `src/analyzer.py`, `src/color_models.py`, `src/conversions.py`, `src/delta_e.py`: Destekleyici analitik ve renk eşikleme modülleri.
  - `tests/test_eda_toolkit.py`: İstatistiksel özet, IQR ve korelasyon birim testleri.
  - `tests/test_color_analysis.py`: Renk uzayı ve kalite derecelendirme testleri.

---

## Architecture
```
day08/
├── README.md
├── day08_kesifsel_veri_analizi.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── eda_toolkit.py
    │   ├── analyzer.py
    │   ├── color_models.py
    │   ├── conversions.py
    │   ├── delta_e.py
    │   └── thresholding.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_eda_toolkit.py
    │   └── test_color_analysis.py
    └── outputs/
```

---

## Experiments
1. **İstatistiksel Özet ve IQR Aykırı Değer Deneyi:**
   - 10 satırlık sentetik telemetri verisinde bilerek eklenen aşırı sıcaklık (180.0°C) aykırı değeri $1.5 \times IQR$ kuralı ile tam 1 adet olarak tespit edildi.
   - Sütunun medyanı, kartilleri ve uç sınırları doğru olarak hesaplandı.
2. **Korelasyon Analizi:**
   - Tezgâh hızı (RPM) ile dokuma gerginliği arasındaki güçlü doğrusal ilişki ($|r| > 0.90$) `top_correlated_pairs` listesinde 1. sıraya yerleşti.
3. **Sayısal Olmayan Veri Hatası:**
   - Sayısal kolon içermeyen DataFrame verildiğinde `EDAToolkit` sınıfının `ValueError` fırlattığı doğrulandı.

---

## Validation
- Pytest ile 12 adet birim test icra edildi:
  - `test_eda_toolkit_summary_and_iqr_outliers`
  - `test_eda_toolkit_empty_raises_value_error`
  - `test_color_analysis_*` (destekleyici analitik testleri)
- Tüm testler **%100 başarıyla (12 passed)** geçti.

---

## Results
- Faz 1'in veri ve geliştirme temelleri başarıyla tamamlanmış; verinin dağılımı, sınırları ve kalitesi güvenceye alınmıştır.
- Bir sonraki Faz 2 (Day 09–15) Bilgisayarlı Görü Zinciri için temiz, analiz edilmiş ve doğrulanmış veri altyapısı hazırdır.

---

## Limitations
- Doğrusal olmayan (non-linear) karmaşık ilişkiler için mutual information (karşılıklı bilgi) metriği bu aşamada yer almamış; doğrusal Pearson matrisi kullanılmıştır.
- Tüm testler sentetik tekstil parametreleriyle gerçekleştirilmiştir.

---

## Files
- `day08/README.md`
- `day08/day08_kesifsel_veri_analizi.ipynb`
- `day08/mini_project/README.md`
- `day08/mini_project/src/__init__.py`
- `day08/mini_project/src/eda_toolkit.py`
- `day08/mini_project/tests/__init__.py`
- `day08/mini_project/tests/test_eda_toolkit.py`
- `day08/mini_project/tests/test_color_analysis.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day08/mini_project/tests/ -v
```

---

## Next Day
- **Day 09:** OpenCV ile Görüntü İşleme Temelleri — BGR-RGB kanal yapısı, görüntü okuma/yazma, en-boy oranını koruyarak yeniden boyutlandırma ve temel filtreleme.