# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
HyDE (Hypothetical Document Embeddings): Hipotetik Fabrika SOP Dokümanı Üretici
"""

import re
from typing import Optional


class HyDEGenerator:
    """
    Kısa veya bozuk operatör sorusundan, Merinos doküman biçiminde ve tonunda
    varsayımsal (hipotetik) bir teknik SOP paragrafı üreten motor.
    """

    def __init__(self, template_mode: str = "industrial_sop"):
        self.template_mode = template_mode

    def generate_hypothetical_document(self, query: str) -> str:
        """
        Sorgu için resmi doküman biçiminde varsayımsal bir SOP paragrafı oluşturur.
        Bu metin, dense arama motorunun sorgu uzayından doküman uzayına geçişini sağlar.
        """
        q_lower = query.lower()

        # 1. Motor Sıcaklığı ve E-401 Senaryosu
        if "e-401" in q_lower:
            return (
                "MERİNOS DOKUMA TEZGÂHI STANDART OPERASYON PROSEDÜRÜ (SOP)\n"
                "Bölüm 4: Kritik Tezgâh Arıza Kodları ve Müdahale Adımları\n"
                "E-401 Arıza Kodu: Ana tahrik motoru gövde sıcaklığı kritik eşik olan 85°C sınırını aştığında "
                "veya inverter motor akımı nominal değerin üzerine çıktığında tezgâh otomatik stop eder. "
                "Operatör acil durdurma butonuna basmalı, motor soğutma fanını basınçlı hava ile temizlemeli "
                "ve sıcaklık 50°C altına inmeden tezgâhı yeniden devreye almamalıdır."
            )
        if any(w in q_lower for w in ["motor", "sıcak", "sicak", "ısın", "isin"]):
            return (
                "Motorda aşırı ısınma tespit edildiğinde operatör derhal motoru durdurmalı, "
                "soğutma sistemini kontrol etmeli, sıcaklık değerlerini izlemeli "
                "ve ilgili bakım prosedürlerine göre gerekli adımları uygulamalıdır."
            )


        # 2. Jakar, Tarak ve Sarı İkaz Lambası Senaryosu
        if any(w in q_lower for w in ["jakar", "sarı lamba", "sari lamba", "kaydı", "kaydi", "yavas", "yavaş"]):
            return (
                "MERİNOS HEREKE JAKARLI HALI DOKUMA ŞARTNAMESİ\n"
                "Bölüm 2: Tarak Boşluğu Toleransı ve Otomatik Hız Ayarı\n"
                "Hereke serisi 80x80 düğüm jakarlı dokuma tezgâhlarında güveler arası tarak boşluğu toleransı "
                "en fazla 0.45 mm olmalıdır. Bu tolerans aşıldığında tezgâh desen kayması semptomu algılar "
                "ve operatörü uyarmak için sarı ikaz lambasını yakarak otomatik olarak yavaş çalışma moduna geçer."
            )

        # 3. Çözgü Çerçeve Kilit ve 6 Bar Basınç (E-256) Senaryosu
        if any(w in q_lower for w in ["cerceve", "çerçeve", "kilit", "6 bar"]):
            return (
                "MERİNOS DOKUMA TEZGÂHI ARIZA REHBERİ\n"
                "Bölüm 4: Çözgü Sistemi Pnömatik ve Hidrolik Arızaları\n"
                "E-256 Arıza Kodu: Çözgü çerçeve kilit mekanizması hidrolik ve pnömatik çalışma basıncı "
                "kritik eşik olan 6 bar seviyesinin altına düştüğünde sistem otomatik stop eder. "
                "Operatör çerçeve pistonlarını ve ana regülatör basınç göstergesini kontrol etmelidir."
            )

        # 4. İplik Tansiyon Basıncı ve 14 Bar (Kopuş) Senaryosu
        if any(w in q_lower for w in ["tansiyon", "vana", "14 bar", "koptu"]):
            return (
                "MERİNOS İPLİK VE ÇÖZGÜ KALİTE STANDARTLARI ŞARTNAMESİ\n"
                "Bölüm 3: İplik Tansiyonu ve Çözgü Gerginlik Limitleri\n"
                "Dokuma tezgâhında iplik tansiyon basıncı 14 bar altına düştüğünde çözgü tellerinde aşırı kopuş "
                "ve dokuma hataları meydana gelir. Operatör acil olarak Vana 3 ayarını kontrol etmeli "
                "ve sistem basıncını 16 bar çalışma seviyesine yükseltmelidir."
            )

        # 5. Buharlı Fikse ve Renk Parlaklığı Senaryosu
        if any(w in q_lower for w in ["fikse", "buhar", "parlak"]):
            return (
                "MERİNOS HALI TERBİYE VE FİNİSAJ EL KİTABI\n"
                "Bölüm 2: Buharlı Fikse Tüneli ve Renk Sabitleme İşlemi\n"
                "Doymuş buharlı fikse tüneli işlemi 60 derece sıcaklıkta gerçekleştirilir. "
                "Bu operasyon iplik polimer zincirindeki kristal yapıyı sabitleyerek halı renk parlaklığını "
                "spektrofotometre CIELAB ölçümlerinde yüzde 12 oranında artırır."
            )

        # 6. Traşlama ve Hav Yüksekliği Senaryosu
        if any(w in q_lower for w in ["tras", "traş", "hav", "bıçak", "bicak"]):
            return (
                "MERİNOS HALI TERBİYE VE SON İŞLEMLER KILAVUZU\n"
                "Bölüm 3: Döner Bıçaklı Traşlama (Shearing) Standardı\n"
                "Buhar fiksesi sonrasında halı yüzeyindeki düzensiz hav iplikleri döner bıçaklı traşlama makinesinde "
                "tam olarak 9.5 mm hav yüksekliği toleransında kesilerek pürüzsüz halı yüzeyi elde edilir."
            )

        # 7. Overlok Dikişi ve 45 Newton Senaryosu
        if any(w in q_lower for w in ["overlok", "newton", "mukavemet"]):
            return (
                "MERİNOS HALI BİTİM VE AMBALAJ KALİTE TALİMATI\n"
                "Bölüm 4: Kenar Overlok Dikiş Dayanım Standartları\n"
                "Kenar overlok operasyonunda kullanılan poliamid takviyeli 3 katlı iplik, "
                "çekme test cihazında en az 45 Newton mekanik mukavemet eşiğini karşılamak zorundadır."
            )

        # 8. Klima, Bağıl Nem ve Statik Elektrik Senaryosu
        if any(w in q_lower for w in ["klima", "nem", "22"]):
            return (
                "MERİNOS DOKUMA SALONU İKLİMLENDİRME VE KALİTE REHBERİ\n"
                "Bölüm 1: Ortam Şartlandırması ve Statik Elektrik Önleme\n"
                "Dokuma salonu klima santrali ortam bağıl nemini yüzde 65 ile 70 arasında ve sıcaklığı "
                "22 santigrat derece seviyesinde tutmalıdır. Sıcaklık 22°C üzerine çıktığında ipliklerde "
                "statik elektrik birikerek tezgâhta atkı besleme hatalarına yol açar."
            )

        # Genel Varsayımsal Fabrika SOP Şablonu (Fallback)
        return (
            "MERİNOS HALI SANAYİ A.Ş. STANDART OPERASYON PROSEDÜRÜ VE TEKNİK KILAVUZU\n"
            f"İlgili Konu: {query}\n"
            "Dokuma, terbiye ve kalite kontrol süreçlerinde belirlenen teknik parametrelere ve güvenlik "
            "kurallarına eksiksiz uyulmalıdır. Belirtilen arıza veya ayar durumunda ilgili tezgâh sensörleri, "
            "basınç regülatörleri ve standart çalışma toleransları derhal kontrol edilmelidir."
        )
