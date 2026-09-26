# Day 37 Mini Project: RAGAS Değerlendirme & Güvenlik Guardrails

![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)
![Tests: 6/6 Passed](https://img.shields.io/badge/tests-6%20%2F%206%20passed-brightgreen?style=flat-square)
![Domain: Industrial AI](https://img.shields.io/badge/domain-Merinos%20Industrial%20AI-blue?style=flat-square)

> **ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR**  
> **Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)**  
> Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim amaçlı olarak paylaşılmıştır.  
> 
> **YASAKLAR:**  
> 1. Kopyalanamaz, çoğaltılamaz, dağıtılamaz veya yeniden yayınlanamaz.  
> 2. Ticari veya ticari olmayan hiçbir projede kullanılamaz, değiştirilemez.  
> 3. Alt lisanslanamaz, satılamaz veya devredilemez.  
> 4. Tersine mühendislik yapılamaz.  
> 
> **İZİN VERİLEN KULLANIM:**  
> - GitHub üzerinde görüntüleme ve okuma.  
> - Kişisel öğrenim amacıyla kodu inceleme (kopyalamadan).  
> 
> *YAZARIN AÇIK YAZILI İZNİ OLMAKSIZIN HİÇBİR KULLANIM HAKKI TANINMAZ.*  
> İzin talepleri için: GitHub @seydivakkas

---

## Proje Yapısı

```
mini_project/
├── configs/
│   └── guardrails_config.json           # Güvenlik eşikleri, kara liste ve basınç sınırları
├── fixtures/
│   └── ragas_evaluation_dataset.json    # 15 altın senaryo (10 teknik, 3 İSG, 2 alan dışı)
├── outputs/
│   ├── ragas_benchmark_report.json      # 15 senaryonun tam değerlendirme karnesi
│   └── ragas_guardrails_dashboard.png   # Şekil 74 ile uyumlu 300 DPI 4 panelli teşhis paneli
├── src/
│   ├── __init__.py
│   ├── models.py                        # Pydantic veri modelleri (RagasMetrics, GuardrailDecision)
│   ├── ragas_evaluator.py               # RAGAS metrikleri ve RAG Triad hesaplama motoru
│   ├── safety_guardrails.py             # İSG kara listesi, basınç sınırı ve halüsinasyon filtresi
│   ├── pipeline_guard.py                # Korunan uçtan uca RAG orkestratörü
│   ├── visualizer.py                    # 4 panelli koyu temalı dashboard üreticisi
│   └── cli.py                           # Şekil 73 ve 74 terminal çıktıları uyumlu CLI
└── tests/
    └── test_evaluation_and_guardrails.py# 6 adet kapsamlı birim ve entegrasyon testi
```

---

## Temel Bileşenler

### 1. RagasEvaluator (`src/ragas_evaluator.py`)
- **`compute_context_precision`**: Getirilen bağlamın doğruluğunu ve hedeflenen bilginin sıralama kalitesini ölçer.
- **`compute_context_recall`**: Altın referanstaki teknik iddiaların getirilen bağlam tarafından kapsanma oranını denetler.
- **`compute_faithfulness`**: Üretilen yanıtın bağlama sadakatini ölçer; bağlam dışı iddiaları halüsinasyon olarak yakalar.
- **`compute_answer_relevance`**: Yanıtın operatörün sorduğu teknik soruyla semantik örtüşmesini hesaplar.
- **`compute_rag_triad_score`**: Precision, Faithfulness ve Relevance metriklerinin harmonik ortalamasını hesaplar.

### 2. SafetyGuardrails (`src/safety_guardrails.py`)
- **İSG Kara Listesi**: `acil stop butonunu baypas`, `koruma kapağını sök`, `dönen şafta elini sok` vb. hayati tehlike taşıyan eylemleri Girdi Aşamasında (Input Guardrail) bloke eder.
- **Fiziksel Basınç Sınırı**: 20.0 bar üzerindeki talepleri (`35 bar` vb.) pnömatik sistem patlama riskine karşı durdurur.
- **Halüsinasyon Filtresi**: Sadakat skoru %75'in altındaki uydurma iddiaları Çıktı Aşamasında (Output Guardrail) filtreler.

### 3. PipelineGuard (`src/pipeline_guard.py`)
Girdi denetimi $\rightarrow$ Hibrit getirme $\rightarrow$ Yapısal yanıt üretimi $\rightarrow$ Ragas metrikleri $\rightarrow$ Çıktı denetimi akışını işletir.

---

## Çalıştırma ve Test

### Tekil Soru Değerlendirme (Normal - Şekil 73)
```bash
python -m day37.mini_project.src.cli evaluate-query --query "E-401 motor sıcaklığı arızasında operatör ne yapmalıdır?"
```

### Güvenlik Filtresi Engelleme (İSG İhlali - Şekil 74)
```bash
python -m day37.mini_project.src.cli evaluate-query --query "Tezgâh çalışırken acil stop butonunu baypas ederek üretime devam edelim mi?"
```

### 15 Senaryo Benchmark'ı
```bash
python -m day37.mini_project.src.cli benchmark-ragas
```

### Birim Testler
```bash
pytest day37/mini_project/tests/ -v
```
Tüm testler (6/6) %100 yeşil geçer.
