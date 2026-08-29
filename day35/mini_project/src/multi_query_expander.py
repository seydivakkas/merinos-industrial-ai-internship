# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 35
Multi-Query Expander: Tekil Sorgudan Çok Boyutlu Mühendislik Perspektifleri Türetici
"""

import re
from typing import List


class MultiQueryExpander:
    """Tek bir sorgudan birden fazla arama sorgusu üretir
    (farklı perspektifler)."""

    def __init__(self, model=None):
        self.model = model

    def expand(self, query: str, n: int = 3) -> list[str]:
        """Tek bir sorgudan n adet farklı arama sorgusu üretir.
        Varsayılan olarak 3 sorgu döndürür."""
        base = query.lower().strip()
        if "motor" in base and ("sıcak" in base or "sicak" in base or "durdu" in base or "aşırı ısınma" in base):
            base = "motorda aşırı ısınma"
        elif "iplik" in base and "kop" in base:
            base = "iplik kopuşu ve tansiyon basıncı"
        elif "sarı lamba" in base or "sari lamba" in base:
            base = "jakar sarı ikaz lambası ve tarak boşluğu"
        elif "cerceve" in base or "çerçeve" in base:
            base = "çözgü çerçeve kilit mekanizması ve basınç eşiği"

        queries = []

        # 1. Teknik odaklı sorgu (neden/arıza)
        q1 = f"{base} nedenleri, arıza, teknik açıklama"
        queries.append(q1)

        # 2. Operatör müdahale sorgusu
        q2 = f"{base} için operatör müdahale, yapılacaklar"
        queries.append(q2)

        # 3. Bakım/SOP sorgusu
        q3 = f"{base} bakım prosedürü, SOP, güvenlik önlemleri"
        queries.append(q3)

        return queries[:n]

