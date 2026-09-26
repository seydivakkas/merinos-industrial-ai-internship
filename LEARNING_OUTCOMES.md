# Öğrenim Kazanımları ve Yetkinlik Matrisi

Bu doküman, 40 günlük staj boyunca bir Bilgisayar Mühendisi olarak kazanılan temel teorik kavramları, endüstriyel pratikleri ve teknik yetkinlikleri özetler.

---

## 1. Temel Mühendislik Kazanımları

1. **Teknolojiyi Problemden Önce Seçmeme İlkesi:**
   - Her aşamada karmaşık derin öğrenme modellerine doğrudan atlamak yerine, önce en yalın klasik veya istatistiksel yöntemle başlanmış, yöntemin sınırları ölçülmüş ve yalnız ihtiyaç duyulduğunda bir üst mimariye geçilmiştir.

2. **Deneysel Dürüstlük ve Sayısal Doğrulama:**
   - "Model iyi çalışıyor" gibi öznel yargılar yerine; Precision@K, Recall@K, MRR, NDCG, LPIPS, $\Delta E^*$, p95 gecikme ve bellek tüketimi gibi nesnel metriklerle sistem performansı raporlanmıştır.

3. **Veri Modelleri ve Tip Güvenliği:**
   - Veri boru hatlarında ham sözlükler (dictionaries) yerine Pydantic v2 modelleri ve katı tip denetimi kullanılarak çalışma zamanı (runtime) hataları üretim öncesinde elenmiştir.

4. **Modüler Tasarım, Tip Güvenliği ve Yerel PoC Servisleştirme:**
   - Ham veri sözlükleri yerine Pydantic v2 modelleri ile veri sözleşmeleri tanımlanmış; geliştirilen algoritmalar yerel FastAPI REST servisi, Streamlit analiz arayüzü ve ONNX INT8 kuantizasyon benchmarkları ile ölçülebilir ve tekrarlanabilir bir PoC mimarisine dönüştürülmüştür.

---

## 2. Faz Bazlı Yetkinlik Matrisi

| Faz | Kazanılan Teknik Yetkinlik | Mühendislik ve Öğrenim Karşılığı |
| :--- | :--- | :--- |
| **Faz 1: Problem, Veri ve Geliştirme Temelleri (Day 01–08)** | Python geliştirme ortamı, Pydantic veri sözleşmeleri, Pandas veri boru hattı ve kalitesi, NumPy vektörizasyonu, uzaklık/benzerlik metrikleri, EDA | Tekrarlanabilir geliştirme ortamı, veri kalite güvencesi ve matematiksel veri işleme temelleri |
| **Faz 2: Bilgisayarlı Görü (Day 09–15)** | OpenCV görüntü ön işleme, CIELAB dönüşümü, CIEDE2000 renk farkı, K-Means palet çıkarma, homografi matrisi, morfoloji, klasik segmentasyon, görsel öznitelik çıkarımı | Görüntü filtreleme, renk analitiği, perspektif düzeltme ve geleneksel bilgisayarlı görü yöntemleri |
| **Faz 3: Klasik Makine Öğrenmesi (Day 16–21)** | Lojistik Regresyon, Decision Tree, Random Forest, XGBoost, LightGBM, SVM, PCA, t-SNE, K-Means, DBSCAN | İkili ve çok sınıflı sınıflandırma, maliyet duyarlı eşik ayarı, hiperparametre optimizasyonu ve gözetimsiz analiz |
| **Faz 4: Retrieval ve RAG Temelleri (Day 22–27)** | TF-IDF, BM25 leksikal arama, Bi-Encoder semantik arama, RRF sıralama füzyonu, doküman chunking, vektör indeksleme, Ragas değerlendirme | Metinlerin sayısal temsili, hibrit arama mekanizmaları ve RAG sistemlerinin nesnel değerlendirilmesi |
| **Faz 5: Görsel Üretim ve Analiz PoC (Day 28–30)** | Yapılandırılmış prompt mühendisliği (SDXL), K-Means renk analitiği, CIELAB $\Delta E^*$, simetri/otokorelasyon, kenar sürekliliği, CNN embedding benzerliği | Sentetik desen varyasyonları üretimi ve üretilen çıktıların çok boyutlu sayısal analizi (yerel PoC) |
| **Faz 6: Doküman RAG, Servisleştirme ve Kapanış (Day 31–40)** | Çoklu doküman işleme (PDF/DOCX/MD), Cross-Encoder reranking, Query Rewrite & HyDE, Pydantic groundedness, İSG guardrails, FastAPI, Streamlit, ONNX INT8 CPU benchmark, final test & raporlama | Uçtan uca doküman RAG boru hattı, yerel REST servisi ve kullanıcı arayüzü, model sıkıştırma ve staj kapanış değerlendirmesi |
