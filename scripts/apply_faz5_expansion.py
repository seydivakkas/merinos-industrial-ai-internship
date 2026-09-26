# -*- coding: utf-8 -*-
"""Apply humanized, deep engineering narrative for Faz 5 (Days 28 to 30 / Yapraks 55 to 60)."""

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'r', encoding='utf-8') as f:
    full_text = f.read()

pos_start = full_text.find('## GÜN 28 — 21 AĞUSTOS 2026')
pos_end = full_text.find('## GÜN 31 — 25 AĞUSTOS 2026')

assert pos_start != -1 and pos_end != -1, 'Day 28 or Day 31 marker not found!'

faz5_expanded = '''## GÜN 28 — 21 AĞUSTOS 2026
**KISIM:** Kontrollü Görsel Üretim  
**YAPRAK NO:** 55  
**YAPILAN İŞ:** Halı tasarım isteğinin yapılandırılması ve sentetik görsel varyasyonlarının oluşturulması  
**TARİH:** 21/08/2026

Stajımın yirmi sekizinci gününde, staj takvimimizin beşinci büyük aşaması olan Görsel Üretim ve Analiz PoC (Proof-of-Concept) fazına başladım. Tasarım stüdyosunda halı desinatörleri ve AR-GE mühendisleriyle bir araya geldiğimizde, tekstil sektöründe yeni bir koleksiyon hazırlamanın aylar süren yoğun bir eskiz, renklendirme ve numune dokuma süreci gerektirdiğini gözlemledim. Üretken yapay zekâ (Generative AI) ve difüzyon modellerinin (Diffusion Models), tasarımcılara ön fikir oluşturma ve prototipleme hızını artırma konusunda muazzam bir potansiyel sunduğunu tartıştık.

Ancak danışman mühendisimle yaptığımız teknik değerlendirmede, endüstriyel bir mühendislik projesinde difüzyon modellerine (örneğin Stable Diffusion XL) rastgele "güzel bir halı deseni çiz" şeklinde serbest metinler vermenin hiçbir pratik değeri olmadığını; bir fabrikanın üretim disiplinine uygun kontrollü, tekrarlanabilir ve parametrik bir üretim mimarisi kurulması gerektiğini netleştirdik.

Bu amaçla `prompt_structurer` modülü altında `PromptStructurer` sınıfını geliştirdim. Tasarımcının isteklerini yapılandırılmış bir veri sözleşmesine (Pydantic şeması) bağladım. Bu şema; halı stili (geleneksel, modern geometrik, minimalist İskandinav), ana motif türü (merkezi madalyon, bordürlü çiçekli, soyut çizgiler), renk paleti (toprak tonları, pastel bej-mavi, canlı kontrast), ilme yoğunluk hissi ve en-boy oranı (örneğin 160x230 cm standart halı oranı) gibi alanları içeriyordu.

Geliştirdiğim yapılandırıcı fonksiyon, bu parametreleri birleştirerek modelin anlayacağı optimize edilmiş pozitif yönlendirici metinler ile istenmeyen bozulmaları (bulanıklık, düşük çözünürlük, asimetrik yazı, filigran) engelleyen negatif yönlendirici metinleri (negative prompt) otomatik olarak inşa ediyordu.

**KONTROL SONUCU:**

---

## GÜN 28 — DEVAM
**KISIM:** Kontrollü Görsel Üretim  
**YAPRAK NO:** 56  
**YAPILAN İŞ:** Seed ve tek değişkenli prompt varyasyonlarının örnek çıktılar üzerinde incelenmesi  
**TARİH:** 21/08/2026

Öğleden sonraki oturumda üretimin tekrarlanabilirliğini ve kontrol edilebilirliğini sağlamak üzere `sdxl_controller` ve `comparator_engine` modüllerini geliştirdim.

Danışman mühendisim, "Eğer ürettiğin bir deseni yarın aynı parametrelerle tekrar üretemiyorsan, o sistem endüstriyel bir araç değil yalnızca bir oyuncaktır" diyerek deterministik üretim kontrolünün önemini vurguladı. Bu doğrultuda `SDXLController` sınıfı içinde difüzyon sürecini kontrol eden kilit hiperparametreleri yapılandırdım: Rastgele sayı üreteci tohumu (`seed`), metne sadakat katsayısı (`guidance_scale=7.5`) ve difüzyon adım sayısı (`num_inference_steps=30`).

Ardından `GenerationComparator` sınıfı ile tek değişkenli kontrol (ablation / single-variable variation) deneylerini koşturdum. Burada çok heyecan verici bir "aha!" anı yaşadım: Rastgele tohumu (`seed=42`) tamamen sabit tutarak, tasarım şablonundaki diğer tüm özellikleri koruyup yalnızca renk paleti parametresini "krem-bordo"dan "antrasit-altın"a değiştirdiğimde; halının merkezindeki madalyon motifinin, köşe kıvrımlarının ve bordür geometrisinin milimetrik olarak aynı kaldığını, yalnızca renk tonlarının başarıyla dönüştüğünü gözlemledim.

Bu kontrollü üretim yeteneği, bir tasarımcının beğendiği bir deseni bozmadan farklı renk varyantlarını saniyeler içinde türetebilmesini sağladı.

Yazdığım üretim kontrolcüsünü `test_controlled_generation` test paketiyle sınadım; şema doğrulamalarını ve seed tutarlılığını pytest ile teyit ettim.

Günün sonunda, difüzyon modellerini rastgelelikten çıkarıp mühendislik parametreleriyle denetlenen bir üretim motoruna dönüştürdük. Ancak üretilen görselin sadece göze güzel görünmesinin yeterli olmadığını, sayısal kalite kriterleriyle ölçülmesi gerektiğini değerlendirerek yarınki analiz aşamasına geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 29 — 22 AĞUSTOS 2026
**KISIM:** Üretilen Görsellerin Sayısal Analizi  
**YAPRAK NO:** 57  
**YAPILAN İŞ:** Sentetik üretilmiş halı görsellerinde renk, simetri ve kenar özelliklerinin çıkarılması  
**TARİH:** 22/08/2026

Stajımın yirmi dokuzuncu gününde, difüzyon modelleri tarafından üretilen sentetik halı görsellerinin nesnel ve matematiksel metriklerle denetlenmesi problemine odaklandım. Üretken yapay zekânın en büyük zaaflarından biri, ilk bakışta etkileyici görünen bir görselin pikselleri yakından incelendiğinde asimetrik kaymalar, kopuk bordür çizgileri veya katalog dışı uyumsuz renk tonları barındırabilmesidir.

Bu kalite denetimini otomatikleştirmek amacıyla `color_analyzer`, `symmetry_analyzer` ve `seam_analyzer` modüllerini geliştirdim:
1. Renk Uyumu Analizi (`ColorDistributionAnalyzer`): Üretilen görsel üzerinde K-Means kümelemesi yaparak baskın renkleri çıkaran ve hedef kurumsal iplik paletiyle CIELAB $\Delta E^*$ farkını hesaplayan fonksiyon.
2. Geometrik Simetri Analizi (`SymmetryAnalyzer`): Klasik halı desenlerinde beklenen yatay ve dikey ayna simetrisini piksel yoğunlukları ve öznitelik seviyesinde ikiye katlayıp (flip) normalleştirilmiş çapraz korelasyon (Normalized Cross-Correlation) ile 0 ile 1 arasında bir Simetri Skoru üreten fonksiyon.
3. Kenar ve Bordür Sürekliliği (`SeamContinuityAnalyzer`): Canny kenar dedektörü ve morfolojik gradyanlar kullanarak halının dış bordür hatlarında bir kopukluk, eğrilik veya dalgalanma olup olmadığını denetleyen Süreklilik İndeksi.

Her üç analiz motorunu sentetik olarak üretilmiş desenler üzerinde koşturarak sayısal kalite karnelerini çıkardım.

**KONTROL SONUCU:**

---

## GÜN 29 — DEVAM
**KISIM:** Üretilen Görsellerin Sayısal Analizi  
**YAPRAK NO:** 58  
**YAPILAN İŞ:** Sentetik katalog üzerinde çok boyutlu görsel analiz sonuçlarının karşılaştırılması  
**TARİH:** 22/08/2026

Öğleden sonraki oturumda, üretilen sentetik görsellerin fabrikanın mevcut tescilli ürün kataloğuyla olan anlamsal benzerliğini denetlemek üzere `embedding_retriever` modülü altında `CNNEmbeddingRetriever` sınıfını geliştirdim.

Danışman mühendisimle telif hakkı ve tasarım özgünlüğü risklerini konuştuk. Yapay zekâ tarafından üretilen bir desenin, firmanın veya rakiplerin tescilli mevcut bir desenine aşırı derecede benzemesi durumunda hukuki ve ticari riskler doğabileceğini tartıştık. Bu riski önceden tarayabilmek amacıyla, üretilen görseli ön-eğitilmiş bir konvolüsyonel sinir ağı (CNN) / Vision Transformer modeliyle 512 boyutlu yoğun bir görsel embedding vektörüne dönüştürdüm. Ardından mevcut sentetik katalog deposunda Kosinüs Benzerliği ile tarama yaparak en çok benzeyen ilk 3 ürünü (Top-K Benzerlik) ve benzerlik skorlarını listeledim.

Daha sonra tüm analizleri tek bir çatıda birleştiren `MasterImageAnalyzer` sınıfını yazdım. Bu sınıf; Renk Skoru, Simetri Skoru, Bordür Sürekliliği ve Katalog Benzerlik İndeksini tek bir yapılandırılmış raporda birleştirdi.

Burada danışman mühendisimle stajımın en kritik etik ve mühendislik ilkelerinden birini kayda geçirdik:
"Görsel benzerlik embedding skoru, hiçbir zaman mutlak bir telif güvenliği veya hukuki özgünlük garantisi olarak sunulamaz. Aynı şekilde hesaplanan matematiksel metrikler, bu desenin tezgâhta doğrudan dokunabilir (dokuma fizibilitesi) olduğunu veya estetik olarak kusursuz olduğunu tek başına iddia edemez. Bu sistem yalnızca insan tasarımcıya ve mühendise karar desteği sunan analitik bir filtreleme aracıdır; nihai onay mutlaka insan uzmana aittir."

Yazdığım analiz modüllerini `test_visual_analysis` test paketiyle sınadım; simetri ve renk metriklerinin beklenen aralıklarda çalıştığını pytest ile doğruladım.

**KONTROL SONUCU:**

---

## GÜN 30 — 24 AĞUSTOS 2026
**KISIM:** Görsel Üretim ve Analiz Mini Prototipi  
**YAPRAK NO:** 59  
**YAPILAN İŞ:** Sentetik tasarım girdisi, görsel oluşturma ve analiz adımlarının tek uygulamada toplanması  
**TARİH:** 24/08/2026

Stajımın otuzuncu gününde, son iki günde parça parça geliştirdiğimiz tasarım yapılandırma, görsel üretim ve çok boyutlu analitik motorlarını tek bir uçtan uca çalışan entegre yerel prototip boru hattında topladım.

Bu mimariyi hayata geçirmek amacıyla `pipeline` modülü altında `IntegratedGenerationPipeline` sınıfını geliştirdim. Bu boru hattı tam entegre 4 aşamalı bir iş akışı yürütüyordu:
1. Tasarım Girdisi Aşaması: Kullanıcıdan veya tasarımcıdan gelen stil, renk ve motif tercihlerini Pydantic veri sözleşmesiyle doğrulama.
2. Kontrollü Üretim Aşaması: Yapılandırılmış prompt ve deterministik seed ile görsel difüzyon üretimini gerçekleştirme.
3. Çok Boyutlu Sayısal Analiz Aşaması: Üretilen görseli anında bellek üzerinden alarak K-Means renk paletini ($\Delta E^*$), dikey/yatay simetri korelasyonunu ve kenar sürekliliğini eş zamanlı hesaplama.
4. Katalog Benzerlik ve Raporlama Aşaması: Görsel embedding çıkarımıyla mevcut desen veritabanında en yakın ürünleri bulup tüm sayısal metrikleri tek bir JSON karnesinde birleştirme.

Geliştirdiğim bu akışın, tasarımcının bir düğmeye basmasıyla birkaç saniye içinde görseli üretip yanına tüm mühendislik analizlerini eksiksiz getirdiğini gözlemledim.

**KONTROL SONUCU:**

---

## GÜN 30 — DEVAM
**KISIM:** Görsel Üretim ve Analiz Mini Prototipi  
**YAPRAK NO:** 60  
**YAPILAN İŞ:** Örnek görsel üretim/analiz uygulamasının kullanıcı arayüzü üzerinden incelenmesi  
**TARİH:** 24/08/2026

Öğleden sonraki oturumda, geliştirdiğim entegre boru hattını teknik olmayan tasarımcıların ve fabrika yöneticilerinin de rahatlıkla deneyimleyebilmesi için görselleştirici ve yerel arayüz bileşenlerini tamamladım.

`visualizer` modülü altında `IntegratedVisualizer` sınıfını kodladım. Bu sınıf; üretilen halı desenini, çıkarılan baskın renk paletini (yüzdesel alan oranları ve en yakın iplik kodlarıyla birlikte), dikey simetri eksen haritasını ve katalogdan çekilen en benzer 3 referans halıyı tek bir çok panelli görselleştirme tablosunda (dashboard) bir araya getiriyordu. Ayrıca Streamlit kütüphanesi kullanarak yerel bir web kullanıcı arayüzü prototipi kurguladım.

Tasarım ofisindeki mühendislerle birlikte yaptığımız canlı prototip oturumunda, parametreleri değiştirerek farklı halı desenleri ürettik ve sistemin ürettiği simetri ve renk metriklerini inceledik. Mühendisler, yapay zekânın sadece "resim çizen" bir araç olmaktan çıkıp, arkasında renk farkı ($\Delta E^*$), dokuma kenar sürekliliği ve katalog çakışma riskini raporlayan bir mühendislik asistanına dönüşmesinden son derece memnun kaldılar.

Yazdığım entegre boru hattını `test_generation_analysis_pipeline` test paketiyle sınadım; uçtan uca akışın veri sözleşmelerine uygunluğunu ve analiz çıktılarının bütünlüğünü pytest ile doğruladım.

Böylece stajımın beşinci büyük aşaması olan **Faz 5: Görsel Üretim ve Analiz PoC** safhasını başarıyla tamamladım. Üretken yapay zekâyı bilgisayarlı görü ve benzerlik analitiğiyle harmanlayarak somut bir katma değer ürettik. Yarın stajımın son ve en kapsamlı etabı olan **Faz 6: Doküman RAG, Servisleştirme ve Kapanış** fazına adım atarak, endüstriyel teknik doküman asistanımızı FastAPI servisine ve canlı operatör arayüzüne dönüştürmeye hazır hale geldim.

**KONTROL SONUCU:**

---
'''

new_full_text = full_text[:pos_start] + faz5_expanded + full_text[pos_end:]

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'w', encoding='utf-8') as f:
    f.write(new_full_text)

print('Successfully applied Faz 5 expansion to Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md!')
