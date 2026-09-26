# Day 15 — Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu (Yaprak 29 & 30)

## Goal
Bu günün amacı, Faz 2 boyunca geliştirilen tüm klasik bilgisayarlı görü ve görüntü analitiği modüllerini (Ön İşleme $\to$ Renk Uzayları $\to$ K-Means Kuantizasyonu $\to$ Homografi $\to$ Morfoloji/Kenar $\to$ Bölütleme $\to$ Öznitelik Çıkarımı) tek ve tutarlı bir endüstriyel kalite muayene boru hattında bir araya getirmektir. Halı yüzey görüntülerinden doku (Haralick GLCM öznitelikleri), renk momentleri ve 3D HSV histogramları, yerel anahtar nokta tanımlayıcıları (ORB ve SIFT) ile geometrik şekil değişmezlerini (7 logaritmik Hu momenti) çıkararak çok modlu öznitelik füzyonu (feature fusion) sağlayan, k-NN desen sınıflandırıcı ve görsel katalog arama motoru sunan ve 6 aşamalı muayene karar motorunu (`CarpetInspectionPipeline`, `MerinosIndustrialVisionToolkit`) hayata geçirmektir.

---

## Engineer Research Assignment
- Farklı ölçek ve fiziksel anlamlara sahip görsel özniteliklerin (GLCM doku matrisleri, HSV renk dağılım istatistikleri, yerel ORB/SIFT anahtar noktaları ve logaritmik Hu şekil momentleri) tek bir özellik vektöründe birleştirilmesinde (Feature Fusion) L2 normalizasyonu ve boyutsal dengeyi sağlamak.
- Gri Seviye Eşoluşum Matrisi (GLCM) hesaplama karmaşıklığını azaltmak için gri tonlamalı pikselleri 32 seviyeye ($// 8$) kuantize ederek Haralick doku metriklerini (kontrast, benzeşmezlik, homojenlik, enerji) gerçek zamanlı hızda çıkarmak.
- ORB ikili tanımlayıcıları (Hamming mesafesi) ile SIFT gradyan tanımlayıcılarını (Öklid mesafesi + Lowe ratio testi + RANSAC homografi) dönüşüm ve ölçek değişmezliği açısından kıyaslamak.
- 6 aşamalı üretim kalite muayene boru hattında (Rektifikasyon $\to$ Renk Eşleme $\to$ Morfoloji $\to$ Bordür Paralelliği $\to$ Motif Bölütleme $\to$ Öznitelik Sınıflandırma) otomatik `ACCEPT`, `WARNING`, `REJECT` kararı üreten HUD overlay sistemini doğrulamak.

---

## Concepts
- **Öznitelik Füzyonu (Feature Fusion):** Çok modlu görsel özniteliklerin (doku, renk, yerel köşe, şekil) birleştirilerek L2 normalize edilmiş sabit boyutlu vektöre dönüştürülmesi.
- **Haralick Doku Analizi (GLCM):** Kontrast, Benzeşmezlik, Homojenlik, Enerji (ASM) ve Korelasyon metrikleri.
- **Yerel Anahtar Noktalar:**
  - **ORB (Oriented FAST and Rotated BRIEF):** Hızlı, ikili (binary) 256-bit tanımlayıcı, canlı hat için ideal ($> 80 \text{ FPS}$).
  - **SIFT (Scale-Invariant Feature Transform):** 128 boyutlu skalar gradyan vektörü, ölçek ve rotasyon değişmezliği yüksek ($~ 15\text{--}25 \text{ FPS}$).
- **Görsel Benzerlik Araması (Content-Based Image Retrieval - CBIR):** Katalogdaki referans modellerle sorgu görseli arasındaki Kosinüs benzerliği üzerinden en yakın Top-K halıyı listeleme.
- **Uçtan Uca Endüstriyel Muayene Boru Hattı:** Rektifikasyon, renk toleransı, morfolojik kusur, bordür paralelliği, motif örtüşümü ve desen türünü içeren 6 aşamalı fabrika kabul sistemi.

---

## Libraries
- `scikit-image` (`skimage.feature`): `graycomatrix()`, `graycoprops()`.
- `opencv-python` (`cv2`): `ORB_create()`, `SIFT_create()`, `BFMatcher()`, `HuMoments()`, `calcHist()`.
- `numpy`: Sayısal tensörler, L2 normalizasyon ve kosinüs benzerliği.
- `pydantic` (v2): `MasterInspectionReport`, `ReleaseManifest`, `CarpetFeatureVector`, `PatternMatchResult`.
- `pytest`: 21 adet kapsamlı birim ve entegrasyon testi.

---

## Functions / Classes Studied
- `VisualFeatureIntegrator`, `IntegratedFeatureVector`
- `CarpetPatternClassifierAndMatcher`, `KeypointFeatureEngine`, `GLCMFeatureEngine`, `ColorHistogramEngine`
- `MerinosIndustrialVisionToolkit`, `CarpetInspectionPipeline`, `Phase2BenchmarkSuite`
- `MasterInspectionReport`, `ReleaseManifest`, `Phase2ModuleBenchmark`

---

## Notebook
- **Dosya:** [`day15_gorsel_ozellik_entegrasyonu.ipynb`](day15_gorsel_ozellik_entegrasyonu.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Doku, renk ve şekil özelliklerinin çıkarılmasını, radar grafiğiyle görselleştirilmesini ve 17 boyutlu vektörün oluşumunu adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `visual-feature-integrator`
- **Modüller:**
  - `src/feature_integrator.py`: 17D GLCM + Renk Momentleri + Hu Momentleri füzyon motoru.
  - `src/keypoint_engine.py`: ORB ve SIFT anahtar nokta çıkarıcı ve eşleştirici.
  - `src/glcm_engine.py`: GLCM Haralick doku analiz motoru.
  - `src/color_histogram.py`: 3D HSV normalize renk histogramı motoru.
  - `src/feature_fusion.py`: Çok modlu öznitelik füzyonu ve desen sınıflandırıcı.
  - `src/toolkit.py`: Faz 2 tüm günleri (Day 07–15) kapsayan birleşik araç seti.
  - `src/inspect_pipeline.py`: 6 aşamalı endüstriyel kalite muayene boru hattı ve HUD çizici.
  - `src/benchmark_suite.py`: 8 modülün başarımını ölçen benchmark motoru ve manifest derleyici.
  - `src/models.py`: Pydantic veri modelleri ve kalite güvence sınıfları.

---

## Architecture
```
day15/
├── README.md
├── day15_gorsel_ozellik_entegrasyonu.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   ├── feature_config.json
    │   └── toolkit_config.json
    ├── fixtures/
    │   ├── benchmark_manifest.json
    │   ├── defective_carpet.png
    │   ├── faded_carpet.png
    │   ├── perfect_carpet.png
    │   ├── skewed_carpet.png
    │   └── patterns/
    │       ├── carpet_class_medallion_classic.png
    │       ├── carpet_class_geometric_modern.png
    │       ├── carpet_class_floral_traditional.png
    │       └── carpet_class_vintage_distressed.png
    ├── src/
    │   ├── __init__.py
    │   ├── benchmark_suite.py
    │   ├── cli.py
    │   ├── color_histogram.py
    │   ├── feature_benchmark.py
    │   ├── feature_cli.py
    │   ├── feature_fusion.py
    │   ├── feature_integrator.py
    │   ├── generator.py
    │   ├── glcm_engine.py
    │   ├── inspect_pipeline.py
    │   ├── keypoint_engine.py
    │   ├── models.py
    │   ├── pattern_generator.py
    │   ├── pattern_models.py
    │   └── toolkit.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_feature_integrator.py
    │   ├── test_features.py
    │   └── test_vision_toolkit.py
    └── outputs/
```

---

## Experiments
1. **17D Görsel Öznitelik Füzyonu Deneyi:**
   - 4 doku özniteliği (GLCM), 6 renk momenti (HSV) ve 7 Hu momenti çıkarılarak `total_dimension == 17` doğrulandı.
2. **ORB ve SIFT Tanımlayıcı Kıyaslaması:**
   - Sentetik halı desenlerinde ORB 32 bayt ikili tanımlayıcı, SIFT 128 boyutlu skalar tanımlayıcı başarıyla çıkardı ve rotasyon/ölçek altında kararlılık sergiledi.
3. **Desen Sınıflandırma ve Katalogda Top-K Arama:**
   - 4 farklı Merinos desen sınıfı (Madalyon, Geometrik, Çiçekli, Vintage) birleştirilmiş öznitelik vektörleri üzerinden k-NN ve kosinüs benzerliği ile %100 başarıyla sınıflandırıldı.
4. **Endüstriyel Muayene Boru Hattı ve HUD Overlay:**
   - Temiz halı için `ACCEPT`, fiziksel dokuma kusurları içeren halı için `REJECT` kararı üretildi; 6 aşamalı görsel HUD overlay oluşturuldu.
5. **Faz 2 Master Benchmark Manifesti:**
   - 8 modülün tamamı başarıyla profillendi ve `ReleaseManifest` (v2.0.0, 8 modül, HEALTHY) olarak kaydedildi.

---

## Validation
- Pytest ile 21 adet birim test icra edildi:
  - `test_feature_integrator.py` (1 test: 17D füzyon)
  - `test_features.py` (10 test: ORB, SIFT, GLCM, Histogram, Füzyon, Sınıflandırma, Top-K Arama)
  - `test_vision_toolkit.py` (10 test: Güvenli G/Ç, Fikstürler, Filtreleme, Renk, Kusur, Bordür, Segmentasyon, Çoklu Mod, Muayene Hattı, Master Benchmark)
- Tüm testler **%100 başarıyla (21 passed)** geçti.

---

## Results
- Faz 2 Klasik Bilgisayarlı Görü zinciri (Day 09–15) başarıyla tamamlanmış, modüller arası arayüzler konsolide edilmiş ve üretime hazır hale getirilmiştir.
- Çıkarılan öznitelik vektörleri, Faz 3 (Day 16–21) Derin Öğrenme ve Yapay Zeka modelleri için referans zemin oluşturmuştur.

---

## Limitations
- Bu aşamadaki öznitelikler kural tabanlı klasik mühendislik öznitelikleridir; derin öğrenme öznitelik çıkarımı (ResNet, CNN ve ViT embeddingleri) Faz 3 ve Faz 4'te ele alınacaktır.
- Testler yerel sentetik prototip fikstürler üzerinde icra edilmiştir; canlı fabrika kamerası bağlı değildir.

---

## Files
- `day15/README.md`
- `day15/day15_gorsel_ozellik_entegrasyonu.ipynb`
- `day15/mini_project/README.md`
- `day15/mini_project/configs/feature_config.json`
- `day15/mini_project/configs/toolkit_config.json`
- `day15/mini_project/src/__init__.py`
- `day15/mini_project/src/benchmark_suite.py`
- `day15/mini_project/src/cli.py`
- `day15/mini_project/src/color_histogram.py`
- `day15/mini_project/src/feature_benchmark.py`
- `day15/mini_project/src/feature_cli.py`
- `day15/mini_project/src/feature_fusion.py`
- `day15/mini_project/src/feature_integrator.py`
- `day15/mini_project/src/generator.py`
- `day15/mini_project/src/glcm_engine.py`
- `day15/mini_project/src/inspect_pipeline.py`
- `day15/mini_project/src/keypoint_engine.py`
- `day15/mini_project/src/models.py`
- `day15/mini_project/src/toolkit.py`
- `day15/mini_project/tests/test_feature_integrator.py`
- `day15/mini_project/tests/test_features.py`
- `day15/mini_project/tests/test_vision_toolkit.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day15/mini_project/tests/ -v

# Uçtan uca halı muayenesi çalıştırma
python -m day15.mini_project.src.cli inspect --image day15/mini_project/fixtures/perfect_carpet.png

# Phase 2 master benchmark suite çalıştırma
python -m day15.mini_project.src.cli benchmark
```

---

## Next Day
- **Day 16:** Derin Öğrenmeye Giriş: PyTorch Tensörleri ve Otomatik Gradyan — Tensor API, GPU hızlandırma ve autograd mekanizması.

---

## AI Coding Agent Prompt
"Day 15 Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu mini projesini çalıştırın, 21 birim testi doğrulayın ve standalone jupyter notebook'u hatasız koşun."