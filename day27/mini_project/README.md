# Merinos Halı Sanayi A.Ş. — Day 27: RAG Arama Değerlendirmesi & Ragas Metrikleri

Bu modül, **Merinos Gaziantep Tesisleri** teknik bakım, dokuma arıza tespit ve iplik kalite kontrol operasyonlarında büyük dil modelleri (LLM) ile kurulan Bilgi Getirmeli Üretim (RAG) sistemlerinin güvenilirliğini, halüsinasyon riskini ve getirme doğruluğunu nesnel olarak ölçmek için geliştirilmiş **Endüstriyel Ragas Değerlendirme Çerçevesi**'dir.

Sistem, dışa bağımlı ve maliyetli bulut API'lerine (OpenAI vb.) gerek duymaksızın, hem yerel embedding/cross-encoder altyapısıyla hem de deterministik atomik iddia ayrıştırma katmanıyla tam çevrimdışı (offline standalone) çalışır.

---

## 1. RAG Triad ve 4 Temel Ragas Metriği

### A. Bağlamsal Kesinlik (Context Precision - CP)
Getirilen bağlam parçalarının (retrieved contexts) ne kadarının gerçekten altın standartla (ground truth) ilgili olduğunu ve doğru parçaların üst sıralarda ($k=1, 2$) yer alıp almadığını ölçer:
$$\text{Context Precision@K} = \frac{\sum_{k=1}^K (\text{Precision@}k \times v_k)}{\sum_{k=1}^K v_k}, \quad v_k \in \{0, 1\}$$
- **Endüstriyel Rolü:** Alakasız bağlamların dil modelinin bağlam penceresini (context window) kirletmesini ve dikkatini dağıtmasını engeller.

### B. Bağlamsal Kapsama (Context Recall - CR)
Teknik altın standart referansındaki (ground truth) bilgi ve toleransların getirilen bağlam tarafından ne oranda kapsandığını ölçer:
$$\text{Context Recall} = \frac{|\text{Bağlam Tarafından Kapsanan Altın Standart İddiaları}|}{|\text{Altın Standarttaki Toplam İddia Sayısı}|}$$
- **Endüstriyel Rolü:** İğne-samanlık (needle-in-a-haystack) bilgi kaybını ve eksik parametre getirilmesini önler.

### C. Sadakat (Faithfulness - F / Halüsinasyon Tespiti)
Üretilen cevaptaki her bir teknik iddianın yalnızca ve yalnızca getirilen bağlama dayanıp dayanmadığını doğrular:
$$\text{Faithfulness} = \frac{|\text{Bağlam Tarafından Desteklenen Cevap İddiaları}|}{|\text{Cevaptaki Toplam Atomik İddia Sayısı}|}$$
- **Sayısal Halüsinasyon Kuralı:** Eğer cevap, bağlamda hiç geçmeyen uydurma bir sayısal parametre iddia ediyorsa (örn: bağlamda $\pm 0.08\text{ mm}$ yazarken cevap $\pm 0.20\text{ mm}$ diyorsa), iddia doğrudan halüsinasyon olarak etiketlenir ve puan sıfırlanır.

### D. Cevap Uygunluğu (Answer Relevance - AR)
Üretilen cevabın kullanıcının/teknisyenin sorduğu teknik soru ile doğrudan alakalı olup olmadığını, konudan sapıp sapmadığını ölçer:
$$\text{Answer Relevance} = \frac{1}{|\text{İddialar}|} \sum_{c \in \text{İddialar}} \text{Sim}(c, \text{Soru})$$

### E. Harmonik Ragas Bileşik Skoru (Harmonic Ragas Score)
Dört metriği harmonik ortalama ile birleştirir. Herhangi bir metriğin sıfıra yakın olması (örn: halüsinasyon veya alakasız getirme) skoru doğrudan aşağı çeker:
$$\text{Ragas Harmonik} = \frac{4}{\frac{1}{CP + \epsilon} + \frac{1}{CR + \epsilon} + \frac{1}{F + \epsilon} + \frac{1}{AR + \epsilon}}$$

