# MERİNOS — 40 GÜNLÜK STAJ DEFTERİ
## 80 Yapraklık Genişletilmiş Ana Sürüm

> **Sabit veri sınırı:** Bu defterde canlı SCADA/PLC sistemlerine bağlanıldığı, gerçek sensör telemetrisi kullanıldığı, gerçek tezgâh hata loglarının işlendiği veya kurum içi veri tabanlarına erişildiği iddia edilmez. Gerekli örneklerde yalnız sentetik, çalışma amacıyla hazırlanmış veya kullanımına izin verilmiş veriler kullanılmıştır.

> **Anlatım standardı:** Günler birbirinden kopuk ders başlıkları olarak değil; önceki çalışmanın oluşturduğu problemden sonraki mühendislik ihtiyacına geçecek şekilde **problem → veri → baseline → alternatif → uygulama → test → gözlem → sınırlama → sonraki problem** zinciriyle yazılmıştır.

---

## GÜN 1 — 21 TEMMUZ 2026
**KISIM:** Firma ve Çalışma Ortamının Tanınması  
**YAPRAK NO:** 1  
**YAPILAN İŞ:** Üretim İşletmesinde Bilgisayar Mühendisliğinin Kullanım Alanlarının İncelenmesi  
**TARİH:** 21/07/2026

Stajımın ilk gününde öncelikle çalışma ortamını tanımaya ve bir üretim işletmesinde bilgisayar mühendisinin hangi alanlarda görev alabileceğini anlamaya çalıştım. Yanında çalıştığım mühendis, bilgisayar mühendisliğinin yalnızca masaüstü veya web uygulaması geliştirmekten ibaret olmadığını; üretim yapan bir işletmede veri işleme, raporlama, görüntü analizi, bilgi sistemleri ve otomasyon gibi farklı alanlarda da kullanılabildiğini anlattı. İlk gün doğrudan bir yazılım geliştirmeye başlamak yerine, ilerleyen günlerde karşılaşacağım teknik konuları daha doğru değerlendirebilmem için önce çalışma ortamını ve ortaya çıkabilecek veri türlerini anlamamın daha yararlı olacağını belirtti.
Bu anlatımdan sonra üretim ortamına bilgisayar mühendisliği açısından bakmaya çalıştım. Bir işletmede makinelerden veya ölçümlerden elde edilebilecek sayısal değerlerin, ürünlere ait görsellerin, tabloların ve yazılı dokümanların bilgisayar açısından farklı biçimlerde ele alındığını fark ettim. Örneğin bir ölçüm değeri sayı olarak işlenebilirken bir ürün fotoğrafının piksel verilerinden oluştuğunu, bir açıklama veya teknik dokümanın ise metin verisi olarak değerlendirilmesi gerektiğini öğrendim. Aynı işletme içerisinde ortaya çıkan verilerin tek bir yöntemle işlenemeyeceğini görmek, kullanılacak aracın öncelikle verinin yapısına bağlı olduğunu anlamamı sağladı.
Yanında çalıştığım mühendis, herhangi bir teknolojiye karar vermeden önce problemin hangi veri üzerinde oluştuğunu anlamanın önemli olduğunu bir örnek üzerinden açıkladı. Bir ürün görseliyle ilgili bir problem yaşandığında görüntü işleme yöntemleri gerekli olabilirken, çok sayıda kayıt arasından belirli bilgilerin bulunması gereken bir durumda tablo veya metin işleme yöntemlerinin daha uygun olabileceğini söyledi. Bu nedenle aynı işletmede birbirinden oldukça farklı bilgisayar mühendisliği problemleri bulunabileceğini gördüm. Bu yaklaşım, ilk günden belirli bir yönteme veya yapay zekâ modeline yönelmek yerine önce problemi tanımam gerektiğini anlamama yardımcı oldu.
Günün devamında öğrendiklerimi daha somut hâle getirmek amacıyla karşılaşılabilecek verileri kendi notlarımda sayısal veri, görsel veri ve metinsel veri şeklinde ayırdım. Bu çalışma gerçek şirket veri tabanının veya şirket içi bir sistemin modellenmesi amacıyla yapılmadı; yalnızca farklı veri türlerinin bilgisayar tarafından nasıl ele alınabileceğini anlamak için oluşturduğum basit bir sınıflandırmaydı. Bu küçük çalışma sırasında bir veri türünü tanımlamanın, daha sonra o veri üzerinde hangi işlemlerin yapılabileceğine karar vermeyi kolaylaştırdığını gördüm.

**KONTROL SONUCU:**

---

## GÜN 1 — DEVAM
**KISIM:** Firma ve Çalışma Ortamının Tanınması  
**YAPRAK NO:** 2  
**YAPILAN İŞ:** Veri Türlerinin Gözlemlenmesi ve Sonraki Teknik Çalışmalara Hazırlık  
**TARİH:** 21/07/2026

İlk incelemede verileri birkaç başlık altında ayırabilsem de bunun tek başına yeterli olmadığını fark ettim. Örneğin bir halı görseli yalnızca “görsel veri” olarak adlandırıldığında, bilgisayarın bu görüntüyü nasıl okuyacağı veya içerisindeki renk ve desenlerin nasıl temsil edileceği henüz açıklanmış olmuyordu. Benzer şekilde bir tabloya bakmak, tablodaki eksik veya hatalı kayıtların nasıl tespit edileceğini göstermiyordu. Yanında çalıştığım mühendis, bilgisayar mühendisliğinde problemi çözmeye başlamadan önce verinin yapısını daha ayrıntılı biçimde incelemem gerektiğini anlattı. Böylece ilk yaptığım sınıflandırmanın problemi çözmek için değil, hangi soruları sormam gerektiğini görmek için yararlı bir başlangıç olduğunu anladım.
Bu noktada bana, gerçek bir çalışma sırasında yalnızca “hangi programlama dilini kullanacağım?” sorusuna odaklanmanın eksik kalacağı anlatıldı. Önce verinin nereden geldiğini, hangi biçimde tutulduğunu, üzerinde hangi işlemlerin yapılmak istendiğini ve elde edilen sonucun nasıl kontrol edileceğini düşünmem gerektiğini öğrendim. Bu yaklaşımı daha iyi anlamak için aynı veri türünün farklı ihtiyaçlarda farklı şekillerde kullanılabileceğini düşündüm. Örneğin bir görüntü yalnız ekranda gösterilmek için kullanılabileceği gibi renklerinin ölçülmesi, belirli bir bölgesinin ayrılması veya başka bir görüntüyle karşılaştırılması için de işlenebilir. Dolayısıyla kullanılacak yöntemi belirleyen şey yalnız veri türü değil, o veriyle çözmeye çalıştığım problemdir.
İlk günün sonunda henüz herhangi bir proje veya uygulama konusu seçmedim. Bunun yerine üretim ortamında bilgisayar mühendisliği açısından karşılaşılabilecek veri ve problem çeşitlerini anlamaya odaklandım. Bu yaklaşımın, ilerleyen günlerde öğreneceğim yöntemleri yalnızca ezberlemek yerine hangi durumda neden kullanılabileceklerini anlamama yardımcı olacağını düşündüm. Ayrıca teknik bir çözüm önermeden önce problemi gözlemlemenin ve ihtiyacı doğru ifade etmenin yazılım geliştirme kadar önemli olduğunu fark ettim.
Günün sonunda yanında çalıştığım mühendisle yaptığım değerlendirmede, bir sonraki adımın farklı veri türlerini daha sistemli biçimde incelemek olması gerektiğine karar verdim. Özellikle tablo şeklinde düzenlenmiş veriler, JSON gibi yarı yapılandırılmış kayıtlar, görseller ve metinsel dokümanlar arasındaki farkları öğrenmeden bunları işleyecek araçlara geçmenin erken olacağını gördüm. Bu nedenle bir sonraki çalışma gününde yapılandırılmış, yarı yapılandırılmış ve yapılandırılmamış veri kavramlarını inceleyerek CSV, JSON ve temel tablo yapıları üzerinden veri modelleme mantığını öğrenmeye devam etmeyi planladım.

**KONTROL SONUCU:**

---

## GÜN 2 — 22 TEMMUZ 2026
**KISIM:** Veri Türleri ve Temel Veri Modelleme  
**YAPRAK NO:** 3  
**YAPILAN İŞ:** Veri Türlerinin Yapılarına Göre İncelenmesi  
**TARİH:** 22/07/2026

Stajımın ikinci gününde, bir önceki gün genel olarak ayırdığım veri türlerini daha sistemli biçimde incelemeye başladım. Yanında çalıştığım mühendis, bilgisayarda işlenen her verinin aynı yapıda olmadığını ve verinin nasıl düzenlendiğinin daha sonra kullanılacak yöntemi etkilediğini anlattı. Satır ve sütunlardan oluşan bir tabloyu, bir ürün görselini ve yazılı bir dokümanı karşılaştırdık. Tabloda ürün kodu veya tarih gibi alanlar önceden belirlenmiş sütunlarda tutulabilirken, bir görselde veya serbest metinde aynı düzenin bulunmadığını gördüm. Bu karşılaştırma sayesinde yapılandırılmış ve yapılandırılmamış veri kavramlarını daha somut biçimde anlamaya başladım.
Yanında çalıştığım mühendis, yapılandırılmış verinin belirli bir şemaya göre düzenlendiğini açıkladı. Bunu anlamak için çalışma amacıyla küçük bir örnek ürün tablosu oluşturdum. Tabloda ürün kodu, ürün grubu, renk bilgisi ve görsel dosya adı gibi alanlar kullandım. Her kaydın aynı sütunlara sahip olması sayesinde belirli bir ürünü bulmanın veya kayıtları karşılaştırmanın daha kolay olduğunu gördüm. Bunun gerçek bir şirket veri tabanı olmadığını, yalnızca veri düzenini anlayabilmek için hazırladığım örnek bir model olduğunu özellikle not ettim.
Daha sonra yarı yapılandırılmış veri kavramına geçtik. Yanında çalıştığım mühendis, JSON gibi yapılarda klasik tablodaki kadar sabit satır-sütun düzeni bulunmasa da verinin anahtar ve değerler aracılığıyla düzen taşıdığını anlattı. Hazırladığım örnek ürün kaydındaki bilgilerin tablo biçiminde ve JSON mantığında nasıl gösterilebileceğini karşılaştırdım. Tablo yapısında alanların sütun başlıklarıyla açıkça ayrıldığını, JSON tarafında ise aynı bilgilerin iç içe alanlar ve listelerle daha esnek tutulabildiğini gördüm. Bir ürüne birden fazla görsel veya özellik bağlanması gerektiğinde bu esnekliğin neden yararlı olabileceğini anladım.
Son olarak yapılandırılmamış veriyi ele aldım. Bir halı fotoğrafı veya serbest biçimde yazılmış bir açıklama, tablodaki ürün kodu gibi doğrudan anlamlı alanlara ayrılmış değildir. Görselin bilgisayar açısından piksellerden, metnin ise karakter ve kelimelerden oluştuğunu öğrendim. Bu nedenle benzer amaçlarla kullanılan veri türlerinin işlenme biçimlerinin farklı olabileceğini fark ettim. Günün bu bölümündeki karşılaştırma, veri türünü doğru belirlemenin kullanılacak araç veya yönteme karar vermeden önce gerekli bir adım olduğunu görmemi sağladı.

**KONTROL SONUCU:**

---

## GÜN 2 — DEVAM
**KISIM:** Veri Türleri ve Temel Veri Modelleme  
**YAPRAK NO:** 4  
**YAPILAN İŞ:** CSV, JSON ve Temel Veri İlişkilerinin Örnek Veri Üzerinde Karşılaştırılması  
**TARİH:** 22/07/2026

Günün devamında veri türlerini yalnız tanımlamak yerine aralarındaki ilişkileri düşünmeye başladım. Yanında çalıştığım mühendis, bir veri kaydının tek başına anlamlı olabileceğini ancak gerçek sistemlerde farklı kayıtların çoğu zaman birbirleriyle bağlantılı tutulduğunu anlattı. Örneğin bir ürünün temel bilgileri bir kayıt altında tutulurken aynı ürüne ait birden fazla görsel bulunabileceğini düşündüm. Bu durumda ürün bilgisini her görsel için tekrar tekrar yazmak yerine ürün ile görseller arasında ilişki kurulmasının daha düzenli olacağını gördüm. Çalışma amacıyla bir ürün kimliğini birden fazla görsel dosya adıyla eşleştirerek basit bir örnek hazırladım.
Bu örnek üzerinde çalışırken bir kaydı diğerinden ayırabilmek için benzersiz bir kimliğin neden gerekli olduğunu öğrendim. Aynı ürün adının farklı kayıtlarda tekrar edebileceğini, ancak ürün kodu veya oluşturulan bir kimlik alanının ilgili kayda ulaşmayı kolaylaştırabileceğini gördüm. Yanında çalıştığım mühendis, bu tür ilişkilerin ileride veritabanlarında daha ayrıntılı biçimde kurulabileceğini ancak şimdilik temel amacımın veriler arasındaki bağlantıyı anlamak olduğunu belirtti. Bu nedenle ürün ve görsel ilişkisini yalnızca basit bir örnek üzerinden inceledim; herhangi bir şirket içi veritabanı yapısını varmış gibi modellemedim.
Daha sonra CSV ile JSON biçimlerini kullanım açısından karşılaştırdım. CSV'nin satır ve sütun şeklindeki düzenli veriler için basit ve okunabilir olduğunu, ancak bir kaydın içinde liste veya iç içe bilgi tutulması gerektiğinde yapının zorlaşabildiğini gördüm. JSON ise daha esnek bir yapı sağlıyordu; buna karşılık veriyi tablo şeklinde hızlıca incelemek CSV kadar doğrudan olmayabiliyordu. Bu karşılaştırma sonunda tek bir dosya biçiminin bütün ihtiyaçlar için en iyi seçenek olmadığını anladım. Kullanılacak biçimin verinin yapısına, taşınma şekline ve yapılacak işleme göre seçilmesi gerektiğini öğrendim.
Günün sonunda farklı veri türlerini ve temel veri ilişkilerini daha net ayırabildiğimi gördüm. Ancak verinin hangi biçimde tutulduğunu bilmenin, çözmek istediğim problemi tek başına tanımlamadığını da fark ettim. Aynı tablo üzerinde farklı sorular sorulabileceği gibi aynı görüntü üzerinde renk, motif veya benzerlik gibi birbirinden farklı problemler de incelenebilirdi. Yanında çalıştığım mühendis, bir sonraki adımda bir problemi bilgisayar mühendisliği açısından nasıl tanımlamam gerektiğini; girdiyi, beklenen çıktıyı ve sonucu nasıl değerlendireceğimi düşünmemin daha doğru olacağını söyledi. Bu nedenle bir sonraki çalışma gününde doğrudan bir algoritma seçmek yerine problemi doğru biçimde ifade etme ve ölçülebilir hâle getirme konusuna geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 3 — 23 TEMMUZ 2026
**KISIM:** Problemin Bilgisayar Mühendisliği Açısından Tanımlanması  
**YAPRAK NO:** 5  
**YAPILAN İŞ:** Problem, Girdi ve Beklenen Çıktının Belirlenmesinin İncelenmesi  
**TARİH:** 23/07/2026

Stajımın üçüncü gününde, bir problemi bilgisayar mühendisliği açısından nasıl ele almam gerektiği üzerinde çalıştım. Yanında çalıştığım mühendis, bir problemle karşılaştığımda doğrudan kullanacağım algoritmayı veya yapay zekâ modelini seçmeye çalışmanın çoğu zaman yanlış bir başlangıç olduğunu anlattı. Önce neyi çözmeye çalıştığımı açık biçimde ifade etmem, hangi veriye sahip olduğumu belirlemem ve sonuçta ne elde etmek istediğimi tanımlamam gerektiğini söyledi. Bu yaklaşımın, uygun yöntemi seçmeden önce problemin sınırlarını anlamamı sağladığını fark ettim.
Konuyu daha iyi anlayabilmem için “iki halı birbirine benziyor mu?” sorusu üzerinden küçük bir düşünme çalışması yaptık. İlk bakışta bu soru tek bir problem gibi görünüyordu. Ancak yanında çalıştığım mühendis, benzerlik sözcüğünün bilgisayar açısından yeterince açık olmadığını gösterdi. İki halı renkleri açısından benzer olabilirken motifleri tamamen farklı olabilirdi. Başka iki halı ise farklı renklerde olmasına rağmen aynı geometrik yapıya veya benzer desen düzenine sahip olabilirdi. Bu örnek üzerinden, günlük dilde kolayca ifade edilen bir isteğin bilgisayar tarafından çözülebilmesi için daha kesin bir probleme dönüştürülmesi gerektiğini öğrendim.
Daha sonra problemi tanımlarken ilk olarak girdiyi belirlemeye çalıştım. Eğer renk benzerliğini incelemek istiyorsam girdinin iki görüntü ve bu görüntülerden elde edilen renk bilgileri olabileceğini düşündüm. Eğer metinsel bir bilgi arama problemi üzerinde çalışıyor olsaydım bu kez girdinin kullanıcı sorusu ve doküman koleksiyonu olacağını gördüm. Yanında çalıştığım mühendis, girdiyi doğru tanımlamadan yönteme karar vermenin zor olduğunu; çünkü görüntü, tablo ve metin gibi farklı veri türlerinin farklı işlemler gerektirdiğini anlattı. Böylece önceki iki günde öğrendiğim veri türleriyle problem tanımlama konusu arasında doğrudan bağlantı kurabildim.
Girdiden sonra beklenen çıktıyı belirledim. “Benzer halıları bulmak” gibi genel bir ifade yerine, örneğin verilen bir görüntüye en yakın beş görüntüyü sıralamak daha açık bir çıktı tanımıydı. Benzer şekilde bir sınıflandırma probleminde çıktı bir sınıf etiketi, bir renk analizinde baskın renkler, bir bilgi arama probleminde ise ilgili metin bölümleri olabilirdi. Bu çalışma sırasında aynı veri üzerinde farklı çıktılar hedeflendiğinde problemin tamamen değişebildiğini gördüm. Bu nedenle algoritmayı seçmeden önce “sisteme ne vereceğim ve sistemden ne bekliyorum?” sorularını açık biçimde cevaplamanın önemli olduğunu anladım.

**KONTROL SONUCU:**

---

## GÜN 3 — DEVAM
**KISIM:** Problemin Bilgisayar Mühendisliği Açısından Tanımlanması  
**YAPRAK NO:** 6  
**YAPILAN İŞ:** Başarı Ölçütü, Basit Başlangıç Yöntemi ve Değerlendirme Mantığının İncelenmesi  
**TARİH:** 23/07/2026

Günün devamında yalnızca girdi ve çıktıyı tanımlamanın yeterli olmadığını öğrendim. Yanında çalıştığım mühendis, geliştirdiğim yöntemin işe yarayıp yaramadığını anlayabilmek için bir başarı ölçütüne ihtiyaç duyacağımı anlattı. Bir benzerlik sistemi gerçekten ilgili örnekleri üst sıralara getiriyor mu veya bir renk karşılaştırması algılanan farkı yeterince yansıtıyor mu gibi soruların önceden düşünülmesi gerektiğini söyledi. Böylece “çalıştı” demenin tek başına teknik bir değerlendirme olmadığını fark ettim.
Bunu daha iyi anlamak için küçük bir örnek hazırladım. Üç örneği renk, parlaklık ve desen yoğunluğu gibi birkaç basit özellik üzerinden düşünerek hangi ikisinin birbirine daha yakın olmasını beklediğimi önce kendim belirledim. Ardından kullanacağım yöntemin bu beklentiyle ne kadar uyumlu sonuç verdiğini nasıl kontrol edebileceğimi düşündüm. Amacım gerçek bir model kurmak değil, sonuçtan önce neyi doğru kabul edeceğimi belirlemenin önemini görmekti. Yanında çalıştığım mühendis, değerlendirme ölçütünün problem tanımının bir parçası olması gerektiğini vurguladı.
Bu çalışma sırasında en basit yöntemin değersiz olmadığını da öğrendim. Yanında çalıştığım mühendis, başlangıçta karmaşık bir model yerine anlaşılması kolay bir yöntemle ilk sonucu elde etmenin yararlı olduğunu anlattı. Basit yöntem yeterli olursa gereksiz karmaşıklıktan kaçınılabileceğini, yetersiz kalırsa da sorunun nerede ortaya çıktığının daha kolay görülebileceğini söyledi. Bu nedenle önce temel bir yöntem denemenin ve sonucu ölçtükten sonra gerekirse daha gelişmiş bir yönteme geçmenin daha sağlıklı olduğunu düşündüm.
Günün sonunda problem çözme sürecini daha düzenli düşünmeye başladım. Önce problemi açık biçimde ifade etmem, girdiyi ve beklenen çıktıyı belirlemem, sonucun nasıl değerlendirileceğine karar vermem ve ancak bundan sonra kullanılacak yöntemi araştırmam gerektiğini öğrendim. Bu yaklaşımın ilerleyen günlerde karşılaşacağım teknolojilerin hangi ihtiyaca cevap verdiğini anlamama yardımcı olacağını düşündüm. Yanında çalıştığım mühendis, bir sonraki adımda Python çalışma ortamını ve temel araçları incelememin uygun olacağını söyledi. Bu nedenle bir sonraki çalışma gününde Python, sanal ortam ve paket kavramlarını öğrenmeye geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 4 — 24 TEMMUZ 2026
**KISIM:** Python Geliştirme Ortamı ve Veri Sözleşmesi  
**YAPRAK NO:** 7  
**YAPILAN İŞ:** Python, Sanal Ortam ve Paket Yönetiminin İncelenmesi  
**TARİH:** 24/07/2026

Stajımın dördüncü gününde, önceki günlerde üzerinde durduğum problem ve veri kavramlarından sonra kullanacağım temel çalışma araçlarını öğrenmeye başladım. Yanında çalıştığım mühendis, Python'ın veri analizi, görüntü işleme ve yapay zekâ çalışmalarında sık kullanılmasının yalnız sözdiziminin kolay olmasından kaynaklanmadığını anlattı. Python'ın geniş kütüphane desteğinin küçük deneyleri hızlı kurmayı kolaylaştırdığını, ancak programlama dilinin her zaman problemin gereksinimine göre seçilmesi gerektiğini belirtti. Böylece Python'ı yalnız popüler olduğu için değil, yapacağım teknik çalışmalar için uygun bir araç olduğu için değerlendirmem gerektiğini anladım.
Konuyu daha iyi anlayabilmek için Python, C++ ve MATLAB'ı kullanım amacı açısından karşılaştırdım. Yanında çalıştığım mühendis, C++'ın yüksek performans ve donanıma yakın kontrol gereken uygulamalarda güçlü olduğunu, ancak geliştirme sürecinin daha ayrıntılı olabildiğini anlattı. MATLAB'ın sayısal hesaplama ve mühendislik çalışmalarında hazır araçlar sunduğunu, fakat farklı bir lisans yapısına sahip olduğunu belirtti. Python'ın açık kaynaklı olması ve veri bilimi kütüphanelerinin genişliği küçük teknik deneyler için uygun görünüyordu. Bu karşılaştırma sonucunda programlama dillerini farklı ihtiyaçlara cevap veren araçlar olarak değerlendirmem gerektiğini gördüm.
Daha sonra Python çalışma ortamının nasıl düzenlenmesi gerektiğini inceledim. Yanında çalıştığım mühendis, farklı çalışmaların farklı kütüphane sürümlerine ihtiyaç duyabileceğini ve bütün paketları tek Python ortamına kurmanın zamanla karışıklığa yol açabileceğini anlattı. Bu nedenle sanal ortam kavramını öğrendim. Basit bir sanal ortam oluşturarak etkinleştirme ve kapatma işlemlerini inceledim. Sanal ortamın yeni bir Python kurulumu yapmak yerine ilgili çalışma için ayrı bir paket alanı oluşturduğunu gördüm. Böylece geliştirme ortamının da düzenli tutulması gerektiğini anlamaya başladım.
Sanal ortamdan sonra paket yönetimini ele aldım. Python'ın temel özelliklerinin her teknik çalışma için yeterli olmadığını, gerektiğinde dış kütüphanelerin paket yöneticisi aracılığıyla ortama eklendiğini öğrendim. Yanında çalıştığım mühendis, kullanılan paket sürümünün de önemli olduğunu açıkladı. Aynı kodun farklı sürümlerde farklı davranabileceğini ve bu nedenle bağımlılıkların kayıt altında tutulmasının çalışmayı daha sonra tekrar kurmayı kolaylaştırdığını gördüm. Paketlerin nasıl listelendiğini ve çalışma ortamına hangi kütüphanelerin kurulduğunu kontrol ederek temel paket yönetimi mantığını inceledim.

**KONTROL SONUCU:**

---

## GÜN 4 — DEVAM
**KISIM:** Python Geliştirme Ortamı ve Veri Sözleşmesi  
**YAPRAK NO:** 8  
**YAPILAN İŞ:** Jupyter Notebook, .py Dosyası ve Temel Python Uygulaması  
**TARİH:** 24/07/2026

Günün devamında Python kodunu hangi ortamda yazabileceğimi inceledim. Yanında çalıştığım mühendis, Jupyter Notebook ile normal bir Python dosyasının aynı dili kullanmasına rağmen çalışma biçimlerinin farklı olduğunu anlattı. Notebook ortamında kodu küçük hücreler hâlinde çalıştırıp her adımın sonucunu hemen görebildiğimi fark ettim. Bu özellik yeni bir yöntemi öğrenirken veya küçük deneyler yaparken kullanışlıydı. Ancak hücrelerin farklı sırayla çalıştırılması durumunda eski değişkenlerin bellekte kalabileceğini ve bunun bazen sonucu anlamayı zorlaştırabileceğini öğrendim.
Daha sonra aynı işlemleri `.py` uzantılı normal bir Python dosyasında ele aldım. Programın yukarıdan aşağıya belirli bir sıra içerisinde çalışması kodun tamamını tek akış hâlinde takip etmemi kolaylaştırdı. Yanında çalıştığım mühendis, tekrar kullanılacak fonksiyonların ve daha düzenli programların Python dosyalarında tutulmasının uygun olabileceğini anlattı. Notebook ve `.py` dosyalarının birbirinin alternatifi olmak zorunda olmadığını; bir konuyu Notebook içerisinde deneyip daha sonra düzenli hâle gelen kodu Python dosyasına taşıyabileceğimi öğrendim.
Öğrendiklerimi uygulamak için temel Python özelliklerini kullanan küçük bir program hazırladım. Çalışma amacıyla oluşturduğum birkaç sayısal değeri bir liste içerisinde tuttum ve bu değerlerin toplamını, ortalamasını, en küçük ve en büyük değerini hesapladım. Önce liste elemanlarına tek tek erişerek işlemlerin nasıl yapıldığını anlamaya çalıştım, daha sonra Python'ın hazır fonksiyonlarını kullanarak aynı işlemleri daha kısa biçimde gerçekleştirdim. Sonuçları ekrana yazdırarak hesaplamaları kontrol ettim. Bu küçük uygulamanın amacı karmaşık bir program geliştirmek değil, çalışma ortamının doğru hazırlandığını ve temel Python işlemlerini kullanabildiğimi görmekti.
Günün sonunda Python ile küçük veri grupları üzerinde rahatlıkla işlem yapabildiğimi, ancak veri miktarı büyüdüğünde veya görüntüler gibi çok boyutlu verilerle çalışıldığında listeler üzerinde tek tek işlem yapmanın zorlaşabileceğini fark ettim. Yanında çalıştığım mühendis, bilimsel hesaplama çalışmalarında bu nedenle sayısal diziler ve matrisler üzerinde daha verimli işlem yapan araçların kullanıldığını anlattı. Bugün öğrendiğim Python temelleri, sanal ortam ve paket yönetimi sonraki çalışmalar için gerekli hazırlığı sağladı. Bir sonraki gün NumPy dizilerini, görüntülerin matris olarak temsil edilmesini ve vektörel işlemleri incelemeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 5 — 25 TEMMUZ 2026
**KISIM:** Pandas, Veri Hattı ve Veri Kalitesi  
**YAPRAK NO:** 9  
**YAPILAN İŞ:** CSV ve JSON Örneklerinin Okunması ve Ortak Şemaya Getirilmesi  
**TARİH:** 25/07/2026

Üçüncü gün farklı kaynaklardan gelen verilerin aynı uygulamada nasıl birleştirilebileceğini çalıştım. Repo içinde `raw_production_logs.csv` ve `raw_catalog_feed.json` gibi üretim çağrışımı yapan dosya adları bulunmasına rağmen bu dosyaların içeriği gerçek fabrika kaydı değildi. Tamamını proje için hazırlanmış sentetik örnekler olarak kullandım. CSV ve JSON dosyalarını ayrı ayrı okuyup ilk birkaç kaydı ekrana yazdırarak sütun adlarının ve veri tiplerinin gerçekten beklediğim gibi geldiğini kontrol ettim.
Pandas ile CSV dosyasını, Python’un JSON araçlarıyla da JSON dosyasını okuyarak ortak alanları belirledim. Farklı kaynaklarda aynı bilginin farklı sütun veya anahtar adlarıyla gelebileceğini gördüm. Bu nedenle alan adlarını tek bir standarda dönüştüren basit bir normalizasyon adımı hazırladım. Kaynaklar arasında aynı bilgiyi temsil eden farklı alan adlarını tek bir isme dönüştürmek için küçük bir eşleme tablosu kullandım ve normalizasyon adımının neden gerekli olduğunu uygulamada gördüm.
Bazı kayıtlarda eksik değer, yanlış tip veya beklenmeyen alan oluşturarak veri hattının nasıl davranacağını gözlemledim. Hatalı kayıtları tamamen silmek yerine ayrı bir `quarantine` çıktısında tutmanın, hatanın nedenini daha sonra incelemek açısından daha doğru olacağını öğrendim. Bozuk kayıtların hangi sebeple karantinaya alındığını ayrıca yazdırarak yalnızca 'hatalı' demek yerine sorunun eksik alan, yanlış tip veya geçersiz değer olduğunu ayırt etmeye çalıştım.
İlk bölümün sonunda temizlenmiş kayıtları tek bir JSON çıktısında topladım. Burada amacım bir üretim sisteminden veri çekmek değil, dosya tabanlı iki farklı kaynağın ortak bir şemaya nasıl getirilebileceğini öğrenmekti. SCADA, PLC veya kurumsal veritabanına herhangi bir bağlantı kurulmadı. Böylece veri hattının çıktısını inceleyen bir kişinin ham dosyaya geri dönmeden hatanın nerede oluştuğu hakkında temel bilgi edinebilmesini sağlamaya çalıştım.

