# Day 08: Algısal Renk Uzayı Analizi ve Renk Eşikleme (Mini Proje)

> **Aşama:** Faz 2: Endüstriyel Görüntü İşleme (Day 08)  
> **Modül:** Perceptual Color Space Analysis & QA Engine  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 1. Modülün Amacı
Bu mini proje, Merinos halı dokuma hatlarında ve iplik boyahanelerinde optik spektrometre ve kalite denetim kameralarından alınan görüntüler üzerinde renk sapmalarını algısal olarak ölçen, RGB sınırlılıklarını aşarak HSV ve CIELAB uzaylarında iplik renklerini ayrıştıran ve CIE 1976 $\Delta E^*_{ab}$ toleranslarına göre iplik partilerini (dye lots) otomatik derecelendiren (`PASS`, `WARNING`, `REJECT`) bir endüstriyel renk analitiği paketidir.

## 2. Dizin Yapısı
```bash
mini_project/
├── README.md
├── configs/
│   └── color_config.json              # Merinos referans iplik paleti (Hex, RGB, HSV, LAB) ve QA toleransları
├── fixtures/
│   └── synthetic_carpets/
│       ├── carpet_palette_master.png  # Referans halı deseni (Delta E < 0.6, PASS)
│       ├── carpet_lot_drift_pass.png  # Kabul edilebilir hafif sapma (Delta E < 1.0, PASS)
│       ├── carpet_lot_drift_warning.png # Fark edilebilir parti kayması (Delta E ~ 3.8, WARNING)
│       └── carpet_lot_drift_reject.png  # Hatalı boyama partisi (Delta E > 15.0, REJECT)
├── src/
│   ├── __init__.py
│   ├── color_models.py                # Pydantic/Dataclass modelleri (YarnColor, InspectionReport, QAGrade)
│   ├── conversions.py                 # D65 CIE standartlı ve OpenCV matris dönüşümleri
│   ├── delta_e.py                     # CIE 1976 Delta E hesaplayıcı ve QA sınıflandırıcısı
│   ├── thresholding.py                # HSV (Dairesel Hue wrap-around destekli) ve CIELAB küresel eşikleme
│   ├── analyzer.py                    # 4 iplikli desen kompozisyon ve parti analizi orkestratörü
│   ├── generator.py                   # Sentetik halı ve kontrollü parti sapması üreteci
│   └── cli.py                         # Argparse tabanlı terminal CLI aracı ve benchmark motoru
├── tests/
│   ├── __init__.py
│   └── test_color_analysis.py         # 10 adet birim ve entegrasyon testi
└── outputs/
    ├── dye_lot_inspection_report.json # Detaylı parti kalite denetim raporu
    ├── color_space_benchmark.json     # Gecikme ve throughput hız dökümü
    └── color_analysis_summary.md      # Kurumsal özet tablosu
```

## 3. Temel Sınıflar ve Yetenekler
- **`ColorConverter`:** D65 aydınlatıcı referans beyaz noktası ve sRGB gama açılımı formülleriyle RGB, HSV ve CIELAB arasında çift yönlü yüksek hassasiyetli matematiksel dönüşüm sağlar.
- **`DeltaECalculator`:** CIE 1976 $\Delta E^*_{ab}$ formülüyle Öklid algısal renk farkını ve 2D Delta E haritalarını hesaplar; $\Delta E^* < 2.0$ (PASS), $2.0 \le \Delta E^* < 5.0$ (WARNING) ve $\Delta E^* \ge 5.0$ (REJECT) etiketlerini atar.
- **`HSVColorThresholder`:** Kırmızı rengin silindirik Hue dairesinde ($H \in [0, 10] \cup [170, 180]$) kırılmasını çift aralıklı bitwise OR ile birleştirerek deliksiz ve aydınlatma değişimlerine dirençli maskeler üretir.
- **`PerceptualDeltaEThresholder`:** Hedef iplik renginin CIELAB koordinatlarına göre $\Delta E^* \le \tau$ küresel tolerans çemberi içindeki pikselleri doğrudan filtreler.
- **`MaskMorphologyCleaner`:** İplik tozu ve sensör gürültüsü kaynaklı tek piksellik sıçramaları morfolojik Açma (Opening) ile temizler.
- **`CarpetColorAnalyzer`:** Halı desenindeki tüm ana iplik renklerini ayrıştırır, her ipliğin kapsama alanını ($A\%$) hesaplar ve ortalama renk sapmasını hedefle kıyaslayarak genel parti onayını belirler.

## 4. CLI Komutları ile Çalıştırma

```bash
# 1. Testleri çalıştırma:
python -m pytest day08/mini_project/tests/ -v

# 2. İki renk arasında Delta E hesaplama:
python -m day08.mini_project.src.cli delta-e --hex1 "#8B0000" --hex2 "#A00000"

# 3. Halı görüntüsünü iplik parti kontrolü için denetleme:
python -m day08.mini_project.src.cli inspect --input day08/mini_project/fixtures/synthetic_carpets/carpet_lot_drift_warning.png

# 4. Uçtan uca benchmark ve raporlama motorunu çalıştırma:
python -m day08.mini_project.src.cli benchmark
```