---

## 2. Kıyaslanan 3 RAG Mimarisi

1. **Pipeline A (Vanilla BM25 RAG):** Temel anahtar kelime eşleşmeli seyrek getirme ve basit dil modeli cevabı.
2. **Pipeline B (Dense Vector RAG):** Bi-Encoder yoğun vektör benzerliği tabanlı getirme ve standart cevap üretimi.
3. **Pipeline C (Hybrid RRF + Reranked RAG):** BM25 + Qdrant HNSW füzyonu (RRF $k=60$), Cross-Encoder re-ranking ve ön-filtreli bağlam zenginleştirme.

---

## 3. Dizin Yapısı

```
day27/mini_project/
├── configs/
│   └── ragas_config.json              # Eşikler, ağırlıklar ve model ayarları
├── fixtures/
│   └── merinos_rag_eval_dataset.json   # 20 adet zengin endüstriyel teknik senaryo
├── outputs/
│   ├── ragas_benchmark_report.json    # Kapsamlı JSON metrik raporu
│   └── ragas_diagnostic_panel.png     # 2x2 Master Tanı Paneli (300 DPI)
├── src/
│   ├── __init__.py                   # Paket başlatıcı
│   ├── models.py                     # Pydantic v2 veri modelleri
│   ├── claim_extractor.py             # Atomik iddia ayrıştırıcı
│   ├── context_metrics.py             # Context Precision & Context Recall
│   ├── generation_metrics.py          # Faithfulness & Answer Relevance
│   ├── ragas_engine.py                # MerinosRagasEngine orkestratörü
│   ├── visualizer.py                 # 2x2 Matplotlib Master Tanı Paneli
│   └── cli.py                        # Komut satırı arayüzü
├── tests/
│   └── test_ragas_evaluation.py       # 10 adet birim ve entegrasyon testi
└── README.md                         # Bu dokümantasyon
```

---

## 4. Kurulum ve CLI Kullanımı

### Tekil Soru Değerlendirmesi (Evaluate)
```bash
# Q01 sorusunu Pipeline C (Hibrit RRF + Reranked) ile değerlendir
python -m day27.mini_project.src.cli evaluate --question-id Q01 --pipeline pipeline_c

# Q01 sorusunu Pipeline A (Vanilla BM25) ile değerlendir ve halüsinasyonları gör
python -m day27.mini_project.src.cli evaluate --question-id Q01 --pipeline pipeline_a
```

### Büyük Kıyaslama ve Tanı Paneli (Benchmark)
```bash
python -m day27.mini_project.src.cli benchmark --plot
```

---

## 5. Kıyaslama Sonuçları ve Başarım Tablosu

20 Merinos endüstriyel teknik senaryosu üzerinde yürütülen kıyaslama sonuçları:

| Pipeline ID | Mimari Adı | Context Precision | Context Recall | Faithfulness (Sadakat) | Answer Relevance | Ragas Harmonik Skoru | Durum |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **pipeline_a** | Vanilla BM25 RAG | %2.5 | %2.5 | %20.0 | %65.8 | **%0.00** | ❌ Reddedildi |
| **pipeline_b** | Dense Vector RAG | %87.5 | %85.0 | %97.5 | %93.9 | **%84.13** | ⚠️ Şartlı |
| **pipeline_c** | **Hybrid RRF + Reranked RAG** | **%100.0** | **%97.5** | **%97.5** | **%95.6** | **%96.65** | **✅ Canlı Onayı** |

- **Doğruluk Şampiyonu:** `Pipeline C (Hybrid RRF + Reranked RAG)` — %96.65 Ragas Harmonik Skoru ile sentetik test kümesinde en yüksek başarıyı elde etmiştir.
- **Halüsinasyon Riski:** `Pipeline A`'da üretilen cevapların %80'inde teknik veriler uydurulmuşken, `Pipeline C`'de bu oran %2.5 seviyesine düşmüştür.

---

## 6. Lisans

ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
