# Merinos Dominant Renk Paleti ve CIEDE2000 Eşleştirme Motoru (Mini Proje)

> **Modül:** Day 11 Mini Project  
> **Konu:** K-Means ile Baskın Renk Paleti Çıkarımı, Renk Kuantizasyonu, ISO/CIE 11664-6:2014 CIEDE2000 Renk Farkı ve Jakarlı Tezgâh Cağlık Bobin Eşleştirmesi  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 📌 Genel Bakış

Endüstriyel jakarlı halı tezgâhları (Merinos Elektronik Jakar Sistemleri), desenleri 6, 8, 10 veya 12 sınırlı bobin rengi (iplik cağlığı / creel) ile dokur. Müşterilerden veya tasarım stüdyolarından gelen dijital desenlerde veya optik hat kameralarından alınan fotoğraflarda ise gölgeler, iplik lif dokuları ve sensör gürültüsü nedeniyle yüz binlerce farklı piksel tonu yer alır.

Bu mini proje:
1. **Denetimsiz K-Means Renk Paleti Çıkarımı:** Halı desenindeki pikselleri CIELAB veya sRGB uzayında kümeleyerek baskın $K$ rengi ve yüzey kaplama oranlarını (`%`) çıkarır.
2. **Uzamsal Alt-Örnekleme (`Subsampling`):** 512x512 veya daha yüksek çözünürlüklü halı görsellerini 15,000 piksellik örneklemle kümeleyerek $10\times$ hızlanma sağlar.
3. **ISO/CIE 11664-6:2014 CIEDE2000 ($\Delta E_{00}$) Motoru:** $S_L, S_C, S_H$ ağırlık fonksiyonları, $G$ kroma düzeltmesi, $360^\circ$ açısal süreksizlik ve mavi bölge elips rotasyon faktörü ($R_T$) ile saniyede 2.1 milyon renk çifti hesaplar.
4. **Fabrika İplik Bobin Eşleştirme & Cağlık Planı:** Çıkarılan serbest renkleri Merinos 16 ipliklik sertifikalı üretim kataloğuyla eşleştirerek jakarlı tezgâh cağlık yerleşim manifestosu (`CreelAllocationPlan`) ve $m^2$ başına tahmini iplik maliyetini hesaplar.
5. **Halı Kuantizasyonu & Distorsiyon Haritası:** Deseni tezgâh ipliklerine indirger (indeksli görüntü simülasyonu) ve piksel bazlı kuantizasyon distorsiyon haritası üretir.

---

## 📁 Dizin Yapısı

```
day11/mini_project/
├── configs/
│   └── palette_config.json          # 16 Merinos sertifikalı iplik kataloğu, K-Means & CIEDE2000 parametreleri
├── fixtures/
│   └── synthetic_carpets/           # Sentetik çok renkli halı test fikstürleri
│       ├── carpet_oriental_classic.png      # 6 renkli klasik madalyon halı
│       ├── carpet_modern_geometric.png      # 5 renkli Bauhaus modern geometrik halı
│       └── carpet_monochrome_textured.png   # 4 renkli dokulu bej/gri halı
├── src/
│   ├── __init__.py
│   ├── color_models.py             # CatalogYarn, ExtractedColor, MatchGrade, CreelAllocationPlan
│   ├── ciede2000.py                # ISO/CIE 11664-6 CIEDE2000 skaler, 2D/3D vektörize motor
│   ├── kmeans_palette.py           # K-Means palet çıkarıcı ve subsampling hızlandırıcı
│   ├── kmeans_palette_engine.py    # Hafif scikit-learn / Pydantic palet çıkarıcı
│   ├── yarn_matcher.py             # Fabrika bobin eşleştirme ve cağlık planlama motoru
│   ├── quantizer.py                # Halı kuantizasyonu ve indeksli harita simülatörü
│   ├── generator.py                # Sentetik benchmark halı üretici
│   └── cli.py                      # extract, match, quantize, benchmark terminal komutları
├── tests/
│   ├── __init__.py
│   ├── test_kmeans_palette_engine.py # K-Means temel birim testleri
│   └── test_palette_and_quantizer.py # 10 birim ve entegrasyon testi
└── outputs/                        # Üretilen JSON raporları, ısı haritaları ve özetler
    ├── sample_palette_extraction.json
    ├── yarn_creel_allocation_report.json
    ├── ciede2000_benchmark.json
    └── palette_summary.md
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Halı Fikstürlerini Üretme
```bash
python -m day11.mini_project.src.cli generate-fixtures
```

### 2. Dominant Renk Paleti Çıkarımı
```bash
python -m day11.mini_project.src.cli extract \
    --image day11/mini_project/fixtures/synthetic_carpets/carpet_oriental_classic.png \
    --k 6 \
    --space LAB \
    --subsample 15000 \
    --output day11/mini_project/outputs/sample_palette_extraction.json
```

### 3. Merinos İplik Kataloğu ile Eşleştirme & Cağlık Planı
```bash
python -m day11.mini_project.src.cli match \
    --image day11/mini_project/fixtures/synthetic_carpets/carpet_oriental_classic.png \
    --k 6 \
    --output day11/mini_project/outputs/yarn_creel_allocation_report.json
```

### 4. Halı Kuantizasyonu ve Hata Isı Haritası
```bash
python -m day11.mini_project.src.cli quantize \
    --image day11/mini_project/fixtures/synthetic_carpets/carpet_oriental_classic.png \
    --target catalog \
    --output-dir day11/mini_project/outputs
```

### 5. Performans ve Standart Doğrulama Benchmark'ı
```bash
python -m day11.mini_project.src.cli benchmark
```

---

## 🧪 Birim Testleri

```bash
python -m pytest day11/mini_project/tests/ -v
```

11 birim testi şunları doğrular:
1. `test_kmeans_palette_extraction`: K-Means kümeleme, HEX kod üretimi ve oran toplamı doğrulaması.
2. `test_palette_extraction`: Çeşitli renk uzaylarında (LAB/RGB) baskın palet çıkarımı.
3. `test_ciede2000_identical_colors_zero`: Özdeş renklerde $\Delta E_{00} = 0.0$.
4. `test_ciede2000_standard_sharma_pairs`: Sharma et al. (2005) standart 6 test çifti doğrulaması ($< 10^{-3}$).
5. `test_ciede2000_blue_region_rotation_significance`: Mavi bölge elips rotasyonu ($h \approx 275^\circ$) doğrulaması.
6. `test_ciede2000_achromatic_numerical_stability`: Nötr gri piksellerde ($C^* \to 0$) NaN ve sıfıra bölme hatası oluşmaz.
7. `test_kmeans_palette_extraction_proportions_sum_to_100`: Çıkarılan küme oranları toplamı tam $\%100.0$ eder.
8. `test_kmeans_palette_rgb_vs_lab_clustering`: CIELAB ve RGB uzaylarında kararlı kümeleme.
9. `test_subsampling_acceleration_and_fidelity`: Subsampling $10\times$ hızlanma sağlarken centroid kayması $< 1.5 \Delta E_{00}$ kalır.
10. `test_carpet_quantization_and_distortion_metric`: İndeksli desen boyutu $(H, W)$ korunur ve kuantizasyon distorsiyon haritası üretilir.
11. `test_yarn_matching`: Katalogdaki bir renk sorgulandığında $\Delta E_{00} = 0$ ve `EXACT` döner.
