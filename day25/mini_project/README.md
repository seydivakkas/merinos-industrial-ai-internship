# Merinos Halı Sanayi A.Ş. — Day 25: Metin Parçalama & Chunking Stratejileri

Bu modül, **Merinos Gaziantep Tesisleri** teknik bakım, üretim ve kalite kontrol SOP dokümanlarının RAG (Retrieval-Augmented Generation) ve bilgi getirme sistemlerinde en yüksek doğrulukla işlenebilmesi için geliştirilmiş **4 Farklı Metin Parçalama (Document Chunking)** motorunu ve getirme başarım analizini içerir.

---

## 1. Parçalama Stratejileri ve Matematiksel Modeller

### A. Sabit Boyutlu Parçalama (Fixed-Size Chunker with Overlap)
Metni sabit karakter penceresi ($L$) ve örtüşme ($O$) adımı ile böler:
$$\text{Adım} = L - O$$
$$C_k = \text{Text}[k \cdot (L - O) : k \cdot (L - O) + L]$$
- **Avantajı:** Düşük hesaplama maliyeti, deterministik uzunluk.
- **Dezavantajı:** Cümle ve paragraf sınırlarını rastgele keserek anlamsal parçalanmaya (semantic fragmentation) ve "iğne-samanlık" (needle-in-a-haystack) bilgi kaybına yol açar.

### B. Özyinelemeli Karakter Parçalama (Recursive Character Text Splitter)
Metni hiyerarşik ayırıcılar dizisi ile anlamsal sınırları koruyarak parçalar:
$$\mathcal{S} = \left[ \text{"\\n\\n" (paragraf)}, \text{"\\n" (satır)}, \text{". " (cümle)}, \text{" " (kelime)}, \text{"" (karakter)} \right]$$
Ayırıcılar sırayla uygulanır; parça boyutu izin verdiği sürece üst seviye ayırıcı korunur.

### C. Anlamsal Parçalama (Semantic Chunker via Cosine Distance Breakpoints)
Ardışık cümle vektörleri $e(s_i)$ ve $e(s_{i+1})$ arasındaki kosinüs mesafesini ölçer:
$$d(s_i, s_{i+1}) = 1 - \frac{e(s_i) \cdot e(s_{i+1})}{\|e(s_i)\|_2 \|e(s_{i+1})\|_2}$$
Belirlenen persentil eşiği ($\tau = P_{85}(\{d\})$) aşıldığında ve minimum boyut ($L_{min}$) sağlandığında kırılma noktası (breakpoint) konularak yeni parça başlatılır.

### D. Markdown Yapı-Duyarlı Parçalama (Markdown-Aware Chunker with Breadcrumbs)
Teknik dokümanlardaki `# H1`, `## H2`, `### H3` başlık hiyerarşisini yığın (stack) yapısı ile takip eder.
Her parçaya hiyerarşik yol (breadcrumb metadata) iliştirilir:
$$\text{Breadcrumb} = H_1 \succ H_2 \succ H_3$$
Örnek: `SOP-001: Van de Wiele RCE02 Halı Dokuma Tezgâhı > 4. Periyodik Kontrol Tablosu`
Tablo ve listeler bölünmeden tek blok olarak korunur.

---

## 2. Dizin Yapısı

```
day25/mini_project/
├── configs/
│   └── chunking_config.json          # Hiperparametreler ve model yolları
├── fixtures/
│   ├── merinos_sop_documents.json    # 12 adet çok bölümlü endüstriyel SOP dokümanı
│   └── chunking_evaluation_queries.json # 15 adet teknik iğne-samanlık değerlendirme sorgusu
├── outputs/
│   ├── chunking_benchmark_report.json # Kıyaslama metrik sonuçları
│   └── chunking_diagnostic_panel.png  # 2x2 Master Tanı Paneli (300 DPI)
├── src/
│   ├── __init__.py                   # Paket başlatıcı
│   ├── models.py                     # Pydantic v2 veri modelleri
│   ├── fixed_chunker.py              # Fixed-size chunker implementasyonu
│   ├── recursive_chunker.py          # Recursive character chunker implementasyonu
│   ├── semantic_chunker.py           # Semantic breakpoint chunker implementasyonu
│   ├── markdown_chunker.py           # Markdown breadcrumb chunker implementasyonu
│   ├── chunk_engine.py               # Birleşik MerinosChunkEngine orkestratörü
│   ├── evaluator.py                  # Geometrik, coherence ve retrieval değerlendirici
│   ├── visualizer.py                 # 2x2 Matplotlib Master Tanı Paneli
│   └── cli.py                        # Argparse komut satırı arayüzü
├── tests/
│   └── test_document_chunking.py     # 10 adet kapsamlı birim ve entegrasyon testi
└── README.md                         # Bu dokümantasyon
```

---

## 3. Kurulum ve CLI Kullanımı

### Parçalama Komutu (Chunk)
```bash
# Markdown-aware ile SOP-001'i parçala ve ekranda gör
python -m day25.mini_project.src.cli chunk --strategy markdown_aware --doc-id SOP-001 --limit 3

# Fixed-size ile parçala ve JSON olarak kaydet
python -m day25.mini_project.src.cli chunk --strategy fixed_size --output outputs/fixed_chunks.json
```

### Büyük Kıyaslama ve Tanı Paneli (Benchmark)
```bash
python -m day25.mini_project.src.cli benchmark --plot
```

---

## 4. Lisans

ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
