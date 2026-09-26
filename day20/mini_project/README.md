# Merinos Support Vector Machines (SVM) Defect Classification Toolkit

> **Aşama:** Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma (Day 20)  
> **Konu:** Destek Vektör Makineleri (Support Vector Machines - SVM)  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. Gaziantep 4. OSB tesislerinde, jakarlı dokuma tezgâhlarından toplanan sensör telemetrisi ve iplik laboratuvar parametreleri arasındaki karmaşık kusur sınırlarını maksimum marjinli (Maximum Margin) hiper-düzlemlerle ayırmak üzere **Destek Vektör Makineleri (SVM)** mimarisi kurulmuştur.

Bu modül kapsamında:
1. **Maksimum Marjin Ayrımı:** Sınıflar arası boşluğu ($\frac{2}{\|\mathbf{w}\|}$) maksimize eden optimal karar hiper-düzleminin inşası.
2. **StandardScaler Standartlaştırması:** Büyük ölçekli telemetri değişkenlerinin ($2200 \text{ dtex}$, $600 \text{ RPM}$) küçük ölçekli iplik özelliklerini ($5.0\text{ H}$, $24^\circ\text{C}$) ezmesini engelleyen data-leakage korumalı ölçekleme.
3. **Çekirdek Hilesi (Kernel Trick):**
   - **Linear SVM:** Hızlı, doğrusal hiper-düzlem referansı.
   - **Polynomial SVM (Cubic):** 3. derece eğrisel etkileşimleri yakalayan çekirdek.
   - **RBF (Gaussian) SVM:** Sonsuz boyutlu Hilbert uzayına haritalama yaparak doğrusal olmayan sınırları yüksek genelleme ile ayıran çekirdek.
4. **Destek Vektörü (Support Vector) Analizi:** Sınıf sınırlarını belirleyen kritik örneklemlerin (`n_support_`) ve dual çarpanların ($\alpha_i$) incelenmesi.
5. **Platt Scaling Olasılık Kalibrasyonu:** Karar mesafelerinin sigmoid fonksiyonu ile güven skorlarına dönüştürülmesi.

---

## 📐 Matematiksel ve Algoritmik Temeller

### 1. Maksimum Marjin ve Primal Formülasyon
$n$ adet eğitim örneği $\{(\mathbf{x}_i, y_i)\}_{i=1}^n$ için karar fonksiyonu:
$$f(\mathbf{x}) = \mathbf{w}^T \phi(\mathbf{x}) + b$$

Yumuşak marjin (Soft-Margin) optimizasyon problemi:
$$\min_{\mathbf{w}, b, \boldsymbol{\xi}} \frac{1}{2} \|\mathbf{w}\|^2 + C \sum_{i=1}^n \xi_i \quad \text{s.t.} \quad y_i (\mathbf{w}^T \phi(\mathbf{x}_i) + b) \ge 1 - \xi_i, \quad \xi_i \ge 0$$
- $C > 0$: Marjin genişliği ile sınıflandırma hatası arasındaki regülarizasyon cezası.
- $\xi_i$: Marjin ihlal miktarı (Gevşek değişken / Slack variable).

### 2. Dual Formülasyon ve Destek Vektörleri
Lagrange çarpanları $\alpha_i$ cinsinden dual problem:
$$\max_{\boldsymbol{\alpha}} \sum_{i=1}^n \alpha_i - \frac{1}{2} \sum_{i=1}^n \sum_{j=1}^n \alpha_i \alpha_j y_i y_j K(\mathbf{x}_i, \mathbf{x}_j) \quad \text{s.t.} \quad 0 \le \alpha_i \le C, \quad \sum_{i=1}^n \alpha_i y_i = 0$$

KKT koşullarına göre:
- $\alpha_i = 0$: Örnek marjinin güvenli tarafında, karar sınırına etkisi yoktur.
- $0 < \alpha_i < C$: Serbest Destek Vektörü (Free SV), tam marjin sınırındadır ($y_i f(\mathbf{x}_i) = 1$).
- $\alpha_i = C$: Sınırlı Destek Vektörü (Bounded SV), marjin içinde veya yanlış taraftadır.

### 3. Çekirdek Türleri (Kernels)
- **Doğrusal (Linear):** $K(\mathbf{x}, \mathbf{z}) = \mathbf{x}^T \mathbf{z}$
- **Polinomial (Cubic):** $K(\mathbf{x}, \mathbf{z}) = (\gamma \mathbf{x}^T \mathbf{z} + r)^d \quad (d=3, r=1)$
- **Gauss (RBF):** $K(\mathbf{x}, \mathbf{z}) = \exp\left( -\gamma \|\mathbf{x} - \mathbf{z}\|^2 \right) \quad (\gamma = \frac{1}{2\sigma^2})$

