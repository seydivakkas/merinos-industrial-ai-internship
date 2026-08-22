# Merinos Mini-Proje: Üretilen Halı Görsellerinin Çok Boyutlu Analizi
## Staj Defteri Yaprak 57 ve 58 Müfredatı

Bu mini-proje, **Merinos Halı Sanayi ve Ticaret A.Ş. (Gaziantep 4. OSB)** tesislerinde Day 28'de SDXL difüzyon modeliyle üretilen sentetik desenlerin görsel beğeni yerine nesnel mühendislik metrikleriyle incelenmesi amacıyla geliştirilmiş çok boyutlu analiz platformudur.

---

## 🏛️ Mimari ve Bileşenler

1. **`color_analyzer.py` (`ColorPaletteAnalyzer` - Yaprak 57):**
   - **K-Means Renk Kümeleme:** Görseldeki milyonlarca pikseli 3B RGB uzayında $K=5$ kümeye ayırarak baskın merkez renkleri ve kapsama yüzdelerini (%) çıkarır.
   - **CIELAB Dönüşümü:** RGB koordinatlarını standart CIE D65 referanslı CIELAB ($L^*, a^*, b^*$) uzayına dönüştürür.
   - **$\Delta E^*$ ve CIEDE2000 Mesafesi:** Merinos kurumsal iplik bobin paletleriyle (`merinos_target_palettes.json`) algısal renk sapmasını ölçer.

2. **`symmetry_analyzer.py` (`StructuralSymmetryAnalyzer` - Yaprak 57):**
   - **Yatay (Bilateral) Ayna Simetrisi:** Sol-sağ yansıma ($I_{\text{fliplr}}$) ile orijinal görüntü arasındaki Pearson korelasyon katsayısını hesaplar.
   - **Dikey Ayna Simetrisi:** Üst-alt yansıma ($I_{\text{flipud}}$) ile korelasyonu hesaplar.
   - **4-Çeyrek Saray Halısı Simetrisi:** Merkez madalyon ve köşe bordür intizamını ölçer.
   - **Otokorelasyon Tabanlı Tekrar Düzeni:** 2D uzamsal kaydırmalı korelasyon ile periyodik motif ritmini sayısallaştırır.

3. **`seam_analyzer.py` (`SeamContinuityAnalyzer` - Yaprak 58):**
   - **Kenar ve Dikiş Sürekliliği (Tileability):** Sol-sağ ve üst-alt kenar şeritlerinin (8 piksel) piksel MSE farkını ölçer.
   - **Sobel Kenar Gradyan Sıçraması:** Dikiş hatlarında ani renk ve motif kopukluklarını denetler.

4. **`embedding_retriever.py` (`CNNEmbeddingRetriever` - Yaprak 58):**
   - **Pretrained CNN Omurgası (ResNet18):** 512 boyutlu $L_2$-normalize latent görsel öznitelik vektörü çıkarır.
   - **Cosine Similarity:** Referans halı kataloğu (`reference_carpet_catalog.json`) ile açısal benzerliği hesaplar.
   - **Top-K Sıralaması:** En çok benzeyen ilk $K$ referans deseni listeler.

5. **`master_analyzer.py` (`MasterCarpetAnalyzer`):**
   - 4 analizörü tek bir akışta birleştirir ve `ComprehensiveVisualReport` nesnesi üretir.

6. **`visualizer.py` (`VisualAnalysisDashboard`):**
   - 300 DPI çözünürlüğünde 2x2 Master Teşhis Paneli (`visual_analysis_dashboard.png`) çizer.

---

## 🚀 CLI Kullanımı

```bash
# 1. K-Means Renk Paleti ve CIELAB Delta E Analizi (Yaprak 57)
python -m day29.mini_project.src.cli analyze-color --clusters 5 --palette PAL-OSMANLI-01

# 2. Yapısal Simetri ve Periyodik Tekrar İncelemesi (Yaprak 57)
python -m day29.mini_project.src.cli analyze-symmetry

# 3. Kenar ve Dikiş Sürekliliği Analizi (Yaprak 58)
python -m day29.mini_project.src.cli analyze-seam

# 4. CNN Embedding ile Top-K Benzer Referans Halı Arama (Yaprak 58)
python -m day29.mini_project.src.cli find-similar --top-k 3

# 5. Uçtan Uca Master Analiz ve 300 DPI Panel Üretimi
python -m day29.mini_project.src.cli full-analysis --palette PAL-OSMANLI-01 --top-k 3
```

---

## 🧪 Testlerin Çalıştırılması

```bash
python -m pytest day29/mini_project/tests/ -v
```
*(15/15 test eksiksiz geçmektedir).*

---

## 📄 Lisans & Telif Hakkı

ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