**KONTROL SONUCU:**

---

## GÜN 5 — DEVAM
**KISIM:** Pandas, Veri Hattı ve Veri Kalitesi  
**YAPRAK NO:** 10  
**YAPILAN İŞ:** Veri Normalizasyonu, Hatalı Kayıtların Ayrılması ve Kalite Kontrolü  
**TARİH:** 25/07/2026

Günün ikinci kısmında hazırladığım veri hattını komut satırından çalıştırdım. Programın normalleştirilmiş kayıtları, hatalı kayıtları ve basit veri kalite özetini ayrı dosyalara yazdığını kontrol ettim. Çıktıların dosya isimlerini ve içeriklerini elle açarak beklediğim alanların oluşup oluşmadığına baktım. Komut satırından çalıştırdığımda oluşan üç çıktı dosyasını tek tek açıp satır sayılarının ve örnek kayıtların birbirleriyle tutarlı olup olmadığını kontrol ettim.
Ardından testleri çalıştırarak parser ve normalizasyon fonksiyonlarının birkaç sınır durumunda doğru çalışıp çalışmadığını kontrol ettim. Bir kaynağın boş gelmesi, zorunlu bir alanın eksik olması veya sayısal beklenen değerin metin olarak gelmesi gibi küçük örnekler üzerinden hata davranışını gözlemledim. Pytest sonuçlarında her testin adını okuyarak parser, normalizer ve pipeline parçalarının ayrı ayrı sınandığını gördüm; bu da büyük bir işlemi küçük parçalara bölmenin yararını gösterdi.
Bu gün bana veri işleme hattının yalnızca “dosyayı okuyup birleştirmekten” ibaret olmadığını gösterdi. Kaynağın nereden geldiğinin bilinmesi, hatalı kayıtların izlenebilmesi ve çıktıların tekrar üretilebilir olması da önemliydi. Bu yüzden kaynak adı ve işlem sonucu gibi basit metadata alanlarını korumaya dikkat ettim. Bir test başarısız olduğunda bütün kodu değiştirmek yerine ilgili fonksiyonun girdisini ve beklenen çıktısını karşılaştırmanın daha hızlı sonuç verdiğini deneyimledim.
Gerçek kurum verileri ileride kullanılacak olursa bu yapının doğrudan yeterli olmayacağını da not ettim. Öncelikle gerçek veri kaynağının formatı, erişim şekli, yetkilendirmesi ve hangi alanların kullanılmasına izin verildiği belirlenmelidir. Sentetik veri hattı yalnızca bu tür bir entegrasyonun yazılım tarafındaki örneğini oluşturdu. İleride gerçek bir kurumsal kaynağa bağlanılacaksa dosya adından çok veri sözleşmesi, erişim izni ve hatalı kayıtların izlenebilirliği gibi konuların belirleyici olacağını not ettim.

Bu çalışma sırasında veri kaynağının ve veri sözleşmesinin açık olmasına özellikle dikkat ettim. Aynı bilginin iki dosyada farklı alan adlarıyla tutulmasının, eksik değerin hangi nedenle oluştuğunun ve bir kaydın neden reddedildiğinin sonraki analizleri doğrudan etkileyebileceğini gördüm. Bu nedenle veri hattını tek bir büyük işlem olarak düşünmek yerine okuma, doğrulama, normalizasyon ve çıktı üretme adımlarına ayırmanın hata ayıklamayı kolaylaştırdığını değerlendirdim. Gerçek bir kurumsal entegrasyonda bu kuralların ilgili birimlerle birlikte tanımlanması gerektiğini, burada kullandığım alan ve kontrollerin ise yalnız sentetik örnekleri anlamaya yönelik olduğunu korudum.

**KONTROL SONUCU:**

---

## GÜN 6 — 27 TEMMUZ 2026
**KISIM:** NumPy ve Vektörel Hesaplama  
**YAPRAK NO:** 11  
**YAPILAN İŞ:** Python Listeleri, NumPy Dizileri ve Vektörel İşlemlerin İncelenmesi  
**TARİH:** 27/07/2026

Stajımın altıncı gününde Python ile yaptığım temel işlemlerden sonra daha büyük sayısal veriler üzerinde nasıl daha düzenli çalışabileceğimi incelemeye başladım. Yanında çalıştığım mühendis, Python listelerinin genel amaçlı yapılar olduğunu, ancak çok sayıda sayısal değer üzerinde işlem yapılacağı zaman NumPy dizilerinin daha uygun olabildiğini anlattı. Önce küçük bir Python listesi oluşturarak elemanlara tek tek eriştim ve basit işlemler yaptım. Daha sonra aynı değerleri NumPy dizisine dönüştürdüm. NumPy dizisinin değerlerin yanında boyut, şekil ve veri tipi gibi bilgileri de düzenli biçimde taşıdığını gördüm.
Python listesi ile NumPy dizisi arasındaki farkı daha iyi anlayabilmek için küçük bir sayısal örnek üzerinde çalıştım. Bir listedeki bütün değerlere aynı sayıyı eklemek istediğimde elemanları tek tek dolaşmam gerektiğini gördüm. NumPy dizisinde ise aynı işlemi bütün diziye tek seferde uygulayabildim. Yanında çalıştığım mühendis bunun vektörel işlem mantığı olduğunu ve özellikle büyük sayısal verilerde kodu daha düzenli hâle getirebildiğini anlattı. Buradaki amacım yalnız daha az kod yazmak değil, aynı matematiksel işlemin veri dizisinin tamamına uygulanabileceğini anlamaktı.
Daha sonra NumPy dizilerinin shape ve dtype özelliklerini inceledim. Tek boyutlu bir dizinin yalnız eleman sayısına sahip olduğunu, iki boyutlu bir yapının satır ve sütun şeklinde düşünülebileceğini öğrendim. Aynı verinin farklı boyutlarda düzenlenmesinin, üzerinde yapılacak işlemleri de etkilediğini gördüm. Veri tipi tarafında ise tam sayı ve ondalıklı sayıların bellekte farklı biçimde tutulabildiğini öğrendim. Yanında çalıştığım mühendis, sayısal işlemlerde veri tipinin göz ardı edilmemesi gerektiğini; çünkü kullanılan veri tipinin değer aralığını ve yapılabilecek işlemleri etkileyebileceğini söyledi.
Bu bölümde yaptığım küçük uygulamalar sonunda NumPy'yi yalnız Python listesinin daha hızlı bir sürümü olarak düşünmemem gerektiğini anladım. NumPy, sayısal verileri belirli boyut ve veri tipi bilgisiyle düzenleyen bir yapı sunuyordu. Bu özellik özellikle bir sonraki aşamada görüntülerle çalışırken önemli olacaktı. Yanında çalıştığım mühendis, ekranda tek bir fotoğraf olarak gördüğüm görüntünün bilgisayar açısından aslında çok sayıda sayısal değerden oluştuğunu söyledi. Bunun üzerine günün devamında bir görüntünün NumPy dizisi olarak nasıl temsil edildiğini incelemeye geçtim.

**KONTROL SONUCU:**

---

## GÜN 6 — DEVAM
**KISIM:** NumPy ve Vektörel Hesaplama  
**YAPRAK NO:** 12  
**YAPILAN İŞ:** Görüntünün Matris Yapısının ve Piksel İşlemlerinin İncelenmesi  
**TARİH:** 27/07/2026

Günün devamında bir görüntünün bilgisayarda nasıl tutulduğunu incelemeye başladım. Yanında çalıştığım mühendis, renkli bir görüntünün yükseklik, genişlik ve renk kanalı olmak üzere üç temel boyutla düşünülebileceğini anlattı. Örneğin bir görüntünün shape bilgisi 1080 × 1920 × 3 biçimindeyse ilk değerin görüntünün yüksekliğini, ikinci değerin genişliğini, son değerin ise renk kanallarını ifade ettiğini öğrendim. Böylece ekranda tek bir bütün olarak gördüğüm fotoğrafın aslında belirli konumlardaki piksel değerlerinden oluşan üç boyutlu bir NumPy dizisi olduğunu daha açık biçimde anladım.
Daha sonra görüntüdeki piksel değerlerinin veri tipini inceledim. Örnek görüntünün uint8 türünde tutulduğunu ve her renk kanalındaki değerlerin 0 ile 255 arasında değiştiğini öğrendim. Birkaç pikselin değerine bakarak görüntünün belirli bir noktasındaki rengin üç kanal üzerinden nasıl temsil edildiğini gözlemledim. Ayrıca görüntünün küçük bir bölümünü satır ve sütun aralıklarıyla seçerek yalnızca o bölge üzerinde işlem yapılabildiğini gördüm. Bu çalışma, daha sonra ilgilendiğim görüntü bölgesini seçerken bütün görüntüyü işlemek zorunda olmayacağımı anlamama yardımcı oldu.
Görüntü üzerinde küçük bir parlaklık değiştirme deneyi yaptım. İlk olarak görüntüdeki pikselleri tek tek dolaşan döngü mantığını düşündüm. Bu yaklaşım işlemin nasıl gerçekleştiğini anlamam açısından yararlıydı; ancak görüntüde çok sayıda piksel bulunduğu için aynı işlemin her piksel için ayrı ayrı yazılması ve yürütülmesi gereksiz bir yük oluşturuyordu. Daha sonra yanında çalıştığım mühendisin yönlendirmesiyle aynı işlemi NumPy'nin vektörel yapısını kullanarak görüntünün tamamına uyguladım. Parlaklık artırırken piksel değerlerinin 255 sınırını geçmemesi gerektiğini de gördüm ve bu nedenle sonuç değerlerini geçerli aralıkta tutmanın önemli olduğunu öğrendim.
İki yaklaşımı karşılaştırdığımda döngülü yöntemin işlemin mantığını öğrenmek için faydalı, NumPy ile yapılan vektörel işlemin ise büyük veri üzerinde daha düzenli olduğunu gördüm. Belirli bir hız değeri elde etmekten çok yöntemlerin çalışma biçimleri arasındaki farkı anlamaya odaklandım. Günün sonunda görüntünün sayısal bir dizi olduğunu, piksel işlemlerinin matris işlemleri olarak ele alınabildiğini ve NumPy'nin bu işlemleri kolaylaştırdığını öğrendim. Yanında çalıştığım mühendis, verileri bu şekilde temsil ettikten sonra sıradaki önemli sorunun iki örneğin birbirine ne kadar benzediğini belirlemek olduğunu söyledi. Bu nedenle bir sonraki çalışma gününde uzaklık ve benzerlik kavramlarını incelemeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 7 — 28 TEMMUZ 2026
**KISIM:** Uzaklık ve Benzerlik Yöntemleri  
**YAPRAK NO:** 13  
**YAPILAN İŞ:** Euclidean, Manhattan ve Cosine Yaklaşımlarının Küçük Sayısal Örneklerle İncelenmesi  
**TARİH:** 28/07/2026

Stajımın yedinci gününde, bir önceki gün NumPy ile sayısal verilerin ve görüntülerin nasıl temsil edildiğini öğrendikten sonra iki sayısal örneğin birbirine ne kadar yakın olduğunu nasıl belirleyebileceğimi incelemeye başladım. Yanında çalıştığım mühendis, bilgisayarın iki görüntüye bakıp doğrudan “bunlar birbirine benziyor” diyemeyeceğini; önce görüntüleri veya diğer verileri karşılaştırılabilir sayısal özelliklerle temsil etmek gerektiğini anlattı. Daha sonra bu özellikler arasındaki farkın bir uzaklık veya benzerlik ölçüsüyle hesaplanabileceğini söyledi. Böylece önceki gün öğrendiğim dizi ve matris yapısının yalnız veriyi saklamak için değil, veriler arasında karşılaştırma yapabilmek için de gerekli olduğunu gördüm.
İlk olarak Öklid uzaklığını inceledim. Yanında çalıştığım mühendis bunu iki nokta arasındaki düz çizgi uzaklığına benzeterek açıkladı. Küçük bir örnekte A noktasını (2, 3), B noktasını ise (5, 7) olarak düşündüm. İki eksendeki farkları birlikte değerlendirdiğimde Öklid uzaklığının 5 olduğunu gördüm. Bu yöntem, özelliklerin aynı ölçekte olduğu ve aralarındaki doğrusal uzaklığın anlamlı kabul edildiği basit durumlarda anlaşılır bir başlangıç sağlıyordu. Ancak özelliklerden biri çok büyük sayılarla, diğeri küçük sayılarla ifade edilirse büyük ölçekli özelliğin sonucu daha fazla etkileyebileceğini de fark ettim.
Daha sonra Manhattan uzaklığını ele aldım. Bu yöntemde iki nokta arasındaki farkların ayrı ayrı toplanması mantığını öğrendim. Aynı A ve B noktaları için eksenlerdeki farkların 3 ve 4 olduğunu, toplam uzaklığın ise 7 çıktığını gördüm. Yanında çalıştığım mühendis, bu yaklaşımın bir şehirde yalnız yatay ve dikey sokaklar üzerinden ilerlemeye benzetilebileceğini söyledi. Öklid ve Manhattan uzaklığının aynı iki örnek için farklı sayılar üretmesi, “uzaklık” kavramının tek bir tanımı olmadığını anlamamı sağladı. Bu nedenle hangi ölçünün kullanılacağına problemin yapısına göre karar verilmesi gerektiğini öğrendim.
Son olarak cosine benzerliğini inceledim. Burada asıl dikkatin iki vektör arasındaki mutlak uzaklıktan çok yön benzerliğine verildiğini öğrendim. Bir vektör diğerinin daha büyük ölçekli bir hâli olsa bile yönleri benzerse cosine benzerliği yüksek olabiliyordu. Bu özellik özellikle değerlerin büyüklüğünden ziyade dağılım yönünün önemli olduğu durumlarda faydalı olabilirdi. Küçük sayısal örneklerle Öklid, Manhattan ve cosine sonuçlarını karşılaştırdığımda aynı verinin farklı ölçütlerle farklı biçimde yorumlanabildiğini gördüm. Günün ilk bölümünde bu üç yöntemin birbirinin yerine otomatik olarak kullanılamayacağını, seçimin veri temsilinin ve problemin amacının bir parçası olduğunu anladım.

**KONTROL SONUCU:**

---

## GÜN 7 — DEVAM
**KISIM:** Uzaklık ve Benzerlik Yöntemleri  
**YAPRAK NO:** 14  
**YAPILAN İŞ:** Covariance ve Mahalanobis Uzaklığının Temel Mantığının İncelenmesi  
**TARİH:** 28/07/2026

Günün devamında, kullandığım uzaklık ölçülerinin bazı durumlarda neden yetersiz kalabileceğini inceledim. Yanında çalıştığım mühendis, iki özelliğin birbirinden tamamen bağımsız olmayabileceğini anlattı. Örneğin bir görüntüden elde edilen parlaklık ile bazı renk değerleri birlikte değişebilir veya benzer iki özellik aynı bilgiyi kısmen tekrar edebilir. Öklid uzaklığında her özellik ayrı bir eksen gibi değerlendirilir ve aralarındaki ilişki doğrudan hesaba katılmaz. Bu nedenle yalnız değer farkına bakmanın bazı veri yapılarında yeterli olmayabileceğini gördüm.
Bu noktada covariance kavramını temel düzeyde inceledim. Covariance'ın iki değişkenin birlikte nasıl değiştiği hakkında bilgi verdiğini öğrendim. İki özellik genellikle birlikte artıp azalıyorsa aralarında bir ilişki bulunabileceğini anladım. Küçük bir örnek veri tablosu oluşturarak NumPy ile covariance matrisi çıkardım ve matrisin özelliklerin tek tek değişiminin yanında özellik çiftlerinin birlikte davranışını da gösterdiğini gözlemledim. Yanında çalıştığım mühendis, burada amacımın değerleri ezberlemek değil, özellikler arasındaki ilişkinin karşılaştırmayı neden etkileyebileceğini anlamak olduğunu belirtti.
Daha sonra Mahalanobis uzaklığını araştırdım. Bu yöntemin iki örnek arasındaki farkı değerlendirirken veri kümesindeki değişkenlerin dağılımını ve birbirleriyle olan ilişkilerini de dikkate aldığını öğrendim. Böylece güçlü biçimde ilişkili özelliklerin etkisi daha kontrollü ele alınabiliyordu. Yanında çalıştığım mühendis, bunun her durumda Öklid uzaklığından daha iyi olduğu anlamına gelmediğini söyledi. Mahalanobis uzaklığının güvenilir covariance bilgisi gerektirdiğini, az sayıda örnekte veya birbirine çok bağımlı özelliklerde matris işlemlerinin sorun çıkarabileceğini öğrendim. Bu nedenle gerektiğinde daha dayanıklı sayısal yöntemlere ihtiyaç duyulabileceğini temel seviyede inceledim.
Günün sonunda Euclidean, Manhattan, cosine ve Mahalanobis yaklaşımlarının aynı soruya farklı bakışlar sunduğunu gördüm. Basit yöntemlerle başlamak sonuçları anlamayı kolaylaştırırken, veri içindeki ilişkiler arttıkça farklı ölçülere ihtiyaç duyulabileceğini öğrendim. Ayrıca karşılaştırmadan önce özelliklerin ölçeklerini kontrol etmenin önemli olduğunu fark ettim. Yanında çalıştığım mühendis, sayısal karşılaştırmaların sağlıklı yapılabilmesi için verinin düzenli ve temiz olması gerektiğini söyledi. Bu nedenle bir sonraki çalışma gününde eksik ve tekrar eden kayıtları incelemek için Pandas ve veri temizliği konusuna geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 8 — 29 TEMMUZ 2026
**KISIM:** Keşifsel Veri Analizi  
**YAPRAK NO:** 15  
**YAPILAN İŞ:** Dağılım, Histogram, Boxplot ve Aykırı Değerlerin İncelenmesi  
**TARİH:** 29/07/2026

Stajımın sekizinci gününde, önceki günlerde Pandas ile temizlediğim tablo verisini yalnız satır ve sütunlara bakarak değerlendirmenin her zaman yeterli olmadığını öğrendim. Yanında çalıştığım mühendis, bir veri setinde değerlerin hangi aralıkta toplandığını, bazı değerlerin diğerlerinden belirgin biçimde ayrılıp ayrılmadığını veya iki değişken arasında bir ilişki olup olmadığını grafikler üzerinden daha kolay görebileceğimi anlattı. Bu nedenle bugün Matplotlib kullanarak temel keşifsel veri analizi yapmaya başladım. Amacım bir model kurmak değil, elimdeki verinin yapısını görerek daha sonra vereceğim kararların hangi gözlemlere dayandığını anlamaktı.
İlk olarak dağılım kavramını ve histogram grafiğini inceledim. Küçük bir örnek veri setindeki sayısal değerlerin hangi aralıklarda yoğunlaştığını görmek için histogram oluşturdum. Tabloya yalnızca sayılar olarak baktığımda fark etmediğim bazı yoğunlaşmaların grafik üzerinde daha belirgin olduğunu gördüm. Yanında çalıştığım mühendis, histogramdaki sütunların tek tek kayıtları değil belirli değer aralıklarında kaç gözlem bulunduğunu gösterdiğini anlattı. Ayrıca kullanılan aralık sayısının grafiğin görünümünü değiştirebildiğini, bu nedenle grafiği yorumlarken yalnız şekle bakıp kesin sonuç çıkarmamam gerektiğini öğrendim.
Daha sonra boxplot grafiğine geçtim. Bu grafik üzerinde verinin orta bölgesini, yayılımını ve diğer değerlerden belirgin şekilde uzaklaşan gözlemleri daha kolay inceleyebildiğimi gördüm. İlk düşüncem bu uzak değerleri doğrudan hatalı kabul etmekti. Ancak yanında çalıştığım mühendis, aykırı görünen bir değerin yanlış kayıt olabileceği gibi gerçekten nadir gerçekleşen doğru bir ölçümü de temsil edebileceğini söyledi. Bu nedenle aykırı değer tespit edildiğinde önce kaynağını ve anlamını incelemek gerektiğini öğrendim. Veri temizleme sırasında kayıt silme kararının yalnız grafikte uzak görünmesine dayanarak verilmemesi gerektiğini fark ettim.
Histogram ve boxplot çalışmalarından sonra aynı sayısal verinin farklı grafiklerle farklı yönlerinin görülebildiğini anladım. Histogram bana dağılımın hangi bölgelerde yoğunlaştığını gösterirken boxplot değerlerin genel yayılımını ve olağan dışı noktaları daha hızlı görmemi sağladı. Böylece keşifsel veri analizinin yalnız güzel grafikler üretmek için yapılmadığını, veri hakkında soru sormayı kolaylaştıran bir inceleme aşaması olduğunu gördüm. Günün devamında ise iki farklı sayısal değişkenin birlikte nasıl davrandığını anlamak için scatter plot ve korelasyon kavramlarını incelemeye geçtim.

**KONTROL SONUCU:**

---

## GÜN 8 — DEVAM
**KISIM:** Keşifsel Veri Analizi  
**YAPRAK NO:** 16  
**YAPILAN İŞ:** Scatter Plot, Korelasyon ve Küçük EDA Uygulamasının Yapılması  
**TARİH:** 29/07/2026

Günün devamında iki sayısal değişken arasındaki ilişkiyi görsel olarak incelemek için scatter plot kullandım. Örnek veri setinde bir değişkeni yatay eksene, diğerini dikey eksene yerleştirerek her kaydı bir nokta şeklinde gösterdim. Noktaların belirli bir yönde toplanmasının iki değişkenin birlikte değişebildiğine işaret edebileceğini gördüm. Bazı örneklerde değişkenlerden biri arttıkça diğerinin de arttığını, bazı örneklerde ise belirgin bir yön bulunmadığını gözlemledim. Yanında çalıştığım mühendis, scatter plot'ın özellikle iki sayısal değişken arasında doğrusal veya doğrusal olmayan bir yapı olup olmadığını ilk bakışta görmek için yararlı olduğunu anlattı.
Scatter plot üzerinde gördüğüm ilişkiyi sayısal olarak ifade edebilmek için korelasyon kavramını inceledim. Korelasyon değerinin iki değişkenin birlikte değişme yönü ve doğrusal ilişkinin gücü hakkında fikir verebildiğini öğrendim. Pozitif bir ilişkinin iki değerin genellikle aynı yönde, negatif bir ilişkinin ise ters yönde değişmesi anlamına gelebileceğini gördüm. Ancak korelasyon değerinin tek başına grafiğin bütün yapısını anlatmadığını da fark ettim. Özellikle birkaç aykırı değerin sonucu etkileyebileceğini ve doğrusal olmayan ilişkilerin basit korelasyon değeriyle yeterince açıklanamayabileceğini öğrendim.
Bu noktada yanında çalıştığım mühendis özellikle korelasyon ile nedensellik arasındaki fark üzerinde durdu. İki değişkenin birlikte hareket etmesinin, değişkenlerden birinin diğerine mutlaka neden olduğu anlamına gelmediğini anlattı. Aradaki ilişkinin başka bir değişkenden kaynaklanabileceğini veya yalnızca aynı dönemde birlikte değişmiş olabileceklerini söyledi. Bu açıklama, grafikte güçlü bir ilişki gördüğümde hemen neden-sonuç yorumu yapmamam gerektiğini anlamamı sağladı. Veri analizinde görsel ve sayısal ilişkilerin önce gözlem olarak ele alınması, nedeninin ise ayrıca araştırılması gerektiğini öğrendim.
Öğrendiklerimi bir araya getirmek için küçük bir keşifsel veri analizi uygulaması yaptım. Önce örnek tablonun sayısal sütunlarını kontrol ettim, ardından histogram ile dağılımı, boxplot ile aykırı görünen değerleri ve scatter plot ile iki değişken arasındaki ilişkiyi inceledim. Sonuçları tek tek yorumlayarak hangi gözlemin hangi grafik tarafından desteklendiğini not ettim. Günün sonunda temiz veriyi grafiklerle incelemenin, tablodan fark edemediğim örüntüleri görmemi kolaylaştırdığını anladım. Yanında çalıştığım mühendis, bir sonraki çalışmada artık tablo verisinden görüntü verisine geçerek OpenCV ile görüntünün nasıl okunup işlendiğini inceleyebileceğimi söyledi. Bu nedenle sonraki gün OpenCV ve temel görüntü işlemleri konusuna geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 9 — 30 TEMMUZ 2026
**KISIM:** OpenCV Temelleri ve Görüntü Ön İşleme  
**YAPRAK NO:** 17  
**YAPILAN İŞ:** Görüntü Okuma, Shape/Dtype ve BGR-RGB Kanal Yapısının İncelenmesi  
**TARİH:** 30/07/2026

Stajımın dokuzuncu gününde, bir önceki gün tablo verilerini grafiklerle incelemeyi öğrendikten sonra bu kez görüntü verisi üzerinde çalışmaya başladım. Yanında çalıştığım mühendis, bir görüntünün bilgisayar açısından yalnızca ekranda görünen bir fotoğraf olmadığını; piksel değerlerinden oluşan sayısal bir veri yapısı olduğunu hatırlattı. NumPy ile görüntünün matris mantığını daha önce incelemiştim. Bugün ise bu görüntüleri okumak, dönüştürmek ve temel işlemler uygulamak için OpenCV kütüphanesini kullanmaya başladım. İlk olarak bir örnek görüntüyü OpenCV ile açtım ve görüntünün belleğe nasıl aktarıldığını inceledim.
Görüntüyü okuduktan sonra ilk olarak shape ve dtype bilgilerine baktım. Shape değerinden görüntünün yüksekliğini, genişliğini ve renk kanalı sayısını görebildiğimi tekrar gözlemledim. Dtype bilgisinin ise piksel değerlerinin hangi veri tipinde tutulduğunu gösterdiğini öğrendim. Örnek görüntünün uint8 türünde olduğunu ve renk kanallarındaki değerlerin 0 ile 255 arasında bulunduğunu gördüm. Yanında çalıştığım mühendis, görüntü üzerinde işlem yaparken hem boyut bilgisinin hem de veri tipinin önemli olduğunu; çünkü yanlış boyut veya değer aralığının sonraki işlemleri etkileyebileceğini anlattı.
Daha sonra OpenCV ile görüntü okurken karşıma çıkan BGR ve RGB sıralamasını inceledim. Görüntüyü OpenCV ile açıp başka bir ortamda doğrudan gösterdiğimde bazı renklerin beklediğimden farklı görünebildiğini fark ettim. Yanında çalıştığım mühendis, OpenCV'nin renkli görüntüleri varsayılan olarak BGR kanal sırasıyla tuttuğunu, birçok görüntü gösterme aracının ise RGB sırasını kullandığını anlattı. Kanalları uygun sıraya dönüştürdüğümde renklerin doğru biçimde görüntülendiğini gördüm. Bu küçük deney, görüntünün üç kanala sahip olduğunu bilmenin tek başına yeterli olmadığını; kanalların hangi sırada tutulduğunu da kontrol etmem gerektiğini gösterdi.
Günün ilk bölümünde son olarak görüntünün belirli bölgelerine erişmeyi ve küçük temel işlemler yapmayı denedim. Satır ve sütun aralıklarını kullanarak görüntünün bir bölümünü seçtim ve bu bölgenin de NumPy dizisi olarak tutulduğunu gördüm. Bu işlem sayesinde bir görüntünün tamamı yerine yalnız ilgilendiğim bölge üzerinde çalışabileceğimi daha iyi anladım. Yanında çalıştığım mühendis, gerçek görüntü işleme çalışmalarında çoğu zaman görüntünün boyutunu değiştirmek veya belirli bir bölgesini ayırmak gerektiğini söyledi. Bunun üzerine günün devamında resize işlemini, en-boy oranını ve farklı interpolation yöntemlerini incelemeye geçtim.

**KONTROL SONUCU:**

---

## GÜN 9 — DEVAM
**KISIM:** OpenCV Temelleri ve Görüntü Ön İşleme  
**YAPRAK NO:** 18  
**YAPILAN İŞ:** Resize, En-Boy Oranı, Interpolation ve Temel Ön İşleme Yaklaşımlarının İncelenmesi  
**TARİH:** 30/07/2026

Günün devamında görüntü boyutlandırma işlemini inceledim. İlk olarak bir görüntünün genişlik ve yükseklik değerlerini doğrudan değiştirerek farklı boyutlarda kopyalar oluşturdum. Yanında çalıştığım mühendis, yalnızca hedef genişlik ve yüksekliği vermenin görüntünün en-boy oranını bozabileceğini anlattı. Kare olmayan bir görüntüyü zorla kare boyuta getirdiğimde nesnelerin yatay veya dikey yönde uzadığını gözlemledim. Bu nedenle bir boyutu değiştirirken diğer boyutu aynı orana göre hesaplamanın görüntünün geometrisini korumak açısından daha doğru olduğunu öğrendim.
Resize işlemi sırasında interpolation kavramını da inceledim. Görüntünün boyutu değiştiğinde yeni piksel konumlarının nasıl doldurulacağına karar verilmesi gerektiğini öğrendim. Nearest-neighbor yaklaşımının en yakın piksel değerini kullandığını, linear ve cubic gibi yöntemlerin ise çevredeki piksellerden yararlanarak yeni değerler hesapladığını gördüm. Küçük bir görüntüyü büyüterek yöntemleri karşılaştırdığımda nearest-neighbor sonucunda piksellerin daha belirgin hâle gelebildiğini, diğer yöntemlerin daha yumuşak geçişler oluşturabildiğini gözlemledim. Yanında çalıştığım mühendis, tek bir interpolation yönteminin her işlem için en iyi kabul edilmemesi gerektiğini ve seçimin yapılan işleme göre değişebileceğini söyledi.
Öğrendiklerimi bir araya getirmek için küçük bir görüntü işleme deneyi yaptım. Örnek görüntüyü OpenCV ile okudum, shape ve dtype bilgilerini kontrol ettim, BGR görüntüyü RGB sırasına dönüştürdüm ve en-boy oranını koruyarak daha küçük bir boyuta getirdim. Daha sonra orijinal görüntü ile yeniden boyutlandırılmış görüntüyü yan yana inceleyerek geometrinin korunup korunmadığını kontrol ettim. Bu çalışma sırasında görüntü işleme adımlarını belirli bir sırayla uygulamanın önemli olduğunu fark ettim. Görüntünün yanlış kanal sırasıyla veya bozulmuş oranla sonraki işlemlere verilmesi, daha sonra elde edilecek sonuçları da etkileyebilirdi.
Günün sonunda OpenCV ile görüntü okuma, temel özelliklerini kontrol etme ve yeniden boyutlandırma işlemlerini uygulamış oldum. Ancak renkli görüntüyü üç kanal olarak görmek, renk bilgisinin hangi amaçla nasıl kullanılacağını henüz açıklamıyordu. Yanında çalıştığım mühendis, aynı rengin farklı renk uzaylarında farklı biçimde temsil edilebildiğini ve bazı işlemlerde RGB yerine başka renk uzaylarının daha uygun olabileceğini anlattı. Özellikle renk seçme, eşikleme ve algısal renk karşılaştırması gibi işlemlerde bu farkın önemli olacağını söyledi. Bu nedenle bir sonraki çalışma gününde RGB, HSV ve CIELAB renk uzaylarını karşılaştırarak neden farklı renk temsillerine ihtiyaç duyulduğunu incelemeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 10 — 31 TEMMUZ 2026
**KISIM:** Renk Uzayları ve Renk Farkı  
**YAPRAK NO:** 19  
**YAPILAN İŞ:** RGB ve HSV Renk Temsillerinin Karşılaştırılması ve Renk Eşikleme Mantığının İncelenmesi  
**TARİH:** 31/07/2026

