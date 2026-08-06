# Merinos Industrial Vision CLI Toolkit (Day 15 — Mini Project)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Phase](https://img.shields.io/badge/Phase%202-Final%20Release-orange.svg)]()
[![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-red.svg)](https://github.com/seydivakkas)
[![Tests](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen.svg)]()

> **Merinos Halı Sanayi ve Ticaret A.Ş. — Gaziantep Dokuma Tesisleri**  
> Faz 2: Endüstriyel Görüntü İşleme nihai üretim sürümü ve birleşik CLI kalite kontrol paketi.

---

## 1. Genel Bakış ve Mimari

Bu paket, Faz 2 boyunca geliştirilen 8 bağımsız bilgisayarlı görü modülünü (Day 07 — Day 14) endüstriyel üretim hattında tek noktadan yönetilebilir bir CLI araç setinde (`merinos-vision`) birleştirmektedir.

```mermaid
flowchart TD
    Raw[Ham Halı Kamerası / Görüntü Dosyası] --> S1[Aşama 1: Perspektif Düzeltme & Homografi\nDay 10]
    S1 --> S2[Aşama 2: K-Means Dominant Palet & CIEDE2000\nDay 08 & 09]
    S1 --> S3[Aşama 3: Morfolojik Kusur Tespiti\nDay 11]
    S1 --> S4[Aşama 4: Kenar & Bordür Paralellik Analizi\nDay 12]
    S1 --> S5[Aşama 5: Havza / Otsu Jakar Segmentasyonu\nDay 13]
    S1 --> S6[Aşama 6: Çok Modlu Öznitelik Füzyonu ORB/GLCM/HSV\nDay 14]
    
    S1 & S2 & S3 & S4 & S5 & S6 --> VerdictEngine[Kalite Karar Motoru\nACCEPT / WARNING / REJECT]
    VerdictEngine --> Report[Yapılandırılmış JSON Raporu]
    VerdictEngine --> HUD[Gerçek Zamanlı HUD Görsel Kaplama]
```

---

## 2. CLI Komutları ve Kullanım

### 1) Sentetik Test Fikstürleri Üretimi
```bash
python -m day15.mini_project.src.cli generate-fixtures --output-dir day15/mini_project/fixtures
```
*Çıktı:* `perfect_carpet.png`, `defective_carpet.png`, `skewed_carpet.png`, `faded_carpet.png`.

### 2) Uçtan Uca Halı Kalite Muayenesi (Inspect)
```bash
python -m day15.mini_project.src.cli inspect \
  --image day15/mini_project/fixtures/perfect_carpet.png \
  --carpet-id "MERINOS-PERFECT-001" \
  --output-hud day15/mini_project/fixtures/hud_perfect.png \
  --output-json day15/mini_project/fixtures/report_perfect.json
```

### 3) Faz 2 Modül Başarım Kıyaslaması (Benchmark)
```bash
python -m day15.mini_project.src.cli benchmark --iterations 10 --output-json day15/mini_project/fixtures/benchmark_manifest.json
```

### 4) Sürüm ve Sağlık Bilgisi (Release-Info)
```bash
python -m day15.mini_project.src.cli release-info
```

---

## 3. Test ve Doğrulama

Birim ve entegrasyon testlerini çalıştırmak için:
```bash
python -m pytest day15/mini_project/tests/ -v
```

---

## 4. Lisans

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
