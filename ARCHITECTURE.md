# Sistem Mimarisi — Industrial AI Internship

Bu doküman, 40 günlük staj boyunca geliştirilen yapay zeka, görüntü analitiği, klasik makine öğrenmesi, hibrit bilgi getirme (RAG) ve yerel servis bileşenlerinin mimari yapısını ve modüller arası mantıksal veri akışını açıklar. Çalışmalar sentetik ve örnek veriler üzerinde yürütülmüş yerel PoC (Proof of Concept) mimarisidir.

---

## 1. Yüksek Seviyeli Mimari Katmanları

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Kullanıcı & Arayüz Katmanı                            │
│                 (Streamlit & Gradio Yerel Prototip Vitrini)                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                         Servis & API Katmanı                                │
│                     (FastAPI ASGI Application)                              │
│   ├── /api/v1/vision        (Görüntü analitiği & renk kuantizasyonu)         │
│   ├── /api/v1/retrieval     (Hibrit arama: BM25 + Cross-Encoder RRF)        │
│   ├── /api/v1/rag           (Citation destekli teknik soru-cevap)           │
│   └── /api/v1/generation    (Desen üretim ve analiz prototipi)              │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │                                      │
  Gerçekleştirilen │ Yerel İstekler         Gelecekteki   │ Dağıtık Senaryo
  Doğrulanmış PoC  │ (In-Process Sync)      Ölçekleme     │ (Opsiyonel Broker)
                   ▼                                      ▼
┌──────────────────────────────┐        ┌─────────────────────────────────────┐
│    Yerel PoC Çıkarım Hattı   │        │     Gelecekteki Asenkron Worker     │
│ ├── OpenCV Görüntü Analitiği │        │     (Kurumsal GPU & Dağıtık Kuyruk) │
│ ├── NumPy / Sklearn Analitik │        │ ├── SDXL Latent Diffusion Pipeline  │
│ └── Bi-Encoder & BM25 Arama  │        │ ├── Multi-ControlNet (Canny/Depth)  │
└──────────────┬───────────────┘        │ └── LoRA Adaptörleri & Celery       │
               │                        └──────────────────┬──────────────────┘
               │                                           │
┌──────────────▼───────────────────────────────────────────▼──────────────────┐
│                             Veri Katmanı                                    │
│ ├── Yerel / Bellek İçi Vektör İndeksleri & Metadata Filtreleme              │
│ ├── Dosya Sistemi (Sentetik Desen Çıktıları, Maskeler, Test Raporları)      │
│ └── Sentetik Tekstil & Teknik Doküman Koleksiyonu (0 Gerçek Firma Verisi)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **Mimari Kapsam Ayrımı (PoC vs. Gelecekteki Entegrasyon):**
> - **Gerçekleştirilen PoC:** Sol kolda yer alan yerel Python/FastAPI/OpenCV/Scikit-learn/PyTorch bileşenleridir. Tamamen yerel bellek ve disk üzerinde harici sunucuya ihtiyaç duymadan çalışır ve test edilir.
> - **Gelecekteki Entegrasyon Olasılığı:** Sağ kolda yer alan Celery/Redis/dağıtık GPU kuyruğu, fabrikanın olası bir gelecekteki kurumsal altyapı dönüşümünde sisteme nasıl eklenebileceğini gösteren kuramsal mimari senaryodur; staj süresince canlı üretim hattına bağlanmamıştır.

---

## 2. Modüler Fazların Mimari Rolleri

### Faz 1: Problem, Veri ve Geliştirme Temelleri (Day 01 – 08)
- **Rol:** Firma ve çalışma ortamının tanınması, veri modelleme, tip korumalı veri sözleşmeleri (Pydantic v2), çok kaynaklı veri alma (ETL/Pandas), veri kalitesi profillemesi, NumPy vektörizasyonu, uzaklık/benzerlik metrikleri ve keşifsel veri analizi (EDA).
- **Sözleşme:** Her model net girdi/çıktı şemasına sahiptir; bellek ve işlemci sınırları önceden analiz edilir.

### Faz 2: Bilgisayarlı Görü (Day 09 – 15)
- **Rol:** OpenCV görüntü ön işleme, kamera açısı ve perspektif bozulmalarını homografi matrisi ile düzeltme, CIELAB uzayında algısal renk farkı ($\Delta E^*$) ve K-Means baskın renk paleti çıkarma, morfoloji, klasik segmentasyon ve birleşik görsel öznitelik çıkarımı.
- **Sözleşme:** Piksel manipülasyonu salt RGB kanal farklarına bırakılmaz; algısal insan gözü hassasiyeti ve renk kısıtları gözetilir.

### Faz 3: Klasik Makine Öğrenmesi (Day 16 – 21)
- **Rol:** Sentetik iplik ve dokuma telemetrisi üzerinde Lojistik Regresyon, Karar Ağaçları, Random Forest, XGBoost, LightGBM ve SVM algoritmaları ile ikili ve çok sınıflı kalite sınıflandırması, dengesiz veri optimizasyonu, maliyet duyarlı eşik ayarı ve gözetimsiz kümeleme/boyut indirgeme (PCA, t-SNE, K-Means, DBSCAN).
- **Sözleşme:** Model başarımı tek başına Accuracy ile ölçülmez; dengesiz veri koşullarında PR-AUC, Recall ve maliyet matrisi ($Cost = 10 \cdot FN + 1 \cdot FP$) esas alınır.

### Faz 4: Retrieval ve RAG Temelleri (Day 22 – 27)
- **Rol:** Kelime bazlı arama (BM25) ile semantik yoğun aramanın (Bi-Encoder) zayıflıklarını Reciprocal Rank Fusion (RRF) ile giderme, doküman chunking yöntemleri, HNSW vektör indeksleme ve Ragas metrikleri ile RAG doğrulama.
- **Sözleşme:** Getirme başarısızlığı ile üretim başarısızlığı birbirinden ayrılır; Ragas metrikleri ile nesnel biçimde ölçülür.

### Faz 5: Görsel Üretim ve Analiz PoC (Day 28 – 30)
- **Rol:** SDXL omurgası ile yapılandırılmış prompt mühendisliği (6 alan), seed ve varyasyon denemeleri, K-Means renk analitiği, CIELAB $\Delta E^*$, ayna simetrisi ve otokorelasyon ile tekrar yapısı, kenar sürekliliği ve CNN embedding benzerliği ile birleşik yerel prototip oluşturulması.
- **Sözleşme:** Üretilen görsel varyasyonlarının analizi nesnel sayısal ölçümlerle desteklenir; otomatik metriklerin estetik yargı veya kesin üretilebilirlik garantisi oluşturamayacağı sınırları belirtilir.

### Faz 6: Doküman RAG, Servisleştirme ve Kapanış (Day 31 – 40)
- **Rol:** PDF/DOCX/Markdown sentetik teknik dokümanlarının ayrıştırılması, hibrit doküman arama ve ölçüm, kaynaklı cevap üretimi (`[S1]`, `[S2]`), Cross-Encoder reranking, Query Rewrite & HyDE, Pydantic ile grounded cevap ve İSG guardrails, FastAPI yerel REST servisi ve Streamlit arayüzü, ONNX INT8 kuantizasyon ve CPU benchmark, kümülatif test ve kapanış değerlendirmesi.
- **Sözleşme:** Gerçek canlı SCADA/PLC veya fabrika deployment iddiası taşımayan, sentetik senaryolarla test edilmiş, sınırları açıkça belgelenmiş yerel bir PoC ve portföy sürümü olarak mühürlenir.
