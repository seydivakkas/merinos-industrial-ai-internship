# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
Query Rewriter: Operatör Argo ve Kısaltmalarını Teknik SOP Diline Dönüştürücü
"""

import re
from typing import Dict, Optional


DEFAULT_SLANG_MAP: Dict[str, str] = {
    "motor cok sıcak": "E-401 ana tahrik motoru gövde sıcaklığı 85 derece aşırı ısınma",
    "motor ısınıyo": "E-401 ana tahrik motoru aşırı ısınması sıcaklık ve akım",
    "napcam": "operatör müdahale adımları ve acil durdurma butonu",
    "sarı lamba": "jakar sarı ikaz lambası otomatik yavaş mod",
    "jakar kaydı": "tarak boşluğu toleransı 0.45 mm desen kayması",
    "cerceve kilit": "E-256 çözgü çerçeve kilit mekanizması",
    "basinc dustu": "basınç düşüşü 6 bar kritik eşiği",
    "iplik koptu": "çözgü telleri kopuşu tansiyon basıncı 14 bar vana 3 ayarı",
    "ip koptu": "çözgü teli kopuşu tansiyon basıncı 14 bar",
    "rezerv bos": "E-108 mekik iplik rezerv sensörü boş uyarısı",
    "traslama": "döner bıçaklı traşlama hav yüksekliği 9.5 mm",
    "fikse": "buharlı fikse tüneli 60 derece renk parlaklığı CIELAB",
    "overlok": "kenar overlok dikişi poliamid 3 kat 45 newton çekme mukavemeti",
    "nem sıcaklık": "dokuma salonu klima şartlandırma bağıl nem yüzde 65 ve 22 derece sıcaklık",
    "hereke jakar": "Hereke serisi klasik jakarlı halı 28 tel ve 80x80 düğüm atkı sıklığı"
}


def clean_text_basic(text: str) -> str:
    """Temel temizleme ve karakter düzenleme."""
    t = text.lower()
    t = t.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return re.sub(r"\s+", " ", t).strip()


class QueryRewriter:
    """Günlük dille yazılan operatör sorularını
    teknik terimlerle yeniden yazar."""
    def __init__(self, config_path=None):
        self.term_dict = {
            "sıcak": "aşırı ısınma",
            "çok sıcak": "aşırı ısınma",
            "ısı": "sıcaklık",
            "motor": "motor",
            "durdu": "durma",
            "napcam": "operatör müdahale",
            "ne yapmalıyım": "operatör müdahale",
            "arıza": "arıza",
            "alarm": "alarm",
            "titreşim": "titreşim",
        }
        self.formal_templates = {
            "motor cok sicak durdu napcam": "motorda aşırı ısınma nedeniyle durma durumu için operatör müdahale prosedürleri nelerdir?",
            "motor cok sıcak durdu napcam": "motorda aşırı ısınma nedeniyle durma durumu için operatör müdahale prosedürleri nelerdir?",
            "cerceve kilit basinc dustu durdu kod ne": "çözgü çerçeve kilit mekanizması hidrolik ve pnömatik 6 bar basınç düşüşü arıza kodu E-256",
            "sarı lamba yanıyo tezgah yavasladı neden": "jakar sarı ikaz lambası yanması ve dokuma hızı yavaşlama nedenleri, tarak boşluğu toleransı 0.45 mm",
            "sari lamba yaniyo tezgah yavasladi neden": "jakar sarı ikaz lambası yanması ve dokuma hızı yavaşlama nedenleri, tarak boşluğu toleransı 0.45 mm",
            "iplik koptu hangi vana basınç kaçtı": "iplik tansiyon basıncı düşüşü ve 14 bar vana 3 ayarı standart prosedürü",
            "kazan buharlı fikse kaç derece yapılıyor": "buharlı fikse tüneli 60 derece sıcaklık ve CIELAB renk parlaklığı standardı",
            "mekik iplik rezerv bos arıza kodu": "mekik iplik rezerv sensörü boş uyarısı arıza kodu E-108",
            "hereke jakar tarak atkı sıklığı kaçtı": "Hereke serisi klasik jakarlı halı 80x80 düğüm ve 28 tel tarak atkı sıklığı",
            "dokuma salonu klima nem sıcaklık kac olmalı": "dokuma salonu klima şartlandırma bağıl nem yüzde 65 ve 22 derece sıcaklık toleransı",
            "halı traslama bıcak hav kac mm kesiyor": "halı traşlama döner bıçak hav yüksekliği 9.5 mm standardı",
            "overlok ipi kac newton dayanır": "kenar overlok dikiş ipi poliamid 3 kat 45 newton çekme mukavemeti standardı",
            "jakar sarı ikazda motor durur mu": "jakar sarı ikaz lambasında motor durma ve yavaş çalışma modu",
            "dokuma sıcaklık 22yi gecerse statik elektrik": "dokuma salonu sıcaklık 22 dereceyi aşarsa statik elektrik oluşumu ve iplik kopuşu",
            "buhar fiksesi renk parlaklıgı ne katar": "buharlı fikse tüneli işlemi renk parlaklığı ve CIELAB renk doğruluğu",
            "cerceve kilit mekanizması 6 barda ne yapar": "çözgü çerçeve kilit mekanizması 6 bar basınç eşiği ve emniyet kilitlemesi"
        }

    def rewrite(self, query: str) -> str:
        """Günlük ifadeleri teknik terimlerle
        yeniden yazar."""
        q_clean = query.lower().strip()
        if q_clean in self.formal_templates:
            return self.formal_templates[q_clean]

        rewritten = query.lower()
        for informal, formal in self.term_dict.items():
            rewritten = rewritten.replace(informal, formal)
        return rewritten.strip()

