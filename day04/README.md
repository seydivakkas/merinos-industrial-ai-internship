# Day 04 — Python Geliştirme Ortamı ve Veri Sözleşmesi

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)
> **Resmi Staj Defteri Konusu:** Python Geliştirme Ortamı ve Veri Sözleşmesi (Yaprak 7 & 8)
> **Müfredat Hizalama Durumu:** Bu klasörün mevcut uygulama içeriği yeni müfredatla ayrıca hizalanmalıdır.

[![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)](file:///C:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg?style=flat-square)](https://www.python.org/)
[![Pandas 2.x](https://img.shields.io/badge/pandas-2.x-150458.svg?style=flat-square)](https://pandas.pydata.org/)
[![Tests](https://img.shields.io/badge/tests-10%20passed-brightgreen.svg?style=flat-square)](file:///C:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/day04/mini_project/tests/test_quality_validation.py)

---

## 1. Başlık ve Üstveri
Bu modül, Merinos fabrikasyon ortamındaki halı üretim logları, sensör telemetrisi ve ürün katalog verilerinin otomatik olarak istatistiksel profillenmesini, deklaratif kalite kuralları (Expectation Suites) ile şema/değer/dağılım düzeyinde doğrulanmasını, anomali içeren kayıtların izole edilmesini ve zengin bir interaktif HTML veri kalitesi paneli (`data_quality_dashboard.html`) üretilmesini ele alır.

## 2. Günün Hedefi ve Kapsamı
- **Temel Hedef:** Geleneksel doğrulamaların ötesine geçerek; parti (batch) seviyesinde eksiklik oranları, mükerrer kayıtlar, fiziksel tolerans aralıkları, regex desenleri ve dağılım kaymalarını (statistical drift) tespit eden kurumsal bir veri gözlemlenebilirlik (Data Observability) hattı inşa etmek.
- **Kapsam:**
  - Great Expectations mimarisinden esinlenen modüler ve genişletilebilir kural motoru (`BaseExpectation`).
  - Satır sayısı, boşluk (nullity), tekillik (uniqueness), aralık (range), küme üyeliği (set membership), regex deseni ve ortalama kayması (drift) kural primitifleri.
  - JSON tabanlı deklaratif paket derleyicisi (`ExpectationSuite`) ve doğrulayıcı (`SuiteValidator`).
  - Otomatik tablo ve sütun profilleme motoru (`AutomatedDataProfiler`).
  - Sıfır dış CDN bağımlılığıyla çalışan koyu temalı interaktif HTML gösterge paneli.
  - Anomali satırlarını downstream modellerden koruyan izolasyon hattı (`anomalous_records.csv`).

## 3. Mühendislik Araştırma Görevi
Endüstriyel üretim hatlarında veri kalitesi yalnız tekil satır doğrulamasıyla sınırlı değildir:
- Bir dokuma tezgâhında mekanik tansiyon gevşemesi yaşandığında tekil halı hav yükseklikleri bireysel sınırları (örneğin 5-25 mm) ihlal etmeyebilir; ancak partinin ortalaması 11 mm'den 18 mm'ye fırlayabilir. Bu durum parti bazında binlerce metrekarelik ürünün kalite standardından sapmasına ve iplik israfına neden olur.
- Benzer biçimde ağ gecikmeleri veya tezgâh yeniden başlatmaları nedeniyle mükerrer kayıtlar oluşabilir.

Bu nedenle araştırmamız:
- Hem şema ve değer doğrulamalarını hem de istatistiksel ortalama sapmalarını (Data Drift) eşzamanlı denetleyen deklaratif bir **Expectation Engine** ve **Data Profiling Pipeline** geliştirmeye odaklanmıştır.

## 4. Teorik ve Kavramsal Altyapı
### İstatistiksel Metrikler ve Kalite Skoru Formülleri
1. **Hücre Bazlı Eksiklik Oranı (Missingness Rate, $\mathcal{M}$):**
   $$\mathcal{M} = \frac{1}{N \cdot P} \sum_{i=1}^N \sum_{j=1}^P \mathbb{I}(x_{ij} = \text{null})$$
2. **Mükerrerlik Oranı (Duplication Rate, $\mathcal{D}$):**
   $$\mathcal{D} = \frac{N_{\text{duplicate}}}{N}$$
3. **Süreç Ortalaması ve Dağılım Kayması (Statistical Drift):**
   $$\bar{\mu} = \frac{1}{n} \sum_{i=1}^n x_i \quad \implies \quad \text{İhlal:} \quad \bar{\mu} \notin [\mu_{\min}, \mu_{\max}]$$
4. **Bileşik Veri Kalite Skoru (Composite Data Quality Score, $Q$):**
   $$Q = S_{\text{expectations}} \times (1 - \mathcal{M}) \times (1 - \mathcal{D})$$
   Burada $S_{\text{expectations}} \in [0, 100]$ kuralların başarı yüzdesidir.

## 5. Kullanılan Kütüphaneler ve Seçim Gerekçeleri
- **Pandas (2.x):** Vektörize doğrulama, hızlı filtreleme, boolean maskeleme ve istatistiksel özetleme işlemleri için kullanıldı.
- **NumPy (1.26+ / 2.x):** Sayısal hesaplamalar, skewness ve quantile kestirimleri için kullanıldı.
- **pytest (9.0.3):** Kural primitifleri, suite derleyicisi, anomali tespiti ve uçtan uca boru hattı senaryolarını test etmek için kullanıldı.

## 6. Temel Fonksiyonlar ve Sınıflar
- `BaseExpectation`: Tüm kural primitiflerinin türediği soyut temel sınıf.
- `ExpectTableRowCountToBeBetween`: Satır sayısının beklenen batch sınırlarında olduğunu denetler.
- `ExpectColumnValuesToNotBeNull`: Sütundaki eksik değerleri tespit eder, `mostly` toleransı destekler.
- `ExpectColumnValuesToBeUnique`: Birincil anahtarların (`product_id`) tekilliğini garantiler.
- `ExpectColumnValuesToBeBetween`: Halı eni, boyu ve hav yüksekliğinin fiziksel toleranslarını doğrular.
- `ExpectColumnValuesToBeInSet`: Malzeme ve koleksiyonların katalog kümesinde olduğunu denetler.
- `ExpectColumnValuesToMatchRegex`: Ürün kodu (`^MRP-[0-9]{4}$`) ve hex renk formatını doğrular.
- `ExpectColumnMeanToBeBetween`: Sayısal sütun ortalamasını denetleyerek kalibrasyon driftini yakalar.
- `ExpectationSuite` & `SuiteValidator`: JSON kural dosyasını yükler, değerlendirir ve `ValidationResult` çıktısı üretir.
- `AutomatedDataProfiler`: Veri kümesinin bellek, eksiklik, teklik ve dağılım profilini çıkarır; tek dosyalık HTML paneli üretir.
- `DataQualityPipeline`: Veri yükleme, profilleme, doğrulama, anomali izolasyonu ve artefakt üretimini koordine eder.

## 7. Notebook İncelemesi
`day04_data_quality_and_profiling.ipynb` 10 standart bölümden oluşur:
1. Problem Tanımı: Endüstriyel Veri Hatlarında Kalite ve Şema Sapması (Data Drift & Schema Drift)
2. Neden Önemli? (Endüstriyel Etki & Model Güvenliği)
3. Matematiksel & İstatistiksel Temeller (Eksiklik, Mükerrerlik ve Z-Score Formülleri)
4. Kütüphane & Mimari İncelemesi (Great Expectations vs Pandera vs Custom Declarative Engine)
5. Minimal Çalışır Kod (Expectation Suite Tanımlama ve DataFrame Doğrulama)
6. Deneyler & Parametre Analizi (Referans, Anomali Enjeksiyonu ve Drift Kıyaslaması)
7. Görselleştirme: Veri Kalite & Profil Dağılımı (KDE Dağılım Grafikleri ve Kalite Skoru Karşılaştırması)
8. Doğrulama ve Testler (İhlal Detaylarının Raporlanması)
9. Hata Durumları, Edge Cases ve Drift Tespiti
10. Mühendislik Çıkarımları & Day 05'e Bağlantı

## 8. Mini Proje Mimarisi ve Kod Açıklaması
Mini proje `day04/mini_project/` dizini altında yapılandırılmıştır:
- `configs/expectation_suite_config.json`: 15 deklaratif kural içeren fabrika şartname paketi.
- `fixtures/`:
  - `clean_production_data.csv`: %100 geçerli 20 referans kayıt.
  - `dirty_production_data.csv`: Null, duplicate, sınır dışı boyut ve yasak malzeme içeren anomali seti.
  - `drifted_production_data.csv`: Hav yüksekliği ortalaması 18.5 mm'ye kaymış tezgâh drift seti.
- `src/expectations.py`: Vektörize Pandas operasyonları kullanan 7 kural sınıfı.
- `src/suite.py`: Konfigürasyon derleyicisi ve doğrulama yürütücüsü.
- `src/profiler.py`: Sayısal/kategorik profil çıkarıcı ve modern CSS HTML paneli motoru.
- `src/pipeline.py`: Uçtan uca ETL doğrulama orkestratörü.
- `tests/test_quality_validation.py`: 10 birim ve entegrasyon testi.

## 9. Sistem Mimarisi ve Veri Akışı Diyagramı

```mermaid
flowchart TD
    A["Girdi Veri Seti (CSV / JSON)"] --> B["DataQualityPipeline"]
    C["expectation_suite_config.json"] --> D["ExpectationSuite Derleyicisi"]
    B --> E["AutomatedDataProfiler"]
    E --> F["data_profile.json"]
    B --> G["SuiteValidator (Vektörize Kural Denetimi)"]
    D --> G
    G --> H{"Tüm Kurallar Geçti mi?"}
    H -->|Evet (%100)| I["Onaylı Veri Akışı"]
    H -->|Hayır (İhlaller Var)| J["anomalous_records.csv (İzole Havuz)"]
    G --> K["validation_report.json"]
    E --> L["data_quality_dashboard.html (Görsel Panel)"]
    G --> L
```

## 10. Deneyler, Parametreler ve Karşılaştırmalar
Notebook ve boru hattı üzerinde 3 farklı üretim senaryosu kıyaslanmıştır:

| Senaryo | Toplam Satır | Anomalili Satır | Kural Başarımı | Bileşik Skor ($Q$) | Karar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Temiz Referans Veri** | 20 | 0 | %100.0 | %100.0 | **ONAYLANDI** |
| **2. Anomali Enjeksiyonu** | 20 | 14 | %26.7 | %23.2 | **REDDEDİLDİ** |
| **3. Tezgâh Tansiyon Drifti** | 20 | 0 (Satır bazlı) | %93.3 | %93.3 | **REDDEDİLDİ (Drift)** |

## 11. Doğrulama, Testler ve Kalite Metrikleri
10 kapsamlı birim test yazılmış ve tamamı geçmiştir:
```bash
python -m pytest day04/mini_project/tests/ -v
```
Test kapsamı:
- `test_expect_column_values_to_not_be_null`: Null içermeyen ve içeren durumlarda doğruluk.
- `test_expect_column_values_to_be_unique`: Tekil ve mükerrer ID ayrımı.
- `test_expect_column_values_to_be_between`: Min/max fiziksel sınır aşımı testleri.
- `test_expect_column_values_to_be_in_set`: Malzeme ve koleksiyon kümesi kontrolü.
- `test_expect_column_values_to_match_regex`: Ürün kodu ve hex renk regex denetimi.
- `test_expect_column_mean_to_be_between_and_drift_detection`: Tezgâh tansiyon kayması tespiti.
- `test_expect_table_row_count_to_be_between`: Minimum ve maksimum satır sayısı denetimi.
- `test_expectation_suite_from_json_and_validate_clean`: Temiz veride %100 başarı.
- `test_expectation_suite_detects_dirty_anomalies`: Anomali verisinde ihlallerin eksiksiz yakalanması.
- `test_data_profiler_and_pipeline_artifacts`: Tüm çıktı artefaktlarının (JSON, CSV, HTML) doğrulanması.

## 12. Çıktılar ve Sonuçlar
- `day04/mini_project/outputs/validation_report.json`: Kural kural başarı durumları ve hata dökümü (8.7 KB).
- `day04/mini_project/outputs/data_profile.json`: İstatistiksel sütun metrikleri ve bellek analizi (6.7 KB).
- `day04/mini_project/outputs/data_quality_dashboard.html`: Tek dosyalık koyu temalı interaktif HTML gösterge paneli (22.1 KB).
- `day04/mini_project/outputs/anomalous_records.csv`: Kurallara takılan izole edilmiş kayıtlar.

## 13. Karşılaşılan Zorluklar, Limitler ve Çözümler
- **Zorluk:** Tekil satır düzeyinde sınırları (5-25 mm) aşmayan ancak partinin tamamında hav yüksekliğinin şişmesine neden olan tezgâh gergi arızalarının yakalanamaması.
- **Çözüm:** `ExpectColumnMeanToBeBetween` kuralı eklenerek parti ortalamasının [8.0, 15.0] mm aralığında kalması zorunlu hale getirildi ve drift anında yakalandı.
- **Zorluk:** Eksik sütun varlığında `KeyError` ile boru hattının çökmesi.
- **Çözüm:** Her kural sınıfında `if self.column not in df.columns` kontrolü eklenerek zarif hata raporlaması sağlandı.

## 14. Dosya Ağacı ve Dizin Yapısı
```bash
day04/
├── README.md
├── day04_data_quality_and_profiling.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── expectation_suite_config.json
    ├── fixtures/
    │   ├── clean_production_data.csv
    │   ├── dirty_production_data.csv
    │   └── drifted_production_data.csv
    ├── src/
    │   ├── __init__.py
    │   ├── expectations.py
    │   ├── suite.py
    │   ├── profiler.py
    │   └── pipeline.py
    ├── tests/
    │   ├── __init__.py
    │   └── test_quality_validation.py
    └── outputs/
        ├── validation_report.json
        ├── data_profile.json
        ├── data_quality_dashboard.html
        └── anomalous_records.csv
```

## 15. Nasıl Çalıştırılır?
```bash
# 1. Testleri çalıştırma:
python -m pytest day04/mini_project/tests/ -v

# 2. Kalite boru hattını ve gösterge panelini çalıştırma:
python -m day04.mini_project.src.pipeline
```

## 16. Bir Sonraki Güne Bağlantı
Day 05 — Pandas, Veri Hattı ve Veri Kalitesi), bu temizlenen ve doğrulanan endüstriyel sayısal veriler ve piksel matrisleri üzerinde Python döngüleri yerine NumPy C-hızında vektörizasyon, broadcasting, bellek düzeni (C vs Fortran order) ve tensör performans kıyaslamaları gerçekleştirilecektir.

## 17. AI Coding Agent Prompt Şablonu
```markdown
Day 04 bağlamında veri kalitesi doğrulama ve profilleme hattı geliştirmek için:
"Merinos halı fabrikası için Great Expectations tasarım desenine uygun;
eksik veri (nullity), tekillik (uniqueness), fiziksel aralık (between), küme üyeliği (set),
regex formatı ve dağılım kaymasını (column mean) denetleyen deklaratif bir ExpectationSuite,
otomatik istatistiksel DataProfiler, interaktif HTML gösterge paneli ve pytest test takımı oluştur."
```