Stajımın onuncu gününde, bir önceki gün OpenCV ile görüntülerin nasıl okunduğunu ve renk kanallarının nasıl tutulduğunu öğrendikten sonra renk bilgisinin bilgisayarda neden farklı biçimlerde temsil edildiğini incelemeye başladım. Yanında çalıştığım mühendis, ekranda gördüğüm tek bir rengin bilgisayar açısından farklı renk uzaylarında farklı sayısal bileşenlerle ifade edilebildiğini anlattı. Aynı görüntünün RGB, HSV veya CIELAB gibi farklı renk uzaylarına dönüştürülmesinin görüntüyü değiştirmekten çok, renk bilgisini yapılacak işleme daha uygun bir biçimde ifade etmek anlamına geldiğini öğrendim.
İlk olarak RGB renk uzayını ele aldım. Kırmızı, yeşil ve mavi kanalların farklı oranlarda birleşmesiyle renklerin temsil edildiğini ve görüntüleme sistemlerinde bu yapının yaygın olarak kullanıldığını gördüm. Örnek bir halı görüntüsündeki birkaç pikselin kanal değerlerini inceleyerek ekranda gördüğüm renklerin üç sayısal değerden oluştuğunu tekrar gözlemledim. Daha sonra aynı görüntünün parlaklığını değiştirdiğimde üç kanalın değerlerinin de değişebildiğini fark ettim. Yanında çalıştığım mühendis, bu nedenle RGB değerlerine doğrudan bakarak renk seçmenin ışık ve parlaklık değişimlerinden etkilenebileceğini anlattı.
Bu durumu küçük bir uygulamayla incelemek için görüntü üzerinde belirli bir mavi tona ait bölgeleri RGB kanal sınırları kullanarak ayırmayı denedim. İlk görüntüde seçtiğim sınırlar bazı bölgeleri ayırabildi, ancak görüntünün parlaklığı değiştirildiğinde aynı sınırların önceki kadar tutarlı davranmadığını gördüm. Bu sonuç RGB'nin yanlış bir renk uzayı olduğu anlamına gelmiyordu; yalnız renk seçme gibi bir işlemde parlaklık ile renk bilgisinin birbirinden daha açık ayrıldığı bir gösterimin işimi kolaylaştırabileceğini gösteriyordu.
Yanında çalıştığım mühendisin yönlendirmesiyle bu noktada HSV renk uzayını incelemeye geçtim. HSV yapısında hue bileşeninin rengin tonunu, saturation bileşeninin rengin doygunluğunu, value bileşeninin ise parlaklık düzeyini ifade ettiğini öğrendim. Aynı görüntüyü HSV biçimine dönüştürdüğümde renk tonu ile parlaklık bilgisinin ayrı bileşenlerde ele alınabilmesinin özellikle belirli bir renk aralığını seçerken daha anlaşılır olduğunu gördüm. Böylece farklı renk uzaylarının aynı görüntüye farklı bir bakış sunduğunu daha net anlamaya başladım.

**KONTROL SONUCU:**

---

## GÜN 10 — DEVAM
**KISIM:** Renk Uzayları ve Renk Farkı  
**YAPRAK NO:** 20  
**YAPILAN İŞ:** CIELAB Renk Uzayı ve Delta E ile Algısal Renk Farkının İncelenmesi  
**TARİH:** 31/07/2026

Günün devamında HSV renk uzayını kullanarak küçük bir renk eşikleme deneyi yaptım. Görüntüde seçtiğim renk tonuna yakın bölgeleri hue ve saturation değerleri üzerinden ayırdım ve oluşan maskeyi inceledim. RGB ile yaptığım ilk denemeye göre renk tonunu ayrı değerlendirebilmek işlemi daha anlaşılır hâle getirdi. Bununla birlikte yanında çalıştığım mühendis, HSV'nin de bütün renk problemlerini çözen tek yöntem olmadığını anlattı. Özellikle iki rengin insan gözüne ne kadar yakın göründüğünü sayısal olarak karşılaştırmak istediğimde farklı bir renk temsilinin daha uygun olabileceğini söyledi.
Bu nedenle CIELAB renk uzayını incelemeye başladım. CIELAB'da L bileşeninin açıklık-parlaklık bilgisini, a ve b bileşenlerinin ise renk yönlerini temsil ettiğini öğrendim. Yanında çalıştığım mühendis, bu renk uzayının renkler arasındaki sayısal farkların insanın algıladığı renk farkına daha yakın olacak şekilde tasarlandığını anlattı. Aynı görüntüyü LAB biçimine dönüştürüp kanalları ayrı ayrı incelediğimde parlaklık bilgisinin renk bileşenlerinden ayrılmasının renk karşılaştırması açısından neden yararlı olabileceğini daha iyi anladım.
Öğrendiklerimi karşılaştırmak için aynı görüntüyü RGB, HSV ve CIELAB biçimlerinde ele aldım. RGB'nin görüntünün doğal kanal yapısını anlamak ve görüntüleme işlemleri için kullanışlı olduğunu, HSV'nin belirli renk tonlarını seçme ve eşikleme işlemlerinde daha anlaşılır olabildiğini, CIELAB'ın ise renkler arasındaki algısal farkları incelemeye daha uygun bir temel sunduğunu gördüm. Burada bir renk uzayını diğerinden genel olarak daha iyi kabul etmemem gerektiğini öğrendim. Kullanılacak temsilin, görüntü üzerinde yapmak istediğim işleme göre seçilmesi gerektiği sonucuna ulaştım.
Günün sonunda aynı görüntünün farklı renk uzaylarında temsil edilmesinin neden gerekli olduğunu daha iyi anladım. Özellikle bir görüntüde baskın renkleri bulmak veya iki renk paletini karşılaştırmak istediğimde yalnız tek tek piksel değerlerine bakmanın yeterli olmayacağını fark ettim. Yanında çalıştığım mühendis, çok sayıda piksel rengini birkaç temsil edici renk grubuna ayırmak için kümeleme yöntemlerinden yararlanılabileceğini anlattı. Bu nedenle bir sonraki çalışma gününde K-Means yöntemini kullanarak görüntüdeki baskın renkleri çıkarmayı ve farklı küme sayılarının oluşan renk paletini nasıl değiştirdiğini incelemeye karar verdim.

CIELAB incelemesinin sonunda iki rengin yalnız kanal değerleriyle değil algısal fark açısından da karşılaştırılabileceğini görmek için Delta E yaklaşımına baktım. Aynı renk çiftlerinde RGB uzaklığı ile Delta E değerlerinin her zaman aynı yorumu vermediğini gördüm. Bu nedenle renk benzerliği probleminde kullanılan sayısal ölçünün de veri temsili kadar önemli olduğunu ve gerçek bir kalite eşiğinin yalnız örnek çalışmaya bakılarak belirlenemeyeceğini not ettim.

**KONTROL SONUCU:**

---

## GÜN 11 — 1 AĞUSTOS 2026
**KISIM:** K-Means ile Baskın Renk Paleti  
**YAPRAK NO:** 21  
**YAPILAN İŞ:** K-Means Mantığı ve Farklı Küme Sayılarının Karşılaştırılması  
**TARİH:** 01/08/2026

Stajımın on birinci gününde, bir önceki gün RGB, HSV ve CIELAB renk uzaylarını karşılaştırdıktan sonra bir görüntüdeki çok sayıdaki piksel rengini daha anlaşılır biçimde nasıl özetleyebileceğimi incelemeye başladım. Yanında çalıştığım mühendis, tek bir halı görüntüsünde binlerce hatta milyonlarca piksel bulunduğunu ve bu piksellerin her birinin farklı renk değerleri taşıyabildiğini anlattı. Böyle bir görüntüyü yalnız tek tek piksel değerlerine bakarak yorumlamanın zor olduğunu, bu nedenle birbirine yakın renklerin gruplandırılarak birkaç temsil edici renge indirgenebileceğini söyledi. Bu noktada K-Means yöntemini kullanarak baskın renk paleti çıkarma fikrini öğrenmeye başladım.
K-Means'in temel mantığını küçük bir sayısal örnek üzerinden anlamaya çalıştım. Yanında çalıştığım mühendis, yöntemin verileri önceden belirlenen sayıda gruba ayırmaya çalıştığını ve her grubun merkezinin o gruptaki örnekleri temsil ettiğini anlattı. Görüntü üzerinde çalışırken her pikseli üç renk değerinden oluşan bir nokta gibi düşündüm. Algoritma benzer renk değerlerine sahip pikselleri aynı gruba yaklaştırıyor, ardından her grubun ortalama konumunu temsil eden bir merkez oluşturuyordu. Bu merkezlerin görüntüdeki baskın renkleri yaklaşık olarak temsil edebileceğini gördüm. Buradaki amacım K-Means'in bütün renklerin anlamını bildiğini düşünmek değil, benzer sayısal renkleri gruplandırdığını anlamaktı.
Daha sonra aynı görüntü üzerinde farklı küme sayıları kullanarak küçük bir karşılaştırma yaptım. İlk olarak k=3 seçerek görüntüyü üç ana renk grubuyla özetledim. Bu durumda palet oldukça sadeleşti ancak bazı ikincil renklerin ana grupların içinde kaybolabildiğini gördüm. k=5 kullandığımda daha ayrıntılı bir palet oluştu ve görüntüdeki ana renklerle birlikte bazı ara tonlar da ayrı gruplar hâline geldi. k=8 değerinde ise renk çeşitliliği daha ayrıntılı temsil edildi, fakat birbirine çok yakın bazı tonların ayrı kümelere bölündüğünü gözlemledim. Bu deney, küme sayısını artırmanın her zaman daha iyi bir palet anlamına gelmediğini gösterdi.
Yanında çalıştığım mühendis, K-Means'teki k değerinin algoritmanın kendisi tarafından otomatik olarak 'doğru renk sayısı' olarak bilinmediğini söyledi. Seçilen k değerinin görüntüyü ne kadar ayrıntılı özetlemek istediğime bağlı olduğunu öğrendim. Çok küçük bir k değeri önemli renkleri birleştirebilirken, çok büyük bir k değeri birbirine çok yakın tonları gereksiz yere ayırabiliyordu. Günün ilk bölümünün sonunda K-Means'in bir görüntünün renklerini daha az sayıda temsil edici merkezle özetlemek için kullanılabileceğini, ancak elde edilen paletin kullanılan k değerine bağlı olduğunu anladım. Daha sonra aynı yöntemin RGB ve CIELAB renk uzaylarında nasıl farklı sonuçlar verebileceğini incelemeye geçtim.

**KONTROL SONUCU:**

---

## GÜN 11 — DEVAM
**KISIM:** K-Means ile Baskın Renk Paleti  
**YAPRAK NO:** 22  
**YAPILAN İŞ:** RGB ve CIELAB Üzerinde Renk Gruplama ve Baskın Renk Oranlarının İncelenmesi  
**TARİH:** 01/08/2026

Günün devamında K-Means işlemini renk uzayı seçiminin sonucu nasıl etkilediğini görmek amacıyla karşılaştırdım. Önce pikselleri RGB değerleri üzerinden gruplandırdım. Algoritma kırmızı, yeşil ve mavi kanal değerleri arasındaki sayısal uzaklıklara göre kümeler oluşturuyordu. Daha önce öğrendiğim gibi RGB görüntüleme açısından doğal bir temsil sunsa da iki RGB renginin sayısal olarak yakın olması, insan gözü tarafından aynı ölçüde yakın algılanacakları anlamına gelmeyebilirdi. Bu nedenle yanında çalıştığım mühendisin yönlendirmesiyle aynı görüntünün CIELAB gösterimi üzerinde de K-Means uyguladım.
CIELAB üzerinde yaptığım gruplamada renklerin açıklık ve renk bileşenleri farklı biçimde temsil edildiği için oluşan küme merkezlerinin RGB'deki sonuçlarla tamamen aynı olmadığını gördüm. Birbirine yakın görünen bazı tonların gruplanma biçiminde farklılıklar oluşabildiğini gözlemledim. Buradan LAB üzerinde kümelemenin her durumda daha iyi olduğu sonucunu çıkarmadım. Yanında çalıştığım mühendis, renk uzayının yapılacak işleme göre seçilmesi gerektiğini hatırlattı; ancak algısal renk karşılaştırmalarında CIELAB'ın yararlı bir temel sağlayabileceğini daha iyi anladım.
Daha sonra yalnız küme merkezlerine bakmanın görüntüde hangi rengin ne kadar yer kapladığını göstermediğini fark ettim. Her kümeye atanan piksel sayısını toplam piksel sayısıyla karşılaştırarak baskın renk oranlarını inceledim. Böylece paletteki bir rengin yalnız var olup olmadığını değil, görüntünün yaklaşık ne kadarını temsil ettiğini de görebildim. Bir küme merkezinin belirgin bir renk olması, o rengin görüntüde en fazla kullanılan renk olduğu anlamına gelmiyordu; bunu anlayabilmek için ilgili kümeye düşen piksel oranına da bakmak gerekiyordu.
Günün sonunda K-Means'in çok sayıdaki piksel rengini birkaç temsil edici renge indirgemek için kullanışlı olduğunu öğrendim. Bununla birlikte küme sayısını benim belirlemem gerekiyordu, sonuç başlangıç koşullarından etkilenebiliyor ve algoritma oluşturduğu renklerin tasarım açısından ne anlama geldiğini bilmiyordu. Ayrıca iki görüntüden çıkardığım paletlerde benzer renklerin bulunması, bu renklerin algısal olarak ne kadar yakın olduğunu tek başına açıklamıyordu. Yanında çalıştığım mühendis, iki renk arasındaki farkı insan algısına daha yakın biçimde sayısallaştırmak için CIELAB üzerinde Delta E yaklaşımının kullanılabileceğini anlattı. Bu nedenle bir sonraki gün renk paletleri arasındaki algısal farkı Delta E ile incelemeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 12 — 3 AĞUSTOS 2026
**KISIM:** Perspektif Düzeltme ve Homografi  
**YAPRAK NO:** 23  
**YAPILAN İŞ:** Açılı Görüntülerde Perspektif Bozulmasının ve Dört Noktalı Dönüşümün İncelenmesi  
**TARİH:** 03/08/2026

Stajımın on ikinci gününde, önceki günlerde renkleri sayısal olarak karşılaştırmayı öğrendikten sonra görüntünün geometrisinin de analiz sonuçlarını etkileyebileceğini incelemeye başladım. Yanında çalıştığım mühendis, bir halı fotoğrafı kameraya tam karşıdan değil de açılı biçimde çekildiğinde gerçekte dikdörtgen olan yüzeyin görüntü üzerinde yamuk veya trapez biçiminde görünebildiğini anlattı. Böyle bir görüntü üzerinde renk bölgelerinin konumu, motiflerin şekli veya kenarların uzunluğu incelenecekse perspektif bozulmasının sonucu yanıltabileceğini söyledi. Bu nedenle görüntüyü analiz etmeden önce geometrik olarak daha düzenli bir görünüme getirme ihtiyacını anlamaya çalıştım.
İlk olarak daha önce kullandığım rotate ve resize işlemlerinin bu problemi çözüp çözemeyeceğini denedim. Açılı çekilmiş örnek bir dikdörtgen görüntüyü döndürdüğümde yalnızca görüntünün yönünün değiştiğini, fakat üst ve alt kenarlar arasındaki perspektif farkının devam ettiğini gördüm. Resize işlemi ise görüntüyü farklı boyuta getirdi ancak yamuk görünen kenarları gerçek dikdörtgen biçimine dönüştürmedi. Yanında çalıştığım mühendis, rotate işleminin görüntüyü düzlem üzerinde çevirdiğini, resize işleminin ise boyutunu değiştirdiğini; perspektif bozulmasında ise görüntüdeki noktaların konumlarının birbirine göre yeniden eşlenmesi gerektiğini anlattı.
Bu noktada perspective transform ve homography kavramlarını incelemeye başladım. Yanında çalıştığım mühendis, düz bir yüzey üzerindeki dört köşenin görüntüdeki konumları bilindiğinde bu noktaların yeni bir dikdörtgen düzleme eşlenebileceğini anlattı. Örnek görüntü üzerinde sol üst, sağ üst, sağ alt ve sol alt köşeleri belirledim. Daha sonra bu dört noktayı hedef görüntüdeki dikdörtgenin dört köşesiyle eşleştirdim. Bu işlemin yalnızca görüntüyü döndürmekten farklı olduğunu, görüntünün içindeki diğer noktaların da köşe eşlemesine göre yeni konumlara taşındığını öğrendim.
Dört nokta üzerinden hesaplanan dönüşümün görüntünün tamamına uygulanmasıyla açılı görünen yüzeyi üstten bakılıyormuş gibi daha düzenli hâle getirebildim. OpenCV'de perspektif dönüşüm için kullanılan temel fonksiyonları inceleyerek kaynak noktalar ile hedef noktalar arasındaki ilişkinin nasıl kurulduğunu anlamaya çalıştım. Elde ettiğim düzeltilmiş görüntüyü orijinal görüntüyle yan yana karşılaştırdığımda, özellikle kenarların daha düzenli hâle geldiğini ve yüzeyin dikdörtgene daha yakın göründüğünü gözlemledim. Günün ilk bölümünde homography yönteminin görüntünün yönünü değiştirmekten çok, perspektif nedeniyle bozulan düzlemsel geometrinin yeniden düzenlenmesi için kullanıldığını anlamış oldum.

**KONTROL SONUCU:**

---

## GÜN 12 — DEVAM
**KISIM:** Perspektif Düzeltme ve Homografi  
**YAPRAK NO:** 24  
**YAPILAN İŞ:** Köşe Seçiminin Sonuca Etkisinin ve Düzeltilmiş Görüntünün Değerlendirilmesi  
**TARİH:** 03/08/2026

Günün devamında dört köşenin doğru seçilmesinin sonucu ne kadar etkilediğini incelemeye başladım. İlk denemede köşe noktalarını yüzeyin gerçek sınırlarına mümkün olduğunca yakın seçtim ve düzeltilmiş görüntüyü kaydettim. Daha sonra köşelerden birini bilinçli olarak biraz içeri kaydırarak aynı dönüşümü tekrar uyguladım. İkinci sonuçta görüntünün bir tarafının gereğinden fazla gerildiğini ve kenarların önceki kadar düzgün görünmediğini fark ettim. Yanında çalıştığım mühendis, homography matrisinin seçtiğim dört noktaya göre hesaplandığını ve bu nedenle başlangıç noktalarındaki küçük hataların bütün görüntüye yayılabileceğini anlattı.
Bu deneme bana manuel köşe seçiminin basit ve anlaşılır bir yöntem olmasına rağmen kullanıcı seçimine bağlı olduğunu gösterdi. Özellikle görüntünün kenarları arka planla benzer renkteyse, gölge varsa veya halının sınırları net görünmüyorsa doğru köşe noktalarını belirlemek zorlaşabilirdi. Yanında çalıştığım mühendis, ileride kenar ve kontur analiziyle köşe noktalarının otomatik bulunmasının araştırılabileceğini, ancak ilk aşamada dönüşüm mantığını anlamak için dört noktayı kontrollü biçimde seçmenin daha uygun olduğunu söyledi. Böylece önce basit ve gözle kontrol edebildiğim yöntemle çalışmanın, daha gelişmiş otomatik yöntemlere geçmeden önce iyi bir başlangıç sağladığını gördüm.
Daha sonra hedef görüntünün boyutunun nasıl seçileceğini de inceledim. Kaynak görüntüde karşılıklı kenarlar perspektif nedeniyle farklı uzunluklarda görünebildiği için hedef dikdörtgenin genişlik ve yüksekliğini belirlerken köşeler arasındaki uzaklıkların dikkate alınabileceğini öğrendim. Çok küçük bir hedef boyut seçildiğinde ayrıntı kaybı, gereğinden büyük bir boyut seçildiğinde ise yeni piksel değerlerinin tahmin edilmesi nedeniyle yumuşama oluşabileceğini gözlemledim. Bu nedenle perspektif düzeltme ile resize işleminin birbirinden ayrı konular olmasına rağmen sonuç görüntünün kalitesinde birlikte etkili olabileceğini anladım.
Günün sonunda görüntünün geometrisini düzeltmenin sonraki görüntü işleme adımları için önemli olduğunu daha net gördüm. Aynı yüzey farklı açılardan çekildiğinde motiflerin şekli, kenarların konumu ve belirli bölgelerin alanı değişmiş gibi görünebilirdi. Perspektifi düzeltilmiş bir görüntü üzerinde renk bölgelerini, motifleri veya sınırları karşılaştırmak daha düzenli bir başlangıç sağlıyordu. Yanında çalıştığım mühendis, bir sonraki aşamada görüntü içerisindeki belirli bölgeleri ayırmanın nasıl yapılabileceğini inceleyebileceğimi söyledi. Bu nedenle sonraki çalışma gününde threshold, morphology, contour ve connected components yöntemleriyle temel segmentasyon konusuna geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 13 — 4 AĞUSTOS 2026
**KISIM:** Morfolojik İşlemler, Kenar ve Çizgi Tespiti  
**YAPRAK NO:** 25  
**YAPILAN İŞ:** Morfolojik İşlemlerle Gürültü ve Bölge Yapısının İncelenmesi  
**TARİH:** 04/08/2026

On birinci gün ikili maskeler ve gri seviye görüntüler üzerinde kullanılan morfolojik işlemleri çalıştım. Erosion ve dilation işlemlerinin bir bölgeyi küçültüp büyütebildiğini; opening ve closing işlemlerinin ise küçük gürültüleri temizlemek veya küçük boşlukları kapatmak için kullanılabildiğini öğrendim. Morfolojik işlemleri önce küçük ikili görüntüler üzerinde deneyerek erosion ve dilation'ın beyaz bölgeleri nasıl küçültüp büyüttüğünü daha açık biçimde gözlemledim.
Bütün görseller proje içinde üretilmiş sentetik halı örnekleriydi. `carpet_clean_reference`, `carpet_defect_yarn_break`, `carpet_defect_hole_puncture` ve `carpet_defect_oil_slub` dosyalarını gerçek kalite kontrol görüntüsü gibi değil, farklı piksel desenlerini temsil eden test materyali olarak kullandım. Kernel boyutunu değiştirdiğimde sonucun belirgin şekilde değiştiğini gördüm; bu nedenle tek bir parametrenin bütün kusur türleri için uygun olmayacağını anladım.
White Top-Hat ve Black-Hat işlemlerinin sırasıyla çevresine göre daha parlak veya daha koyu küçük bölgeleri öne çıkarabildiğini gördüm. Kernel boyutunun sonucu doğrudan etkilediğini, çok büyük bir kernel seçildiğinde desenin normal ayrıntılarının da kusur gibi görünebildiğini gözlemledim. Opening ve closing işlemlerini sentetik gürültü ve küçük boşluklar üzerinde karşılaştırarak hangi durumda hangi sıranın daha yararlı olduğunu inceledim.
Bu nedenle morfolojik işlem sonuçlarını doğrudan “kusur var/yok” kararı olarak kullanmadım. Sentetik görsellerde hangi işlemin hangi tür yapıyı vurguladığını inceleyerek daha sonraki segmentasyon ve özellik çıkarımı günleri için temel oluşturdum. Gerçek kusur örnekleri bulunmadığı için algoritmanın endüstriyel başarı oranı hakkında yorum yapmadım; yalnızca işlemlerin görsel etkisini ve mantığını öğrendim.

Yöntemleri karşılaştırırken aynı görüntü üzerinde mümkün olduğunca tek değişkeni değiştirmeye dikkat ettim. Böylece oluşan farkın kullanılan filtre, eşik, renk uzayı veya geometrik dönüşümden mı kaynaklandığını daha açık biçimde takip edebildim. Görüntü üzerinde yalnız gözle iyi görünen sonucu seçmenin yeterli olmadığını; boyut, piksel aralığı, maske alanı, kenar sayısı veya benzeri basit sayısal kontrollerin de sonucu doğrulamada yararlı olabileceğini gördüm. Kullandığım görseller şirketin canlı kalite kontrol sisteminden alınmadığı için elde ettiğim sonuçları üretim doğruluğu olarak değil, yöntemin çalışma mantığını anlamaya yönelik kontrollü örnekler olarak değerlendirdim.

**KONTROL SONUCU:**

---

## GÜN 13 — DEVAM
**KISIM:** Morfolojik İşlemler, Kenar ve Çizgi Tespiti  
**YAPRAK NO:** 26  
**YAPILAN İŞ:** Canny ve Hough ile Kenar ve Çizgi Yapısının İncelenmesi  
**TARİH:** 04/08/2026

On ikinci gün görüntüdeki ani parlaklık değişimlerinden kenar bulma yöntemlerini çalıştım. Sobel, Scharr, Laplacian ve Canny algoritmalarını aynı sentetik halı görseli üzerinde uyguladım. Böylece her yöntemin kenarları farklı yoğunlukta ve farklı gürültü seviyesinde gösterebildiğini karşılaştırdım. Sobel ve Scharr çıktılarında yatay ve dikey değişimleri ayrı ayrı inceleyerek gradyan kavramını piksel seviyesinde daha iyi anlamaya çalıştım.
Kenar operatörlerinde görüntünün önce gri tona çevrilmesi ve bazı durumlarda hafif bulanıklaştırılması gerektiğini gördüm. Özellikle Canny algoritmasındaki alt ve üst eşiklerin sonucu belirgin şekilde etkilediğini, tek bir eşik değerinin her görüntü için uygun olmayacağını not ettim. Laplacian ve Canny sonuçlarını aynı sentetik halı üzerinde karşılaştırınca yöntemlerin kenar yoğunluğu ve gürültüye verdikleri tepkinin farklı olduğunu gördüm.
Bu gün de gerçek kalite kamerasından veri kullanmadım. Kullanılan bordür görüntüleri sentetikti. Amaç, halı gibi tekrar eden desen içeren bir görselde normal desen kenarları ile dış sınırların birbirine karışabileceğini görmek ve çizgi tespitine hazırlık yapmaktı. Canny eşiklerini değiştirerek çok düşük değerde gereksiz kenarların, çok yüksek değerde ise bazı gerçek sınırların kaybolabildiğini gözlemledim.
İlk bölüm sonunda farklı kenar görüntülerini notebook üzerinde yan yana koyarak hangi yöntemin dış sınırları daha belirgin verdiğini inceledim. “En iyi yöntem” gibi genel bir sonuca varmak yerine, görüntü yapısına ve sonraki işleme göre seçim yapılması gerektiğini öğrendim. Bu parametrelerin gerçek kamera görüntülerine doğrudan taşınamayacağını, gerçek görüntü koşullarında yeniden ayarlanması gerektiğini not ettim.

Bu aşamada alternatif yöntemleri aynı problem açısından düşünmeye çalıştım. Daha karmaşık bir yöntem kullanmanın otomatik olarak daha doğru sonuç vermediğini; bazı örneklerde basit eşikleme veya temel bir özellik çıkarımının yeterli olabileceğini, bazı görüntülerde ise ışık, arka plan veya desen karmaşıklığı nedeniyle daha gelişmiş yaklaşımlara ihtiyaç duyulabileceğini gördüm. Bu nedenle kullandığım her tekniğin hangi varsayıma dayandığını ve hangi koşulda yetersiz kalabileceğini not ettim. Bir sonraki adıma geçerken yeni yöntemi yalnız daha gelişmiş olduğu için değil, mevcut yöntemde gözlediğim belirli bir sınırlamayı çözmek için seçmeye çalıştım.

**KONTROL SONUCU:**

---

## GÜN 14 — 5 AĞUSTOS 2026
**KISIM:** Klasik Görüntü Segmentasyonu  
**YAPRAK NO:** 27  
**YAPILAN İŞ:** Otsu, Watershed ve GrabCut yöntemlerinin sentetik görsellerde uygulanması  
**TARİH:** 05/08/2026

On üçüncü gün görüntünün tamamını tek parça olarak değerlendirmek yerine belirli bölgeleri ayırmayı amaçlayan segmentasyon yöntemlerini çalıştım. Otsu eşikleme, Watershed ve GrabCut yöntemlerini aynı sentetik halı örnekleri üzerinde denedim. Otsu yöntemini uygularken eşik değerinin görüntü histogramından otomatik seçildiğini ve bu yüzden elle sabit eşik vermekten farklı bir yaklaşım olduğunu gözlemledim.
Otsu yönteminin görüntü histogramından otomatik bir eşik seçtiğini, Watershed yönteminin işaretleyiciler üzerinden bölgeleri ayırabildiğini ve GrabCut’ın ön plan-arka plan ayrımı için farklı bir yaklaşım kullandığını kod üzerinde inceledim. Her yöntemin aynı girdide farklı maske üretebildiğini gördüm. Watershed için ön işlem adımlarını takip ederek işaretçi bölgelerin doğru hazırlanmasının sonuç üzerinde önemli olduğunu gördüm.
Sentetik veri kullanmanın bu gün önemli bir avantajı oldu; çünkü referans maskeyi kendim üretebildiğim için segmentasyon sonucunu neyle karşılaştıracağım belliydi. Gerçek üretim görüntülerinde ise böyle bir ground-truth maskenin insan tarafından ayrıca hazırlanması gerekebilir. GrabCut yönteminde başlangıç dikdörtgeninin veya maskenin sonucu etkilediğini deneyerek segmentasyon yöntemlerinin çoğunda başlangıç bilgisinin önemli olabileceğini fark ettim.
Yöntemlerin parametrelerini değiştirerek motif, zemin ve bordür bölgelerinin ayrılma biçimini gözlemledim. Bazı yöntemler daha hızlı çalışırken bazılarının sınırları daha düzgün verdiğini gördüm. Bu farkın veri yapısına bağlı olduğunu not ettim. Referans maskeler de proje için oluşturulmuş sentetik etiketlerdi; bu nedenle IoU sonuçlarını gerçek saha doğruluğu olarak yorumlamadım.

