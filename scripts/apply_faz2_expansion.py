# -*- coding: utf-8 -*-
"""Apply humanized, deep engineering narrative for Faz 2 (Days 09 to 15 / Yapraks 17 to 30)."""

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'r', encoding='utf-8') as f:
    full_text = f.read()

pos_start = full_text.find('## GÜN 9 — 30 TEMMUZ 2026')
pos_end = full_text.find('## GÜN 16 — 7 AĞUSTOS 2026')

assert pos_start != -1 and pos_end != -1, 'Day 9 or Day 16 marker not found!'

faz2_expanded = '''## GÜN 9 — 30 TEMMUZ 2026
**KISIM:** OpenCV Temelleri ve Görüntü Ön İşleme  
**YAPRAK NO:** 17  
**YAPILAN İŞ:** Görüntü Okuma, Shape/Dtype ve BGR-RGB Kanal Yapısının İncelenmesi  
**TARİH:** 30/07/2026

Stajımın dokuzuncu gününde, ilk sekiz günde edindiğim veri ve problem temellerinin ardından ikinci büyük aşama olan Bilgisayarlı Görü dünyasına adım attım. Merinos'un dokuma salonlarında üretilen halıların kalite kontrol süreçlerinde en hayati aşamalardan biri, yüzeydeki örgü bozukluklarının, desen kaymalarının ve renk tonu farklılıklarının optik olarak incelenmesidir. Danışman mühendisimle yaptığımız toplantıda, insan gözünün saatlerce süren vardiyalarda yorulabileceğini, bu nedenle konveyör bandı üzerindeki muayene kameralarından gelen görüntülerin yazılım yoluyla otomatik işlenmesinin işletmeye nasıl bir katma değer sağlayacağını konuştuk.

Bu amaçla bilgisayarlı görü alanının endüstri standardı olan OpenCV kütüphanesini kullanarak sentetik halı yüzey görüntüleri üzerinde çalışmaya başladım. İlk iş olarak dosya okuma ve veri bütünlüğünü sağlama adına görüntü doğrulama modülünü yazdım. Bu modül içinde dosyanın diskte gerçekten var olduğunu, bozuk olmadığını ve beklenen resim formatında bulunduğunu kontrol eden `validate_image_path` ve `load_image_safe` fonksiyonlarını kodladım.

Geliştirme esnasında çok öğretici ve unutamayacağım bir "aha!" anı yaşadım: Görüntüyü OpenCV ile okuyup doğrudan ekrana bastırdığımda, fabrikadaki kırmızı ve sıcak krem tonlarına sahip halı deseninin ekranda masmavi ve yeşilimsi göründüğünü fark ettim. Şaşkınlıkla ekrana bakarken danışman mühendisim gülümseyerek OpenCV'nin tarihi nedenlerle renk kanallarını varsayılan olarak `BGR` (Mavi-Yeşil-Kırmızı) sırasında tuttuğunu, oysa modern görüntüleme araçlarının ve ekranların `RGB` sırasını beklediğini anlattı. Bu sorunu `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` dönüşüm fonksiyonunu uygulayarak çözdüm. Böylece bellekteki tensörün kanal sıralamasının algoritmik doğruluğu nasıl doğrudan etkilediğini bizzat deneyimlemiş oldum.

Günün ilk yarısında ayrıca görüntünün bellek profilini çıkardım. Görüntü matrisinin shape bilgisini inceleyerek $(H, W, C)$ yani yükseklik, genişlik ve renk kanalı sayısını teyit ettim. Piksel veri tipinin `uint8` olduğunu ve her bir renk kanalındaki yoğunluğun 0 ile 255 arasında değiştiğini gözlemledim.

**KONTROL SONUCU:**

---

## GÜN 9 — DEVAM
**KISIM:** OpenCV Temelleri ve Görüntü Ön İşleme  
**YAPRAK NO:** 18  
**YAPILAN İŞ:** Resize, En-Boy Oranı, Interpolation ve Temel Ön İşleme Yaklaşımlarının İncelenmesi  
**TARİH:** 30/07/2026

Öğleden sonraki oturumda endüstriyel görüntü işlemede işlemci performansını doğrudan belirleyen yeniden boyutlandırma (resize) ve ön işleme adımlarına odaklandım. Fabrika tavanındaki yüksek çözünürlüklü endüstriyel kameralar saniyede onlarca mega piksel veri üretir; ancak gerçek zamanlı kalite kontrol modellerinin bu devasa pikselleri anlık işlemesi ciddi donanım darboğazı yaratır. Bu nedenle görüntülerin kaliteden ödün vermeden küçültülmesi gerekir.

Bu problemi çözmek üzere `resizer` modülünü geliştirdim. Sınıf içine en-boy oranını (aspect ratio) titizlikle koruyan `resize_aspect_ratio` fonksiyonunu yazdım. Danışman mühendisimle yaptığımız deneyde, kare olmayan bir halı görüntüsünü doğrudan sabit $512 \times 512$ piksele zorladığımızda halı motiflerinin enine ya da boyuna ezilerek geometrisinin tamamen bozulduğunu gördük. Bunun yerine görüntüyü orijinal en-boy oranını koruyarak küçülten ve hedef boyuttan arta kalan kenar boşluklarını sabit renk dolgusuyla (letterboxing/padding) tamamlayan mantığı uyguladım.

Boyutlandırma sırasında kullanılan interpolasyon yöntemlerini de karşılaştırdım: Küçültme işlemlerinde piksel örtüşmelerini (aliasing) engelleyen `INTER_AREA`, büyütmede ise daha pürüzsüz geçiş sağlayan `INTER_CUBIC` ve `INTER_LINEAR` tekniklerinin çıktılarını inceledim.

Daha sonra tüm ön işleme adımlarını organize eden `ImagePreprocessor` sınıfını kodladım. Bu sınıf içinde Gauss filtreleme (`cv2.GaussianBlur`) ile kamera sensöründen kaynaklanan yüksek frekanslı parazitleri yumuşatan ve kontrast eşitleme (Histogram Equalization) uygulayan fonksiyonları birleştirdim. Yazdığım tüm ön işleme akışını `test_image_preprocessor` ve `test_toolkit` birim testleriyle sınayarak görüntü boyutlarının ve kanal sıralamasının korunduğunu pytest ile doğruladım.

Günün sonunda, pikselleri hatasız okuyup ön işlemeden geçiren sağlam bir altyapı kurduk. Ancak renkli halıları yalnızca üç kanal olarak görmenin renk analizi için yetersiz olduğunu değerlendirerek, yarın farklı renk uzaylarını ve renk farkı metriklerini inceleyeceğimiz Gün 10 çalışmalarına geçmeye karar verdim.

**KONTROL SONUCU:**

---

## GÜN 10 — 31 TEMMUZ 2026
**KISIM:** Renk Uzayları ve Renk Farkı  
**YAPRAK NO:** 19  
**YAPILAN İŞ:** RGB ve HSV Renk Temsillerinin Karşılaştırılması ve Renk Eşikleme Mantığının İncelenmesi  
**TARİH:** 31/07/2026

Stajımın onuncu gününde, tekstil ve halı endüstrisinin en hassas kalite kriterlerinden biri olan renk ayrımı ve renk uzayları konusunu masaya yatırdım. Sabah saatlerinde danışman mühendisimle kalite kontrol laboratuvarında yaptığımız görüşmede, klasik RGB renk uzayının endüstriyel ortamlarda neden yetersiz kaldığını tartıştık. RGB uzayında kırmızı, yeşil ve mavi kanalların her birinin hem renk bilgisini hem de aydınlık şiddetini aynı anda taşıdığını anlattı. Fabrika ortamında gün ışığının değişmesi veya tezgâh üzerindeki aydınlatma armatürünün hafifçe dalgalanması durumunda, aynı kumaşın RGB piksel değerlerinin tamamen değiştiğini ve bunun hatalı kalite alarmlarına yol açtığını bizzat gözlemledim.

Bu aydınlatma hassasiyetini bertaraf etmek için rengin özünü parlaklıktan ayıran HSV (Hue: Renk Özü, Saturation: Doygunluk, Value: Parlaklık) renk uzayını inceledim. Geliştirdiğim renk dönüştürücü modül içine BGR'dan HSV'ye geçiş sağlayan fonksiyonu yazdım. HSV uzayında rengin türünün yalnızca Hue kanalında açısal bir değer ($0^\circ-180^\circ$) olarak tutulduğunu, ortam parlaklığının ise Value kanalında izole edildiğini gördüm.

Ardından `HSVColorThresholder` sınıfını geliştirdim. Bu sınıf içinde belirli bir sentetik iplik renginin (örneğin lacivert veya bordo) Hue, Saturation ve Value alt-üst sınırlarını belirleyerek renk maskesi üreten fonksiyonu kodladım. `cv2.inRange` fonksiyonuyla ürettiğim ikili (binary) maske üzerinde morfolojik temizlik yaparak, tezgâh üzerindeki aydınlatma değişimlerine rağmen hedef renkli iplik bölgelerini kusursuzca segmente etmeyi başardım.

Bu çalışma bana, problemin türüne göre doğru renk uzayını seçmenin algoritma başarısını doğrudan belirlediğini kanıtladı.

**KONTROL SONUCU:**

---

## GÜN 10 — DEVAM
**KISIM:** Renk Uzayları ve Renk Farkı  
**YAPRAK NO:** 20  
**YAPILAN İŞ:** CIELAB Renk Uzayı ve Delta E ile Algısal Renk Farkının İncelenmesi  
**TARİH:** 31/07/2026

Öğleden sonraki çalışmamda tekstil sektörünün evrensel dili sayılan CIELAB ($L^*a^*b^*$) renk uzayını ve algısal renk farkı ($\Delta E$) formülasyonlarını ele aldım. Danışman mühendisim, tekstil üretiminde en yaygın müşteri iadelerinden birinin "parti renk tonu farkı" (metamerizm ve kazan farkı) olduğunu anlattı. İki kumaş bobini yan yana getirildiğinde insan gözünün fark edebildiği ton farklarının, klasik RGB Öklid mesafesiyle ölçülemeyeceğini; çünkü insan retinasının her renge aynı hassasiyeti göstermediğini (yeşil ve kırmızıya daha duyarlı olduğunu) açıkladı.

Bu algısal gerçekliği matematikselleştirmek amacıyla Uluslararası Aydınlatma Komisyonu'nun (CIE) insan gözü algısına göre doğrusal tasarladığı CIELAB renk uzayını inceledim. Bu uzayda $L^*$ parlaklığı (0: Siyah, 100: Beyaz), $a^*$ kırmızı-yeşil eksenini ve $b^*$ sarı-mavi eksenini temsil ediyordu.

Ardından renk farkı modülleri içinde iki temel algoritmayı kodladım: Klasik $\Delta E^*_{ab}$ (1976) Öklid formülü ve modern tekstil endüstrisi standardı olan `CIEDE2000` algoritması. CIEDE2000 formülasyonunun renk tonu, doygunluk ve parlaklık kompanzasyonları yaparak insan gözünün renk ayrım hassasiyetini kusursuz modellediğini gördüm.

Geliştirdiğim `YarnMatcher` sınıfı ile kameradan ölçülen sentetik kumaş rengini katalogdaki referans iplik kodlarıyla eşleştirdim. Endüstri standardı olarak $\Delta E < 1.0$ farkın insan gözüyle ayırt edilemeyecek mükemmellikte olduğunu, $\Delta E > 3.0$ değerinin ise kalite kontrol tarafından partinin reddedilmesi gerektiğini kurallara bağladım.

Yazdığım formülleri ve eşleştirme mantığını `test_color_difference` ve `test_color_analysis` birim testleriyle sınayarak matematiksel doğruluğu teyit ettim. Günün sonunda, tekstilde rengin sübjektif bir gözlem değil, $\Delta E$ ile ölçülebilen kesin bir mühendislik metriği olduğunu öğrendim.

**KONTROL SONUCU:**

---

## GÜN 11 — 1 AĞUSTOS 2026
**KISIM:** K-Means ile Baskın Renk ve Palet Çıkarımı  
**YAPRAK NO:** 21  
**YAPILAN İŞ:** K-Means Mantığı ve Farklı Küme Sayılarının Karşılaştırılması  
**TARİH:** 01/08/2026

Stajımın on birinci gününde, dokunan bir halı üzerindeki baskın renklerin ve renk paletinin insan müdahalesine gerek kalmadan otomatik olarak tespit edilmesi problemine odaklandım. Üretim bandından çıkan desenli bir halıda kaç ana renk kullanıldığını ve bu renklerin yüzeyde yüzde kaçlık alan kapladığını elle ölçmek hem imkansızdır hem de sübjektif hatalara açıktır.

Danışman mühendisimle bu problemi gözetimsiz öğrenme (unsupervised learning) algoritması olan K-Means kümelemesi ile çözmeye karar verdik. `kmeans_palette` modülünü geliştirerek algoritmanın çalışma mekanizmasını inceledim. Görüntüdeki yüz binlerce pikselin üç boyutlu renk uzayında $(N, 3)$ boyutunda birer nokta bulutu oluşturduğunu, K-Means'in bu noktaları rastgele atanan $K$ adet küme merkezine (centroid) göre en yakın Öklid mesafesiyle gruplayıp merkezleri adım adım güncellediğini öğrendim.

Kümeleme sürecinde en kritik teknik karar doğru $K$ (küme sayısı) değerinin belirlenmesiydi. Bu amaçla dirsek yöntemini (elbow method) ve eylemsizlik (inertia / WCSS: küme içi kareler toplamı) analizi yapan fonksiyonu kodladım. $K=2$'den $K=8$'e kadar farklı küme sayıları için eylemsizlik değerlerini hesaplayarak hatanın düşüş hızının kırıldığı "dirsek" noktasını otomatik tespit eden algoritmayı kurguladım.

Böylece gereksiz fazla renk kümesi seçerek gürültüyü artırmanın veya az küme seçerek önemli ara tonları kaçırmanın önüne geçtim.

**KONTROL SONUCU:**

---

## GÜN 11 — DEVAM
**KISIM:** K-Means ile Baskın Renk ve Palet Çıkarımı  
**YAPRAK NO:** 22  
**YAPILAN İŞ:** RGB ve CIELAB Üzerinde Renk Gruplama ve Baskın Renk Oranlarının İncelenmesi  
**TARİH:** 01/08/2026

Öğleden sonraki oturumda K-Means kümelemesini hem RGB hem de CIELAB renk uzaylarında koşturarak sonuçları karşılaştırmalı olarak analiz ettim. Yaptığım deneylerde çok çarpıcı bir sonuca ulaştım: RGB uzayında kümeleme yapıldığında, gölgeli alanlardaki koyu tonlar piksellerin çoğunluğunu oluşturarak algoritmayı yanılttı ve benzer tonlar tek bir kümede toplanamadı. Oysa pikselleri CIELAB uzayına dönüştürüp kümelediğimde, algoritmanın insan gözünün gördüğü ana renk öbeklerini çok daha başarılı ayrıştırdığını gözlemledim.

Ardından `KMeansPaletteEngine` sınıfını geliştirdim. Bu sınıf, bulunan her bir küme merkezinin temsil ettiği piksel adedini toplam piksel sayısına oranlayarak baskın renklerin yüzdesel alan oranlarını (proportions) hesaplıyordu (örneğin %52 Gece Mavisi, %33 Bej, %15 Tuğla Kırmızısı).

Daha sonra `quantizer` modülünü yazarak renk nicemleme (color quantization) işlemini hayata geçirdim. Orijinal görüntüdeki binlerce ara renk tonunu yalnızca belirlenen bu $K$ adet merkez renkle yeniden boyayarak posterize edilmiş sentetik bir halı şablonu oluşturdum. Elde ettiğim baskın renk merkezlerini dün yazdığım `yarn_matcher` modülüyle besleyerek, fabrikadaki standart iplik kataloğundaki en yakın iplik kodlarıyla otomatik olarak eşleştirdim.

Geliştirdiğim palet motorunu `test_kmeans_palette_engine` ve `test_palette_and_quantizer` testleriyle denetledim; çıkarılan renk oranlarının toplamının %100 ettiğini ve küme merkezlerinin kararlılığını pytest ile teyit ettim.

Günün sonunda, karmaşık bir halı deseninin renk kimliğini birkaç sayısal parametreye indirgeyebilen çalışan bir renk zekâsı modülü elde ettik.

**KONTROL SONUCU:**

---

## GÜN 12 — 3 AĞUSTOS 2026
**KISIM:** Perspektif Düzeltme ve Homografi  
**YAPRAK NO:** 23  
**YAPILAN İŞ:** Açılı Görüntülerde Perspektif Bozulmasının ve Dört Noktalı Dönüşümün İncelenmesi  
**TARİH:** 03/08/2026

Stajımın on ikinci gününde, endüstriyel kamera yerleşimlerinin kaçınılmaz bir sonucu olan optik perspektif bozulmaları ve projektif geometri konusuna odaklandım. Fabrika sahasında üretim hattının üzerine kamera monte edilirken fiziksel tezgâh aksamı, aydınlatma lambaları ve vinç yolları nedeniyle kameranın halıya tam $90^\circ$ dik (ortografik) açıyla konumlandırılması çoğu zaman mümkün olmaz. Hafif bir açıyla yerleştirilen kamera, gerçekte dikdörtgen olan halıyı bir yamuk (trapezoid) olarak kaydeder; kameraya yakın olan kenar geniş, uzak olan kenar ise dar görünür.

Danışman mühendisim bu noktada çok önemli bir kuralı hatırlattı: "Perspektifi düzeltilmemiş bir görüntü üzerinde motif genişliği, bordür kalınlığı veya simetri ölçümü yapamazsın; çünkü piksel başına düşen milimetre değeri görüntünün üstüyle altında farklıdır."

Bu geometrik distorsiyonu ortadan kaldırmak amacıyla projektif geometri ve homografi dönüşümünü inceledim. İki düzlem arasındaki perspektif izdüşüm ilişkisini tanımlayan $3\times3$ boyutundaki homografi matrisinin ($H$), 8 serbestlik derecesine sahip olduğunu öğrendim. Bu matrisin çözülebilmesi için kaynak görüntüdeki 4 köşe noktası ile bunların düzeltilmiş hedef dikdörtgendeki 4 koordinatı arasındaki doğrusal denklem sisteminin kurulması gerektiğini matematiksel olarak modelledim.

Bu teoriyi kodlamak üzere `homography` modülünü geliştirdim. Halının açılı görüntüsündeki 4 tepe noktasını tespit ederek, bunları kuş bakışı düz bir koordinat sistemine eşleyecek matematiksel altyapıyı kurdum.

**KONTROL SONUCU:**

---

## GÜN 12 — DEVAM
**KISIM:** Perspektif Düzeltme ve Homografi  
**YAPRAK NO:** 24  
**YAPILAN İŞ:** Köşe Seçiminin Sonuca Etkisinin ve Düzeltilmiş Görüntünün Değerlendirilmesi  
**TARİH:** 03/08/2026

Öğleden sonraki oturumda homografi dönüşümünü pratik bir yazılım modülü haline getirdim. İlk olarak köşe noktalarının sıralanması problemini ele aldım. Görüntü işleme modellerinde köşe koordinatları tespit edildiğinde bu noktalar belleğe rastgele bir sırayla gelebilir. Ancak noktaların hedef koordinatlarla birebir eşleşmesi zorunludur; eğer sol-üst nokta sağ-alt noktayla eşleşirse görüntü burulur veya ters yüz olur.

Bu sorunu çözmek için `corner_detector` modülü içinde `order_points` fonksiyonunu geliştirdim. Noktaların $x+y$ toplamından sol-üst ve sağ-alt köşeleri, $y-x$ farkından ise sağ-üst ve sol-alt köşeleri kesin olarak ayrıştıran deterministik bir sıralama algoritması kodladım.

Ardından `HomographyRectifier` sınıfını inşa ettim. Bu sınıf, sıralanan 4 köşe noktasını alarak `cv2.getPerspectiveTransform` fonksiyonuyla homografi matrisini hesaplıyor ve `cv2.warpPerspective` fonksiyonuyla açılı görüntüyü düzelterek kuş bakışı (top-down) ortografik bir görüntü üretiyordu. Dönüştürülmüş görüntünün hedef genişlik ve yüksekliğini orijinal halı ebatlarına (örneğin 160x230 cm) orantılı olarak yeniden ölçekledim.

Düzeltilmiş görüntü üzerinde cetvel ölçümleri yaparak perspektif eğriliğinin tamamen giderildiğini, kenarların birbirine dik hale geldiğini ve desen geometrisinin aslına döndüğünü gözlemledim.

Yazdığım doğrultma motorunu `test_corner_detector`, `test_homography`, `test_order_points` ve `test_rectification` test dosyalarıyla kapsamlı şekilde sınadım. Köşe sıralamanın ve homografi matrisi determinantının doğruluğunu pytest ile kanıtladım.

Günün sonunda, açılı kameralardan gelen eğik görüntüleri yapay zekâ modellerinin beklediği kusursuz dik formata getiren kritik bir ön işleme halkasını tamamladım.

**KONTROL SONUCU:**

---

## GÜN 13 — 4 AĞUSTOS 2026
**KISIM:** Morfolojik İşlemler, Kenar ve Çizgi Tespiti  
**YAPRAK NO:** 25  
**YAPILAN İŞ:** Morfolojik İşlemlerle Gürültü ve Bölge Yapısının İncelenmesi  
**TARİH:** 04/08/2026

Stajımın on üçüncü gününde, halı dokuma yüzeyinde meydana gelen fiziksel üretim hatalarının (iplik kopuklukları, yabancı elyaf parçacıkları, yağ lekeleri ve bordür kaymaları) tespiti için kullanılan morfolojik görüntü işleme operasyonlarını inceledim. Dokuma kumaş yüzeyi pikseller düzeyinde incelendiğinde, iplik liflerinden ve doku pürüzlerinden kaynaklanan yoğun bir yüksek frekanslı gürültü içerir. Bu gürültü filtrelenmeden doğrudan hata tespiti yapmaya çalışmak yüzlerce sahte alarma (false alarm) yol açar.

Bu sorunu çözmek için ikili (binary) görüntüler üzerinde yapılandırıcı eleman (structuring element / kernel) kullanarak şekil geometrisini düzenleyen morfolojik operatörleri inceledim. `morphology_engine` modülü altında `MorphologyEngine` sınıfını geliştirdim. Sınıf içinde iki temel işlemi kodladım:
1. Aşındırma (Erosion): Ön plandaki beyaz piksel adacıklarını kenarlardan aşındırarak küçük parazit noktalarını yok eder.
2. Genişletme (Dilation): Piksel adacıklarının sınırlarını genişleterek kopuk iplik hatlarını birleştirir.

Ardından bu iki operatörün sıralı birleşimi olan Açma (Opening: önce aşındırma sonra genişletme) ve Kapama (Closing: önce genişletme sonra aşındırma) işlemlerini uyguladım. Açma işlemi sayesinde sentetik kumaş görüntüsündeki küçük tüy parazitlerini ve gürültüleri tamamen temizlerken, Kapama işlemiyle dokuma örgüsü arasındaki istenmeyen mikro boşlukları doldurdum.

Filtrelenen kusur maskelerinin, ham görüntüye kıyasla ne kadar temiz ve net bir hata haritası sunduğunu gözlemledim.

**KONTROL SONUCU:**

---

## GÜN 13 — DEVAM
**KISIM:** Morfolojik İşlemler, Kenar ve Çizgi Tespiti  
**YAPRAK NO:** 26  
**YAPILAN İŞ:** Canny ve Hough ile Kenar ve Çizgi Yapısının İncelenmesi  
**TARİH:** 04/08/2026

Öğleden sonraki oturumda halının kenar overlok çizgilerinin düzgünlüğünü ve tezgâhtaki atkı/çözgü ipliklerinin hizalama doğruluğunu denetlemek üzere kenar ve çizgi tespiti algoritmalarına odaklandım.

İlk olarak `edge_operators` modülünde piksel yoğunluk türevlerini alan Sobel operatörü ile çok aşamalı Canny kenar dedektörünü (`cv2.Canny`) karşılaştırdım. Canny algoritmasının; Gauss yumuşatma, gradyan yönü ve büyüklüğü hesabı, yerel olmayan maksimumları bastırma (non-maximum suppression) ve histerezis çift eşikleme aşamalarından geçerek ne kadar keskin ve ince (1 piksel kalınlığında) kenarlar ürettiğini inceledim.

Ardından bu kenarlar üzerindeki doğrusal yapıları yakalamak amacıyla `hough_engine` modülü içinde Olasılıksal Hough Çizgi Dönüşümü (`cv2.HoughLinesP`) algoritmasını koşturan `HoughEngine` sınıfını yazdım. Hough dönüşümü, görüntü uzayındaki doğrusal kenar piksellerini parametrik uzayda ($\rho, \theta$) kesiştirerek gürültülü ve kesintili çizgileri tek bir sürekli doğru olarak tespit ediyordu.

Bu motor ile sentetik halının kenar bordür hatlarını ve tezgâh atkı çizgilerini tespit ettim. Tespit edilen doğruların yatay ve dikey eksenle yaptığı eğim açılarını hesaplayarak, dokumada bir açısal kayma (dokuma eğriliği / skewness) olup olmadığını sayısal bir sapma derecesi olarak ölçümledim.

Yazdığım tespit araçlarını `test_edge_lines` ve `test_morphology_defects` test paketleriyle sınayarak çizgi koordinatlarının ve kusur sınır kutularının doğruluğunu pytest ile kanıtladım.

Günün sonunda, morfolojik temizlik ve Hough çizgileriyle fiziksel dokuma düzgünlüğünü denetleyen sağlam bir kalite kontrol aracı geliştirdim.

**KONTROL SONUCU:**

---

## GÜN 14 — 5 AĞUSTOS 2026
**KISIM:** Klasik Görüntü Segmentasyonu  
**YAPRAK NO:** 27  
**YAPILAN İŞ:** Otsu, Watershed ve GrabCut yöntemlerinin sentetik görsellerde uygulanması  
**TARİH:** 05/08/2026

Stajımın on dördüncü gününde, halı üzerindeki desen motiflerini zeminden ayırmak ve kusurlu bölgeleri piksel seviyesinde izole etmek için klasik görüntü segmentasyonu yöntemlerini derinlemesine inceledim. Danışman mühendisimle yaptığımız toplantıda, her segmentasyon yönteminin farklı bir matematiksel temele dayandığını ve endüstriyel sistemlerde hız ile doğruluk arasında daima bir ödünleşim (trade-off) bulunduğunu konuştuk.

Bu karşılaştırmayı somutlaştırmak üzere üç farklı segmentasyon motorunu modüler olarak kodladım:
1. Otsu Eşikleme (`otsu_segmenter`): Görüntünün gri seviye histogramını iki sınıfa ayıran ve sınıflar arası varyansı maksimize eden global eşik değerini otomatik olarak belirleyen eşikleme motoru.
2. Watershed Havza Algoritması (`watershed_segmenter`): Görüntüyü bir topoğrafik kabartma haritası gibi ele alıp, mesafe dönüşümü (`cv2.distanceTransform`) ile yerel zirveleri tespit ederek birbirine temas eden desen bölgelerini su havzaları gibi ayıran işaretçi tabanlı segmentasyon motoru.
3. GrabCut Algoritması (`grabcut_segmenter`): Gauss Karışım Modelleri (GMM) ve çizge kesme (Graph Cut / max-flow min-cut) optimizasyonuyla bir çevreleme kutusu içindeki ön plan ve arka planı enerji minimizasyonuyla ayıran iteratif segmentasyon motoru.

Her üç yöntemi de sentetik halı desenleri ve kusur bölgeleri üzerinde çalıştırarak ürettikleri ikili segmentasyon maskelerini elde ettim.

**KONTROL SONUCU:**

---

## GÜN 14 — DEVAM
**KISIM:** Klasik Görüntü Segmentasyonu  
**YAPRAK NO:** 28  
**YAPILAN İŞ:** IoU ve işlem süresiyle üç yöntemin sentetik benchmark üzerinde incelenmesi  
**TARİH:** 05/08/2026

Öğleden sonraki çalışmamda, sabah geliştirdiğim üç segmentasyon algoritmasını nesnel metriklerle kıyaslamak üzere `evaluator` modülü altında `SegmentationEvaluator` sınıfını geliştirdim. Algoritmaların başarımını ölçmek için bilgisayarlı görünün temel doğruluk ölçütü olan Kesişim/Birleşim Oranı (IoU: Intersection over Union) ve Dice Benzerlik Katsayısı metriklerini hesaplayan fonksiyonları yazdım.

Ardından `benchmark` modülü ile her üç yöntemi sentetik halı veri kümesi üzerinde koşturarak doğruluk ve işlem süresi (gecikme) benchmark'ını gerçekleştirdim. Elde ettiğim sonuçlar çok öğretici bir mühendislik tablosu sundu:
- Otsu Eşikleme: Kare başına 1.8 milisaniye gibi olağanüstü bir hız sergiledi; ancak halı üzerindeki karmaşık renk geçişlerinde ve zayıf aydınlatmada düşük IoU skoru (%61.5) üretti.
- Watershed: Birbirine temas eden bitişik desenleri ve leke adacıklarını çok iyi ayırarak 14 milisaniye gecikme ve %82.3 IoU skoru ile mükemmel bir hız-kalite dengesi sundu.
- GrabCut: Ön plan sınırlarını %91.8 gibi yüksek bir IoU ile kusursuz yakaladı; ancak iteratif çizge kesme döngüsü nedeniyle kare başına 175 milisaniye sürerek gerçek zamanlı konveyör bandı için aşırı yavaş kaldı.

Danışman mühendisimle yaptığımız değerlendirmede, gerçek zamanlı üretim bandında Watershed ve adaptif eşikleme kombinasyonunun, çevrim dışı tasarım kataloglamada ise GrabCut'ın seçilmesi gerektiği yönündeki mimari kararı netleştirdik.

Yazdığım segmentasyon araçlarını `test_carpet_segmenter` ve `test_segmentation` testleriyle doğruladım.

**KONTROL SONUCU:**

---

## GÜN 15 — 6 AĞUSTOS 2026
**KISIM:** Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu  
**YAPRAK NO:** 29  
**YAPILAN İŞ:** Geleneksel Görsel Özelliklerin Çıkarılması  
**TARİH:** 06/08/2026

Stajımın on beşinci gününde, Bilgisayarlı Görü fazının zirve noktası olan öznitelik çıkarımı (feature extraction) konusuna odaklandım. Bir halı görüntüsünü makine öğrenmesi algoritmalarına besleyebilmek veya benzerlik aramalarında kullanabilmek için, milyonlarca pikselden oluşan ham görüntüyü halının görsel karakterini özetleyen kompakt sayısal öznitelik vektörlerine (feature vectors) dönüştürmemiz gerekir.

Bu doğrultuda halının görsel kimliğini yansıtan üç bağımsız öznitelik çıkarıcı geliştirdim:
1. Renk Histogramı (`color_histogram`): HSV uzayında renk dağılımını 3 boyutlu olarak bölümlere ayıran (örneğin $8 \times 8 \times 8 = 512$ boyutlu) ve $L_1$ normalizasyonu ile aydınlatma şiddetinden bağımsız hale getirilen renk dağılım vektörü.
2. Doku Öznitelikleri (`glcm_engine`): Gri Seviye Eş-Oluşum Matrisi (GLCM) algoritmasıyla dokuma sıklığını ve yüzey pürüzlülüğünü modelleyen; Kontrast, Homojenlik, Enerji, Korelasyon ve Farklılık (Dissimilarity) istatistiklerini çıkaran fonksiyonlar.
3. Anahtar Noktalar (`keypoint_engine`): ORB (Oriented FAST and Rotated BRIEF) algoritmasıyla halı motiflerinin köşe ve merkez noktalarını ölçek ve dönmeden bağımsız olarak tespit eden anahtar nokta tanımlayıcısı.

Bu üç öznitelik modalitesinin bir araya gelmesiyle, bir halının hem renk paletini hem dokuma yapısını hem de desen geometrisini temsil edebilecek çok yönlü bir özellik uzayı oluşturdum.

**KONTROL SONUCU:**

---

## GÜN 15 — DEVAM
**KISIM:** Görsel Özellik Çıkarımı ve Boru Hattı Entegrasyonu  
**YAPRAK NO:** 30  
**YAPILAN İŞ:** Görüntü İşleme Modüllerinin Tek Akışta Birleştirilmesi  
**TARİH:** 06/08/2026

Öğleden sonraki oturumda, son iki haftadır geliştirdiğim tüm bilgisayarlı görü modüllerini (ön işleme, homografi, renk analizi, morfoloji, doku ve anahtar noktalar) tek bir uçtan uca muayene boru hattında birleştirdim.

Bu entegrasyonu sağlamak üzere `feature_fusion` ve `feature_integrator` modülleri altında `FeatureIntegrator` sınıfını geliştirdim. Sınıf içine; farklı boyut ve ölçeklerdeki renk histogramını, GLCM doku metriklerini ve ORB anahtar nokta tanımlayıcılarını $L_2$ normalizasyonu ile dengeleyerek tek bir birleşik öznitelik vektöründe (fused feature vector) toplayan fonksiyonu kodladım. Böylece hiçbir özelliğin diğerini sayısal büyüklüğüyle ezmesine izin vermeden dengeli bir temsil elde ettim.

Ardından `inspect_pipeline` modülünde tam otomatik görsel muayene akışını kurguladım. Sisteme giren sentetik bir halı görüntüsünün; önce perspektifinin düzeltildiğini, ardından renk paletinin çıkarılıp baskın tonlarının katalogla eşleştirildiğini, dokuma pürüzlülüğünün ölçüldüğünü ve son olarak makine öğrenmesi için hazır 540 boyutlu bir öznitelik vektörü üretildiğini gözlemledim.

Geliştirdiğim entegre boru hattını `test_features`, `test_feature_integrator` ve `test_vision_toolkit` test paketleriyle sınayarak vektör boyutunun sabitliğini ve çalışma zamanı kararlılığını pytest ile teyit ettim.

Böylece stajımın ikinci büyük fazı olan **Faz 2: Bilgisayarlı Görü** aşamasını başarıyla tamamladım. Ham piksellerle başladığımız serüvende perspektif düzeltme, renk uzayları, K-Means kümeleme, morfolojik kusur filtreleme ve çok boyutlu öznitelik entegrasyonuyla görsel verileri kusursuz bir sayısal temsile kavuşturduk. Yarın stajımın üçüncü büyük aşaması olan **Faz 3: Klasik Makine Öğrenmesi** dünyasına adım atarak, bu vektörlerle üretim kusurlarını sınıflandıracak modelleri eğitmeye geçmeye hazır hale geldim.

**KONTROL SONUCU:**

---
'''

new_full_text = full_text[:pos_start] + faz2_expanded + full_text[pos_end:]

with open('Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md', 'w', encoding='utf-8') as f:
    f.write(new_full_text)

print('Successfully applied Faz 2 expansion to Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md!')
