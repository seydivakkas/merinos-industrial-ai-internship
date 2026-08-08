# Merinos Multiclass Defect Classification & Quality Triage Toolkit

> **Aşama:** Faz 3: Klasik Makine Öğrenmesi & Kalite Sınıflandırma (Day 17)  
> **Konu:** Çok Sınıflı Kusur Sınıflandırması (Multiclass Classification)  
> **Yazar:** Seydi Eryılmaz (@seydivakkas)  
> **Telif Hakkı:** (c) 2026 Seydi Eryılmaz. Özel Lisans — Tüm Hakları Saklıdır.

---

## 🎯 Projenin Amacı ve Endüstriyel Kapsam
Merinos Halı Sanayi ve Ticaret A.Ş. bünyesinde ikili sınıflandırmanın ötesine geçilerek, dokuma ve iplik kalite kontrol süreçlerinde tespit edilen kusurların **kök nedenlerine göre 4 ana sınıfa** otomatik ayrıştırılması (triage) sağlanmıştır:

1. `YARN_BREAKAGE` (İplik Kopması / Çözgü-Atkı Kopuşu)
2. `OIL_STAIN` (Mekanik Yağ Lekesi / Rulman Sızıntısı)
3. `JACQUARD_PATTERN_SHIFT` (Jakar Desen Kayması / Faz Senkronizasyon Hatası)
4. `BORDER_SEWING_DEFECT` (Kenar Dikiş / Overlok Hatası)

İki temel çok sınıflı mimari karşılaştırılmıştır:
- **Softmax Multinomial Lojistik Regresyon:** Tüm sınıfları ortak bir olasılık uzayında ($\sum_k P_k = 1$) eşzamanlı optimize eden konveks model.
- **One-vs-Rest (OvR / One-vs-All):** 4 bağımsız ikili lojistik regresyon modelinin birleşimi.

---

## 📐 Matematiksel Temeller

### 1. Softmax Fonksiyonu ve Multinomial Olasılık
$$P(Y = k \mid \mathbf{x}) = \frac{\exp(\mathbf{w}_k^T \mathbf{x} + b_k)}{\sum_{j=0}^{K-1} \exp(\mathbf{w}_j^T \mathbf{x} + b_j)} \quad (K = 4)$$

### 2. Çok Sınıflı Çapraz Entropi (Categorical Cross-Entropy)
$$\mathcal{L}(\mathbf{W}, \mathbf{b}) = -\frac{1}{N} \sum_{i=1}^N \sum_{k=0}^{K-1} y_{i,k} \ln\left(P(Y = k \mid \mathbf{x}_i)\right) + \frac{1}{2C} \sum_{k=0}^{K-1} \|\mathbf{w}_k\|_2^2$$

### 3. One-vs-Rest (OvR) Ayrıştırması
Her $k \in \{0, 1, 2, 3\}$ için ikili lojistik regresyon modeli $f_k(\mathbf{x}) = \sigma(\mathbf{w}_k^T \mathbf{x} + b_k)$ eğitilir. Nihai sınıf:
$$\hat{y} = \arg\max_{k \in \{0, 1, 2, 3\}} f_k(\mathbf{x})$$

### 4. Makro, Mikro ve Ağırlıklı F1 Skorları
- **Makro F1 (Macro F1):** Sınıfların boyutundan bağımsız aritmetik ortalama (nadir kusurlar için en adil metrik):
  $$\text{Macro F1} = \frac{1}{K} \sum_{k=0}^{K-1} F1_k$$
- **Mikro F1 (Micro F1):** Tüm sınıfların toplam $TP, FP, FN$ değerleri üzerinden hesaplanır (Doğruluk oranına eşdeğerdir).
- **Ağırlıklı F1 (Weighted F1):** Sınıf örneklem oranlarıyla ($w_k = N_k / N$) ağırlıklandırılmış ortalama:
  $$\text{Weighted F1} = \sum_{k=0}^{K-1} w_k \cdot F1_k$$

---

## 📂 Paket Mimarisi

```
day17/mini_project/
├── configs/
│   └── multiclass_config.json        # 4 kusur sınıfı tanımı ve hiperparametreler
├── fixtures/
│   └── multiclass_defect_dataset.csv # 3000 satırlık sentetik telemetri verisi
├── outputs/
│   ├── multiclass_master_report.json    # Softmax vs OvR model karşılaştırma raporu
│   └── multiclass_diagnostic_panel.png  # 2x2 Kurumsal çok sınıflı teşhis paneli
├── src/
│   ├── __init__.py                   # Modül dışa aktarımları
│   ├── models.py                     # Pydantic v2 modelleri (DefectClass, Metrics, Report)
│   ├── data_generator.py             # 4 sınıflı sentetik sensör telemetrisi jeneratörü
│   ├── preprocessor.py               # Tabakalı bölme ve StandardScaler motoru
│   ├── multiclass_classifier.py      # Softmax ve OvR Lojistik Regresyon motoru
│   ├── evaluator.py                  # 4x4 Karar Matrisi, Makro/Mikro F1, OvR ROC-AUC
│   ├── visualizer.py                 # Matplotlib/Seaborn 2x2 teşhis paneli çizicisi
│   └── cli.py                        # Komut satırı yönetim arayüzü
└── tests/
    ├── __init__.py
    └── test_multiclass_classification.py # 10 adet kapsamlı test
```

---

## 💻 CLI Kullanım Kılavuzu

### 1. Çok Sınıflı Veri Kümesi Üretimi
```bash
python -m day17.mini_project.src.cli generate-data --samples 3000
```

### 2. Model Eğitimi
```bash
python -m day17.mini_project.src.cli train
```

### 3. Model Kıyaslama ve Raporlama
```bash
python -m day17.mini_project.src.cli evaluate
```

### 4. 2x2 Teşhis Paneli Üretimi
```bash
python -m day17.mini_project.src.cli plot
```

### 5. Canlı Sensör Verisinden Kusur Teşhisi
```bash
# İplik Kopması Teşhisi (Düşük mukavemet, yüksek gerilim dalgalanması)
python -m day17.mini_project.src.cli predict \
  --tensile 14.5 --elongation 6.8 --hairiness 5.5 --twist 410 \
  --dtex 2220 --rpm 680 --tension 49.0 --humidity 52.0 --temp 25.0 --weft 550

# Yağ Lekesi Teşhisi (Yüksek sıcaklık, düşük nem, yüksek tüylülük)
python -m day17.mini_project.src.cli predict \
  --tensile 25.0 --elongation 13.5 --hairiness 9.2 --twist 440 \
  --dtex 2210 --rpm 625 --tension 21.0 --humidity 37.0 --temp 34.0 --weft 540
```

---

## 🧪 Testleri Çalıştırma
```bash
python -m pytest day17/mini_project/tests/ -v
```

---

## 📜 Lisans
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") Seydi Eryılmaz'a aittir. **ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR**. İzin alınmadan kopyalanamaz, çoğaltılamaz veya dağıtılamaz.
