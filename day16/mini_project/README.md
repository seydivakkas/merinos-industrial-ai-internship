# Merinos Industrial Binary Classification & Quality Control Toolkit

> **Aşama:** Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma (Day 16)  
> **Konu:** İkili Sınıflandırma ve Lojistik Regresyon Temelleri  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı ve İplik Üretim Tesisleri'nde (Gaziantep 4. OSB) dokuma tezgâhlarından ve ring/open-end iplik eğirme hatlarından toplanan 10 farklı sensör verisi üzerinden, partilerin **Kusursuz (Standart - 0)** veya **Kusurlu (Hatalı - 1)** olduğunu gerçek zamanlı olarak kestiren Lojistik Regresyon tabanlı ikili sınıflandırma motorudur.

Endüstriyel gerçeklik gereği veri kümesindeki kusur oranı yaklaşık **%10** seviyesindedir (Dengesiz Sınıflandırma / Imbalanced Classification). Bu modül, standart $\tau = 0.50$ eşiğinin azınlık sınıfını kaçırma (Tip II Hata / False Negative) zaafını çözmek için **sınıf ağırlıklandırması (`class_weight='balanced'`)**, **Youden's J İstatistiği** ve **Maliyete Duyarlı Eşik Optimizasyonu ($Cost = 10 \cdot FN + 1 \cdot FP$)** algoritmalarını bünyesinde barındırır.

---

## 📐 Matematiksel Temeller

### 1. Lojistik Fonksiyon ve Sigmoid
$$z = \mathbf{w}^T \mathbf{x} + b = w_0 + \sum_{j=1}^{10} w_j x_j$$
$$P(Y = 1 \mid \mathbf{x}) = \sigma(z) = \frac{1}{1 + e^{-z}}$$

### 2. İkili Çapraz Entropi (Binary Cross-Entropy / Log-Loss)
$$\mathcal{L}_{BCE}(\mathbf{w}, b) = -\frac{1}{N} \sum_{i=1}^N \left[ y_i \log(\sigma(z_i)) + (1 - y_i) \log(1 - \sigma(z_i)) \right] + \frac{1}{2C} \|\mathbf{w}\|_2^2$$

### 3. Odds Oranı (Odds Ratio)
$$\text{Odds} = \frac{P(Y = 1 \mid \mathbf{x})}{1 - P(Y = 1 \mid \mathbf{x})} = e^{\mathbf{w}^T \mathbf{x} + b}$$
$$\text{OR}_j = \exp(w_j)$$
- $\text{OR}_j > 1$: $j$. özelliğin 1 birimlik artışı kusur riskini $\text{OR}_j$ katına çıkarır (Risk Artırıcı).
- $\text{OR}_j < 1$: $j$. özelliğin artışı kusur riskini azaltır (Koruyucu Etki).

### 4. Youden's J İstatistiği ve Maliyet Fonksiyonu
$$J(\tau) = \text{TPR}(\tau) - \text{FPR}(\tau) = \text{Recall}(\tau) - (1 - \text{Specificity}(\tau))$$
$$\tau_{\text{optimal}} = \arg\max_\tau J(\tau)$$
$$\mathcal{C}(\tau) = c_{FN} \cdot FN(\tau) + c_{FP} \cdot FP(\tau) \quad (c_{FN} = 10, \, c_{FP} = 1)$$

---

## 📂 Paket Mimarisi

```
day16/mini_project/
├── configs/
│   └── classification_config.json    # Sensör özellikleri, maliyet matrisi ve model ayarları
├── fixtures/
│   └── yarn_quality_dataset.csv      # 2500 satırlık sentetik iplik/dokuma sensör verisi
├── outputs/
│   ├── classification_master_report.json    # Model başarım metrikleri ve katsayılar
│   └── classification_diagnostic_panel.png  # 2x2 Kurumsal ROC, PR, CM ve Eşik teşhis paneli
├── src/
│   ├── __init__.py                   # Modül dışa aktarımları
│   ├── models.py                     # Pydantic v2 veri şemaları (QualityClass, Metrics, Report)
│   ├── data_generator.py             # Dengesiz endüstriyel sensör verisi üreticisi
│   ├── preprocessor.py               # Tabakalı bölme (stratified) ve StandardScaler motoru
│   ├── logistic_classifier.py        # Standart ve dengeli Lojistik Regresyon sarıcısı
│   ├── evaluator.py                  # ROC-AUC, PR-AUC, Karar Matrisi ve Eşik tarayıcı
│   ├── visualizer.py                 # Matplotlib/Seaborn 2x2 teşhis paneli çizicisi
│   └── cli.py                        # Komut satırı kullanıcı arayüzü
└── tests/
    ├── __init__.py
    └── test_binary_classification.py # 10 adet birim ve entegrasyon testi
```

---

## 💻 CLI Kullanım Kılavuzu

### 1. Sentetik Veri Kümesi Üretimi
```bash
python -m day16.mini_project.src.cli generate-data --samples 2500 --defect-ratio 0.10
```

### 2. Model Eğitimi ve Katsayı Analizi
```bash
python -m day16.mini_project.src.cli train
```

### 3. Kapsamlı Değerlendirme ve Raporlama
```bash
python -m day16.mini_project.src.cli evaluate
```

### 4. 2x2 Teşhis Paneli Üretimi
```bash
python -m day16.mini_project.src.cli plot
```

### 5. Canlı Sensör Ölçümü Kalite Tahmini (Inference)
```bash
# Kusurlu Parti Tahmini (Düşük mukavemet, yüksek gerilim dalgalanması)
python -m day16.mini_project.src.cli predict \
  --tensile 16.0 --elongation 7.5 --hairiness 8.5 --twist 340 \
  --dtex 2400 --rpm 680 --tension 45.0 --humidity 45.0 --temp 30.0 --weft 600

# Standart Parti Tahmini (Yüksek mukavemet, optimum gerilim ve nem)
python -m day16.mini_project.src.cli predict \
  --tensile 28.0 --elongation 15.0 --hairiness 3.8 --twist 460 \
  --dtex 2180 --rpm 610 --tension 16.0 --humidity 64.0 --temp 23.0 --weft 535
```

---

## 🧪 Testleri Çalıştırma
```bash
python -m pytest day16/mini_project/tests/ -v
```

---

## 📜 Lisans
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") Seydi Eryılmaz'a aittir. **ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR**. İzin alınmadan ticari veya gayriticari amaçla kopyalanamaz, çoğaltılamaz veya dağıtılamaz.
