# Day 07: OpenCV Görüntü İşleme & Analitik Araç Kiti (Mini Proje)

> **Aşama:** Faz 2: Endüstriyel Görüntü İşleme (Day 07)  
> **Modül:** OpenCV Image Analytics & Enhancement Toolkit  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Lisans:** [Özel Lisans — Tüm Hakları Saklıdır](file:///c:/Users/seydieryilmaz/Desktop/Projeler/Merinos%2040%20G%C3%BCnl%C3%BCk%20Staj%20Deneyimim/merinos-industrial-ai-internship/LICENSE)  

---

## 1. Modülün Amacı
Bu mini proje, Merinos fabrikası dokuma ve kalite kontrol hatlarında optik sensörler, endüstriyel kameralar ve tarayıcılardan elde edilen halı görüntülerinin ön işlemesini, gürültü temizlemesini, kontrast iyileştirmesini ve sayısal istatistiksel profillemesini gerçekleştiren modüler bir görüntü analitiği kütüphanesi ve CLI aracıdır.

## 2. Dizin Yapısı
```bash
mini_project/
├── README.md
├── configs/
│   └── toolkit_config.json
├── fixtures/
│   └── synthetic_carpets/
│       ├── carpet_normal.png
│       ├── carpet_low_contrast.png
│       ├── carpet_noisy.png
│       └── carpet_uneven_illumination.png
├── src/
│   ├── __init__.py
│   ├── io_validator.py       # Unicode / Türkçe yol uyumlu imread/imwrite ve meta doğrulama
│   ├── color_spaces.py       # BGR, RGB, GRAY, HSV, LAB, YCrCb dönüşüm ve istatistikleri
│   ├── resizer.py            # En-boy oranını koruyan simetrik letterbox resizing
│   ├── filters.py            # Gaussian, Median, Bilateral ve Unsharp Masking filtreleri
│   ├── equalization.py       # Global HE ve Algısal CLAHE (CIELAB L* ve YCrCb Y)
│   ├── analytics.py          # Shannon entropisi, RMS kontrastı, dinamik aralık motoru
│   ├── generator.py          # Sentetik halı desen ve yapay bozulma üreteci
│   └── cli.py                # Argparse tabanlı terminal CLI aracı ve benchmark orkestratörü
├── tests/
│   ├── __init__.py
│   └── test_toolkit.py       # 10 adet birim ve entegrasyon testi
└── outputs/
    ├── sample_analysis_report.json
    ├── image_enhancement_benchmark.json
    └── toolkit_summary.md
```

## 3. Temel Sınıflar ve Yetenekler
- **`ImageIOValidator`:** Windows işletim sisteminde Türkçe karakter içeren dosya yollarında (`Merinos 40 Günlük Staj Deneyimim`) `cv2.imread`'in sessizce başarısız olmasını engellemek için `np.fromfile` ve `cv2.imdecode` ile güvenli ikili okuma/yazma sağlar.
- **`ColorSpaceConverter`:** 6 endüstriyel renk uzayı arasında kayıpsız dönüşüm ve kanal istatistikleri (`H, S, V`, `L, a, b` vb.) üretir.
- **`AspectPreservingResizer`:** Halı madalyonlarının ve bordürlerinin elipsleşmesini önlemek için letterbox padding uygulayarak istenen kare boyuta (512x512 vb.) ölçekler.
- **`IndustrialFilterPipeline`:** İplik tozu ve optik sensör gürültüsü için Median filtre, kenar keskinliğini koruyarak ilmek dokusunu pürüzsüzleştirmek için Bilateral filtre, desen kusurlarını belirginleştirmek için Unsharp Masking sunar.
- **`HistogramEqualizer`:** Renkli halı görüntülerinde kromatizasyon bozulmasını (renk sapmasını) önlemek için eşitliği sadece CIELAB $L^*$ veya YCrCb $Y$ parlaklık kanalına uygular.
- **`ImageAnalyticsEngine`:** Shannon entropisi, RMS kontrastı, dinamik aralık ve Laplacian keskinlik varyansı ile görüntü kalite profili çıkarır.

## 4. CLI Komutları ile Çalıştırma

```bash
# 1. Testleri çalıştırma:
python -m pytest day07/mini_project/tests/ -v

# 2. Tekil bir halı görüntüsünü analiz etme:
python -m day07.mini_project.src.cli analyze --input day07/mini_project/fixtures/synthetic_carpets/carpet_normal.png

# 3. Düşük kontrastlı görüntüyü algısal CLAHE (LAB) ile iyileştirme:
python -m day07.mini_project.src.cli enhance --input day07/mini_project/fixtures/synthetic_carpets/carpet_low_contrast.png --method clahe_lab --output outputs/enhanced_carpet.png

# 4. En-boy oranını koruyarak 512x512 letterbox boyutlandırma:
python -m day07.mini_project.src.cli resize --input day07/mini_project/fixtures/synthetic_carpets/carpet_normal.png --size 512 512 --output outputs/resized_carpet.png

# 5. Uçtan uca benchmark motorunu çalıştırma:
python -m day07.mini_project.src.cli benchmark
```
