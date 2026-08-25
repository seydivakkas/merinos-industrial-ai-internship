# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Text Cleaner: Endüstriyel Doküman Temizleme, Başlık Ayrıştırma ve Normalizasyon
"""

import re
from typing import List, Tuple


class TextCleaner:
    """Endüstriyel metin temizleyici ve bölüm ayrıştırıcı."""

    @staticmethod
    def clean(text: str) -> str:
        """
        Ham doküman metnini temizler:
        - Boşluk ve sayfa sonu karakterlerini normalize eder.
        - Satır sonundaki kırık tireli kelimeleri birleştirir (örn: 'dokuma-\nları' -> 'dokumaları').
        - Ardışık boş satırları tek satıra indirger.
        """
        if not text:
            return ""

        # 1. Unicode boşluk normalizasyonu
        cleaned = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")

        # 2. Satır sonu kırık kelimeleri birleştir (örn: 'iplik-\nler' -> 'iplikler')
        cleaned = re.sub(r"(\w+)-\n\s*(\w+)", r"\1\2", cleaned)

        # 3. Sayfa altı/üstü kalıp çöplerini temizle (örn: '--- Sayfa 1 ---' veya 'Sayfa 1 / 5')
        cleaned = re.sub(r"(?i)---\s*sayfa\s*\d+\s*---", "", cleaned)
        cleaned = re.sub(r"(?i)sayfa\s+\d+\s+/\s+\d+", "", cleaned)

        # 4. Satır başı ve sonu boşlukları temizle
        lines = [line.strip() for line in cleaned.split("\n")]

        # 5. Art arda gelen 2'den fazla boş satırı tek boş satıra indir
        result_lines: List[str] = []
        blank_count = 0
        for line in lines:
            if not line:
                blank_count += 1
                if blank_count <= 1:
                    result_lines.append("")
            else:
                blank_count = 0
                result_lines.append(line)

        return "\n".join(result_lines).strip()

    @staticmethod
    def extract_sections(text: str) -> List[Tuple[str, str]]:
        """
        Metin içindeki başlıkları tespit edip (başlık, bölüm_metni) çiftleri olarak böler.
        Markdown başlıkları ('#', '##'), 'BÖLÜM X:', 'MADDE X:' gibi kalıpları destekler.
        """
        lines = text.split("\n")
        sections: List[Tuple[str, List[str]]] = []
        current_title = "Giriş ve Genel Tanım"
        current_lines: List[str] = []

        header_pattern = re.compile(
            r"^(?:#{1,4}\s+|BÖLÜM\s+\d+[:.]?|MADDE\s+\d+[:.]?|\d+\.\s+[A-ZÇĞİÖŞÜ])",
            re.IGNORECASE
        )

        for line in lines:
            s_line = line.strip()
            if header_pattern.match(s_line) and len(s_line) < 120:
                # Yeni bir başlık bulundu
                if current_lines:
                    sec_text = "\n".join(current_lines).strip()
                    if sec_text:
                        sections.append((current_title, current_lines))
                # Başlığı temizle (örn: '## 1. Tarak Ayarları' -> '1. Tarak Ayarları')
                clean_title = re.sub(r"^#{1,4}\s*", "", s_line).strip()
                current_title = clean_title
                current_lines = [s_line]
            else:
                current_lines.append(line)

        if current_lines:
            sec_text = "\n".join(current_lines).strip()
            if sec_text:
                sections.append((current_title, current_lines))

        if not sections:
            return [("Genel", text)]

        return [(title, "\n".join(body_lines).strip()) for title, body_lines in sections]
