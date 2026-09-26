# Merinos Unsupervised Quality Analysis & Phase 3 Master Benchmark Release

> **Aşama:** Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma (Day 21 - Faz 3 Final Sürümü)  
> **Konu:** Boyut İndirgeme ve Kümeleme ile Gözetimsiz Kalite Analizi & Faz 3 Modelleri Büyük Final Kıyaslama Raporu  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.  
> **Lisans Badge:** ![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. Gaziantep 4. OSB tesislerindeki dokuma tezgâhlarında sensör telemetrisi ve laboratuvar kalite verileri çoğunlukla etiketlenmemiş (unlabelled) olarak SCADA sunucularına akar. 

**Day 21: Faz 3 Final Sürümü** iki kritik endüstriyel hedefi gerçekleştirmek üzere tasarlanmıştır:
1. **Gözetimsiz Kalite Analizi ve Anomali Keşfi:** Etiket gerektirmeksizin yüksek boyutlu telemetri verilerinin yapısını **PCA** ve **t-SNE** ile görselleştirmek; **K-Means** ile doğal kusur kümelerini ayrıştırmak ve **DBSCAN** ile bilinmeyen ekstrem arızaları (sensör kopması, motor aşırı yüklenmesi, klima arızası) yoğunluk dışı gürültü olarak izole etmek.
2. **Faz 3 Modelleri Karşılaştırmalı Büyük Final Kıyaslaması:** Faz 3 boyunca (Day 16–20) geliştirilen 7 temel algoritmayı (**Multinomial Lojistik Regresyon, Pruned Karar Ağacı, Random Forest, XGBoost, LightGBM, Doğrusal SVM, RBF SVM**) standart bir test kümesinde aynı anda koşturarak; doğruluk, F1 skoru, eğitim süresi, tekil çıkarım gecikmesi (ms), saniyedeki kare/işlem kapasitesi (FPS), bellek ayak izi ve endüstriyel konuşlandırma katmanları (Edge PLC, SCADA, MLOps Sunucu) kriterleriyle konsolide etmek.

---

## 📐 Matematiksel ve Algoritmik Temeller

### 1. Temel Bileşen Analizi (PCA - Principal Component Analysis)
Yüksek boyutlu telemetri matrisi $\mathbf{X} \in \mathbb{R}^{n \times d}$ merkezileştirildikten sonra kovaryans matrisi hesaplanır:
$$\boldsymbol{\Sigma} = \frac{1}{n} \mathbf{X}^T \mathbf{X}$$

Özdeğer ayrışımı (Eigenvalue Decomposition):
$$\boldsymbol{\Sigma} \mathbf{v}_i = \lambda_i \mathbf{v}_i, \quad \lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_d \ge 0$$
- $k$-ıncı bileşenin açıkladığı varyans oranı:
$$\text{EVR}_k = \frac{\lambda_k}{\sum_{j=1}^d \lambda_j}$$
- %95 kümülatif varyans hedefi:
$$k_{95} = \arg\min_k \left( \sum_{i=1}^k \text{EVR}_i \ge 0.95 \right)$$

### 2. t-Dağıtılmış Stokastik Komşuluk Gömme (t-SNE)
Yüksek boyutlu uzayda örnekler arasındaki koşullu benzerlik Gauss dağılımı ile modellenir:
$$p_{j|i} = \frac{\exp(-\|\mathbf{x}_i - \mathbf{x}_j\|^2 / 2\sigma_i^2)}{\sum_{k \ne i} \exp(-\|\mathbf{x}_i - \mathbf{x}_k\|^2 / 2\sigma_i^2)}, \quad p_{ij} = \frac{p_{j|i} + p_{i|j}}{2n}$$

2D gömme uzayında $\mathbf{y}_i, \mathbf{y}_j$ arasındaki benzerlik uzun kuyruklu Student-t (1 serbestlik dereceli) ile modellenir:
$$q_{ij} = \frac{(1 + \|\mathbf{y}_i - \mathbf{y}_j\|^2)^{-1}}{\sum_{k \ne l} (1 + \|\mathbf{y}_k - \mathbf{y}_l\|^2)^{-1}}$$

Kullback-Leibler (KL) sapması gradyan inişi ile minimize edilir:
$$\mathcal{L}_{t\text{-SNE}} = \text{KL}(P \parallel Q) = \sum_{i \ne j} p_{ij} \log \frac{p_{ij}}{q_{ij}}$$

### 3. K-Means Kümeleme ve Doğrulama Metrikleri
Küme içi kareler toplamını (Inertia) minimize eden $k$ adet merkez ($\boldsymbol{\mu}_c$) optimize edilir:
$$J = \sum_{c=1}^k \sum_{\mathbf{x} \in S_c} \|\mathbf{x} - \boldsymbol{\mu}_c\|^2$$
- **Silhouette Skoru:** $s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$, $s \in [-1, 1]$
- **Davies-Bouldin İndeksi:** $R_{ij} = \frac{s_i + s_j}{d(\boldsymbol{\mu}_i, \boldsymbol{\mu}_j)}$, $\text{DB} = \frac{1}{k}\sum_{i=1}^k \max_{j \ne i} R_{ij}$ (Düşük daha iyi)
- **Adjusted Rand Index (ARI):** Gözetimsiz kümelerin zemin gerçek etiketlerle uyum derecesi (Şans faktöründen arındırılmış, $[-1, 1]$).

### 4. DBSCAN Yoğunluk Tabanlı Kümeleme & Anomali Tespiti
Parametreler: $\varepsilon$ (komşuluk yarıçapı) ve $\text{MinPts}$ (minimum çekirdek yoğunluğu).
$$N_\varepsilon(\mathbf{x}) = \{\mathbf{x}' \in D \mid \|\mathbf{x} - \mathbf{x}'\| \le \varepsilon\}$$
- **Çekirdek Nokta (Core Point):** $|N_\varepsilon(\mathbf{x})| \ge \text{MinPts}$
- **Sınır Nokta (Border Point):** Çekirdek noktanın $\varepsilon$-komşuluğunda olup kendi komşuluğu yetersiz olan nokta.
- **Gürültü / Anomali (Noise Point - Etiket: -1):** Hiçbir çekirdek noktaya doğrudan yoğunluk-erişilebilir (density-reachable) olmayan uç değerler.

---

## 📂 Paket Mimarisi

```
day21/mini_project/
├── configs/
│   └── unsupervised_config.json               # PCA, t-SNE, K-Means, DBSCAN hiperparametreleri
├── fixtures/
│   └── carpet_defect_unsupervised_dataset.csv # 3060 satırlık sentetik telemetri ve anomali verisi
├── outputs/
│   ├── phase3_master_benchmark_report.json    # Faz 3 kümülatif kıyaslama JSON raporu
│   └── unsupervised_master_panel.png          # 2x2 Faz 3 master teşhis ve kıyas paneli
├── src/
│   ├── __init__.py                            # Paket ihracı
│   ├── models.py                              # Pydantic v2 veri modelleri ve rapor şeması
│   ├── data_generator.py                      # 4 kusur sınıfı ve ekstrem gürültü üreteci
│   ├── preprocessor.py                        # Data-leakage korumalı StandardScaler
│   ├── dimensionality.py                      # PCA ve t-SNE indirgeme motoru
│   ├── clustering.py                          # K-Means, DBSCAN ve canlı anomali tespit motoru
│   ├── benchmark_consolidator.py              # 7 Faz 3 modelini konsolide eden kıyas motoru
│   ├── visualizer.py                          # 2x2 kurumsal master grafik paneli
│   └── cli.py                                 # Argparse CLI uç noktası
├── tests/
│   └── test_unsupervised_benchmark.py         # 10 birim ve entegrasyon testi
└── README.md                                  # Teknik dokümantasyon
```

---

## 🛠️ CLI Kullanım Kılavuzu

### 1. Sentetik Telemetri ve Anomali Verisi Üretimi
```bash
python -u -m day21.mini_project.src.cli generate-data --samples 3000 --anomalies 60
```

### 2. PCA ve t-SNE Boyut İndirgeme
```bash
python -u -m day21.mini_project.src.cli reduce
```

### 3. K-Means ve DBSCAN Gözetimsiz Analiz
```bash
python -u -m day21.mini_project.src.cli cluster
```

### 4. Faz 3 Master Model Kıyaslaması (7 Model)
```bash
python -u -m day21.mini_project.src.cli benchmark
```

### 5. 2x2 Master Teşhis Paneli Üretimi
```bash
python -u -m day21.mini_project.src.cli plot
```

### 6. Canlı Telemetride Anomali Triage Denetimi
```bash
# Nominal numune
python -u -m day21.mini_project.src.cli detect-anomaly --tension 22.0 --temp 24.0

# Ekstrem arıza / anomali
python -u -m day21.mini_project.src.cli detect-anomaly --tension 75.0 --temp 38.0
```

---

## 📊 Faz 3 Büyük Final Kıyaslama Raporu (7 Model)

Aşağıdaki sonuçlar 3060 numunelik Merinos telemetri test kümesinde aynı koşullarda çalıştırılarak elde edilmiştir:

| Model Adı | Gün Tagı | Algoritmik Paradigma | Test Doğruluğu | Makro F1 | Tekil Çıkarım Gecikmesi | İşlem Kapasitesi (FPS) | Bellek Ayak İzi | Önerilen Endüstriyel Konuşlandırma Katmanı |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Multinomial Logistic Regression** | Day 17 | Doğrusal Hiper-Düzlem (Softmax) | **%100.00** | **1.0000** | **0.0417 ms** | **23,971.2 FPS** | Orta (Düşük Parametre) | SCADA İkincil Denetim & İstatistiksel Raporlama |
| **Cost-Complexity Pruned Decision Tree** | Day 18 | Eksene Dik Karar Ağacı (Pruned) | %99.50 | 0.9950 | 0.0556 ms | 17,991.4 FPS | En Düşük (Kural Ağacı) | **Kenar PLC / Mikrodenetleyici (Ultra Düşük Gecikme)** |
| **Random Forest Classifier** | Day 18 | Topluluk Öğrenmesi (Bagging) | %100.00 | 1.0000 | 30.1605 ms | 33.2 FPS | Yüksek (100 Ağaç) | Sunucu / MLOps Kalite Triage Katmanı |
| **XGBoost Classifier** | Day 19 | Gradient Boosting (Taylor 2. Derece) | %100.00 | 1.0000 | 0.4533 ms | 2,205.8 FPS | Orta-Yüksek | Yüksek Hızlı Kamera Denetim Hattı |
| **LightGBM Classifier** | Day 19 | Gradient Boosting (Leaf-wise Hist) | %100.00 | 1.0000 | 0.9735 ms | 1,027.2 FPS | Orta (Histogram Sıkıştırma) | Sürekli Yeniden Eğitim (Continuous Retraining) |
| **Linear Support Vector Machine** | Day 20 | Maksimum Marjin Hiper-Düzlem | %100.00 | 1.0000 | 0.1259 ms | 7,944.9 FPS | En Düşük (Sadece w ve b) | Kenar PLC & Donanımsal FPGA / DSP |
| **RBF Support Vector Machine** | Day 20 | Çekirdek Hilesi (Sonsuz Hilbert) | %100.00 | 1.0000 | 0.1353 ms | 7,390.8 FPS | Düşük (Destek Vektörleri) | Laboratuvar İplik & Halı Test Cihazları |

---

## 🏆 Endüstriyel Mimari Kararları & Şampiyonlar

1. **Kenar (Edge PLC / Gömülü) Şampiyonu:**  
   `Multinomial Logistic Regression` (0.0417 ms, ~24.000 FPS) ve `Pruned Decision Tree` (0.0556 ms, ~18.000 FPS). Tezgâh üzeri mikrosaniye mertebesinde tetiklenebilir, deterministik ve donanımsal C koduna kolaylıkla çevrilebilir.
2. **Merkezi Sunucu & MLOps Şampiyonu:**  
   `XGBoost` (0.45 ms, ~2.200 FPS) ve `Linear/RBF SVM` (0.12 ms, ~7.500 FPS). Yüksek genelleme başarımı, gürültü direnci ve karmaşık doğrusal olmayan sınırları mükemmel marjin ile ayırma kabiliyeti.
3. **Gözetimsiz Triage Katmanı:**  
   `K-Means` ile bilinen 4 kusur kümesi %100 uyumla (ARI: 1.00) keşfedilirken, `DBSCAN` etiketsiz gelen 60 adet ekstrem anomaliyi %100 hassasiyetle yakalayarak alarm üretmektedir.

---

## 🧪 Test Doğrulaması

Test paketini çalıştırmak için:
```bash
python -m pytest day21/mini_project/tests/ -v
```
- **Sonuç:** 10/10 test sıfır hata ile geçmektedir.

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