Yöntemleri karşılaştırırken aynı görüntü üzerinde mümkün olduğunca tek değişkeni değiştirmeye dikkat ettim. Böylece oluşan farkın kullanılan filtre, eşik, renk uzayı veya geometrik dönüşümden mı kaynaklandığını daha açık biçimde takip edebildim. Görüntü üzerinde yalnız gözle iyi görünen sonucu seçmenin yeterli olmadığını; boyut, piksel aralığı, maske alanı, kenar sayısı veya benzeri basit sayısal kontrollerin de sonucu doğrulamada yararlı olabileceğini gördüm. Kullandığım görseller şirketin canlı kalite kontrol sisteminden alınmadığı için elde ettiğim sonuçları üretim doğruluğu olarak değil, yöntemin çalışma mantığını anlamaya yönelik kontrollü örnekler olarak değerlendirdim.

**KONTROL SONUCU:**

---

## GÜN 14 — DEVAM
**KISIM:** Klasik Görüntü Segmentasyonu  
**YAPRAK NO:** 28  
**YAPILAN İŞ:** IoU ve işlem süresiyle üç yöntemin sentetik benchmark üzerinde incelenmesi  
**TARİH:** 05/08/2026

Günün ikinci bölümünde segmentasyon maskelerini referans maskeyle IoU üzerinden karşılaştırdım. Ayrıca her yöntemin çalışma süresini kaydettim. Repo içindeki sayılar sentetik görüntü ve kendi bilgisayar ortamına ait benchmark değerleriydi; canlı üretim hattı ölçümü değildi. Üç yöntemin çıktılarını aynı panelde yan yana koyarak yalnızca IoU değerine değil, sınırların görsel olarak nasıl ayrıldığına da baktım.
Karşılaştırma panelinde orijinal görüntü, referans maske ve üç yöntemden elde edilen sonuçları aynı ekranda gösterdim. Bu şekilde yalnız tek bir puana bakmak yerine maskenin nerede hata yaptığını da görsel olarak inceleyebildim. İşlem sürelerini karşılaştırdığımda daha karmaşık yöntemin her zaman daha hızlı olmadığını, doğruluk ve süre arasında tercih yapılabileceğini gördüm.
Testlerde boş maske, geçerli görüntü ve çıktı boyutu gibi temel durumları kontrol ettim. Başarılı testler algoritmanın gerçek fabrika görüntülerindeki başarısını göstermiyor; yalnızca kodun hazırlanan sentetik senaryolarda beklenen biçimde çalıştığını doğruluyordu. Benchmark JSON'u ile paneldeki değerleri karşılaştırarak görsel raporun kaydedilen sonuçlarla uyumlu olduğunu kontrol ettim.
On üçüncü gün sonunda segmentasyon yöntemlerini hız, maske kalitesi ve kullanım kolaylığı açısından kıyaslamayı öğrendim. İleride gerçek görüntü sağlanırsa öncelikle etiketli küçük bir doğrulama seti oluşturulması ve eşiklerin o veri üzerinde yeniden ayarlanması gerektiği sonucuna vardım. Günün sonunda segmentasyon yönteminin seçiminin veri tipine, hız ihtiyacına ve istenen sınır hassasiyetine göre değişebileceğini öğrendim.

Bu aşamada alternatif yöntemleri aynı problem açısından düşünmeye çalıştım. Daha karmaşık bir yöntem kullanmanın otomatik olarak daha doğru sonuç vermediğini; bazı örneklerde basit eşikleme veya temel bir özellik çıkarımının yeterli olabileceğini, bazı görüntülerde ise ışık, arka plan veya desen karmaşıklığı nedeniyle daha gelişmiş yaklaşımlara ihtiyaç duyulabileceğini gördüm. Bu nedenle kullandığım her tekniğin hangi varsayıma dayandığını ve hangi koşulda yetersiz kalabileceğini not ettim. Bir sonraki adıma geçerken yeni yöntemi yalnız daha gelişmiş olduğu için değil, mevcut yöntemde gözlediğim belirli bir sınırlamayı çözmek için seçmeye çalıştım.

Bu aşamada alternatif yöntemleri aynı problem açısından düşünmeye çalıştım. Daha karmaşık bir yöntem kullanmanın otomatik olarak daha doğru sonuç vermediğini; bazı örneklerde basit eşikleme veya temel bir özellik çıkarımının yeterli olabileceğini, bazı görüntülerde ise ışık, arka plan veya desen karmaşıklığı nedeniyle daha gelişmiş yaklaşımlara ihtiyaç duyulabileceğini gördüm. Bu nedenle kullandığım her tekniğin hangi varsayıma dayandığını ve hangi koşulda yetersiz kalabileceğini not ettim. Bir sonraki adıma geçerken yeni yöntemi yalnız daha gelişmiş olduğu için değil, mevcut yöntemde gözlediğim belirli bir sınırlamayı çözmek için seçmeye çalıştım.

**KONTROL SONUCU:**

---

## GÜN 15 — 6 AĞUSTOS 2026
**KISIM:** Görsel Özellik Çıkarımı ve Entegrasyon  
**YAPRAK NO:** 29  
**YAPILAN İŞ:** Geleneksel Görsel Özelliklerin Çıkarılması  
**TARİH:** 06/08/2026

On dördüncü gün görüntüyü doğrudan bütün pikselleriyle kullanmak yerine belirli özelliklerle temsil etmeyi çalıştım. ORB ve SIFT yöntemleriyle dikkat çekici noktaların bulunmasını, GLCM ile doku bilgilerinin ve HSV histogramıyla renk dağılımının çıkarılmasını inceledim. ORB ve SIFT anahtar noktalarını aynı sentetik görüntü üzerinde göstererek iki yöntemin farklı sayıda ve farklı konumlarda nokta seçebildiğini gözlemledim.
Anahtar nokta yöntemlerinde aynı sentetik görsel üzerinde farklı sayıda nokta bulunduğunu gördüm. Noktaların çevresinden çıkarılan tanımlayıcıların, iki görüntüde benzer bölgeleri eşleştirmek için kullanılabildiğini öğrendim. Burada gerçek ürün eşleştirmesi yapmadım; proje görsellerini kullandım. Descriptor çıktılarının doğrudan insan tarafından anlamlandırılması zor olsa da eşleştirme aşamasında görüntünün yerel yapılarını temsil ettiğini uygulamada gördüm.
GLCM tarafında kontrast, homojenlik ve benzeri doku özetlerini hesapladım. Renk histogramında ise görüntüde belirli renk aralıklarının dağılımını çıkardım. Bu özelliklerin her biri görüntünün farklı bir yönünü temsil ettiği için tek başına bütün bilgiyi taşımadığını fark ettim. GLCM hesaplarında dokuya ait kontrast ve homojenlik gibi özet değerlerin, görüntünün yalnızca renk bilgisinden farklı bir özellik sunduğunu öğrendim.
İlk bölüm sonunda ORB, SIFT, doku ve renk özelliklerini ayrı ayrı dosyalarda tutmak yerine ortak bir özellik vektöründe birleştiren kodu inceledim. Bu yaklaşımın sonraki sınıflandırma ve benzerlik çalışmalarında giriş verisi olarak kullanılabileceğini düşündüm. Renk histogramını da ekleyerek tek bir özelliğe bağlı kalmadan farklı bilgi kaynaklarının birlikte kullanılabileceğini denedim.

Yöntemleri karşılaştırırken aynı görüntü üzerinde mümkün olduğunca tek değişkeni değiştirmeye dikkat ettim. Böylece oluşan farkın kullanılan filtre, eşik, renk uzayı veya geometrik dönüşümden mı kaynaklandığını daha açık biçimde takip edebildim. Görüntü üzerinde yalnız gözle iyi görünen sonucu seçmenin yeterli olmadığını; boyut, piksel aralığı, maske alanı, kenar sayısı veya benzeri basit sayısal kontrollerin de sonucu doğrulamada yararlı olabileceğini gördüm. Kullandığım görseller şirketin canlı kalite kontrol sisteminden alınmadığı için elde ettiğim sonuçları üretim doğruluğu olarak değil, yöntemin çalışma mantığını anlamaya yönelik kontrollü örnekler olarak değerlendirdim.

**KONTROL SONUCU:**

---

## GÜN 15 — DEVAM
**KISIM:** Görsel Özellik Çıkarımı ve Entegrasyon  
**YAPRAK NO:** 30  
**YAPILAN İŞ:** Görüntü İşleme Modüllerinin Tek Akışta Birleştirilmesi  
**TARİH:** 06/08/2026

On beşinci gün önceki görüntü işleme çalışmalarını tek tek dosyalarda bırakmak yerine ortak bir araç altında toplamaya çalıştım. Yazılım mühendisinin yönlendirmesiyle kodları doğrudan kopyalamak yerine her işlemin giriş ve çıkışını belirleyip ortak bir `toolkit` sınıfından çağrılabilir hale getirdim. Önceki günlerde ayrı dosyalarda kullandığım işlemleri tek bir sınıf altında çağırırken hangi sırayla uygulanmaları gerektiğini düşünmem gerekti; bu durum basit bir pipeline mantığını anlamamı sağladı.
Bu uygulamada görüntüyü okuma, perspektif düzeltme, renk analizi, bazı morfolojik kontroller ve özellik çıkarma adımları sırayla çalıştırılabiliyordu. Böylece bir modülde yapılan değişikliğin diğer adımları nasıl etkilediğini daha kolay takip edebildim. Araç setine görüntü okuma, perspektif düzeltme, renk ve kusur analizi gibi adımları eklerken her fonksiyonun giriş ve çıkışını birbirine uyumlu tutmaya çalıştım.
Projede kullanılan `perfect_carpet`, `defective_carpet`, `skewed_carpet` ve `faded_carpet` örnekleri sentetikti. Gerçek kalite kontrol kamerasından alınmış görüntüler değildi. Bu nedenle sonuçlara “üretimde kabul/ret başarısı” gibi bir anlam vermedim. Normal ve kusurlu sentetik örnekleri aynı akıştan geçirerek aynı kodun farklı girdilerde nasıl sonuç verdiğini gözlemledim.
Birleştirme sırasında özellikle hata yönetimine dikkat ettim. Görüntü dosyası bulunmadığında veya bir aşama sonuç üretemediğinde bütün programın kontrolsüz biçimde kapanması yerine anlaşılır bir hata mesajı vermesini sağlamaya çalıştım. Buradaki kabul veya ret ifadelerinin gerçek Merinos kalite kararı olmadığını; proje içindeki örnek kurallara göre oluşturulduğunu defterde açık tuttum.

Bu aşamada alternatif yöntemleri aynı problem açısından düşünmeye çalıştım. Daha karmaşık bir yöntem kullanmanın otomatik olarak daha doğru sonuç vermediğini; bazı örneklerde basit eşikleme veya temel bir özellik çıkarımının yeterli olabileceğini, bazı görüntülerde ise ışık, arka plan veya desen karmaşıklığı nedeniyle daha gelişmiş yaklaşımlara ihtiyaç duyulabileceğini gördüm. Bu nedenle kullandığım her tekniğin hangi varsayıma dayandığını ve hangi koşulda yetersiz kalabileceğini not ettim. Bir sonraki adıma geçerken yeni yöntemi yalnız daha gelişmiş olduğu için değil, mevcut yöntemde gözlediğim belirli bir sınırlamayı çözmek için seçmeye çalıştım.

**KONTROL SONUCU:**

---

## GÜN 16 — 7 AĞUSTOS 2026
**KISIM:** İkili Sınıflandırma Temelleri  
**YAPRAK NO:** 31  
**YAPILAN İŞ:** Sentetik kalite özellikleriyle lojistik regresyon modelinin kurulması  
**TARİH:** 07/08/2026

On altıncı gün makine öğrenmesi çalışmalarına geçtim. İlk olarak iki sınıflı bir problem seçerek lojistik regresyonun temel mantığını inceledim. Girdi olarak gerçek makine sensörleri yerine bilgisayarda oluşturulmuş sentetik kalite özellikleri kullandım. Makine öğrenmesine geçmeden önce sentetik veri setindeki özellikleri ve hedef sınıfı ayrı sütunlar halinde inceleyerek modelin hangi bilgiden tahmin yapacağını netleştirdim.
Veri setindeki özelliklerin sayısal dağılımlarını gözden geçirip eğitim ve test olarak iki bölüme ayırdım. Modeli eğitim verisiyle kurup daha sonra görmediği test bölümünde tahmin yaptırdım. Böylece bütün veride eğitim yapıp aynı veride sonuç ölçmenin yanıltıcı olabileceğini öğrendim. Veriyi eğitim ve test bölümlerine ayırmanın, modeli eğittiğim kayıtlarla değerlendirmemek için gerekli olduğunu küçük bir örnek üzerinden gördüm.
Lojistik regresyonda sigmoid fonksiyonunun sayısal çıktıyı 0 ile 1 arasında bir olasılık benzeri değere dönüştürdüğünü, belirli bir eşik üzerinden sınıf kararı verilebildiğini kod üzerinde gördüm. Özellikleri standartlaştırmanın modele etkisini de denedim. Lojistik regresyondaki olasılık çıktısını sınıfa çevirmek için kullanılan eşik değerini değiştirerek precision ve recall arasındaki dengenin nasıl etkilenebildiğini gözlemledim.
Buradaki sınıflar gerçek Merinos kalite etiketlerinden alınmadı. Veri sentetik olduğu için modelin yüksek doğruluk göstermesi gerçek üretimde aynı başarıyı sağlayacağını kanıtlamıyordu. Bu ayrımı günlük notlarımda özellikle belirttim. Sentetik veride yüksek doğruluk elde edilmesinin gerçek üretim koşullarına genellenemeyeceğini özellikle not ettim.

Model karşılaştırmalarında veri hazırlama adımlarını mümkün olduğunca sabit tutmanın önemini fark ettim. Farklı bir train/test bölünmesi, ölçekleme yöntemi veya random seed kullanıldığında sonuçların değişebileceğini gördüğüm için modelleri aynı koşullarda değerlendirmeye çalıştım. Accuracy değerini tek başına yeterli kabul etmedim; sınıf dağılımına göre precision, recall ve F1 gibi ölçülerin farklı bilgiler verebildiğini inceledim. Kullanılan veri sentetik olduğundan yüksek bir skorun gerçek üretim başarısı anlamına gelmeyeceğini özellikle korudum; amaç algoritmanın nasıl davrandığını ve hangi varsayımlarla çalıştığını öğrenmekti.

**KONTROL SONUCU:**

---

## GÜN 16 — DEVAM
**KISIM:** İkili Sınıflandırma Temelleri  
**YAPRAK NO:** 32  
**YAPILAN İŞ:** Train/test ayrımı, confusion matrix ve temel metriklerin incelenmesi  
**TARİH:** 07/08/2026

Günün devamında accuracy, precision, recall ve F1 score kavramlarını çalıştım. Her metriğin farklı bir soruya cevap verdiğini, yalnız accuracy değerine bakmanın özellikle sınıflar dengesiz olduğunda yeterli olmayabileceğini öğrendim. Confusion matrix üzerindeki doğru ve yanlış sınıflandırmaları tek tek okuyarak accuracy değerinin tek başına hatanın hangi sınıfta oluştuğunu göstermediğini öğrendim.
Confusion matrix üzerinde doğru ve yanlış tahminlerin hangi sınıflarda toplandığını inceledim. Bu tablo sayesinde modelin yalnız toplam başarı oranını değil, hata türlerini de görmenin mümkün olduğunu fark ettim. StandardScaler kullanımının farklı ölçeklerdeki özellikleri dengelediğini ve özellikle bazı modellerde ön işlem adımının sonuç üzerinde etkili olabileceğini gördüm.
Testlerde veri hazırlama, model eğitimi ve tahmin fonksiyonlarının beklenen şekillerde çıktı üretmesini kontrol ettim. Ayrıca aynı random seed kullanıldığında deneyi tekrar edebilmenin sonuç karşılaştırmasını kolaylaştırdığını gördüm. Testlerde tahminlerin beklenen sınıf kümesinde kalması ve olasılıkların uygun aralıkta olması gibi temel kontroller yaptım.
On altıncı gün sonunda basit bir sınıflandırma modelinin eğitim, test ve değerlendirme adımlarını baştan sona uygulamış oldum. Gerçek üretim verisine geçilecek olursa sınıfların anlamı, etiket kalitesi ve veri dağılımı yeniden incelenmeden bu sentetik model kullanılamaz. Bu günkü çalışma bana model kurmaktan önce veri bölme, ön işleme ve değerlendirme adımlarının birlikte düşünülmesi gerektiğini gösterdi.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

**KONTROL SONUCU:**

---

## GÜN 17 — 8 AĞUSTOS 2026
**KISIM:** Çok Sınıflı Sınıflandırma  
**YAPRAK NO:** 33  
**YAPILAN İŞ:** Dört sentetik kusur sınıfı için veri hazırlama ve model kurma  
**TARİH:** 08/08/2026

On yedinci gün iki sınıflı örnekten çok sınıflı sınıflandırmaya geçtim. Proje içinde dört farklı kusur türünü temsil eden sentetik bir veri seti oluşturdum. Bu sınıflar gerçek üretim kayıtlarından alınmadı; yalnızca çok sınıflı model yapısını deneyebilmek için kullanıldı. Dört sentetik kusur sınıfının örnek sayılarının dengeli olup olmadığını kontrol ettim; sınıf dağılımındaki dengesizliğin değerlendirme sonucunu etkileyebileceğini öğrendim.
Veri oluşturma kodunda iplik uzunluğu, kopma sayısı, bazı oranlar ve ortamı temsil eden örnek sayısal alanlar bulunuyordu. Bu alanların değerlerini sınıflar arasında belirgin olacak şekilde sentetik ürettim. Bu nedenle veri gerçek hayata göre daha kolay ayrılabilir durumdaydı. Softmax yaklaşımında tek modelin bütün sınıflar için olasılık üretmesini, One-vs-Rest yaklaşımında ise her sınıfın diğerlerinden ayrı ele alınmasını kod üzerinden karşılaştırdım.
Softmax lojistik regresyon ile One-vs-Rest yaklaşımını kurup aralarındaki farkı inceledim. Softmax modelinin sınıfları birlikte ele aldığını, OvR yönteminin ise her sınıf için diğerlerine karşı ayrı bir ikili problem oluşturduğunu öğrendim. Her sınıf için precision, recall ve F1 değerlerini ayrı ayrı inceleyerek toplam doğruluğun sınıf bazlı davranışı gizleyebileceğini gördüm.
Model kodunu incelerken ölçekleme adımının `Pipeline` içinde tutulmasının eğitim ve tahmin sırasında aynı dönüşümün uygulanmasını kolaylaştırdığını gördüm. Bu, veri sızıntısını azaltmak ve kodu daha düzenli tutmak açısından yararlı bir alışkanlık oldu. Bu veri setinin sentetik ve ayrımı kolay hazırlanmış olması nedeniyle yüzde yüz gibi sonuçların gerçek fabrika performansı anlamına gelmediğini açıkça belirttim.

Model karşılaştırmalarında veri hazırlama adımlarını mümkün olduğunca sabit tutmanın önemini fark ettim. Farklı bir train/test bölünmesi, ölçekleme yöntemi veya random seed kullanıldığında sonuçların değişebileceğini gördüğüm için modelleri aynı koşullarda değerlendirmeye çalıştım. Accuracy değerini tek başına yeterli kabul etmedim; sınıf dağılımına göre precision, recall ve F1 gibi ölçülerin farklı bilgiler verebildiğini inceledim. Kullanılan veri sentetik olduğundan yüksek bir skorun gerçek üretim başarısı anlamına gelmeyeceğini özellikle korudum; amaç algoritmanın nasıl davrandığını ve hangi varsayımlarla çalıştığını öğrenmekti.

**KONTROL SONUCU:**

---

## GÜN 17 — DEVAM
**KISIM:** Çok Sınıflı Sınıflandırma  
**YAPRAK NO:** 34  
**YAPILAN İŞ:** Çok sınıflı sonuçların confusion matrix ve sınıf bazlı metriklerle incelenmesi  
**TARİH:** 08/08/2026

Günün devamında confusion matrix, precision, recall, F1 ve ROC benzeri grafiklerin çok sınıflı durumda nasıl gösterildiğini inceledim. Sentetik veri çok ayrık üretildiği için kaydedilmiş örnek sonuçlarda modellerin çok yüksek başarı elde edebildiğini gördüm. ROC eğrilerini incelerken çok sınıflı problemde her sınıfın diğerlerine karşı ayrı değerlendirilebildiğini gördüm.
Bu yüksek sonucu gerçek üretim performansı olarak yorumlamadım. Özellikle savunmada, sentetik veri sınıfları arasında yapay olarak belirgin farklar bulunduğunu ve gerçek kusur kayıtlarında sınıfların bu kadar kolay ayrılmayabileceğini açıklayabilecek şekilde not aldım. Karar matrisi üzerinde hangi sınıfın hangisiyle karıştığını kontrol ederek yalnızca nihai yüzdelere bakmak yerine hata yapısını okumaya çalıştım.
Testlerde veri üretme, model fit etme, olasılık çıktısı oluşturma ve değerlendirme panelini hazırlama fonksiyonlarını kontrol ettim. Güncel görsellerde kullanılan değerleri repo çıktısıyla eşleştirerek yanlış veya eski bir benchmark sonucunu deftere taşımamaya dikkat ettim. Testlerde modelin dört sınıfı da üretebildiğini ve çıktı boyutlarının veri setiyle uyumlu olduğunu kontrol ettim.
On yedinci gün sonunda çok sınıflı bir problemi nasıl kuracağımı ve sonuçları sınıf bazında nasıl yorumlayacağımı öğrendim. Gerçek uygulama için sentetik sınıfların yerine uzmanlar tarafından etiketlenmiş gerçek örneklerin kullanılması gerektiği açıktı. Günün sonunda çok sınıflı sınıflandırmada değerlendirme raporunun tek bir accuracy sayısından daha fazla bilgi sunduğunu öğrenmiş oldum.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

**KONTROL SONUCU:**

---

## GÜN 18 — 10 AĞUSTOS 2026
**KISIM:** Decision Tree ve Random Forest  
**YAPRAK NO:** 35  
**YAPILAN İŞ:** Sentetik veri üzerinde karar ağacı ve topluluk modelinin kurulması  
**TARİH:** 10/08/2026

On sekizinci gün karar ağaçları ve Random Forest yöntemlerini çalıştım. Önceki günlerde kullandığım sentetik sınıflandırma verisine benzer bir veri seti üzerinde tek bir karar ağacının nasıl bölünmeler yaptığını inceledim. Ağacın her düğümde bir özelliğe göre veriyi iki gruba ayırdığını gördüm. Karar ağacını incelerken her düğümde bir özelliğe göre bölme yapıldığını ve ağaç derinliği arttıkça modelin daha karmaşık kararlar verebildiğini gözlemledim.
Ağaç derinliği arttıkça eğitim verisine daha iyi uyum sağlarken test verisinde aşırı öğrenme riski oluşabildiğini küçük örneklerle gözlemledim. Bu nedenle `max_depth` ve minimum yaprak örneği gibi parametrelerin model davranışını etkilediğini öğrendim. Çok derin bir ağacın eğitim verisini ezberleyebileceğini küçük deneylerde görerek overfitting kavramını önceki modellerden farklı bir biçimde tekrar ettim.
Daha sonra birden fazla ağacın farklı örnekler ve özelliklerle eğitildiği Random Forest yaklaşımını inceledim. Tek ağacın kararına bağlı kalmak yerine birçok ağacın sonucunu birleştirmenin daha dengeli sonuç verebildiğini sentetik veri üzerinde gördüm. Random Forest'ta birden fazla ağacın farklı örnek ve özelliklerle eğitilip sonuçlarının birleştirilmesinin tek ağaca göre daha dengeli davranabileceğini gördüm.
Bu çalışmalar gerçek tezgâh sensörlerinden veya arıza kayıtlarından yapılmadı. Repo içindeki değişken adları endüstriyel senaryoya benzetilmiş olsa da sayıların tamamı proje için oluşturulmuştu. Bu nedenle model sonucunu saha tahmini gibi anlatmadım. Bütün sonuçların sentetik veri üzerinde elde edildiğini, gerçek arıza veya kalite kayıtlarından türetilmediğini not ettim.

Model karşılaştırmalarında veri hazırlama adımlarını mümkün olduğunca sabit tutmanın önemini fark ettim. Farklı bir train/test bölünmesi, ölçekleme yöntemi veya random seed kullanıldığında sonuçların değişebileceğini gördüğüm için modelleri aynı koşullarda değerlendirmeye çalıştım. Accuracy değerini tek başına yeterli kabul etmedim; sınıf dağılımına göre precision, recall ve F1 gibi ölçülerin farklı bilgiler verebildiğini inceledim. Kullanılan veri sentetik olduğundan yüksek bir skorun gerçek üretim başarısı anlamına gelmeyeceğini özellikle korudum; amaç algoritmanın nasıl davrandığını ve hangi varsayımlarla çalıştığını öğrenmekti.

**KONTROL SONUCU:**

---

## GÜN 18 — DEVAM
**KISIM:** Decision Tree ve Random Forest  
**YAPRAK NO:** 36  
**YAPILAN İŞ:** Özellik önemleri ve model sonuçlarının karşılaştırılması  
**TARİH:** 10/08/2026

Günün devamında özellik önemlerini inceleyerek modelin hangi girişleri daha fazla kullandığını gözlemledim. Özellik öneminin nedensellik göstermediğini; modelin yalnızca kendi karar yapısı içinde bu alanlardan daha fazla yararlandığını not ettim. Özellik önemlerini grafikte sıralayarak modelin hangi sentetik değişkenleri daha fazla kullandığını inceledim; bu değerleri nedensellik olarak yorumlamamaya dikkat ettim.
Tek ağaç ile Random Forest’ın doğruluk ve F1 sonuçlarını karşılaştırdım. Sentetik veri üzerinde küçük farklar görüldü. Ancak veri yapay üretildiği için model sıralaması gerçek üretim probleminde aynı olmak zorunda değildi. Ağaç sayısını ve derinliği değiştirip sonucu tekrar çalıştırarak model ayarlarının performans ve çalışma süresi üzerindeki etkisini gözlemledim.
Testlerde modelin fit edilmesi, tahmin çıktısının beklenen sınıf etiketlerinden oluşması ve özellik önemlerinin doğru uzunlukta dönmesi gibi temel kontroller yaptım. Böylece algoritmanın kullanım biçimini daha sistematik hale getirdim. Testlerde aynı random state ile tekrar çalıştırmanın aynı sonucu üretmesi, deneylerin tekrarlanabilirliği açısından neden yararlı olduğunu anlamamı sağladı.
On sekizinci gün sonunda ağaç tabanlı modellerin hem sınıflandırma hem de belirli ölçüde yorumlanabilirlik açısından kullanışlı olabileceğini öğrendim. Gerçek bakım veya kalite tahmini için önce güvenilir, etiketli ve yeterli miktarda gerçek veri gerekir. Bu gün karar ağaçlarının yorumlanabilir tarafını ve topluluk yöntemlerinin tek modelin hatalarını azaltmak için nasıl kullanılabildiğini öğrenmiş oldum.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

**KONTROL SONUCU:**

---

## GÜN 19 — 11 AĞUSTOS 2026
**KISIM:** Gradient Boosting Modelleri  
**YAPRAK NO:** 37  
**YAPILAN İŞ:** XGBoost ve LightGBM yaklaşımının sentetik sınıflandırma verisinde denenmesi  
**TARİH:** 11/08/2026

On dokuzuncu gün ağaç tabanlı modellerin başka bir ailesi olan gradient boosting yöntemlerini inceledim. Random Forest’tan farklı olarak ağaçların birbirinden bağımsız kurulması yerine önceki modelin hatalarını azaltmaya çalışacak şekilde sıralı olarak eklenmesi fikrini öğrendim. Boosting yöntemlerinin ağaçları birbirinden bağımsız kurmak yerine önceki hatalara odaklanarak sırayla geliştirdiğini kod ve grafik üzerinden inceledim.
XGBoost ve LightGBM kütüphanelerini aynı sentetik veri üzerinde denedim. Eğitim sırasında ağaç sayısı, öğrenme oranı ve derinlik gibi ayarların modele etkisini gözlemledim. Çok fazla ağaç veya gereğinden büyük derinlik seçmenin her zaman daha iyi sonuç vermediğini gördüm. XGBoost ve LightGBM için benzer veri hazırlama adımları kullanılsa da kütüphanelerin parametre isimleri ve eğitim yapısının farklı olduğunu gördüm.
Veri yine gerçek fabrika kayıtlarından gelmiyordu. Bu nedenle kod içinde “industrial defect” gibi isimler geçse de çalışmayı gerçek kusur sınıflandırması olarak değerlendirmedim. Sentetik veri, yalnızca algoritmalar arasındaki kullanım farklarını güvenli biçimde denememe yaradı. Öğrenme oranı ve ağaç sayısı gibi ayarları değiştirince sonucun değişebildiğini gözlemleyerek hiperparametre kavramını daha somut biçimde anlamaya başladım.
Model eğitimlerini aynı train/test ayrımı üzerinde yaparak sonuçların karşılaştırılabilir olmasını sağladım. Farklı random seed veya farklı veri bölünmesi kullanıldığında puanların değişebileceğini de not ettim. Sentetik kusur verisi üzerinde iyi sonuç çıkmasının, gerçek üretim koşullarında aynı performansın garanti edildiği anlamına gelmediğini korudum.

Model karşılaştırmalarında veri hazırlama adımlarını mümkün olduğunca sabit tutmanın önemini fark ettim. Farklı bir train/test bölünmesi, ölçekleme yöntemi veya random seed kullanıldığında sonuçların değişebileceğini gördüğüm için modelleri aynı koşullarda değerlendirmeye çalıştım. Accuracy değerini tek başına yeterli kabul etmedim; sınıf dağılımına göre precision, recall ve F1 gibi ölçülerin farklı bilgiler verebildiğini inceledim. Kullanılan veri sentetik olduğundan yüksek bir skorun gerçek üretim başarısı anlamına gelmeyeceğini özellikle korudum; amaç algoritmanın nasıl davrandığını ve hangi varsayımlarla çalıştığını öğrenmekti.

