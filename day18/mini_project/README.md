# Merinos Decision Trees & Random Forest Quality Classification Toolkit

> **Aşama:** Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma (Day 18)  
> **Konu:** Karar Ağaçları ve Random Forest Topluluk Öğrenmesi (Decision Trees & Random Forest Ensemble)  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. bünyesinde doğrusal modellerin ötesine geçilerek, dokuma tezgâhı mekanik telemetrisi ile iplik fiziksel öznitelikleri arasındaki karmaşık, basamaklı ve doğrusal olmayan etkileşimleri yakalamak üzere **Karar Ağaçları (Decision Tree)** ve **Random Forest Topluluk Öğrenmesi (Ensemble Learning)** mimarisi kurulmuştur.

Proje kapsamında 3 temel aşama gerçekleştirilmiştir:
1. **Budanmamış Karar Ağacı (Unpruned Tree):** Tam derinlikte eğitilen, yüksek varyans ve aşırı öğrenme (Overfitting) sergileyen referans ağaç.
2. **Minimal Maliyet-Karmaşıklık Budaması (Cost-Complexity Pruning - ccp_alpha):** Test genellemesini maksimize ederken yaprak sayısını budayan matematiksel düzenlileştirme.
3. **Random Forest Topluluk Modeli:** Bagging ve Rastgele Alt-Uzay (Random Subspace) yöntemiyle 100 karar ağacını birleştiren, varyansı minimize eden ve Out-Of-Bag (OOB) ile doğrulanan şampiyon model.

---

## 📐 Matematiksel Temeller

### 1. Safsızlık Kriterleri (Gini vs Shannon Entropy)
Bir $t$ düğümündeki safsızlık (impurity):
- **Gini Safsızlığı (Gini Impurity):**
  $$I_G(t) = 1 - \sum_{k=0}^{K-1} p(k \mid t)^2$$
- **Shannon Entropisi (Information Gain / Entropy):**
  $$I_E(t) = -\sum_{k=0}^{K-1} p(k \mid t) \log_2 p(k \mid t)$$

### 2. Minimal Maliyet-Karmaşıklık Budaması (Cost-Complexity Pruning)
Karmaşıklık ceza fonksiyonu:
$$R_\alpha(T) = R(T) + \alpha |T|$$
- $R(T)$: Ağacın toplam sınıflandırma safsızlığı / hatası.
- $|T|$: Ağaçtaki terminal yaprak sayısı.
- $\alpha \ge 0$: Yaprak başına uygulanan karmaşıklık ceza katsayısı (`ccp_alpha`).

### 3. Random Forest ve Varyans Azaltımı
$B$ adet korelasyonsuz ağacın ortalaması alındığında tahmin varyansı:
$$\text{Var}(\bar{f}) = \rho \sigma^2 + \frac{1 - \rho}{B} \sigma^2$$
$\rho$ (ağaçlar arası korelasyon) $\sqrt{p}$ rastgele öznitelik seçimiyle düşürülür; $B \to \infty$ iken ikinci terim sıfıra yaklaşır.

### 4. Out-Of-Bag (OOB) Hatası
Her bootstrap torbasına girmeyen yaklaşık $\%36.8$ ($e^{-1}$) oranındaki gözlemler test kümesi gibi kullanılarak bağımsız hata tahmin edilir:
$$\text{OOB Error} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}\left(y_i \neq \arg\max_k \sum_{b \in \mathcal{B}_i^c} \mathbb{I}(h_b(\mathbf{x}_i) = k)\right)$$

---

## 📂 Paket Mimarisi

```
day18/mini_project/
├── configs/
│   └── tree_config.json              # Model, veri ve budama hiperparametreleri
├── fixtures/
│   └── carpet_defect_tree_dataset.csv # 3000 satırlık sentetik telemetri veri kümesi
├── outputs/
│   ├── tree_ensemble_master_report.json   # Kapsamlı karşılaştırma ve benchmark raporu
│   └── tree_ensemble_diagnostic_panel.png # 2x2 Kurumsal model teşhis grafiği
├── src/
│   ├── __init__.py                   # Modül dışa aktarımları
│   ├── models.py                     # Pydantic v2 şemaları (DefectClass, Metrics, Report)
│   ├── data_generator.py             # Doğrusal olmayan sentetik veri üreteci
│   ├── preprocessor.py               # Tabakalı bölme ve tensör hazırlayıcı
│   ├── tree_models.py                # MerinosDecisionTreeClassifier & MerinosRandomForestClassifier
│   ├── evaluator.py                  # Ağaç ve topluluk değerlendirme motoru
│   ├── visualizer.py                 # 2x2 Kurumsal teşhis paneli çizici
│   └── cli.py                        # Komut satırı yönetim arayüzü
├── tests/
│   └── test_tree_models.py           # 10 birim ve entegrasyon testi
└── README.md                         # Mini-proje teknik kılavuzu
```

---

## 🚀 Hızlı Başlangıç & CLI Komutları

```bash
# 1. Sentetik veri üretimi (3000 satır)
python -u -m day18.mini_project.src.cli generate-data --samples 3000

# 2. Budanmamış Ağaç ve Random Forest eğitimi
python -u -m day18.mini_project.src.cli train

# 3. Minimal Cost-Complexity Pruning analizi
python -u -m day18.mini_project.src.cli prune

# 4. Kapsamlı değerlendirme ve master JSON raporu
python -u -m day18.mini_project.src.cli evaluate

# 5. 2x2 Teşhis panelini PNG olarak çizme
python -u -m day18.mini_project.src.cli plot

# 6. Canlı telemetri değerleriyle kusur sınıfı tahmini (Inference)
python -u -m day18.mini_project.src.cli predict \
  --tensile 12.5 --elongation 7.0 --hairiness 5.0 --twist 410 \
  --dtex 2200 --rpm 620 --tension 48.0 --humidity 55.0 --temp 24.0 --weft 530
```

---

## 📊 Kıyaslama Sonuçları (600 Test Örneği)

| Model | Eğitim Doğruluğu | Test Doğruluğu | Overfitting Boşluğu | Makro F1 | Yaprak Sayısı | Tekil Gecikme |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Budanmamış Ağaç** | %99.75 | %99.17 | %0.58 | 0.9907 | 22 Yaprak | 0.047 ms |
| **Budanmış Ağaç** | %99.75 | %99.33 | %0.42 | 0.9925 | 17 Yaprak | 0.048 ms |
| **Random Forest (100 Ağaç)**| **%100.00** | **%99.67** | **%0.33** | **0.9967** | 100 Ağaç | 63.4 ms |

---

## 🔒 Lisans & Telif Hakkı
ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
