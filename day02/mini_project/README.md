# Day 02 Mini Project: Endüstriyel Veri Modelleri ve JSON Schema Motoru

Bu mini proje, Merinos halı üretim hattındaki görsel kataloglama, dokümantasyon ve yapay zeka çıkarım (inference) servisleri için **Pydantic v2** tabanlı katı veri doğrulama (strict validation) ve serileştirme mimarisini uygular.

---

## 📁 Proje Yapısı

```bash
day02/mini_project/
├── configs/
│   └── models_config.json      # Model sınır değerleri, regex kuralları ve varsayılan konfigürasyon
├── src/
│   ├── __init__.py
│   ├── models.py               # Pydantic v2 modelleri, özel enumlar, validator'lar ve custom istisnalar
│   └── serializer.py           # Model örnekleme, JSON serileştirme ve JSON Schema dışa aktarma
├── tests/
│   ├── __init__.py
│   └── test_models.py          # 8 kapsamlı pytest birim ve sınır değeri testi
├── outputs/
│   ├── sample_models.json      # Doğrulanmış örnek modellerin JSON çıktısı
│   └── schemas.json            # Tüm modellerin OpenAPI / JSON Schema spesifikasyonları
└── README.md                   # Bu dokümantasyon
```

---

## 🛡️ Modeller ve Doğrulama Kuralları

| Model | Alanlar & Kısıtlar | Doğrulama & Sınır Kuralları |
|---|---|---|
| `IndustrialImageMetadata` | `image_id`, `width_px`, `height_px`, `channels`, `color_space`, `dpi`, `knot_density` | Çözünürlük pozitif olmalı, `channels` ∈ {1, 3, 4}, DPI ≥ 72, ilmek sıklığı (knot density) ≥ 10. Renk uzayı `ColorSpaceEnum` ile kısıtlıdır. |
| `CarpetDimensions` | `width_cm`, `length_cm`, `pile_height_mm`, `aspect_ratio` | En & boy [20.0, 1200.0] cm, hav yüksekliği [1.0, 50.0] mm. Boy/en en-boy oranı (aspect ratio) endüstriyel standart olan 0.3 ile 5.0 arasında olmalıdır. |
| `CarpetProduct` | `product_id`, `name`, `collection`, `material`, `dominant_hex_palette`, `dimensions`, `metadata` | `product_id` kesinlikle `MER-[A-Z0-9]{3,8}-[0-9]{3,5}` regex şablonuna uymalıdır. Hex paletindeki her renk `#RRGGBB` formatında 7 karakter olmalıdır. |
| `TechnicalDocument` | `doc_id`, `title`, `source_type`, `version`, `text_content`, `created_at` | İmmutable (`frozen=True`). `doc_id` `DOC-[A-Z0-9]+` şablonuna uymalıdır. Versiyon boş olamaz ve text en az 10 karakter olmalıdır. |
| `InferenceRequest` | `request_id`, `model_name`, `image_b64_or_path`, `top_k`, `min_confidence` | `top_k` [1, 50] aralığında, `min_confidence` [0.0, 1.0] aralığında olmalıdır. |
| `InferenceResponse` | `request_id`, `model_name`, `matches`, `latency_ms`, `success` | `latency_ms` ≥ 0.0 olmalı, matches listesi `SimilarityMatch` objeleri içermelidir. |

---

## 🚀 Nasıl Çalıştırılır?

### 1. Testleri Çalıştırma
```bash
python -m pytest day02/mini_project/tests/ -v
```

### 2. Örnek Modelleri ve JSON Şemalarını Üretme
```bash
python day02/mini_project/src/serializer.py
```

Üretilen çıktılar `outputs/sample_models.json` ve `outputs/schemas.json` dosyalarına kaydedilir.

---

## ⚠️ Sınır ve Hata Durumları (Edge & Failure Cases)
1. **Negatif veya Sıfır Boyut:** En veya boy 0 veya negatif girildiğinde `InvalidDimensionsError` veya `ValidationError` fırlatılır.
2. **Uç Boyut Oranı (Aspect Ratio Anomaly):** 10 cm genişlik ve 5000 cm uzunluk gibi endüstriyel üretim hattına sığmayan değerler model validator tarafından reddedilir.
3. **Geçersiz Hex Kodu:** `#GG0011` veya `#FFF` gibi hatalı hex renk kodları yakalanır.
4. **Bilinmeyen Ek Alanlar (Extra Fields):** `extra="forbid"` kuralı sayesinde şemada tanımlanmayan beklenmedik JSON anahtarları doğrudan reddedilir.