**KONTROL SONUCU:**

---

## GÜN 19 — DEVAM
**KISIM:** Gradient Boosting Modelleri  
**YAPRAK NO:** 38  
**YAPILAN İŞ:** Model performansı ve özellik etkilerinin örnek veri üzerinde incelenmesi  
**TARİH:** 11/08/2026

Günün devamında modellerin sınıf tahminleri ile olasılık çıktısını inceledim. Yanlış tahmin edilen örneklerin özelliklerini kontrol ederek modelin hangi bölgelerde zorlandığını anlamaya çalıştım. Bu, yalnız tek bir başarı oranına bakmaktan daha öğretici oldu. Model karşılaştırmasında yalnızca doğruluk değil eğitim süresi ve sınıf bazlı F1 değerlerine de bakarak tek bir metriğe bağlı kalmamaya çalıştım.
Özellik önemlerini ağaç modelleri arasında karşılaştırdım. Aynı sentetik veride iki modelin önem sıralaması benzer görünse de bunun gerçek süreçte aynı anlamı taşımayacağını öğrendim. Gerçek veride alanların ölçüm hatası ve korelasyonu ayrıca incelenmelidir. Feature importance çıktılarını önceki Random Forest günüyle karşılaştırarak farklı model ailelerinin aynı özelliğe farklı önem verebildiğini gördüm.
Testlerde model nesnesinin oluşturulması, fit/tahmin akışı ve değerlendirme çıktıları kontrol edildi. Kullanılan kütüphanelerin sürümlerini de repo bağımlılıklarında kayıt altında tutarak çalışmanın tekrar edilebilir olmasına dikkat ettim. Testlerde eğitim fonksiyonlarının beklenen model nesnesini ve tahmin boyutlarını üretmesini kontrol ettim.
On dokuzuncu gün sonunda boosting modellerinin güçlü araçlar olduğunu ancak yüksek benchmark puanının tek başına üretim kullanımını haklı çıkarmadığını öğrendim. Veri kalitesi, açıklanabilirlik ve gerçek saha doğrulaması olmadan model yalnızca bir PoC olarak kalmalıdır. Bu çalışma sayesinde boosting yöntemlerinin temel fikrini öğrendim ancak hangi modelin gerçek üretim için uygun olduğunu söyleyebilmek için gerçek etiketli veriye ihtiyaç olduğunu not ettim.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

**KONTROL SONUCU:**

---

## GÜN 20 — 12 AĞUSTOS 2026
**KISIM:** Support Vector Machine  
**YAPRAK NO:** 39  
**YAPILAN İŞ:** Sentetik sınıflandırma verisinde SVM ve kernel seçeneklerinin denenmesi  
**TARİH:** 12/08/2026

Yirminci gün Support Vector Machine yöntemini çalıştım. İlk olarak iki sınıf arasına mümkün olduğunca geniş bir ayırıcı sınır yerleştirme fikrini basit iki boyutlu örneklerde anlamaya çalıştım. Daha sonra aynı yaklaşımı daha fazla özellik içeren sentetik veri üzerinde kullandım. SVM'nin sınıfları ayıran bir karar sınırı oluşturduğunu ve mümkün olduğunca geniş bir marjin bırakmaya çalıştığını iki boyutlu sentetik örnekler üzerinden inceledim.
SVM’nin özellik ölçeklerine duyarlı olabildiğini gördüğüm için StandardScaler kullandım. Ölçekleme yapılmadan ve yapıldıktan sonra sonuçları karşılaştırarak bazı sayısal alanların yalnız büyük değer aralığı nedeniyle modeli etkilemesini azaltmanın önemini öğrendim. Özellikleri ölçeklemeden ve ölçekledikten sonra sonucu karşılaştırarak SVM'nin veri ölçeğine duyarlı olabileceğini uygulamada gördüm.
Linear, RBF gibi kernel seçeneklerinin veriyi farklı biçimde ayırabildiğini inceledim. Kernel seçiminin veri yapısına göre yapılması gerektiğini; en karmaşık yöntemin otomatik olarak en doğru sonuç vermediğini gözlemledim. Linear ve RBF kernel seçeneklerini deneyerek doğrusal ayrılmayan örneklerde kernel yaklaşımının karar sınırını değiştirebildiğini gözlemledim.
Bu gün kullanılan örnekler de sentetikti. Gerçek hata logu, tezgâh telemetrisi veya şirket kalite etiketi kullanılmadı. Bu nedenle SVM’nin Merinos’taki bir üretim problemini çözdüğü gibi bir iddiada bulunmadım. Buradaki sınıfların proje için üretilmiş olduğunu ve gerçek kusur ölçümlerine dayanmaması nedeniyle sonucu yalnızca eğitim deneyi olarak değerlendirdim.

Model karşılaştırmalarında veri hazırlama adımlarını mümkün olduğunca sabit tutmanın önemini fark ettim. Farklı bir train/test bölünmesi, ölçekleme yöntemi veya random seed kullanıldığında sonuçların değişebileceğini gördüğüm için modelleri aynı koşullarda değerlendirmeye çalıştım. Accuracy değerini tek başına yeterli kabul etmedim; sınıf dağılımına göre precision, recall ve F1 gibi ölçülerin farklı bilgiler verebildiğini inceledim. Kullanılan veri sentetik olduğundan yüksek bir skorun gerçek üretim başarısı anlamına gelmeyeceğini özellikle korudum; amaç algoritmanın nasıl davrandığını ve hangi varsayımlarla çalıştığını öğrenmekti.

**KONTROL SONUCU:**

---

## GÜN 20 — DEVAM
**KISIM:** Support Vector Machine  
**YAPRAK NO:** 40  
**YAPILAN İŞ:** Ölçekleme, sınıf ayrımı ve temel değerlendirme metriklerinin karşılaştırılması  
**TARİH:** 12/08/2026

Günün devamında modelin tahminlerini confusion matrix ve F1 gibi metriklerle değerlendirdim. Özellikle yanlış sınıflandırılan örnekleri ayrı inceleyerek sınıf sınırlarına yakın kayıtların daha zor olabildiğini gördüm. C ve gamma gibi parametrelerin değişmesiyle modelin daha sıkı veya daha esnek karar sınırları oluşturabildiğini küçük denemelerle gördüm.
C ve gamma parametrelerinin sonuç üzerindeki etkisini küçük bir aralıkta denedim. Bu deneme bana hiperparametre aramasının çok sayıda kombinasyonu körü körüne denemekten ziyade kontrollü ve doğrulama verisiyle yapılması gerektiğini düşündürdü. Confusion matrix ve sınıf bazlı metrikleri önceki günlerin sonuçlarıyla aynı formatta tutarak yöntemleri daha kolay karşılaştırabildim.
Testlerde ölçekleyici ve modelin aynı pipeline içinde çalışması, tahmin sayısının giriş örnek sayısıyla eşleşmesi ve hatalı veri biçiminde anlaşılır hata alınması gibi noktaları kontrol ettim. Testlerde modelin eğitimden sonra tahmin üretebilmesi ve sınıf etiketlerinin beklenen kümede kalması gibi temel kontroller yaptım.
Yirminci gün sonunda SVM’yi temel mantığı ve kullanım adımlarıyla öğrenmiş oldum. Gerçek üretim probleminde algoritma seçiminin sentetik benchmark puanına göre değil, gerçek verideki doğrulama sonuçlarına ve operasyonel gereksinimlere göre yapılması gerektiğini not ettim. Bu günün sonunda tek bir algoritmayı ezberlemek yerine, veri ölçeği, kernel seçimi ve parametre ayarlarının birlikte değerlendirilmesi gerektiğini anladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

**KONTROL SONUCU:**

---

## GÜN 21 — 13 AĞUSTOS 2026
**KISIM:** Gözetimsiz Öğrenme ve Boyut İndirgeme  
**YAPRAK NO:** 41  
**YAPILAN İŞ:** PCA, t-SNE, K-Means ve DBSCAN yöntemlerinin sentetik veride uygulanması  
**TARİH:** 13/08/2026

Yirmi birinci gün etiketli sınıflandırma yerine verinin kendi içindeki grupları araştıran gözetimsiz yöntemlere geçtim. PCA, t-SNE, K-Means ve DBSCAN araçlarını aynı sentetik veri seti üzerinde kullanarak her birinin farklı bir amaç taşıdığını anlamaya çalıştım. PCA uygulamadan önce sentetik özellikleri ölçekledim ve çok boyutlu verinin daha az bileşenle ne kadar temsil edilebildiğini açıklanan varyans oranı üzerinden inceledim.
PCA ile çok sayıda özelliği daha az boyutta temsil etmeyi denedim. İlk iki bileşenin toplam varyansın ne kadarını taşıdığını inceledim. Bu yöntemin görselleştirmeyi kolaylaştırdığını fakat bütün bilgiyi korumadığını gördüm. İlk iki bileşeni grafikte göstererek benzer kayıtların birbirine yakınlaşıp yakınlaşmadığını gözlemledim; bu grafiği doğrudan sınıflandırma sonucu olarak yorumlamadım.
t-SNE ile de kayıtları iki boyutta göstermeyi denedim. Görselde oluşan kümelerin gerçek üretim sınıfları olarak yorumlanmaması gerektiğini öğrendim; t-SNE özellikle görselleştirme amaçlıydı ve parametre değişiklikleri görünümü etkileyebiliyordu. t-SNE çıktısının farklı random state veya ayarlarda değişebildiğini görerek görselleştirme yöntemlerinde tekrar üretilebilirlik konusuna dikkat ettim.
Veri gerçek üretim kayıtlarından oluşmadığı için küme sonuçlarına operasyonel bir anlam yüklemedim. Sentetik örnekler yalnızca etiket olmadan benzer kayıtların nasıl gruplanabileceğini ve aykırı noktaların nasıl görülebileceğini anlamama yardımcı oldu. Gerçek üretim verisi bulunmadığı için ortaya çıkan kümeleri gerçek arıza grupları veya ürün aileleri olarak adlandırmadım.

Model karşılaştırmalarında veri hazırlama adımlarını mümkün olduğunca sabit tutmanın önemini fark ettim. Farklı bir train/test bölünmesi, ölçekleme yöntemi veya random seed kullanıldığında sonuçların değişebileceğini gördüğüm için modelleri aynı koşullarda değerlendirmeye çalıştım. Accuracy değerini tek başına yeterli kabul etmedim; sınıf dağılımına göre precision, recall ve F1 gibi ölçülerin farklı bilgiler verebildiğini inceledim. Kullanılan veri sentetik olduğundan yüksek bir skorun gerçek üretim başarısı anlamına gelmeyeceğini özellikle korudum; amaç algoritmanın nasıl davrandığını ve hangi varsayımlarla çalıştığını öğrenmekti.

**KONTROL SONUCU:**

---

## GÜN 21 — DEVAM
**KISIM:** Gözetimsiz Öğrenme ve Boyut İndirgeme  
**YAPRAK NO:** 42  
**YAPILAN İŞ:** Etiketsiz sentetik kayıtların iki boyutta incelenmesi ve kümelerin karşılaştırılması  
**TARİH:** 13/08/2026

Günün devamında K-Means ile önceden belirlenen sayıda küme oluşturup DBSCAN ile yoğunluğa dayalı kümeleri karşılaştırdım. DBSCAN’in bazı noktaları gürültü olarak bırakabildiğini ve küme sayısını önceden istemediğini gördüm. K-Means ile belirli sayıda küme tanımlarken DBSCAN'in yoğunluğa göre küme oluşturup bazı noktaları gürültü olarak bırakabildiğini karşılaştırdım.
Küme merkezlerini ve gruplara düşen örnek sayılarını inceledim. Sentetik veride sınıflar belirgin üretildiği için kümeler anlaşılır görünüyordu. Gerçek veride ise özellik seçimi, ölçekleme ve gürültü miktarının sonucu daha fazla etkileyebileceğini not ettim. Küme etiketlerini iki boyutlu projeksiyon üzerinde renklendirerek algoritmanın hangi noktaları birlikte değerlendirdiğini görsel olarak kontrol ettim.
Görselleştirme panelinde PCA/t-SNE dağılımları ile küme etiketlerini yan yana koydum. Böylece bir algoritmanın oluşturduğu kümeyi yalnız sayısal etiket olarak değil, veri dağılımı üzerinde de inceleyebildim. Silhouette gibi basit ölçümlerin kümelerin ayrışması hakkında fikir verebildiğini ancak tek başına gerçek iş anlamı sağlamadığını öğrendim.
Yirmi birinci gün sonunda etiketsiz veride örüntü aramanın mümkün olduğunu öğrendim. Ancak kümeye bir “arıza” veya “kalite sınıfı” anlamı vermek için mutlaka alan bilgisi ve gerçek kayıtların uzman tarafından yorumlanması gerekir. Faz sonunda gözetimli ve gözetimsiz öğrenmenin farklı sorulara cevap verdiğini, etiketin bulunup bulunmamasının yöntem seçimini doğrudan etkilediğini gördüm.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

Ayrıca eğitim verisi ile değerlendirme verisinin birbirine karışmasının yanıltıcı sonuç üretebileceğini öğrendim. Modelin daha önce gördüğü örnekler üzerinde başarılı olması, yeni veriye genelleyebildiğini göstermiyordu. Bu nedenle veri sızıntısı, aşırı öğrenme ve sınıf dengesizliği gibi kavramları sonuçları yorumlarken göz önünde bulundurdum. Bir modelin karmaşıklığını artırmadan önce basit modelin nerede hata yaptığını incelemenin daha anlamlı olduğunu gördüm. Böylece model seçimini yalnız puana göre değil, açıklanabilirlik, hesaplama maliyeti ve veri gereksinimi gibi mühendislik ölçütleriyle birlikte değerlendirmeye başladım.

**KONTROL SONUCU:**

---

## GÜN 22 — 14 AĞUSTOS 2026
**KISIM:** Metinlerin Sayısal Temsili ve BM25  
**YAPRAK NO:** 43  
**YAPILAN İŞ:** Örnek teknik metinlerde TF-IDF ve BM25 tabanlı aramanın kurulması  
**TARİH:** 14/08/2026

Yirmi ikinci gün görüntü ve sayısal veriden metin tarafına geçtim. Yazılım mühendisi, kurumlarda teknik doküman sayısı arttığında doğru bilgiye erişmenin de ayrı bir yazılım problemi olduğunu anlattı. Bu nedenle ilk olarak kelime tabanlı arama yöntemlerini çalıştım. Metin aramaya başlamadan önce örnek dokümanları küçük parçalara ayırıp Türkçe karakterleri koruyan basit bir tokenizasyon işlemi uyguladım.
Gerçek bakım kılavuzları veya kurum içi PDF’ler bana verilmedi. Proje için kısa teknik açıklamalar ve örnek sorular hazırladım. Bu metinleri tokenlara ayırıp Türkçe karakterleri koruyarak basit bir ön işleme uyguladım. TF-IDF ağırlıklarında her kelimenin yalnızca tekrar sayısına değil, bütün dokümanlarda ne kadar yaygın olduğuna da bağlı olduğunu küçük örneklerle gördüm.
TF-IDF ile kelimelerin dokümandaki önemini sayısal olarak temsil etmeyi, BM25 ile de sorgudaki kelimelerle dokümanları puanlamayı inceledim. Belirli bir hata kodu veya çok özgül bir teknik terim geçtiğinde kelime tabanlı aramanın anlaşılır sonuçlar verdiğini gördüm. BM25 sonuçlarını aynı sorguda TF-IDF ile karşılaştırarak doküman uzunluğu ve kelime sıklığı düzeltmelerinin sıralamayı değiştirebildiğini gözlemledim.
Bu çalışma herhangi bir Merinos bakım arşivini indekslemedi. Doküman içerikleri sentetik olduğu için arama başarısını da yalnız proje veri seti kapsamında değerlendirdim. Gerçek sistemde doküman erişim izinleri ve güncellik bilgisi ayrıca ele alınmalıdır. Kullandığım teknik metinlerin kurum içi bakım kılavuzları değil, proje için hazırlanmış örnek içerikler olduğunu her aşamada korudum.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 22 — DEVAM
**KISIM:** Metinlerin Sayısal Temsili ve BM25  
**YAPRAK NO:** 44  
**YAPILAN İŞ:** Sentetik soru ve dokümanlar üzerinde lexical retrieval sonuçlarının incelenmesi  
**TARİH:** 14/08/2026

Günün devamında farklı soru biçimlerini BM25 ile arattım. Aynı kelimeleri içeren sorularda doğru örnek dokümanın üst sıralara gelmesi kolayken, aynı anlamın farklı kelimelerle yazıldığı sorularda sonucun değişebildiğini gördüm. Özellikle arıza kodu gibi birebir geçen teknik terimlerde kelime tabanlı yöntemin neden güçlü olabileceğini sonuç listelerinden fark ettim.
Sonuç listesindeki ilk birkaç dokümanı puanlarıyla birlikte gösterdim. Bir dokümanın yüksek BM25 puanı almasının, içerdiği cevabın mutlaka doğru olduğu anlamına gelmediğini; bunun yalnızca kelime eşleşmesi temelli bir sıralama olduğunu öğrendim. Türkçe karakterli ve karaktersiz iki benzer sorguyu deneyerek metin normalizasyonunun arama sonucuna etkisini inceledim.
Testlerde tokenizasyon, indeks oluşturma ve sorgu fonksiyonlarının çıktısını kontrol ettim. Özellikle aynı hata kodunun geçtiği örneklerde sıralamanın beklediğim yönde olup olmadığını gözlemledim. Testlerde boş sorgu, bilinmeyen kelime ve aynı kelimenin tekrar edilmesi gibi durumlarda skorların beklenmedik hata üretmediğini kontrol ettim.
Yirmi ikinci gün sonunda lexical retrieval yaklaşımının basit ve açıklanabilir bir başlangıç olduğunu gördüm. Bir sonraki gün, aynı kelimeyi kullanmadan benzer anlam taşıyan soruları bulabilmek için vektör tabanlı metin aramasını incelemeye geçtim. Bu gün kelime tabanlı aramanın anlaşılır ve hızlı bir temel yöntem olduğunu, fakat aynı anlamın farklı kelimelerle ifade edildiği sorularda sınırlı kalabileceğini öğrendim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

**KONTROL SONUCU:**

---

## GÜN 23 — 15 AĞUSTOS 2026
**KISIM:** Vektör Tabanlı Metin Arama  
**YAPRAK NO:** 45  
**YAPILAN İŞ:** Bi-Encoder benzeri temsil ve cosine similarity ile sentetik doküman araması  
**TARİH:** 15/08/2026

Yirmi üçüncü gün metinleri yalnız kelime eşleşmesiyle değil, sayısal vektörler üzerinden karşılaştırmayı çalıştım. Önceki gün BM25’in aynı kelimeler bulunmadığında zorlanabileceğini görmüştüm. Bu kez soru ve dokümanları benzer boyutta vektörlerle temsil eden bir dense retrieval yapısını inceledim. Yoğun aramada metnin doğrudan kelime sayımı yerine sabit uzunlukta sayısal bir vektörle temsil edilmesi fikrini önce küçük örneklerle anlamaya çalıştım.
Projede hazır model kullanılabildiğinde cümle embedding yaklaşımına benzeyen bir akış vardı; modelin yüklenemediği durumlar için ise alternatif puanlama yöntemleri bulunuyordu. Bu nedenle kayıtlı çıktıyı belirli bir büyük modelin kesin sonucu gibi yorumlamadım. Soru ve doküman vektörleri arasında kosinüs benzerliği hesaplayarak ortak kelime az olsa bile anlamsal olarak yakın sonuçların üst sıralara gelebileceğini gözlemledim.
Soru vektörüyle doküman vektörleri arasında cosine similarity hesaplayıp en yakın sonuçları sıraladım. Aynı anlamı farklı kelimelerle yazan sentetik sorularda, kelime tabanlı aramaya göre farklı sonuçlar elde edilebildiğini gördüm. Kodda hazır model yüklenemediğinde devreye giren alternatif temsil yolunu ayrıca inceledim; bu nedenle kayıtlı raporu belirli bir modelin kesin çalışma kanıtı olarak görmedim.
Kullandığım doküman ve sorular yine örnek içeriklerdi. Gerçek kurum dokümanlarının embeddinglerini üretmedim. Çalışmanın amacı yalnızca yoğun arama yaklaşımının temel veri akışını anlamaktı. Gerçek kurum dokümanı olmaması nedeniyle bütün sonuçları eğitim amaçlı örnek retrieval çıktıları olarak değerlendirdim.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 23 — DEVAM
**KISIM:** Vektör Tabanlı Metin Arama  
**YAPRAK NO:** 46  
**YAPILAN İŞ:** Örnek soruların vektör benzerliği ve alternatif puanlama yollarıyla değerlendirilmesi  
**TARİH:** 15/08/2026

Günün devamında ilk aşamada bulunan birkaç dokümanı tekrar puanlama fikrini inceledim. Sorgu ve doküman çiftini birlikte değerlendiren basit bir reranking adımının, sonuç sırasını değiştirebileceğini gördüm. Bi-Encoder yaklaşımında doküman vektörlerinin önceden hesaplanabilmesinin arama açısından neden avantaj sağlayabileceğini kod yapısından anladım.
Hazır modellerin her ortamda indirilemeyebileceği veya çalışmayabileceği için kodun fallback davranışını da kontrol ettim. Bu özellik, bir rapordaki yüksek puanın arka planda hangi yöntemin gerçekten çalıştığını tek başına göstermediğini anlamam açısından önemliydi. Cross-Encoder fikrini ise sorgu ve aday metni birlikte değerlendirerek daha ayrıntılı puanlama yapan ikinci bir adım olarak kavramsal düzeyde inceledim.
Notebook içindeki sonuçları incelerken kullanılan yöntemi ve veri setini not ettim. Model adı veya performans sayısını bağlamdan koparıp “fabrikada şu doğruluğu aldım” şeklinde ifade etmemeye dikkat ettim. Top-K sonuçlarında benzer puanlı kayıtların yer değiştirebildiğini görerek küçük skor farklarını kesin doğruluk farkı olarak yorumlamamaya dikkat ettim.
Yirmi üçüncü gün sonunda kelime tabanlı ve vektör tabanlı aramanın farklı güçlü yönleri olduğunu öğrendim. Sonraki gün bu iki yöntemin sonuçlarını tek listede birleştiren hibrit arama yaklaşımını çalıştım. Bu gün sparse ve dense aramanın farklı güçlü yönleri olduğunu gördüğüm için bir sonraki gün bunları birlikte kullanma fikrine geçiş yaptım.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

**KONTROL SONUCU:**

---

## GÜN 24 — 17 AĞUSTOS 2026
**KISIM:** Hibrit Retrieval ve RRF  
**YAPRAK NO:** 47  
**YAPILAN İŞ:** BM25 ve vektör tabanlı arama sonuçlarının birlikte kullanılması  
**TARİH:** 17/08/2026

Yirmi dördüncü gün BM25 ve vektör tabanlı aramanın sonuçlarını tek bir arama sistemi içinde birleştirmeyi çalıştım. Bir yöntem belirli teknik kodlarda daha iyi sonuç verirken diğerinin farklı ifadelerle sorulan sorularda yararlı olabileceğini önceki günlerde görmüştüm. Hibrit aramada önce BM25 ve dense sonuçlarının kendi sıralarını ayrı ayrı sakladım; böylece birleşimden sonra hangi sonucun hangi yöntemden geldiğini takip edebildim.
İlk olarak aynı sorguyu iki ayrı arama yöntemine gönderip iki sonuç listesi aldım. Sonuçların puan ölçekleri birbirinden farklı olduğu için doğrudan toplamak yerine sıralama konumlarını kullanan Reciprocal Rank Fusion yaklaşımını inceledim. RRF hesabında ham skorları aynı ölçeğe çevirmek yerine sonuçların sıralarının kullanıldığını küçük bir tablo üzerinden adım adım kontrol ettim.
RRF’de bir doküman iki listede de üst sıralardaysa ortak sıralamada güçlenebiliyordu. Parametre olarak kullanılan `k` değerinin etkisini küçük örneklerde gözlemledim. Bu yöntem, modelleri yeniden eğitmeden sonuç listelerini birleştirmeyi mümkün kılıyordu. Bir dokümanın iki listede de üst sıralarda bulunmasının birleşik puanını artırdığını gözlemleyerek yöntemin temel mantığını uygulamada gördüm.
Bütün sorgu ve dokümanlar sentetikti. Gerçek teknik kılavuz veya kullanıcı araması kullanılmadığı için Precision@1 gibi ölçümler yalnızca bu hazırlanmış benchmark’ın sonucuydu. Benchmark soruları sentetik olduğu için elde edilen Precision@1 değerlerini gerçek operatör arama başarısı olarak sunmadım.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 24 — DEVAM
**KISIM:** Hibrit Retrieval ve RRF  
**YAPRAK NO:** 48  
**YAPILAN İŞ:** Sentetik benchmark üzerinde iki arama listesinin sıralama füzyonuyla karşılaştırılması  
**TARİH:** 17/08/2026

Günün devamında hibrit aramadan sonra ek bir yeniden sıralama adımını denedim. İlk birkaç adayın daha ayrıntılı puanlanmasıyla sonuç sırası değişebiliyordu. Böylece hızlı bir ilk arama ile daha ayrıntılı ikinci aşamanın birlikte kullanılabileceğini gördüm. Farklı k değerleri veya Top-K uzunluklarıyla sıralamanın nasıl değişebildiğini deneyerek RRF'nin de parametre seçiminden bağımsız olmadığını gördüm.
Repo README’si ile güncel JSON/PNG çıktıları arasında bazı eski ve yeni benchmark değerlerinin farklı olduğunu fark ettim. Defter görsellerinde güncel dosya çıktısını esas alarak ölçüm kaynağını karıştırmamaya çalıştım. README ile güncel JSON raporu arasında farklı değerler bulunduğunda görsel çıktıyı ve kayıtlı raporu esas alarak dokümantasyonun güncel tutulmasının önemini fark ettim.
Testlerde BM25, dense sonuçları ve RRF listesinin beklenen veri yapısında oluşması kontrol edildi. Arama kalitesinin gerçek hayatta ölçülebilmesi için gerçek kullanıcı soruları ve doğru cevap dokümanlarıyla hazırlanmış bir değerlendirme seti gerektiğini not ettim. Testlerde aynı dokümanın iki listeden geldiğinde tek sonuç olarak birleşmesi gibi durumları kontrol ettim.
Yirmi dördüncü gün sonunda hibrit aramanın farklı arama yaklaşımlarını ortak bir listede kullanma fikrini öğrendim. Bu yapı ileride gerçek kurum dokümanlarıyla denenebilir; ancak önce doküman erişimi, etiketli sorular ve başarı kriterleri kurum tarafından belirlenmelidir. Günün sonunda hibrit aramanın iki yöntemin sonuçlarını bir araya getirebildiğini, ancak gerçek faydanın gerçek soru ve dokümanlarla ayrıca ölçülmesi gerektiğini not ettim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

**KONTROL SONUCU:**

---

## GÜN 25 — 18 AĞUSTOS 2026
**KISIM:** Doküman Chunking Yöntemleri  
**YAPRAK NO:** 49  
**YAPILAN İŞ:** Sabit, recursive, semantic ve Markdown tabanlı chunking yöntemlerinin incelenmesi  
**TARİH:** 18/08/2026

Yirmi beşinci gün uzun metinlerin arama sisteminde doğrudan tek parça halinde tutulmasının sorunlarını çalıştım. Çok uzun bir doküman içinde doğru bölüm bulunsa bile arama sonucunun gereksiz fazla metin getirebileceğini gördüm. Bu nedenle metni daha küçük parçalara ayıran chunking yöntemlerini inceledim. Uzun metni sabit karakter sayısına göre böldüğümde bazı cümlelerin ortadan ayrılabildiğini görerek yalnızca boyuta dayalı parçalamanın sınırlamasını fark ettim.
Fixed-size yönteminde metni belirli karakter sayısına göre ayırdım ve parçalar arasında overlap bıraktım. Recursive yöntemde önce paragraf ve cümle gibi doğal sınırları kullanmaya çalıştım. Markdown-aware yöntemde başlık yapısını korumanın mümkün olduğunu gördüm. Recursive yöntemde daha doğal ayırıcıları öncelemeyi, Markdown-aware yöntemde ise başlık yapısını korumayı kod üzerinden karşılaştırdım.
Semantic olarak adlandırılan yöntemde cümleler arasındaki benzerliğe göre sınır oluşturma fikrini inceledim. Hazır cümle modeli kullanılamadığı durumda alternatif vektör üretimi devreye girebildiği için elde edilen sonuçların yöntem ayrıntısıyla birlikte değerlendirilmesi gerektiğini not ettim. Semantic yöntemin kullandığı temsilin hazır model bulunamaması durumunda alternatif biçimde üretilebildiğini inceleyerek sonuçları tek bir modelle ilişkilendirmedim.
Kullanılan SOP ve teknik dokümanlar gerçek Merinos bakım belgeleri değildi. İçerikler proje için hazırlanmış örnek metinlerden oluşuyordu. Bu nedenle chunking ayarlarını şirketin gerçek doküman standardı gibi kabul etmedim. Örnek SOP dokümanları tamamen proje için hazırlanmıştı; gerçek bakım kılavuzları olmadığı için chunk boyutlarını kurumsal standart gibi değerlendirmedim.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 25 — DEVAM
**KISIM:** Doküman Chunking Yöntemleri  
**YAPRAK NO:** 50  
**YAPILAN İŞ:** Sentetik teknik dokümanlarda parça boyutu ve arama etkisinin değerlendirilmesi  
**TARİH:** 18/08/2026

