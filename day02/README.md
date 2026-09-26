# Day 02 — Veri Türleri ve Temel Veri Modelleme

> **Aşama:** Faz 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)  
> **Resmi Staj Defteri Konusu:** Veri Türleri ve Temel Veri Modelleme (Yaprak 3 & 4)

## Goal
Bu günün amacı, halı tasarım ve üretim süreçlerinde ortaya çıkan heterojen veri yapılarını; yapılandırılmış (structured - tabular CSV katalog kayıtları), yarı yapılandırılmış (semi-structured - hiyerarşik JSON dokümanları) ve yapılandırılmamış (unstructured - görsel piksel matrisleri ve teknik çizimler) veri modelleri olarak kurgulamaktır. Ürünler ile çoklu görseller arasındaki 1-N ilişkilerde referans bütünlüğü (referential integrity) doğrulayıcısı geliştirmek ve Pydantic v2 ile tip denetimli veri sözleşmeleri inşa etmektir.

---

## Engineer Research Assignment
- Tekstil işletmesinde düz tablo (CSV) yapısının değişken sayıda fotoğraf ve etiket içeren halı desenlerini saklamadaki yetersizliklerini ve veri tekrarı risklerini analiz etmek.
- Hiyerarşik doküman modelinin (JSON) zengin görsel metadata ve tasarım özniteliklerini saklamadaki avantajlarını değerlendirmek.
- Tabular ürün kayıtları ile görsel varlıklar arasındaki ilişkisel bütünlüğü (referential integrity) çalışma zamanında denetleyen bir algoritma tasarlamak; yetim (orphan) görsel veya var olmayan ürün referanslarını yakalamak.
- Pydantic v2 ile veri modellerinin JSON Schema (`model_json_schema()`) standartlarına uygun serileştirilmesini sağlamak.

---

## Concepts
- **Yapılandırılmış Veri (Structured Data):** Sabit kolonlu, tip tanımlı düz veri yapıları (halı en, boy, koleksiyon, ana renk bilgisi).
- **Yarı Yapılandırılmış Veri (Semi-Structured Data):** Esnek, iç içe geçebilen, değişken sayıda alt nesne barındıran hiyerarşik yapılar (JSON katalog formatı).
- **Yapılandırılmamış Veri (Unstructured Data):** Piksel dizileri, tarayıcı/kamera ham çıktıları veya teknik serbest metinler.
- **Referans Bütünlüğü (Referential Integrity):** Bir ürünün referans verdiği görsel kimliklerinin gerçekte var olup olmadığını garanti eden bütünlük kuralı.
- **Şema Dönüşümü (Schema Transformation):** Düz tabular satırların ve ilişkili görsel metadata nesnelerinin birleşik bir doküman modeline dönüştürülmesi.

---

## Libraries
- `pydantic` (v2): Tip güvenliği, model validatörleri ve JSON Schema dışa aktarımı.
- `typing`, `enum`: Tip ipuçları ve ayrık durum kümeleri (ColorSpace, Material, StructureType).
- `pathlib`: Dosya ve dizin yolu soyutlaması.
- `json`: JSON serileştirme ve standart veri alışverişi.
- `pytest`: Doğrulama ve model sınır testleri.

---

## Functions / Classes Studied
- `pydantic.BaseModel`, `pydantic.Field`, `pydantic.ConfigDict`
- `pydantic.field_validator`, `pydantic.model_validator`
- `BaseModel.model_dump()`, `BaseModel.model_dump_json()`, `BaseModel.model_json_schema()`
- `SchemaTransformer.add_product()`, `SchemaTransformer.add_asset()`
- `SchemaTransformer.link_product_to_images()`, `SchemaTransformer.validate_referential_integrity()`
- `SchemaTransformer.build_composite_catalog()`

---

## Notebook
- **Dosya:** [`day02_veri_turleri_ve_modelleme.ipynb`](day02_veri_turleri_ve_modelleme.ipynb)
- **Kapsam:** 10 standart bölüm (Problem, Neden Önemli, Mühendislik Kavramları, Kütüphane İncelemesi, Minimal Uygulama, Deney, Görselleştirme, Doğrulama, Hata Senaryoları, Sonuç). Düz CSV, ilişkisel bağlantılar ve hiyerarşik JSON dönüşümünü adım adım inceler.

---

