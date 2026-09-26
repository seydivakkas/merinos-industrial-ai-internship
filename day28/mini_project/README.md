# Merinos Endüstriyel AI — Day 28: Entegre RAG Hattı & Canlıya Geçiş Kalite Kapısı

Bu paket, Merinos Halı Sanayi ve Ticaret A.Ş. (Gaziantep 4. OSB) tesislerindeki üretim, dokuma, iplik eğirme, boyahane ve mekanik bakım birimlerinin tüm teknik el kitapları, arıza kodları ve SOP dokümanlarını birleştiren uçtan uca hibrit RAG hattı ve CI/CD canlıya geçiş kalite kapısıdır.

---

## 🏗️ Mimari Bileşenler

1. **Markdown-Duyarlı Doküman Parçalama (`DocumentIndexer`)**:
   - Başlık hiyerarşisi (`# H1`, `## H2`, `### H3`) taranarak her alt bölüme breadcrumbs (`H1 > H2 > H3`) enjekte edilir.
   - Parçaların bağlam kaybı olmadan aranabilmesini sağlar.
2. **Çift Yollu İndeksleme**:
   - **BM25 Seyrek İndeks**: Okapi BM25 formülü ile fabrika terminolojisi ve makine kodları için leksikal arama.
   - **Qdrant HNSW + Int8 Skalar Kuantalama**: In-memory Qdrant vektör tabanı ile kosinüs benzerliği ve %75 bellek tasarrufu.
3. **Ön-Filtreleme & Aday Daraltma**:
   - Departman ve makine kodu bazlı payload ön-filtresi ile arama uzayını hızla daraltır.
4. **Reciprocal Rank Fusion (RRF $k=60$)**:
   - Seyrek ve yoğun arama sıralamalarını normalize etmeden, sıralama tabanlı birleştirir.
5. **Cross-Encoder Yeniden Sıralama**:
   - En iyi adayları derin anlamsal çapraz kodlayıcı ile sorgu-metin çifti olarak yeniden puanlar.
6. **Alıntı Destekli Kanıtlı Üretim (`GroundedGenerator`)**:
   - Yalnızca getirilen bağlamlardaki teknik gerçekleri alıntılar (`[SOP-CAP-001: ...]`) ile yapılandırarak halüsinasyonsuz cevap üretir.
7. **Otomatik Canlıya Geçiş Kalite Kapısı (`DeploymentGate`)**:
   - Day 27 Ragas metrikleri (Sadakat, Bağlamsal Kesinlik, Bağlamsal Kapsama, Cevap Uygunluğu, Harmonik Ragas) ile CI/CD hattında dağıtım onay/red kararı verir.
8. **FastAPI Mikroservisi (`service.py`)**:
   - `/api/v1/query`, `/api/v1/gate-check`, `/api/v1/stats`, `/api/v1/health` uç noktaları sunar.

---

## 💻 CLI Kullanımı

```bash
# 1. Tekil RAG Sorgulaması
python -m day28.mini_project.src.cli query --query "Van de Wiele tezgahında atkı tel kopuşunda ne yapılır?" --department dokuma_salonu_1 --top-k 3

# 2. Otomatik Kalite Kapısı Denetimi
python -m day28.mini_project.src.cli gate-check

# 3. Kıyaslama & 2x2 Tanı Paneli Üretimi
python -m day28.mini_project.src.cli benchmark --plot

# 4. FastAPI Mikroservisini Başlatma
python -m day28.mini_project.src.cli serve --host 127.0.0.1 --port 8028
```

---

## 🧪 Testleri Çalıştırma

```bash
python -m pytest day28/mini_project/tests/test_integrated_pipeline.py -v
```

---

## 📄 Lisans

ÖZEL LİSANS — TÜM HAKLARI SAKLIDIR  
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
