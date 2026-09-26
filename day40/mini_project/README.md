# Day 40 Mini Project — Final Test, Dokümantasyon ve Staj Değerlendirmesi

![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)
![Tests](https://img.shields.io/badge/tests-8%20%2F%208%20passed-brightgreen?style=flat-square)
![Status: PoC Completed](https://img.shields.io/badge/status-PoC%20Completed-blue?style=flat-square)

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

---

## Proje Özeti

Bu mini proje, 40 günlük staj maratonunda geliştirilen örnek yapay zekâ modüllerini (Bilgisayarlı Görü, Kestirimci Analiz, Endüstriyel RAG & Guardrails, Yerel Optimizasyon) tek bir master orkestrasyon motoru altında birleştirerek yerel ortamda kapsamlı değerlendirme, kümülatif test ve kapanış raporlamasını gerçekleştirir.

Platform, sentetik tezgâh telemetri verilerini (sıcaklık, basınç), örnek hata kodlarını ve operatör sorgularını yerel çok modlu (multi-modal) mantıkla işleyerek kök neden analizi ve adım adım SOP eylem planı simülasyonu üretir. Çift katmanlı İSG kural denetimi ile güvenli olmayan komutları yerel seviyede filtreler ve staj boyunca geliştirilen bileşenlerin teknik performansını özetleyen staj kapanış karnesini oluşturur.

> **Önemli Not:** Tüm analizler sentetik ve çalışma amacıyla hazırlanmış örnek veriler üzerinde yürütülen yerel öğrenme / PoC çalışmalarıdır. Canlı fabrika veya gerçek SCADA bağlantısı içermez.

---

## Dizin Yapısı

```
mini_project/
├── configs/
│   └── master_platform_config.json                 # Platform alt sistemleri ve örnek parametre eşikleri
├── outputs/
│   ├── internship_final_evaluation_report.json     # 40 günlük detaylı JSON staj kapanış karnesi
│   └── master_platform_dashboard.png               # 300 DPI 4 panelli kurumsal teşhis dashboard'u
├── src/
│   ├── __init__.py
│   ├── models.py                                   # Pydantic v2 DTO ve veri sözleşmesi modelleri
│   ├── master_platform.py                          # Modülleri birleştiren ana platform orkestratörü
│   ├── final_evaluator.py                          # Staj kümülatif karne ve parametrik analiz motoru
│   ├── visualizer.py                               # 300 DPI karanlık tema (#0e1117) dashboard üreticisi
│   └── cli.py                                      # diagnose, health, final-report komut arayüzü
└── tests/
    └── test_master_platform_final.py               # 8 adet birim ve entegrasyon testi
```

---

## Hızlı Başlangıç

### 1. Testleri Koşturma (Şekil 80)
```bash
pytest day40/mini_project/tests/ -v
```

### 2. Örnek Çok Modlu Tezgâh Arıza Teşhisi Simülasyonu (Şekil 79)
```bash
python -m day40.mini_project.src.cli diagnose --loom-id TEZGAH-01 --error-code E-401 --motor-temp 87.5 --pressure 13.5 --vision-defect
```

### 3. Platform Sistem Sağlık Taraması (Şekil 80)
```bash
python -m day40.mini_project.src.cli health
```

### 4. 40 Günlük Kapsamlı Staj ve Parametrik Analiz Raporu (Şekil 80)
```bash
python -m day40.mini_project.src.cli final-report --total-looms 120
```

---

## Sentetik Simülasyon ve PoC Değerlendirme Çıktıları

- **Kümülatif Test Başarım Oranı**: %100 (218 / 218 test yeşil)
- **Modüler Entegrasyon Durumu**: 5 alt sistem ve 4 modül başarıyla koordine edilmiştir.
- **Yerel Çıkarım Gecikmesi**: 0.63 ms (Yerel CPU ONNX Dynamic INT8 çıkarımı)
- **Platform Bellek Tüketimi**: 73.2 MB (Düşük bellekli yerel ortamlarla uyumlu)
- **İSG Korkuluk Başarımı**: Emniyet kuralı ihlalleri yerel kurallarla < 1 ms sürede başarıyla engellenmiştir.
- **Teorik Parametrik Model**: 120 tezgâhlık varsayımsal fabrika ölçeğinde teorik duruş ve maliyet azaltma senaryosu matematiksel olarak modellenmiştir.
- **Staj Değerlendirme Kararı**: `POC_TAMAMLANDI`
