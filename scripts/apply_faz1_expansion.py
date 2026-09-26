# -*- coding: utf-8 -*-
"""Apply humanized, deep engineering narrative for Faz 1 (Days 1 to 8 / Yapraks 1 to 16)."""

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'r', encoding='utf-8') as f:
    full_text = f.read()

pos_start = full_text.find('## GÜN 1 — 21 TEMMUZ 2026')
pos_end = full_text.find('## GÜN 9 — 30 TEMMUZ 2026')

assert pos_start != -1 and pos_end != -1, 'Day 1 or Day 9 marker not found!'

faz1_expanded = '''## GÜN 1 — 21 TEMMUZ 2026
**KISIM:** Firma ve Çalışma Ortamının Tanınması  
**YAPRAK NO:** 1  
**YAPILAN İŞ:** Üretim İşletmesinde Bilgisayar Mühendisliğinin Kullanım Alanlarının İncelenmesi  
**TARİH:** 21/07/2026

Stajımın ilk gününde Merinos halı üretim tesislerine adım attığımda, bilgisayar mühendisliğinin teorik dünyası ile devasa bir endüstriyel tesisin dinamik operasyonel gerçekliği arasındaki o keskin köprüyü ilk kez hissettim. Dokuma salonundaki tezgâhların ritmik temposu, üretim bantlarındaki kesintisiz malzeme akışı ve mühendislik birimlerinin operasyonel hareketliliği, üniversite sıralarında öğrendiğimiz yazılım kavramlarının sahada neye karşılık geldiğini sorgulamamı sağladı. İlk oryantasyon toplantımızda danışman mühendisimle yaptığımız teknik sohbette, bilgisayar mühendisliğinin bu tesisteki rolünün yalnızca klasik bir web arayüzü veya masaüstü formu geliştirmekten ibaret olmadığını; asıl katma değerin üretim hattından süzülen veriyi yakalamak, anlamlandırmak, görsel kalite denetimini otomatikleştirmek ve teknik bilgi birikimini akıllı sistemlerle operatörlerin hizmetine sunmak olduğunu gördüm.

İlk gün doğrudan aceleyle bir kod bloğu yazmak yerine, tesisteki bilgi ve veri akışının röntgenini çekmeye karar verdik. Üretim bandında yaptığım gözlemlerde, fabrikanın aslında heterojen veri üreten devasa bir ekosistem olduğunu fark ettim. Bir yanda dokuma tezgâhlarından anlık olarak üretilen mekanik telemetri verileri (iplik gerginliği, tezgâh devri, fırın kurutma sıcaklıkları), diğer yanda yüzey tarama kameralarının yakaladığı yüksek çözünürlüklü halı deseni görüntüleri ve son olarak tezgâh operatörlerinin başvurduğu teknik bakım el kitapları ile arıza kayıtları yer alıyordu. Bu üç veri türünün bilgisayar belleğinde ve algoritmik düzeyde bambaşka matematiksel temsiller gerektirdiğini analiz ettim: Sayısal sensör verileri zaman serileri ve skaler dizilerken, halı fotoğrafları çok boyutlu tensörler (piksel matrisleri), arıza dokümanları ise ayrık sembolik dil belirteçleriydi (token).

Mühendisimle yaptığımız değerlendirmede, endüstride yapılacak bir yapay zekâ veya veri projesinde en büyük hatanın her probleme aynı araçla yaklaşmak olduğunu tartıştık. Bir kalite kusuru için piksel seviyesinde bilgisayarlı görü gerekirken, tezgâhın plansız duruşlarını önlemek için sayısal istatistiksel modelleme, operatörün arıza anında bakım kılavuzundaki doğru prosedüre hızla erişebilmesi için ise metin arama yöntemlerinin devreye girmesi gerekiyordu. Bu farkındalık, stajım boyunca rastgele kütüphaneler denemek yerine, problemin doğasına ve verinin modalitesine göre mimari kurgulayan bir mühendislik disiplini edinmemin temel taşı oldu.

Günün teknik hazırlık safhasında kurumsal veri güvenliği prensiplerini masaya yatırdık. Gerçek bir endüstriyel ortamda stajyer olarak canlı SCADA ve PLC hatlarına doğrudan müdahale etmenin veya kurum içi gizli verileri dış ortama aktarmanın getireceği riskleri konuştuk. Bu doğrultuda, staj çalışmalarımızın tamamında geçerli olacak bir veri gerçekliği politikası belirledik. Bu kural uyarınca, canlı sistemlere bağlıymış gibi gerçek dışı iddialarda bulunmayacak; tüm mühendislik çalışmalarımızı üretim senaryolarını kusursuz taklit eden sentetik veri setleri, matematiksel simülasyonlar ve açık kaynaklı doğrulanmış varlıklar üzerinde yerel PoC (Proof-of-Concept) mimarisiyle inşa edecektik. Bu kurumsal yaklaşım, ilk günden itibaren hem etik hem de teknik olarak savunulabilir bir mühendislik zemini sağladı.

**KONTROL SONUCU:**

---

## GÜN 1 — DEVAM
**KISIM:** Firma ve Çalışma Ortamının Tanınması  
**YAPRAK NO:** 2  
**YAPILAN İŞ:** Veri Türlerinin Gözlemlenmesi ve Sonraki Teknik Çalışmalara Hazırlık  
**TARİH:** 21/07/2026

İlk yarıdaki kavramsal gözlemleri somut bir yazılım mühendisliği çıktısına dönüştürmek amacıyla öğleden sonraki oturumda yerel geliştirme iş istasyonumu yapılandırdım. İlk iş olarak Python ortamında modern tip güvenliği standartlarını uygulamak adına Pydantic kütüphanesini kullanarak endüstriyel veri taksonomisini modelledim. Bu kapsamda `DataModality` adında bir Enum sınıfı tanımlayarak fabrikada tespit ettiğimiz üç ana ekseni (`NUMERICAL`, `VISUAL`, `TEXTUAL`) kesin kurallarla birbirinden ayırdım.

Geliştirdiğim veri modelleme modülü içerisinde, her bir endüstriyel veri varlığını temsil eden `DataAsset` modelini kodladım. Bu model; benzersiz kimlik (`asset_id`), varlık adı (`name`), veri modalitesi (`modality`), kaynak sistem (`source_type`) ve dosya boyutu (`estimated_size_kb`) gibi alanları denetliyordu. Pydantic üzerinde uyguladığım kural kontrolleri sayesinde, örneğin negatif bir dosya boyutu veya tanımsız bir modalite girildiğinde sistemin çalışma zamanında anında `ValidationError` fırlatmasını sağladım. Verinin henüz depolama aşamasına gelmeden sözleşmelerle sıkı şekilde denetlenmesinin, büyük veri boru hatlarında sessiz hataların (silent failure) önüne nasıl geçtiğini bu ilk prototipte bizzat deneyimledim.

Ardından bu varlıkları bellek üzerinde yöneten `ObservationCatalog` sınıfını geliştirdim. Bu sınıf içinde yeni veri kaydı ekleyen `add_asset`, belirli bir modaliteye göre filtreleme yapan `filter_by_modality` ve sistemdeki toplam varlık ile boyut istatistiklerini çıkaran `get_summary` fonksiyonlarını yazdım. Tezgâh telemetrisi (`SimLoom`), muayene kamerası (`SimCamera`) ve teknik dokümantasyon (`SimDoc`) gibi sentetik tekstil varlıklarını bu kataloğa kaydedip JSON formatında dışa aktarma işlevini hayata geçirdim.

Yazdığım mantığın sağlamlığını garanti altına almak için test odaklı geliştirme (TDD) anlayışıyla `pytest` çatısını kullanarak `test_observation_catalog` test dosyasını hazırladım. Pozitif varlık kaydı, negatif boyut doğrulama hatası, modalite bazlı filtreleme ve JSON serileştirme döngüsünü içeren testlerin terminalde yeşil yandığını görmek, ilk günün teorik çıkarımlarını somut ve çalışan bir mühendislik ürününe bağlamamı sağladı. Günün sonunda danışman mühendisimle yaptığımız teknik kapanış değerlendirmesinde, yarın bu veri tiplerinin dosya seviyesindeki düzenleniş biçimlerini, yani CSV, JSON ve ilişkisel veri modellerini incelemeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 2 — 22 TEMMUZ 2026
**KISIM:** Veri Türleri ve Temel Veri Modelleme  
**YAPRAK NO:** 3  
**YAPILAN İŞ:** Veri Türlerinin Yapılarına Göre İncelenmesi  
**TARİH:** 22/07/2026

Stajımın ikinci gününde, ilk gün genel çerçevesini çizdiğim veri türlerini dosya formatları ve depolama mimarisi düzeyinde incelemeye başladım. Danışman mühendisimle üretim ortamında verilerin saklanma biçimlerini masaya yatırdığımızda verileri üç ana yapıya ayırdık: Sabit satır ve sütunlardan oluşan yapılandırılmış (structured) tablolar, esnek anahtar-değer ilişkisi sunan yarı yapılandırılmış (semi-structured) kayıtlar ve serbest metin veya görüntü gibi önceden tanımlı bir şemaya sığmayan yapılandırılmamış (unstructured) veriler.

Bu kavramları somutlaştırmak için Pydantic kütüphanesini kullanarak sentetik bir halı ürün kaydını temsil eden `CarpetProductRecord` modelini geliştirdim. Bu modelde ürün kodu, ürün grubu, taban malzemesi, ilme sıklığı ve ana renk kodu gibi nitelikleri kesin veri tipleriyle tanımladım. Satır ve sütun düzenine sahip klasik tablo yapısının (CSV), ürün kodu veya dokuma tarihi gibi alanları hızlıca filtrelemek ve indekslemek için son derece pratik olduğunu gözlemledim. Ancak bir halı ürününe ait birden fazla yüksek çözünürlüklü desen fotoğrafı, değişken tezgâh ayarları veya ucu açık kalite kontrol notları bağlamak istediğimizde iki boyutlu tablonun katı şema yapısının tıkandığını fark ettim.

Bu sınırlamayı aşmak için JSON formatının sağladığı esnekliği inceledim. JSON yapısında bir ürün kaydının altında bir liste halinde birden fazla görsel dosya adını veya iç içe nesneler halinde tezgâh telemetri okumalarını tutabildiğimi gördüm. Mühendisimle yaptığımız teknik tartışmada, tablodaki sütun zorunluluğunun şema katılığını getirdiğini, JSON’ın ise esneklik sağlamakla birlikte büyük veri yığınlarında depolama ve sorgulama maliyetini artırabileceğini değerlendirdik.

Günün bu bölümünde yapılandırılmamış verilerin (halı yüzey fotoğrafları) ise doğrudan veritabanında tutulmak yerine dosya sisteminde saklanıp, tablolarda yalnızca bunların dosya yollarının ve meta verilerinin tutulmasının endüstri standardı olduğunu öğrendim. Böylece verinin yapısına göre en verimli saklama stratejisinin nasıl kurgulanması gerektiğini netleştirdim.

**KONTROL SONUCU:**

---

## GÜN 2 — DEVAM
**KISIM:** Veri Türleri ve Temel Veri Modelleme  
**YAPRAK NO:** 4  
**YAPILAN İŞ:** CSV, JSON ve Temel Veri İlişkilerinin Örnek Veri Üzerinde Karşılaştırılması  
**TARİH:** 22/07/2026

Öğleden sonraki oturumda tekil kayıtların ötesine geçerek üretim süreçlerindeki ilişkisel veri modelleme mantığını ele aldım. Gerçek bir tekstil işletmesinde bir ürün kaydının tek başına izole yaşamadığını; üretim partisi (`batch`), dokuma tezgâhı ve kalite muayene raporlarıyla doğrudan ilişkili olduğunu gözlemledim. Bu ilişkiyi modellemek üzere `RelationalCarpetBatch` ve `InspectionAnnotation` sınıflarını geliştirdim. Ürün kimliğini (`product_id`) birincil anahtar (primary key) olarak kullanarak bir partiye ait birden fazla muayene kaydını bire-çok (one-to-many) ilişkiyle birbirine bağladım.

Daha sonra düz tablo verileri ile hiyerarşik JSON kayıtları arasında iki yönlü dönüşüm sağlayan `SchemaTransformer` sınıfını kodladım. Bu sınıf içinde yer alan `flatten_to_nested` fonksiyonu sayesinde, CSV'den okunan düz satırları ilişkisel hiyerarşiye dönüştürerek JSON nesnelerine çevirdim. Ayrıca `DataSerializer` sınıfını yazarak verilerin CSV ve JSON formatlarında diske yazılmasını ve diske yazılan dosyanın bozulmadan geri okunabilmesini (round-trip serialization) sağlayan fonksiyonları tamamladım.

Yazdığım mimariyi doğrulamak için `test_data_models` ve `test_models` test dosyalarını hazırladım. Testlerde özellikle ilişkisel anahtarların doğruluğunu, zorunlu alan kontrolünü ve CSV-JSON dönüşümünde veri tipi kaybı yaşanıp yaşanmadığını denetledim. Pytest ile çalıştırdığım tüm testlerin başarıyla geçmesi, tasarladığım veri modellerinin sağlamlığını kanıtladı.

Günün teknik kapanışında danışman mühendisimle önemli bir çıkarıma vardık: Veriyi ister CSV ister JSON olarak saklayalım, verinin biçimi tek başına çözmek istediğimiz problemi tanımlamaz. Aynı tablo veya görsel üzerinde kalite sınıflandırması, benzerlik araması veya arıza tahmini gibi tamamen farklı hedefler güdülebilir. Bu nedenle yarın doğrudan bir algoritmaya atlamak yerine, bir mühendislik problemini, girdilerini, çıktılarını ve başarı kriterlerini nasıl tanımlayacağımızı inceleyeceğimiz Gün 3 çalışmalarına geçmeyi kararlaştırdık.

**KONTROL SONUCU:**

---

## GÜN 3 — 23 TEMMUZ 2026
**KISIM:** Problemin Bilgisayar Mühendisliği Açısından Tanımlanması  
**YAPRAK NO:** 5  
**YAPILAN İŞ:** Problem, Girdi ve Beklenen Çıktının Belirlenmesinin İncelenmesi  
**TARİH:** 23/07/2026

Stajımın üçüncü gününde, bir endüstriyel problemi bilgisayar mühendisliği nosyonuyla formüle etme disiplini üzerine odaklandım. Sabah saatlerinde danışman mühendisimle planlama ofisinde yaptığımız teknik görüşmede masaya çok kritik bir soru geldi: "Üretim hattında veya katalogda iki halının birbirine benzediğini nasıl söyleriz?" İlk bakışta oldukça basit ve insani görünen bu sorunun, bir bilgisayar algoritması için ne kadar belirsiz ve kaygan bir zemin olduğunu tartıştık.

Mühendisim, "Benzerlik dediğinde neden bahsediyorsun? İki halı renk paleti açısından birebir aynı tonlarda olabilir ama biri modern geometrik, diğeri klasik madalyon desenli olabilir. Ya da tam tersi, desen şablonu tamamen aynıyken renkleri zıt olabilir. Bilgisayara 'bana benzer halıları getir' diyemezsin; bilgisayara hangi matematiksel uzayda neyi karşılaştıracağını kesin olarak söylemek zorundasın" dediğinde zihnimde büyük bir aydınlanma ("aha!" anı) yaşandı. Günlük dildeki sezgisel isteklerin, mühendislikte kesin girdi ve çıktı sınırlarıyla sınırlandırılması gerektiğini anladım.

Bu doğrultuda problemi resmileştirmek için `ProblemSpecification` sınıfını yazdım. Bu sınıf içinde problemin tipini (örneğin görsel benzerlik araması), sisteme verilecek girdiyi (sorgu halı görüntüsü ve taranacak katalog) ve sistemden beklenen çıktıyı (en yüksek benzerlik skoruna sahip ilk k adet ürün kimliği) kesin kurallarla tanımladım.

Ayrıca `EvaluationCriteria` sınıfını oluşturarak sisteme yalnızca doğruluk değil, endüstriyel gerçeklik kısıtları da ekledim. Bir üretim ortamında çalışan algoritmanın sonsuz zamanı yoktur; bu nedenle sistemin yanıt süresini (maksimum 200 ms) ve bellek sınırını da birer mühendislik başarı ölçütü olarak şemaya dahil ettim. Böylece bir yapay zekâ probleminin yalnızca model mimarisinden ibaret olmadığını, sistem sınırlarıyla yaşayan bir bütün olduğunu somutlaştırdım.

**KONTROL SONUCU:**

---

## GÜN 3 — DEVAM
**KISIM:** Problemin Bilgisayar Mühendisliği Açısından Tanımlanması  
**YAPRAK NO:** 6  
**YAPILAN İŞ:** Başarı Ölçütü, Basit Başlangıç Yöntemi ve Değerlendirme Mantığının İncelenmesi  
**TARİH:** 23/07/2026

Öğleden sonraki çalışmamda, belirlenen hedeflerin başarısının nasıl ölçüleceğini ve ilk çözüm adımının (baseline) nasıl kurgulanması gerektiğini inceledim. Danışman mühendisim, yapay zekâ projelerinde sıkça düşülen en büyük tuzağın, problemin en başında en karmaşık derin öğrenme modeline veya devasa sinir ağlarına sarılmak olduğunu anlattı. "Önce elinde en basit, kural tabanlı veya istatistiksel bir referans noktası (baseline) olmalı ki, daha sonra kuracağın karmaşık modellerin gerçekten bir katma değer üretip üretmediğini ispatlayabilesin" tavsiyesinde bulundu.

Bu tavsiye doğrultusunda `RuleBasedBaselineClassifier` sınıfını geliştirdim. Bu sınıf, sentetik halı kayıtlarını karmaşık yapay zekâ yerine temel renk ortalamaları ve basit piksel eşik kurallarıyla sınıflandıran sezgisel bir başlangıç algoritması uyguluyordu. Ardından bu baseline modelin başarımını ölçmek üzere `BaselineEvaluator` sınıfını yazdım. Bu sınıf içinde doğruluk (accuracy), kesinlik (precision) ve duyarlılık (recall) metriklerini hesaplayan fonksiyonları kodladım.

Yaptığımız sentetik deneyde, kural tabanlı basit modelin net ve bariz desenlerde %75 gibi makul bir doğruluk verdiğini, ancak desenlerde hafif bir kayma, renk tonunda gölgelenme veya gürültü oluştuğunda hızla çuvalladığını gözlemledim. İşte bu başarısızlık anı, makine öğrenmesi ve yapay zekâya neden ihtiyaç duyduğumuzun somut mühendislik kanıtı oldu. Karmaşık modellerin gerekliliği soyut bir heves olmaktan çıkıp, ölçülmüş bir ihtiyaca dönüştü.

Geliştirdiğim problem spesifikasyonunu ve değerlendirme fonksiyonlarını `test_problem_spec` birim testleriyle sınadım. Parametrelerin doğruluğunu ve sınır kısıtlarını başarıyla doğruladım. Günün sonunda, sağlam bir problem tanımı ve baseline olmadan yazılım geliştirilemeyeceğini kavrayarak, yarın bu algoritmaları koşturacağımız Python geliştirme altyapısını ve sözleşmelerini kuracağımız Gün 4 aşamasına geçmeye hazır hale geldim.

**KONTROL SONUCU:**

---

## GÜN 4 — 24 TEMMUZ 2026
**KISIM:** Python Geliştirme Ortamı ve Veri Sözleşmesi  
**YAPRAK NO:** 7  
**YAPILAN İŞ:** Python, Sanal Ortam ve Paket Yönetiminin İncelenmesi  
**TARİH:** 24/07/2026

Stajımın dördüncü gününde, önceki günlerde teorik sınırlarını çizdiğimiz veri ve problem modellerini hayata geçirecek profesyonel yazılım geliştirme ortamının inşasına odaklandım. Danışman mühendisimle bir araya geldiğimizde, veri bilimi ve yapay zekâ ekosisteminde Python'ın neden fiili standart haline geldiğini konuştuk. Python'ın C++ gibi donanıma yakın diller kadar hızlı olmadığını, ancak zengin bilimsel kütüphaneleri ve hızlı prototipleme kabiliyeti sayesinde algoritma geliştirme maliyetini dramatik biçimde düşürdüğünü; performans kritik bölümlerin ise arka planda C/C++ ile derlenmiş kütüphaneler (NumPy, OpenCV) tarafından kotarıldığını analiz ettik.

Mühendisim bu noktada çok hayati bir kurumsal prensibin altını çizdi: "Geliştirme yaparken asla işletim sisteminin global Python ortamına paket yükleme. Birkaç hafta sonra farklı projelerin farklı kütüphane sürümleri çakışır ve 'benim bilgisayarımda çalışıyordu' kaosu başlar." Bu disiplinle, Python'ın yerleşik `venv` modülünü kullanarak tamamen yalıtılmış bir sanal ortam kurdum.

Ardından ortamın donanım ve yazılım uyumluluğunu otomatik olarak denetleyen `VirtualEnvChecker` ve `EnvironmentProfiler` sınıflarını yazdım. Bu sınıflar; sistemdeki CPU çekirdek sayısı, RAM miktarı, işletim sistemi mimarisi ve aktif Python sürümünün projenin asgari gereksinimlerini karşılayıp karşılamadığını denetleyen fonksiyonlar barındırıyordu.

Kullanılan tüm kütüphanelerin tam sürümlerini kayıt altına alarak deterministik ve tekrar üretilebilir bir ortam sağladım. Böylece projenin başka bir mühendisin iş istasyonunda veya bir sunucuda tek komutla sıfır hatayla ayağa kalkmasını garanti altına aldım.

**KONTROL SONUCU:**

---

## GÜN 4 — DEVAM
**KISIM:** Python Geliştirme Ortamı ve Veri Sözleşmesi  
**YAPRAK NO:** 8  
**YAPILAN İŞ:** Jupyter Notebook, .py Dosyası ve Temel Python Uygulaması  
**TARİH:** 24/07/2026

Öğleden sonraki oturumda, veri projelerinde sıklıkla birbirine karıştırılan iki çalışma aracının mimari sınırlarını netleştirdim: Jupyter Notebook ve modüler `.py` dosyaları. Danışman mühendisimle yaptığımız analizde, Jupyter Notebook'un interaktif veri görselleştirme, hızlı grafik çizimi ve adım adım deney takibi için harika bir laboratuvar olduğunu; ancak hücrelerin sırasız çalıştırılabilmesi ve gizli durum (hidden state) değişkenleri barındırabilmesi nedeniyle üretim sistemlerine doğrudan sürülemeyeceğini tartıştık. Kalıcı, test edilebilir ve yeniden kullanılabilir kodların mutlaka modüler Python paketleri halinde yapılandırılması gerektiği sonucuna vardık.

Bu doğrultuda sistemin veri alışveriş güvenliğini sağlamak için veri sözleşmeleri modülünü geliştirdim. Bu modül içinde tezgâh telemetrisi için `LoomTelemetryContract` ve görsel muayene kayıtları için `CarpetInspectionContract` sınıflarını kodladım. Bu sözleşmeler, gelen verilerde iplik gerginliğinin belirlenen fiziksel sınırların dışında olması (örneğin negatif gerginlik veya aşırı yüksek basınç) ya da zorunlu alanların eksik gelmesi durumunda derhal hata fırlatarak sistemi korumaya alıyordu.

Geliştirdiğim ortam denetleyiciyi ve veri sözleşmelerini `test_data_contracts` ve `test_env_checker` test dosyalarıyla sınadım. Pytest ile çalıştırdığım testlerde, sınır dışı veri girişlerinin sözleşmeler tarafından başarıyla yakalandığını ve sanal ortam profilinin doğru raporlandığını teyit ettim.

Günün sonunda hem deneysel araştırma (Notebook) hem de endüstriyel üretim kodu (modüller ve sözleşmeler) arasındaki dengeyi başarıyla kurdum. Ancak tek tek nesneler üzerinde doğrulama yapmanın yeterli olmadığını, binlerce satırlık gerçek veri tablolarının okunması, temizlenmesi ve işlenmesi gerektiğini görerek, yarın Pandas ile veri hattı ve veri kalitesi denetimini yapacağımız Gün 5 çalışmalarına geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 5 — 25 TEMMUZ 2026
**KISIM:** Pandas, Veri Hattı ve Veri Kalitesi  
**YAPRAK NO:** 9  
**YAPILAN İŞ:** CSV ve JSON Örneklerinin Okunması ve Ortak Şemaya Getirilmesi  
**TARİH:** 25/07/2026

Stajımın beşinci gününde, bir önceki gün kurduğumuz veri sözleşmelerini çok kaynaklı veri entegrasyonu problemine uyguladım. Endüstriyel bir işletmede verilerin hiçbir zaman tek bir kaynaktan tertemiz gelmediğini; bir yanda tezgâh loglarının CSV formatında tutulurken diğer yanda üretim planlama ve katalog bilgilerinin JSON akışlarıyla geldiğini gözlemledim. Bu iki farklı dünyayı birleştirmek amacıyla proje kapsamında hazırlanan sentetik `raw_production_logs.csv` ve `raw_catalog_feed.json` dosyaları üzerinde çalışmaya başladım.

İlk olarak Pandas kütüphanesini kullanarak her iki veri kaynağını bellek üzerine aldım. Dosyaları incelerken karşılaştığım ilk büyük zorluk, alan adlarının ve tiplerinin uyuşmamasıydı. Örneğin CSV dosyasında `loom_id` ve `speed_rpm` olarak adlandırılan sütunların, JSON tarafında `tezgah_kodu` ve `devir_hizi` olarak tutulduğunu tespit ettim. Bu heterojenliği gidermek için `DataNormalizer` sınıfını ve kolon eşleme mantığını kodladım. Eşleme tablosu sayesinde farklı isimlerdeki sütunları ortak bir endüstriyel veri şemasına dönüştürdüm.

Ardından `ETLPipeline` sınıfını geliştirdim. Bu sınıf, okuma (`extract`), dönüştürme (`transform`) ve yükleme (`load`) aşamalarını modüler fonksiyonlar halinde yürütüyordu.

Veri hattı çalışırken eksik sütunlu veya veri tipi bozulmuş kayıtlarla karşılaşıldığında tüm süreci çökertmek yerine, hatalı satırları karantina mekanizmasıyla (`quarantine`) ayıracak bir mantık kurdum. Bozuk kayıtların hangi sebeple (eksik alan, tip uyumsuzluğu) reddedildiğini metaveri olarak kaydedip temiz verileri birleştirilmiş bir veri çerçevesine aktardım.

**KONTROL SONUCU:**

---

## GÜN 5 — DEVAM
**KISIM:** Pandas, Veri Hattı ve Veri Kalitesi  
**YAPRAK NO:** 10  
**YAPILAN İŞ:** Veri Normalizasyonu, Hatalı Kayıtların Ayrılması ve Kalite Kontrolü  
**TARİH:** 25/07/2026

Öğleden sonraki çalışmamda veri kalitesini sistematik bir denetime bağlamak üzere `DataQualitySuite` sınıfını inşa ettim. Danışman mühendisimle yaptığımız teknik incelemede, makine öğrenmesi modellerinin "çöp girerse çöp çıkar" (garbage in, garbage out) ilkesiyle çalıştığını; bu nedenle veri hattının çıkış kapısında sıkı bir kalite kontrol filtresi olması gerektiğini tartıştık.

Yazdığım `DataQualitySuite` sınıfına; eksik değer oranını hesaplayan, benzersiz anahtarların tekilliğini doğrulayan ve sayısal sütunların beklenen değer aralığında olup olmadığını denetleyen doğrulama kuralları ekledim. Örneğin tezgâh sıcaklığının fiziksel olarak imkânsız bir değere ulaşması durumunda kalite raporunun anında uyarı üretmesini sağladım.

Ayrıca büyük veri kümelerinde bellek tüketiminin nasıl optimize edilebileceğini araştırmak üzere `memory_analyzer` modülünü yazdım. Pandas'ın varsayılan olarak metin sütunlarını `object` veri tipinde tuttuğunu ve bunun devasa bellek tükettiğini gözlemledim. Bu sütunları `category` tipine dönüştürerek bellek kullanımında %60'a varan bir tasarruf elde ettiğimi ölçümledim.

Tüm bu veri hattını doğrulamak için `test_etl_pipeline` ve `test_quality_validation` test paketlerini çalıştırdım. Pytest ortamında; boş veri gelmesi, hatalı tip barındıran CSV satırları ve karantinaya alma süreçlerinin beklendiği gibi kusursuz işlediğini teyit ettim.

Günün sonunda, dağınık dosyalardan başlayıp temiz, normalize edilmiş ve kalitesi doğrulanmış bir veri seti elde ettik. Ancak tablo işlemlerinin satır satır mantığının büyük matris operasyonlarında ve görüntü işlemede yetersiz kalacağını değerlendirerek, yarın NumPy ve vektörel hesaplama dünyasını inceleyeceğimiz Gün 6 aşamasına geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 6 — 27 TEMMUZ 2026
**KISIM:** NumPy ve Vektörel Hesaplama  
**YAPRAK NO:** 11  
**YAPILAN İŞ:** Python Listeleri, NumPy Dizileri ve Vektörel İşlemlerin İncelenmesi  
**TARİH:** 27/07/2026

Stajımın altıncı gününde, veri işlemede performansın ve matematiksel hesaplamanın kalbi olan NumPy kütüphanesini ve vektörel hesaplama prensiplerini derinlemesine inceledim. Sabah saatlerinde danışman mühendisimle bilgisayar mimarisinde bellek yönetimi üzerine çok eğitici bir tartışma yaptık. Standart Python listelerinin aslında nesne göstericilerinden (pointer) oluşan dinamik yapılar olduğunu, bu nedenle bellekte dağınık yerleştiğini ve her elemana erişimde fazladan bellek atlamaları (cache miss) yaşandığını anlattı. Buna karşılık NumPy'nin `ndarray` yapısının C dilinde olduğu gibi bellekte ardışık ve tek tip (contiguous array) yerleştiğini öğrendim.

Bu teorik farkı kod seviyesinde görmek için temel dizi operasyonlarını, matris çarpımlarını ve yayınlama (broadcasting) kurallarını kodladım. Farklı boyutlardaki dizilerin NumPy tarafından otomatik olarak nasıl hizalandığını inceledim.

Ardından bu mimari farkın endüstriyel boyuttaki etkisini kanıtlamak amacıyla `VectorizationBenchmark` sınıfını geliştirdim. Bir milyon elemanlı sentetik telemetri dizisi üzerinde aynı matematiksel işlemi (skaler çarpım ve toplama); önce geleneksel Python `for` döngüsüyle, ardından NumPy'nin vektörel SIMD (Single Instruction, Multiple Data) yetenekleriyle koşturdum.

Sonuçları ekrana yazdırdığımda çarpıcı bir mühendislik gerçeğiyle karşılaştım: Saf Python döngüsü yaklaşık 180 milisaniye sürerken, NumPy vektörel operasyonu işlemi sadece 2.5 milisaniyede tamamladı. Aradaki 70 katı aşkın bu hız farkı, endüstriyel gerçek zamanlı sistemlerde neden döngülerden kaçınıp vektörize operasyonlara yönelmemiz gerektiğinin tartışmasız bir ispatı oldu.

**KONTROL SONUCU:**

---

## GÜN 6 — DEVAM
**KISIM:** NumPy ve Vektörel Hesaplama  
**YAPRAK NO:** 12  
**YAPILAN İŞ:** Görüntünün Matris Yapısının ve Piksel İşlemlerinin İncelenmesi  
**TARİH:** 27/07/2026

Öğleden sonraki çalışmamda, öğrendiğim matris ve tensör kavramlarını dijital görüntü dünyasına uyguladım. Danışman mühendisim, ekranda gördüğümüz rengarenk bir halı deseninin bilgisayar işlemcisi için aslında üç boyutlu bir sayısal tensörden başka bir şey olmadığını hatırlattı. Bu yapıyı incelemek amacıyla `ImageMatrixHandler` sınıfını geliştirdim.

Görüntünün yükseklik, genişlik ve 3 renk kanalından (H, W, C) oluşan bir `ndarray` olduğunu, her bir piksel değerinin 8-bit işaretsiz tamsayı (`uint8`) tipinde 0 ile 255 arasında değiştiğini modelledim. `ImageMatrixHandler` sınıfı içinde parlaklık ayarlayan `adjust_brightness` ve renk kanallarını manipüle eden fonksiyonlar yazdım.

Bu geliştirme sırasında çok öğretici bir "aha!" anı yaşadım: Görüntü parlaklığını artırmak için piksel matrisine doğrudan 50 eklediğimde, değeri 220 olan açık renkli piksellerin 270 olmak yerine 14 değerine düştüğünü ve görüntüde aniden garip siyah lekeler oluştuğunu gördüm. Mühendisimle incelediğimizde bunun tipik bir `uint8` taşması (arithmetic overflow) olduğunu tespit ettik; çünkü 8-bit tamsayılar 255'ten sonra sıfırlanıyordu. Bu sorunu çözmek için matrisi önce float tipine çevirip işlemi yaptıktan sonra `np.clip(val, 0, 255)` fonksiyonuyla sınırlandırıp tekrar `uint8`'e dönüştürme pratiğini uyguladım.

Yazdığım görüntü matrisi fonksiyonlarını ve taşma kontrollerini `test_array_ops` birim testleriyle doğruladım.

Günün sonunda, görüntülerin sayısal birer matris olduğunu ve piksel işlemlerinin saf lineer cebir operasyonlarıyla nasıl yönetildiğini somutlaştırdım. Ancak pikselleri matris olarak temsil etmenin ötesinde, iki farklı desenin veya sensör kaydının birbirine ne kadar yakın olduğunu matematiksel olarak hesaplayabilmek gerektiğini değerlendirerek, yarın uzaklık ve benzerlik metriklerini inceleyeceğimiz Gün 7 aşamasına geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 7 — 28 TEMMUZ 2026
**KISIM:** Uzaklık ve Benzerlik Yöntemleri  
**YAPRAK NO:** 13  
**YAPILAN İŞ:** Euclidean, Manhattan ve Cosine Yaklaşımlarının Küçük Sayısal Örneklerle İncelenmesi  
**TARİH:** 28/07/2026

Stajımın yedinci gününde, iki sayısal veri noktasının veya öznitelik vektörünün birbirine ne kadar benzediğini ölçen temel uzaklık ve benzerlik metriklerini masaya yatırdım. Danışman mühendisimle yaptığımız teknik oturumda, makine öğrenmesi ve yapay zekâ algoritmalarının çoğunun (kümeleme, sınıflandırma, arama) özünde bir "vektör uzayında mesafe hesaplama" problemine dayandığını konuştuk.

Bu matematiksel temelleri kodlamak amacıyla `DistanceSimilarityMetrics` sınıfını geliştirdim. Bu sınıf içinde üç temel metriği fonksiyonel olarak tanımladım:
1. Öklid Uzaklığı (`euclidean_distance`): İki nokta arasındaki kuş uçuşu geometrik doğrusal mesafeyi hesaplar.
2. Manhattan Uzaklığı (`manhattan_distance`): Yalnızca eksenler boyunca ızgara tarzı hareketle mutlak farkların toplamını alır.
3. Kosinüs Benzerliği (`cosine_similarity`): Vektörlerin mutlak büyüklüklerinden bağımsız olarak aralarındaki açının kosinüsünü bularak yönsel benzerliği ölçer.

Geliştirme esnasında danışman mühendisimle kritik bir deney yaptık: İki halı kaydını karşılaştırırken özelliklerden birinin ilme sayısı (örneğin 10.000 ilme), diğerinin ise halı kalınlığı (örneğin 1.2 cm) olduğunu varsaydık. Bu iki özelliği doğrudan Öklid formülüne soktuğumuzda, ilme sayısındaki küçük bir farkın kalınlık bilgisini tamamen ezip yok ettiğini gördük. Bu tehlikeyi bertaraf etmek için `FeatureStandardScaler` sınıfını yazdım. Özellikleri ortalaması 0, standart sapması 1 olacak şekilde Z-score dönüşümüne tabi tutarak ölçeklemenin (scaling), mesafe hesaplamalarında ne kadar hayati bir ön koşul olduğunu kanıtladım.

**KONTROL SONUCU:**

---

## GÜN 7 — DEVAM
**KISIM:** Uzaklık ve Benzerlik Yöntemleri  
**YAPRAK NO:** 14  
**YAPILAN İŞ:** Covariance ve Mahalanobis Uzaklığının Temel Mantığının İncelenmesi  
**TARİH:** 28/07/2026

Öğleden sonraki oturumda standart uzaklık metriklerinin tıkandığı daha karmaşık bir problemi ele aldım: Değişkenler arasındaki korelasyon ve boyut laneti. Danışman mühendisim, gerçek üretim verilerinde değişkenlerin birbirinden bağımsız olmadığını; örneğin iplik gerginliği ile tezgâh motor torkunun çoğu zaman birlikte artıp azaldığını anlattı. Öklid mesafesinin bu iki değişkeni tamamen bağımsız varsayarak aynı bilgiyi iki kez hesaba kattığını açıkladı.

Bu sorunu çözmek için verilerin kovaryans matrisini hesaba katan Mahalanobis uzaklığı mantığını inceledim. Değişkenler arasındaki korelasyonu ve eksenlerin varyansını formüle dahil ederek, verinin gerçek dağılım geometrisine uygun bir mesafe metriği elde etmenin teorisini öğrendim.

Ardından çok boyutlu uzayların getirdiği tehlikeleri analiz etmek üzere `CurseOfDimensionalityAnalyzer` sınıfını geliştirdim. Sentetik olarak 2 boyuttan 500 boyuta kadar rastgele noktalar üreterek, en yakın komşu ile en uzak komşu arasındaki mesafe oranını hesaplattım. Boyut arttıkça bu oranın hızla 1'e yaklaştığını; yani yüksek boyutlu uzaylarda tüm noktaların birbirinden neredeyse eşit uzaklıkta görünmeye başladığını deneysel olarak gözlemledim. Bu deney, ilerleyen günlerde görüntü ve metin gömmeleriyle (embeddings) çalışırken boyut indirgemenin neden zorunlu olduğunu anlamamı sağlayan büyük bir "aha!" anı oldu.

Geliştirdiğim metrikleri ve ölçekleyicileri `test_distance_similarity` birim testleriyle sınadım. Tüm testlerin yeşil yanmasıyla hesaplama doğruluğunu garantiye aldım.

Günün sonunda sayısal mesafelerin doğasını kavrayarak, yarın modelleme öncesinde verilerin dağılımını, aykırı değerlerini ve ilişkilerini görselleştireceğimiz Keşifsel Veri Analizi (EDA) aşamasına geçmeye hazırlandım.

**KONTROL SONUCU:**

---

## GÜN 8 — 29 TEMMUZ 2026
**KISIM:** Keşifsel Veri Analizi  
**YAPRAK NO:** 15  
**YAPILAN İŞ:** Dağılım, Histogram, Boxplot ve Aykırı Değerlerin İncelenmesi  
**TARİH:** 29/07/2026

Stajımın sekizinci gününde, Faz 1'in kapanış halkası olan Keşifsel Veri Analizi (EDA) metodolojisini uyguladım. Danışman mühendisimle yaptığımız teknik değerlendirmede, bir veri setini sadece tablodaki kuru sayılar olarak görmenin büyük yanılgılara yol açabileceğini; verinin istatistiksel dağılımını, merkezsel eğilimlerini ve olağan dışı uç noktalarını görselleştirmeden sağlıklı bir yapay zekâ modeli kurulamayacağını konuştuk.

Bu amaçla `IndustrialEDAToolkit` sınıfını geliştirdim. Sınıf içine ilk olarak veri serilerinin temel karakteristiğini çıkaran `compute_descriptive_stats` fonksiyonunu yazdım. Bu fonksiyon; ortalama, medyan, standart sapma, minimum-maksimum değerlerin yanı sıra dağılımın asimetrisini ölçen çarpıklık (skewness) ve uç değer yoğunluğunu gösteren basıklık (kurtosis) değerlerini hesaplıyordu.

Ardından görselleştirme araçlarına geçerek histogram ve kutu grafiği (boxplot) analizlerini kurguladım. Kutu grafiği üzerinde çeyrekler açıklığı (IQR: Interquartile Range) yöntemini uygulayan `detect_outliers_iqr` fonksiyonunu kodladım. Birinci çeyreğin ($Q_1$) $1.5 \\times \\text{IQR}$ altı ve üçüncü çeyreğin ($Q_3$) $1.5 \\times \\text{IQR}$ üstü değerleri otomatik olarak aykırı değer (outlier) olarak işaretledim.

Bu analiz sırasında mühendisim çok önemli bir endüstriyel uyarıda bulundu: "Her aykırı değer veri hatası veya çöp değildir. Bazen tezgâhtaki nadir bir mekanik zorlanma veya gerçek bir üretim kusuru da kendini istatistiksel aykırı değer olarak gösterir. Bu yüzden aykırı değerleri körü körüne silmek yerine, arkasındaki mühendislik nedenini sorgulamalısın." Bu öğüt, verilere ezbere bir veri bilimci gibi değil, sahayı anlayan bir mühendis gibi yaklaşmam gerektiğini zihnime kazıdı.

**KONTROL SONUCU:**

---

## GÜN 8 — DEVAM
**KISIM:** Keşifsel Veri Analizi  
**YAPRAK NO:** 16  
**YAPILAN İŞ:** Scatter Plot, Korelasyon ve Küçük EDA Uygulamasının Yapılması  
**TARİH:** 29/07/2026

Öğleden sonraki oturumda tek değişkenli analizlerden iki değişken arasındaki ilişkileri inceleyen bivariate analizlere geçtim. Değişken çiftleri arasındaki etkileşimi görselleştirmek için serpilme diyagramı (scatter plot) mantığını inceledim. Ardından `IndustrialEDAToolkit` sınıfı içine Pearson ve Spearman korelasyon katsayılarını hesaplayıp bir korelasyon matrisi üreten `compute_correlation_matrix` fonksiyonunu ekledim.

Sentetik üretim verileri üzerinde yaptığımız korelasyon testinde, örneğin fırın kurutma sıcaklığı ile nem oranı arasında güçlü bir negatif korelasyon, iplik gerginliği ile kopuş riski arasında ise pozitif bir korelasyon olduğunu gözlemledim.

Burada danışman mühendisimle istatistiğin altın kuralını tartıştık: "Korelasyon asla nedensellik (causation) anlamına gelmez." İki değişkenin birlikte hareket etmesinin birinin diğerine sebep olduğunu tek başına ispatlamayacağını, arkada ölçülmemiş üçüncü bir çevresel faktör olabileceğini bilerek temkinli yorum yapmanın önemini konuştuk.

Günün sonunda tüm EDA araçlarını birleştiren entegre bir veri analiz raporu fonksiyonu yazarak sentetik veri setinin genel sağlık karnesini çıkardım. Yazdığım analiz araçlarını `test_eda_toolkit` test paketiyle denetledim; çeyrek hesaplamalarının ve korelasyon değerlerinin sınır koşullarda hatasız çalıştığını pytest ile doğruladım.

Böylece stajımın ilk 8 gününü kapsayan **Faz 1: Problem, Veri ve Geliştirme Temelleri** aşamasını eksiksiz tamamladım. Veri taksonomisinden sözleşmelere, Pandas veri hatlarından NumPy vektörizasyonuna, uzaklık metriklerinden EDA'ya kadar sağlam bir zemin inşa ettik. Yarın stajımın ikinci büyük fazı olan **Faz 2: Bilgisayarlı Görü** dünyasına adım atarak, doğrudan halı yüzey görüntülerinin OpenCV ile pikseller düzeyinde işlenmesine geçmeye karar verdim.

**KONTROL SONUCU:**

---
'''

new_full_text = full_text[:pos_start] + faz1_expanded + full_text[pos_end:]

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'w', encoding='utf-8') as f:
    f.write(new_full_text)

print('Successfully applied Faz 1 expansion to Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md!')
