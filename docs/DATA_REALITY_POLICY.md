# Veri ve Sistem Gerçekliği Politikası (Data & System Reality Policy)

Bu doküman, Merinos Halı Sanayi ve Ticaret A.Ş. bünyesinde gerçekleştirilen 40 günlük Bilgisayar Mühendisliği Endüstriyel Yapay Zeka Staj Portföyü'nün veri etiği, sistem kapsamı ve deneysel dürüstlük standartlarını belirler.

---

## 1. Temel İlke ve Yasal Dayanak

Merinos Halı Sanayi ve Ticaret A.Ş.'nin kurumsal veri gizliliği, ticari sırların korunması ve Kişisel Verilerin Korunması Kanunu (KVKK) politikaları gereğince:
1. **Sıfır Özel Veri Kuralı:** Canlı üretim hattından çekilmiş gizli SCADA/PLC verileri, gerçek müşteri siparişleri, ticari maliyet tabloları, tescilli dokuma desen dosyaları ve kurum içi özel teknik dokümanlar geliştirici ortamına aktarılmamış ve repoya dahil edilmemiştir.
2. **Sentetik Veri İlkesi:** Repodaki tüm sayısal sensör telemetrileri, görsel kusur simülasyonları ve teknik bakım dokümantasyonları; tekstil makinelerinin (Van de Wiele ve Schönherr jakarlı dokuma tezgâhları) fiziksel çalışma prensipleri ve uluslararası standartlar (ISO VG 220, CIEDE2000 vb.) modellenerek **%100 sentetik veya açık kaynaklı** olarak üretilmiştir.

---

## 2. Sistem Kapsamı: Yerel PoC vs. Üretim Sistemi

- **Gerçekleştirilen Çalışma:** Bu depoda yer alan tüm kodlar, algoritmalar ve mikroservisler; Gaziantep Bilgi İşlem ofisindeki yerel geliştirme ortamında çalışan **modüler bir Kavram Kanıtı (Proof of Concept - PoC)** niteliğindedir.
- **Canlı Sistem İddiası Yoktur:** Sistemin canlı SCADA/PLC ağlarına doğrudan bağlandığı, fiziksel dokuma tezgâhlarını otonom durdurduğu veya kurumsal ERP/MES veri tabanlarına doğrudan yazma yetkisi bulunduğu iddia edilmez.
- **Gelecekteki Entegrasyon Senaryosu:** Mimari dokümanlarda (örneğin Celery, Redis broker, OPC-UA ağ geçitleri) bahsi geçen kurumsal yapılar; projenin gelecekte fiziksel tesise entegre edilmesi durumunda izlenebilecek kuramsal ölçekleme senaryolarıdır (Future Work).

---

## 3. Deneysel Dürüstlük ve Benchmark İlkeleri

1. **Uydurma Metrik Yasağı:** Model başarım metrikleri (Doğruluk, ROC-AUC, PR-AUC, MRR, NDCG, gecikme, bellek tüketimi), gerçekte çalıştırılmamış veya hesaplanmamışsa kesinlikle uydurulamaz.
2. **`NOT_EXECUTED` Standardı:** Donanım yetersizliği veya test edilmemiş bir durum söz konusu olduğunda tahmini sayı yazmak yerine açıkça `NOT_EXECUTED` ibaresi kullanılır.
3. **Retrieval ve Generation Ayrımı:** RAG sistemlerinde bilgi getirme (retrieval) başarımı ile yanıt üretme (generation) başarımı ayrı ayrı değerlendirilir.
4. **Görsel Kalite Garantisi Sınırı:** Üretilen sentetik halı desenlerinde otomatik hesaplanan metrikler ($\Delta E^*$, simetri skoru) fiziksel imalat garantisi veya nihai estetik kalite kanıtı olarak sunulamaz.

---

## 4. Bağımsız Çalışabilirlik (Standalone Notebooks)

Tüm 40 günün Jupyter Notebook (`.ipynb`) dosyaları; harici disk dosyalarına, alt modül importlarına veya ağ bağlantısına ihtiyaç duymadan, herhangi bir izole ortamda (Google Colab, VS Code, temiz Python) tek tıkla (**Run All**) sıfır hatayla çalışacak şekilde kendi kendine yeterli (self-contained) tasarlanmıştır.

---

## 5. Lisans ve Telif Hakkı

Bu projenin tüm hakları saklıdır. Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas). MIT veya türevi açık kaynak lisansları geçerli değildir; kodlar yalnızca eğitim ve portföy inceleme amacıyla paylaşılmıştır.