---

## 📂 Paket Mimarisi

```
day20/mini_project/
├── configs/
│   └── svm_config.json               # Model hiperparametreleri ve grid arama ayarları
├── fixtures/
│   └── carpet_defect_svm_dataset.csv # 3000 satırlık sentetik telemetri veri kümesi
├── outputs/
│   ├── svm_master_report.json        # Kapsamlı karşılaştırma ve çıkarım gecikmesi metrikleri
│   └── svm_diagnostic_panel.png      # 2x2 Kurumsal karşılaştırmalı teşhis paneli
├── src/
│   ├── __init__.py                   # Modül dışa aktarımları
│   ├── models.py                     # Pydantic v2 veri şemaları (Metrics, SVs, Report)
│   ├── data_generator.py             # 10 fiziksel sensörlü doğrusal olmayan veri üretici
│   ├── preprocessor.py               # StandardScaler ve 80/20 tabakalı bölme
│   ├── svm_models.py                 # MerinosSVMClassifier sarmalayıcısı (Linear/Poly/RBF)
│   ├── evaluator.py                  # Değerlendirme, grid taraması ve raporlama motoru
│   ├── visualizer.py                 # 2x2 Teşhis paneli ve 2D karar sınırı çizici
│   └── cli.py                        # Modüler komut satırı arayüzü (CLI)
└── tests/
    └── test_svm_models.py            # 10 kapsamlı birim ve entegrasyon testi
```

---

## 🚀 Komut Satırı Arayüzü (CLI) Kullanım Rehberi

### 1. Sentetik Veri Kümesi Üretimi
```bash
python -u -m day20.mini_project.src.cli generate-data --samples 3000
```

### 2. Modellerin Eğitimi ve Destek Vektör Sayılarının İncelenmesi
```bash
python -u -m day20.mini_project.src.cli train
```

### 3. Hiperparametre Grid Taraması (C ve gamma)
```bash
python -u -m day20.mini_project.src.cli tune
```

### 4. Kapsamlı Model Kıyaslaması ve Master JSON Raporu
```bash
python -u -m day20.mini_project.src.cli evaluate
```

### 5. 2x2 Teşhis Paneli ve 2D Karar Sınırları Grafiği
```bash
python -u -m day20.mini_project.src.cli plot
```

### 6. Canlı Dokuma Tezgâhı Kusur Teşhisi (Platt Scaling Olasılıkları)
```bash
python -u -m day20.mini_project.src.cli predict \
  --tensile 15.0 --elongation 9.5 --hairiness 4.5 --twist 430.0 \
  --dtex 2220.0 --rpm 610.0 --tension 42.0 --humidity 58.0 --temp 23.5 --weft 525.0
```

---

## 📊 Endüstriyel Model Kıyaslama Sonuçları

| Performans Metriği | Linear SVM | Polynomial SVM (d=3) | RBF (Gaussian) SVM | Üstünlük & Mühendislik Değerlendirmesi |
| :--- | :---: | :---: | :---: | :--- |
| **Test Doğruluğu** | **%100.00** | **%100.00** | **%100.00** | Tüm çekirdekler tam ayrım sağladı |
| **Makro F1-Skoru** | **1.0000** | **1.0000** | **1.0000** | Kusursuz sınıf dengesi |
| **Cohen Kappa ($\kappa$)** | **1.0000** | **1.0000** | **1.0000** | Şans dışı tam uyum |
| **Destek Vektörü (Adet)** | **41 SV** | 47 SV | 95 SV | 🏆 **Linear SVM (En Sade / Seyrek Model)** |
| **Destek Vektör Oranı** | **%1.7** | %2.0 | %4.0 | Örneklemlerin sadece %1.7'si sınırdadır |
| **Eğitim Süresi** | 17.3 ms | **16.6 ms** | 44.7 ms | 🏆 **Poly & Linear SVM (Ultra Hızlı)** |
| **Tekil Çıkarım Gecikmesi** | **0.0589 ms** | 0.0595 ms | 0.0635 ms | 🏆 **Linear SVM (En Düşük Gecikme)** |
| **Throughput (FPS)** | **16,980 FPS** | 16,800 FPS | 15,740 FPS | Gömülü PLC ve kamera hattı için mükemmel |

---

## 📜 Lisans

```
ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR

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