Günün devamında dört yöntemin ürettiği parça sayısını, ortalama uzunluğu ve basit arama sonuçlarını karşılaştırdım. Çok küçük parçaların bağlamı bölebildiğini, çok büyük parçaların ise gereksiz metin taşıyabildiğini gördüm. Parça sayısı arttıkça arama yapılacak kayıt sayısının da arttığını, çok büyük parçalarda ise farklı konuların tek metinde karışabildiğini gördüm.
Overlap miktarı arttığında komşu parçalar arasında bilgi kaybı azalabiliyordu fakat aynı metnin tekrar indekslenmesi nedeniyle fazladan veri oluşuyordu. Bu dengeyi sentetik dokümanlar üzerinde gözlemledim. Overlap kullanmanın iki parça sınırında kalan cümlelerin bağlamını korumaya yardımcı olabileceğini örnek metin üzerinde gözlemledim.
Kayıtlı benchmark değerlerinin README’deki bazı eski ifadelerle uyuşmadığını fark ettiğim için defterde güncel JSON ve PNG çıktısını esas aldım. Bunun da yalnızca örnek veri seti sonuçları olduğunu belirttim. Değerlendirme panelinde Precision@1 ile önemli bilginin ilk beş sonuçta bulunma oranını birlikte okuyarak tek metriğin bütün resmi göstermediğini gördüm.
Yirmi beşinci gün sonunda doküman parçalama işleminin arama kalitesini doğrudan etkileyebileceğini öğrendim. Gerçek bakım veya prosedür dokümanları sağlanırsa başlık yapısı, tablo içeriği ve doküman türüne göre chunking stratejisinin yeniden seçilmesi gerekir. Günün sonunda chunking kararının doğrudan arama sonucunu etkileyen bir ön işleme adımı olduğunu ve gerçek doküman yapısına göre yeniden ayarlanması gerektiğini öğrendim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

**KONTROL SONUCU:**

---

## GÜN 26 — 19 AĞUSTOS 2026
**KISIM:** Vektör İndeksleme Yöntemleri  
**YAPRAK NO:** 51  
**YAPILAN İŞ:** Exact, IVF ve HNSW indekslerinin sentetik vektörler üzerinde incelenmesi  
**TARİH:** 19/08/2026

Yirmi altıncı gün vektör sayısı arttığında bütün kayıtlarla tek tek karşılaştırma yapmanın maliyetini azaltmak için kullanılan indeksleme yöntemlerini çalıştım. Exact Flat yaklaşımını temel alıp IVF ve HNSW yapılarının aramayı nasıl hızlandırmaya çalıştığını inceledim. Exact aramayı referans kabul ederek IVF ve HNSW sonuçlarını onunla karşılaştırdım; böylece hız kazanırken doğru komşuları ne kadar koruduğumu Recall@5 üzerinden anlamaya çalıştım.
IVF’de vektörlerin önce daha küçük gruplara ayrıldığını, sorgu sırasında yalnızca bazı grupların taranabildiğini öğrendim. HNSW’de ise vektörlerin bir grafik yapısında birbirine bağlanarak yakın komşulara aşamalı biçimde ulaşılabildiğini kod üzerinden takip ettim. IVF yönteminde vektörlerin önce kümelere ayrılması, HNSW'de ise komşuluk grafiği kurulması fikrini kodun veri yapıları üzerinden inceledim.
Kullandığım vektör corpus’u sentetikti. Gerçek doküman embeddingleri veya üretim sisteminden alınmış kayıtlar kullanılmadı. Bu nedenle sorgu süreleri ve recall değerleri yalnızca kendi bilgisayarımda ve proje veri setinde elde edilen teknik denemelerdi. İndeks oluşturma süresi ile sorgu süresinin farklı maliyetler olduğunu, bir sistem tasarlanırken yalnızca sorgu gecikmesine bakılmaması gerektiğini fark ettim.
Ayrıca vektörleri daha küçük sayısal temsil ile saklama fikrini inceledim. Kod içinde SQ8 benzeri sıkıştırma hesapları bulunuyordu. Buradaki “indeks boyutu” değerinin bilgisayarın gerçek toplam RAM tüketimiyle aynı olmadığını özellikle not ettim. Kullanılan vektör korpusu sentetik olduğundan sonuçları gerçek Merinos doküman sayısı veya gerçek üretim ölçeği gibi sunmadım.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 26 — DEVAM
**KISIM:** Vektör İndeksleme Yöntemleri  
**YAPRAK NO:** 52  
**YAPILAN İŞ:** Arama süresi, recall ve hesaplanan indeks boyutlarının karşılaştırılması  
**TARİH:** 19/08/2026

Günün devamında Exact, IVF, HNSW ve kuantize HNSW için arama süresi, Recall@5 ve yaklaşık indeks boyutlarını karşılaştırdım. Daha hızlı aramanın bazı durumlarda kesin sonuçtan ödün verme ihtimali taşıdığını gördüm. Kuantize edilmiş vektörlerin hesaplanan dosya boyutunu orijinal vektörlerle karşılaştırarak sıkıştırma fikrini daha sonraki Edge AI gününden önce tanıdım.
Filtreli arama örneğinde departman veya makine gibi metadata alanlarıyla sonuçların daraltılabileceğini inceledim. Bu metadata alanları gerçek kurum organizasyonundan alınmadı; filtre mantığını göstermek için örnek olarak oluşturuldu. Filtreli arama örneklerinde departman veya makine etiketi gibi metadata alanlarının aday kümesini daraltabildiğini gördüm.
Testlerde indeks oluşturma, sorgu yapma, top-k sonuç sayısı ve filtre davranışları kontrol edildi. Bu testler gerçek vektör veritabanı altyapısının ölçek testleri değildi; küçük sentetik veri üzerinde fonksiyonların doğru çalışmasını doğruluyordu. Kodda sıkıştırılmış vektör oluşturulmasına rağmen aramanın bazı bölümlerde orijinal vektörleri kullandığını fark ederek rapordaki bellek değerlerini dikkatli yorumladım.
Yirmi altıncı gün sonunda arama sistemi büyüdükçe veri yapısının ve indeks seçiminin önemli hale geldiğini öğrendim. Gerçek kullanımda veri sayısı, gecikme hedefi ve doğruluk beklentisi ölçülmeden hangi indeksin seçileceğine karar verilmemelidir. Bu gün arama kalitesi, hız ve bellek kullanımının birlikte düşünülmesi gerektiğini, gerçek ölçek için ayrıca yük testi yapılması gerektiğini öğrendim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

**KONTROL SONUCU:**

---

## GÜN 27 — 20 AĞUSTOS 2026
**KISIM:** RAG Temelleri ve Değerlendirme  
**YAPRAK NO:** 53  
**YAPILAN İŞ:** Sentetik teknik soru-cevap örnekleri için değerlendirme kodlarının incelenmesi  
**TARİH:** 20/08/2026

Yirmi yedinci gün arama ve cevap üretme sistemlerinde yalnızca çıktı almak yerine sonucun kalitesini nasıl kontrol edebileceğimi çalıştım. Proje içinde hazırlanmış soru, kaynak metin ve örnek cevaplardan oluşan küçük bir değerlendirme veri seti kullandım. Değerlendirme veri setinde her sorunun beklenen cevap veya kaynak bilgisiyle birlikte tutulmasının otomatik karşılaştırma yapmayı kolaylaştırdığını gördüm.
`context_metrics.py` dosyasında getirilen metinlerin soruyla ilişkisini ölçmeye çalışan basit hesaplamaları, `generation_metrics.py` içinde ise cevabın gerekli bilgileri taşıyıp taşımadığını kontrol eden yaklaşımları inceledim. Bu ölçümlerin gerçek insan değerlendirmesinin yerini tamamen tutmadığını gördüm. Context precision ve recall benzeri kontrolleri ayrı ayrı inceleyerek aramanın gereksiz metin getirmesi ile gerekli metni kaçırmasının farklı hata türleri olduğunu öğrendim.
Cevaptaki bazı iddiaları ayrı parçalara ayırıp kaynak metinde karşılığı olup olmadığını kontrol eden yaklaşımı da inceledim. Bu sayede yüksek genel puanın altında belirli bir cümlenin sorunlu olabileceğini fark ettim. Generation tarafındaki ölçümlerde cevap içeriği ile kaynak metin arasındaki ilişkiye bakıldığını, yalnızca akıcı bir cümlenin kaliteli cevap anlamına gelmediğini fark ettim.
Kullanılan sorular gerçek çalışanlardan veya bakım ekiplerinden toplanmadı. Tamamen proje için hazırlanmış sentetik örneklerdi. Bu nedenle sonuçları “operatörlerin sorularında başarı” şeklinde yorumlamadım. Kullanılan soru ve cevaplar sentetik olduğu için değerlendirme puanlarını gerçek saha kullanıcı memnuniyeti veya gerçek teknik doğruluk göstergesi olarak sunmadım.

RAG akışını değerlendirirken retrieval ile generation aşamalarını birbirinden ayırmanın önemli olduğunu gördüm. Doğru bilgi parçası bulunmadığında dil modelinden güvenilir cevap beklemenin doğru olmayacağını; buna karşılık doğru parça getirildiği hâlde cevabın kaynaktan uzaklaşmasının ayrı bir generation problemi olduğunu fark ettim. Bu nedenle her denemede önce bulunan parçaları okuyup sorguyla ilişkisini kontrol ettim, ardından cevap içindeki önemli ifadelerin gerçekten verilen context içinde bulunup bulunmadığını karşılaştırdım. Böylece tek bir “cevap doğru/yanlış” değerlendirmesi yerine hata kaynağını daha ayrıntılı inceleyebildim.

**KONTROL SONUCU:**

---

## GÜN 27 — DEVAM
**KISIM:** RAG Temelleri ve Değerlendirme  
**YAPRAK NO:** 54  
**YAPILAN İŞ:** Kaynak kapsamı ve cevap uygunluğu metriklerinin sentetik veri üzerinde değerlendirilmesi  
**TARİH:** 20/08/2026

Günün devamında üç farklı örnek retrieval/cevap akışını aynı veri setinde karşılaştırdım. Bazı yöntemlerin belirli sorularda daha iyi görünmesine rağmen sonuçların veri seti küçük olduğunda genelleme yapılamayacağını not ettim. Farklı pipeline sonuçlarını aynı panelde karşılaştırırken hangi yaklaşımın hangi sorularda hata verdiğini tek tek incelemeye çalıştım.
Notebook içindeki diagnostic panelde kaynakla örtüşme, gerekli bilginin bulunması ve genel sonuçları tek ekranda inceledim. Grafiğin amacı sistemi güzel göstermekten çok hangi sorularda zayıflık olduğunu fark etmekti. Bir metrik yüksek çıktığında örnek cevabı da açıp içerikle uyuşup uyuşmadığını kontrol etmek, otomatik puanların sınırlamalarını görmemi sağladı.
Testlerde metrik fonksiyonlarının beklenen aralıkta değer üretmesi ve boş kaynak gibi durumlarda kontrollü davranması doğrulandı. Bu gün, değerlendirme kodunun da en az arama kodu kadar dikkatli tasarlanması gerektiğini anlamama yardımcı oldu. Testlerde değerlendirme fonksiyonlarının boş kaynak veya eksik cevap gibi durumlarda kontrollü sonuç üretmesine dikkat ettim.
Yirmi yedinci gün sonunda bir PoC’nin yalnız demo ekranından ibaret olmaması gerektiğini öğrendim. Gerçek kurumsal kullanım düşünülürse alan uzmanlarının hazırladığı soru-cevap seti ve insan değerlendirmesi ile ayrıca doğrulama yapılmalıdır. Bu gün ölçüm yapmanın sistemi geliştirmek kadar önemli olduğunu, ancak metriğin neyi ölçtüğünü bilmeden yalnızca sayıya bakmanın yanıltıcı olabileceğini öğrendim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

**KONTROL SONUCU:**

---

## GÜN 28 — 21 AĞUSTOS 2026
**KISIM:** Kontrollü Görsel Üretim  
**YAPRAK NO:** 55  
**YAPILAN İŞ:** Halı tasarım isteğinin yapılandırılması ve sentetik görsel varyasyonlarının oluşturulması  
**TARİH:** 21/08/2026

Yirmi sekizinci gün üretken yapay zekâ tarafında kontrollü görsel üretim mantığını çalıştım. Amaç gerçek Merinos tasarım sürecine müdahale etmek değil, metinle verilen bir tasarım isteğini yazılım içinde daha düzenli alanlara ayırıp farklı çıktılar üretme yöntemini öğrenmekti. Tasarım isteğini tek uzun cümle olarak kullanmak yerine stil, motif, ana renk, yardımcı renk, kompozisyon ve bordür gibi alanlara ayırmanın daha kontrollü giriş sağladığını gördüm.
Stil, motif, ana renk, ikincil renk, kompozisyon ve bordür gibi alanlar tanımladım. Serbest biçimde yazılan bir cümlenin bu alanlara ayrılması, aynı isteğin daha kontrollü şekilde tekrar kullanılmasını sağladı. Kullandığım tasarım brief’leri tamamen örnekti. Aynı tasarım bilgilerinde yalnızca tek bir alanı değiştirerek oluşan farkı karşılaştırmak, hangi girdinin görsel sonucu etkilediğini daha anlaşılır hale getirdi.
Repo içinde SDXL gibi üretken model kavramları ve prompt yapıları incelendi. Modelin erişilebilir olmadığı veya farklı ortamda çalıştığı durumları da göz önünde bulundurdum. Üretilen görselleri gerçek ürün tasarımı veya üretim reçetesi olarak değerlendirmedim. Seed kavramını kullanarak aynı koşullarda tekrar üretilebilirlik fikrini inceledim ve rastlantısallığın sonuçları değiştirebildiğini gördüm.
Aynı prompt ile seed değiştirildiğinde ayrıntıların değişebildiğini, seed sabit tutulup tek bir alan değiştirildiğinde farkı daha kontrollü karşılaştırmanın mümkün olduğunu öğrendim. Bu deneyler üretken modellerde tekrar üretilebilirliği anlamama yardımcı oldu. Gerçek tasarım departmanı verisi, müşteri siparişi veya kurum içi renk reçetesi kullanılmadığı için çalışmayı yalnızca sentetik görsel üretim deneyi olarak tuttum.

Üretken görüntü tarafında değerlendirmeyi yalnız estetik beğeni üzerinden yapmamaya çalıştım. Aynı girdide seed değişiminin, aynı seed değerinde ise tek bir prompt alanının değiştirilmesinin sonucu nasıl etkilediğini ayrı ayrı gözlemledim. Model çıktılarının fiziksel üretilebilirlik, iplik seçimi veya makine kısıtları hakkında doğrudan bilgi vermediğini özellikle ayırdım. Bu nedenle oluşturulan görselleri nihai ürün tasarımı olarak değil, daha önce öğrendiğim renk, geometri ve benzerlik yöntemlerini uygulayabileceğim kontrollü dijital örnekler olarak kullandım.

**KONTROL SONUCU:**

---

## GÜN 28 — DEVAM
**KISIM:** Kontrollü Görsel Üretim  
**YAPRAK NO:** 56  
**YAPILAN İŞ:** Seed ve tek değişkenli prompt varyasyonlarının örnek çıktılar üzerinde incelenmesi  
**TARİH:** 21/08/2026

Günün devamında birkaç örnek varyasyonu yan yana koyarak yalnız motif veya renk gibi tek bir alanın değiştirilmesinin sonucu nasıl etkilediğini inceledim. Böylece çok sayıda değişkeni aynı anda değiştirdiğimde hangi unsurun sonucu etkilediğini anlamanın zorlaştığını gördüm. Prompt metnini oluştururken boş bırakılan alanların gereksiz ifade üretmemesine dikkat ederek basit bir giriş doğrulama mantığı kullandım.
Promptları kısa ve açık tutmaya, modele kesin üretim bilgisi vermek yerine görsel betimleme sağlamaya dikkat ettim. Gerçek tasarım departmanının renk reçeteleri, desen dosyaları veya tescilli ürün verileri bana verilmedi ve kullanılmadı. Farklı varyasyonları yan yana inceleyerek aynı temel tanımın birden fazla görsel sonuç üretebileceğini ve insan seçiminin hâlâ gerekli olduğunu fark ettim.
Üretilen görsellerin fiziksel olarak dokunabilir olup olmadığını, iplik seçimini veya üretim makinelerinin kısıtlarını doğrulayacak bir sistemim olmadığını not ettim. Bu nedenle çalışma yalnızca dijital görsel denemesiydi. Notebook çıktılarında hangi parametreyle hangi görselin üretildiğini birlikte tutmanın daha sonra karşılaştırma yapmayı kolaylaştırdığını gördüm.
Yirmi sekizinci günün sonunda kontrollü görsel üretimde girişlerin yapılandırılması ve tek değişkenli karşılaştırma yapmanın önemini öğrendim. Gerçek tasarım kullanımına geçilmesi halinde tasarım ekibinin kuralları ve üretilebilirlik kriterleri ayrıca sisteme dahil edilmelidir. Bu günkü çalışma bana üretken bir aracın doğrudan nihai tasarım kararı vermek yerine fikir geliştirme veya görsel deneme aracı olarak değerlendirilebileceğini gösterdi.

Bu yaklaşım aynı zamanda önceki günlerde öğrendiğim analiz araçlarını tek bir problem etrafında birleştirmemi sağladı. Üretilen görüntünün renk paletini çıkarmak, Delta E ile bazı renkleri karşılaştırmak, simetri veya kenar düzenini ölçmek ve benzer örnekleri sıralamak; tek başına görüntü üretmekten daha mühendislik odaklı bir çalışma oluşturdu. Sonuçların hangi girdi ve parametrelerle üretildiğini kayıt altında tutmanın tekrar üretilebilirlik açısından önemli olduğunu gördüm. Böylece görsel üretim modülünü bağımsız bir “AI özelliği” yerine ölçülebilir bir deney akışının bir bileşeni olarak değerlendirdim.

Bu yaklaşım aynı zamanda önceki günlerde öğrendiğim analiz araçlarını tek bir problem etrafında birleştirmemi sağladı. Üretilen görüntünün renk paletini çıkarmak, Delta E ile bazı renkleri karşılaştırmak, simetri veya kenar düzenini ölçmek ve benzer örnekleri sıralamak; tek başına görüntü üretmekten daha mühendislik odaklı bir çalışma oluşturdu. Sonuçların hangi girdi ve parametrelerle üretildiğini kayıt altında tutmanın tekrar üretilebilirlik açısından önemli olduğunu gördüm. Böylece görsel üretim modülünü bağımsız bir “AI özelliği” yerine ölçülebilir bir deney akışının bir bileşeni olarak değerlendirdim.

**KONTROL SONUCU:**

---

## GÜN 29 — 22 AĞUSTOS 2026
**KISIM:** Üretilen Görsellerin Sayısal Analizi  
**YAPRAK NO:** 57  
**YAPILAN İŞ:** Sentetik üretilmiş halı görsellerinde renk, simetri ve kenar özelliklerinin çıkarılması  
**TARİH:** 22/08/2026

Yirmi dokuzuncu gün önceki gün oluşturulan örnek görselleri yalnız görsel olarak değerlendirmek yerine sayısal özelliklerle incelemeye çalıştım. Renk paleti, LAB renk farkı, yatay/dikey simetri ve kenar yoğunluğu gibi daha önce öğrendiğim yöntemleri aynı görüntü üzerinde bir araya getirdim. Üretilen görseli analiz ederken önce baskın renkleri çıkarıp hedef paletle karşılaştırdım; böylece üretim adımından bağımsız bir kontrol katmanı oluşturmayı denedim.
İlk olarak baskın renkleri K-Means ile çıkardım ve örnek hedef paletle Delta E üzerinden karşılaştırdım. Bu karşılaştırmada kullanılan renkler gerçek iplik kartelası değildi; proje içinde hazırlanmış sentetik referanslardı. Simetri analizinde görüntünün sağ-sol ve üst-alt yarılarını karşılaştırarak özellikle merkezî desenlerde yapısal benzerliğin sayısal hale getirilebildiğini gördüm.
Daha sonra görüntünün sağ-sol ve üst-alt bölümlerini karşılaştırarak basit simetri skorları hesapladım. Halı desenlerinin her zaman tam simetrik olmak zorunda olmadığını bildiğim için bu değeri kalite kararı olarak değil, yalnızca görsel bir özellik olarak kullandım. Kenar şeritlerini ayrı alıp karşılıklı kenarları karşılaştırmak, tekrar eden desenlerde süreklilik kontrolünün basit bir örneğini verdi.
Kenar ve dikiş sürekliliğini temsil eden bazı basit ölçümler ekledim. Bu alanların gerçek dokuma kusurunu kanıtlamadığını, yalnızca görüntüdeki çizgi ve kenar değişimlerini sayısallaştırdığını özellikle not ettim. Bütün bu ölçümlerin estetik kalite veya gerçek dokuma uygunluğu anlamına gelmediğini ve uzman değerlendirmesinin yerini tutmadığını not ettim.

Üretken görüntü tarafında değerlendirmeyi yalnız estetik beğeni üzerinden yapmamaya çalıştım. Aynı girdide seed değişiminin, aynı seed değerinde ise tek bir prompt alanının değiştirilmesinin sonucu nasıl etkilediğini ayrı ayrı gözlemledim. Model çıktılarının fiziksel üretilebilirlik, iplik seçimi veya makine kısıtları hakkında doğrudan bilgi vermediğini özellikle ayırdım. Bu nedenle oluşturulan görselleri nihai ürün tasarımı olarak değil, daha önce öğrendiğim renk, geometri ve benzerlik yöntemlerini uygulayabileceğim kontrollü dijital örnekler olarak kullandım.

**KONTROL SONUCU:**

---

## GÜN 29 — DEVAM
**KISIM:** Üretilen Görsellerin Sayısal Analizi  
**YAPRAK NO:** 58  
**YAPILAN İŞ:** Sentetik katalog üzerinde çok boyutlu görsel analiz sonuçlarının karşılaştırılması  
**TARİH:** 22/08/2026

Günün devamında sentetik bir referans katalog oluşturarak üretilen görselin benzer örneklerini aramayı denedim. Vektör/embedding kullanılabildiği durumda benzerlik puanı hesaplanıyor, model bulunamazsa kod içindeki alternatif yöntemler devreye girebiliyordu. Örnek katalog vektörlerini kullanarak en yakın birkaç kaydı sıraladım ve benzerlik skorunun hangi özelliklerden üretildiğini kod içinde kontrol ettim.
Bu nedenle “pretrained CNN kesin olarak çalıştı” gibi bir iddiayı yalnız kayıtlı rapora dayanarak kullanmadım. Çalışan yöntemin ortam koşullarına göre değişebileceğini ve gerçek görsel benzerlik sisteminde modelin açık biçimde doğrulanması gerektiğini gördüm. Hazır bir derin öğrenme modeli çalıştığı varsayımına gitmeden, mevcut kodun renk ve doku temelli özelliklerle sonuç üretebildiğini özellikle dikkate aldım.
Analiz sonuçlarını tek bir JSON ve görsel panelde topladım. Böylece bir görüntü için renk, simetri ve benzerlik bilgilerini ayrı dosyalardan okumak yerine ortak bir raporda inceleyebildim. Rapor çıktısında renk, simetri, kenar ve benzerlik sonuçlarını aynı dosyada toplamanın farklı analizleri tek yerden izlemeyi kolaylaştırdığını gördüm.
Yirmi dokuzuncu gün sonunda üretilen bir görseli farklı açılardan sayısallaştırmanın mümkün olduğunu öğrendim. Ancak bu puanların gerçek kalite, özgünlük veya üretilebilirlik kararı vermediğini; gerçek veri ve uzman görüşü olmadan yalnızca PoC çıktısı olduğunu not ettim. Günün sonunda bir görseli tek bir puanla değerlendirmek yerine farklı özellikleri ayrı ölçüp birlikte yorumlamanın daha açıklanabilir bir yaklaşım sunduğunu öğrendim.

Bu yaklaşım aynı zamanda önceki günlerde öğrendiğim analiz araçlarını tek bir problem etrafında birleştirmemi sağladı. Üretilen görüntünün renk paletini çıkarmak, Delta E ile bazı renkleri karşılaştırmak, simetri veya kenar düzenini ölçmek ve benzer örnekleri sıralamak; tek başına görüntü üretmekten daha mühendislik odaklı bir çalışma oluşturdu. Sonuçların hangi girdi ve parametrelerle üretildiğini kayıt altında tutmanın tekrar üretilebilirlik açısından önemli olduğunu gördüm. Böylece görsel üretim modülünü bağımsız bir “AI özelliği” yerine ölçülebilir bir deney akışının bir bileşeni olarak değerlendirdim.

Bu yaklaşım aynı zamanda önceki günlerde öğrendiğim analiz araçlarını tek bir problem etrafında birleştirmemi sağladı. Üretilen görüntünün renk paletini çıkarmak, Delta E ile bazı renkleri karşılaştırmak, simetri veya kenar düzenini ölçmek ve benzer örnekleri sıralamak; tek başına görüntü üretmekten daha mühendislik odaklı bir çalışma oluşturdu. Sonuçların hangi girdi ve parametrelerle üretildiğini kayıt altında tutmanın tekrar üretilebilirlik açısından önemli olduğunu gördüm. Böylece görsel üretim modülünü bağımsız bir “AI özelliği” yerine ölçülebilir bir deney akışının bir bileşeni olarak değerlendirdim.

**KONTROL SONUCU:**

---

## GÜN 30 — 24 AĞUSTOS 2026
**KISIM:** Görsel Üretim ve Analiz Mini Prototipi  
**YAPRAK NO:** 59  
**YAPILAN İŞ:** Sentetik tasarım girdisi, görsel oluşturma ve analiz adımlarının tek uygulamada toplanması  
**TARİH:** 24/08/2026

Otuzuncu gün 28 ve 29. günlerde ayrı ayrı çalıştığım görsel oluşturma ve analiz işlemlerini tek bir uygulama akışında birleştirdim. Kullanıcıdan stil, motif ve renk gibi örnek alanlar alınıyor; daha sonra sentetik bir görsel oluşturulup aynı görsel üzerinde analiz adımları çalıştırılıyordu. Pipeline sınıfını incelerken önce kullanıcı girdisinin doğrulandığını, ardından görsel oluşturma ve analiz modüllerinin sırayla çağrıldığını takip ettim.
`pipeline.py` içinde işlemlerin hangi sırayla çağrıldığını inceledim. Girdi kontrolü, prompt/brief hazırlama, görsel oluşturma, renk analizi, simetri ve benzerlik işlemlerinin çıktılarını ortak bir sonuç nesnesinde toplamaya çalıştım. Bir adımın çıktısının sonraki adıma girdi olması nedeniyle dosya yolları, veri tipleri ve hata durumlarının modüller arasında uyumlu tutulmasının önemli olduğunu gördüm.
Bu uygulama gerçek bir üretim tasarım sistemi değildi. Tezgâha reçete göndermiyor, gerçek tasarım arşivini kullanmıyor ve üretilebilirlik hesabı yapmıyordu. Bilgisayarımda çalışan farklı modülleri tek akışta yönetmeyi öğrenmek için hazırladığım yerel bir PoC idi. Aynı örnek brief'i birkaç kez çalıştırarak üretilen dosya ile analiz raporunun aynı işlem kimliği altında tutulmasının takip kolaylığı sağladığını fark ettim.
Kodları birleştirirken bir modül hata verdiğinde diğer işlemlerin nasıl etkilenebileceğini gördüm. Bu nedenle zorunlu alanların kontrolü, boş katalog durumu ve dosya kaydetme hataları gibi birkaç temel hata senaryosunu ele aldım. Uygulama hiçbir üretim reçetesini gerçek sisteme göndermediği için bu çalışmayı yalnızca masaüstü PoC olarak değerlendirdim.

Üretken görüntü tarafında değerlendirmeyi yalnız estetik beğeni üzerinden yapmamaya çalıştım. Aynı girdide seed değişiminin, aynı seed değerinde ise tek bir prompt alanının değiştirilmesinin sonucu nasıl etkilediğini ayrı ayrı gözlemledim. Model çıktılarının fiziksel üretilebilirlik, iplik seçimi veya makine kısıtları hakkında doğrudan bilgi vermediğini özellikle ayırdım. Bu nedenle oluşturulan görselleri nihai ürün tasarımı olarak değil, daha önce öğrendiğim renk, geometri ve benzerlik yöntemlerini uygulayabileceğim kontrollü dijital örnekler olarak kullandım.

**KONTROL SONUCU:**

---

## GÜN 30 — DEVAM
**KISIM:** Görsel Üretim ve Analiz Mini Prototipi  
**YAPRAK NO:** 60  
**YAPILAN İŞ:** Örnek görsel üretim/analiz uygulamasının kullanıcı arayüzü üzerinden incelenmesi  
**TARİH:** 24/08/2026

Günün devamında HTML/CSS/JavaScript ile hazırlanmış basit bir yerel arayüzü inceledim. Kullanıcı formdan örnek tasarım alanlarını dolduruyor ve analiz sonucunu aynı sayfada görebiliyordu. Arayüz yalnız localhost üzerinde çalıştı; kurumsal bir sunucuya dağıtılmadı. Web arayüzündeki alanların arka taraftaki veri modeline nasıl dönüştürüldüğünü inceleyerek kullanıcı arayüzü ile Python kodu arasındaki veri akışını daha iyi anladım.
Web tarafıyla Python kodu arasında veri aktarımını sağlayan servis dosyasını okuyarak form girdilerinin nasıl modele dönüştürüldüğünü gördüm. Bu, daha sonraki FastAPI gününe geçmeden önce web arayüzü ile Python uygulaması arasındaki bağlantıyı anlamama yardımcı oldu. Eksik stil, motif veya renk gibi girişlerde programın uyarı vermesi, kullanıcıdan gelen verinin daha işleme başlamadan kontrol edilmesi gerektiğini gösterdi.
Testlerde eksik zorunlu alan, boş referans katalog ve normal akış gibi durumları kontrol ettim. Kullanılan görseller ve sonuçlar sentetik olduğundan testlerin amacı gerçek kalite veya üretim uygunluğu değil, yazılım akışının kırılmadan çalışmasıydı. Örnek katalog bulunmadığında diğer analizlerin devam edebilmesi gibi hata durumlarını incelemek, uygulamanın tek bir eksik bileşen yüzünden tamamen durmaması fikrini anlamamı sağladı.
Otuzuncu gün sonunda farklı modülleri ortak bir kullanıcı akışında birleştirme konusunda deneyim kazandım. Gerçek işletme kullanımında bu tür bir uygulamanın veri kaynakları, yetkilendirme ve iş süreçleri kurum tarafından ayrıca tanımlanmalıdır. Bu gün önceki modülleri birleştirirken entegrasyonun yeni hatalar oluşturabileceğini ve tek tek çalışan parçaların birlikte de ayrıca test edilmesi gerektiğini öğrendim.