## Mini Project
- **Dizin:** [`mini_project/`](mini_project/)
- **Adı:** `data-types-and-modeling`
- **Modüller:**
  - `src/models.py`: `ProductTabularRecord`, `VisualAssetMetadata`, `ProductVisualRelationship`, `ProductCompositeCatalog`, `CarpetProduct`, `IndustrialImageMetadata`, `InferenceRequest`, `InferenceResponse`.
  - `src/schema_transformer.py`: Tabular veriler ile görsel varlıkları birleştiren ve referans bütünlüğünü denetleyen dönüştürücü sınıf.
  - `src/serializer.py`: Pydantic modellerinden JSON şema ve örnek veri üreten serileştirme aracı.
  - `tests/test_data_models.py`: Veri türleri dönüşümü ve referans bütünlüğü testleri.
  - `tests/test_models.py`: Pydantic model sınır ve validasyon testleri.
  - `outputs/`: Üretilen JSON şemalar ve örnek katalog dosyaları.

---

## Architecture
```
day02/
├── README.md
├── day02_veri_turleri_ve_modelleme.ipynb
└── mini_project/
    ├── README.md
    ├── configs/
    ├── src/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── schema_transformer.py
    │   └── serializer.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_data_models.py
    │   └── test_models.py
    └── outputs/
        ├── composite_catalog.json
        └── schemas/
```

---

## Experiments
1. **Referans Bütünlüğü ve Yetim Kayıt Tespiti:**
   - Var olan bir ürüne sistemde bulunmayan `IMG-999` görsel ID'si bağlandığında `validate_referential_integrity()` metodu hatayı yakaladı ve `False` döndürdü.
2. **Tabular $\to$ Hiyerarşik JSON Dönüşümü:**
   - 1 satırlık `ProductTabularRecord` ile 2 adet `VisualAssetMetadata` nesnesi, tek bir `ProductCompositeCatalog` JSON hiyerarşisinde başarıyla birleştirildi.
3. **Pydantic Model Doğrulama:**
   - Negatif piksel boyutları, geçersiz renk uzayları ve sınır dışı en-boy oranları çalışma zamanında engellendi.

---

## Validation
- Pytest ile 11 adet birim test icra edildi:
  - `test_product_tabular_and_visual_asset_creation`
  - `test_referential_integrity_success`
  - `test_referential_integrity_missing_image`
  - `test_composite_catalog_generation_and_export`
  - `test_image_metadata_validation`
  - `test_carpet_dimensions_validation`
  - `test_carpet_product_validation`
  - `test_inference_request_validation`
  - `test_inference_response_validation`
  - `test_model_json_schema_export`
  - `test_invalid_inputs_raise_errors`
- Tüm testler **%100 başarıyla (11 passed)** geçti.

---

## Results
- Heterojen veri türleri tekilleştirilmiş, referans bütünlüğü garanti altına alınmış ve hiyerarşik JSON doküman dönüşümü doğrulanmıştır.
- JSON şemaları `mini_project/outputs/schemas/` altına dışa aktarılmıştır.

---

## Limitations
- Bu aşamada veriler yerel bellek (in-memory) üzerinde ve JSON dosyalarında işlenmiştir; kalıcı SQL/NoSQL veritabanı sürücüsü entegrasyonu sonraki aşamalara bırakılmıştır.
- Tüm veri tipleri ve şemalar sentetik halı üretim modelleriyle test edilmiştir.

---

## Files
- `day02/README.md`
- `day02/day02_veri_turleri_ve_modelleme.ipynb`
- `day02/mini_project/README.md`
- `day02/mini_project/src/__init__.py`
- `day02/mini_project/src/models.py`
- `day02/mini_project/src/schema_transformer.py`
- `day02/mini_project/src/serializer.py`
- `day02/mini_project/tests/__init__.py`
- `day02/mini_project/tests/test_data_models.py`
- `day02/mini_project/tests/test_models.py`
- `day02/mini_project/outputs/composite_catalog.json`

---

## How to Run
```bash
# JSON şemalarını ve örnek modelleri üretme
python day02/mini_project/src/serializer.py

# Birim testleri koşma
pytest day02/mini_project/tests/ -v
```

---

## Next Day
- **Day 03:** Problemin Bilgisayar Mühendisliği Açısından Tanımlanması — Girdi, çıktı, başarı ölçütü ve sezgisel baseline karşılaştırmaları.