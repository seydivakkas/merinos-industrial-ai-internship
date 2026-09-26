# Day 01 — Firma ve Çalışma Ortamının Tanınması

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Firma ve Çalışma Ortamının Tanınması (Yaprak 1 & 2)

---

## Goal
Bu ilk günde amaç, Merinos halı üretim işletmesinde bilgisayar mühendisliği uygulama alanlarını, üretim ortamında ortaya çıkan heterojen veri türlerini (sayısal sensör telemetrisi, görsel halı yüzeyi/desen görüntüleri, teknik bakım ve işletim dokümanları) ve veri modelleme gereksinimlerini analiz etmektir. İlk gün oryantasyon kapsamında; firma çalışma ortamının tanınması, veri modaliteleri taksonomisinin modellenmesi ve sentetik veri gözlem kataloğunun oluşturulması hedeflenmiştir.

---

## Engineer Research Assignment
- Kurumsal bir tekstil üretim tesisinde bilgisayar mühendisliği problemlerini (sayısal telemetri, bilgisayarlı görü ve teknik dokümantasyon analitiği) sınıflandırmak.
- Heterojen veri türlerinin (yapılandırılmış sensör verileri, yarı yapılandırılmış kataloglar ve yapılandırılmamış görsel/metin verileri) depolama ve işleme gereksinimlerini karşılaştırmak.
- Veri türlerini (`numerical`, `visual`, `textual`) tip güvenli şemalarla modelleyen bir gözlem kataloğu tasarlamak.
- Üretim ortamını riske atmadan sentetik ve örnek verilerle güvenli yerel geliştirme sınırlarını belirlemek ([`docs/DATA_REALITY_POLICY.md`](../docs/DATA_REALITY_POLICY.md)).

---

## Concepts
- **Endüstriyel Veri Modaliteleri (Modalities):**
  - **Sayısal (Numerical):** İplik gerginliği, tezgâh devri, fırın sıcaklığı gibi zaman serisi ve telemetri kayıtları.
  - **Görsel (Visual):** Halı dokuma yüzeyi kamera görüntüleri, örgü hataları ve desen motifleri.
  - **Metinsel (Textual):** Tezgâh bakım el kitapları, işletme standartları (SOP) ve arıza kayıtları.
- **Problem Alanları:** Kalite kontrol (defects), süreç izleme (monitoring), dokümantasyon asistanı (retrieval/RAG).
- **Tip Güvenliği ve Doğrulama:** Pydantic v2 ile veri varlıklarının çalışma zamanında doğrulanması.
- **Yerel PoC Sınırları:** Canlı SCADA ve üretim hatlarına müdahale etmeden, izole ortamda sentetik varlıklarla çalışma.

---

## Libraries
- `pathlib`: İşletim sisteminden bağımsız nesne yönelimli dosya yolu yönetimi.
- `pydantic` (v2): Çalışma zamanı veri şeması, tip güvenliği ve alan doğrulama.
- `pytest`: Otomatik birim test çatısı.
- `json`: Şema ve katalog serileştirme.

---

## Functions / Classes Studied
- `pydantic.BaseModel`, `pydantic.Field`
- `enum.Enum` (DataModality)
- `pytest.fixture`
- `json.dumps()`, `json.loads()`

---

## Notebook
- **Dosya:** [`day01_firma_ve_calisma_ortami.ipynb`](day01_firma_ve_calisma_ortami.ipynb)
- **Kapsam:** 10 standart bölüm:
  1. Problem: Üretim işletmesinde heterojen veri türlerinin varlığı
  2. Neden Önemli: Doğru veriye doğru aracın seçilmesi gerekliliği
  3. Mühendislik Kavramları: Sayısal, görsel, metinsel veri akışları
  4. Kütüphane İncelemesi: Pydantic v2 ve Python veri yapıları
  5. Minimal Uygulama: Veri modelleri ve katalog yapısı
  6. Deney: Sentetik tekstil varlıklarının kataloglanması
  7. Görselleştirme: Modalite dağılımı özeti
  8. Doğrulama: Model doğrulama kuralları
  9. Hata Senaryoları: Geçersiz modalite, negatif dosya boyutu
  10. Sonuç: Mühendislik çıkarımları ve sonraki güne hazırlık

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `industrial-observation-catalog`
- **Modüller:**
  - `src/models.py`: `DataModality`, `DataAsset`, `SystemResourceRequirements` veri modelleri.
  - `src/observation_catalog.py`: Endüstriyel veri varlıklarını modaliteye göre sınıflandıran, özet istatistik üreten ve JSON dışa aktarımı sağlayan katalog sınıfı.
  - `configs/catalog_config.json`: Problem alanları ve modalite tanımları konfigürasyonu.
  - `tests/test_observation_catalog.py`: Varlık oluşturma, doğrulama kuralları ve katalog operasyonları testleri.

> *Not:* Ortam profilleme ve bağımlılık denetimi (`env_checker`, `environment_profiler`) modülleri müfredat uyumu doğrultusunda **Day 04 (Python Ortamı ve Veri Sözleşmesi)** altına taşınmıştır.

---

## Architecture
```
day01/
├── README.md
├── day01_firma_ve_calisma_ortami.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    │   └── catalog_config.json
    ├── src/
    │   ├── __init__.py
    │   ├── models.py
    │   └── observation_catalog.py
    └── tests/
        ├── __init__.py
        └── test_observation_catalog.py
```

---

## Experiments
- **Deney 1 — Sentetik Varlıkların Modalite Bazlı Sınıflandırılması:**
  - Sayısal (telemetri), Görsel (kamera karesi) ve Metinsel (SOP kılavuzu) varlıklar başarıyla modellendi ve doğrulandı.
- **Deney 2 — Tip Güvenliği ve Kısıt Denetimi:**
  - Negatif dosya boyutu (`estimated_size_kb < 0`) ve geçersiz modalite atamaları `ValidationError` ile yakalandı.

---

## Validation
- `pytest day01/mini_project/tests -q` çalıştırıldı.
- 5 testin tamamı başarıyla geçti.

---

## Results
- Heterojen veri türleri arasındaki depolama, format ve işleme farkları ortaya kondu.
- Gerçek şirket verisi kullanılmadan, sentetik temsillerle veri kataloğu oluşturuldu.

---

## Limitations
- Gözlem kataloğu yerel bellek içi (in-memory) bir PoC'tur; kalıcı bir veri tabanına bağlı değildir.
- Varlık boyutları ve açıklamaları sentetik senaryolara dayanmaktadır.

---

## Files
- `day01/README.md`
- `day01/day01_firma_ve_calisma_ortami.ipynb`
- `day01/mini_project/src/models.py`
- `day01/mini_project/src/observation_catalog.py`
- `day01/mini_project/configs/catalog_config.json`
- `day01/mini_project/tests/test_observation_catalog.py`

---

## How to Run
```bash
# Birim testleri çalıştırma
pytest day01/mini_project/tests -q

# Notebook çalıştırma
jupyter notebook day01/day01_firma_ve_calisma_ortami.ipynb
```

---

## Next Day
**Day 02 — Veri Türleri ve Temel Veri Modelleme:** Yapılandırılmış (CSV/Tablo), yarı yapılandırılmış (JSON) ve yapılandırılmamış verilerin ayrımı, veri modelleri ve serileştirme.