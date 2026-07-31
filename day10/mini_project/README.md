# Merinos Halı Perspektif Düzeltme ve Homografi Matrisi Motoru (Mini Proje)

> **Modül:** Day 10 Mini Project  
> **Konu:** DLT Homografi Matrisi, Otomatik 4 Köşe Tespiti, Geometrik Ortogonalizasyon ve Konveyör Perspektif Rektifikasyonu  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 📌 Genel Bakış

Merinos halı üretim hatlarında konveyör bantları üzerinde hareket eden halıların kalite kontrolü yüksek çözünürlüklü endüstriyel kameralarla yapılır. Ancak fiziksel kamera açısı eğimi (oblique pitch), konveyör kılavuzundan kaynaklanan açısal sapmalar ve geniş açılı lens distorsiyonları nedeniyle kamera görüntüsü tezgâhtan çıkan dikdörtgen halıyı bir **yamuk (trapezoid/quadrilateral)** olarak kaydeder.

Bu perspektif bozulması (keystone distorsiyonu):
1. Milimetrik desen ve bordür genişliklerinin ölçümünü bozar.
2. Tezgâh atkı/çözgü sıklığı (density) sayımında piksel ölçeğini konveyör derinliği boyunca değişken kılar.
3. Tezgâh desen şablonu ile dokunan halı arasında dijital piksel farkı (subtraction) almayı imkânsız hale getirir.

Bu mini proje:
1. **Otomatik 4 Köşe Tespiti (`CornerDetector`):** Endüstriyel konveyör üzerindeki halı dış hatlarını Canny ve morfolojik kapama ile tespit eder, konveks gövde (`convexHull`) ve Ramer-Douglas-Peucker poligon basitleştirmesi (`approxPolyDP`) ile 4 köşeyi sub-pixel hassasiyetle bulur.
2. **Deterministik Saat Yönü Köşe Sıralama (`order_points`):** Geometrik ağırlık merkezi etrafında polar açı sıralaması ve orijine en yakın tepe noktası seçimiyle köşeleri her zaman `[Top-Left, Top-Right, Bottom-Right, Bottom-Left]` formatında deterministik olarak sıralar (kendi içinde kesişen kum saati/bowtie poligon anomalilerini engeller).
3. **Doğrudan Lineer Dönüşüm (DLT) Homografi Çözücü (`HomographyEngine`):** 8 Serbestlik Dereceli (8-DOF) izdüşümsel homografi matrisini ($3 \times 3$) çözer; tekillik, eşdoğrusallık (collinear), determinant ve matris koşul sayısı ($Cond(H) < 10^6$) kontrolleri uygular.
4. **Merinos Sertifikalı Ebat Rektifikasyonu (`CarpetPerspectiveRectifier`):** İster ortalama kenar uzunluklarından türetilen adaptif boyutlarda, ister Merinos standart en-boy oranlarında (`160x230`, `200x290`, `80x150`, `100x100 cm`) pikselEnterpolasyonu (Bilinear / Bicubic) ile kuşbakışı ortogonal görüntü üretir.
5. **Ortogonalite ve Kalite Güvence Değerlendirmesi (`QA Grading`):** Düzeltilen halının köşe iç açılarını hesaplar, $90.0^\circ$ diklikten sapmayı ölçer ve üretim hattı için PASS / WARNING / FAIL raporu üretir.

---

## 📁 Dizin Yapısı

```
day10/mini_project/
├── configs/
│   └── rectification_config.json    # Canny, blur, Merinos standart ebatları ve QA tolerans eşikleri
├── fixtures/
│   └── synthetic_carpets/           # Sentetik perspektif distorsiyonlu halı test fikstürleri
│       ├── carpet_skewed_oblique_25deg.png      # 25° eğik kamera açısı
│       ├── carpet_conveyor_skewed_35deg.png    # 35° konveyör yaklaşım açısı
│       └── carpet_skewed_severe_45deg.png      # 45° şiddetli perspektif keystone açısı
├── src/
│   ├── __init__.py
│   ├── models.py                    # Point2D, QuadCorners, HomographyResult, RectificationReport
│   ├── corner_detector.py           # order_points, CornerDetector (Canny + Hull + approxPolyDP)
│   ├── homography.py                # compute_homography, transform_points, warp_perspective
│   ├── rectifier.py                 # CarpetPerspectiveRectifier (pipeline & QA grader)
│   ├── generator.py                 # Sentetik desenli perspektif halı üretici
│   └── cli.py                       # detect-corners, rectify, benchmark, generate-fixtures CLI
├── tests/
│   ├── __init__.py
│   └── test_rectification.py        # 10 kapsamlı birim ve entegrasyon testi
└── outputs/                         # Üretilen rektifiye edilmiş halılar ve benchmark raporları
    ├── sample_corners.json
    ├── sample_corner_detection_overlay.png
    ├── sample_rectified_carpet.png
    ├── sample_rectification_report.json
    ├── rectification_benchmark.json
    └── rectification_summary.md
```

---

## 🚀 CLI Kullanım Kılavuzu

### 1. Sentetik Fikstürleri Üretme
```bash
python -m day10.mini_project.src.cli generate-fixtures
```

### 2. Halı Köşelerini Tespit Etme ve Görselleştirme
```bash
python -m day10.mini_project.src.cli detect-corners \
    --image day10/mini_project/fixtures/synthetic_carpets/carpet_skewed_oblique_25deg.png \
    --output day10/mini_project/outputs/sample_corners.json \
    --overlay-output day10/mini_project/outputs/sample_corner_detection_overlay.png
```

### 3. Perspektif Düzeltme (Rektifikasyon) ve Kalite Raporu
```bash
# Adaptif Boyutlandırma Modu
python -m day10.mini_project.src.cli rectify \
    --image day10/mini_project/fixtures/synthetic_carpets/carpet_skewed_oblique_25deg.png \
    --mode adaptive \
    --output-image day10/mini_project/outputs/sample_rectified_carpet.png \
    --output-report day10/mini_project/outputs/sample_rectification_report.json

# Standart Merinos 160x230 cm Oranı Modu
python -m day10.mini_project.src.cli rectify \
    --image day10/mini_project/fixtures/synthetic_carpets/carpet_skewed_oblique_25deg.png \
    --mode standard \
    --ratio 160x230 \
    --output-image day10/mini_project/outputs/sample_rectified_160x230.png
```

### 4. Hız ve Doğruluk Benchmark Testi
```bash
python -m day10.mini_project.src.cli benchmark
```

---

## 🧪 Birim Testleri

Test paketini çalıştırmak için:
```bash
python -m pytest day10/mini_project/tests/ -v
```
Tüm 10 test homografi matrisi tersinirliği, köşe açı hesaplamaları, deterministik saat yönü sıralaması, dejenere eşdoğrusal nokta hata yakalama ve sentetik fikstür doğruluğunu test eder.
