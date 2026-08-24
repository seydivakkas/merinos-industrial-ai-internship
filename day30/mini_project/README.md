# Merinos Day 30 Mini Proje — Tümleşik Halı Desen Üretim ve Analiz Boru Hattı

Bu paket, **Merinos Halı Sanayi ve Ticaret A.Ş.** için geliştirilen uçtan uca görüntü üretim, analiz ve görsel benzerlik arama motorunu içerir.

[![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)](https://github.com/seydivakkas)
[![Tests: 16/16 Passing](https://img.shields.io/badge/tests-16%2F16%20passed-brightgreen.svg?style=flat-square)](file:///tests)

---

## Proje Yapısı

```text
day30/mini_project/
├── configs/
│   └── pipeline_config.json                # Eşikler, küme sayısı ve çözünürlük ayarları
├── fixtures/
│   ├── sample_design_briefs.json           # Klasik, modern ve geçersiz test brifleri
│   ├── reference_carpet_catalog.json       # CNN benzerlik araması referans kataloğu
│   └── merinos_yarn_palette.json           # Cağlık bobin fiziksel renk paleti (Pantone / Lab)
├── src/
│   ├── __init__.py                         # Dışa aktarılan modüller
│   ├── models.py                           # Pydantic v2 veri modelleri ve sınır raporu
│   ├── prompt_synthesizer.py               # Day 29 Nano-LLM ve BPE tokenizer entegrasyonu
│   ├── generator_engine.py                 # Deterministik halı desen üretim motoru
│   ├── analyzer_engine.py                  # K-Means, CIEDE2000, Simetri ve Dikiş analizleri
│   ├── similarity_engine.py                # CNN Embedding ve Cosine Similarity arama motoru
│   ├── pipeline.py                         # Uçtan uca orkestrasyon ve hata yönetimi
│   ├── visualizer.py                       # 300 DPI 4-panelli master teşhis paneli üreticisi
│   └── cli.py                              # Komut satırı arayüzü
├── tests/
│   └── test_generation_analysis_pipeline.py# 16 birim ve entegrasyon testi
└── outputs/                                # Üretilen desenler, JSON raporlar ve grafikler
```

---

## Kurulum & Çalıştırma

### 1. Test Paketini Koşturma
```powershell
python -m pytest day30/mini_project/tests/ -v
```

### 2. Örnek Brif ile Boru Hattını Çalıştırma
```powershell
python -m day30.mini_project.src.cli run --brief-id BRF-CLS-01
```

### 3. Özel Parametrelerle Çalıştırma
```powershell
python -m day30.mini_project.src.cli run \
  --style "Klasik Saray" \
  --motif "Barok Madalyon" \
  --primary-color "Krem" \
  --secondary-color "Osmanlı Kırmızısı" \
  --border-type "Geniş su bordürü" \
  --symmetry "BILATERAL_AND_VERTICAL" \
  --seed 1042
```

### 4. Teknik Sınırlar Raporunu Görüntüleme (Staj Defteri Yaprak 60)
```powershell
python -m day30.mini_project.src.cli report-limitations
```

---

## Lisans
Özel Lisans — Tüm Hakları Saklıdır. Copyright (c) 2026 Seydi Eryılmaz (@seydivakkas).
İzinsiz kopyalanamaz, çoğaltılamaz veya dağıtılamaz.
