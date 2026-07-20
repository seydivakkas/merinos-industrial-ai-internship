# Yol Haritası ve Faz Planı — 40 Günlük Staj

Bu doküman, 40 günlük staj defteri resmi planına göre organize edilmiş mühendislik fazlarını, gün gün hedefleri ve standart Git commit mesaj zincirini içerir.

> **Sabit Veri ve Gerçeklik Sınırı:** Bu projedeki tüm çalışmalar sentetik, çalışma amacıyla hazırlanmış veya açık veriler üzerinde yürütülen yerel öğrenme / PoC (Proof of Concept) çalışmalarıdır. Canlı SCADA/PLC sistemlerine bağlanıldığı, gerçek sensör telemetrisi kullanıldığı, gerçek tezgâh hata loglarının işlendiği veya fabrika içi veritabanlarına canlı erişildiği iddia edilmez.

---

## Faz ve Gün Matrisi

### FAZ 1 — Problem, Veri ve Geliştirme Temelleri (Day 01–08)
- **Day 01:** `day01: firma ve calisma ortaminin taninmasi` — Üretim işletmesinde bilgisayar mühendisliği alanları, sayısal/görsel/metinsel veri türleri ve çalışma ortamının incelenmesi (Yaprak 1 & 2).
- **Day 02:** `day02: veri turleri ve temel veri modelleme` — Yapılandırılmış, yarı yapılandırılmış (JSON) ve yapılandırılmamış veriler, CSV ve temel veri ilişkilerinin incelenmesi (Yaprak 3 & 4).
- **Day 03:** `day03: problemin bilgisayar muhendisligi acisindan tanimlanmasi` — Problem tanımı, girdi/çıktı sınırları, başarı ölçütleri ve baseline değerlendirme mantığı (Yaprak 5 & 6).
- **Day 04:** `day04: python gelistirme ortami ve veri sozlesmesi` — Python sanal ortamı, paket yönetimi, modüler yapı ve tip korumalı veri sözleşmeleri (Yaprak 7 & 8).
- **Day 05:** `day05: pandas, veri hatti ve veri kalitesi` — Çok kaynaklı verilerin Pandas ile okunması, birleştirilmesi, temizlenmesi ve veri kalitesi denetimi (Yaprak 9 & 10).
- **Day 06:** `day06: numpy ve vektorel hesaplama` — NumPy dizi operasyonları, matris çarpımları, broadcasting ve vektörize hesaplama kıyaslaması (Yaprak 11 & 12).
- **Day 07:** `day07: uzaklik ve benzerlik yontemleri` — Öklid, Manhattan, Kosinüs mesafe metrikleri, özellik ölçekleme ve boyut laneti analizi (Yaprak 13 & 14).
- **Day 08:** `day08: kesifsel veri analizi` — İstatistiksel dağılımlar, aykırı değer tespiti (IQR/Z-Score), korelasyon matrisi ve keşifsel veri analizi (Yaprak 15 & 16).

### FAZ 2 — Bilgisayarlı Görü (Day 09–15)
- **Day 09:** `day09: opencv temelleri ve goruntu on isleme` — Piksel matrisleri, renk kanalları (BGR/RGB), boyutlandırma, filtreleme ve histogram analizi (Yaprak 17 & 18).
- **Day 10:** `day10: renk uzaylari ve renk farki` — RGB, HSV, CIELAB ($L^*a^*b^*$) dönüşümleri, algısal renk farkı ($\Delta E^*$, CIEDE2000) ve renk eşikleme (Yaprak 19 & 20).
- **Day 11:** `day11: k-means ile baskin renk paleti` — K-Means renk kümeleme, baskın renk merkezleri, alan oranları ve katalog rengi eşleştirme (Yaprak 21 & 22).
- **Day 12:** `day12: perspektif duzeltme ve homografi` — Kamera açısı eğiklikleri, 4 köşe tespiti, $3\times3$ homografi matrisi ve perspektif düzeltme (Yaprak 23 & 24).
- **Day 13:** `day13: morfolojik islemler, kenar ve cizgi tespiti` — Erozyon, dilatasyon, açma, kapama, Sobel/Canny kenar tespiti ve Hough dönüşümü (Yaprak 25 & 26).
- **Day 14:** `day14: klasik goruntu segmentasyonu` — Otsu eşikleme, Watershed havza algoritması ve GrabCut segmentasyon kıyaslaması (Yaprak 27 & 28).
- **Day 15:** `day15: gorsel ozellik cikarimi ve entegrasyon` — Renk histogramı, GLCM doku öznitelikleri, ORB/SIFT anahtar noktaları ve birleşik öznitelik entegrasyonu (Yaprak 29 & 30).

### FAZ 3 — Klasik Makine Öğrenmesi (Day 16–21)
- **Day 16:** `day16: ikili siniflandirma temelleri` — Lojistik Regresyon, karışıklık matrisi, ROC-AUC eğrisi, dengesiz veri ve maliyet duyarlı eşik optimizasyonu (Yaprak 31 & 32).
- **Day 17:** `day17: cok sinifli siniflandirma` — Çok sınıflı kusur sınıflandırması, Multinomial Logistic Regression, Softmax ve One-vs-Rest (OvR) stratejileri (Yaprak 33 & 34).
- **Day 18:** `day18: decision tree ve random forest` — Karar ağaçları, bilgi kazancı/Gini indeksi, Random Forest topluluğu ve öznitelik önem analizi (Yaprak 35 & 36).
- **Day 19:** `day19: gradient boosting modelleri` — XGBoost ve LightGBM mimarileri, gradyan artırma dinamikleri, hiperparametre optimizasyonu ve erken durdurma (Yaprak 37 & 38).
- **Day 20:** `day20: support vector machine` — Destek Vektör Makineleri (Linear ve RBF çekirdek), marjin maksimizasyonu ve karar sınırlarının incelenmesi (Yaprak 39 & 40).
- **Day 21:** `day21: gozetimsiz ogrenme ve boyut indirgeme` — PCA, t-SNE, K-Means ve DBSCAN ile gözetimsiz kümeleme ve boyut indirgeme analizi (Yaprak 41 & 42).

