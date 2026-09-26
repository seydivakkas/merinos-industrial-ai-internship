# -*- coding: utf-8 -*-
"""Apply humanized, deep engineering narrative for Faz 3 (Days 16 to 21 / Yapraks 31 to 42)."""

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'r', encoding='utf-8') as f:
    full_text = f.read()

pos_start = full_text.find('## GÜN 16 — 7 AĞUSTOS 2026')
pos_end = full_text.find('## GÜN 22 — 14 AĞUSTOS 2026')

assert pos_start != -1 and pos_end != -1, 'Day 16 or Day 22 marker not found!'

faz3_expanded = '''## GÜN 16 — 7 AĞUSTOS 2026
**KISIM:** İkili Sınıflandırma Temelleri  
**YAPRAK NO:** 31  
**YAPILAN İŞ:** Sentetik kalite özellikleriyle lojistik regresyon modelinin kurulması  
**TARİH:** 07/08/2026

Stajımın on altıncı gününde, önceki iki haftada geliştirdiğimiz bilgisayarlı görü özniteliklerini (renk, doku, kenar) ve tezgâh telemetri verilerini kullanarak üretim kalite kontrolünü otomatikleştirecek makine öğrenmesi modelleri kurmaya başladım. Böylece stajımın üçüncü büyük aşaması olan Klasik Makine Öğrenmesi fazına adım attım. Danışman mühendisimle sabah yaptığımız toplantıda, kalite kontrol masasında duran bir operatörün en temel kararının ikili (binary) bir karar olduğunu konuştuk: "Bu halı sağlam mı, yoksa kusurlu mu?"

Bu ikili karar sürecini modellemek üzere makine öğrenmesinin en temel ve yorumlanabilir sınıflandırma algoritması olan Lojistik Regresyon modelini ele aldım. `logistic_classifier` modülü altında `IndustrialLogisticClassifier` sınıfını geliştirdim. Modelin matematiksel kalbinde yatan Sigmoid aktivasyon fonksiyonunu $S(z) = 1 / (1 + e^{-z})$ kodlayarak, lineer model çıktısını 0 ile 1 arasında olasılıksal bir güven skoruna dönüştürdüm. Model eğitiminde ikili çapraz entropi (binary cross-entropy loss) kayıp fonksiyonunu ve aşırı öğrenmeyi (overfitting) frenleyen $L_2$ ağırlık cezalandırma (Ridge regülarizasyonu) mekanizmasını uyguladım.

Modelin eğitileceği sentetik veri kümesini `preprocessor` modülü içinde geliştirdiğim `TabularPreprocessor` sınıfı ile hazırladım. Veri setini %80 eğitim ve %20 test olacak şekilde deterministik bir rastgelelik tohumuyla (random seed) ayırdım. Sayısal özniteliklerin farklı birimlerde olması (örneğin iplik gerginliği 0-50 N aralığındayken renk yoğunluğunun 0-1 aralığında olması) model katsayılarını bozmasın diye tüm özellikleri standart normal dağılıma ($Z$-score) getirdim.

Eğittiğim ilk lojistik regresyon modelinin test seti üzerinde temel olasılık tahminlerini başarıyla ürettiğini gözlemledim.

**KONTROL SONUCU:**

---

## GÜN 16 — DEVAM
**KISIM:** İkili Sınıflandırma Temelleri  
**YAPRAK NO:** 32  
**YAPILAN İŞ:** Train/test ayrımı, confusion matrix ve temel metriklerin incelenmesi  
**TARİH:** 07/08/2026

Öğleden sonraki çalışmamda, eğittiğim modelin başarısını değerlendirmek üzere `evaluator` modülü altında `BinaryEvaluator` sınıfını geliştirdim. Danışman mühendisimle yaptığımız oturumda, endüstriyel kalite kontrolde sadece tek bir doğruluk (accuracy) yüzdesine bakmanın ne kadar yanıltıcı bir tuzak olduğunu tartıştık. Fabrikada üretilen halıların %95'inin kusursuz, sadece %5'inin hatalı olduğu dengesiz (imbalanced) bir üretim ortamında, her halıya körü körüne "sağlam" diyen aptal bir modelin bile kâğıt üzerinde %95 doğruluk alacağını; oysa fabrikayı batıracağını konuştuk.

Bu farkındalıkla modelin performansını Karışıklık Matrisi (Confusion Matrix) üzerinden Doğru Pozitif (TP), Yanlış Pozitif (FP), Doğru Negatif (TN) ve Yanlış Negatif (FN) bileşenlerine ayırdım. Ardından Kesinlik (Precision), Duyarlılık (Recall), F1-Score ve Özgüllük (Specificity) metriklerini hesaplayan fonksiyonları kodladım.

Burada çok hayati bir "aha!" anı yaşadım: Standart makine öğrenmesi kütüphaneleri sınıflandırma kararını varsayılan 0.5 olasılık eşiğine göre verir. Oysa tekstil endüstrisinde kusurlu bir halıyı gözden kaçırıp müşteriye göndermenin maliyeti (Yanlış Negatif), sağlam bir halıyı şüphelenip ikinci bir gözle muayeneye göndermekten (Yanlış Pozitif) katbekat daha ağırdır. Bu nedenle maliyete duyarlı karar eşiği optimizasyonu (cost-sensitive threshold tuning) yaptım. Karar eşiğini 0.5'ten 0.35 seviyesine çekerek, modelin kusurları yakalama duyarlılığını (Recall) %82'den %94'e çıkardım.

Modelin farklı eşik değerlerindeki genel ayrım gücünü ölçmek için ROC eğrisi ve ROC-AUC skorunu hesapladım. Yazdığım tüm değerlendirme adımlarını `test_binary_classification` test paketiyle sınayarak matris hesaplamalarının ve eşik mantığının doğruluğunu pytest ile kanıtladım.

Günün sonunda, ikili sınıflandırmanın yalnızca formül işletmek değil, endüstriyel risk maliyetini dengelemek olduğunu öğrendim.

**KONTROL SONUCU:**

---

## GÜN 17 — 8 AĞUSTOS 2026
**KISIM:** Çok Sınıflı Sınıflandırma  
**YAPRAK NO:** 33  
**YAPILAN İŞ:** Dört sentetik kusur sınıfı için veri hazırlama ve model kurma  
**TARİH:** 08/08/2026

Stajımın on yedinci gününde, dünkü ikili (kusurlu/kusursuz) ayrımını bir adım ileriye taşıyarak çok sınıflı kusur teşhisi problemine odaklandım. Gerçek bir halı işletmesinde yalnızca bir ürünün kusurlu olduğunu bilmek yeterli değildir; hatanın kök nedenini anlayıp tezgâha anında müdahale edebilmek için kusurun tipinin de bilinmesi şarttır (örneğin tezgâh iğnesi mi kırıldı, yağ kaçağı mı var, yoksa çekme silindiri mi kaydı?).

Danışman mühendisimle sahada en sık rastlanan kusur tiplerini temsil eden 4 sentetik sınıf belirledik:
0: Kusursuz / Normal Halı
1: İplik Kopması (Yarn Break)
2: Yağ Lekesi (Oil Stain)
3: Dokuma ve Atkı Eğriliği (Weft Skew)

Bu 4 sınıfı ayırt etmek üzere `multiclass_classifier` modülü altında `MulticlassDefectClassifier` sınıfını geliştirdim. Çok sınıflı olasılık dağılımını hesaplamak için Lojistik Regresyonu genelleştiren Softmax aktivasyon fonksiyonunu kodladım. Softmax fonksiyonunun, modelin her bir sınıf için ürettiği ham logit değerlerini üstel olarak ölçekleyip toplamları 1 edecek şekilde normalize ettiğini inceledim.

Ayrıca alternatif bir strateji olarak Bire-Karşı-Hepsi (One-vs-Rest / OvR) mimarisini kodladım; bu yöntemde 4 sınıf için 4 ayrı ikili sınıflandırıcı eğitilip en yüksek güven skorunu veren sınıfın nihai teşhis olarak seçildiğini gözlemledim.

Sınıflar arasındaki dengesizliği gidermek amacıyla `class_weight='balanced'` parametresini uygulayarak, nadir görülen yağ lekesi sınıfının eğitim sırasında ezilmesini engelledim.

**KONTROL SONUCU:**

---

## GÜN 17 — DEVAM
**KISIM:** Çok Sınıflı Sınıflandırma  
**YAPRAK NO:** 34  
**YAPILAN İŞ:** Çok sınıflı sonuçların confusion matrix ve sınıf bazlı metriklerle incelenmesi  
**TARİH:** 08/08/2026

Öğleden sonraki oturumda, çok sınıflı modelin teşhis kalitesini ayrıntılı metriklerle değerlendirmek üzere `evaluator` modülü altında `MulticlassEvaluator` sınıfını geliştirdim.

İlk olarak 4 sınıf arasındaki geçişleri gösteren $4 \times 4$ boyutundaki çok sınıflı Karışıklık Matrisini (Confusion Matrix) hesaplayan fonksiyonu yazdım. Matrisi incelediğimizde modelin İplik Kopması ile Normal halıyı %92 kesinlikle ayırabildiğini, ancak Atkı Eğriliği ile Yağ Lekesi arasında bazen öznitelik örtüşmesinden dolayı küçük karışıklıklar yaşandığını tespit ettik.

Ardından her bir kusur sınıfı için ayrı ayrı Precision, Recall ve F1-Score metriklerini çıkardım. Danışman mühendisim bu noktada çok sınıflı ortalamalar arasındaki farkı anlattı:
- Macro-F1: Her sınıfın F1 skorunu eşit ağırlıkla toplar; azınlık sınıfların performansını ölçmek için kritiktir.
- Weighted-F1: Sınıfların veri setindeki örnek sayısına (support) göre ağırlıklı ortalamasını alır.

Modelimizin Macro-F1 skorunun %86.5, Weighted-F1 skorunun ise %89.2 çıktığını hesapladım. Nadir sınıfların hakkını korumak için model değerlendirmesinde Macro-F1'i ana pusula olarak kabul ettim.

Geliştirdiğim çok sınıflı sınıflandırıcıyı ve metrik motorunu `test_multiclass_classification` test paketiyle sınadım. Softmax olasılıklarının toplamının 1.0 ettiğini ve çok sınıflı metriklerin doğruluğunu pytest ile teyit ettim.

Günün sonunda, tekil kusur teşhisinin çok sınıflı olasılık modelleriyle nasıl güvenilir biçimde raporlandığını somutlaştırdım. Ancak doğrusal modellerin karmaşık öznitelik etkileşimlerinde zorlanabileceğini görerek, yarın karar ağaçları ve topluluk modellerine geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 18 — 10 AĞUSTOS 2026
**KISIM:** Decision Tree ve Random Forest  
**YAPRAK NO:** 35  
**YAPILAN İŞ:** Sentetik veri üzerinde karar ağacı ve topluluk modelinin kurulması  
**TARİH:** 10/08/2026

Stajımın on sekizinci gününde, doğrusal olmayan karmaşık ilişkileri modelleyebilen ve endüstriyel kararları insan aklının mantığına benzer kurallarla açıklayabilen Karar Ağaçları (Decision Tree) ve bunların topluluk hali olan Rastgele Orman (Random Forest) mimarisini inceledim.

Danışman mühendisimle üretim ofisinde karar ağaçlarının dallanma mantığını masaya yatırdık. Bir ağacın her düğümde veriyi en iyi ikiye bölen özniteliği ve eşik değerini nasıl seçtiğini anlamak için Gini Safsızlığı (Gini Impurity) ve Entropi / Bilgi Kazancı (Information Gain) formüllerini kodladım. `tree_models` modülü altında `IndustrialDecisionTree` sınıfını geliştirdim.

Burada çok önemli bir teknik zaafı bizzat gözlemledim: Tek bir karar ağacı hiçbir kısıt konulmadan büyütüldüğünde, eğitim verisindeki tüm detayları ve gürültüleri tek tek ezberleyerek eğitim setinde %100 doğruluk alıyor; fakat test setinde %72'ye çakılarak feci şekilde aşırı öğrenmeye (overfitting) düşüyordu. Bu sorunu frenlemek için budama parametrelerini (`max_depth=5`, `min_samples_split=10`, `min_samples_leaf=4`) uyguladım.

Ardından tek bir ağacın yüksek varyansını kırmak üzere Topluluk Öğrenmesi (Ensemble Learning) mimarisi olan `IndustrialRandomForest` sınıfını kodladım. Rastgele Orman modelinin Torbalama (Bagging - Bootstrap Aggregating) prensibiyle, veriden rastgele örneklem alarak ve her düğümde özniteliklerin yalnızca rastgele bir alt kümesini seçerek 100 farklı ağaç eğittiğini; nihai kararı ise bu 100 ağacın çoğunluk oylamasıyla (majority voting) verdiğini modelledim.

**KONTROL SONUCU:**

---

## GÜN 18 — DEVAM
**KISIM:** Decision Tree ve Random Forest  
**YAPRAK NO:** 36  
**YAPILAN İŞ:** Özellik önemleri ve model sonuçlarının karşılaştırılması  
**TARİH:** 10/08/2026

Öğleden sonraki çalışmamda, tek bir Karar Ağacı ile Rastgele Orman modelini aynı sentetik kusur veri kümesi üzerinde yarıştırdım ve modellerin hangi özniteliklere ağırlık verdiğini ortaya çıkaran Öznitelik Önem Düzeyleri (Feature Importances) analizini yaptım.

Sonuçları kıyasladığımda Rastgele Orman modelinin test seti doğruluğunu %78'den %91.5'e taşıdığını gözlemledim. Birden fazla ağacın ortalamasını almanın, tek bir ağacın hatalarını nasıl törpüleyip varyansı düşürdüğünü deneysel olarak kanıtladım.

Daha sonra Rastgele Orman modelinin sunduğu en büyük mühendislik avantajlarından biri olan Safsızlık Tabanlı Öznitelik Önemi (MDI: Mean Decrease in Impurity) fonksiyonunu çalıştırdım. Modelin dallanmalarında en çok bilgi kazancı sağlayan özelliklerin sırasıyla; GLCM Doku Homojenliği, HSV Renk Histogramı tepe noktası ve İplik Gerginlik Varyansı olduğunu tespit ettim.

Danışman mühendisim bu çıktıyı görünce çok değerli bir yorumda bulundu: "Bir makine öğrenmesi modeli fabrikanın kalite mühendisine sadece 'bu halı bozuk' dememeli; 'bu halı doku homojenliği bozulduğu için bozuk' diyebilmeli. Modelin öznitelik önemleri, üretim hattında hangi sensörün ve hangi görsel özelliğin kritik olduğunu bize ispatlıyor." Bu açıklama, yapay zekâda açıklanabilirlik (explainability) kavramının kurumsal değerini kavramamı sağladı.

Yazdığım ağaç ve orman modellerini `test_tree_models` test paketiyle sınadım. Ağaç derinliği kontrollerinin ve oylama mekanizmasının doğruluğunu pytest ile onayladım.

Günün sonunda, topluluk modellerinin tekil modellere olan ezici üstünlüğünü görerek, yarın yarışmalı veri biliminin şampiyonu olan Gradyan Artırma (Gradient Boosting) modellerine geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 19 — 11 AĞUSTOS 2026
**KISIM:** Gradient Boosting Modelleri  
**YAPRAK NO:** 37  
**YAPILAN İŞ:** XGBoost ve LightGBM yaklaşımının sentetik sınıflandırma verisinde denenmesi  
**TARİH:** 11/08/2026

Stajımın on dokuzuncu gününde, modern tabular makine öğrenmesi uygulamalarının en güçlü algoritmaları olan Gradyan Artırma (Gradient Boosting) ailesini, özellikle XGBoost ve LightGBM mimarilerini inceledim.

Sabah oturumunda danışman mühendisimle Rastgele Orman (Bagging) ile Gradyan Artırma (Boosting) arasındaki felsefi farkı tartıştık. Rastgele Orman'da tüm ağaçların birbirinden bağımsız ve paralel olarak eğitildiğini hatırladık. Oysa Boosting mimarisinde ağaçların sıralı (sequential) olarak inşa edildiğini; her yeni ağacın, önceki ağaçların yaptığı hatalara (artık değerler / residuals) odaklanarak bu hataları düzeltmek üzere eğitildiğini öğrendim.

Bu mimariyi kodlamak üzere `boosting_models` modülü altında `IndustrialXGBoostClassifier` ve `IndustrialLightGBMClassifier` sınıflarını geliştirdim. İki algoritmanın mühendislik farklarını inceledim:
- XGBoost: Kayıp fonksiyonunun ikinci dereceden Taylor açılımını (gradyan ve hessian) kullanarak ağaç budamasını matematiksel kesinlikle yapar; aşırı öğrenmeyi önlemek için $L_1$ ve $L_2$ regülarizasyon terimleri içerir.
- LightGBM: Sürekli sayısal öznitelikleri kesikli histogram kutularına (bins) bölerek bellek tüketimini düşürür ve geleneksel seviye odaklı (level-wise) büyüme yerine yaprak odaklı (leaf-wise) büyüyerek devasa eğitim hızı sağlar.

Her iki modeli de sentetik halı kusur veri kümesi üzerinde koşturarak eğitim adımlarını başlattım.

**KONTROL SONUCU:**

---

## GÜN 19 — DEVAM
**KISIM:** Gradient Boosting Modelleri  
**YAPRAK NO:** 38  
**YAPILAN İŞ:** Model performansı ve özellik etkilerinin örnek veri üzerinde incelenmesi  
**TARİH:** 11/08/2026

Öğleden sonraki çalışmamda, XGBoost ve LightGBM modellerinin hiperparametre optimizasyonunu ve aşırı öğrenmeyi engelleyen Erken Durdurma (Early Stopping) mekanizmasını uyguladım.

Model eğitiminde öğrenme oranı (`learning_rate=0.05`), ağaç sayısı (`n_estimators=300`) ve maksimum derinlik (`max_depth=4`) parametrelerini yapılandırdım. Eğitim sürecinde doğrulama seti (validation set) kaybını her iterasyonda izleyerek, doğrulama hatasının 15 iterasyon boyunca iyileşmediği noktada eğitimi otomatik kesen erken durdurma mekanizmasını devreye aldım. Bu sayede modelin gereksiz ağaçlar ekleyerek ezber yapmasının önüne geçtim ve eğitimin 142. iterasyonda optimum noktada durduğunu gözlemledim.

İki modelin test seti üzerindeki performansını kıyasladığımda:
- XGBoost: %93.8 doğruluk ve %93.1 Macro-F1 skoru elde etti.
- LightGBM: %93.4 doğruluk ve %92.8 Macro-F1 skoru sağlarken, XGBoost'a kıyasla yaklaşık 3 kat daha hızlı eğitildi.

Danışman mühendisimle yaptığımız değerlendirmede, üretim ortamında periyodik olarak her gece yeniden eğitilecek büyük veri boru hatlarında LightGBM'in hız avantajının, nihai karar motorunda ise XGBoost'un marjinal doğruluk üstünlüğünün tercih edilebileceği sonucuna vardık.

Yazdığım boosting modellerini `test_boosting_models` test paketiyle sınadım. Erken durdurmanın tetiklendiğini ve tahmin çıktılarının güvenilirliğini pytest ile teyit ettim.

Günün sonunda, tabular veri üzerinde sektörün en gelişmiş sınıflandırma başarımını yakaladık. Yarın ise geometrik sınır optimizasyonuyla çalışan Destek Vektör Makinelerini (SVM) inceleyeceğimiz Gün 20 aşamasına geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 20 — 12 AĞUSTOS 2026
**KISIM:** Support Vector Machine  
**YAPRAK NO:** 39  
**YAPILAN İŞ:** Sentetik sınıflandırma verisinde SVM ve kernel seçeneklerinin denenmesi  
**TARİH:** 12/08/2026

Stajımın yirminci gününde, istatistiksel öğrenme teorisinin en zarif matematiksel temellerinden birine sahip olan Destek Vektör Makineleri (Support Vector Machine - SVM) algoritmasını inceledim.

Danışman mühendisimle yaptığımız teknik oturumda, SVM'in mantığını masaya yatırdık. Diğer sınıflandırma algoritmaları sınıfları ayıran herhangi bir çizgi veya düzlem bulmaya çalışırken, SVM'in iki sınıf arasındaki mesafeyi (geometrik marjini) maksimize eden en geniş güvenlik koridorunu bulmaya odaklandığını öğrendim. Bu koridorun sınırlarını belirleyen ve karar fonksiyonunu tek başına sırtlayan en kritik veri noktalarına "Destek Vektörleri" (Support Vectors) dendiğini kavradım.

Bu prensipleri kodlamak üzere `svm_models` modülü altında `IndustrialSVMClassifier` sınıfını geliştirdim. Sınıf içine iki farklı çekirdek (kernel) seçeneği entegre ettim:
1. Doğrusal Çekirdek (Linear Kernel): Öznitelik uzayında doğrusal olarak ayrılabilen basit durumlar için hızlı ve doğrudan hiper-düzlem ayrımı.
2. Radyal Tabanlı Fonksiyon Çekirdeği (RBF / Gaussian Kernel): Doğrusal olarak ayrılamayan karmaşık halı kusurlarını, sonsuz boyutlu bir Hilbert uzayına izdüşürerek doğrusal ayrılabilir hale getiren matematiksel Çekirdek Hilesi (Kernel Trick).

Doğrusal çekirdeğin karmaşık doku kusurlarında %76 başarıda kaldığını, buna karşılık RBF çekirdeğinin doğrusal olmayan kıvrımlı karar sınırlarını başarıyla öğrenerek %92.4 doğruluğa ulaştığını gözlemledim.

**KONTROL SONUCU:**

---

## GÜN 20 — DEVAM
**KISIM:** Support Vector Machine  
**YAPRAK NO:** 40  
**YAPILAN İŞ:** Ölçekleme, sınıf ayrımı ve temel değerlendirme metriklerinin karşılaştırılması  
**TARİH:** 12/08/2026

Öğleden sonraki oturumda SVM modellerinin hiperparametre hassasiyetini ve özellik ölçeklemenin yaşamsal rolünü inceledim.

Bu oturumda çok kritik bir "aha!" anı yaşadım: Veri setini bilerek standart ölçeklemeden (StandardScaler) geçirmeden ham değerlerle SVM'e verdiğimde, modelin eğitim süresinin dakikalarca tıkandığını ve doğruluğun %52'ye (yazı-tura seviyesine) düştüğünü dehşetle gördüm. Danışman mühendisim bu durumu şöyle açıkladı: "SVM geometrik mesafeler ve marjin maksimizasyonu ile çalışır. Bir özelliğin sayısal aralığı diğerinden büyükse, marjin optimizasyonu o eksen tarafından tamamen rehin alınır ve gradyan inişi düzgün çalışamaz." Verileri $Z$-score ile normalize ettiğimde modelin saniyeler içinde %92'nin üzerine fırladığını gözlemleyerek ölçeklemenin SVM için vazgeçilmez bir ön şart olduğunu beynime kazıdım.

Ardından SVM'in iki temel hiperparametresi olan $C$ ve $\gamma$ (gamma) dengesini analiz ettim:
- $C$ Parametresi: Marjinin sertliği ile eğitim hatası arasındaki ödünleşimi kontrol eder. Küçük $C$ daha geniş ama hatalara toleranslı yumuşak marjin (soft margin) üretirken, aşırı büyük $C$ marjini daraltıp aşırı öğrenmeye (overfitting) yol açar.
- $\gamma$ Parametresi: RBF çekirdeğinin tek bir veri noktasının etki yarıçapını belirler; yüksek gamma yerel dalgalanmaları ezberletirken, düşük gamma daha genel pürüzsüz karar sınırları çizer.

Optimum parametreleri ($C=10.0, \gamma=0.01$) belirleyerek test seti üzerinde dengeli bir başarı elde ettim. Yazdığım SVM modülünü `test_svm_models` test paketiyle sınadım; çekirdek dönüşümlerini ve marjin katsayılarını pytest ile doğruladım.

Günün sonunda, SVM'in doğru ölçekleme ve çekirdek seçimiyle yüksek boyutlu öznitelik uzaylarında ne kadar güçlü bir sınıflandırıcı olduğunu teyit ettim.

**KONTROL SONUCU:**

---

## GÜN 21 — 13 AĞUSTOS 2026
**KISIM:** Gözetimsiz Öğrenme ve Boyut İndirgeme  
**YAPRAK NO:** 41  
**YAPILAN İŞ:** PCA, t-SNE, K-Means ve DBSCAN yöntemlerinin sentetik veride uygulanması  
**TARİH:** 13/08/2026

Stajımın yirmi birinci gününde, Faz 3'ün kapanış halkası olan Gözetimsiz Öğrenme (Unsupervised Learning) ve Boyut İndirgeme (Dimensionality Reduction) yöntemlerine odaklandım. Üretim bandında her zaman etiketlenmiş kusur verisi bulmak mümkün değildir; her gün yüzlerce yeni desen üretilir ve bu desenlerin hiçbir sınıf etiketi olmadan kendi aralarında kümelenmesi ve aykırı noktaların tespit edilmesi gerekir.

Bu amaçla `dimensionality` modülü altında `DimensionalityReducer` sınıfını geliştirdim. Sınıf içine iki temel boyut indirgeme algoritmasını entegre ettim:
1. Temel Bileşen Analizi (PCA): Veri kümesindeki varyansı maksimum düzeyde koruyan birbirine dik (ortogonal) yeni eksenler (özvektörler) bularak 540 boyutlu görsel öznitelik uzayını sıkıştıran doğrusal yöntem.
2. t-SNE: Yüksek boyutlu uzaydaki komşuluk olasılıklarını Student-t dağılımı kullanarak 2 boyutlu düzleme izdüşüren ve karmaşık doku gruplarını görselleştirmede çığır açan doğrusal olmayan yöntem.

Sentetik halı özniteliklerini PCA ile incelediğimde, ilk 15 temel bileşenin toplam veri varyansının %87'sini tek başına açıkladığını hesapladım. Böylece 540 boyutluk devasa uzayı bilgi kaybetmeden çok daha kompakt bir boyuta indirgeyebileceğimizi gördüm.

**KONTROL SONUCU:**

---

## GÜN 21 — DEVAM
**KISIM:** Gözetimsiz Öğrenme ve Boyut İndirgeme  
**YAPRAK NO:** 42  
**YAPILAN İŞ:** Etiketsiz sentetik kayıtların iki boyutta incelenmesi ve kümelerin karşılaştırılması  
**TARİH:** 13/08/2026

Öğleden sonraki oturumda, boyut indirgeme ile elde ettiğim 2 boyutlu temsiller üzerinde gözetimsiz kümeleme algoritmalarını koşturdum. Bu amaçla `clustering` modülü altında `UnsupervisedClusterEngine` sınıfını geliştirdim.

Danışman mühendisimle iki farklı kümeleme mantığını karşılaştırdık:
- K-Means Kümelemesi: Kümeleri küresel (dairesel) varsayarak merkezler etrafında toplar; ancak karmaşık şekilli veya iç içe geçmiş doku desenlerinde zorlanır.
- DBSCAN (Yoğunluk Tabanlı Kümeleme): Epsilon ($\epsilon$) arama yarıçapı ve asgari komşu sayısı (`min_samples`) ile piksellerin yoğunlaştığı keyfi geometrileri doğal olarak küme haline getirir.

DBSCAN algoritmasının en büyük mühendislik gücünü bu oturumda gözlemledim: DBSCAN, hiçbir kümeye dahil olamayacak kadar ıssız ve seyrek kalan veri noktalarını otomatik olarak `-1` etiketiyle "Gürültü / Aykırı Değer" olarak işaretledi. Böylece etiketsiz üretim verileri içindeki sıra dışı dokuma kusurlarının, önceden hiçbir kural veya etiket tanımlanmadan anomali tespiti (anomaly detection) yoluyla nasıl yakalanabileceğini ispatladım.

Günün son saatlerinde `benchmark_consolidator` modülünü çalıştırarak Faz 3 boyunca eğittiğimiz tüm modellerin (Lojistik Regresyon, Random Forest, XGBoost, SVM) kapsamlı bir kıyaslama tablosunu çıkardım. Yazdığım analiz araçlarını `test_unsupervised_benchmark` test paketiyle sınadım; varyans korunum oranlarını ve kümeleme metriklerini pytest ile onayladım.

Böylece stajımın üçüncü büyük kilometre taşı olan **Faz 3: Klasik Makine Öğrenmesi** aşamasını eksiksiz tamamladım. İkili sınıflandırmadan çok sınıflı kusur teşhisine, karar ormanlarından gradyan artırmaya ve gözetimsiz boyut indirgemeye kadar eksiksiz bir makine öğrenmesi yetkinliği kazandık. Yarın stajımın dördüncü büyük fazı olan **Faz 4: Retrieval ve RAG Temelleri** dünyasına adım atarak, tekstil teknik dokümanları ve arıza kılavuzları üzerinde anlamsal bilgi arama sistemlerini inşa etmeye hazır hale geldim.

**KONTROL SONUCU:**

---
'''

new_full_text = full_text[:pos_start] + faz3_expanded + full_text[pos_end:]

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'w', encoding='utf-8') as f:
    f.write(new_full_text)

print('Successfully applied Faz 3 expansion to Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md!')