Bu yaklaşım aynı zamanda önceki günlerde öğrendiğim analiz araçlarını tek bir problem etrafında birleştirmemi sağladı. Üretilen görüntünün renk paletini çıkarmak, Delta E ile bazı renkleri karşılaştırmak, simetri veya kenar düzenini ölçmek ve benzer örnekleri sıralamak; tek başına görüntü üretmekten daha mühendislik odaklı bir çalışma oluşturdu. Sonuçların hangi girdi ve parametrelerle üretildiğini kayıt altında tutmanın tekrar üretilebilirlik açısından önemli olduğunu gördüm. Böylece görsel üretim modülünü bağımsız bir “AI özelliği” yerine ölçülebilir bir deney akışının bir bileşeni olarak değerlendirdim.

Bu yaklaşım aynı zamanda önceki günlerde öğrendiğim analiz araçlarını tek bir problem etrafında birleştirmemi sağladı. Üretilen görüntünün renk paletini çıkarmak, Delta E ile bazı renkleri karşılaştırmak, simetri veya kenar düzenini ölçmek ve benzer örnekleri sıralamak; tek başına görüntü üretmekten daha mühendislik odaklı bir çalışma oluşturdu. Sonuçların hangi girdi ve parametrelerle üretildiğini kayıt altında tutmanın tekrar üretilebilirlik açısından önemli olduğunu gördüm. Böylece görsel üretim modülünü bağımsız bir “AI özelliği” yerine ölçülebilir bir deney akışının bir bileşeni olarak değerlendirdim.

**KONTROL SONUCU:**

---

## GÜN 31 — 25 AĞUSTOS 2026
**KISIM:** Doküman Alma ve Ön İşleme  
**YAPRAK NO:** 61  
**YAPILAN İŞ:** PDF, Word ve Markdown örneklerinin okunması, temizlenmesi ve parçalanması  
**TARİH:** 25/08/2026

Otuz birinci gün doküman arama çalışmalarını daha düzenli bir yapı altında tekrar ele aldım. Bu aşamada özellikle gerçek kurum dokümanları kullanmadığımı netleştirdim. Bana bakım kılavuzu, tezgâh hata kayıtları veya şirket içi prosedür PDF’leri teslim edilmedi. PDF, DOCX ve Markdown dosyalarını ayrı yükleyicilerle okuyup elde edilen metinlerin ortak bir `Document` yapısına dönüştüğünü kontrol ettim.
Bunun yerine proje içinde PDF, DOCX ve Markdown biçiminde örnek teknik dokümanlar oluşturdum. Dosya isimleri dokuma, kalite ve finisaj gibi endüstriyel konuları temsil etse de içerikler sentetikti. Amaç farklı dosya türlerini yazılımla okuyabilmekti. Metin temizleme aşamasında gereksiz boşluk, satır sonu bölünmesi ve başlık bilgilerini koruma gibi küçük ayrıntıların arama kalitesini etkileyebileceğini gördüm.
PDF ve Word dosyalarının metnini çıkaran loader fonksiyonlarını inceledim. Daha sonra gereksiz boşluk, sayfa bilgisi ve satır bölünmelerini temizleyen küçük bir metin temizleme adımı kullandım. Kaynak dosya adı ve başlık gibi metadata bilgilerini korumaya dikkat ettim. Metadata alanlarına dosya adı, bölüm ve sayfa gibi bilgiler ekleyerek daha sonra bulunan parçanın kaynağına geri dönmenin mümkün olmasını hedefledim.
Temizlenen metinleri sabit boyutlu ve başlık/paragraf yapısını dikkate alan iki yöntemle parçalara ayırdım. Sentetik üç dokümandan üretilen parça sayılarını karşılaştırarak parçalama yönteminin indeks yapısını etkilediğini gördüm. Kullandığım PDF ve Word dosyalarının gerçek kurum belgeleri değil, çalışma için hazırlanmış örnek teknik içerikler olduğunu açıkça korudum.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 31 — DEVAM
**KISIM:** Doküman Alma ve Ön İşleme  
**YAPRAK NO:** 62  
**YAPILAN İŞ:** Sentetik teknik dokümanlar üzerinde iki arama yaklaşımının karşılaştırılması  
**TARİH:** 25/08/2026

Günün devamında aynı doküman parçaları üzerinde BM25 ve yoğun arama yöntemlerini karşılaştırdım. `test_queries.json` içindeki sorular yine proje için hazırlanmıştı; gerçek operatörlerden veya bakım personelinden toplanmamıştı. Fixed-size ve başlık duyarlı parçalama sonuçlarında oluşan parça sayılarını karşılaştırarak yöntem seçiminin indeks büyüklüğünü de etkilediğini gördüm.
Bazı sorular açık hata kodu içerirken bazıları aynı konuyu günlük ifadelerle soruyordu. Bu sayede kelime eşleşmesi ağırlıklı BM25 ile anlam yakınlığına dayalı yaklaşımın farklı sorularda farklı sıralamalar üretebildiğini gözlemledim. BM25 ve dense retrieval sonuçlarını aynı 10 soru üzerinde karşılaştırarak bazı sorularda aynı, bazı sorularda farklı ilk sonuçlar geldiğini gözlemledim.
Kayıtlı sonuçlarda iki yöntemin bazı sorularda aynı, bazı sorularda farklı dokümanı öne çıkardığını gördüm. Hangi yöntemin “fabrika için daha iyi” olduğu gibi bir sonuç çıkarmadım; veri seti çok küçük ve sentetikti. Bir yöntemin her soruda üstün olmadığını görmek, gerçek uygulamada değerlendirme seti olmadan yöntem seçmenin sağlıklı olmayacağını anlamamı sağladı.
Otuz birinci gün sonunda gerçek doküman entegrasyonuna geçmeden önce dosya okuma, temizleme, metadata ve chunking gibi hazırlık aşamalarının önemli olduğunu öğrendim. Kurum gerçek doküman erişimi sağlarsa bu adımlar gerçek belge yapısına göre yeniden test edilmelidir. Bu gün doküman arama sisteminde asıl işin yalnızca sorgu çalıştırmak değil, belgeyi doğru okuyup temizlemek, bölmek ve kaynağını korumakla başladığını öğrendim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 32 — 26 AĞUSTOS 2026
**KISIM:** Hibrit Doküman Arama ve Ölçüm  
**YAPRAK NO:** 63  
**YAPILAN İŞ:** BM25 ve vektör tabanlı sonuçların ağırlıklı ve RRF yöntemleriyle birleştirilmesi  
**TARİH:** 26/08/2026

Otuz ikinci gün önceki gün elde edilen BM25 ve yoğun arama sonuçlarını ortak bir listede birleştirmeye odaklandım. `hybrid_retriever.py` içinde aynı sorgunun iki arama yöntemine gönderildiğini ve sonuçların ağırlıklı toplam veya RRF ile birleştirilebildiğini inceledim. İki arama yönteminden gelen skorların aynı ölçeğe sahip olmadığını gördüğüm için doğrusal birleşimde önce normalizasyon yaklaşımını inceledim.
Ağırlıklı yöntemde iki skorun önce karşılaştırılabilir hale getirilmesi gerektiğini gördüm. Başlangıçta iki yönteme eşit ağırlık verdim ve ağırlık değiştiğinde sıralamanın nasıl değiştiğini sentetik örneklerde inceledim. RRF yönteminde ise doğrudan sıraları kullanmanın, skor ölçekleri farklı olduğunda daha sade bir birleşim yolu sunduğunu fark ettim.
RRF yönteminde doğrudan skor büyüklüğünden çok dokümanın listedeki sırası kullanılıyordu. Bu yaklaşımın farklı ölçeklerde puan üreten sistemleri birleştirmeyi kolaylaştırdığını öğrendim. Golden benchmark dosyasında beklenen dokümanın önceden belirtilmesi, yanlış sonucu otomatik olarak tespit edebilmem için gerekli bir referans sağladı.
Kullanılan `golden_benchmark_dataset.json` gerçek kullanıcı sorularından oluşmuyordu. Dokuma, bakım ve kalite konularını temsil eden 15 sentetik soru hazırlanmıştı. Bir soru da sistemin kapsamı dışında kalacak şekilde örneklenmişti. Bu benchmark gerçek kullanıcı sorgularından oluşmadığı için elde edilen oranları saha başarısı olarak yorumlamadım.

Arama tarafında bir sonucun üst sıraya gelmesinin tek başına yeterli olmadığını gördüm. Önce hangi parçanın gerçekten ilgili kabul edileceğini küçük bir test kümesi üzerinde belirlemek, daha sonra Top-K sonuçlarını bu beklentiyle karşılaştırmak gerektiğini öğrendim. Kelime tabanlı ve vektör tabanlı yöntemlerin farklı sinyaller kullandığı için aynı sorguda farklı sıralamalar üretebilmesi normaldi. Bu nedenle bir yöntemi tek örnek üzerinden başarılı veya başarısız ilan etmek yerine aynı sorgu kümesi, aynı doküman parçaları ve aynı değerlendirme ölçütleriyle karşılaştırmaya dikkat ettim.

**KONTROL SONUCU:**

---

## GÜN 32 — DEVAM
**KISIM:** Hibrit Doküman Arama ve Ölçüm  
**YAPRAK NO:** 64  
**YAPILAN İŞ:** Sentetik golden set üzerinde sıralama ve hata türlerinin incelenmesi  
**TARİH:** 26/08/2026

Günün devamında doğru dokümanın ilk sırada, ilk üçte veya ilk beşte bulunup bulunmadığını ölçtüm. Bu ölçümler arama sisteminin “cevabı doğru verdiğini” değil, önceden belirlenen ilgili dokümanı listede hangi sıraya getirdiğini gösteriyordu. Precision@1, Recall@5, MRR ve NDCG gibi ölçümlerin farklı yönleri gösterdiğini örnek sorgular üzerinden okuyarak tek metrik kullanımının sınırlamasını gördüm.
Yanlış sonuçları `error_analyzer.py` ile sınıflandırmaya çalıştım. Bazı hataların soru ifadesinden, bazılarının chunk sınırından veya arama yönteminin kelime ağırlığından kaynaklanabileceğini gördüm. Bu inceleme, tek bir ortalama puanın hatanın nedenini göstermediğini ortaya koydu. Hata analizinde bazı sorunların arama yönteminden değil, chunk sınırından veya sorunun yazılış biçiminden kaynaklanabileceğini fark ettim.
Kayıtlı benchmark değerlerini sentetik veri bağlamında tuttum. Gerçek kullanım için kullanıcıların hangi tür sorular sorduğu ve hangi dokümanların gerçekten doğru kaynak kabul edildiği kurum içindeki uzmanlar tarafından belirlenmelidir. Ağırlıkları değiştirip sonucu yeniden hesaplayarak hibrit sistemlerin ayarlarının da değerlendirme verisine göre seçilmesi gerektiğini gördüm.
Otuz ikinci gün sonunda arama sistemini hem birleştirme hem değerlendirme açısından daha sistematik ele almayı öğrendim. Sentetik golden set, kodu geliştirmek için yararlıydı; ancak gerçek üretim veya bakım kararına temel oluşturacak doğrulama yerine geçmiyordu. Günün sonunda doğru dokümanı bulmak için yalnızca yeni algoritma eklemek yerine hata kaynağını önce sınıflandırmanın daha sağlıklı bir geliştirme yaklaşımı olduğunu öğrendim.

Bu çalışmalarda kullanılan metinler ve sorgular proje için hazırlanmış örnek içeriklerdi. Gerçek bakım talimatı, operatör mesajı veya kurum içi doküman kullanılmadığı için elde ettiğim Precision@K, Recall@K ya da benzer sıralama sonuçlarını şirket performansı olarak yorumlamadım. Bununla birlikte sentetik çalışma, retrieval sistemindeki hatanın hangi katmanda oluştuğunu ayırmayı öğrenmem açısından yararlı oldu. Yanlış sonuç geldiğinde önce sorgu temsilini, sonra chunk yapısını, ardından indeks ve sıralama adımlarını kontrol etmenin daha sistematik bir hata ayıklama yöntemi olduğunu gördüm.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 33 — 27 AĞUSTOS 2026
**KISIM:** Kaynaklı Cevap Üretimi  
**YAPRAK NO:** 65  
**YAPILAN İŞ:** Bulunan sentetik doküman parçalarının kaynak numaralarıyla cevapta kullanılması  
**TARİH:** 27/08/2026

Otuz üçüncü gün arama sonucunda bulunan doküman parçalarını doğrudan kullanıcıya listelemek yerine, bu parçaları kullanarak kaynaklı bir cevap hazırlama yaklaşımını çalıştım. Önceki günlerde olduğu gibi kullanılan dokümanlar gerçek şirket bakım kılavuzları değil, proje için oluşturulmuş sentetik metinlerdi. Context builder içinde bulunan ilk birkaç parçayı `[S1]`, `[S2]` ve `[S3]` biçiminde etiketleyerek cevap içindeki kaynak numarasının hangi metne karşılık geldiğini izleyebildim.
`context_builder.py` içinde ilk birkaç metin parçasının `[S1]`, `[S2]`, `[S3]` gibi kaynak kimlikleriyle bir araya getirildiğini gördüm. Kaynak dosya ve bölüm bilgisini korumak, cevabın hangi metne dayandığını daha sonra kontrol etmeyi kolaylaştırıyordu. Cevap hazırlama kodunda kaynakta geçen cümlelerin seçildiğini görünce bu yapının serbest metin üretiminden daha sınırlı ama daha izlenebilir bir yaklaşım olduğunu fark ettim.
`rag_generator.py` içinde soru ile ilgili cümlelerin kaynak metinden seçilip cevapta kullanılmasını inceledim. Mevcut yapı gerçek bir büyük dil modeline zorunlu olarak bağlı değildi; kaynak cümlelerini seçen basit ve kontrol edilebilir bir yaklaşım bulunuyordu. Kaynak bilgisi olmayan bir cümle eklenmesi durumunda doğrulama adımının bunu nasıl işaretlediğini küçük örneklerle test ettim.
Yeterli kaynak bulunmadığında tahmin yürütmek yerine “bilgi bulunamadı” benzeri bir çıktı verme fikrini denedim. Özellikle teknik konularda bilinmeyen değeri uydurmak yerine cevap vermemek daha güvenli bir davranış olarak ele alındı. Örnek dokümanlar gerçek bakım talimatları olmadığı için cevapları gerçek operasyon talimatı olarak değerlendirmedim.

RAG akışını değerlendirirken retrieval ile generation aşamalarını birbirinden ayırmanın önemli olduğunu gördüm. Doğru bilgi parçası bulunmadığında dil modelinden güvenilir cevap beklemenin doğru olmayacağını; buna karşılık doğru parça getirildiği hâlde cevabın kaynaktan uzaklaşmasının ayrı bir generation problemi olduğunu fark ettim. Bu nedenle her denemede önce bulunan parçaları okuyup sorguyla ilişkisini kontrol ettim, ardından cevap içindeki önemli ifadelerin gerçekten verilen context içinde bulunup bulunmadığını karşılaştırdım. Böylece tek bir “cevap doğru/yanlış” değerlendirmesi yerine hata kaynağını daha ayrıntılı inceleyebildim.

**KONTROL SONUCU:**

---

## GÜN 33 — DEVAM
**KISIM:** Kaynaklı Cevap Üretimi  
**YAPRAK NO:** 66  
**YAPILAN İŞ:** Hazırlanan cevapların sentetik kaynak metinlerle karşılaştırılması  
**TARİH:** 27/08/2026

Günün devamında cevaptaki kaynak numaralarının gerçekten var olup olmadığını ve cümlelerin ilgili kaynak metinle ne kadar örtüştüğünü kontrol eden `citation_verifier.py` dosyasını inceledim. Kontrol ağırlıklı olarak kelime eşleşmesine dayandığı için bunun tam doğruluk garantisi olmadığını öğrendim. Citation verifier içinde cümle ve kaynak arasındaki kelime örtüşmesini inceleyerek bu basit kontrolün semantik doğruluğu tam olarak garanti etmediğini gördüm.
Örneğin kaynakta bulunmayan bir sayı cevaba eklenirse bu durumun işaretlenebilmesini denedim. Buna rağmen yalnız otomatik puana güvenmenin yeterli olmayacağını, özellikle bakım ve güvenlik gibi alanlarda insan kontrolünün gerekli olduğunu not ettim. Bilgi bulunmayan bir soruda sistemin tahmin yürütmek yerine yetersiz bilgi mesajı vermesi, kapalı dünya yaklaşımının amacını anlamama yardımcı oldu.
Testlerde kaynak numarası üretme, bilinmeyen kaynak kimliği ve bilgi bulunmayan soru gibi durumları kontrol ettim. Kayıtlı raporda yüksek değerler görülse de veri sentetik olduğu için “sıfır halüsinasyon” gibi kesin bir iddia kullanmadım. Rapor sonuçlarını tek tek örnek cevaplarla karşılaştırarak yüzde yüz görünen bir metriğin bile içerik kontrolü gerektirdiğini fark ettim.
Otuz üçüncü gün sonunda RAG yaklaşımını “önce ilgili metni bul, sonra cevabı bu metne dayandır ve kaynağı göster” şeklinde sade biçimde anlayabildim. Gerçek kurumsal dokümanlarla kullanılacaksa erişim yetkileri ve kaynak güncelliği ayrıca yönetilmelidir. Bu gün kaynak göstermekle kaynak doğruluğunu doğrulamanın aynı şey olmadığını ve ikisinin ayrı kontroller gerektirdiğini öğrendim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 34 — 28 AĞUSTOS 2026
**KISIM:** Reranking ve Context Yönetimi  
**YAPRAK NO:** 67  
**YAPILAN İŞ:** İlk aşama adaylarının ikinci bir puanlamayla daraltılması  
**TARİH:** 28/08/2026

Otuz dördüncü gün arama sisteminin ilk aşamada getirdiği çok sayıda aday arasından daha ilgili olanları seçme konusunu çalıştım. İlk aşamada hibrit aramayla birkaç doküman parçası getiriliyor, ikinci aşamada bu adaylar tekrar puanlanarak daha küçük bir liste oluşturuluyordu. İlk aşamada en fazla 10 aday parça getirip ikinci aşamada bunların daha küçük bir alt kümesini seçmenin context miktarını nasıl azaltabildiğini kod akışında takip ettim.
`two_stage_pipeline.py` dosyasında ilk aramadan örneğin 10 aday alınması ve daha sonra bunlardan üç tanesinin seçilmesi akışını inceledim. Bu yaklaşımın cevap hazırlama aşamasına gereksiz metin göndermeyi azaltmak için kullanılabileceğini gördüm. Reranker sınıfının mevcut varsayılan biçimde kelime, hata kodu ve sayısal değer eşleşmelerini kullandığını görerek README'deki model isimlerini doğrudan çalışmış kabul etmedim.
`cross_encoder_reranker.py` içinde gerçek bir Cross-Encoder modeli kullanılabilecek yapı bulunmakla birlikte mevcut varsayılan akışta kelime, hata kodu ve sayısal değer eşleşmelerine dayanan alternatif puanlama da vardı. Bu yüzden çalışmayı doğrudan “Cross-Encoder başarısı” diye anlatmadım. Adayların yeniden sıralanmasından önce ve sonra aynı dokümanın konumunu karşılaştırarak yöntemin gerçekten sıralamayı değiştirip değiştirmediğini kontrol ettim.
Sorgular ve belgeler sentetikti. E-401 gibi kodlar proje senaryosunu anlamak için örneklenmişti; bana gerçek tezgâh hata logu veya bakım kaydı verilmedi. Kullanılan teknik sorular ve dokümanlar sentetik olduğundan hız ve başarı değerlerini gerçek operasyon performansı olarak sunmadım.

RAG akışını değerlendirirken retrieval ile generation aşamalarını birbirinden ayırmanın önemli olduğunu gördüm. Doğru bilgi parçası bulunmadığında dil modelinden güvenilir cevap beklemenin doğru olmayacağını; buna karşılık doğru parça getirildiği hâlde cevabın kaynaktan uzaklaşmasının ayrı bir generation problemi olduğunu fark ettim. Bu nedenle her denemede önce bulunan parçaları okuyup sorguyla ilişkisini kontrol ettim, ardından cevap içindeki önemli ifadelerin gerçekten verilen context içinde bulunup bulunmadığını karşılaştırdım. Böylece tek bir “cevap doğru/yanlış” değerlendirmesi yerine hata kaynağını daha ayrıntılı inceleyebildim.

**KONTROL SONUCU:**

---

## GÜN 34 — DEVAM
**KISIM:** Reranking ve Context Yönetimi  
**YAPRAK NO:** 68  
**YAPILAN İŞ:** Sentetik sorgularda iki aşamalı retrieval sonuçlarının incelenmesi  
**TARİH:** 28/08/2026

Günün devamında ilk ve ikinci aşamadaki sıraları karşılaştırdım. Kayıtlı örneklerde doğru dokümanların zaten üst sırada olduğu durumlar bulunduğu için yeniden sıralamanın her sorguda belirgin kazanç sağlamadığını gördüm. Context sıkıştırma hesabında ilk aşamadaki toplam metin uzunluğu ile seçilen üç parçanın uzunluğunu karşılaştırarak azaltım oranının nasıl elde edildiğini inceledim.
Bunun yerine seçilen metin miktarının azaltılması daha görünür bir sonuçtu. Ancak rapordaki “tasarruf” değeri gerçek LLM faturası veya fabrika maliyeti değildi; metin uzunluğundan yapılan proje içi bir tahmindi. Kayıtlı raporda doğru dokümanların zaten ilk sırada olduğu durumlarda reranking'in sıralamayı iyileştirmediğini, daha çok metin miktarını azalttığını gördüm.
Testlerde yeniden sıralama, top-k/top-n davranışı ve basit maliyet/uzunluk hesabı kontrol edildi. Kullanılan kodun gerçek kurumsal dokümanlar üzerinde doğrulanmadığını günlüğümde belirttim. Testlerde üçüncü sıradaki doğru adayın birinci sıraya taşındığı kontrollü örnek bulunması, reranking mantığını küçük ve anlaşılır bir senaryoda doğrulamama yardımcı oldu.
Otuz dördüncü gün sonunda iki aşamalı arama fikrini öğrenmiş oldum. Gerçek kullanımda yeniden sıralama modelinin ayrıca seçilmesi, gerçek soru setinde ölçülmesi ve ek gecikmenin sağladığı kalite artışına değip değmediğinin incelenmesi gerekir. Bu gün her ek model veya aşamanın gerçekten fayda sağlayıp sağlamadığının ölçülmesi gerektiğini, yalnızca mimariyi karmaşıklaştırmanın yeterli olmadığını öğrendim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 35 — 29 AĞUSTOS 2026
**KISIM:** Query Rewrite, Multi-Query ve HyDE  
**YAPRAK NO:** 69  
**YAPILAN İŞ:** Günlük dilde yazılmış sentetik soruların teknik terimlerle düzenlenmesi  
**TARİH:** 29/08/2026

Otuz beşinci gün kullanıcının teknik bir soruyu her zaman dokümandaki ifadelerle yazmayabileceği problemine odaklandım. Proje için Türkçe karakter eksikleri, kısa ifadeler ve günlük konuşma biçimleri içeren sentetik sorular hazırladım. Bu sorular gerçek Merinos çalışanlarından toplanmadı. Noisy query dosyasındaki yazım hatalı ve günlük dildeki soruları tek tek okuyarak teknik doküman diliyle kullanıcı dili arasındaki farkı önce örnekler üzerinden anlamaya çalıştım.
`query_rewriter.py` içinde bazı gündelik kelimeleri daha teknik ifadelerle ilişkilendiren küçük bir sözlük kullandım. Örneğin sıcaklık veya arıza ile ilgili kısa bir ifade, aramada kullanılabilecek ek teknik kelimelerle genişletilebiliyordu. Query rewriter içinde kullanılan sözlüğün hangi ifadeyi hangi teknik kelimeyle genişlettiğini kontrol ederek kural tabanlı dönüşümün avantaj ve sınırlamalarını gördüm.
`multi_query_expander.py` ile aynı sorudan birkaç alternatif sorgu oluşturmayı denedim. Bir sorgu belirtiye, diğeri hata kodu veya teknik değere, başka biri ise bakım eylemine odaklanabiliyordu. Sonuçların tek bir ifadeye bağımlı kalmamasını amaçladım. Multi-query yaklaşımında aynı sorunun belirti, hata kodu ve müdahale odaklı farklı sürümlerinin oluşturulması, aramanın tek ifadeye bağımlılığını azaltmayı amaçlıyordu.
HyDE olarak adlandırılan bölümde ise gerçek bir dil modeli zorunlu olmadan, hazır şablonlar kullanılarak teknik belgeye benzeyen örnek bir paragraf üretiliyordu. Bu metni gerçek bakım talimatı olarak değil, aramaya yardımcı sentetik bir temsil olarak değerlendirdim. Sorular gerçek operatörlerden toplanmadığı için bu dönüşümlerin sahadaki kullanıcı dilini temsil ettiğini iddia etmedim.

RAG akışını değerlendirirken retrieval ile generation aşamalarını birbirinden ayırmanın önemli olduğunu gördüm. Doğru bilgi parçası bulunmadığında dil modelinden güvenilir cevap beklemenin doğru olmayacağını; buna karşılık doğru parça getirildiği hâlde cevabın kaynaktan uzaklaşmasının ayrı bir generation problemi olduğunu fark ettim. Bu nedenle her denemede önce bulunan parçaları okuyup sorguyla ilişkisini kontrol ettim, ardından cevap içindeki önemli ifadelerin gerçekten verilen context içinde bulunup bulunmadığını karşılaştırdım. Böylece tek bir “cevap doğru/yanlış” değerlendirmesi yerine hata kaynağını daha ayrıntılı inceleyebildim.

**KONTROL SONUCU:**

---

## GÜN 35 — DEVAM
**KISIM:** Query Rewrite, Multi-Query ve HyDE  
**YAPRAK NO:** 70  
**YAPILAN İŞ:** Rewrite, multi-query ve HyDE benzeri yöntemlerin sentetik benchmark üzerinde incelenmesi  
**TARİH:** 29/08/2026

Günün devamında orijinal soru, rewrite edilmiş soru, multi-query ve HyDE benzeri sorguların sonuçlarını karşılaştırdım. Bazı sentetik sorularda teknik terim eklemek beklenen dokümanı üst sıraya taşırken bazı sorularda sonucu kötüleştirebildi. HyDE bölümünde örnek teknik paragrafın hazır şablonlarla oluşturulduğunu koddan doğrulayarak bunu canlı bir dil modeli çıktısı gibi anlatmadım.
Bu durum bana sorguyu her zaman otomatik değiştirmek yerine orijinal ifadeyi de korumanın yararlı olabileceğini gösterdi. Kullanıcının gerçekten ne demek istediğini aşırı dönüştürmeyle kaybetmemek gerektiğini not ettim. Farklı dönüşüm yöntemlerinin aynı soruda farklı dokümanları öne çıkarabildiğini gözlemleyerek dönüşümün her zaman iyileştirme sağlamadığını gördüm.
Testlerde sorgu dönüştürme fonksiyonlarının boş metinde davranışı, alternatif sorgu sayısı ve birleşik sonuç yapısı kontrol edildi. Benchmark değerlerinin gerçek operatör davranışını temsil etmediğini özellikle belirttim. Özellikle bazı sorularda orijinal ifadenin daha iyi sonuç verdiğini görmek, otomatik yeniden yazmanın ölçülmeden zorunlu hale getirilmemesi gerektiğini gösterdi.
Otuz beşinci gün sonunda kullanıcı dili ile doküman dili arasındaki farkı azaltmak için basit yöntemler öğrenmiş oldum. Gerçek kullanım için önce gerçek soru örneklerinin anonim ve izinli biçimde toplanması, ardından bu dönüşümlerin gerçekten fayda sağlayıp sağlamadığının ölçülmesi gerekir. Günün sonunda sorgu dönüşümünü arama öncesi yardımcı bir katman olarak değerlendirdim ve gerçek kullanıcı verisiyle ayrıca test edilmesi gerektiğini not ettim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 36 — 31 AĞUSTOS 2026
**KISIM:** Yapılandırılmış ve Grounded Cevap  
**YAPRAK NO:** 71  
**YAPILAN İŞ:** Sentetik teknik dokümanlardan düzenli cevap alanlarının hazırlanması  
**TARİH:** 31/08/2026

Otuz altıncı gün bulunan metni uzun bir paragraf olarak vermek yerine daha düzenli bir cevap yapısı hazırlamayı çalıştım. `prompt_builder.py` içinde soru, kaynaklar ve cevap kurallarının ayrı bölümlerde tutulduğunu gördüm. Bu şablon gerçek kurumsal talimat değil, proje için oluşturulmuş bir cevap formatıydı. Prompt builder dosyasında sistem talimatı, kullanıcı sorusu ve kaynak parçalarının ayrı bölümlerde tutulmasının çıktıyı daha düzenli hale getirdiğini gördüm.
`structured_generator.py` içinde doğrudan cevap, işlem adımları, teknik değerler ve kaynaklar gibi alanların ayrı tutulmasını inceledim. Kaynak metinde yeterli eşleşme varsa ilgili cümleler seçiliyor, bilgi yoksa cevap üretmek yerine bunu belirten bir sonuç dönüyordu. Structured generator'ın serbest bir dil modeli yerine kaynak cümlelerini seçip alanlara yerleştirdiğini kod üzerinden doğruladım.
Kullanılan bakım, kalite ve dokuma içerikleri yine sentetikti. Gerçek bakım kılavuzları bana verilmediği için kod içindeki sayı ve hata kodlarını işletmenin gerçek limitleri gibi kullanmadım. Doğrudan cevap, işlem adımı, teknik değer ve kaynak alanlarını ayırmak, uzun bir paragraf yerine daha kolay kontrol edilebilir çıktı üretmenin bir yolu oldu.
Bu gün yapılandırılmış çıktının kullanıcı arayüzünde daha kolay gösterilebileceğini fark ettim. Ayrıca her alanın ayrı olması, sonradan kaynak kontrolü veya güvenlik filtresi uygulamayı da kolaylaştırıyordu. Bu yanıtların gerçek bakım talimatı olmadığını; örnek dokümanlardan derlenen proje çıktıları olduğunu özellikle korudum.

RAG akışını değerlendirirken retrieval ile generation aşamalarını birbirinden ayırmanın önemli olduğunu gördüm. Doğru bilgi parçası bulunmadığında dil modelinden güvenilir cevap beklemenin doğru olmayacağını; buna karşılık doğru parça getirildiği hâlde cevabın kaynaktan uzaklaşmasının ayrı bir generation problemi olduğunu fark ettim. Bu nedenle her denemede önce bulunan parçaları okuyup sorguyla ilişkisini kontrol ettim, ardından cevap içindeki önemli ifadelerin gerçekten verilen context içinde bulunup bulunmadığını karşılaştırdım. Böylece tek bir “cevap doğru/yanlış” değerlendirmesi yerine hata kaynağını daha ayrıntılı inceleyebildim.

