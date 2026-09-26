# Day 15 — Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu

> **Aşama:** Faz 2 — Klasik Bilgisayarlı Görü ve Görüntü Analitiği (Day 09–15)  
> **Resmi Staj Defteri Konusu:** Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu (Yaprak 29 & 30)

## Goal
Bu günün amacı, Faz 2 boyunca geliştirilen tüm klasik bilgisayarlı görü ve görüntü analitiği modüllerini (Ön İşleme $\to$ Renk Uzayları $\to$ K-Means Kuantizasyonu $\to$ Homografi $\to$ Morfoloji/Kenar $\to$ Bölütleme) bir araya getirmektir. Halı yüzey görüntülerinden doku (Haralick GLCM öznitelikleri), renk momentleri (HSV uzayında ortalama ve standart sapma) ve geometrik şekil değişmezlerini (7 logaritmik Hu momenti) çıkararak 17 boyutlu sabit uzunluklu öznitelik vektöründe birleştiren (feature fusion) ve makine öğrenmesi modelleri için girdi hazırlayan `VisualFeatureIntegrator` boru hattını inşa etmektir.

---

## Engineer Research Assignment
- Farklı ölçek ve fiziksel anlamlara sahip görsel özniteliklerin (GLCM doku matrisleri, HSV renk dağılım istatistikleri ve logaritmik Hu şekil momentleri) tek bir özellik vektöründe birleştirilmesinde (Feature Fusion) boyutsal dengeyi sağlamak.
- Gri Seviye Eşoluşum Matrisi (GLCM) hesaplama karmaşıklığını azaltmak için gri tonlamalı pikselleri 32 seviyeye ($// 8$) kuantize ederek Haralick doku metriklerini (kontrast, benzeşmezlik, homojenlik, enerji) gerçek zamanlı hızda çıkarmak.
- 7 Hu momentinin ($\phi_1 - \phi_7$) halı motiflerinin dönme (rotation), ölçek (scale) ve öteleme (translation) değişimlerinden bağımsız kalan değişmezlik (invariance) kuralını formüle etmek.
- `VisualFeatureIntegrator` ile uçtan uca 17 boyutlu öznitelik çıkarımını birim testlerle doğrulamak.

---

## Concepts
- **Öznitelik Füzyonu (Feature Fusion):** Farklı görsel alanlardan (doku, renk, şekil) elde edilen bilgilerin tek bir temsil vektöründe birleştirilmesi.
- **Gri Seviye Eşoluşum Matrisi (GLCM):** Belirli mesafe ($d=1$) ve açıda ($\theta=0^\circ$) yan yana gelen gri piksel ikililerinin ortak olasılık dağılımı.
- **Haralick Doku Metrikleri:**
  - Kontrast: $\sum_{i,j} |i-j|^2 p(i,j)$
  - Benzeşmezlik: $\sum_{i,j} |i-j| p(i,j)$
  - Homojenlik: $\sum_{i,j} \frac{p(i,j)}{1 + (i-j)^2}$
  - Enerji (ASM): $\sum_{i,j} p(i,j)^2$
- **Renk Momentleri (Color Moments):** HSV kanallarının birinci ($\mu$) ve ikinci ($\sigma$) merkezi momentleri.
- **Hu Değişmez Momentleri:** Merkezcil momentlerden türetilen, görüntü rotasyonundan ve ölçeğinden etkilenmeyen 7 logaritmik skalar.

---

## Libraries
- `scikit-image` (`skimage.feature`): `graycomatrix()`, `graycoprops()`.
- `opencv-python` (`cv2`): `moments()`, `HuMoments()`, `cvtColor()`.
- `numpy`: Sayısal tensörler ve vektör birleştirme (`concatenate`).
- `pydantic` (v2): `IntegratedFeatureVector` şeması.
- `pytest`: Öznitelik boyutu ve füzyon doğruluğu testleri.

---

## Functions / Classes Studied
- `VisualFeatureIntegrator`, `IntegratedFeatureVector`
- `VisualFeatureIntegrator.fuse_features()`, `VisualFeatureIntegrator.extract_glcm_texture()`, `VisualFeatureIntegrator.extract_color_moments()`, `VisualFeatureIntegrator.extract_hu_moments()`
- `graycomatrix()`, `graycoprops()`, `cv2.HuMoments()`
- `MerinosIndustrialVisionToolkit`, `CarpetInspectionPipeline`

---

## Notebook
- **Dosya:** [`day15_gorsel_ozellik_entegrasyonu.ipynb`](day15_gorsel_ozellik_entegrasyonu.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Doku, renk ve şekil özelliklerinin çıkarılmasını, radar grafiğiyle görselleştirilmesini ve 17 boyutlu vektörün oluşumunu adım adım sunar.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `visual-feature-integrator`
- **Modüller:**
  - `src/feature_integrator.py`: `VisualFeatureIntegrator` ve `IntegratedFeatureVector` sınıfları.
  - `src/toolkit.py`: Faz 2 görüntü işleme araç seti.
  - `src/inspect_pipeline.py`: Uçtan uca muayene boru hattı.
  - `src/benchmark_suite.py`: Modül başarım kıyaslama motoru.
  - `tests/test_feature_integrator.py`: Öznitelik füzyon boyutu (17D) testleri.
  - `tests/test_vision_toolkit.py`: Araç seti entegrasyon testleri.

---

## Architecture
```
day15/
├── README.md
├── day15_gorsel_ozellik_entegrasyonu.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── feature_integrator.py
    │   ├── toolkit.py
    │   ├── inspect_pipeline.py
    │   ├── benchmark_suite.py
    │   └── models.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_feature_integrator.py
    │   └── test_vision_toolkit.py
    └── outputs/
```

---

## Experiments
1. **Görsel Öznitelik Füzyonu Deneyi:**
   - $100 \times 100 \times 3$ sentetik halı görüntüsü üzerinde füzyon çalıştırıldı.
   - 4 doku özniteliği (GLCM), 6 renk momenti (HSV ortalama/std) ve 7 Hu momenti çıkarıldı.
   - Toplam öznitelik vektörü boyutunun tam 17 olduğu ve `total_dimension == 17` sağlandığı doğrulandı.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_visual_feature_fusion`
  - `test_vision_toolkit_*` (araç seti ve boru hattı testleri)
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Faz 2 Klasik Bilgisayarlı Görü zinciri başarıyla tamamlanmış ve konsolide edilmiştir.
- Çıkarılan 17 boyutlu öznitelik vektörleri, Faz 3 (Day 16–21) Makine Öğrenmesi ve Derin Öğrenme sınıflandırıcıları için doğrudan hazır hale getirilmiştir.

---

## Limitations
- Bu aşamadaki öznitelikler kural tabanlı klasik mühendislik öznitelikleridir; derin öğrenme öznitelik çıkarımı (ResNet, CNN ve ViT embeddingleri) Faz 3 ve Faz 4'te ele alınacaktır.
- Testler sentetik halı dokusu üzerinde icra edilmiştir.

---

## Files
- `day15/README.md`
- `day15/day15_gorsel_ozellik_entegrasyonu.ipynb`
- `day15/mini_project/README.md`
- `day15/mini_project/src/__init__.py`
- `day15/mini_project/src/feature_integrator.py`
- `day15/mini_project/tests/__init__.py`
- `day15/mini_project/tests/test_feature_integrator.py`
- `day15/mini_project/tests/test_vision_toolkit.py`

---

## How to Run
```bash
# Birim testleri koşma
pytest day15/mini_project/tests/ -v
```

---

## Next Day
- **Day 16:** Derin Öğrenmeye Giriş: PyTorch Tensörleri ve Otomatik Gradyan — Tensor API, GPU hızlandırma ve autograd mekanizması.