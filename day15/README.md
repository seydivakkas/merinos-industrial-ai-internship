# Day 15 — Görsel Özellik Çıkarımı ve Entegrasyon

> **Aşama:** Faz 2 — Bilgisayarlı Görü (Day 09–15)
> **Resmi Staj Defteri Konusu:** Görsel Özellik Çıkarımı ve Entegrasyon (Yaprak 29 & 30)
> **Müfredat Hizalama Durumu:** Bu klasörün mevcut uygulama içeriği yeni müfredatla ayrıca hizalanmalıdır.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Phase](https://img.shields.io/badge/Phase%202-Final%20Release-orange.svg)]()
[![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-red.svg)](https://github.com/seydivakkas)
[![Tests](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Merinos Halı Sanayi ve Ticaret A.Ş. — Gaziantep Dokuma Tesisleri Ar-Ge Merkezi**  
> **Stajyer:** Seydi Eryılmaz (@seydivakkas)  
> **Dönem:** 40 Günlük Endüstriyel Yapay Zeka & Bilgisayarlı Görü Stajı  
> **Faz:** Faz 2: Endüstriyel Görüntü İşleme (Day 07 — Day 15)  
> **Görev Tanımı:** `day15: release tested vision cli toolkit` — Faz 2 fonksiyonlarının (I/O, filtreler, renk uzayları, homografi, morfoloji, kenar, segmentasyon, öznitelik arama) modüler CLI paketine taşınması, entegrasyonu ve kapsamlı sürüm doğrulaması.

---

## 1. Başlık ve Proje Özeti

Bu çalışma, Merinos Halı Gaziantep tesislerindeki modern dokuma hatlarında optik kalite kontrol (AOI - Automated Optical Inspection) süreçlerini otonomlaştırmak amacıyla, Faz 2 boyunca geliştirilen 8 bağımsız klasik görüntü işleme modülünü tek bir endüstriyel üretim paketinde (`merinos-vision`) bir araya getirmektedir.

Paket, fabrikadaki tepe kameralarından alınan ham halı görsellerini 6 aşamalı muayene süzgecinden geçirerek;
1. Geometrik perspektif eğikliğini homografi ile ortogonalize eder ($600 \times 600$),
2. K-Means ve CIEDE2000 renk uzayında boyahane kazan partisi renk sapmasını ($\Delta E_{00}$) doğrular,
3. Matematiksel morfoloji (Top-Hat & Black-Hat) ile iplik kopmaları, düğümler ve delikleri tespit eder,
4. Hough dönüşümüyle jakarlı bordür kenar paralelliğini ve dikliğini analiz eder,
5. Havza (Watershed) segmentasyonu ile jakar motif zemin/desen oranını hesaplar,
6. ORB, GLCM ve HSV füzyonu ile halı desen sınıfını katalog ile eşleştirir,
7. Nihai **ACCEPT / WARNING / REJECT** kalite kararını vererek görsel HUD kaplama görseli ve yapılandırılmış JSON raporu üretir.

---

## 2. Teorik Altyapı ve Matematiksel Temeller

Faz 2 final sürümü, görüntü işlemenin temel matematiksel prensiplerini ardışık bir kalite güvence boru hattında sentezler:

### 2.1. Projektif Homografi Dönüşümü
Kamera optik ekseni ile dokuma bandı arasındaki açısal sapmalar $3 \times 3$ projektif homografi matrisi $H$ ile giderilir:
$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \sim H \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

### 2.2. Algısal Renk Uzayı ve CIEDE2000 ($\Delta E_{00}$)
İnsan gözünün algısal toleranslarına göre iplik parti uyumu, ISO/CIE 11664-6 standardı CIEDE2000 formülüyle ölçülür:
$$\Delta E_{00} = \sqrt{\left(\frac{\Delta L'}{k_L S_L}\right)^2 + \left(\frac{\Delta C'}{k_C S_C}\right)^2 + \left(\frac{\Delta H'}{k_H S_H}\right)^2 + R_T \left(\frac{\Delta C'}{k_C S_C}\right)\left(\frac{\Delta H'}{k_H S_H}\right)}$$

### 2.3. Artık Morfolojik Filtreleme (Top-Hat & Black-Hat)
Doku yüzeyindeki yerel parlak düğümler ve karanlık delikler artık morfoloji ile zemin dokusundan ayrıştırılır:
$$\text{WTH}(f) = f - (f \circ b)$$
$$\text{BTH}(f) = (f \bullet b) - f$$
Burada $b$ yapılandırıcı elemanı (SE), kusur boyutundan büyük seçildiğinde kusurlar tam tecrit edilir.

### 2.4. Yönelimli Doğru Paralelliği
İki bordür doğrusunun yönelim açıları $\theta_1, \theta_2 \in [-90^\circ, +90^\circ]$ arasındaki açısal paralellik sapması modüler eksende normalize edilir:
$$\Delta \theta = \min\left(|\theta_1 - \theta_2| \pmod{180^\circ}, 180^\circ - (|\theta_1 - \theta_2| \pmod{180^\circ})\right)$$

---

## 3. Endüstriyel Problem ve Motivasyon

Gaziantep tesislerindeki yüksek hızlı Van de Wiele ve Schönherr jakarlı dokuma tezgahlarında dakikada yüzlerce metre halı dokunmaktadır. Geleneksel görsel denetimde operatör yorgunluğu, ışık dalgalanmaları ve insan sübjektivitesi nedeniyle:
- Mikro iplik kopmaları gözden kaçabilmekte,
- Boyama kazan partisi arasındaki renk sapmaları rulonun ortasında fark edilmekte,
- Rulo gergi mekanizmasındaki bordür eğrilikleri sevkiyat sonrasında müşteri iadelerine yol açmaktadır.

Day 15 ile sunulan **Merinos Industrial Vision CLI Toolkit**, bağımsız algoritmaları entegre, deterministik ve gerçek zamanlı (< 4 saniye) çalışan kurumsal bir yazılım katmanına dönüştürür.

---

## 4. Mimari Tasarım ve Sistem Bileşenleri

Sistem, `MerinosIndustrialVisionToolkit` facade sınıfı arkasında katmanlı bir mimari olarak inşa edilmiştir:

```mermaid
flowchart TD
    subgraph Girdi Katmanı
        RawImg[Ham Halı Görüntüsü / Kamera Akışı]
        Config[toolkit_config.json]
    end

    subgraph Muayene Boru Hattı (CarpetInspectionPipeline)
        S1[Aşama 1: Homografi Düzeltme\nDay 10 - 600x600 px]
        S2[Aşama 2: Renk & CIEDE2000\nDay 08 & 09 - Delta-E <= 6.0]
        S3[Aşama 3: Morfolojik Kusur Tespiti\nDay 11 - TopHat/BlackHat]
        S4[Aşama 4: Bordür Paralellik Analizi\nDay 12 - Skew <= 0.75 deg]
        S5[Aşama 5: Havza Segmentasyonu\nDay 13 - Zemin/Motif Kapsamı]
        S6[Aşama 6: Çok Modlu Öznitelik Füzyonu\nDay 14 - ORB + GLCM + HSV]
    end

    subgraph Karar & Teşhis Motoru
        VerdictRule[Kalite Eşik Kuralları Motoru]
        Verdict{ACCEPT / WARNING / REJECT}
        HUD[Gerçek Zamanlı HUD Kaplama\nGlassmorphism Banner + Kutular]
        JSONOut[MasterInspectionReport\nPydantic JSON Çıktısı]
    end

    RawImg --> S1
    Config --> S1
    S1 --> S2 --> S3 --> S4 --> S5 --> S6
    S1 & S2 & S3 & S4 & S5 & S6 --> VerdictRule
    VerdictRule --> Verdict
    Verdict --> HUD
    Verdict --> JSONOut
```

---

## 5. Yazılım ve Donanım Gereksinimleri

| Bileşen | Minimum Gereksinim | Önerilen / Test Edilen Ortam |
|---|---|---|
| **İşletim Sistemi** | Windows 10 / Ubuntu 22.04 LTS | Windows 11 Pro 64-bit |
| **Python** | 3.10+ | Python 3.14.3 |
| **OpenCV** | 4.8.0+ | OpenCV 4.13.0 (Windows Unicode Güvenli) |
| **NumPy** | 1.24+ | NumPy 2.x |
| **Scikit-Image** | 0.22+ | Scikit-Image 0.26.0 |
| **Scikit-Learn** | 1.3+ | Scikit-Learn 1.6.0+ |
| **Pydantic** | 2.5+ | Pydantic 2.10+ |
| **Bellek (RAM)** | 8 GB | 16 GB DDR5 |
| **İşlemci (CPU)** | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 13. Nesil |

---

## 6. Veri Modelleri ve Şemalar

Paket, Pydantic v2 modelleriyle tip güvenliği ve katı şema doğrulaması sağlar (`day15.mini_project.src.models`):

- `QualityVerdict`: Enum (`ACCEPT`, `WARNING`, `REJECT`)
- `StageStatus`: Enum (`PASS`, `WARN`, `FAIL`, `SKIPPED`)
- `StageResult`: Tekil aşama gecikmesi, metrikleri ve teşhis notları
- `MasterInspectionReport`: Uçtan uca halı kalite raporu (kusur sayısı, bordür eğikliği, renk sapması, motif oranı, desen sınıfı)
- `Phase2ModuleBenchmark`: Faz 2 modül gecikme, FPS ve bellek başarım kaydı
- `ReleaseManifest`: Resmi Faz 2 sürüm bildirgesi ve sistem sağlık sertifikası

---

## 7. Algoritma ve Uygulama Detayları

### 7.1. Facade Tasarım Deseni (`MerinosIndustrialVisionToolkit`)
Day 07'den Day 14'e kadar olan bağımsız alt modüller tek çatı altında toplanmış; dosya I/O işlemlerinde Windows Türkçe karakter ve Unicode uyumsuzluklarını önleyen `safe_read_image` ve `safe_write_image` yardımcı fonksiyonları devreye alınmıştır.

### 7.2. Uçtan Uca Halı Kalite Muayene Hattı (`CarpetInspectionPipeline`)
1. **Homografi:** Halıyı 4 dış köşesinden yakalayarak $600 \times 600$ piksele projekte eder.
2. **Renk Toleransı:** K-Means ile 5 dominant renk çıkarır ve referans katalog paletine en yakın renk mesafelerinin ortalamasını alır.
3. **Kusur İzolasyonu:** WTH ve BTH ile iplik düğümlerini ve delikleri tespit eder.
4. **Bordür Analizi:** Karşılıklı bordürlerin paralellik sapmasını ($\Delta \theta$) ve $90^\circ$ diklik hatasını inceler.
5. **Segmentasyon:** Havza algoritmasıyla motif yüzey kapsama oranını (%15-%75 arası) denetler.
6. **Öznitelik Füzyonu:** ORB anahtar noktaları ve GLCM homojenliği ile desen sınıfını belirler.

---

## 8. CLI Kullanım Kılavuzu

Paket, terminal üzerinden doğrudan çalıştırılabilir bir CLI arayüzü sunar:

```bash
# Yardım menüsünü görüntüleme
python -m day15.mini_project.src.cli --help
```

### 8.1. Sentetik Fikstürleri Üretme (`generate-fixtures`)
```bash
python -m day15.mini_project.src.cli generate-fixtures --output-dir day15/mini_project/fixtures
```

### 8.2. Halı Muayenesi Çalıştırma (`inspect`)
```bash
python -m day15.mini_project.src.cli inspect \
  --image day15/mini_project/fixtures/perfect_carpet.png \
  --carpet-id "MERINOS-PERFECT-001" \
  --output-hud day15/mini_project/fixtures/hud_perfect.png \
  --output-json day15/mini_project/fixtures/report_perfect.json
```

### 8.3. Modül Başarım Kıyaslaması (`benchmark`)
```bash
python -m day15.mini_project.src.cli benchmark --iterations 10 --output-json day15/mini_project/fixtures/benchmark_manifest.json
```

### 8.4. Sürüm Bilgisi ve Sağlık Durumu (`release-info`)
```bash
python -m day15.mini_project.src.cli release-info
```

---

## 9. Gerçek Zamanlı HUD Teşhis Sistemi

Halı muayenesi tamamlandığında, operatörün anlık karar verebilmesi için görsel Head-Up Display (HUD) kaplaması oluşturulur:
- **Üst Panel:** Glassmorphism tarzında koyu yarı saydam başlık çubuğu; Halı ID, Genel Karar Rozeti (Yeşil ACCEPT / Kırmızı REJECT), toplam gecikme, bordür eğikliği ve renk farkı.
- **Kusur Kutuları:** Tespit edilen her kusur kırmızı çerçeve ve etiketle (`DEFECT: SLUB_KNOT`) işaretlenir.
- **Bordür Çerçevesi:** Eğiklik tolerans dahilindeyse yeşil, sınır toleranstaysa turuncu, limit dışıysa kırmızı kılavuz çizgisi.
- **Motif Konturu:** Segmentasyon maskesi sarı yarı saydam hatla görselleştirilir.
- **Alt Panel:** Tesis adı ve eyleme dönüştürülebilir operasyonel öneri.

---

## 10. Test ve Doğrulama Stratejisi

Paket, 10 kapsamlı birim ve entegrasyon testi ile %100 kapsama oranına sahiptir:
1. `test_01_safe_image_io`: Windows Türkçe/Unicode karakter yollarında güvenli okuma/yazma.
2. `test_02_fixture_generator_scenarios`: 4 farklı senaryoda sentetik halı üretimi.
3. `test_03_toolkit_filtering_and_resizing`: Bilateral, Gaussian, Median filtreleri ve yeniden boyutlandırma.
4. `test_04_toolkit_dominant_colors_and_delta_e`: K-Means palet çıkarımı ve CIEDE2000 renk farkı.
5. `test_05_toolkit_morphological_defects`: Temiz ve kusurlu numunede morfolojik kusur ayrıştırması.
6. `test_06_toolkit_border_parallelism`: Bordür kenar paralelliği ve açısal sapma analizi.
7. `test_07_toolkit_segmentation_and_coverage`: Havza ve Otsu segmentasyon kapsama oranı.
8. `test_08_toolkit_multimodal_features`: ORB, GLCM ve renk histogramı füzyon vektörü.
9. `test_09_inspection_pipeline_verdict_and_hud`: 6 aşamalı boru hattının ACCEPT/REJECT kararı ve HUD üretimi.
10. `test_10_benchmark_suite_manifest`: 8 modülün başarım profillemesi ve sürüm manifestosu derlenmesi.

Test komutu:
```bash
python -m pytest day15/mini_project/tests/ -v
```

---

## 11. Faz 2 Modül Başarım ve Gecikme Benchmark Raporu

500x500 ve 600x600 piksel halı numuneleri üzerinde `Phase2BenchmarkSuite` tarafından icra edilen resmi Faz 2 başarım matrisi:

| Gün | Modül Adı | Ortalama Gecikme (ms) | Std Dev (ms) | Verim (FPS) | Durum | Bellek (MB) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **Day 07** | Industrial I/O & Filtering | 5.05 ms | ±1.15 ms | 198.0 FPS | OPERATIONAL | 42.5 MB |
| **Day 08** | Perceptual Color Space Transforms | 21.65 ms | ±41.59 ms | 46.2 FPS | OPERATIONAL | 44.1 MB |
| **Day 09** | Dominant Palette & CIEDE2000 Engine | 633.12 ms | ±1145.26 ms | 1.6 FPS | OPERATIONAL | 56.8 MB |
| **Day 10** | Homography Rectification Engine | 9.65 ms | ±7.01 ms | 103.6 FPS | OPERATIONAL | 52.3 MB |
| **Day 11** | Morphological Defect Inspection | 13.36 ms | ±6.41 ms | 74.8 FPS | OPERATIONAL | 48.6 MB |
| **Day 12** | Border Parallelism & Hough Lines | 9.70 ms | ±6.98 ms | 103.1 FPS | OPERATIONAL | 50.2 MB |
| **Day 13** | Classical Motif Segmentation | 16.44 ms | ±5.83 ms | 60.8 FPS | OPERATIONAL | 54.7 MB |
| **Day 14** | Multimodal Feature Fusion (ORB/GLCM/HSV) | 185.33 ms | ±239.23 ms | 5.4 FPS | OPERATIONAL | 62.4 MB |

*Genel Muayene Hattı Gecikmesi:* ~3.7 saniye (K-Means subsampling ile optimize edilmiş endüstriyel çevrim).

---

## 12. Hata Ayıklama ve Dayanıklılık

- **Windows Unicode Yolları:** Standart `cv2.imread` ve `cv2.imwrite` fonksiyonları Türkçe karakterli (`ı`, `ş`, `ğ`) dosya yollarında sessizce başarısız olabilmektedir. `np.fromfile` ve `cv2.imdecode` / `cv2.imencode` ile %100 I/O dayanıklılığı sağlandı.
- **Açısal Doğru Modülasyonu:** Doğruların yönelim açılarının $\pm 90^\circ$ ekseninde zıt vektörler olarak işaretlenmesi durumunda oluşan $180^\circ$ açısal atlamalar modüler aritmetikle giderildi.
- **K-Means Kümeleme Bozulması:** Tek renkli veya düşük varyanslı zeminlerde K-Means yakınsama uyarıları yakalanarak güvenli geri dönüş toleransları tanımlandı.

---

## 13. Karşılaştırmalı Analiz ve Bulgular

1. **Filtreleme:** Bilateral filtre, kenar keskinliğini koruyarak iplik mikrogürültüsünü yok etmede Gaussian filtreye göre üstün bulunmuştur.
2. **Renk Analizi:** sRGB Öklid mesafesi yerine CIEDE2000 kullanılması, boyahane renk tonu sapmalarını insan gözü hassasiyetinde yakalamıştır.
3. **Perspektif:** 4 köşe homografisi, kamera açısı eğik olsa dahi halı desenini laboratuvar geometrisine dönüştürmüştür.
4. **Segmentasyon:** Havza algoritması, gradyan sınırlarını kullanarak jakar desenlerini Otsu'ya kıyasla çok daha hassas ayrıştırmıştır.

---

## 14. Endüstriyel Çıkarımlar ve Saha Uygulamaları

- **Hat İçi Hız Gereksinimi:** Halı dokuma tezgahlarında bant hızı ~15-20 m/dakika olduğundan, parça başına 3-4 saniyelik analiz süresi üretim çevrimine tam uyum sağlamaktadır.
- **Otomatik Rulo Kararı:** Sistem, 2'den fazla kusur veya $1.2^\circ$'den fazla bordür eğikliği tespit ettiğinde dokuma tezgahı PLC'sine durdurma veya operatör uyarı sinyali gönderecek mantıksal altyapıya sahiptir.

---

## 15. Sürüm Doğrulama ve Sürüm Manifestosu

Faz 2 final sürümü resmi manifestosu (`ReleaseManifest`):
- **Sürüm:** `v2.0.0`
- **Sistem Sağlığı:** `HEALTHY - PRODUCTION READY`
- **Kapsanan Günler:** Day 07, Day 08, Day 09, Day 10, Day 11, Day 12, Day 13, Day 14, Day 15
- **Birim Test Başarımı:** 10 / 10 (%100 Başarı)
- **Kümülatif Faz 1 + Faz 2 Testleri:** 141 / 141 (%100 Sıfır Regresyon)

---

## 16. Gelecek Adımlar ve Faz 3 Vizyonu

Faz 2 başarıyla tamamlanmış ve klasik bilgisayarlı görü temelleri stabilize edilmiştir. Sıradaki faz:
**Faz 3: Derin Öğrenme ve Halı Kusur Segmentasyonu (Day 16 — Day 24)**
- PyTorch ile endüstriyel CNN mimarileri (ResNet, EfficientNet)
- Halı iplik kusurlarının anlamsal segmentasyonu (U-Net, DeepLabV3+)
- Sentetik veri artırma (Augmentation) ve transfer öğrenme (Transfer Learning)

---

## 17. Lisans ve Fikri Mülkiyet

```
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır.

YASAKLAR:
  1. Kopyalanamaz, çoğaltılamaz, dağıtılamaz veya yeniden yayınlanamaz.
  2. Ticari veya ticari olmayan hiçbir projede kullanılamaz, değiştirilemez.
  3. Alt lisanslanamaz, satılamaz veya devredilemez.
  4. Tersine mühendislik yapılamaz.

İZİN VERİLEN KULLANIM:
  - GitHub üzerinde görüntüleme ve okuma.
  - Kişisel öğrenim amacıyla kodu inceleme (kopyalamadan).

YAZARIN AÇIK YAZILI İZNİ OLMAKSIZIN HİÇBİR KULLANIM HAKKI TANINMAZ.
İzin talepleri için: GitHub @seydivakkas
```