**KONTROL SONUCU:**

---

## GÜN 36 — DEVAM
**KISIM:** Yapılandırılmış ve Grounded Cevap  
**YAPRAK NO:** 72  
**YAPILAN İŞ:** Groundedness benzeri basit kontroller ve bilgi bulunmayan soruların incelenmesi  
**TARİH:** 31/08/2026

Günün devamında `groundedness_checker.py` ile cevap cümlelerini kaynak metinlerle karşılaştırdım. Kelime örtüşmesi, hata kodu ve sayısal değerlerin kaynakta bulunup bulunmadığına bakarak basit bir kontrol puanı üretildi. Groundedness checker içinde sayı ve hata kodu gibi ifadelerin kaynakta geçip geçmediğinin ayrıca kontrol edilmesini inceleyerek kritik değerlerin neden özel ele alınabileceğini gördüm.
Bu puanın gerçek doğruluk garantisi olmadığını gördüm. Bir cümle aynı kelimeleri kullanıp yine de yanlış anlam taşıyabilir. Bu nedenle özellikle güvenlik veya bakım konularında otomatik kontrolün uzman incelemesinin yerine geçemeyeceğini not ettim. Kapsam dışı sorularda fallback mesajı verilmesi, sistemin bilmediği konuda tahmin üretmemesi için basit bir güvenlik davranışı sağladı.
Kapsam dışı birkaç sentetik soruda sistemin “yeterli bilgi yok” cevabı vermesini denedim. Bu davranışın bilinmeyen bilgiyi uydurmaktan daha güvenli olduğunu düşündüm. Değerlendirme raporunda yüksek görünen oranları örnek cevaplarla birlikte okuyarak kelime örtüşmesinin teknik doğrulukla aynı olmadığını tekrar fark ettim.
Otuz altıncı gün sonunda yapılandırılmış cevap ve kaynak kontrolü kavramlarını öğrendim. Gerçek dokümanlara geçildiğinde prompt, eşik ve kontrol kurallarının kurumun onayladığı içerik ve kullanım amacıyla yeniden tasarlanması gerekir. Bu gün yapılandırılmış çıktı ve kaynak kontrolünün, daha sonra API arayüzünde sonuçları kullanıcıya düzenli göstermeyi de kolaylaştıracağını öğrendim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 37 — 1 EYLÜL 2026
**KISIM:** RAG Değerlendirmesi ve Guardrail  
**YAPRAK NO:** 73  
**YAPILAN İŞ:** Sentetik soru-cevap örneklerinin metrik ve kural tabanlı kontrollerle incelenmesi  
**TARİH:** 01/09/2026

Otuz yedinci gün soru-cevap sisteminin hem içerik kalitesi hem de güvenlik açısından nasıl kontrol edilebileceğini çalıştım. Proje için normal teknik sorular, kapsam dışı sorular ve tehlikeli müdahale talebini temsil eden sentetik örnekler hazırladım. Ragas evaluator içinde retrieval ve generation tarafını ayrı metriklerle değerlendirmek, hatanın arama mı yoksa cevap oluşturma aşamasında mı olduğunu ayırt etmeye yardımcı oldu.
`ragas_evaluator.py` içinde getirilen dokümanların soruyla ilişkisi, cevabın kaynakla örtüşmesi ve cevabın soruyla ilgili olması gibi basit ölçümleri inceledim. Bunlar gerçek RAGAS servisinin veya insan uzman değerlendirmesinin birebir karşılığı değildi; proje içi kontrol mantığıydı. Örnek sorulardaki cevapları tek tek açtığımda bazı yüksek puanlı sonuçlarda hata kodlarının karışabildiğini görerek otomatik metriğin insan kontrolünün yerini tutmadığını fark ettim.
`safety_guardrails.py` dosyasında belirli tehlikeli ifadeleri engelleyen bir kelime/kural listesi bulunuyordu. Örneğin acil durdurma sistemini devre dışı bırakma gibi bir ifade görülürse normal cevap akışı durdurulabiliyordu. Safety guardrails içinde belirli tehlikeli ifadelerin doğrudan eşleştirilmesi, basit ama açıklanabilir bir ilk kontrol mekanizması sağladı.
Bu kuralları Merinos’un resmi İSG prosedürü olarak kabul etmedim. Bana şirketin gerçek güvenlik prosedür dokümanları verilmedi. Kurallar yalnızca yazılımda bir güvenlik filtresinin nerede ve nasıl uygulanabileceğini öğrenmek amacıyla hazırlandı. Bu kurallar Merinos'un resmi İSG prosedürlerinden alınmadığı için yalnızca proje kapsamında güvenlik filtresi örneği olarak değerlendirildi.

RAG akışını değerlendirirken retrieval ile generation aşamalarını birbirinden ayırmanın önemli olduğunu gördüm. Doğru bilgi parçası bulunmadığında dil modelinden güvenilir cevap beklemenin doğru olmayacağını; buna karşılık doğru parça getirildiği hâlde cevabın kaynaktan uzaklaşmasının ayrı bir generation problemi olduğunu fark ettim. Bu nedenle her denemede önce bulunan parçaları okuyup sorguyla ilişkisini kontrol ettim, ardından cevap içindeki önemli ifadelerin gerçekten verilen context içinde bulunup bulunmadığını karşılaştırdım. Böylece tek bir “cevap doğru/yanlış” değerlendirmesi yerine hata kaynağını daha ayrıntılı inceleyebildim.

**KONTROL SONUCU:**

---

## GÜN 37 — DEVAM
**KISIM:** RAG Değerlendirmesi ve Guardrail  
**YAPRAK NO:** 74  
**YAPILAN İŞ:** Örnek tehlikeli taleplerin filtrelenmesi ve sonuçların değerlendirilmesi  
**TARİH:** 01/09/2026

Günün devamında giriş kontrolü, doküman arama, cevap hazırlama ve çıkış kontrolünü tek akışta birleştiren `pipeline_guard.py` dosyasını inceledim. Bir soru daha başta riskli bulunursa gereksiz diğer işlemleri çalıştırmadan engellenebildiğini gördüm. Sayısal eşik kontrolünde yapılandırma dosyasındaki sınırın üzerinde değer görüldüğünde uyarı üretilmesini inceleyerek metin dışındaki basit parametre kontrollerini de gördüm.
Kayıtlı değerlendirme panelinde bazı soruların engellendiğini, bazılarının normal işleme devam ettiğini gördüm. Yüksek otomatik puanların her zaman doğru teknik cevap anlamına gelmediğini özellikle fark ettim; bazı yanlış içerikler de basit metriklerden yüksek puan alabiliyordu. Input ve output kontrolünü ayrı düşünmek, hem tehlikeli isteği erken engelleme hem de üretilmiş cevabı sonradan denetleme fikrini anlamamı sağladı.
Testlerde normal soru, tehlikeli ifade ve kaynakla yeterince örtüşmeyen cevap gibi durumları kontrol ettim. Bu testler şirket güvenlik onayı değil, yalnızca proje kodunun tanımlanan kurallara göre davranmasını gösteriyordu. Testlerde güvenli bir sorunun yanlışlıkla engellenmemesi kadar tehlikeli örneğin de atlanmaması gerektiğini gördüm; bu iki hata türünün farklı sonuçları olabileceğini not ettim.
Otuz yedinci gün sonunda güvenlik filtresinin bir yazılım katmanı olarak yararlı olabileceğini ancak gerçek üretim kullanımında İSG, bakım ve hukuk birimlerinin onayladığı kurallar olmadan güvenilir sayılamayacağını öğrendim. Günün sonunda güvenlik filtresinin gerçek uygulamada uzman kuralları, kayıt mekanizması ve insan onayıyla birlikte tasarlanması gerektiğini öğrendim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

Kaynaklı cevap üretiminde “bilgi yok” durumunu da normal bir sistem davranışı olarak ele aldım. Örnek dokümanlarda bulunmayan bir bilgi için kesin bir cevap üretmek yerine yetersiz bağlamı açıkça belirtmenin daha güvenilir olduğunu gördüm. Kaynak kimliklerini cevapla birlikte taşımak, kullanıcının verilen bilginin hangi parçaya dayandığını kontrol edebilmesini sağlıyordu. Gerçek kurumsal kullanımda yetkilendirme, hassas veri sınıflandırması ve erişim politikalarının ayrıca tanımlanması gerektiğini; bu staj çalışmasının yalnız yerel ve sentetik bir PoC olduğunu not ettim.

**KONTROL SONUCU:**

---

## GÜN 38 — 2 EYLÜL 2026
**KISIM:** Yerel API Servisi ve Basit Arayüz  
**YAPRAK NO:** 75  
**YAPILAN İŞ:** Sentetik doküman soru-cevap akışının FastAPI ile erişilebilir hale getirilmesi  
**TARİH:** 02/09/2026

Otuz sekizinci gün önceki günlerde yazdığım Python fonksiyonlarını yalnız komut satırından çağırmak yerine bir servis üzerinden kullanmayı çalıştım. FastAPI ile yerel bilgisayarımda çalışan küçük bir API oluşturdum. Bu servis gerçek fabrika ağına veya kurumsal sunucuya dağıtılmadı. FastAPI uygulamasındaki endpoint'leri okuyarak kullanıcıdan gelen bir HTTP isteğinin Pydantic modeliyle doğrulanıp servis sınıfına nasıl aktarıldığını adım adım takip ettim.
`app.py` içinde sağlık kontrolü, örnek sorgu gönderme ve bazı sabit bilgileri döndürme uç noktalarını inceledim. `service.py` dosyasında ise sentetik doküman arama, cevap oluşturma ve guardrail adımları tek sınıf altında çağrılıyordu. Health ve query gibi uç noktaların farklı sorumluluklar taşımasını inceleyerek API'nin tek büyük fonksiyon yerine küçük görevler halinde tasarlanmasının yararını gördüm.
Örnek tezgâh kodu ve vardiya gibi alanlar yapılandırma dosyasında bulunuyordu. Bunlar canlı SCADA veya üretim sisteminden okunmadı; yalnızca API isteğinin nasıl bir metadata taşıyabileceğini göstermek için sentetik olarak tanımlandı. Servis sınıfında önce güvenlik kontrolü, sonra arama ve cevap hazırlama adımlarının sırayla çağrıldığını gözlemledim.
Bu aşamada özellikle “API var = üretime hazır” şeklinde düşünmemek gerektiğini öğrendim. Kimlik doğrulama, yetkilendirme, loglama, ağ politikaları ve kurumsal entegrasyon gibi konular gerçek kullanımdan önce ayrıca ele alınmalıdır. Uygulamanın hiçbir SCADA, PLC veya kurum içi ağa bağlı olmadığını; bütün veri kaynaklarının proje içindeki örnek dosyalardan geldiğini korudum.

Servis ve optimizasyon aşamasında yerel deney ile gerçek üretim dağıtımını birbirinden ayırmaya dikkat ettim. Endpoint'in kendi bilgisayarımda cevap vermesi, model dosyasının küçülmesi veya CPU üzerinde belirli bir gecikme ölçülmesi sistemin fabrika ortamına hazır olduğu anlamına gelmiyordu. Gerçek kullanımda hedef donanım, ağ yapısı, eşzamanlı istek sayısı, hata toleransı, güvenlik ve bakım sorumlulukları ayrıca değerlendirilmelidir. Bu nedenle burada yaptığım ölçümleri yalnız aynı yerel ortamda farklı seçenekleri karşılaştırmaya yarayan teknik göstergeler olarak kullandım.

**KONTROL SONUCU:**

---

## GÜN 38 — DEVAM
**KISIM:** Yerel API Servisi ve Basit Arayüz  
**YAPRAK NO:** 76  
**YAPILAN İŞ:** Streamlit ekranında sentetik sorgu, sonuç ve güvenlik bilgilerinin gösterilmesi  
**TARİH:** 02/09/2026

Günün devamında Streamlit ile basit bir kullanıcı arayüzü inceledim. Kullanıcı örnek bir soru yazabiliyor, bazı sentetik seçenekleri seçebiliyor ve uygulamanın döndürdüğü cevap ile kaynak bilgilerini ekranda görebiliyordu. Streamlit arayüzünde tezgâh, vardiya ve soru alanlarının yalnızca demo amaçlı girişler olduğunu, gerçek operasyon kayıtlarıyla eşleşmediğini not ettim.
Arayüzde güvenlik nedeniyle engellenen örnek bir sorunun normal cevap yerine uyarı göstermesini de test ettim. Bu davranış tamamen yerel kod ve sentetik kurallara dayanıyordu; gerçek operatör veya iş güvenliği sistemine bağlı değildi. Arayüzde yanıt, kaynak ve güvenlik sonucunun ayrı bölümlerde gösterilmesi, arka plandaki veri yapısının kullanıcıya nasıl sunulabileceğini görmemi sağladı.
Test dosyasında API’nin ayakta olması, hatalı girişte uygun cevap dönmesi ve örnek servis akışının çalışması gibi durumlar kontrol edildi. Kayıtlı gecikme değerlerini kendi bilgisayar ortamına ait demo ölçümü olarak değerlendirdim. Testlerde endpoint durum kodları, geçersiz girişler ve güvenlik nedeniyle engellenen örnekler kontrol edilerek web katmanının da ayrıca test edilmesi gerektiğini gördüm.
Otuz sekizinci gün sonunda Python uygulamasını API ve basit arayüz üzerinden sunmanın temelini öğrendim. Gerçek işletme kullanımında önce hangi kullanıcıların erişeceği, hangi ağa kurulacağı ve hangi verilerin gösterilebileceği Bilgi İşlem tarafından ayrıca belirlenmelidir. Bu gün kodun çalışmasını bir web arayüzüne taşımayı öğrendim; gerçek kurumsal entegrasyon için kimlik doğrulama, ağ güvenliği ve yetkilendirme gibi ek katmanların gerekeceğini not ettim.

Aynı şekilde performans iyileştirmesini yalnız hız veya dosya boyutuyla değerlendirmedim. Bir dönüşümden sonra çıktıların referansla yeterince tutarlı kalıp kalmadığını, hata durumlarının kontrollü ele alınıp alınmadığını ve testlerin tekrar çalıştırılabildiğini de kontrol ettim. Bu yaklaşım staj boyunca tekrar eden temel düşünceyi güçlendirdi: bir yöntemin çalışması kadar, hangi koşullarda çalıştığının ve sınırlarının açık biçimde bilinmesi de önemlidir. Son değerlendirmelerde gerçek fabrika verisi veya canlı sistem erişimi olmadığı için tüm sonuçları öğrenme ve PoC kapsamıyla sınırlı tuttum.

Aynı şekilde performans iyileştirmesini yalnız hız veya dosya boyutuyla değerlendirmedim. Bir dönüşümden sonra çıktıların referansla yeterince tutarlı kalıp kalmadığını, hata durumlarının kontrollü ele alınıp alınmadığını ve testlerin tekrar çalıştırılabildiğini de kontrol ettim. Bu yaklaşım staj boyunca tekrar eden temel düşünceyi güçlendirdi: bir yöntemin çalışması kadar, hangi koşullarda çalıştığının ve sınırlarının açık biçimde bilinmesi de önemlidir. Son değerlendirmelerde gerçek fabrika verisi veya canlı sistem erişimi olmadığı için tüm sonuçları öğrenme ve PoC kapsamıyla sınırlı tuttum.

**KONTROL SONUCU:**

---

## GÜN 39 — 3 EYLÜL 2026
**KISIM:** ONNX, Kuantizasyon ve Yerel Benchmark  
**YAPRAK NO:** 77  
**YAPILAN İŞ:** Küçük örnek sinir ağlarının ONNX formatına çevrilmesi ve INT8 ile küçültülmesi  
**TARİH:** 03/09/2026

Otuz dokuzuncu gün modellerin daha düşük kaynak kullanan ortamlarda nasıl çalıştırılabileceğini anlamak için ONNX ve kuantizasyon konularını çalıştım. Repo içinde bu gün için iki küçük PyTorch ağı tanımlanmıştı. Bunlar gerçek üretimde kullanılan eğitilmiş modeller değil, dönüşüm sürecini öğrenmek için hazırlanmış örnek ağlardı. ONNX export işleminde giriş ve çıkış isimlerinin açık biçimde tanımlandığını inceleyerek model dosyasının başka bir çalışma motoru tarafından nasıl okunabildiğini anlamaya çalıştım.
`onnx_exporter.py` ile bu ağları ONNX formatına çevirdim ve oluşturulan grafiği ONNX checker ile doğruladım. ONNX formatının farklı çalışma ortamlarında modeli daha taşınabilir hale getirebildiğini öğrendim. FP32 model dosyasını INT8'e çevirdikten sonra dosya boyutlarını bayt ve MB cinsinden karşılaştırarak sıkıştırma oranını doğrudan dosya üzerinden kontrol ettim.
Daha sonra `quantizer.py` ile FP32 ağırlıkları dinamik INT8 biçimine dönüştürdüm. Kayıtlı örneklerde model dosya boyutunun yaklaşık dörtte bire yakın küçülebildiğini gördüm. Bu sonuç yalnızca bu küçük örnek ağlara aitti. Kuantizasyonun yalnızca dosyayı küçültmek değil, sayısal hassasiyeti değiştirmek anlamına geldiğini ve bu nedenle çıktıların ayrıca karşılaştırılması gerektiğini öğrendim.
Bu gün de gerçek edge bilgisayarına, PLC’ye veya tezgâh başı cihaza kurulum yapmadım. Tüm işlemler kendi geliştirme bilgisayarımda ve sentetik sayısal girişlerle gerçekleşti. Kullanılan modeller küçük örnek ağlardı ve gerçek bir üretim modelinin tezgâh başı cihazda çalıştırıldığı anlamına gelmiyordu.

Servis ve optimizasyon aşamasında yerel deney ile gerçek üretim dağıtımını birbirinden ayırmaya dikkat ettim. Endpoint'in kendi bilgisayarımda cevap vermesi, model dosyasının küçülmesi veya CPU üzerinde belirli bir gecikme ölçülmesi sistemin fabrika ortamına hazır olduğu anlamına gelmiyordu. Gerçek kullanımda hedef donanım, ağ yapısı, eşzamanlı istek sayısı, hata toleransı, güvenlik ve bakım sorumlulukları ayrıca değerlendirilmelidir. Bu nedenle burada yaptığım ölçümleri yalnız aynı yerel ortamda farklı seçenekleri karşılaştırmaya yarayan teknik göstergeler olarak kullandım.

**KONTROL SONUCU:**

---

## GÜN 39 — DEVAM
**KISIM:** ONNX, Kuantizasyon ve Yerel Benchmark  
**YAPRAK NO:** 78  
**YAPILAN İŞ:** ONNX Runtime ile sentetik girdiler üzerinde gecikme ve dosya boyutu karşılaştırması  
**TARİH:** 03/09/2026

Günün devamında ONNX Runtime ile FP32 ve INT8 modelleri CPU üzerinde birkaç kez çalıştırıp gecikme değerlerini kaydettim. Dosya boyutunun küçülmesinin her zaman daha hızlı çalışma anlamına gelmediğini; örnek ölçümlerde bazı INT8 çalıştırmaların FP32’den daha yavaş olabildiğini gördüm. ONNX Runtime ile farklı thread sayılarında yapılan ölçümleri inceleyerek daha fazla thread'in her zaman doğrusal hızlanma sağlamadığını gözlemledim.
Farklı CPU thread sayılarıyla kısa denemeler yaptım. Bu ölçümler bilgisayarın yüküne ve donanımına bağlı olduğu için gerçek endüstriyel IPC performansı olarak değerlendirilmedi. Benchmark raporunda FP32 ONNX sürümünün bazı ölçümlerde INT8'den daha hızlı görünmesi, model küçültmenin otomatik olarak hız artışı anlamına gelmediğini açık biçimde gösterdi.
Kuantizasyon sonrası çıktıların referansla benzerliğini hesaplayan kodu da inceledim. Kayıtlı rapordaki bazı karşılaştırmalar farklı rastgele ağırlıklarla üretildiği için bunları gerçek doğruluk kaybı olarak yorumlamanın doğru olmayacağını not ettim. Accuracy preservation testinde referans ve kuantize çıktıların karşılaştırılmasını inceleyerek performans ile sayısal tutarlılığın birlikte ölçülmesi gerektiğini gördüm.
Otuz dokuzuncu gün sonunda ONNX, Runtime ve INT8 kuantizasyon kavramlarını uygulamalı olarak gördüm. Gerçek bir edge dağıtımı düşünülürse hedef cihazın seçilmesi, aynı model ağırlıklarının kullanılması ve cihaz üzerinde yeniden performans/doğruluk testi yapılması gerekir. Günün sonunda bu çalışmayı gerçek edge deployment değil, ileride düşük kaynaklı bir cihaz hedeflenirse kullanılabilecek dönüşüm ve ölçüm tekniklerinin yerel denemesi olarak değerlendirdim.

Aynı şekilde performans iyileştirmesini yalnız hız veya dosya boyutuyla değerlendirmedim. Bir dönüşümden sonra çıktıların referansla yeterince tutarlı kalıp kalmadığını, hata durumlarının kontrollü ele alınıp alınmadığını ve testlerin tekrar çalıştırılabildiğini de kontrol ettim. Bu yaklaşım staj boyunca tekrar eden temel düşünceyi güçlendirdi: bir yöntemin çalışması kadar, hangi koşullarda çalıştığının ve sınırlarının açık biçimde bilinmesi de önemlidir. Son değerlendirmelerde gerçek fabrika verisi veya canlı sistem erişimi olmadığı için tüm sonuçları öğrenme ve PoC kapsamıyla sınırlı tuttum.

Aynı şekilde performans iyileştirmesini yalnız hız veya dosya boyutuyla değerlendirmedim. Bir dönüşümden sonra çıktıların referansla yeterince tutarlı kalıp kalmadığını, hata durumlarının kontrollü ele alınıp alınmadığını ve testlerin tekrar çalıştırılabildiğini de kontrol ettim. Bu yaklaşım staj boyunca tekrar eden temel düşünceyi güçlendirdi: bir yöntemin çalışması kadar, hangi koşullarda çalıştığının ve sınırlarının açık biçimde bilinmesi de önemlidir. Son değerlendirmelerde gerçek fabrika verisi veya canlı sistem erişimi olmadığı için tüm sonuçları öğrenme ve PoC kapsamıyla sınırlı tuttum.

**KONTROL SONUCU:**

---

## GÜN 40 — 4 EYLÜL 2026
**KISIM:** Final Test, Dokümantasyon ve Staj Değerlendirmesi  
**YAPRAK NO:** 79  
**YAPILAN İŞ:** Geliştirilen örnek modüllerin, testlerin ve öğrenme çıktılarının gözden geçirilmesi  
**TARİH:** 04/09/2026

Kırkıncı ve son gün staj boyunca yaptığım çalışmaları baştan sona gözden geçirdim. Bu stajın ana çalışma alanı Bilgi İşlem / Yazılım Departmanıydı. Üretim alanını yalnız kısa bir tanıma gezisinde gördüm; günlük çalışmalarımı benimle ilgilenen yazılım mühendisinin yönlendirmeleriyle bilgisayar başında yürüttüm. Son gün repo içindeki farklı günleri tekrar açarak görüntü işleme, makine öğrenmesi, retrieval, RAG, API ve ONNX çalışmalarının birbirinden nasıl devam ettiğini kronolojik olarak gözden geçirdim.
İlk haftalardaki Python, veri modeli ve veri kalitesi çalışmalarından başlayarak görüntü işleme, makine öğrenmesi, doküman arama, RAG, API ve model optimizasyonuna kadar farklı konuları küçük modüller halinde geliştirdim. Bu modüllerin ortak özelliği gerçek fabrika verisi yerine sentetik ve örnek veriler kullanmasıydı. Master platform dosyasındaki dört sütunun gerçek çalışan alt sistemler yerine önceki çalışmaların kavramsal özeti olduğunu kod üzerinden fark ettim.
Staj boyunca canlı SCADA/PLC telemetrisi, kalite kontrol kamera görüntüsü, gerçek tezgâh hata logu veya kurum içi bakım PDF’i bana verilmedi. Dolayısıyla repo içinde bu tür verileri temsil eden dosyalar gerçek kayıt değil, yazılım akışlarını test etmek için oluşturulmuş örneklerdi. Sentetik telemetri ve görsel kusur alanlarını tek bir örnek olay yapısında birleştirmek, farklı veri türlerinin gelecekte aynı serviste nasıl toplanabileceğini düşünmemi sağladı.
Son gün `master_platform.py` ve `final_evaluator.py` gibi kapanış dosyalarını incelerken repo içindeki bazı büyük iddiaları da ayırdım. Kodda tanımlı “sağlıklı sistem”, üretime hazır olma, tezgâh sayısı veya ekonomik kazanım gibi değerlerin gerçek fabrika ölçümü olmadığını açıkça not ettim. Bu senaryoyu canlı fabrika teşhisi olarak değil, modüllerin birlikte nasıl çağrılabileceğini gösteren bir PoC kapanış örneği olarak değerlendirdim.

Servis ve optimizasyon aşamasında yerel deney ile gerçek üretim dağıtımını birbirinden ayırmaya dikkat ettim. Endpoint'in kendi bilgisayarımda cevap vermesi, model dosyasının küçülmesi veya CPU üzerinde belirli bir gecikme ölçülmesi sistemin fabrika ortamına hazır olduğu anlamına gelmiyordu. Gerçek kullanımda hedef donanım, ağ yapısı, eşzamanlı istek sayısı, hata toleransı, güvenlik ve bakım sorumlulukları ayrıca değerlendirilmelidir. Bu nedenle burada yaptığım ölçümleri yalnız aynı yerel ortamda farklı seçenekleri karşılaştırmaya yarayan teknik göstergeler olarak kullandım.

**KONTROL SONUCU:**

---

## GÜN 40 — DEVAM
**KISIM:** Final Test, Dokümantasyon ve Staj Değerlendirmesi  
**YAPRAK NO:** 80  
**YAPILAN İŞ:** Sentetik çalışma sınırlarının belirlenmesi ve olası pilot kullanım adımlarının yazılması  
**TARİH:** 04/09/2026

Günün devamında çalışmayı “hemen fabrikaya kurulabilecek ürün” olarak değil, ileride gerçek veri erişimi sağlanırsa geliştirilebilecek bir Ar-Ge / PoC altyapısı olarak değerlendirdim. Gerçek kullanım için önce kurumun hangi problemi çözmek istediğinin ve hangi veri kaynağının kullanılacağının netleştirilmesi gerektiğini yazdım. Final evaluator içindeki tezgâh sayısı, maliyet ve tasarruf değerlerinin kodda sabit varsayımlar olduğunu gördüğüm için bunları gerçek Merinos KPI'ı olarak kullanmamaya karar verdim.
Sonraki aşamada veri erişim izinleri belirlenmeli, gerçek veri şemaları incelenmeli ve sentetik veriyle yazılmış modüller bu yapıya uyarlanmalıdır. İlk doğrulamanın geçmiş veriler üzerinde yapılması, daha sonra sistemin yalnız öneri ürettiği “gölge mod” bir pilotla denenmesi bana en mantıklı geçiş yolu olarak göründü. Kapanışta gerçek veriye geçiş için önce izin, veri şeması, geçmiş veri doğrulaması ve gölge mod pilotu gerektiğini not ederek projenin sonraki aşamasını daha gerçekçi biçimde tanımladım.
Pilot sonucunda bakım, kalite, üretim, iş güvenliği ve Bilgi İşlem tarafındaki sorumlu kişiler sonuçları birlikte değerlendirmeden sistemin üretim kararına bağlanmaması gerektiği sonucuna vardım. Başarılı ve güvenli olduğu görülürse ancak bundan sonra sınırlı bir alanda kademeli kullanım düşünülebilir. Sekiz final testi, kapanış kodunun beklenen sentetik senaryolarda çalıştığını kontrol ediyordu; bunların fabrika sistemlerinin tamamının doğrulandığı anlamına gelmediğini özellikle ayırdım.
Kırk günlük stajın sonunda en önemli kazanımım, bir yapay zekâ projesinde yalnız algoritmanın değil veri kaynağının, testin, hata yönetiminin, dokümantasyonun ve kullanım sınırlarının da önemli olduğunu görmek oldu. Sentetik verilerle hazırladığım bu proje, gerçek veriye geçildiğinde yeniden doğrulanması gereken bir öğrenme ve PoC çalışması olarak tamamlandı. Stajın sonunda asıl kazanımımın belirli bir ürünü canlıya almak değil, yazılım mühendisinin yönlendirmesiyle farklı yapay zekâ ve yazılım bileşenlerini küçük, test edilebilir örnekler halinde geliştirmeyi öğrenmek olduğunu değerlendirdim.

Aynı şekilde performans iyileştirmesini yalnız hız veya dosya boyutuyla değerlendirmedim. Bir dönüşümden sonra çıktıların referansla yeterince tutarlı kalıp kalmadığını, hata durumlarının kontrollü ele alınıp alınmadığını ve testlerin tekrar çalıştırılabildiğini de kontrol ettim. Bu yaklaşım staj boyunca tekrar eden temel düşünceyi güçlendirdi: bir yöntemin çalışması kadar, hangi koşullarda çalıştığının ve sınırlarının açık biçimde bilinmesi de önemlidir. Son değerlendirmelerde gerçek fabrika verisi veya canlı sistem erişimi olmadığı için tüm sonuçları öğrenme ve PoC kapsamıyla sınırlı tuttum.

**KONTROL SONUCU:**

---

# EK — YAZIM VE VERİ GERÇEKLİĞİ KONTROLÜ

- Toplam çalışma günü: **40**
- Toplam yaprak: **80**
- Her gün iki yaprağa bölünmüştür: **GÜN / GÜN — DEVAM**
- Gerçek SCADA/PLC bağlantısı: **Yok**
- Gerçek sensör telemetrisi: **Yok**
- Gerçek tezgâh hata logu: **Yok**
- Kurum içi bakım dokümanı/veritabanı kullanımı: **Yok**
- Kullanılan örnekler: **sentetik, çalışma amacıyla hazırlanmış veya izinli veriler**
- Teknik sonuçların kapsamı: **öğrenme, yerel deney ve PoC**
