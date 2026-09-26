# Merinos Industrial RAG API & Streamlit Operatör Konsolu (Mini Proje)

![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)
![Stack: FastAPI + Streamlit](https://img.shields.io/badge/stack-FastAPI%20%2B%20Streamlit-009688?style=flat-square)
![Tests: 100% Passed](https://img.shields.io/badge/tests-9%20%2F%209%20passed-brightgreen?style=flat-square)

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

## Proje Mimarisi

Bu mini proje, Merinos Gaziantep Halı Fabrikası dokuma salonları için geliştirilen RAG (Retrieval-Augmented Generation) altyapısını;
1. **FastAPI REST API Servisi** (`src/app.py`),
2. **Streamlit SCADA Operatör Konsolu** (`src/ui.py`),
3. **Endüstriyel RAG Servis Katmanı** (`src/service.py`),
4. **300 DPI Sistem Dashboard'u Görselleştiricisi** (`src/visualizer.py`),
5. **Yük Testi ve CLI Yönetim Aracı** (`src/cli.py`)
bileşenleriyle kurumsal üretim seviyesine taşır.

---

## Dizin Yapısı

```
mini_project/
├── README.md
├── configs/
│   └── api_config.json
├── src/
│   ├── __init__.py
│   ├── app.py           # FastAPI REST API ve Swagger UI (Şekil 75)
│   ├── service.py       # IndustrialRagService iş mantığı ve orkestrasyon
│   ├── models.py        # Pydantic DTO şemaları (OperatorQuery, CitationDto vb.)
│   ├── ui.py            # Streamlit Dokuma Salonu Operatör Konsolu (Şekil 76)
│   ├── visualizer.py    # 300 DPI Sistem Dashboard'u çizicisi
│   └── cli.py           # CLI yönetim ve benchmark çalıştırıcısı
├── tests/
│   └── test_api_and_ui.py
└── outputs/
    ├── api_benchmark_report.json
    └── api_system_dashboard.png
```

---

## Uç Noktalar (Endpoints)

| Uç Nokta | Metot | Açıklama |
|---|---|---|
| `/api/v1/process-operator-query` | `POST` | Şekil 75 uyumlu operatör teknik arıza / bakım sorgulama uç noktası. |
| `/api/v1/query` | `POST` | Yapılandırılmış operatör yanıtı ve Ragas metrikleri dönen standart uç nokta. |
| `/api/v1/guardrails/check` | `POST` | Hızlı İSG kontrolü (erken kesme ile < 1 ms). |
| `/api/v1/health` | `GET` | API ve bilgi tabanı canlılık ve sağlık durumu. |
| `/api/v1/metrics` | `GET` | Canlı sistem metrikleri (toplam sorgu, gecikme, engelleme oranı). |
| `/api/v1/looms` | `GET` | Fabrika tezgâh envanteri listesi. |
| `/api/v1/docs` | `GET` | Etkileşimli OpenAPI Swagger dokümantasyonu. |

---

## Çalıştırma Talimatları

### 1. Testleri Koşma
```bash
pytest day38/mini_project/tests/ -v
```

### 2. FastAPI Sunucusunu Başlatma
```bash
python -m day38.mini_project.src.cli serve-api --host 127.0.0.1 --port 8000
```
Swagger UI: `http://127.0.0.1:8000/api/v1/docs`

### 3. Streamlit Konsolunu Başlatma
```bash
python -m day38.mini_project.src.cli serve-ui --port 8501
```
Web Arayüzü: `http://localhost:8501`

### 4. Benchmark ve Dashboard Üretimi
```bash
python -m day38.mini_project.src.cli benchmark-api
```
