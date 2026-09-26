# Merinos Industrial AI Internship Portfolio

[![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg?style=flat-square)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-ee4c2c.svg?style=flat-square)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat-square)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square)](https://www.docker.com/)

Bu repository, **Bilgisayar Mühendisliği Endüstriyel Yapay Zeka Staj Programı** kapsamında 40 günlük aşamalı bir mühendislik müfredatını içeren kapsamlı portföy projesidir. Çalışmalar sentetik, çalışma amacıyla hazırlanmış veya açık veriler üzerinde yürütülen yerel öğrenme / PoC (Proof of Concept) çalışmalarıdır.

---

## Müfredat ve Faz Mimarisi

Repository, 40 günlük resmi staj defteri planı doğrultusunda 6 aşamalı modüler mühendislik fazı olarak organize edilmiştir:

```
[Faz 1: Problem, Veri & Geliştirme Temelleri] ──► [Faz 2: Bilgisayarlı Görü] ──► [Faz 3: Klasik Makine Öğrenmesi]
                                                                                               │
[Faz 6: Doküman RAG, Servisleştirme & Kapanış] ◄── [Faz 5: Görsel Üretim & Analiz PoC] ◄───────┴── [Faz 4: Retrieval & RAG Temelleri]
```

### Faz Özeti

| Faz | Odak Alanı | Günler | Temel Konular & Kapsam |
| :--- | :--- | :--- | :--- |
| **Faz 1** | Problem, Veri ve Geliştirme Temelleri | Day 01 – Day 08 | Firma ve çalışma ortamının tanınması, veri modelleme, problem tanımı, Python geliştirme ortamı & veri sözleşmesi, Pandas veri hattı & kalitesi, NumPy vektörel hesaplama, uzaklık & benzerlik metrikleri, keşifsel veri analizi (EDA). |
| **Faz 2** | Bilgisayarlı Görü | Day 09 – Day 15 | OpenCV temelleri ve görüntü ön işleme, renk uzayları ve renk farkı ($\Delta E^*$), K-Means ile baskın renk paleti, perspektif düzeltme & homografi, morfolojik işlemler & kenar/çizgi tespiti, klasik segmentasyon, görsel özellik çıkarımı & entegrasyon. |
| **Faz 3** | Klasik Makine Öğrenmesi | Day 16 – Day 21 | İkili sınıflandırma temelleri (Lojistik Regresyon), çok sınıflı sınıflandırma, Decision Tree & Random Forest, Gradient Boosting modelleri (XGBoost/LightGBM), Support Vector Machine (SVM), gözetimsiz öğrenme & boyut indirgeme (PCA, t-SNE, K-Means, DBSCAN). |
| **Faz 4** | Retrieval ve RAG Temelleri | Day 22 – Day 27 | Metinlerin sayısal temsili & BM25, vektör tabanlı metin arama (Bi-Encoder), hibrit retrieval & RRF füzyonu, doküman chunking yöntemleri, vektör indeksleme yöntemleri, RAG temelleri & değerlendirme (Ragas). |
| **Faz 5** | Görsel Üretim ve Analiz PoC | Day 28 – Day 30 | Kontrollü görsel üretim (SDXL prompt/seed alanları), üretilen görsellerin sayısal analizi (K-Means, CIELAB $\Delta E^*$, simetri, süreklilik, CNN embedding & Top-K benzerlik), görsel üretim ve analiz mini prototipi. |
| **Faz 6** | Doküman RAG, Servisleştirme ve Kapanış | Day 31 – Day 40 | Doküman alma & ön işleme, hibrit doküman arama & ölçüm, kaynaklı cevap üretimi, reranking & context yönetimi, query rewrite & HyDE, yapılandırılmış ve grounded cevap, RAG değerlendirmesi & guardrail, yerel API servisi & basit arayüz, ONNX kuantizasyon & yerel benchmark, final test & staj değerlendirmesi. |

---

## Günlük Geliştirme Kontratı

Her gün klasörü (`dayXX/`) kesinlikle aşağıdaki hiyerarşiyi uygular:

```
dayXX/
├── README.md                     # Kurumsal mühendislik raporu standardı
├── dayXX_<topic>.ipynb           # 10 bölümlü teorik/deneysel bağımsız eğitim notebook'u
└── mini_project/                 # Yerel, testli, modüler PoC Python paketi
    ├── README.md                 # Mini proje mimarisi ve çalıştırma rehberi
    ├── src/                      # Tip korumalı, loglamalı modüler PoC kodu
    ├── tests/                    # Pytest birim ve entegrasyon testleri
    ├── configs/                  # Dışsal parametreler ve şemalar
    └── outputs/                  # Deney logları ve test raporları
```

---

## Veri, Deney ve Yapay Zeka İlkeleri

Ayrıntılı veri ve sistem politikası için [DATA_REALITY_POLICY.md](docs/DATA_REALITY_POLICY.md) dokümanına bakınız.

- **Veri Gizliliği:** Bu depoda hiçbir özel firma verisi, iç kimlik bilgisi veya telifli doküman kullanılmaz. Tüm çalışmalar sentetik, çalışma amacıyla hazırlanmış veya açık verilerle yürütülür.
- **Sistem Kapsamı:** Çıktılar yerel öğrenme / PoC (Proof of Concept) niteliğindedir; canlı fabrika, üretim hattı veya SCADA/PLC sistemlerine doğrudan bağlı değildir.
- **Deneysel Dürüstlük:** Hiçbir başarım metriği (doğruluk, gecikme, bellek tüketimi) uydurulmaz. Gerçekte çalıştırılmamış testler için açıkça `NOT_EXECUTED` ibaresi düşülür.
- **Mühendislik Gerçekçiliği:** Model çıktıları mutlak gerçek kabul edilmez; RAG sistemlerinde retrieval ve generation başarımları ayrı ayrı ölçülür. Üretilen halı desenlerinde otomatik metrikler mutlak estetik veya üretilebilirlik garantisi olarak sunulmaz.

---

## Hızlı Başlangıç

### 1. Bağımlılıkların Kurulumu
```bash
# Sanal ortam oluşturma ve etkinleştirme
python -m venv .venv
source .venv/bin/activate  # Windows için: .venv\Scripts\activate

# Bağımlılıkları yükleme
pip install -r requirements.txt  # veya: poetry install
```

### 2. Ortam Değişkenleri
```bash
cp .env.example .env
```

### 3. Testlerin Çalıştırılması
```bash
pytest
```

---

## Lisans

Bu proje **özel lisans** ile korunmaktadır. Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas). Tüm hakları saklıdır. Ayrıntılar için [LICENSE](LICENSE) dosyasına başvurunuz.