### FAZ 4 — Retrieval ve RAG Temelleri (Day 22–27)
- **Day 22:** `day22: metinlerin sayisal temsili ve bm25` — Kelime torbası (BoW), TF-IDF, Okapi BM25 seyrek arama algoritması ve ters dizin (inverted index) mekanizması (Yaprak 43 & 44).
- **Day 23:** `day23: vektor tabanli metin arama` — Bi-Encoder gömme (embedding) modelleri, anlamsal yoğun arama ve Kosinüs benzerliği ile aday getirme (Yaprak 45 & 46).
- **Day 24:** `day24: hibrit retrieval ve rrf` — Leksikal (BM25) ve yoğun semantik arama sonuçlarının Reciprocal Rank Fusion (RRF) ile harmanlanması (Yaprak 47 & 48).
- **Day 25:** `day25: dokuman chunking yontemleri` — Sabit boyutlu, recursive, anlamsal ve Markdown tabanlı parçalama (chunking) yöntemleri ve örtüşme (overlap) analizi (Yaprak 49 & 50).
- **Day 26:** `day26: vektor indeksleme yontemleri` — Exact Flat, IVF ve HNSW vektör indeks yapıları, arama hızı ve recall dengesi (Yaprak 51 & 52).
- **Day 27:** `day27: rag temelleri ve degerlendirme` — Soru-cevap RAG boru hattı, bağlam getirme, RAG Triad prensipleri ve Ragas değerlendirme metrikleri (Yaprak 53 & 54).

### FAZ 5 — Görsel Üretim ve Analiz PoC (Day 28–30)
- **Day 28:** `day28: kontrollu gorsel uretim` — Tasarım briflerinin yapılandırılması (stil, motif, renk vb.), SDXL ile kontrollü üretim, seed varyasyonları ve prompt mühendisliği (Yaprak 55 & 56).
- **Day 29:** `day29: uretilen gorsellerin sayisal analizi` — Üretilen görsellerde K-Means renk paleti, CIELAB $\Delta E^*$, simetri/otokorelasyon, kenar sürekliliği ve CNN embedding analizi (Yaprak 57 & 58).
- **Day 30:** `day30: gorsel uretim ve analiz mini prototipi` — Sentetik tasarım girdisi, görsel üretimi ve çok boyutlu analitiğin birleşik yerel prototip arayüzünde toplanması (Yaprak 59 & 60).

### FAZ 6 — Doküman RAG, Servisleştirme ve Kapanış (Day 31–40)
- **Day 31:** `day31: dokuman alma ve on isleme` — PDF, DOCX ve Markdown sentetik teknik metinlerin ayrıştırılması, metadata çıkarımı, chunking ve ilk getirme (Yaprak 61 & 62).
- **Day 32:** `day32: hibrit dokuman arama ve olcum` — BM25 ve vektör aramanın ağırlıklı/RRF füzyonu, IR başarım metrikleri (Hit@K, MRR, NDCG) ve getirme hatalarının analizi (Yaprak 63 & 64).
- **Day 33:** `day33: kaynakli cevap uretimi` — Alıntılanabilir bağlam hazırlama, `[S1]`, `[S2]` kaynak kimliği eşleştirmesi ve retrieval vs. generation hata ayrımı (Yaprak 65 & 66).
- **Day 34:** `day34: reranking ve context yonetimi` — Bi-Encoder ilk aşama adaylarının Cross-Encoder ile yeniden puanlanması ve bağlam penceresi sıkıştırması (Yaprak 67 & 68).
- **Day 35:** `day35: query rewrite, multi-query ve hyde` — Operatör sorgularının genişletilmesi, Query Rewrite, Multi-Query ve HyDE (Hypothetical Document Embeddings) teknikleri (Yaprak 69 & 70).
- **Day 36:** `day36: yapilandirilmis ve grounded cevap` — Pydantic şemalı yapılandırılmış yanıtlar, NLI/groundedness kontrolleri ve güvenli geri çekilme (fallback) mekanizması (Yaprak 71 & 72).
- **Day 37:** `day37: rag degerlendirmesi ve guardrail` — Ragas triad metrikleri, İSG tehlikeli talep filtreleri ve kural tabanlı erken kesme (early-exit) güvenlik korkulukları (Yaprak 73 & 74).
- **Day 38:** `day38: yerel api servisi ve basit arayuz` — Sentetik teknik doküman RAG hattının FastAPI REST servisi ve Streamlit yerel kullanıcı arayüzü ile sunumu (Yaprak 75 & 76).
- **Day 39:** `day39: onnx, kuantizasyon ve yerel benchmark` — Küçük örnek modellerin ONNX formatına dönüştürülmesi, dinamik INT8 kuantizasyonu ve ONNX Runtime CPU gecikme benchmark'ı (Yaprak 77 & 78).
- **Day 40:** `day40: final test, dokumantasyon ve staj degerlendirmesi` — Geliştirilen örnek modüllerin ve iki ana PoC'nin genel değerlendirmesi, regresyon testleri, teknik sınırlamalar ve staj kazanımlarının raporlanması (Yaprak 79 & 80).
