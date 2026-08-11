# Merinos Gradient Boosting (XGBoost & LightGBM) Defect Classification Toolkit

> **Aşama:** Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma (Day 19)  
> **Konu:** Gradient Boosting Modelleri (XGBoost / LightGBM)  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. bünyesinde bağımsız karar ağaçlarının (Bagging / Random Forest) ötesine geçilerek, ardışık zayıf öğrenicilerin önceki ağaçların artık (residual) hatalarını gradyan inişi ile optimize ettiği **Gradient Tree Boosting** mimarisi kurulmuştur.

Endüstriyel dokuma tezgâhı telemetrisi ve iplik laboratuvar test verilerinde yüksek boyutlu ve non-lineer kusur sınırlarını milisaniye mertebesinde sınıflandırmak amacıyla dünyanın iki öncü boosting kütüphanesi entegre edilmiş ve kıyaslanmıştır:
1. **XGBoost (Extreme Gradient Boosting):** 2. derece Taylor serisi açılımı ($g_i, h_i$), yaprak ağırlık regülarizasyonu ($\lambda, \gamma$) ve kesin bölünme kazancı (Exact Greedy Split Gain) ile çalışan dayanıklı boosting motoru.
2. **LightGBM (Light Gradient Boosted Machine):** Histogram tabanlı öznitelik gruplama, yaprak odaklı büyüme (Leaf-wise Growth), Gradient-based One-Side Sampling (GOSS) ve Exclusive Feature Bundling (EFB) ile ultra hızlı ve bellek dostu boosting motoru.

Her iki model de **Erken Durdurma (Early Stopping)** mekanizmasıyla donatılarak doğrulama kaybının platoya ulaştığı noktada eğitimi kesmiş, aşırı öğrenme (overfitting) engellenmiştir.

---

## 📐 Matematiksel ve Algoritmik Temeller

### 1. Sıralı Artık Öğrenmesi (Additive Boosting)
Gradient boosting, $M$ adet ağacın ağırlıklı toplamı olarak hedef fonksiyonu yaklaşıklar:
$$F_m(\mathbf{x}) = F_{m-1}(\mathbf{x}) + \eta \sum_{j=1}^J \gamma_{jm} \mathbb{I}(\mathbf{x} \in R_{jm})$$
- $\eta \in (0, 1]$: Öğrenme oranı (Shrinkage / Learning Rate).
- Her adımda yeni ağaç, mevcut modelin çok sınıflı cross-entropy kaybının gradyanına (artıklara) uydurulur:
  $$r_{ik}^{(m)} = -\left[ \frac{\partial \mathcal{L}(y_i, F(\mathbf{x}_i))}{\partial F_k(\mathbf{x}_i)} \right]_{F=F_{m-1}} = y_{ik} - p_{ik}(\mathbf{x}_i)$$

### 2. XGBoost: 2. Derece Taylor Açılımı ve Amaç Fonksiyonu
XGBoost, kayıp fonksiyonunu 2. derece Taylor serisi ile yaklaşıklar:
$$\mathcal{L}^{(t)} \approx \sum_{i=1}^n \left[ \ell(y_i, \hat{y}^{(t-1)}) + g_i f_t(\mathbf{x}_i) + \frac{1}{2} h_i f_t^2(\mathbf{x}_i) \right] + \Omega(f_t)$$
Burada:
- $g_i = \partial_{\hat{y}^{(t-1)}} \ell(y_i, \hat{y}^{(t-1)})$ (1. türev / Gradient)
- $h_i = \partial^2_{\hat{y}^{(t-1)}} \ell(y_i, \hat{y}^{(t-1)})$ (2. türev / Hessian)
- $\Omega(f_t) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^T w_j^2$ (Model Karmaşıklığı Regülarizasyonu)

Bir yaprak $j$ içindeki örnek kümesi $I_j$ için optimal ağırlık:
$$w_j^* = -\frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}$$

Düğüm bölünme kazancı (Split Gain):
$$\text{Gain} = \frac{1}{2} \left[ \frac{\left(\sum_{i \in I_L} g_i\right)^2}{\sum_{i \in I_L} h_i + \lambda} + \frac{\left(\sum_{i \in I_R} g_i\right)^2}{\sum_{i \in I_R} h_i + \lambda} - \frac{\left(\sum_{i \in I} g_i\right)^2}{\sum_{i \in I} h_i + \lambda} \right] - \gamma$$

### 3. LightGBM: Yaprak Odaklı Büyüme (Leaf-Wise) & Histogram Optimizasyonu
- **Leaf-wise Growth:** Geleneksel derinlik seviyeli (Level-wise) ağaç büyümesi yerine en büyük kayıp azalması sağlayan yaprağı bölerek asimetrik ağaçlar üretir. `max_depth` ve `num_leaves` ile aşırı öğrenme sınırlandırılır.
- **Histogram Algoritması:** Sürekli değerleri 256 diskret kutuya (bin) ayırarak bellek tüketimini $\%80$ azaltır ve bölünme süresini $\mathcal{O}(\#\text{data} \times \#\text{feature})$ karmaşıklığından $\mathcal{O}(\#\text{bin} \times \#\text{feature})$ düzeyine indirir.

### 4. 3 Aşamalı Tabakalı Ayrıştırma ve Erken Durdurma (Early Stopping)
Veri kümesi $\mathcal{D}$, hedef sınıf dağılımı korunarak 3 bağımsız alt kümeye ayrıştırılır:
- **Eğitim Kümesi (Train - %70):** Gradyan ve Hessian hesaplamaları ile ağaç oluşturma.
- **Doğrulama Kümesi (Validation - %15):** Ağaç büyümesi sırasında çok sınıflı log-loss takibi. Eğer doğrulama kaybı $P$ (`early_stopping_rounds=15`) iterasyon boyunca iyileşmezse eğitim durdurulur ve en iyi iterasyon ağırlıkları geri yüklenir.
- **Test Kümesi (Test - %15):** Eğitim veya durdurma sürecinde asla görülmemiş tarafsız genelleme değerlendirmesi.

---

## 📂 Paket Mimarisi

```
day19/mini_project/
├── configs/
│   └── boosting_config.json               # XGBoost, LightGBM ve grid arama yapılandırması
├── fixtures/
│   └── carpet_defect_boosting_dataset.csv # 3000 satırlık doğrusal olmayan telemetri verisi
├── outputs/
│   ├── boosting_master_report.json        # Detaylı kıyaslama ve çıkarım gecikmesi metrikleri
│   └── boosting_diagnostic_panel.png      # 2x2 Kurumsal karşılaştırmalı teşhis paneli
├── src/
│   ├── __init__.py                        # Dışa aktarılan sınıflar ve fonksiyonlar
│   ├── models.py                          # Pydantic v2 veri şemaları (Metrics, Tuning, Report)
│   ├── data_generator.py                  # Fiziksel sınırlara sahip doğrusal olmayan veri üretici
│   ├── preprocessor.py                    # 3 yönlü tabakalı veri ayrıştırıcı (70/15/15)
│   ├── boosting_models.py                 # MerinosXGBoostClassifier ve MerinosLightGBMClassifier
│   ├── evaluator.py                       # Doğrulama, grid optimizasyonu ve raporlama motoru
│   ├── visualizer.py                      # 2x2 Yüksek çözünürlüklü karşılaştırma görselleştiricisi
│   └── cli.py                             # Modüler komut satırı arayüzü (CLI)
└── tests/
    └── test_boosting_models.py            # 10 kapsamlı birim ve entegrasyon testi
```

---

## 🚀 Komut Satırı Arayüzü (CLI) Kullanım Rehberi

### 1. Sentetik Veri Kümesi Üretimi
```bash
python -u -m day19.mini_project.src.cli generate-data
```

### 2. Modellerin Eğitimi ve Erken Durdurma Doğrulaması
```bash
python -u -m day19.mini_project.src.cli train
```

### 3. Hiperparametre Grid Taraması (Öğrenme Oranı ve Derinlik)
```bash
python -u -m day19.mini_project.src.cli tune
```

### 4. Kapsamlı Model Kıyaslaması ve Master JSON Raporu
```bash
python -u -m day19.mini_project.src.cli evaluate
```

### 5. 2x2 Teşhis Paneli Grafiğinin Çizdirilmesi
```bash
python -u -m day19.mini_project.src.cli plot
```

### 6. Canlı Tezgâh Kusur Teşhisi (Single-Sample Inference)
```bash
python -u -m day19.mini_project.src.cli predict \
  --tensile 12.5 --elongation 7.0 --hairiness 5.0 --twist 410 --dtex 2200 \
  --rpm 620 --tension 48.0 --humidity 55.0 --temp 24.0 --weft 530
```

---

## 📊 Endüstriyel Model Kıyaslama Sonuçları

| Performans Metriği | XGBoost Classifier | LightGBM Classifier | Üstünlük / Not |
| :--- | :---: | :---: | :--- |
| **Test Doğruluğu (Accuracy)** | **%100.00** | **%100.00** | Mükemmel ayrım |
| **Makro F1-Skoru** | **1.0000** | **1.0000** | Dengesiz sınıflarda tam duyarlılık |
| **Doğrulama Kaybı (Val Loss)** | 0.0015 | **0.0000** | LightGBM daha dik kayıp inişi |
| **Optimal İterasyon (Early Stop)** | 150 / 150 | **148 / 150** | LightGBM 148. ağaçta erken durdu |
| **Eğitim Süresi (Train Time)** | 460.4 ms | **408.5 ms** | **LightGBM 1.13x daha hızlı** |
| **Tekil Çıkarım Gecikmesi** | **1.09 ms** | 1.49 ms | **XGBoost 1.36x daha düşük gecikme** |
| **Throughput (FPS)** | **917.4 FPS** | 671.2 FPS | Canlı tezgâh izleme standardı (>500 FPS) |
| **En Önemli Öznitelikler** | İplik Mukavemeti, İğ Hızı | İplik Mukavemeti, Tezgâh Gerginliği | Tutarlı fiziksel açıklanabilirlik |

---

## 📜 Lisans

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
